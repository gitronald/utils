""" dtables : The python version of the R package dtables
"""

import pandas as pd

def neat_n(n): return f'{n:,}'
def neat_p(p): return f'{round(p*100, 1)}%' if pd.notnull(p) else '-'

def dft(col, neat=True, dropna=True, sort_index=False):
    """A descriptive frequencies table
    
    Arguments:
        col {str} -- A string indicating which column to use.
    
    Keyword Arguments:
        neat {bool} -- Format output (default: {True})
        dropna {bool} -- Drop null values (default: {True})
        sort_index {bool} -- Sort index of output (default: {False})
    
    Returns:
        pd.DataFrame -- A dataframe with descriptive frequencies
    """
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
    tab = series.describe().T[keep_cols]
    try:
        tab['sem'] = series.sem()
        tab['median'] = series.median()
        tab['sum'] = series.sum()
        tab['num_null'] = series.isnull().sum()
        return tab
    except TypeError:
        return tab

def dnum(df_col, rnd=3):
    if df_col.dtype in [int, float]:
        return df_col.describe().round(rnd).to_frame().T
    else:
        return pd.np.nan

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

# Descriptive Stats ------------------------------------------------------------

def groupby_value_counts(gdf, col, add_prefix=True):
    """Get value counts for a column with a grouped DataFrame, e.g. by `serp_id`
    
    Args:
        gdf (groupby): A dataframe grouped by a key
        col (str): The column to get value counts for
    
    Returns:
        pd.DataFrame : DataFrame with value counts as `f'n_{factor}'` columns, 
        where `factor` is each unique value in the selected column.
    """
    count_df = gdf[col].value_counts().unstack()
    colnames = [f"n_{c}" if add_prefix else c for c in count_df.columns]
    count_df.columns = colnames
    return count_df.fillna(0).astype(int).reset_index()


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
    
    types['type'] = main_types.apply(lambda col: col[col].index.item(), axis=1)

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

