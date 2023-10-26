# TODO:
#     Image previews
#     File renaming from treeview selection
#     Polish UI
#     Auto dating from metadata
#     Auto numbering from selection
#     Refresh treeview button
  
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
from PIL import Image, ImageTk
from os import listdir
from os.path import isfile, join, getmtime 
from datetime import datetime

FILENAME_VALID = "Valid"
FILENAME_INVALID_YEAR = "Invalid year!"
FILENAME_NO_MONTH = "Select a month!"
FILENAME_INVALID_DAY = "Invalid day!"
FILENAME_INVALID_ROLL_LETTER = "Invalid roll letter!"
FILENAME_INVALID_NUMBER = "Invalid sequence number!"
FILENAME_INVALID_APPENDIX = "Invalid appendix!"
DIVIDER = "_"

class PhotographRenamer:
    def __init__(self, master=None):
        # Create main window and frame
        window = tk.Tk()
        frame = ttk.Frame(window)

        # Choose folder -----------------------------------------------------------------------------------------------------------------------------
        chooseFolderFrame = ttk.LabelFrame(frame, text="Choose folder")

        self.folder = tk.StringVar()
        folderEntry = ttk.Entry(chooseFolderFrame, textvariable=self.folder)
        folderEntry.pack(expand=True, fill='x', side='left')
        chooseFolderButton = ttk.Button(chooseFolderFrame, text="Choose folder", command=self.load_folder) # TODO add functionality
        chooseFolderButton.pack(side='left')
        
        chooseFolderFrame.pack(fill='x', side='top')

        # Select files --------------------------------------------------------------------------------------------------------------------------
        selectFilesFrame = ttk.LabelFrame(frame, text="Select files")

        fileListFrame = ttk.Frame(selectFilesFrame)

        self.fileList = ttk.Treeview(fileListFrame, columns=('filename', 'date_created'))
        self.fileList.config(selectmode='extended')
        self.fileList['show'] = 'headings'
        self.fileList.heading("filename", text="File name", anchor='w')
        self.fileList.heading("date_created", text="Date created", anchor='w')
        self.fileList.bind('<<TreeviewSelect>>', self.updateThumbnail)
        self.fileList.pack(expand=True, fill='x', side='left')

        fileListScrollbar = ttk.Scrollbar(fileListFrame, orient="vertical")
        fileListScrollbar.configure(command = self.fileList.yview)
        self.fileList.config(yscrollcommand=fileListScrollbar.set)
        fileListScrollbar.pack(side='left', fill='both')

        fileListFrame.pack(side='top', fill='x')

        fileListControlFrame = ttk.Frame(selectFilesFrame)

        selectAllButton = ttk.Button(fileListControlFrame, text="Select all") # TODO add functionality
        selectAllButton.pack(side='left')
        refreshFileListButton = ttk.Button(fileListControlFrame, text="Refresh folder") # TODO add functionality
        refreshFileListButton.pack(side='left')

        fileListControlFrame.pack(side='top', fill='x')

        selectFilesFrame.pack(fill='x', side='top')

        # Filename construction ---------------------------------------------------------------------------------------
        constructFilenameFrame = ttk.LabelFrame(frame, text="Construct filename")

        # Construction options
        filenameOptionsFrame = ttk.Frame(constructFilenameFrame)

        # Auto date option
        self.autoDating = tk.BooleanVar()
        self.autoDating.set(False)
        autoDatingCheckbox = ttk.Checkbutton(filenameOptionsFrame)
        autoDatingCheckbox.configure(text="Grab date from metadata", variable=self.autoDating, command=self.toggleAutoDate)
        autoDatingCheckbox.pack(side='left', padx=5)

        # Roll letter option
        self.rollFilm= tk.BooleanVar()
        self.rollFilm.set(False)
        rollFilmCheckbox = ttk.Checkbutton(filenameOptionsFrame)
        rollFilmCheckbox.configure(text="Roll film", variable=self.rollFilm, command=self.togglRollFilm)
        rollFilmCheckbox.pack(side='left', padx=5)

        self.appendixing = tk.BooleanVar()
        self.appendixing.set(False)
        appendixingCheckbox = ttk.Checkbutton(filenameOptionsFrame)
        appendixingCheckbox.configure(text="Add appendix", variable=self.appendixing, command=self.toggleAppendix)
        appendixingCheckbox.pack(side='left', padx=5)

        filenameOptionsFrame.pack(fill='x', side='top')

        # Data entry --------------------------------------------------------------------------------------------------------------------------------
        filenameEntriesFrame = ttk.Frame(constructFilenameFrame)

        self.dateEntryFrame = ttk.Frame(filenameEntriesFrame)

        # Year
        self.year = tk.StringVar()
        yearEntryLabel = ttk.Label(self.dateEntryFrame, text="  Year: ")
        yearEntryLabel.pack(side='left')
        yearEntry = ttk.Entry(self.dateEntryFrame, textvariable=self.year, width=5)
        yearEntry.pack(side='left')

        # Month
        month_label = ttk.Label(self.dateEntryFrame, text="  Month: ")
        month_label.pack(side='left')
        self.month = ttk.Combobox(self.dateEntryFrame, state='readonly', width=10,
            values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        self.month.pack(side='left')

        # Day 
        self.day = tk.StringVar()
        dayEntryLabel = ttk.Label(self.dateEntryFrame, text="  Day: ")
        dayEntryLabel.pack(side='left')
        self.dayEntry = ttk.Entry(self.dateEntryFrame, textvariable="", width=3)
        self.dayEntry.pack(side='left')

        self.dateEntryFrame.pack(fill='x', side='left')

        # Roll letter
        self.rollLetterEntryFrame = ttk.Frame(filenameEntriesFrame)

        self.rollLetter = tk.StringVar()
        rollLetterEntryLabel = ttk.Label(self.rollLetterEntryFrame, text="Roll letter: ")
        rollLetterEntryLabel.pack(side='left')
        self.rollLetterEntry = ttk.Entry(self.rollLetterEntryFrame, textvariable="", width=3)
        self.rollLetterEntry.pack(side='left')
        self.rollLetterEmpty = ttk.Label(self.rollLetterEntryFrame, text="")

        self.rollLetterEntryFrame.pack(fill='x', side='left')

        # Start number 
        self.startNumberEntryFrame = ttk.Frame(filenameEntriesFrame)

        self.startNumber = tk.StringVar()
        self.startNumberEntryLabel = ttk.Label(self.startNumberEntryFrame, text="Start number: ")
        self.startNumberEntryLabel.pack(side='left')
        startNumberEntry = ttk.Entry(self.startNumberEntryFrame, textvariable=self.startNumber, width=4)
        startNumberEntry.pack(side='left')

        self.startNumberEntryFrame.pack(fill='x', side='left')

        # Appendix entry
        self.appendixEntryFrame = ttk.Frame(filenameEntriesFrame)

        self.appendix = tk.StringVar()
        appendixEntryLabel = ttk.Label(self.appendixEntryFrame, text="Appendix:")
        appendixEntryLabel.pack(side='left')
        self.appendixEntry = ttk.Entry(self.appendixEntryFrame, textvariable="" , width=10)
        self.appendixEntry.pack(side='left')

        self.appendixEntryFrame.pack(fill='x', side='left')

        filenameEntriesFrame.pack(fill='x', side='top')
        constructFilenameFrame.pack(fill='x', side='top')

        # Image preview
        thumbnailFrame = ttk.LabelFrame(frame, text="Image preview")

        # TODO temporary cat pic, replace with a startup image
        self.thumbnailImage = Image.open("test_images/cat.jpeg")
        self.thumbnailImage.thumbnail((400,400), Image.Resampling.LANCZOS)
        self.thumbnailImage = ImageTk.PhotoImage(self.thumbnailImage)
        self.thumbnail = ttk.Label(thumbnailFrame, image=self.thumbnailImage)
        self.thumbnail.pack(fill="both", side='top')

        thumbnailFrame.pack(fill='both', side='left')

        # Current filename and rename button
        self.currentFilename = tk.StringVar()
        self.currentFilenameLabel = ttk.Label(frame, textvariable="")
        self.updateCurrentFilename()

        rename_button = ttk.Button(frame, text="Rename file(s)", command=self.rename_files)
        rename_button.pack(side='bottom')
        self.currentFilenameLabel.pack(side='bottom', pady=5)

        self.toggleAutoDate()
        self.togglRollFilm()
        self.toggleAppendix()

        frame.config(width="500")
        frame.pack(expand=True, fill='both', side='top', padx=5, pady=5)
        window.resizable(False, False)
        window.title("Photograph Renamer")
        self.window = window

    # TODO filter out non-image files
    def load_folder(self):
        for file in self.fileList.get_children():
            self.fileList.delete(file)

        self.folder.set(filedialog.askdirectory())

        onlyfiles = [f for f in listdir(self.folder.get()) if isfile(join(self.folder.get(), f))]
        for file in onlyfiles:
            creation_date = datetime.fromtimestamp(getmtime(self.folder.get() + "/" + file))
            self.fileList.insert("", 'end', text=file, values=(file, creation_date))

    # TODO rework for funky TIFFs and raws
    def updateThumbnail(self, event):
        selected_files = self.fileList.selection()
        if selected_files:
            image_path = self.fileList.item(selected_files[0])['values'][0]
            self.thumbnailImage = Image.open(self.folder.get() + "/" + image_path)
            self.thumbnailImage.thumbnail((400,400), Image.LANCZOS)
            self.thumbnailImage = ImageTk.PhotoImage(self.thumbnailImage)
            self.thumbnail.configure(image=self.thumbnailImage)

    # Enable of disable the UI for manual date entry based on the corresponding checkbox
    def toggleAutoDate(self):
        if self.autoDating.get():
            for child in self.dateEntryFrame.winfo_children():
                child.configure(state='disable')
        else:
            for child in self.dateEntryFrame.winfo_children():
                child.configure(state='enable')

    # Enable or disable the UI for film roll letters
    def togglRollFilm(self):
        if self.rollFilm.get():
            for child in self.rollLetterEntryFrame.winfo_children():
                child.pack(side='left')
            self.rollLetterEmpty.pack_forget()
        else:
            for child in self.rollLetterEntryFrame.winfo_children():
                child.pack_forget()
            self.rollLetterEmpty.pack(side='left')

    # Enable or disable the UI for appendices
    def toggleAppendix(self):
        if self.appendixing.get():
            for child in self.appendixEntryFrame.winfo_children():
                child.pack(side='left')
        else:
            for child in self.appendixEntryFrame.winfo_children():
                child.pack_forget()

    def get_filename(self, sequence_counter):
        filename = ""
        filenameState = self.checkFilenameEntries()
        if filenameState == FILENAME_VALID:
            # Add date
            if not self.autoDating.get():
                filename += self.getFileYear() + self.getFileMonth() + self.getFileDay()
            else:
                filename += "YYMMDD" # TODO auto dating

            # Add dividier
            filename += DIVIDER

            # Add roll letter and two digit number if roll film
            numberPadding = 3
            if self.rollFilm.get():
                filename += self.getRollLetter()
                numberPadding = 2

            # Add sequence number
            filename += str(int(self.startNumber.get()) + sequence_counter).zfill(numberPadding)

            # Add appendix if its enabled
            if self.appendixing.get():
                filename += "_" + self.appendix.get()

            # TODO Add file extension

        else: 
            filename += filenameState
        
        return filename

    # TODO: Chomping and leading 0's
    def updateCurrentFilename(self):
        filename = self.get_filename(0)
        self.currentFilenameLabel.configure(text=filename)
        self.currentFilenameLabel.after(5, self.updateCurrentFilename)

    def rename_files(self):
        self.updateCurrentFilename()
        print(self.currentFilenameLabel.cget("text"))

    # Check the entered data for its validity, return error message if it's not
    def checkFilenameEntries(self):
        error = ""
        if not self.autoDating.get():
            if not(self.year.get().isnumeric()): # TODO do a better check than this so your aren't in the future
                error += FILENAME_INVALID_YEAR + "\n"
            
            if self.month.current() == -1:
                error += FILENAME_NO_MONTH + "\n"
            
            if not(self.day.get().isnumeric()): # TODO do a better check so the day actually exists
                error += FILENAME_INVALID_DAY + "\n"
            
        if self.rollFilm.get() and not(self.rollLetter.get().isalpha()):
            error += FILENAME_INVALID_ROLL_LETTER + "\n"
        
        if not(self.startNumber.get().isnumeric()):
            error += FILENAME_INVALID_NUMBER + "\n"
        
        if self.appendixing.get() and not(self.appendix.get().isalpha()):
            error += FILENAME_INVALID_APPENDIX + "\n"

        if error != "":
            return error
        else: 
            return FILENAME_VALID

    def getFileYear(self):
        return self.year.get().zfill(2)[-2:]

    def getFileMonth(self):
        return str(self.month.current() + 1).zfill(2)

    def getFileDay(self):
        return self.day.get().zfill(2)
    
    def getRollLetter(self):
        return self.rollLetter.get().upper()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    application = PhotographRenamer()
    application.run()