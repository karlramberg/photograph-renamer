import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd

class PhotographRenamer:
    def __init__(self, master=None):
        # Create main window and frame
        window = tk.Tk()
        frame = ttk.Frame(window)

        # File picker -------------------------------------------------------------------------------------------------
        folder_picker_frame = ttk.LabelFrame(frame, text="Choose a folder")

        folder_picker_input = ttk.Entry(folder_picker_frame, textvariable="")
        folder_picker_input.pack(expand=True, fill='x', side='left')

        folder_picker_button = ttk.Button(folder_picker_frame, text="Choose folder")
        folder_picker_button.pack(side='left')
        # TODO: add button functionality
        
        folder_picker_frame.pack(fill='x', side='top')

        # Folder tree view
        file_tree_frame = ttk.LabelFrame(frame, text="Select photographs")

        file_treeview = ttk.Treeview(file_tree_frame, columns=('filename', 'date'))
        file_treeview.config(selectmode='extended')
        file_treeview['show'] = 'headings'
        file_treeview.heading("filename", text="File name", anchor='w')
        file_treeview.heading("date", text="Date", anchor='w')
        file_treeview.pack(expand=True, fill='x', side='left')

        file_treeview_scrollbar = ttk.Scrollbar(file_tree_frame, orient="vertical")
        file_treeview_scrollbar.configure(command = file_treeview.yview)
        file_treeview.config(yscrollcommand=file_treeview_scrollbar.set)
        file_treeview_scrollbar.pack(side='left', fill='y')

        file_tree_frame.pack(fill='x', side='top')

        # Filename construction ---------------------------------------------------------------------------------------
        construct_filename_frame = ttk.LabelFrame(frame, text="Construct filename")

        auto_filename_options_frame = ttk.Frame(construct_filename_frame)
        self.manual_date_frame = ttk.Frame(construct_filename_frame)
        self.manual_number_frame = ttk.Frame(construct_filename_frame)

        # Auto file naming
        self.auto_date = tk.BooleanVar()
        self.auto_date.set(False)

        auto_date_checkbox = ttk.Checkbutton(auto_filename_options_frame)
        auto_date_checkbox.configure(text="Grab date from metadata", variable=self.auto_date, command=self.toggle_date_entry)
        auto_date_checkbox.pack(side='left', padx=5)

        self.auto_number = tk.BooleanVar()
        self.auto_number.set(False)
        auto_number_checkbox = ttk.Checkbutton(auto_filename_options_frame)
        auto_number_checkbox.configure(text="Add number automatically", variable=self.auto_number, command=self.toggle_number_entry)
        auto_number_checkbox.pack(side='left', padx=5)

        auto_filename_options_frame.pack(fill='x', side='top')

        # Manual date entry
        year_label = ttk.Label(self.manual_date_frame, text="  Year: ")
        year_label.pack(side='left')
        year_entry = ttk.Entry(self.manual_date_frame, textvariable="", width=5)
        year_entry.pack(side='left')

        month_label = ttk.Label(self.manual_date_frame, text="  Month: ")
        month_label.pack(side='left')
        month_entry = ttk.Combobox(self.manual_date_frame, state='readonly', width=10,
            values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        month_entry.pack(side='left')

        day_label = ttk.Label(self.manual_date_frame, text="  Day: ")
        day_label.pack(side='left')
        day_entry = ttk.Entry(self.manual_date_frame, textvariable="", width=3)
        day_entry.pack(side='left')

        # Manual number entry
        number_label = ttk.Label(self.manual_number_frame, text="  Number: ")
        number_label.pack(side='left')
        number_entry = ttk.Entry(self.manual_number_frame, textvariable="", width=4)
        number_entry.pack(side='left')

        self.manual_date_frame.pack(fill='x', side='left')
        self.manual_number_frame.pack(fill='x', side='left')
        construct_filename_frame.pack(fill='x', side='top')

        # Rename button -----------------------------------------------------------------------------------------------
        rename_button = ttk.Button(frame, text="Rename file(s)", command=self.rename_files)
        rename_button.pack(side='bottom')

        self.toggle_date_entry()
        self.toggle_number_entry()

        frame.config(width="500", height="600")
        frame.pack(expand=True, fill='both', side='top', padx=5, pady=5)
        window.geometry('500x600')
        window.resizable(False, False)
        window.title("Photograph Renamer")
        self.window = window

    # Enable of disable the UI for manual date entry based on the corresponding checkbox
    def toggle_date_entry(self):
        if self.auto_date.get():
            for child in self.manual_date_frame.winfo_children():
                child.configure(state='disable')
        else:
            for child in self.manual_date_frame.winfo_children():
                child.configure(state='enable')

    # Enable or disable the UI for manual sequence number entry based on the corresponding checkbox
    def toggle_number_entry(self):
        if self.auto_number.get():
            for child in self.manual_number_frame.winfo_children():
                child.configure(state='disable')
        else:
            for child in self.manual_number_frame.winfo_children():
                child.configure(state='enable')

    # TODO Rename files selected in the treeview using date and sequence number
    def rename_files(self):
        print("renaming selected files")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    application = PhotographRenamer()
    application.run()