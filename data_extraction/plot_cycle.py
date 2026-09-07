

"""
Type details about the function here
"""
def plot_cycle(x_data, y_data, x_axis_title, y_axis_title, label, color, ax, marker, linestyle, yerr=None, markersize=6, capsize=4, elinewidth=1, axis_font=12):
    ax.set_xlabel(x_axis_title, fontsize=axis_font)
    ax.set_ylabel(y_axis_title, fontsize=axis_font)

    if yerr is not None:
        ax.errorbar(
            x_data,
            y_data,
            yerr=yerr,
            label=label,
            color=color,
            marker=marker,
            linestyle=linestyle,
            capsize=capsize,
            elinewidth=elinewidth,
            markersize=markersize
        )
    else:
        ax.plot(x_data, y_data, label=label, color=color, marker=marker, linestyle=linestyle, markersize=markersize)
