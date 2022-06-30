# ver = '2022-5-10-1'

import plot_methods as pl
import numpy as np
from constants import *
import filename_methods as fm
from tkinter import messagebox


class SessionProcessCSV:
    def __init__(self, user_entry, session_log, textbox, session_option):
        self.user_entry = user_entry
        self.session_log = session_log
        self.textbox = textbox
        self.session_option = session_option

        self.rows_to_display = []
        self.data_raw = []
        self.data_n_columns = 0
        self.data_n_rows = 0
        self.data_requested_np = None
        self.data_requested_timestamp_np = None
        self.data_parsed = []
        self.column_choice_list = []
        self.timestamps = []
        self.header_list = []
        self.header_list_np = np.empty((0, 0))
        self.data_end_index = 0
        self.timestamps_np = np.empty((0, 0))

        self.data_valid = None
        self.figure_list = []
        self.figures_valid = None

        if self.session_option is OPTION_PEAK_FILE:
            self.peak_data()

        elif self.session_option is OPTION_PROCESS_FILE:
            self.process_data()

    def load_and_peak(self):
        # Read file
        message = "Reading File\n"
        message_colour = "brown"
        self.session_log.write_textbox(message, message_colour)

        # Construct file name
        file_fullname = fm.FileNameMethods.build_file_name_full(self.user_entry.file_location,
                                                                self.user_entry.file_name, self.user_entry.file_suffix)

        # Read file, parse data
        with open(file_fullname, 'r') as f:
            self.data_raw = f.readlines()
            for row in self.data_raw:
                # Remove spaces and '\n'. Use strip() or: self.data_parsed.append(row.replace("\n", ""))
                row = row.strip()
                # Parse elements using delimiter
                if self.user_entry.read_delimiter_type == DELIMITER_TYPE_COMMA:
                    self.data_parsed.append(row.split(','))
                elif self.user_entry.read_delimiter_type == DELIMITER_TYPE_TAB:
                    self.data_parsed.append(row.split('\t'))

        # Get dimensions of data file
        self.data_n_rows = len(self.data_parsed)
        self.data_n_columns = len(self.data_parsed[self.user_entry.data_start_row_index])

        self.rows_to_display = []
        # Display first rows of file on the textbox
        for row in range(0, self.user_entry.n_rows_to_peak):
            self.rows_to_display.append('Row-' + str(row) + ':\n' + str(self.data_parsed[row]) + '\n\n')

        self.textbox_update(self.rows_to_display)

    def peak_data(self):
        self.close_plots()
        self.load_and_peak()

    def process_data(self):
        self.close_plots()
        self.load_and_peak()

        # Check user entry for length of data to read
        # If entry is default (0), then read all file
        if self.user_entry.data_end_row_index == 0:
            self.data_end_index = self.data_n_rows - 1
        elif self.user_entry.data_end_row_index > self.data_n_rows - 1:
            # self.data_end_index = self.data_n_rows
            message = "Number of Rows Requested Exceeds Data File Size\n" + "Rows in file = " +  \
                      str(self.data_n_rows) + '\n'
            message_colour = 'red'
            self.session_log.write_textbox(message, message_colour)
            messagebox.showerror("Error", message)
            return
        else:
            self.data_end_index = self.user_entry.data_end_row_index

        print("::data_end_index:", self.data_end_index)
        print("::data_n_rows:", self.data_n_rows)

        # Update session log
        message = "Data File Rows: " + str(self.data_n_rows) + '\n'
        message_colour = "blue"
        self.session_log.write_textbox(message, message_colour)

        message = "Data File Columns: " + str(self.data_n_columns) + '\n'
        message_colour = "blue"
        self.session_log.write_textbox(message, message_colour)

        message = "Index of last row to read: " + str(self.data_end_index) + '\n'
        message_colour = "blue"
        self.session_log.write_textbox(message, message_colour)

        message = "Number of rows to read: " + str(self.data_end_index - self.user_entry.data_start_row_index + 1) + '\n'
        message_colour = "blue"
        self.session_log.write_textbox(message, message_colour)

        # # Get column headers
        # self.header_list = self.data_parsed[self.user_entry.header_row_index]

        # Extract column list
        if self.user_entry.column_choice_option == COLUMNS_ALL:
            self.column_choice_list = list(range(0, self.data_n_columns))
        else:
            self.column_choice_list = self.user_entry.column_choice_list

        print("::column_choice_list: ", self.column_choice_list)

        message = 'Columns to Process: ' + str(self.column_choice_list) + '\n'
        colour = 'blue'
        self.session_log.write_textbox(message, colour)

        # Check column_choice_list is valid, requested columns are within file size
        columns_to_process_is_valid = not any((column_index > self.data_n_columns - 1) for column_index in self.column_choice_list)
        print("::columns_to_process_is_valid: ", columns_to_process_is_valid)

        if columns_to_process_is_valid is not True:
            message = 'Requested columns are out of range\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            return

        # Extract requested rows
        data_requested = self.data_parsed[self.user_entry.data_start_row_index: self.data_end_index + 1]
        # Convert list to numpy array
        self.data_requested_np = np.array(data_requested)
        # Convert blank data to zeros
        self.data_requested_np = np.where(self.data_requested_np == '', 0, self.data_requested_np)
        # Convert string to float
        self.data_requested_np = self.data_requested_np.astype(np.float)

        # Extract timestamps
        if self.user_entry.timestamp_extract == 1:
            self.timestamps = self.data_requested_np[:, 0]
        else:
            self.timestamps = list(range(0, self.data_end_index - self.user_entry.data_start_row_index + 1))
        # print("SG Test self.timestamps: ", self.timestamps[0:20])

        self.timestamps_np = np.empty((1, 1))
        self.timestamps_np = np.array(self.timestamps)
        self.timestamps_np = np.reshape(self.timestamps_np, (-1, 1))

        # Extract requested columns
        data_requested = self.data_requested_np
        self.data_requested_np = data_requested[:, self.column_choice_list]

        # Add timestamps
        self.data_requested_timestamp_np = np.concatenate((self.timestamps_np, self.data_requested_np), axis=1)

        # Extract headers
        if self.user_entry.header_include == HEADER_INCLUDE:
            self.header_list = self.data_parsed[self.user_entry.header_row_index]
            self.header_list_np = np.array(self.header_list)

        # Plot data if requested
        if self.user_entry.action == PROCESS_AND_PLOT:
            self.plot_data()

            if self.figure_list is not None:
                self.figures_valid = True
            else:
                self.figures_valid = False

    ############################################################################################

    def plot_data(self):
        message = 'Plot Data\n'
        message_colour = 'blue'
        self.session_log.write_textbox(message, message_colour)

        if self.user_entry.header_include == HEADER_INCLUDE_NOT:
            # self.figure_list = pl.plot_data_np_timestamp_multicolumn_header(self.data_requested_np, self.timestamps, None)
            # self.figure_list = pl.plot_data_np_timestamp_multicolumn(self.data_requested_np, self.timestamps)

            pl.plot_data_np_timestamp_multicolumn_header(self.data_requested_np, self.timestamps, None)
        else:
            header_list_np = self.header_list_np[self.column_choice_list]
            # self.figure_list = pl.plot_data_np_timestamp_multicolumn_header(self.data_requested_np, self.timestamps,
            #                                                                          header_list_np)
            pl.plot_data_np_timestamp_multicolumn_header(self.data_requested_np, self.timestamps, header_list_np)
        # pl.plot_show_plots()

        # message = 'Generated ' + str(len(self.figure_list)) + ' Plots\n'
        message = 'Generated ' + str(self.data_requested_np.size) + ' Plots\n'
        message_colour = 'black'
        self.session_log.write_textbox(message, message_colour)

        message = 'End of Plotting\n'
        message_colour = 'blue'
        self.session_log.write_textbox(message, message_colour)

    @staticmethod
    def close_plots():
        pl.plot_close()

    def textbox_update(self, data):
        self.textbox.configure(state='normal')
        self.textbox.delete('1.0', 'end')
        self.textbox.insert('end', data)
        self.textbox.configure(state='disabled')
