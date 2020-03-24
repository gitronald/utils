""" General purpose functions
"""

import os
import re
import json
import random
import itertools
import pandas as pd
from string import ascii_letters, digits

pd.set_option('max.columns', None)  # Show all columns
pd.set_option('max_colwidth', 70)   # Max single column width
pd.set_option('display.width', 80)  # Expand display width

# Files ------------------------------------------------------------------------

def all_paths(dir, absolute=False):
    """Return all relative or absolute paths for a directory"""
    file_paths = []
    for folder, subs, files in os.walk(dir):
        for filename in files:
            fp = os.path.join(folder, filename)
            file_paths.append(os.path.abspath(fp) if absolute else fp)
    return file_paths

def humanbytes(size):
    """Return the given bytes as a human friendly KB, MB, GB, or TB string
    KB = 2**10 = 1024
    """
    power = 2**10
    n = 0
    power_name = {0 : '', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB'}
    while size > power:
        size /=  power
        n += 1
    return f'{round(size,2)} {power_name[n]}'


# Data ------------------------------------------------------------------------

def read_lines(fp, max_line=10**7):
    with open(fp, 'r') as infile:
        if '.txt' in fp:
            return [l.strip() for n, l in enumerate(infile) if n < max_line]
        elif '.json' in fp:
            return [json.loads(l.strip()) for n, l in enumerate(infile) if n < max_line]

def write_lines(iter_data, fp, fmode='a+', verbose=False):
    with open(fp, fmode) as outfile:
        if verbose: print(fp)
        if fp.endswith('.txt'):
            for data in iter_data:
                outfile.write(f'{data}\n')
        elif fp.endswith('.json'):
            for data in iter_data:
                outfile.write(f'{json.dumps(data)}\n')

def read_tsv(FP):
    return pd.read_csv(FP, sep='\t')

def write_tsv(df, fp, index=False, verbose=False):
    if verbose: print(fp)
    return df.to_csv(fp, sep='\t', index=index)

# Lists ------------------------------------------------------------------------

def unlist(nested_list):
    """Flatten a nested list"""
    return list(itertools.chain.from_iterable(nested_list))

def chunk_list(l, n, as_list=True):
    """Create a list or generator chunked to size n"""
    if as_list: return [l[i:i + n] for i in range(0, len(l), n)]
    else:       return (l[i:i + n] for i in range(0, len(l), n))

def zip_with_scalar(l, o, as_list=True):
    if as_list: return [(i, o) for i in l]
    else:       return ((i, o) for i in l)

# Strings ----------------------------------------------------------------------

def num_words(string, list_words=False):
    """Number of words in a string"""
    string = str(string) if type(string) != str else string
    words = re.findall(r'\w+', string)
    nwords = len(words)
    out_data = (nwords, words) if list_words else nwords
    return out_data

def split_by_spaces(s, n=2): return re.split('\s{%d,}' % n, s)
def get_between_brackets(s): return re.search('\[(.*?)\]', s).group(1)
def get_between_parentheses(s): return re.search('\((.*?)\)', s).group(1)
def get_list_pattern(l): return '|'.join([re.escape(s) for s in l])
def remove_digits(s): return "".join([i for i in s if not i.isdigit()]).strip()

def alphanumerics():
    """Generate upper and lowercase letters and digits"""
    return list(ascii_letters + digits)

def random_string(length=12):
    """Generate a random string of alphanumerics"""
    return ''.join(random.choice(alphanumerics()) for i in range(length))
    
def make_id():
    """Generate hash ID based on current datetime"""
    return sha224(now().encode('utf-8')).hexdigest()

def salt_id(s, salt='saltytears_forthesultan'):
    """Generate salted ID based on input string"""
    return sha224((salt+s).encode('utf-8')).hexdigest()

def print_line(word='', length=80):
    """Print a word followed by a line to a specified length (default=80)"""
    if word: print(word + ' ' + ''.join(['-'] * (80 - len(word))))
    else:    print(''.join(['-']*length))

def write_latex_figure(caption, caption_title, fig_fp, fig_ref, latex_fp=''):
    """Save figure details to latex inputable file"""
    latex = '\n'.join([
        "\\begin{figure}[t]",
        "\\centering",
        "\\includegraphics[width=1.0\\columnwidth]{"+fig_fp+"}",
        "\\caption{\\textbf{"+caption_title+"} "+caption+"}",
        "\\label{fig:"+fig_ref+"}",
        "\\end{figure}"
    ])
    if latex_fp:
        assert latex_fp.endswith('.tex'), "Filepath not to latex (.tex)"
        with open(latex_fp, 'w') as outfile:
            print(f'Writing latex figure: {latex_fp}')
            outfile.write(latex)
    else:
        return latex

