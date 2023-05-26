from constants import *


class UserEntry:
    def __init__(self):
        self.file_location = FILE_LOCATION
        self.file_name = FILE_NAME
        self.file_suffix = FILE_SUFFIX
        self.file_name_save = FILE_NAME_SAVE
        self.sample_freq = SAMPLE_FREQ
        self.file_save_option = FILE_SAVE_SINGLE_COLUMN
        self.action = PROCESS_ONLY

        self.multi_files = MULTI_FILES
        self.multi_file_list = []
        self.multi_file_name = []
        self.multi_file_suffix = []
        self.multi_file_location = []
        self.n_multi_files = 0

        self.timestamp_extract = TIMESTAMP_EXTRACT
        self.header_row_index = ROW_HEADER
        self.data_start_row_index = DATA_ROW_START_INDEX_DEFAULT
        self.data_length_requested = DATA_LENGTH_REQUESTED_DEFAULT
        self.read_delimiter_type = DELIMITER_TYPE_COMMA
        self.write_delimiter_type = DELIMITER_TYPE_COMMA
        self.n_rows_to_peak = N_ROWS_TO_PEAK
        self.column_choice_option = COLUMNS_ALL
        self.column_choice_list = []
        self.column_choice_list_multi_files = []
        self.timestamp_include = TIMESTAMP_INCLUDE
        self.header_include_plots = HEADER_INCLUDE_PLOTS_NOT
        self.header_include_files = HEADER_INCLUDE_FILES_NOT
        self.plots_overlap = PLOTS_OVERLAP
        self.include_plot_title = INCLUDE_PLOT_TITLE
        self.plot_title = PLOT_TITLE
