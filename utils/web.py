""" web: A useful collection of web utilities

Note on using socks5h, hostname resolution
https://stackoverflow.com/questions/12601316/how-to-make-python-requests-work-via-socks-proxy
"""

import os
import re
import atexit
import emoji
import brotli
import requests
import subprocess
import tldextract
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from urllib import parse

# Load ------------------------------------------------------------------------

def load_html(fp, zipped=False):
    """Load html file, with option for brotli decompression"""
    read_func = lambda i: brotli.decompress(i.read()) if zipped else i.read()
    read_type = 'rb' if zipped else 'r'
    with open(fp, read_type) as infile:
        return read_func(infile)

def make_soup(html, parser='lxml'):
    """Create soup object, defaults to lxml parser"""
    return BeautifulSoup(html, parser)

def load_soup(fp, zipped=False):
    """Load HTML file and convert to soup"""
    return make_soup(load_html(fp, zipped))

# URLs -------------------------------------------------------------------------

def join_url_quote(quote_dict):
    return '&'.join([f'{k}={v}' for k, v in quote_dict.items()])

def parse_url_query(query):
    return {f'qs_{k}': '|'.join(q) for k, q in parse.parse_qs(query).items()}

def parse_url(url, parse_query=True):
    # Extract and shape all details from a url
    parsed = parse.urlparse(url)
    parsed = { # Convert object to dict
        'scheme': parsed.scheme,
        'netloc': parsed.netloc,
        'path': parsed.path,
        'params': parsed.params,
        'query': parsed.query,
        'fragment': parsed.fragment
    }
    # Extract queries
    if parsed['query'] and parse_query: 
        qs = parse_url_query(parsed['query'])
        parsed['has_query'] = True if qs else False
        parsed.update(qs)
    return parsed

def url_unquote(url):
    """Unquote a URL to remove encoding"""
    return parse.unquote(url)

def url_table(url):
    """Break down a url into a table of its component parts"""
    return pd.Series(tldextract.extract(url), index=['subdomain','domain','suffix'])


def get_domain(url, fillna=''):
    """Extract a full domain from a url, drop www"""
    if pd.isnull(url): return fillna
    extracted = tldextract.extract(url)
    components = [extracted.subdomain, extracted.domain, extracted.suffix]
    domain_str = '.'.join(filter(None, components))
    return domain_str


def is_ipv4(s):
    """Check if a string is an IPv4 address"""
    pieces = s.split('.')
    if len(pieces) != 4: return False
    try: return all(0<=int(p)<256 for p in pieces)
    except ValueError: return False

# Requests --------------------------------------------------------------------

def start_sesh(headers=None, proxy_port=None):
    protocols = ['http', 'https']
    proxy_base = "socks5://127.0.0.1:"
    
    # Generate a requests session object
    sesh = requests.Session()

    if headers: # Add headers to all requests
        sesh.headers.update(headers)

    if proxy_port: # Send all requests through an ssh tunnel
        proxies = {p: f'{proxy_base}{p}' for p in protocols}
        sesh.proxies.update(proxies)

    for protocol in protocols: # Auto retry if random connection error
        sesh.mount(protocol, requests.adapters.HTTPAdapter(max_retries=3))

    return sesh

# SSH -------------------------------------------------------------------------

class SSH(object):
    """ Create SSH cmd and tunnel objects """
    def __init__(self, user='ubuntu', port=6000, ip='', keyfile=''):
        self.user = user
        self.keyfile = keyfile
        self.port = port
        self.ip = ip
        self.machine = '{}@{}'.format(self.user, self.ip)
        self.cmd = ['ssh','-i', self.keyfile,'-ND','127.0.0.1:%s' % self.port,
                    '-o','StrictHostKeyChecking=no',self.machine]
        self.cmd_str = ' '.join(self.cmd)
    
    def open_tunnel(self):
        self.tunnel = subprocess.Popen(self.cmd, shell=False)

def generate_ssh_tunnels(ips, ports, keyfile):
    """ Generate SSH tunnels for each (IP, port) combination"""

    def generate_ssh_tunnel(ip, port, keyfile=keyfile):
        ssh_tunnel = SSH(ip=ip, port=port, keyfile=keyfile)
        subprocess.call(['chmod', '600', keyfile])
        print('{}'.format(ssh_tunnel.cmd_str))
        ssh_tunnel.open_tunnel()
        atexit.register(exit_handler, ssh_tunnel) # Always kill tunnels on exit

    return [generate_ssh_tunnel(ip, port) for ip, port in zip(ips, ports)]

def exit_handler(ssh):
    print('Killing: {} on port: {}'.format(ssh.machine, ssh.port))
    ssh.tunnel.kill()

# Parsing ----------------------------------------------------------------------

def strip_html_tags(string):
    """Strips HTML <tags>"""
    return re.sub('<[^<]+?>', '', string)

def has_captcha(soup):
    """Detect CAPTCHA appearance in soup"""
    return True if soup.find(text=re.compile('CAPTCHA')) else False

def get_html_language(soup):
    """Extract langauge from HTML tags"""
    try:
        language = soup.html.attrs['lang']
    except Exception:
        language = ''
    return language

def parse_hashtags(text):
    """Extract unique hashtags and strip surrounding punctuation"""
    hashtags = set([w for w in text.split() if w.startswith("#")])
    hashtags = [re.sub(r"(\W+)$", "", h, flags = re.UNICODE) for h in hashtags]
    return list(set(hashtags))

def parse_emojis(text):
    """Extract all emojis in a string"""
    return [emoji.demojize(e['emoji']) for e in emoji.emoji_lis(text)]

def extract_css(soup):
    """Extract embedded CSS """
    
    def split_style(style):
        if style.string:
            return style.string.replace('}', '}\n').split('\n')
        else:
            return None

    styles = soup.find_all('style')
    if styles:
        return sum(list(map(split_style, styles)), [])
    else:
        return None

def extract_html_json(data_fp, extract_to, id_col):
    """Save HTML to directory for viewing """
    os.makedirs(extract_to, exist_ok=True)
    data = pd.read_json(data_fp, lines=True)
    for idx, row in data.iterrows():
        fp = os.path.join(extract_to, row[id_col] + '.html') 
        with open(fp, 'wb') as outfile:
            outfile.write(row['html'])

# Sessions ---------------------------------------------------------------------

def get_sequential_duplicates(series): 
    """Returns a boolean indicating if previous entry has same value"""
    boolean = series.shift() == series
    return boolean if type(series) == pd.Series else boolean.all(axis=1)

def get_interrow_interval(series):
    """Returns the time difference between datetime entries in seconds"""
    return series.diff().dt.total_seconds()

def get_sessions(user, tvar='unixtime', dupe_col='', session_delimiter=30*60):
    """Add browsing session based on time delimiter
    
    Arguments:
        user {pd.DataFrame} -- Dataframe for a single user
    
    Keyword Arguments:
        tvar {str} -- Time stamp column to use (default: {'unixtime'})
        dupe_col {str} -- Optional, column to check for sequential duplicates
        session_delimiter {int} -- idle threshold in seconds (default: {30*60})
    
    Returns:
        pd.DataFrame -- Dataframe with added session columns
    """
    
    # Sort by visit time, calculate time diff
    user = user.sort_values(tvar).reset_index(drop=True)
    user['time_diff'] = get_interrow_interval(user[tvar])

    # Add sequential duplicates
    if dupe_col:
        user['seq_dupe'] = get_sequential_duplicates(user[dupe_col])
    
    # Reset index to get ordered int, cut on index if time from last action 
    # greater than set delimiter
    user = user.reset_index()
    user['bool_sesh'] = user.time_diff > session_delimiter
    # print(f'Number of search sessions: {user["bool_sesh"].sum()}')

    # Set cut points, include max and min manually as np.inf
    session_cut_points = [idx for idx, b in user['bool_sesh'].items() if b]
    session_cut_points = [-np.inf] + session_cut_points + [np.inf]
    
    # Make the cuts
    user['session'] = pd.cut(user['index'], bins=session_cut_points,
                             right=False, labels=False)

    # Mark session index (i.e. subunits)
    user['session_idx'] = user.groupby(
        (user['session'] != user['session'].shift(1)).cumsum()
    ).cumcount() + 1

    # Add latency (time_diff - from session data) as time elapsed on the page
    user['time_elapsed'] = user['time_diff'].shift(-1)

    # Remove process variables
    del user['index']
    del user['bool_sesh']

    return user

