# ver = '2022-5-28-1'

import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, ScalarFormatter
import numpy as np


def plot_close():
    plt.close('all')


def plot_data_np_timestamp_multicolumn_header(data_list, timestamp, header_list):
    column_list = list(range(0, data_list.shape[1]))
    figure_list = []

    for i in column_list:
        fig = plt.figure(i)
        figure_list.append(fig)
        # figure_list[i] = plt.figure(i)
        if header_list is not None:
            plt.title(str(header_list[i]))
        # if timestamp is not None:
        #     plt.plot(timestamp, data_list[:, i])
        # else:
        #     plt.plot(data_list[:, i])
        plt.plot(timestamp, data_list[:, i])

        # Axes in scientific notation
        # plt.gca().xaxis.set_major_formatter(ScalarFormatter())
        # plt.ticklabel_format(axis="x", style="sci", scilimits=(0, 0))
        # plt.gca().yaxis.set_major_formatter(ScalarFormatter())
        # plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

        # plt.gca().axes.yaxis.set_ticklabels([])

        # # Scale axes major and minor ticks
        # plt.gca().xaxis.set_major_locator(MultipleLocator(20))
        # plt.gca().xaxis.set_minor_locator(MultipleLocator(5))
        # plt.gca().yaxis.set_major_locator(MultipleLocator(20))
        # plt.gca().yaxis.set_minor_locator(MultipleLocator(5))

        # Axes labels
        # if header_list is not None:
        #     plt.xlabel(header_list[0])
        #     plt.ylabel(header_list[i])
        # plot_show_plots(plt.figure(i))
        # figure_list[i].show()
        fig.show()
