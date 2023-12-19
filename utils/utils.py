""" General purpose functions
"""

import os
import re
import bz2
import sys
import json
import random
import itertools
import pandas as pd
from hashlib import sha224
from string import ascii_letters, digits

from .timers import now

# Shell ------------------------------------------------------------------------

def in_notebook() -> bool:
    """Returns `True` if running in IPython kernel else `False`"""
    return 'ipykernel' in sys.modules


# Files ------------------------------------------------------------------------

def all_paths(dir, absolute=False):
    """Return all relative or absolute paths for a directory"""
    file_paths = []
    for folder, subs, files in os.walk(dir):
        for filename in files:
            fp = os.path.join(folder, filename)
            file_paths.append(os.path.abspath(fp) if absolute else fp)
    return file_paths


# Data ------------------------------------------------------------------------

def read_lines(fp: str, 
               max_line: int = 1e12, 
               as_dataframe: bool = False, 
               filetype: str = ''):
    """Read lines from file

    Args:
        fp (str): filepath
        max_line (int, optional): Maximum lines to read in. Defaults to 1e12.
        as_dataframe (bool, optional): Return as dataframe. Defaults to False.
        filetype (str, optional): Select filetype ending. Automatic by default.

    Raises:
        ValueError: If filepath not found

    Returns:
        list/pd.DataFrame: The loaded list or dataframe
    """

    if fp.endswith('.csv') or filetype == 'csv':
        return pd.read_csv(fp)

    elif fp.endswith('.tsv')  or filetype == 'tsv':
        return pd.read_csv(fp, sep='\t')

    elif fp.endswith('.txt') or filetype == 'txt':
        with open(fp, 'r') as infile:
            lines = [l.strip() for n, l in enumerate(infile) if n < max_line]
            return pd.DataFrame(lines) if as_dataframe else lines

    elif fp.endswith('.json') or filetype == 'json':
        with open(fp, 'r') as infile:
            lines = [json.loads(l.strip()) for n, l in enumerate(infile) \
                     if n < max_line]
            return pd.DataFrame(lines) if as_dataframe else lines

    elif fp.endswith('.json.bz2')  or filetype == 'json.bz2':
        with bz2.open(fp, "rt") as infile:
            lines = [json.loads(l.strip()) for n, l in enumerate(infile) \
                     if n < max_line]
            return pd.DataFrame(lines) if as_dataframe else lines
    
    else:
        raise ValueError('Filepath not recognized')               

def write_lines(iter_data, fp, fmode='a+', verbose=False):
    with open(fp, fmode) as outfile:
        if verbose: print(fp)
        if fp.endswith('.txt'):
            for data in iter_data:
                outfile.write(f'{data}\n')
        elif fp.endswith('.json'):
            for data in iter_data:
                outfile.write(f'{json.dumps(data)}\n')

def read_tsv(fp):
    """Read a TSV to dataframe"""
    return pd.read_csv(fp, sep='\t')

def write_tsv(df, fp, index=False, verbose=False):
    """Write a dataframe to a TSV"""
    if verbose: print(fp)
    return df.to_csv(fp, sep='\t', index=index)

def read_json(fp):
    """Read in a json file (not lines)"""
    with open(fp, 'r') as infile:
        return json.load(infile)

def write_sql_row(data, table, conn):
    """Write a dict `data` as a row in `table` via SQL connection `conn`

    Arguments:
        data (dict) -- A dictionary to insert as a row.
        table (str) -- The name of the table.
        conn -- A connection to a SQL database.
    """
    row = pd.DataFrame(data, index=[0])
    row.to_sql(table, con=conn, index=False, if_exists='append')
    # cursor = conn.cursor()
    # columns = ', '.join("`"+str(x).replace('/','_')+"`" for x in data.keys())
    # values = ', '.join("'"+str(x).replace('/','_')+"'" for x in data.values())

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

def hash_id(s): 
    """Generate hash ID based on decoded string input"""
    return sha224(s.encode('utf-8')).hexdigest()

def make_id():
    """Generate hash ID based on current datetime"""
    return sha224(now().encode('utf-8')).hexdigest()

def salt_id(s, salt='saltytears_forthesultan'):
    """Generate salted ID based on input string"""
    return sha224((salt+s).encode('utf-8')).hexdigest()

def str_to_id(s):
    replace = str.maketrans({
        " ": "_",  
        ",": "_",  
        "'": "",
        '"': ""
    })
    return s.lower().translate(replace)

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

