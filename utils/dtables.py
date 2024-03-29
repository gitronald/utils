""" dtables : The python version of the R package dtables
"""

from . import utils

import os
import numpy as np
import pandas as pd
from functools import reduce

def neat_n(n): return f'{n:,.0f}'
def neat_p(p): return f'{round(p*100, 1)}%' if pd.notnull(p) else '-'

def dfshape(df):
    """A cleaner version of df.shape

    Args:
        df (pd.DataFrame): A dataframe

    Returns:
        str: formatted dataframe shape "n_rows | n_cols" 
    """
    return ' | '.join([f"{s:,}" for s in df.shape])


def dft(col, neat=True, dropna=True, sort_index=False, binned=False):
    """A descriptive frequencies table
    
    Arguments:
        col {str} -- A string indicating which column to use.
    
    Keyword Arguments:
        neat {bool} -- Format output (default: {True})
        dropna {bool} -- Drop null values (default: {True})
        sort_index {bool} -- Sort index of output (default: {False})
        binned {bool} -- Count binned values, log10 (default: {False})
    
    Returns:
        pd.DataFrame -- A dataframe with descriptive frequencies
    """

    if binned:
        col = binned_col(col)

    tab = pd.DataFrame({
        'n': col.value_counts(dropna=dropna),
        'p': col.value_counts(normalize=True, dropna=dropna)
    })
    tab = tab.sort_index() if sort_index else tab
    if neat:
        tab['n'] = tab['n'].apply(neat_n)
        tab['p'] = tab['p'].apply(neat_p)
    return tab


def describe(series):
    """Enhanced describe, featuring sem, median, sum, and null count
    
    Arguments:
        series {pd.Series} -- A pandas series to describe
    
    Returns:
        pd.DataFrame -- A dataframe with descriptive stats
    """
    keep_cols = ['count', 'mean', 'std', 'min', 'max']
    tab = series.describe(datetime_is_numeric=True).T
    tab = tab.reindex(keep_cols)
    
    try:
        tab['sem'] = series.sem()
        tab['median'] = series.median()
        tab['sum'] = series.sum()
        tab['num_null'] = series.isnull().sum()
        return tab
    except TypeError:
        return tab

def describe_multi(df, cols):
    """Describe multiple columns"""
    return df[cols].apply(describe).T.convert_dtypes()

def dnum(df_col, rnd=3):
    if df_col.dtype in [int, float]:
        return df_col.describe().round(rnd).to_frame().T
    else:
        return np.nan

def presentation_table(df):
    """Make a dataframe more presentable
    
    Arguments:
        df {pd.DataFrame} -- Dataframe to spruce up
    
    Returns:
        pd.DataFrame -- A neatified DataFrame
    """
    for c in df:
        if c == 'n' or c.startswith('n_'):
            df[c] = df[c].apply(neat_n)
        if c == 'p' or c.startswith('p_'):
            df[c] = df[c].apply(neat_p)
        if c.startswith('mean_'):
            df[c] = df[c].apply(lambda n: f'{n:.3f}')
    return df

def get_column_unique(fp, col):
    if os.path.exists(fp):
        try:
            df = utils.read_lines(fp, as_dataframe=True)
            data = set(df[col])
        except Exception as error:
            print("Error loading dataframe", error)
    else:
        data = {}
    
    print(f"Unique [{fp}|{col}]: {len(data):,}")
    return data


def join_dfs(df_list):
    """Joins a list of pd.DataFrame objects"""
    return reduce(lambda df_n,df_i: df_n.join(df_i), df_list)


def binned_col(col, 
               bins=[-0.1, 0, 1, 10, 100, 1000, 10000],
               labels=['0', '1', '2-10','11-100','101-1000','1000+']):
    """Get log-style binning of column by default"""
    n_bins = pd.cut(col, bins=bins, include_lowest=True)
    return n_bins


def pivot_unique(df, index, columns, values, margins=True):
    """Pivot table, returns nunique values by index and columns"""
    out = df.pivot_table(index=index, columns=columns, values=values,
                         aggfunc=lambda x: x.nunique(), margins=margins)
    return out


def get_top_label(df, cols):
    """Get column name for cell with highest value in row"""
    return df[cols].replace(0, np.nan).idxmax(axis=1)


# Descriptive Stats ------------------------------------------------------------


def get_cumsum_tab(col):
    """Get a cumulative sum table from a dataframe column

    Args:
        col (pd.Series): a column of values

    Returns:
        pd.DataFrame: dataframe containing cumulative sum of values and index
    """
    col = col.sort_values(ascending=False)
    df = col.cumsum().reset_index()
    df['n'] = range(1, col.shape[0]+1)
    df.drop('index', axis=1, inplace=True)
    df.columns = ['n_cumsum', 'n']
    df['p'] = df['n'] / col.shape[0]
    df['p_cumsum'] = df['n_cumsum'] / col.sum()
    
    return df

def groupby_value_counts(gb, col, prefix="n_", dropna=True, reset_index=True):
    """Get value counts for a column with a grouped DataFrame, e.g. by `serp_id`
    
    Args:
        gb (pd.DataFrameGroupBy): The grouped DataFrame
        col (str): The column to get value counts for
        prefix (str, optional): The prefix to add to the column names. Defaults to "n_".
        dropna (bool): Whether to drop nulls or not
        reset_index (bool): Whether to reset the index or not
    
    Returns:
        pd.DataFrame : DataFrame with value counts as `f'n_{factor}'` columns, 
        where `factor` is each unique value in the selected column.
    """
    counts = gb[col].value_counts(dropna=dropna).unstack().fillna(0).astype(int)
    counts.columns = [f"{prefix}_{c}" if prefix else c for c in counts]
    return counts.reset_index() if reset_index else counts

def get_masked_nunique(df, mask, unique):
    """ Get the number of unique values in a masked dataframe column

    Args:
        df (pd.DataFrame): The dataframe to operate on.
        mask (str): The mask column name.
        unique (str): The unique values column name.

    Returns:
        int: count of the unique values in the masked column
    """
    return 0 if not df[mask].any() else df[df[mask] == 1][unique].nunique()


def df_types(df, thresh=0, perc=True):
    # Get dtype of every cell in a column, not a fast operation
    types = df.apply(lambda col: col.apply(lambda r: type(r)).value_counts(perc))
    types = types.T.fillna(0)
    types.columns = [str(c).split("'")[1] for c in types.columns]

    # Get main columns type; type that composes > 50% of types
    main_types = types.apply(lambda col: col.apply(lambda r: r > 0.5), axis=1)

    # Get number of types per column
    types_binary = types.apply(lambda col: col.apply(lambda r: r > 0), axis=1)
    types['n_types'] = types_binary.sum(axis=1)
    
    types['type'] = main_types.apply(lambda col: col[col].index.iloc[0], axis=1)

    return types

def df_columns(df, type_details=True, head=3):
    # Get useful information about DataFrame columns
    columns_df = pd.DataFrame({
        'dtype': df.dtypes,
        'n_unique': df.apply(lambda col: col.nunique(), axis=0),
        'n_null': df.apply(lambda col: col.isnull().sum(), axis=0)
    })
    if type_details:
        columns_df = pd.concat([columns_df, df_types(df)], sort=True, axis=1)

    if head > 0:
        columns_df = pd.concat([columns_df, df.head(head).T], sort=True, axis=1)

    col_order = ['type', 'n_types', 'dtype', 'n_null', 'n_unique'] + list(range(head))
    return columns_df[col_order].sort_values('type')

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


def df_info(df, verbose=True, type_details=True, head=1, memory_usage='deep'):
    # Get a useful header of information about a DataFrame
    info = {
        'columns': f'{df.shape[1]:,}',
        'rows': f'{df.shape[0]:,}, {df.index._start} to {df.index._stop}',
        'memory_usage': humanbytes(df.memory_usage(deep=True).sum()),
    }
    columns_df = df_columns(df, type_details=type_details, head=head)
    if verbose:
        for info_var in ['memory_usage', 'rows', 'columns']:
            print(f'{info_var:>12s} : {info[info_var]}')
        print()
        print(columns_df)
    return (info, columns_df)
