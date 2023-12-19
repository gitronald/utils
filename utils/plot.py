""" Plotting designs
"""

import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt


# ------------------------------------------------------------------------------
# Plot Settings - Font Size

def set_font_config():
    """Set matplotlib fonts config for PDF publication"""

    # Output fonts in pdf as text not shape
    mpl.rcParams['pdf.fonttype'] = 42
    mpl.rcParams['ps.fonttype'] = 42

    TINY_SIZE = 6
    SMALL_SIZE = 7
    LARGE_SIZE = 8

    font_settings = {
        'font': {
            'family': 'sans-serif',
            'weight': 'regular',
            'size': SMALL_SIZE,
        },
        'axes': {
            'titlesize': SMALL_SIZE, # fontsize of the axis title
            'labelsize': SMALL_SIZE, # fontsize of the x and y labels
        },
        'xtick': {'labelsize': TINY_SIZE},   # fontsize of the tick labels
        'ytick': {'labelsize': TINY_SIZE},   # fontsize of the tick labels
        'legend': {'fontsize': TINY_SIZE},   # legend fontsize
        'figure': {'titlesize': LARGE_SIZE}  # fontsize of the figure title
    }

    # Set default font size and family
    for name, settings in font_settings.items():
        plt.rc(name, **settings)

    sns.set_style("whitegrid")

# ------------------------------------------------------------------------------
# Plot Settings - Figure Formatting

strip_kws = dict(
    jitter=True, 
    size=1.5, 
    alpha=0.7
)

box_kws = dict(
    linewidth=0.75, 
    color='whitesmoke', 
    width=.5, 
    fliersize=0
)

pointplot_kws = dict(
    scale=0.5,
    alpha=0.8,
    errwidth=1,
    dodge=0.2
)

heatmap_kws_proportion = dict(
    annot=True,
    annot_kws={'size':8}, fmt='.2f',
    cmap='bone_r',
    cbar=True,
    cbar_kws={
        'label': '',
        'orientation': 'vertical',
        'pad': 0.01,
        'shrink': 1,
        'ticks': [0, 1],
        'format': '%.1f'
    },
    linewidths=0.1,
    linecolor='whitesmoke',
    vmax=1,
    vmin=0
)

# ------------------------------------------------------------------------------
# Plot Data

def get_binning(values, num_bins = 15, log_binning = True, is_pmf = True):

    # We need to define the support of our distribution
    lower_bound = min(values)
    upper_bound = max(values)
    
    # And the type of binning we want
    if log_binning:
        lower_bound = np.log10(lower_bound)
        upper_bound = np.log10(upper_bound)
        bins = np.logspace(lower_bound,upper_bound,num_bins+1, base = 10)
    else:
        bins = np.linspace(lower_bound,upper_bound,num_bins+1)
    
    # Then we can compute the histogram using numpy
    if is_pmf:
        y, __ = np.histogram(values, bins = bins, density=False)
        p = y/float(y.sum())
        
    else:
        p, __ = np.histogram(values, bins = bins, density=True)
    
    # Now, we need to compute for each y the value of x
    x = bins[1:] - np.diff(bins)/2.0    
    
    x = x[p>0]
    p = p[p>0]

    return x, p


# ------------------------------------------------------------------------------
# Plot Adjustments

def remove_yaxis_ticks(ax, major=True, minor=True):
    if major:
        for tic in ax.yaxis.get_major_ticks():
            tic.tick1line.set_visible(False)
            tic.tick2line.set_visible(False)
    if minor:
        for tic in ax.yaxis.get_minor_ticks():
            tic.tick1line.set_visible(False)
            tic.tick2line.set_visible(False)


def remove_xaxis_ticks(ax, major=True, minor=True):
    if major:
        for tic in ax.xaxis.get_major_ticks():
            tic.tick1line.set_visible(False)
            tic.tick2line.set_visible(False)
    if minor:
        for tic in ax.xaxis.get_minor_ticks():
            tic.tick1line.set_visible(False)
            tic.tick2line.set_visible(False)


def reorder_legend(handles=None, labels=None, order=None, unique=False):
    """Reorder legend handles and labels with ordered list

    Credit: @CPBL
    https://stackoverflow.com/questions/22263807/how-is-order-of-items-in-matplotlib-legend-determined/35926913#35926913

    Args:
        handles (list): handles obtained via ax.get_legend_handles_labels()
        labels (list): labels obtained via ax.get_legend_handles_labels()
        order (list): list of labels in desired order, strings must match
        unique (bool): option to drop duplicates and keep first label instance

    Returns:
        tuple: the sorted handles and labels objects
    """

    # Sort both labels and handles by labels
    labels, handles = zip(*sorted(zip(labels, handles), key=lambda l: l[0]))
    if order is not None:
        # Sort according to a given list (not necessarily complete)
        keys = dict(zip(order,range(len(order))))
        labels, handles = zip(*sorted(zip(labels, handles), key=lambda l, 
                                      keys=keys: keys.get(l[0], np.inf)))

    # Keep only the first of each handle
    if unique: 
        labels, handles= zip(*unique_everseen(zip(labels,handles), key=labels))
    return handles, labels


def unique_everseen(seq, key=None):
    seen = set()
    seen_add = seen.add
    return [x for x,k in zip(seq,key) if not (k in seen or seen_add(k))]


def set_share_axes(axs, target=None, sharex=False, sharey=False):
    """Set which plt.subplots rows or columns have shared x or y
    
    # Example
    fig, axs = plt.subplots(5, 4)
    set_share_axes(axs[:,:2], sharex=True)
    set_share_axes(axs[:,2:], sharex=True)

    """
    if target is None:
        target = axs.flat[0]
    # Manage share using grouper objects
    for ax in axs.flat:
        if sharex:
            target._shared_x_axes.join(target, ax)
        if sharey:
            target._shared_y_axes.join(target, ax)
    # Turn off x tick labels and offset text for all but the bottom row
    if sharex and axs.ndim > 1:
        for ax in axs[:-1,:].flat:
            ax.xaxis.set_tick_params(which='both', labelbottom=False, labeltop=False)
            ax.xaxis.offsetText.set_visible(False)
    # Turn off y tick labels and offset text for all but the left most column
    if sharey and axs.ndim > 1:
        for ax in axs[:,1:].flat:
            ax.yaxis.set_tick_params(which='both', labelleft=False, labelright=False)
            ax.yaxis.offsetText.set_visible(False)


# ------------------------------------------------------------------------------
# Plot Generators

def quad_plot(data, xlist, ylist, 
        label_colors, 
        label_order,
        figsize=(8,3),
        strip_kws=strip_kws,
        box_kws=box_kws):
    """ Quad plot: Each column shares x axis, each row shares y axis
    """

    gridspec_kw={'height_ratios':[1,2.2]}
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=figsize, 
                           gridspec_kw=gridspec_kw)

    # Separate shared axes
    set_share_axes(axs[:,0], sharex=True)
    set_share_axes(axs[:,1], sharex=True)
    set_share_axes(axs[0,:], sharey=True)
    set_share_axes(axs[1,:], sharey=True)

    for yidx, y in enumerate(ylist): # Each fig column
        for xidx, x in enumerate(xlist): # Each fig row 
        
            ax = axs[xidx, yidx]
            sns.boxplot(y=x, x=y, data=data, ax=ax, 
                        order=label_order[x], 
                        **box_kws)
            sns.stripplot(y=x, x=y, data=data, ax=ax,
                          palette=label_colors[x],
                          order=label_order[x], 
                          **strip_kws)

            if xidx != len(xlist) - 1:
                # Remove xtick marks until last row
                remove_xaxis_ticks(ax)
                ax.tick_params(bottom=False, labelbottom=False)
                ax.set(xlabel='')

            if yidx != 0:
                # Remove xtick marks until last row
                remove_yaxis_ticks(ax)
                ax.tick_params(left=False, labelleft=False)
                ax.set(ylabel='')

    # Styling
    for idx, ax in enumerate(axs.flatten()):
        ax.grid(b=True, axis='x', which='major', color='#E7E8E8', linestyle='--', linewidth=0.5)
        for spine in ['top', 'right']:
            ax.spines[spine].set_visible(False)
            if idx in [0, 1]:
                ax.spines['bottom'].set_visible(False)
    
    return fig, axs

def plot_bias_distribution(dist, ax, color='#3B3838', label='',
                           linestyle='-', alpha=1, shade=True):
    ax = sns.kdeplot(dist, color=color, shade=False, alpha=alpha,
                     ax=ax,linestyle=linestyle, linewidth=1.2, label=label)
    
    if shade:
        # Extract coordinates
        line = ax.get_lines()[-1]
        x, y = line.get_data()

        # Shade regions by selecting those points and calling ax.fill_between:
        mask = x >= -0.005
        _x, _y = x[mask], y[mask]
        ax.fill_between(_x, y1=_y, alpha=0.5, facecolor='red')
        mask = x <= 0.01
        _x, _y = x[mask], y[mask]
        ax.fill_between(_x, y1=_y, alpha=0.5, facecolor='cornflowerblue')
    
    # Style
    ax.set(xlim=(-1,1))#, ylim=(0,max(y)))
    # for spine in ['top', 'right']:
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set(color='#DDDEDE', alpha=0.75, linewidth=0.75)
    ax.legend().remove()
    ax.tick_params(axis='x')
    ax.axvline(x=0, color='#3B3838', alpha=0.7, linewidth=1.2)
    ax.set_xticklabels(['-1', '', '-0.5', '', '0', '', '0.5', '', '1'])
    ax.grid(b=True, axis='both', which='major', color='#DDDEDE', alpha=0.75, linewidth=0.6)
    
    return ax
