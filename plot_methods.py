# ver = '2022-5-28-1'

import matplotlib.pyplot as plt


def plot_close():
    plt.close('all')


def plot_data_np_timestamp_multicolumn_header(data_list, timestamp, header_list, include_title, title):
    column_list = list(range(0, data_list.shape[1]))
    figure_list = []

    for i in column_list:
        fig = plt.figure(i)
        figure_list.append(fig)
        # figure_list[i] = plt.figure(i)
        if header_list is not None:
            plt.title(str(header_list[i]))
        plt.plot(timestamp, data_list[:, i])
        if include_title:
            plt.title(title)
        fig.show()


def plot_data_np_timestamp_multicolumn_header_plot_overlap(data_list, timestamp, legend, include_title, title):
    column_list = list(range(0, data_list.shape[1]))
    fig = plt.figure()

    if legend is None:
        for i in column_list:
            plt.plot(timestamp, data_list[:, i])
            if include_title:
                plt.title(title)
            fig.show()
    else:
        for i in column_list:
            plt.plot(timestamp, data_list[:, i], label=legend[i])
            plt.legend(loc='lower right')
            if include_title:
                plt.title(title)
            fig.show()
