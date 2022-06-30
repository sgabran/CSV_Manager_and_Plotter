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

        self.timestamp_extract = TIMESTAMP_EXTRACT
        self.header_row_index = ROW_HEADER
        self.data_start_row_index = ROW_DATA_START
        self.data_end_row_index = ROW_DATA_END
        self.read_delimiter_type = DELIMITER_TYPE_COMMA
        self.write_delimiter_type = DELIMITER_TYPE_COMMA
        self.n_rows_to_peak = N_ROWS_TO_PEAK
        self.column_choice_option = COLUMNS_ALL
        self.column_choice_list = []
        self.timestamp_include = TIMESTAMP_INCLUDE
        self.header_include = HEADER_INCLUDE_NOT
