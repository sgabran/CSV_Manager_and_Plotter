# ver = '2022-5-10-1'

from tkinter import messagebox

import numpy as np

import filename_methods as fm
import plot_methods as pl
from constants import *


class SessionProcessCSV:
    def __init__(self, user_entry, session_log, textbox, session_option):
        self.user_entry = user_entry
        self.session_log = session_log
        self.textbox = textbox
        self.session_option = session_option

        self.data_raw = []
        self.data_parsed = []
        self.rows_to_peak = []

        self.data_raw_n_rows = 0
        self.data_raw_n_rows_multi_file = []
        self.data_raw_n_columns = 0
        self.data_raw_n_columns_multi_file = []

        self.data_requested_np_multi_file_2D = np.array([])
        self.headers_np_multi_file_2D = np.array([])

        self.min_n_row_multi_file = 0
        self.min_n_column_multi_file = 0

        self.columns_indices_to_process = []
        self.data_end_index = 0
        self.data_length_to_get = 0

        self.data_requested_np = np.array(())
        self.data_requested_np_multi_file = np.array(())

        self.timestamps_np = np.array(())

        self.data_requested_with_timestamp_np = np.array(())
        self.data_requested_with_timestamp_np_multi_file = np.array(())
        self.data_requested_with_timestamps_np_multi_file_2D = np.array(())

        self.headers_np = np.array(())
        self.headers_np_multi_file = np.array(())
        self.header_list_multi_file = []

        self.data_valid = None
        self.figure_list = []
        self.figures_valid = None

        if self.session_option is OPTION_PEAK_FILE:
            self.peak_data()

        elif self.session_option is OPTION_PROCESS_FILE:
            if not self.user_entry.multi_files:
                self.process_data()
            else:
                self.process_data_multi_files()

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
        self.data_raw_n_rows = len(self.data_parsed)
        self.data_raw_n_columns = len(self.data_parsed[self.user_entry.data_start_row_index])

        # Peak data
        # Display first rows of file on the textbox
        for row in range(0, self.user_entry.n_rows_to_peak):
            self.rows_to_peak.append('Row-' + str(row) + ':\n' + str(self.data_parsed[row]) + '\n\n')

        self.textbox_update(self.rows_to_peak)

    def load_multi_files(self):
        # Read file
        message = "Reading Multiple Files\n"
        message_colour = "brown"
        self.session_log.write_textbox(message, message_colour)

        for file in self.user_entry.multi_file_list:
            file_fullname = file
            # Read file, parse data
            data_parsed_temp = []
            with open(file_fullname, 'r') as f:
                data_raw = f.readlines()
                for row in data_raw:
                    # Remove spaces and '\n'. Use strip() or: self.data_parsed.append(row.replace("\n", ""))
                    row = row.strip()
                    # Parse elements using delimiter
                    if self.user_entry.read_delimiter_type == DELIMITER_TYPE_COMMA:
                        data_parsed_temp.append(row.split(','))
                    elif self.user_entry.read_delimiter_type == DELIMITER_TYPE_TAB:
                        data_parsed_temp.append(row.split('\t'))

            # Get dimensions of data file
            self.data_raw_n_rows_multi_file.append(len(data_parsed_temp))
            self.data_raw_n_columns_multi_file.append(len(data_parsed_temp[self.user_entry.data_start_row_index]))

            self.data_parsed.append(data_parsed_temp)

        self.min_n_row_multi_file = min(self.data_raw_n_rows_multi_file)
        print("::self.min_n_row_multi_file: ", self.min_n_row_multi_file)
        if len(self.data_raw_n_rows_multi_file) > 0:
            result = all(elem == self.data_raw_n_rows_multi_file[0] for elem in self.data_raw_n_rows_multi_file)
            if not result:
                message = "NOTE: Rows don't have same length" + "\n"
                message_colour = 'red'
                self.session_log.write_textbox(message, message_colour)
                print(message)

        self.min_n_column_multi_file = min(self.data_raw_n_columns_multi_file)
        if len(self.data_raw_n_columns_multi_file) > 0:
            result = all(elem == self.data_raw_n_columns_multi_file[0] for elem in self.data_raw_n_columns_multi_file)
            if not result:
                message = "NOTE: Files don't have same number of columns" + "\n"
                message_colour = 'red'
                self.session_log.write_textbox(message, message_colour)
                print(message)

    def peak_data(self):
        self.close_plots()
        self.load_and_peak()

        message = "Total Data File Rows: " + str(self.data_raw_n_rows) + '\n'
        message_colour = "blue"
        self.session_log.write_textbox(message, message_colour)

        message = "Total Data File Columns: " + str(self.data_raw_n_columns) + '\n'
        message_colour = "blue"
        self.session_log.write_textbox(message, message_colour)

    def process_data(self):
        self.close_plots()
        self.load_and_peak()

        # Check user entry for length of data to read
        if 0 < self.user_entry.data_length_requested < self.user_entry.data_start_row_index:
            message = 'Invalid row entry. Data Start Index is larger than Data End Index\n'
            message_colour = 'red'
            self.session_log.write_textbox(message, message_colour)
            return

        # Get indices of rows to read
        # If entry is default (0), then read all file
        if self.user_entry.data_length_requested == 0:
            self.data_end_index = self.data_raw_n_rows - 1
            self.data_length_to_get = self.data_end_index - self.user_entry.data_start_row_index + 1
        # User entry is not valid
        elif self.user_entry.data_length_requested > self.data_raw_n_rows - 1:
            message = "Number of Rows Requested Exceeds Data File Size\n" + "Rows in file = " + \
                      str(self.data_raw_n_rows) + '\n'
            message_colour = 'red'
            self.session_log.write_textbox(message, message_colour)
            messagebox.showerror("Error", message)
            return
        # Use the user entry
        else:
            self.data_end_index = self.user_entry.data_length_requested + self.user_entry.data_start_row_index - 1
            self.data_length_to_get = self.user_entry.data_length_requested

        print("::self.data_end_index:", self.data_end_index)
        print("::self.data_length_to_get:", self.data_length_to_get)

        message = "Number of Data Points to Process: " + str(self.user_entry.data_length_requested) + '\n'
        message_colour = "blue"
        self.session_log.write_textbox(message, message_colour)

        # Get indices of columns to read
        # If entry is COLUMNS_ALL then read all columns, use the shortest file as reference
        if self.user_entry.column_choice_option == COLUMNS_ALL:
            self.columns_indices_to_process = list(range(0, self.data_raw_n_columns))
        else:
            self.columns_indices_to_process = self.user_entry.column_choice_list

        print("::column_choice_list: ", self.columns_indices_to_process)

        message = 'Columns to Process: ' + str(self.columns_indices_to_process) + '\n'
        colour = 'blue'
        self.session_log.write_textbox(message, colour)

        # Check column_choice_list is valid, requested columns are within file size
        columns_to_process_is_valid = not any(
            (column_index > self.data_raw_n_columns - 1) for column_index in self.columns_indices_to_process)
        print("::columns_to_process_is_valid: ", columns_to_process_is_valid)

        if columns_to_process_is_valid is not True:
            message = 'Requested columns are out of range\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            messagebox.showerror("Error", message)
            return

        # Extract requested rows
        data_requested = self.data_parsed[self.user_entry.data_start_row_index: self.data_end_index + 1]
        # Convert list to numpy array
        data_requested_np = np.array(data_requested)
        # Convert blank data to zeros
        data_requested_np = np.where(data_requested_np == '', 0, data_requested_np)
        # Convert string to float
        try:
            data_requested_np = data_requested_np.astype(np.float)
        except:
            message = "Error Reading File:\n-Check column for empty cells\n-Check non numeric values for data\n-Check delimiter type\n"
            messagebox.showerror("Data Read Error", message)
            return

        # Extract timestamps
        if self.user_entry.timestamp_extract == 1:
            timestamps = data_requested_np[:, 0]
        else:
            timestamps = list(range(0, self.data_end_index - self.user_entry.data_start_row_index + 1))

        self.timestamps_np = np.array(timestamps)
        self.timestamps_np = np.reshape(self.timestamps_np, (-1, 1))

        print("TIMESTAMPS")
        print(":: Shape of self.timestamps_np: ", self.timestamps_np.shape)

        # Extract requested columns
        self.data_requested_np = data_requested_np[:, self.columns_indices_to_process]

        # Add timestamps
        self.data_requested_with_timestamp_np = np.concatenate((self.timestamps_np, self.data_requested_np), axis=1)
        print(":: Shape of self.data_requested_with_timestamp_np_multi_file: ",
              self.data_requested_with_timestamp_np.shape)

        # Extract headers
        if (self.user_entry.header_include_plots == HEADER_INCLUDE_PLOTS) | (
                self.user_entry.header_include_files == HEADER_INCLUDE_FILES):
            headers = self.data_parsed[self.user_entry.header_row_index]
            self.headers_np = np.array(headers)

        # Plot data if requested
        if self.user_entry.action == PROCESS_AND_PLOT:
            self.plot_data(self.user_entry.include_plot_title, self.user_entry.plot_title)

            if self.figure_list is not None:
                self.figures_valid = True
            else:
                self.figures_valid = False

    def process_data_multi_files(self):
        self.close_plots()
        self.load_multi_files()

        # Check user entry for length of data to read
        if 0 < self.user_entry.data_length_requested < self.user_entry.data_start_row_index:
            message = 'Invalid row entry. Data Start Index is larger than Data End Index\n'
            message_colour = 'red'
            self.session_log.write_textbox(message, message_colour)
            return

        # Get indices of rows to read
        # If entry is default (0), then read all rows, use the shortest file as reference
        if self.user_entry.data_length_requested == 0:
            self.data_end_index = self.min_n_row_multi_file - 1
            self.data_length_to_get = self.data_end_index - self.user_entry.data_start_row_index + 1
        # User entry is not valid
        elif self.user_entry.data_length_requested > self.min_n_row_multi_file - 1:
            message = "Number of Rows Requested Exceeds Data File Size\n" + "Rows in file = " + \
                      str(self.min_n_row_multi_file) + '\n'
            message_colour = 'red'
            self.session_log.write_textbox(message, message_colour)
            messagebox.showerror("Error", message)
            return
        # Use the user entry
        else:
            self.data_end_index = self.user_entry.data_length_requested + self.user_entry.data_start_row_index - 1
            self.data_length_to_get = self.user_entry.data_length_requested

        print("::self.data_end_index:", self.data_end_index)
        print("::self.data_length_to_get:", self.data_length_to_get)

        message = "Number of Data Points to Process: " + str(self.user_entry.data_length_requested) + '\n'
        message_colour = "blue"
        self.session_log.write_textbox(message, message_colour)

        # Get indices of columns to read
        # If entry is COLUMNS_ALL then read all columns, use the shortest file as reference
        if self.user_entry.column_choice_option == COLUMNS_ALL:
            self.columns_indices_to_process = list(range(0, self.min_n_column_multi_file))
        else:
            self.columns_indices_to_process = self.user_entry.column_choice_list

        print("::column_choice_list: ", self.columns_indices_to_process)

        message = 'Columns to Process: ' + str(self.columns_indices_to_process) + '\n'
        colour = 'blue'
        self.session_log.write_textbox(message, colour)

        # Check column_choice_list is valid, requested columns are within file size
        columns_to_process_is_valid = not any(
            (column_index > self.min_n_column_multi_file - 1) for column_index in self.columns_indices_to_process)
        print("::columns_to_process_is_valid: ", columns_to_process_is_valid)

        if columns_to_process_is_valid is not True:
            message = 'Requested columns are out of range\n'
            colour = 'red'
            self.session_log.write_textbox(message, colour)
            messagebox.showerror("Error", message)
            return

        # Extract requested rows
        self.data_requested_np_multi_file = np.zeros(
            (self.user_entry.n_multi_files, self.data_length_to_get, len(self.columns_indices_to_process)), dtype=float)
        print("::shape of data_requested_np_multi_file: ", self.data_requested_np_multi_file.shape)

        for file in range(self.user_entry.n_multi_files):
            print("PROCESSING FILE: ", file)
            # Extract requested rows
            data_requested_temp = self.data_parsed[file][self.user_entry.data_start_row_index: self.data_end_index + 1]
            data_requested_temp_np = np.array(data_requested_temp)
            # Convert blank data to zeros
            data_requested_temp_np = np.where(data_requested_temp_np == '', 0, data_requested_temp_np)
            # Convert string to float
            # data_requested_temp_np = data_requested_temp_np.astype(np.float)
            try:
                data_requested_temp_np = data_requested_temp_np.astype(np.float)
            except:
                message = "Error Reading File:\n-Check column for empty cells\n-Check non numeric values for data\n-Check delimiter type\n"
                messagebox.showerror("Data Read Error", message)
                return
            # Extract requested columns
            data_requested_temp_np = data_requested_temp_np[:, self.columns_indices_to_process]
            self.data_requested_np_multi_file[file, :, :] = data_requested_temp_np
        print(":: Shape of self.data_requested_np_multi_file: ", self.data_requested_np_multi_file.shape)

        # Extract timestamps
        if self.user_entry.timestamp_extract == 1:
            timestamps = self.data_requested_np_multi_file[0, :, 0]
        else:
            timestamps = list(range(0, self.data_length_to_get))
            # timestamps = range(0, self.user_entry.data_length_requested)

        print(":: Length of timestamps: ", len(timestamps))

        self.timestamps_np = np.array(timestamps)
        self.timestamps_np = np.reshape(self.timestamps_np, (-1, 1))

        # Add timestamps
        self.data_requested_with_timestamp_np_multi_file = np.zeros(
            (self.user_entry.n_multi_files, self.data_length_to_get, len(self.columns_indices_to_process) + 1),
            dtype=float)
        for file in range(self.user_entry.n_multi_files):
            self.data_requested_with_timestamp_np_multi_file[file] = np.hstack(
                (self.timestamps_np, self.data_requested_np_multi_file[file, :, :]))

        print("TIMESTAMPS")
        print(":: Shape of self.timestamps_np: ", self.timestamps_np.shape)
        print(":: Shape of self.data_requested_with_timestamp_np_multi_file: ",
              self.data_requested_with_timestamp_np_multi_file.shape)

        # Extract headers
        if (self.user_entry.header_include_plots == HEADER_INCLUDE_PLOTS) | (
                self.user_entry.header_include_files == HEADER_INCLUDE_FILES):
            for file in range(self.user_entry.n_multi_files):
                self.header_list_multi_file.append(self.data_parsed[file][self.user_entry.header_row_index])
        print("HEADERS")
        print(":: Length of Shape of self.header_list_multi_file: ", len(self.header_list_multi_file))

        self.headers_np_multi_file = np.array(self.header_list_multi_file)
        print(":: self.headers_np_multi_file: ", self.headers_np_multi_file.shape)

        self.format_multi_file_to_single_file()

        # Plot data if requested
        if self.user_entry.action == PROCESS_AND_PLOT:
            # data_to_plot = self.format_multi_file_to_single_file_for_plotting(self.user_entry.n_multi_files, self.data_requested_np_multi_file)
            self.plot_data_multi_file(self.user_entry.include_plot_title, self.user_entry.plot_title)

            if self.figure_list is not None:
                self.figures_valid = True
            else:
                self.figures_valid = False

    ############################################################################################

    def plot_data(self, include_title, title):
        message = 'Plot Data\n'
        message_colour = 'blue'
        self.session_log.write_textbox(message, message_colour)

        if self.user_entry.header_include_plots == HEADER_INCLUDE_PLOTS_NOT:
            if self.user_entry.plots_overlap:
                pl.plot_data_np_timestamp_multicolumn_header_plot_overlap(self.data_requested_np, self.timestamps_np,
                                                                          None, include_title, title)
            else:
                pl.plot_data_np_timestamp_multicolumn_header(self.data_requested_np, self.timestamps_np, None,
                                                             include_title, title)
        else:
            headers_np = self.headers_np[self.columns_indices_to_process]
            if self.user_entry.plots_overlap:
                pl.plot_data_np_timestamp_multicolumn_header_plot_overlap(self.data_requested_np, self.timestamps_np,
                                                                          headers_np, include_title, title)
            else:
                pl.plot_data_np_timestamp_multicolumn_header(self.data_requested_np, self.timestamps_np, headers_np,
                                                             include_title, title)

        message = 'Generated ' + str(self.data_requested_np.size) + ' Plots\n'
        message_colour = 'black'
        self.session_log.write_textbox(message, message_colour)

        message = 'End of Plotting\n'
        message_colour = 'blue'
        self.session_log.write_textbox(message, message_colour)

    def plot_data_multi_file(self, include_title, title):
        message = 'Plot Data\n'
        message_colour = 'blue'
        self.session_log.write_textbox(message, message_colour)
        if self.user_entry.header_include_plots == HEADER_INCLUDE_PLOTS_NOT:
            if self.user_entry.plots_overlap:
                pl.plot_data_np_timestamp_multicolumn_header_plot_overlap(self.data_requested_np_multi_file_2D,
                                                                          self.timestamps_np, None, include_title,
                                                                          title)
            else:
                pl.plot_data_np_timestamp_multicolumn_header(self.data_requested_np_multi_file_2D, self.timestamps_np,
                                                             None, include_title, title)
        else:
            if self.user_entry.plots_overlap:
                pl.plot_data_np_timestamp_multicolumn_header_plot_overlap(self.data_requested_np_multi_file_2D,
                                                                          self.timestamps_np,
                                                                          self.headers_np_multi_file_2D, include_title,
                                                                          title)
            else:
                pl.plot_data_np_timestamp_multicolumn_header(self.data_requested_np_multi_file_2D, self.timestamps_np,
                                                             self.headers_np_multi_file_2D, include_title, title)

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

    def format_multi_file_to_single_file(self):
        for file in range(self.user_entry.n_multi_files):
            temp = self.data_requested_np_multi_file[file, :, :]
            self.data_requested_np_multi_file_2D = np.hstack(
                [self.data_requested_np_multi_file_2D, temp]) if self.data_requested_np_multi_file_2D.size else temp
            if self.user_entry.header_include_plots == HEADER_INCLUDE_PLOTS:
                try:
                    headers_np_temp = self.headers_np_multi_file[file, self.columns_indices_to_process]
                    self.headers_np_multi_file_2D = np.append(self.headers_np_multi_file_2D,
                                                              headers_np_temp) if self.headers_np_multi_file_2D.size else headers_np_temp
                except:
                    message = "Error in files.\nMake sure files have same structure (rows and columns)\n"
                    message_colour = 'red'
                    self.session_log.write_textbox(message, message_colour)
                    messagebox.showerror("Error", message)
                    return

        self.data_requested_with_timestamps_np_multi_file_2D = np.array(
            [self.data_length_to_get, len(self.columns_indices_to_process) + 1])
        self.data_requested_with_timestamps_np_multi_file_2D = np.concatenate(
            (self.timestamps_np, self.data_requested_np_multi_file_2D), axis=1)
