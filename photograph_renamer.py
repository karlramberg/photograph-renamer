# TODO:
#     Film roll lettering
#     Image previews
#     File renaming from treeview selection
#     Polish UI
#     Folder selection
#     Treeview population
#     Auto dating from metadata
#     Auto numbering from selection
#     Refresh treeview button
  
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as fd
from PIL import Image, ImageTk

class PhotographRenamer:
    def __init__(self, master=None):
        # Create main window and frame
        window = tk.Tk()
        frame = ttk.Frame(window)

        # Choose folder -----------------------------------------------------------------------------------------------------------------------------
        choose_folder = ttk.LabelFrame(frame, text="Choose folder")

        self.folder = ttk.Entry(choose_folder, textvariable="")
        self.folder.pack(expand=True, fill='x', side='left')

        choose_folder_button = ttk.Button(choose_folder, text="Choose folder") # TODO add functionality
        choose_folder_button.pack(side='left')
        
        choose_folder.pack(fill='x', side='top')

        # Select files --------------------------------------------------------------------------------------------------------------------------
        select_files = ttk.LabelFrame(frame, text="Select files")

        file_list_frame = ttk.Frame(select_files)
        self.file_list = ttk.Treeview(file_list_frame, columns=('filename', 'date_created'))
        self.file_list.config(selectmode='extended')
        self.file_list['show'] = 'headings'
        self.file_list.heading("filename", text="File name", anchor='w')
        self.file_list.heading("date_created", text="Date created", anchor='w')
        self.file_list.pack(expand=True, fill='x', side='left')

        file_list_scrollbar = ttk.Scrollbar(file_list_frame, orient="vertical")
        file_list_scrollbar.configure(command = self.file_list.yview)
        self.file_list.config(yscrollcommand=file_list_scrollbar.set)
        file_list_scrollbar.pack(side='left', fill='both')

        file_list_control_frame = ttk.Frame(select_files)
        select_all_button = ttk.Button(file_list_control_frame, text="Select all") # TODO add functionality
        select_all_button.pack(side='left')

        refresh_file_list = ttk.Button(file_list_control_frame, text="Refresh folder") # TODO add functionality
        refresh_file_list.pack(side='left')

        file_list_frame.pack(side='top', fill='x')
        file_list_control_frame.pack(side='top', fill='x')
        select_files.pack(fill='x', side='top')

        # Filename construction ---------------------------------------------------------------------------------------
        construct_filename = ttk.LabelFrame(frame, text="Construct filename")

        # Construction options
        filename_options = ttk.Frame(construct_filename)

        # Auto date option
        self.auto_dating = tk.BooleanVar()
        self.auto_dating.set(False)
        auto_date_checkbox = ttk.Checkbutton(filename_options)
        auto_date_checkbox.configure(text="Grab date from metadata", variable=self.auto_dating, command=self.toggle_date_entry)
        auto_date_checkbox.pack(side='left', padx=5)

        # Auto sequence number option
        self.auto_numbering = tk.BooleanVar()
        self.auto_numbering.set(False)
        auto_number_checkbox = ttk.Checkbutton(filename_options)
        auto_number_checkbox.configure(text="Add number automatically", variable=self.auto_numbering, command=self.toggle_number_entry)
        auto_number_checkbox.pack(side='left', padx=5)

        # Roll letter option
        self.roll_film= tk.BooleanVar()
        self.roll_film.set(False)
        roll_film_checkbox = ttk.Checkbutton(filename_options)
        roll_film_checkbox.configure(text="Roll film", variable=self.roll_film, command=self.toggle_roll_film)
        roll_film_checkbox.pack(side='left', padx=5)

        filename_options.pack(fill='x', side='top')

        # Data entry
        filename_entries = ttk.Frame(construct_filename)

        # Manual date entry
        self.manual_date_frame = ttk.Frame(filename_entries)

        year_label = ttk.Label(self.manual_date_frame, text="  Year: ")
        year_label.pack(side='left')
        self.year = ttk.Entry(self.manual_date_frame, textvariable="", width=5)
        self.year.pack(side='left')

        month_label = ttk.Label(self.manual_date_frame, text="  Month: ")
        month_label.pack(side='left')
        self.month = ttk.Combobox(self.manual_date_frame, state='readonly', width=10,
            values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        self.month.pack(side='left')

        day_label = ttk.Label(self.manual_date_frame, text="  Day: ")
        day_label.pack(side='left')
        self.day = ttk.Entry(self.manual_date_frame, textvariable="", width=3)
        self.day.pack(side='left')

        self.manual_date_frame.pack(fill='x', side='left')

        # Roll letter entry
        self.roll_letter_frame = ttk.Frame(filename_entries)

        roll_letter_label = ttk.Label(self.roll_letter_frame, text="  Roll letter: ")
        roll_letter_label.pack(side='left')
        self.roll_letter = ttk.Entry(self.roll_letter_frame, textvariable="", width=3)
        self.roll_letter.pack(side='left')
        self.roll_letter_empty = ttk.Label(self.roll_letter_frame, text="")

        self.roll_letter_frame.pack(fill='x', side='left')

        # Manual number entry
        self.manual_number_frame = ttk.Frame(filename_entries)

        number_label = ttk.Label(self.manual_number_frame, text="  Number: ")
        number_label.pack(side='left')
        self.sequence_number = ttk.Entry(self.manual_number_frame, textvariable="", width=4)
        self.sequence_number.pack(side='left')
        self.manual_number_frame.pack(fill='x', side='left')

        filename_entries.pack(fill='x', side='top')

        construct_filename.pack(fill='x', side='top')

        # Image preview
        image_preview = ttk.LabelFrame(frame, text="Image preview")

        # TODO temporary cat pic
        self.image = Image.open("cat.jpeg")
        self.image.thumbnail((400,400))
        self.image = ImageTk.PhotoImage(self.image)
        image_container = ttk.Label(image_preview, image=self.image)
        image_container.pack(fill="both", side='top')

        image_preview.pack(fill='y', side='left')

        # Current filename and rename button
        self.current_filename_label = ttk.Label(frame, textvariable="")
        self.update_filename_label()

        rename_button = ttk.Button(frame, text="Rename file(s)", command=self.rename_files)
        rename_button.pack(side='bottom')
        self.current_filename_label.pack(side='bottom', pady=5)

        self.toggle_date_entry()
        self.toggle_number_entry()
        self.toggle_roll_film()

        frame.config(width="500", height="600")
        frame.pack(expand=True, fill='both', side='top', padx=5, pady=5)
        window.geometry('500x800')
        window.resizable(False, False)
        window.title("Photograph Renamer")
        self.window = window

    # Enable of disable the UI for manual date entry based on the corresponding checkbox
    def toggle_date_entry(self):
        if self.auto_dating.get():
            for child in self.manual_date_frame.winfo_children():
                child.configure(state='disable')
        else:
            for child in self.manual_date_frame.winfo_children():
                child.configure(state='enable')

    # Enable or disable the UI for film roll letters
    def toggle_roll_film(self):
        if self.roll_film.get():
            for child in self.roll_letter_frame.winfo_children():
                child.pack(side='left')
            self.roll_letter_empty.pack_forget()
        else:
            for child in self.roll_letter_frame.winfo_children():
                child.pack_forget()
            self.roll_letter_empty.pack(side='left')

    # Enable or disable the UI for manual sequence number entry based on the corresponding checkbox
    def toggle_number_entry(self):
        if self.auto_numbering.get():
            for child in self.manual_number_frame.winfo_children():
                child.configure(state='disable')
        else:
            for child in self.manual_number_frame.winfo_children():
                child.configure(state='enable')

    # TODO: Chomping and leading 0's
    # TODO: Seperate parts into functions so a rename file function can use them later
    def update_filename_label(self):
        filename = ""

        if not self.auto_dating.get():
            if self.year.get().isnumeric(): # TODO do a better check than this so your aren't in the future
                filename += self.year.get().zfill(2)[-2:]
            else:
                filename += "??"
            
            if self.month.current() != -1:
                filename += str(self.month.current() + 1).zfill(2)
            else:
                filename += "??"
            
            if self.day.get().isnumeric(): # TODO do a better check than this so it matches the acutal month
                filename += self.day.get().zfill(2)
            else:
                filename += "??"
        else:
            filename += "YYMMDD" # TODO auto date from metadata

        filename += "_"

        if self.roll_film.get():
            # Add roll letter or error char
            if self.roll_letter.get().isalpha():
                filename += self.roll_letter.get().upper()
            else:
                filename += "?"

            # Two digit sequence number
            if not self.auto_numbering.get() and self.sequence_number.get().isnumeric():
                filename += self.sequence_number.get().zfill(2)
            else:
                filename += "##" if self.auto_numbering.get() else "??"
        else:
            # Three digit sequence number
            if not self.auto_numbering.get() and self.sequence_number.get().isnumeric():
                filename += self.sequence_number.get().zfill(3)
            else:
                filename += "###" if self.auto_numbering.get() else "???"
        
        self.current_filename_label.configure(text=filename)
        self.current_filename_label.after(5, self.update_filename_label)
    
    def rename_files(self):
        self.update_filename_label()
        print(self.current_filename_label.cget("text"))

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    application = PhotographRenamer()
    application.run()