import os
import os.path
from idlelib.tooltip import *
from tkinter import filedialog
from tkinter import messagebox

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

import filename_methods as fm
import misc_methods as mm
from constants import *
from session_log import SessionLog
from session_process_csv import SessionProcessCSV
from tooltips_text import *
from user_entry import UserEntry


# Class to create GUI
class MainWindow:
    # Dependencies: MainWindow communicate with classes that are related to GUI contents and buttons
    def __init__(self):  # instantiation function. Use root for GUI and refers to main window

        root = Tk()
        root.title("CSV File Manager and Plotter")
        self.root_frame = root
        self.user_entry = UserEntry()
        self.session_log = SessionLog(self.user_entry)
        self.session_process_csv = None

        self.session_option = OPTION_PEAK_FILE

        self.rows_to_peak = [0] * self.user_entry.n_rows_to_peak

        # GUI Frames
        self.frame_root_title = Frame(root, highlightthickness=0)
        self.frame_root_session = LabelFrame(root, width=120, height=390, padx=5, pady=5, text="Session")
        self.frame_root_commands = LabelFrame(root, width=120, height=80, padx=5, pady=5, text="")

        # Disable resizing the window
        root.resizable(False, False)

        # Grids
        self.frame_root_title.grid(row=0, column=0, padx=10, pady=5, ipadx=5, ipady=5)
        self.frame_root_session.grid(row=1, column=0, sticky="W", padx=10, pady=(5, 5), ipadx=5, ipady=2)
        self.frame_root_commands.grid(row=2, column=0, sticky="W", padx=10, pady=(10, 5), ipadx=5, ipady=2)
        # self.frame_root_session.grid_propagate(False)  # Prevents automatic resizing of frame
        # self.frame_root_commands.grid_propagate(False)  # Prevents automatic resizing of frame

        entry_validation_positive_numbers = root.register(mm.only_positive_numbers)
        entry_validation_numbers = root.register(mm.only_digits)
        entry_validation_numbers_space = root.register(mm.digits_or_space)
        entry_validation_positive_numbers_comma = root.register(mm.positive_numbers_or_comma)

        ######################################################################
        # Frame Session
        # Labels
        label_file_name = Label(self.frame_root_session, text="File Name")
        label_multi_files = Label(self.frame_root_session, text="Read Multiple Files")
        label_rows_to_peak = Label(self.frame_root_session, text="Rows to Peak")
        Label_rows = Label(self.frame_root_session, text="Rows")
        label_columns_to_process = Label(self.frame_root_session, text="Columns to Process")
        label_timestamp_extract = Label(self.frame_root_session, text="Timestamp at Col. 0")
        label_timestamp_include = Label(self.frame_root_session, text="Include Timestamp")
        label_header_include_plots = Label(self.frame_root_session, text="Include Header or Legend in Plots/Files")
        # label_header_include_files = Label(self.frame_root_session, text="Include Header in Saved Files")
        label_read_delimiter_type = Label(self.frame_root_session, text="Read File Delimiter")
        label_write_delimiter_type = Label(self.frame_root_session, text="Save File Delimiter")
        label_header = Label(self.frame_root_session, text="Header Index")
        label_data_start = Label(self.frame_root_session, text="Data Start Index")
        label_data_end = Label(self.frame_root_session, text="Data Length to Read")
        label_data_end_2 = Label(self.frame_root_session, text="Type 0 to read all rows")
        label_action = Label(self.frame_root_session, text="Action")
        label_plots_overlap = Label(self.frame_root_session, text="Overlap Plots")
        label_include_plot_title = Label(self.frame_root_session, text="Plot Title")

        # Entries
        self.entry_file_name_entry = StringVar()
        self.entry_file_name_entry.trace("w", lambda name, index, mode,
                                                     entry_file_name_entry=self.entry_file_name_entry: self.entry_update_file_name_and_suffix())
        self.entry_file_name = Entry(self.frame_root_session, width=81, textvariable=self.entry_file_name_entry)
        self.entry_file_name.insert(END, (FILE_NAME if FILE_NAME else FILE_NAME_INIT))

        self.entry_file_location_entry = StringVar()
        self.entry_file_location_entry.trace("w", lambda name, index, mode,
                                                         entry_file_location_entry=self.entry_file_location_entry: self.entry_update_file_location())
        self.entry_file_location = Entry(self.frame_root_session, width=80, textvariable=self.entry_file_location_entry)
        self.entry_file_location.insert(END, os.path.normcase(FILE_LOCATION))

        self.entry_rows_to_peak_entry = IntVar()
        self.entry_rows_to_peak_entry.trace("w", lambda name, index, mode,
                                                        entry_rows_to_peak_entry=self.entry_rows_to_peak_entry: self.entry_update_rows_to_peak())
        self.entry_rows_to_peak = Entry(self.frame_root_session, width=6, textvariable=self.entry_rows_to_peak_entry,
                                        validate="key", validatecommand=(entry_validation_positive_numbers, '%P'))
        self.entry_rows_to_peak.insert(END, str(N_ROWS_TO_PEAK))

        self.entry_columns_to_process_entry = StringVar()
        self.entry_columns_to_process_entry.trace("w", lambda name, index, mode,
                                                              entry_columns_to_process_entry=self.entry_columns_to_process_entry: self.entry_update_columns_to_process())
        self.entry_columns_to_process = Entry(self.frame_root_session, width=80,
                                              textvariable=self.entry_columns_to_process_entry,
                                              validate="key",
                                              validatecommand=(entry_validation_positive_numbers_comma, '%S'))
        self.entry_columns_to_process.insert(END, str(PROCESS_ALL_COLUMNS))
        self.entry_columns_to_process.configure(state='disabled')

        self.entry_header_row_entry = StringVar()
        self.entry_header_row_entry.trace("w", lambda name, index, mode,
                                                      entry_header_row_entry=self.entry_header_row_entry: self.entry_update_header_row())
        self.entry_header_row = Entry(self.frame_root_session, width=10, textvariable=self.entry_header_row_entry,
                                      validate="key", validatecommand=(entry_validation_positive_numbers, '%P'))
        self.entry_header_row.insert(END, str(ROW_HEADER))

        self.entry_data_start_row_entry = StringVar()
        self.entry_data_start_row_entry.trace("w", lambda name, index, mode,
                                                          entry_data_start_row_entry=self.entry_data_start_row_entry: self.entry_update_data_start_row())
        self.entry_data_start_row = Entry(self.frame_root_session, width=10,
                                          textvariable=self.entry_data_start_row_entry, validate="key",
                                          validatecommand=(entry_validation_positive_numbers, '%P'))
        self.entry_data_start_row.insert(END, str(DATA_ROW_START_INDEX_DEFAULT))

        self.entry_data_length_requested_entry = StringVar()
        self.entry_data_length_requested_entry.trace("w", lambda name, index, mode,
                                                                 entry_data_length_requested_entry=self.entry_data_length_requested_entry: self.entry_update_data_length_requested())
        self.entry_data_length_requested = Entry(self.frame_root_session, width=10,
                                                 textvariable=self.entry_data_length_requested_entry, validate="key",
                                                 validatecommand=(entry_validation_positive_numbers, '%S'))
        self.entry_data_length_requested.insert(END, str(DATA_LENGTH_REQUESTED_DEFAULT))

        self.entry_plot_title_entry = StringVar()
        self.entry_plot_title_entry.trace("w", lambda name, index, mode,
                                                      entry_plot_title_entry=self.entry_plot_title_entry: self.entry_update_plot_title())
        self.entry_plot_title = Entry(self.frame_root_session, width=60, textvariable=self.entry_plot_title_entry)
        self.entry_plot_title.insert(END, str(PLOT_TITLE))

        # Checkboxes
        self.checkbox_multi_files_entry = IntVar(value=self.user_entry.multi_files)
        self.checkbox_multi_files = Checkbutton(self.frame_root_session,
                                                variable=self.checkbox_multi_files_entry,
                                                command=self.checkbox_update_multi_files)

        # Radiobuttons
        self.radiobutton_column_choice_entry = IntVar(value=self.user_entry.column_choice_option)
        self.radiobutton_column_choice_1 = Radiobutton(self.frame_root_session, text="Select Columns",
                                                       command=self.radiobutton_column_choice_option,
                                                       variable=self.radiobutton_column_choice_entry,
                                                       value=COLUMNS_SELECT)
        self.radiobutton_column_choice_2 = Radiobutton(self.frame_root_session, text="All Columns",
                                                       command=self.radiobutton_column_choice_option,
                                                       variable=self.radiobutton_column_choice_entry,
                                                       value=COLUMNS_ALL)

        self.radiobutton_read_delimiter_type_entry = IntVar(value=self.user_entry.read_delimiter_type)
        self.radiobutton_read_delimiter_type_1 = Radiobutton(self.frame_root_session, text="comma",
                                                             command=self.radiobutton_read_delimiter_type,
                                                             variable=self.radiobutton_read_delimiter_type_entry,
                                                             value=DELIMITER_TYPE_COMMA)
        self.radiobutton_read_delimiter_type_2 = Radiobutton(self.frame_root_session, text="tab",
                                                             command=self.radiobutton_read_delimiter_type,
                                                             variable=self.radiobutton_read_delimiter_type_entry,
                                                             value=DELIMITER_TYPE_TAB)

        self.radiobutton_write_delimiter_type_entry = IntVar(value=self.user_entry.write_delimiter_type)
        self.radiobutton_write_delimiter_type_1 = Radiobutton(self.frame_root_session, text="comma",
                                                              command=self.radiobutton_write_delimiter_type,
                                                              variable=self.radiobutton_write_delimiter_type_entry,
                                                              value=DELIMITER_TYPE_COMMA)
        self.radiobutton_write_delimiter_type_2 = Radiobutton(self.frame_root_session, text="tab",
                                                              command=self.radiobutton_write_delimiter_type,
                                                              variable=self.radiobutton_write_delimiter_type_entry,
                                                              value=DELIMITER_TYPE_TAB)

        self.radiobutton_action_entry = IntVar(value=self.user_entry.action)
        self.radiobutton_action_1 = Radiobutton(self.frame_root_session, text="Process Only",
                                                command=self.radiobutton_action,
                                                variable=self.radiobutton_action_entry,
                                                value=PROCESS_ONLY)
        self.radiobutton_action_2 = Radiobutton(self.frame_root_session, text="Process and Plot",
                                                command=self.radiobutton_action,
                                                variable=self.radiobutton_action_entry,
                                                value=PROCESS_AND_PLOT)

        # Textbox
        self.textbox_rows = Text(self.frame_root_session, height=10, width=100)
        # self.textbox_rows_hscroll_bar = Scrollbar(self.frame_root_session, orient="horizontal")
        # self.textbox_rows_hscroll_bar.config(command=self.textbox_rows.xview)
        # self.textbox_rows.config(xscrollcommand=self.textbox_rows_hscroll_bar.set)
        self.textbox_rows_vscroll_bar = Scrollbar(self.frame_root_session, orient="vertical")
        self.textbox_rows_vscroll_bar.config(command=self.textbox_rows.yview)
        self.textbox_rows.config(yscrollcommand=self.textbox_rows_vscroll_bar.set)
        self.textbox_row_clear()

        # Checkboxes
        self.checkbox_timestamp_extract_entry = IntVar(value=self.user_entry.timestamp_extract)
        self.checkbox_timestamp_extract = Checkbutton(self.frame_root_session,
                                                      variable=self.checkbox_timestamp_extract_entry,
                                                      command=self.checkbox_update_timestamp_extract)

        self.checkbox_timestamp_include_entry = IntVar(value=self.user_entry.timestamp_include)
        self.checkbox_timestamp_include = Checkbutton(self.frame_root_session,
                                                      variable=self.checkbox_timestamp_include_entry,
                                                      command=self.checkbox_update_timestamp_include)

        # self.checkbox_header_include_files_entry = IntVar(value=self.user_entry.header_include_files)
        # self.checkbox_header_include_files = Checkbutton(self.frame_root_session,
        #                                                  variable=self.checkbox_header_include_files_entry,
        #                                                  command=self.checkbox_update_header_include_files)

        self.checkbox_header_include_plots_entry = IntVar(value=self.user_entry.header_include_plots)
        self.checkbox_header_include_plots = Checkbutton(self.frame_root_session,
                                                         variable=self.checkbox_header_include_plots_entry,
                                                         command=self.checkbox_update_header_include_plots)

        self.checkbox_plots_overlap_entry = IntVar(value=self.user_entry.plots_overlap)
        self.checkbox_plots_overlap = Checkbutton(self.frame_root_session,
                                                  variable=self.checkbox_plots_overlap_entry,
                                                  command=self.checkbox_update_plots_overlap)

        self.checkbox_include_plot_title_entry = IntVar(value=self.user_entry.include_plot_title)
        self.checkbox_include_plot_title = Checkbutton(self.frame_root_session,
                                                       variable=self.checkbox_include_plot_title_entry,
                                                       command=self.checkbox_update_include_plot_title)

        # Buttons
        self.button_choose_single_file = Button(self.frame_root_session, text="Choose File", command=self.choose_file,
                                                pady=0, width=10, fg='brown')
        self.button_file_peak = Button(self.frame_root_session, text="File Peak", command=self.button_file_peak, pady=0,
                                       width=10)
        self.button_choose_multi_files = Button(self.frame_root_session, text="Choose Multi Files", pady=0, width=15,
                                                fg="blue", command=self.choose_multi_file)

        # Grids
        label_file_name.grid(row=5, column=0, sticky=E)
        self.entry_file_name.grid(row=5, column=1, sticky=W)
        label_multi_files.grid(row=5, column=1, sticky=W, padx=(510, 0))
        self.checkbox_multi_files.grid(row=5, column=1, sticky=W, padx=(615, 0))
        self.button_file_peak.grid(row=7, column=0, sticky=NE)
        if self.user_entry.multi_files:
            self.show_button_choose_multi_files()
            self.disable_button_file_peak()
        else:
            self.show_button_choose_single_file()
            self.enable_button_file_peak()
        self.entry_file_location.grid(row=6, column=1, sticky=W, padx=(5, 0))
        label_rows_to_peak.grid(row=6, column=1, sticky=W, padx=(500, 0))
        self.entry_rows_to_peak.grid(row=6, column=1, sticky=W, padx=(580, 0))
        Label_rows.grid(row=7, column=0, sticky=E)
        self.textbox_rows.grid(row=7, column=1, sticky=W)
        self.textbox_rows_vscroll_bar.grid(row=7, column=1, sticky=NS, padx=(805, 0))
        label_columns_to_process.grid(row=8, column=0, sticky=E)
        self.entry_columns_to_process.grid(row=8, column=1, sticky=W)
        self.radiobutton_column_choice_1.grid(row=8, column=1, sticky=W, padx=(380, 0))
        self.radiobutton_column_choice_2.grid(row=8, column=1, sticky=W, padx=(490, 0))
        label_timestamp_extract.grid(row=9, column=0, sticky=E, padx=(15, 25))
        self.checkbox_timestamp_extract.grid(row=9, column=0, sticky=E)
        label_timestamp_include.grid(row=9, column=1, sticky=W)
        self.checkbox_timestamp_include.grid(row=9, column=1, sticky=W, padx=(105, 10))
        label_read_delimiter_type.grid(row=10, column=0, sticky=E)
        self.radiobutton_read_delimiter_type_1.grid(row=10, column=1, sticky=W)
        self.radiobutton_read_delimiter_type_2.grid(row=10, column=1, sticky=W, padx=(100, 0))
        label_write_delimiter_type.grid(row=11, column=0, sticky=E)
        self.radiobutton_write_delimiter_type_1.grid(row=11, column=1, sticky=W)
        self.radiobutton_write_delimiter_type_2.grid(row=11, column=1, sticky=W, padx=(100, 0))
        label_header.grid(row=13, column=0, sticky=E)
        # label_header_include_files.grid             (row=13, column=1, sticky=W, padx=(70, 0))
        # self.checkbox_header_include_files.grid     (row=13, column=1, sticky=W, padx=(230, 0))
        self.entry_header_row.grid(row=13, column=1, sticky=W)
        label_data_start.grid(row=14, column=0, sticky=E)
        self.entry_data_start_row.grid(row=14, column=1, sticky=W)
        label_data_end.grid(row=15, column=0, sticky=E)
        label_data_end_2.grid(row=15, column=1, sticky=W, padx=(70, 0))
        self.entry_data_length_requested.grid(row=15, column=1, sticky=W)
        label_action.grid(row=16, column=0, sticky=E)
        self.radiobutton_action_1.grid(row=16, column=1, sticky=W)
        self.radiobutton_action_2.grid(row=16, column=1, sticky=W, padx=(150, 0))
        label_header_include_plots.grid(row=16, column=1, sticky=W, padx=(300, 0))
        self.checkbox_header_include_plots.grid(row=16, column=1, sticky=W, padx=(510, 0))
        # self.checkbox_header_include_files.configure(state='disabled')
        label_plots_overlap.grid(row=16, column=1, sticky=W, padx=(545, 0))
        self.checkbox_plots_overlap.grid(row=16, column=1, sticky=W, padx=(620, 0))
        label_include_plot_title.grid(row=17, column=0, sticky=E)
        self.checkbox_include_plot_title.grid(row=17, column=1, sticky=W)
        self.entry_plot_title.grid(row=17, column=1, sticky=W, padx=(30, 0))

        self.update_entry_plot_title_status()

        # Tooltips
        Hovertip(self.checkbox_timestamp_extract, tooltip_checkbox_timestamp_text)
        Hovertip(self.textbox_rows, tooltip_textbox_rows)
        Hovertip(self.entry_columns_to_process, tooltip_entry_columns_to_process)
        Hovertip(self.radiobutton_read_delimiter_type_1, tooltip_radiobutton_read_file_delimiter)
        Hovertip(self.radiobutton_read_delimiter_type_2, tooltip_radiobutton_read_file_delimiter)
        Hovertip(self.radiobutton_write_delimiter_type_1, tooltip_radiobutton_write_file_delimiter)
        Hovertip(self.radiobutton_write_delimiter_type_2, tooltip_radiobutton_write_file_delimiter)
        Hovertip(self.entry_header_row, tooltip_entry_header_row)
        Hovertip(self.entry_data_start_row, tooltip_entry_data_start_row)
        Hovertip(self.entry_data_length_requested, tooltip_entry_data_end_row)
        Hovertip(self.radiobutton_action_1, tooltip_radiobutton_action_1)
        Hovertip(self.radiobutton_action_2, tooltip_radiobutton_action_2)
        # END OF FRAME #######################################################

        ######################################################################
        # Frame Commands
        self.button_open_folder = Button(self.frame_root_commands, text="Open Folder",
                                         command=lambda: self.open_folder(self.user_entry.file_location),
                                         pady=3, width=20)
        self.button_load_defaults = Button(self.frame_root_commands, text="Load Defaults",
                                           command=self.load_defaults, pady=3, width=20)
        self.button_plot_data = Button(self.frame_root_commands, text="Plot Data", pady=3, width=20,
                                       command=self.start_plot_figures)
        self.button_process_file = Button(self.frame_root_commands, text="Process File", pady=3, width=20, fg="green",
                                          command=self.process_file)
        self.button_save_plots = Button(self.frame_root_commands, text="Save Plots", pady=3, width=20,
                                        command=self.start_save_figures)
        self.button_exit = Button(self.frame_root_commands, text="Exit", fg='red', command=self.quit_program, pady=3,
                                  width=20)
        self.button_save_csv = Button(self.frame_root_commands, text="Save CSV", pady=3, width=20,
                                      command=self.start_save_csv)
        self.button_close_plots = Button(self.frame_root_commands, text="Close Plots", command=self.close_plots,
                                         pady=3, width=20)

        # Grids
        self.button_open_folder.grid(row=1, column=1, padx=(2, 0))
        self.button_load_defaults.grid(row=2, column=1, padx=(2, 0))
        self.button_plot_data.grid(row=1, column=2)
        self.button_save_plots.grid(row=2, column=2)
        self.button_process_file.grid(row=1, column=3)
        self.button_save_csv.grid(row=2, column=3)
        self.button_exit.grid(row=1, column=4)
        self.button_close_plots.grid(row=2, column=4)

        # self.gui_process_file_button_disable()
        # self.gui_plot_data_button_disable()
        # END OF FRAME #######################################################

        self.root_frame.mainloop()

    ######################################################################

    def setState(self, widget, state):
        print(type(widget))
        try:
            widget.configure(state=state)
        except:
            pass
        for child in widget.winfo_children():
            self.setState(child, state=state)

    def gui_entry_unlock(self):
        self.setState(self.frame_root_session, state='normal')
        self.setState(self.frame_root_commands, state='normal')

    # Disable user entries in offline mode
    def gui_entry_lock(self):
        self.setState(self.frame_root_session, state='disabled')
        self.setState(self.frame_root_commands, state='disabled')

    def entry_update_header_row(self):
        try:
            entry_header_row = self.entry_header_row_entry.get()
            self.user_entry.header_row_index = int(entry_header_row)
            print("::user_entry.header_row_index: ", self.user_entry.header_row_index)
        except:
            self.user_entry.header_row_index = ROW_HEADER
            print("::user_entry.header_row_index: ", self.user_entry.header_row_index)

    def entry_update_data_start_row(self):
        try:
            entry_data_start_row = self.entry_data_start_row_entry.get()
            self.user_entry.data_start_row_index = int(entry_data_start_row)
            print("::user_entry.data_start_row_index: ", self.user_entry.data_start_row_index)
        except:
            self.user_entry.data_start_row_index = DATA_ROW_START_INDEX_DEFAULT
            print("::user_entry.data_start_row_index: ", self.user_entry.data_start_row_index)

    def entry_update_data_length_requested(self):
        try:
            data_length_requested = self.entry_data_length_requested_entry.get()
            self.user_entry.data_length_requested = int(data_length_requested)
            print("::user_entry.data_length_requested: ", self.user_entry.data_length_requested)
        except:
            self.user_entry.data_length_requested = DATA_LENGTH_REQUESTED_DEFAULT
            print("::user_entry.data_length_requested: ", self.user_entry.data_length_requested)

    def entry_update_plot_title(self):
        try:
            plot_title = self.entry_plot_title_entry.get()
            self.user_entry.plot_title = plot_title
            print("::user_entry.plot_title: ", self.user_entry.plot_title)
        except:
            self.user_entry.plot_title = PLOT_TITLE
            print("::user_entry.plot_title: ", self.user_entry.plot_title)

    def entry_update_rows_to_peak(self):
        try:
            entry_rows_to_peak = self.entry_rows_to_peak_entry.get()
            self.user_entry.n_rows_to_peak = int(entry_rows_to_peak)
            print("::user_entry.n_rows_to_peak: ", self.user_entry.n_rows_to_peak)
        except:
            self.user_entry.data_start_row_index = N_ROWS_TO_PEAK
            print("::user_entry.erows_to_peak: ", self.user_entry.n_rows_to_peak)
        self.rows_to_peak = [0] * self.user_entry.n_rows_to_peak

    def entry_update_columns_to_process(self):
        entry_columns_to_process_split = []
        try:
            entry_columns_to_process_string = self.entry_columns_to_process_entry.get()
            entry_columns_to_process_split.extend(entry_columns_to_process_string.split(','))
            self.user_entry.column_choice_list = [int(item) for item in entry_columns_to_process_split]
        except:
            pass
        print("::user_entry.column_choice_list: ", self.user_entry.column_choice_list)

    def entry_update_file_location(self):
        file_location = self.entry_file_location_entry.get()
        if fm.FileNameMethods.check_file_location_valid(file_location):
            self.user_entry.file_location = file_location
        else:
            self.user_entry.file_location = FILE_LOCATION
        print("::user_entry.file_location: ", self.user_entry.file_location)

    def entry_update_file_name_and_suffix(self):
        file_name_suffix = self.entry_file_name_entry.get()
        file_name = os.path.splitext(file_name_suffix)[0]
        file_suffix = os.path.splitext(file_name_suffix)[1]

        if fm.FileNameMethods.check_filename_components_exists(self.user_entry.file_location, file_name, file_suffix):
            self.user_entry.file_name = file_name
            self.user_entry.file_suffix = file_suffix
            # try:
            #     self.gui_process_file_button_enable()
            # except Exception as e:
            #     e = None
        else:
            self.user_entry.file_name = FILE_NAME
            self.user_entry.file_suffix = FILE_SUFFIX
            # try:
            #     self.gui_process_file_button_enable()
            # except Exception as e:
            #     e = None
        print("::user_entry.file_name: ", self.user_entry.file_name)
        print("::user_entry.file_suffix: ", self.user_entry.file_suffix)

    def load_defaults(self):
        # Entries
        self.entry_file_location.delete(0, END)
        self.entry_file_name.delete(0, END)
        self.entry_columns_to_process.delete(0, END)
        self.entry_header_row.delete(0, END)
        self.entry_data_start_row.delete(0, END)
        self.entry_data_length_requested.delete(0, END)
        self.entry_rows_to_peak.delete(0, END)

        # Reload defaults values
        # Reload text entries
        self.user_entry.file_location = FILE_LOCATION
        self.entry_file_location.insert(0, os.path.normcase(self.user_entry.file_location))
        self.user_entry.file_name = FILE_NAME
        self.entry_file_name.insert(0, (self.user_entry.file_name if self.user_entry.file_name else FILE_NAME_INIT))

        self.entry_columns_to_process.insert(0, PROCESS_ALL_COLUMNS)
        self.entry_header_row.insert(0, ROW_HEADER)
        self.entry_data_start_row.insert(0, DATA_ROW_START_INDEX_DEFAULT)
        self.entry_data_length_requested.insert(0, DATA_LENGTH_REQUESTED_DEFAULT)
        self.entry_rows_to_peak.insert(0, N_ROWS_TO_PEAK)
        self.textbox_row_clear()

        # Reset radiobuttons
        self.user_entry.action = PROCESS_ONLY
        self.user_entry.read_delimiter_type = DELIMITER_TYPE_COMMA
        self.user_entry.write_delimiter_type = DELIMITER_TYPE_COMMA

        self.radiobutton_action_entry.set(self.user_entry.action)
        self.radiobutton_read_delimiter_type_entry.set(self.user_entry.read_delimiter_type)
        self.radiobutton_write_delimiter_type_entry.set(self.user_entry.write_delimiter_type)

        # Reset Checkboxes
        # self.user_entry.header_include_files = HEADER_INCLUDE_FILES_NOT
        self.user_entry.header_include_plots = HEADER_INCLUDE_PLOTS_NOT
        self.user_entry.plots_overlap = PLOTS_OVERLAP
        # self.checkbox_header_include_files_entry.set(self.user_entry.header_include_plots)
        self.checkbox_header_include_plots_entry.set(self.user_entry.header_include_files)
        self.checkbox_plots_overlap_entry.set(self.user_entry.plots_overlap)

        message = 'Defaults Loaded\n'
        message_colour = 'blue'
        self.session_log.write_textbox(message, message_colour)

        try:
            del self.session_process_csv
        except Exception as e:
            pass

        self.close_plots()
        self.root_frame.mainloop()

    def close_plots(self):
        # if self.session_process_csv:
        try:
            self.session_process_csv.close_plots()
        except:
            pass

    @staticmethod
    def quit_program():
        # quit()  # quit() does not work with pyinstaller, use sys.exit()
        sys.exit()

    def peak_file(self):
        try:
            if fm.FileNameMethods.check_filename_components_exists(self.user_entry.file_location,
                                                                   self.user_entry.file_name,
                                                                   self.user_entry.file_suffix) is not True:
                message = 'Invalid file\n'
                message_colour = 'red'
                self.session_log.write_textbox(message, message_colour)
                messagebox.showerror('Error', message)
                return
        except Exception as e:
            e = 'Invalid file\n'
            message_colour = 'red'
            self.session_log.write_textbox(e, message_colour)
            messagebox.showerror('Error', e)
            return

        message = 'Peak File: ' + fm.FileNameMethods.build_file_name_full(
            self.user_entry.file_location, self.user_entry.file_name, self.user_entry.file_suffix) + '\n'
        message_colour = 'brown'
        self.session_log.write_textbox(message, message_colour)

        self.session_process_csv = SessionProcessCSV(self.user_entry, self.session_log, self.textbox_rows,
                                                     self.session_option)

    def process_file(self):
        self.session_option = OPTION_PROCESS_FILE

        if not self.user_entry.multi_files:
            # Check File exists
            try:
                if fm.FileNameMethods.check_filename_components_exists(self.user_entry.file_location,
                                                                       self.user_entry.file_name,
                                                                       self.user_entry.file_suffix) is not True:
                    message = 'Invalid file\n'
                    message_colour = 'red'
                    self.session_log.write_textbox(message, message_colour)
                    messagebox.showerror('Error', message)
                    return
            except Exception as e:
                e = 'Invalid file\n'
                message_colour = 'red'
                self.session_log.write_textbox(e, message_colour)
                messagebox.showerror('Error', e)
                return

            message = 'Start Session\n'
            message_colour = 'brown'
            self.session_log.write_textbox(message, message_colour)

            self.display_session_settings()
            # self.gui_entry_lock()
            self.session_process_csv = SessionProcessCSV(self.user_entry, self.session_log, self.textbox_rows,
                                                         self.session_option)
            # self.gui_entry_unlock()

            message = 'Finish Session\n'
            message_colour = 'brown'
            self.session_log.write_textbox(message, message_colour)

        else:
            # Check Files exist
            for file in self.user_entry.multi_file_list:
                try:
                    if fm.FileNameMethods.check_filename_full_exists(file) is not True:
                        message = 'Invalid file\n'
                        message_colour = 'red'
                        self.session_log.write_textbox(message, message_colour)
                        messagebox.showerror('Error', message)
                        return
                except Exception as e:
                    e = 'Invalid file\n'
                    message_colour = 'red'
                    self.session_log.write_textbox(e, message_colour)
                    messagebox.showerror('Error', e)
                    return

            message = 'Start Session\n'
            message_colour = 'brown'
            self.session_log.write_textbox(message, message_colour)

            if not self.user_entry.multi_files:
                self.display_session_settings()
            # self.gui_entry_lock()

            self.session_process_csv = SessionProcessCSV(self.user_entry, self.session_log, self.textbox_rows,
                                                         self.session_option)
            # self.gui_entry_unlock()

            message = 'End of Session\n'
            message_colour = 'brown'
            self.session_log.write_textbox(message, message_colour)

    ######################################################################

    ######################################################################
    def hide_button_choose_single_file(self):
        self.button_choose_single_file.grid_forget()

    def show_button_choose_single_file(self):
        self.button_choose_single_file.grid(row=6, column=0, sticky=E)

    def hide_button_choose_multi_files(self):
        self.button_choose_multi_files.grid_forget()

    def show_button_choose_multi_files(self):
        self.button_choose_multi_files.grid(row=6, column=0, sticky=E)

    def enable_button_file_peak(self):
        self.button_file_peak["state"] = ACTIVE

    def disable_button_file_peak(self):
        self.button_file_peak["state"] = DISABLED

    def enable_entry_plot_title(self):
        self.entry_plot_title["state"] = NORMAL

    def disable_entry_plot_title(self):
        self.entry_plot_title["state"] = DISABLED

    def update_entry_plot_title_status(self):
        if self.user_entry.include_plot_title:
            self.enable_entry_plot_title()
        else:
            self.disable_entry_plot_title()

    # Methods for data files
    def choose_file(self):
        # Clear entry fields before selecting file, else the entry will be cleared after file is selected
        # and the user_entry fields will be cleared as well
        file_location_current = self.user_entry.file_location
        self.entry_file_name.delete(0, END)
        self.entry_file_location.delete(0, END)

        file_type = [('csv', '*.csv')]
        file_full_name = filedialog.askopenfilename(initialdir=file_location_current,
                                                    title="Select File", filetypes=file_type,
                                                    defaultextension=file_type)
        self.user_entry.file_name = os.path.splitext(os.path.basename(file_full_name))[0]
        self.user_entry.file_suffix = os.path.splitext(os.path.basename(file_full_name))[1]
        self.user_entry.file_location = os.path.dirname(file_full_name)

        self.entry_file_name.insert(0, (self.user_entry.file_name + self.user_entry.file_suffix))
        self.entry_file_location.insert(0, os.path.normcase(self.user_entry.file_location))
        message = 'File Loaded: ' + str(file_full_name) + '\n'
        message_colour = 'black'
        self.session_log.write_textbox(message, message_colour)
        print("::file name: ", self.user_entry.file_name)
        print("::file suffix: ", self.user_entry.file_suffix)
        print("::file location: ", self.user_entry.file_location)

    def choose_multi_file(self):
        # Clear entry fields before selecting file, else the entry will be cleared after file is selected
        # and the user_entry fields will be cleared as well
        file_location_current = self.user_entry.file_location
        self.entry_file_name.delete(0, END)
        # self.entry_file_location.delete(0, END)

        file_type = [('csv', '*.csv')]
        self.user_entry.multi_file_list = filedialog.askopenfilenames(initialdir=file_location_current,
                                                                      title="Select Files", filetypes=file_type,
                                                                      defaultextension=file_type)

        self.user_entry.n_multi_files = len(self.user_entry.multi_file_list)
        message = "Number of Files to Process: " + str(self.user_entry.n_multi_files) + '\n'
        message_colour = "brown"
        self.session_log.write_textbox(message, message_colour)

        for file in self.user_entry.multi_file_list:
            self.user_entry.multi_file_name.append(os.path.splitext(os.path.basename(file))[0])
            self.user_entry.multi_file_suffix.append(os.path.splitext(os.path.basename(file))[1])
            self.user_entry.multi_file_location.append(os.path.dirname(file))
        self.entry_file_location.delete(0, END)
        self.entry_file_location.insert(0, os.path.normcase(self.user_entry.multi_file_location[0]))
        message = 'Files Loaded: \n'
        message_colour = 'black'
        self.session_log.write_textbox(message, message_colour)
        for file in self.user_entry.multi_file_list:
            message = '\t' + str(file) + '\n'
            message_colour = 'black'
            self.session_log.write_textbox(message, message_colour)

    def button_file_peak(self):
        self.session_option = OPTION_PEAK_FILE
        self.peak_file()

    def open_folder(self, folder_path):
        temp_path = os.path.realpath(folder_path)
        try:
            os.startfile(temp_path)
        except:
            try:
                os.mkdir(FILE_LOCATION)
                self.user_entry.file_location = FILE_LOCATION
                self.session_log.write_textbox("Folder Created", "blue")
                print("Folder Created")
            except OSError as e:
                print("Failed to Create Folder")
                e = Exception("Failed to Create Folder")
                self.session_log.write_textbox(str(e), "red")
                raise e

    def start_plot_figures(self):
        try:
            self.session_process_csv.plot_data()
        except:
            self.message_box('Save Error', 'No Data to Plot')

    def start_save_figures(self):
        try:
            if self.session_process_csv.figure_list is not None:
                self.save_figure_list()
        except:
            self.message_box('Save Error', 'No Plots Loaded to Save')

    def save_figure_list(self):
        message = 'Saving figures in: ' + str(self.user_entry.file_location) + '\n'
        colour = 'black'
        self.session_log.write_textbox(message, colour)
        for fig in self.session_process_csv.figure_list:
            file_name = str(self.user_entry.file_name) + '-' + str(fig.number)  # First column in headers is "timestamp"
            print("::file_name: ", file_name)
            self._save_figure(self.user_entry.file_location, file_name)
            self.session_log.write_textbox("Figure saved: ", "green")
            fig.savefig((str(self.user_entry.file_location) + "/" + str(file_name) + ".png"))
            self.session_log.write_textbox_append(file_name + ".png" + '\n', "blue")

    def _save_figure(self, folder, file_name):
        file_address = (folder + "/" + file_name + '.png')
        if os.path.isfile(file_address):
            self.session_log.write_textbox("Figure Exists and Will Be Overwritten: ", "red")
        plt.savefig((str(self.user_entry.file_location) + "/" + str(file_name) + ".png"))

    def start_save_csv(self):
        file_location = self.user_entry.file_location
        delimiter = self.user_entry.write_delimiter_type

        if self.user_entry.multi_files:
            file_name = FILE_NAME_MULTI_FILE_SAVE
            if self.user_entry.timestamp_include:
                data_to_write = self.session_process_csv.data_requested_with_timestamps_np_multi_file_2D
            else:
                data_to_write = self.session_process_csv.data_requested_np_multi_file_2D

            if self.user_entry.header_include_plots:
                if self.user_entry.timestamp_include:
                    headers = np.concatenate((['t'], self.session_process_csv.headers_np_multi_file_2D))
                else:
                    headers = self.session_process_csv.headers_np_multi_file_2D
            else:
                headers = None

        else:
            file_name = str(self.user_entry.file_name + self.user_entry.file_name_save)
            if self.user_entry.timestamp_include:
                data_to_write = self.session_process_csv.data_requested_with_timestamp_np
            else:
                data_to_write = self.session_process_csv.data_requested_np

            if self.user_entry.header_include_plots:
                headers = self.session_process_csv.headers_np[self.session_process_csv.columns_indices_to_process]
                if self.user_entry.timestamp_include:
                    headers = np.concatenate((['t'], headers))
            else:
                headers = None

        self.save_csv(file_name, file_location, data_to_write, delimiter, headers=headers)

    def save_csv(self, file_name, file_location, data_to_write, delimiter, headers):
        if headers is not None:
            self._save_data_pandas_header_delimiter(file_location, file_name, data_to_write, headers, delimiter)
        else:
            self._save_data_pandas_delimiter(file_location, file_name, data_to_write, delimiter)

        self.session_log.write_textbox("File saved: ", "green")
        self.session_log.write_textbox_append(file_name + '\n', "blue")

    def _save_data_pandas_delimiter(self, folder, file_name, data, delimiter):
        file_address = (folder + "\\" + file_name + '.csv')
        if os.path.isfile(file_address):
            self.session_log.write_textbox("File Exists and Will Be Overwritten: ", "red")
        if delimiter == DELIMITER_TYPE_COMMA:
            pd.DataFrame(data).to_csv(file_address, index=False, header=False, sep=',')
        elif delimiter == DELIMITER_TYPE_TAB:
            pd.DataFrame(data).to_csv(file_address, index=False, header=False, sep='\t')

    def _save_data_pandas_header_delimiter(self, folder, file_name, data, header_list, delimiter):
        file_address = (folder + "\\" + file_name + '.csv')
        if os.path.isfile(file_address):
            self.session_log.write_textbox("File Exists and Will Be Overwritten: ", "red")

        print("header_list: ", header_list)
        print(data)

        if delimiter == DELIMITER_TYPE_COMMA:
            pd.DataFrame(data).to_csv(file_address, index=False, header=header_list, sep=',')
        elif delimiter == DELIMITER_TYPE_TAB:
            pd.DataFrame(data).to_csv(file_address, index=False, header=header_list, sep='\t')

    def _save_data_pandas(self, folder, file_name, data):
        file_address = (folder + "/" + file_name + '.csv')
        if os.path.isfile(file_address):
            self.session_log.write_textbox("File Exists and Will Be Overwritten: ", "red")
        pd.DataFrame(data).to_csv(file_address, index=False, header=False)

    ######################################################################

    @staticmethod
    def message_box(title, data):
        try:
            messagebox.showinfo(title=title, message=data)
        except:
            data = 'Invalid data'

    def display_session_settings(self):
        message = 'File To Process: ' + fm.FileNameMethods.build_file_name_full(
            self.user_entry.file_location, self.user_entry.file_name, self.user_entry.file_suffix) + '\n'
        colour = "blue"
        self.session_log.write_textbox(message, colour)

        message = 'Extract Timestamp: ' + ('yes' if self.user_entry.timestamp_extract == 1 else 'no') + '\n'
        self.session_log.write_textbox(message, colour)

        message = 'Read Delimiter: ' + (
            'Comma' if self.user_entry.read_delimiter_type == DELIMITER_TYPE_COMMA else 'Tab') + '\n'
        self.session_log.write_textbox(message, colour)

        message = ' Header at Row: ' + str(self.user_entry.header_row_index) + '\n'
        self.session_log.write_textbox(message, colour)

        message = 'Data Start at Row: ' + str(self.user_entry.data_start_row_index) + '\n'
        self.session_log.write_textbox(message, colour)

        message = 'Data Length Requested: ' + str(self.user_entry.data_length_requested) + '\n'
        self.session_log.write_textbox(message, colour)

        message = 'Include Header in Plot: ' + str(self.user_entry.header_include_plots) + '\n'
        self.session_log.write_textbox(message, colour)

    def radiobutton_action(self):
        radiobutton_action = self.radiobutton_action_entry.get()
        self.user_entry.action = radiobutton_action
        print("::user_entry.action: ", self.user_entry.action)

    def radiobutton_read_delimiter_type(self):
        radiobutton_read_delimiter_type = self.radiobutton_read_delimiter_type_entry.get()
        self.user_entry.read_delimiter_type = radiobutton_read_delimiter_type
        print("::user_entry.read_delimiter_type: ", self.user_entry.read_delimiter_type)

    def radiobutton_write_delimiter_type(self):
        radiobutton_write_delimiter_type = self.radiobutton_write_delimiter_type_entry.get()
        self.user_entry.write_delimiter_type = radiobutton_write_delimiter_type
        print("::user_entry.write_delimiter_type: ", self.user_entry.write_delimiter_type)

    def radiobutton_column_choice_option(self):
        radiobutton_column_choice_option = self.radiobutton_column_choice_entry.get()
        self.user_entry.column_choice_option = radiobutton_column_choice_option
        if self.user_entry.column_choice_option is COLUMNS_ALL:
            self.entry_columns_to_process.configure(state='disabled')
        else:
            self.entry_columns_to_process.configure(state='normal')
        print("::user_entry.radiobutton_column_choice_option: ", self.user_entry.column_choice_option)

    def checkbox_update_multi_files(self):
        checkbox_multi_files_entry = self.checkbox_multi_files_entry.get()
        self.user_entry.multi_files = checkbox_multi_files_entry
        print("::user_entry.multi_files: ", self.user_entry.multi_files)
        if self.user_entry.multi_files:
            self.entry_file_name.configure(state='disabled')
            self.hide_button_choose_single_file()
            self.disable_button_file_peak()
            self.show_button_choose_multi_files()
            self.textbox_update("Processing Multiple Files\nPeak Not Available")
        else:
            self.entry_file_name.configure(state='normal')
            self.hide_button_choose_multi_files()
            self.show_button_choose_single_file()
            self.enable_button_file_peak()
            self.textbox_update(FILE_NAME_INIT)

    def checkbox_update_timestamp_extract(self):
        checkbox_timestamp_extract_entry = self.checkbox_timestamp_extract_entry.get()
        self.user_entry.timestamp_extract = checkbox_timestamp_extract_entry
        print("::user_entry.timestamp_extract: ", self.user_entry.timestamp_extract)

    def checkbox_update_timestamp_include(self):
        checkbox_timestamp_include_entry = self.checkbox_timestamp_include_entry.get()
        self.user_entry.timestamp_include = checkbox_timestamp_include_entry
        print("::user_entry.timestamp_include: ", self.user_entry.timestamp_include)

    # def checkbox_update_header_include_files(self):
    #     checkbox_header_include_files_entry = self.checkbox_header_include_files_entry.get()
    #     self.user_entry.header_include_files = checkbox_header_include_files_entry
    #     print("::user_entry.header_include_files: ", self.user_entry.header_include_files)

    def checkbox_update_header_include_plots(self):
        checkbox_header_include_plots_entry = self.checkbox_header_include_plots_entry.get()
        self.user_entry.header_include_plots = checkbox_header_include_plots_entry
        print("::user_entry.header_include_plots: ", self.user_entry.header_include_plots)

    def checkbox_update_plots_overlap(self):
        checkbox_plots_overlap_entry = self.checkbox_plots_overlap_entry.get()
        self.user_entry.plots_overlap = checkbox_plots_overlap_entry
        print("::user_entry.plots_overlap: ", self.user_entry.plots_overlap)

    def checkbox_update_include_plot_title(self):
        checkbox_include_plot_title_entry = self.checkbox_include_plot_title_entry.get()
        self.user_entry.include_plot_title = checkbox_include_plot_title_entry
        print("::user_entry.include_plot_title: ", self.user_entry.include_plot_title)
        self.update_entry_plot_title_status()

    def textbox_row_clear(self):
        self.textbox_rows.configure(state='normal')
        self.textbox_rows.delete('1.0', 'end')
        self.textbox_rows.insert('end', 'No Files Loaded')
        self.textbox_rows.configure(state='disabled')

    def textbox_update(self, data):
        self.textbox_rows.configure(state='normal')
        self.textbox_rows.delete('1.0', 'end')
        self.textbox_rows.insert('end', data)
        self.textbox_rows.configure(state='disabled')
