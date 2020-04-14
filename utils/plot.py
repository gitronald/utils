""" Plotting designs
"""

import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt

TINY_SIZE = 6
SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

font = {'family' : 'sans', # controls default text sizes
        'weight' : 'regular',
        'size'   : SMALL_SIZE}
plt.rc('font', **font)

plt.rc('font', size=SMALL_SIZE)          
plt.rc('axes', titlesize=MEDIUM_SIZE)    # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=TINY_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# Seaborn Keyword Args ---------------------------------------------------------

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

# Plots -----------------------------------------------------------------------

def quad_plot(data, xlist, ylist, label_colors, label_order):
    """ Quad plot: Each column shares x axis, each row shares y axis
    """

    strip_kws = dict(jitter=True, size=1.75, alpha=0.7)
    box_kws = dict(linewidth=0.75, color='whitesmoke', width=.5, fliersize=0)

    gridspec_kw={'height_ratios':[1,2.2]}
    fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(8,3), 
                           gridspec_kw=gridspec_kw)

    # Separate shared axes
    set_share_axes(axs[:,0], sharex=True)
    set_share_axes(axs[:,1], sharex=True)
    set_share_axes(axs[0,:], sharey=True)
    set_share_axes(axs[1,:], sharey=True)

    for yidx, y in enumerate(ylist): # Each fig column
        for xidx, x in enumerate(xlist): # Each fig row 
        
            ax = axs[xidx, yidx]
            sns.boxplot(y=x, x=y, data=data, ax=ax, **box_kws)
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

# Colors ----------------------------------------------------------------------

"""From https://bsou.io/posts/color-gradients-with-python"""
hex_dict = {}
hex_dict.update(sns.colors.xkcd_rgb)
hex_dict.update(mpl.colors.cnames)

def hex_to_RGB(hex):
    ''' "#FFFFFF" -> [255,255,255] '''
    # Pass 16 to the integer function for change of base
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]

def RGB_to_hex(RGB):
    ''' [255,255,255] -> "#FFFFFF" '''
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "#"+"".join(["0{0:x}".format(v) if v < 16 else
            "{0:x}".format(v) for v in RGB])

def color_dict(gradient):
    ''' Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on 
    '''
    return {"hex":[RGB_to_hex(RGB) for RGB in gradient],
      "r":[RGB[0] for RGB in gradient],
      "g":[RGB[1] for RGB in gradient],
      "b":[RGB[2] for RGB in gradient]}

def linear_gradient(start_hex, finish_hex="#FFFFFF", n=10, hex_dict=hex_dict):
    ''' returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    inlcuding the number sign ("#FFFFFF") 
    '''

    # Convert names to hex
    if not start_hex.startswith('#'):
        assert start_hex in hex_dict, "Unknown color name check hex dict"
        start_hex = hex_dict[start_hex]

    if not finish_hex.startswith('#'):
        assert finish_hex in hex_dict, "Unknown color name check hex dict"
        finish_hex = hex_dict[finish_hex]

    # Starting and ending colors in RGB form
    s = hex_to_RGB(start_hex)
    f = hex_to_RGB(finish_hex)
    
    # Initilize a list of the output colors with the starting color
    RGB_list = [s]
    
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
    
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [int(s[j] + (float(t)/(n-1))*(f[j]-s[j])) for j in range(3)]
        
        # Add it to our list of output colors
        RGB_list.append(curr_vector)

    return color_dict(RGB_list)
