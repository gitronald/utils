""" stats: A useful collection of statistics utilities
"""

import pandas as pd
import scipy.stats as st
import statsmodels.stats.weightstats as weight_st
from statsmodels.stats.contingency_tables import mcnemar
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.sandbox.stats.multicomp import multipletests
from collections import OrderedDict

from . import dtables
from . import utils

def kruskal_test_multi(data, metrics, groups, details=True):
    
    for metric in metrics:
        all_df = dtables.describe(data[metric])
        s = f"Mean {metric}: {all_df['mean']:,.1f} (SD = {all_df['std']:,.1f})"
        print(s)

        for group in groups:

            utils.print_line()
            print(f'Group: {group}')
            print(f'Metric: {metric}')

            if details:
                tab = data.groupby(group)[metric]\
                        .apply(dtables.describe)\
                        .unstack().round(3)
                print(f'{tab}\n')

            X, p = kruskal_test(data, group=group, metric=metric, 
                                fmt=True, nan_policy='omit')
            print(f'Krusukal-Wallis [KW] $X^{2} = {X}$; $P = {p}$)')
            print()

def paired_ttest(df, var1, var2, root='all', date=''):
    """Paired T-test on two columns in a pd.DataFrame"""
    overall = {}
    if root != 'all':
        df = df[df.root==root]
    if date != '':
        df = df[df.date==date]
    
    t, p = st.ttest_rel(df[var1], df[var2], 
                        nan_policy='omit')
    overall = OrderedDict([('root', root), 
               (var1, df[var1].mean()), 
               (var2, df[var2].mean()), 
               ('effect_size', df[var2].mean()-df[var1].mean()),
               ('t', t),
               ('P', p)])
    return overall

def get_median_category(df, group, category):
    df = df.groupby(group)[category].apply(lambda x: x.value_counts()[:1]).reset_index()
    return df.set_index(group).drop(category, axis=1).rename(columns={'level_1':'category'}).reset_index()

def kruskal_test(data, group, metric, fmt=False, nan_policy='raise'):
    groups = {key:value for key, value in data.groupby(group)[metric]}
    X, p = st.kruskal(*groups.values(), nan_policy=nan_policy)
    if fmt:
        return '{:.3f}'.format(X), '{:.4f}'.format(p) #p_value_sig(p)
    else:
        return {'chi':X, 'P':p} 

def mannw_test(data, group, metric, fmt=False):
    groups = {key:value for key, value in data.groupby(group)[metric]}
    U, p = st.mannwhitneyu(*groups.values())
    if fmt:
        return '{:.3f}'.format(U), '{:.4f}'.format(p) #p_value_sig(p)
    else:
        return {'U':U, 'P':p}

def spearmanr(data, metric1, metric2, fmt=False, nan_policy='omit'):
    rho, p = st.spearmanr(data[metric1], data[metric2], nan_policy=nan_policy)
    if fmt:
        return metric1, metric2, '{:.3f}'.format(rho), p_value_sig(p)
    else:
        return {'rho':rho, 'p':p}

def nonparametric_sig_test(data, group, metric):
    groups = {key:value for key, value in data.groupby(group)[metric]}
    ngroups = len(groups.keys())
    if ngroups == 2:
        data = mannw_test(df, group, metric)
        out_data = OrderedDict([
            ('group', group), ('U', data['U']), ('p', data['p'])
        ])
        
    else:
        data = kruskal_test(df, group, metric)
        out_data = OrderedDict([
            ('group',idx), ('chi', data['X']), ('p', data['p'])
        ])
    return out_data

def mcnemar_test(data, group1, group2):
    xtab = pd.crosstab(data[group1], data[group2])
    stats = mcnemar(xtab.as_matrix())
    output = {}
    output['pvalue'] = stats.pvalue
    output['chi2'] = stats.statistic
    return xtab, output

# def z_test():
#     z, p = proportions_ztest([standard, incognito], [15747, 15747], 0, alternative='two-sided')
#     compare_data_z.loc[idx, 'z'] = round(z, 3)
#     compare_data_z.loc[idx, 'p'] = utils.p_value_sig(p) # round(p, 3) 

def p_value_sig(p_val):
    if p_val < 0.001:
        return '***'
    elif p_val < 0.01:
        return '**'
    elif p_val < 0.05:
        return '*'
    else:
        return ''
    
    
import numpy as np
from scipy import stats

def pearsonr_ci(data, x, y, alpha=0.05, filterna=True):
    ''' Calculate Pearson correlation along with the confidence interval using scipy and numpy. See (https://zhiyzuo.github.io/Pearson-Correlation-CI-in-Python/)
    
    Parameters
    ----------
    x, y : iterable object such as a list or np.array
      Input for correlation calculation
    alpha : float
      Significance level. 0.05 by default
    Returns
    -------
    r : float
      Pearson's correlation coefficient
    pval : float
      The corresponding p value
    lo, hi : float
      The lower and upper bound of confidence intervals
    '''

    if filterna:
        mask = ((~pd.isnull(data[x])) & (~pd.isnull(data[y])))
        r, p = stats.pearsonr(data[mask][x],data[mask][y])
    else:
        r, p = stats.pearsonr(data[x],data[y])

    r_z = np.arctanh(r)
    se = 1/np.sqrt(data[x].size-3)
    z = stats.norm.ppf(1-alpha/2)
    lo_z, hi_z = r_z-z*se, r_z+z*se
    lo, hi = np.tanh((lo_z, hi_z))
    return {'r':r, 'p':p, 'ci_min':lo, 'ci_max':hi}