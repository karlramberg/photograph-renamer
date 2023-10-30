# TODO:
#     Thumbnail generation needs polish 
#     Auto dating
#     Auto numbering
#     Replace cat with startup pick

import numpy as np 
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import rawpy
import math
from PIL import Image, ImageTk
from os import listdir, rename
from os.path import isfile, join, getmtime, splitext 
from datetime import datetime

FILENAME_VALID = "Select a file"
FILENAME_INVALID_YEAR = "Invalid year!"
FILENAME_NO_MONTH = "Select a month!"
FILENAME_INVALID_DAY = "Invalid day!"
FILENAME_INVALID_ROLL_LETTER = "Invalid roll letter!"
FILENAME_INVALID_NUMBER = "Invalid sequence number!"
FILENAME_INVALID_APPENDIX = "Invalid appendix!"
DIVIDER = "_"

IMAGE_EXTENSTIONS = (".JPG", ".JPEG", ".TIF", ".TIFF", ".DNG", ".RAF", ".NEF", ".PNG")
RAW_EXTENSIONS = (".RAF", ".NEF")
TRANSPARENT = (255, 255, 255, 0)

THUMBNAIL_SIZE = 400

class PhotographRenamer:
    # Set up the UI
    def __init__(self, master=None):
        # Create main window and frame
        window = tk.Tk()
        frame = ttk.Frame(window)

        # Choose folder -----------------------------------------------------------------------------------------------------------------------------
        chooseFolderFrame = ttk.LabelFrame(frame, text="Choose folder")
        self.folder = tk.StringVar()
        folderEntry = ttk.Entry(chooseFolderFrame, textvariable=self.folder)
        folderEntry.pack(expand=True, fill='x', side='left')
        chooseFolderButton = ttk.Button(chooseFolderFrame, text="Choose folder", command=self.chooseFolder)
        chooseFolderButton.pack(side='left')
        chooseFolderFrame.pack(fill='x', side='top')

        # Select files --------------------------------------------------------------------------------------------------------------------------
        selectFilesFrame = ttk.LabelFrame(frame, text="Select files")

        # Treeview and scrollbar
        fileListFrame = ttk.Frame(selectFilesFrame)

        self.fileList = ttk.Treeview(fileListFrame, columns=('filename', 'displayDate', 'formattedDate'))
        self.fileList['displaycolumns'] = ('filename', 'displayDate')
        self.fileList.config(selectmode='extended')
        self.fileList['show'] = 'headings'
        self.fileList.heading("filename", text="File name", anchor='w')
        self.fileList.heading("displayDate", text="Date created/modified", anchor='w')
        self.fileList.bind('<<TreeviewSelect>>', self.updateThumbnail)
        self.fileList.pack(expand=True, fill='x', side='left')

        fileListScrollbar = ttk.Scrollbar(fileListFrame, orient="vertical")
        fileListScrollbar.configure(command = self.fileList.yview)
        self.fileList.config(yscrollcommand=fileListScrollbar.set)
        fileListScrollbar.pack(side='left', fill='both')

        fileListFrame.pack(side='top', fill='x')

        # Select all and refresh controls
        fileListControlFrame = ttk.Frame(selectFilesFrame)
        selectAllButton = ttk.Button(fileListControlFrame, text="Select all", command=self.selectAllFiles)
        selectAllButton.pack(side='left')
        refreshFileListButton = ttk.Button(fileListControlFrame, text="Refresh folder", command=self.loadFolder)
        refreshFileListButton.pack(side='left')
        fileListControlFrame.pack(side='top', fill='x')

        selectFilesFrame.pack(fill='x', side='top')

        # Filename construction ---------------------------------------------------------------------------------------
        constructFilenameFrame = ttk.LabelFrame(frame, text="Construct filename")

        # Construction options
        filenameOptionsFrame = ttk.Frame(constructFilenameFrame)

        # Auto date option
        self.autoDating = tk.BooleanVar()
        self.autoDating.set(True)
        autoDatingCheckbox = ttk.Checkbutton(filenameOptionsFrame, text="Grab date from metadata", variable=self.autoDating, command=self.toggleAutoDate)
        autoDatingCheckbox.pack(side='left')

        # Roll letter option
        self.rollFilm = tk.BooleanVar()
        self.rollFilm.set(False)
        rollFilmCheckbox = ttk.Checkbutton(filenameOptionsFrame, text="Roll film", variable=self.rollFilm, command=self.toggleRollFilm)
        rollFilmCheckbox.pack(side='left')

        self.appendixing = tk.BooleanVar()
        self.appendixing.set(False)
        appendixingCheckbox = ttk.Checkbutton(filenameOptionsFrame, text="Add appendix", variable=self.appendixing, command=self.toggleAppendix)
        appendixingCheckbox.pack(side='left')

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
        monthEntryLabel = ttk.Label(self.dateEntryFrame, text="  Month: ")
        monthEntryLabel.pack(side='left')
        self.month = ttk.Combobox(self.dateEntryFrame, state='readonly', width=10,
            values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
        self.month.pack(side='left')

        # Day 
        self.day = tk.StringVar()
        dayEntryLabel = ttk.Label(self.dateEntryFrame, text="  Day: ")
        dayEntryLabel.pack(side='left')
        dayEntry = ttk.Entry(self.dateEntryFrame, textvariable=self.day, width=3)
        dayEntry.pack(side='left')

        self.dateEntryFrame.pack(fill='x', side='left')

        # Roll letter
        self.rollLetterEntryFrame = ttk.Frame(filenameEntriesFrame)

        self.rollLetter = tk.StringVar()
        rollLetterEntryLabel = ttk.Label(self.rollLetterEntryFrame, text="Roll letter: ")
        rollLetterEntryLabel.pack(side='left')
        rollLetterEntry = ttk.Entry(self.rollLetterEntryFrame, textvariable=self.rollLetter, width=3)
        rollLetterEntry.pack(side='left')
        self.rollLetterEmpty = ttk.Label(self.rollLetterEntryFrame, text="")

        self.rollLetterEntryFrame.pack(fill='x', side='left')

        # Start number 
        self.startNumberEntryFrame = ttk.Frame(filenameEntriesFrame)

        self.startNumber = tk.StringVar()
        self.startNumber.set("1")
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
        self.appendixEntry = ttk.Entry(self.appendixEntryFrame, textvariable=self.appendix , width=10)
        self.appendixEntry.pack(side='left')

        self.appendixEntryFrame.pack(fill='x', side='left')

        filenameEntriesFrame.pack(fill='x', side='top')
        constructFilenameFrame.pack(fill='x', side='top')

        # Image preview
        self.thumbnailFrame = ttk.LabelFrame(frame, width=410, height=425, text="Image preview")

        self.image = Image.open("cat.jpeg")
        self.thumbnailImage()
        self.image = ImageTk.PhotoImage(self.image)
        self.thumbnail = ttk.Label(self.thumbnailFrame, image=self.image)
        self.thumbnail.pack(fill="x", side='top', anchor='c')
        self.loadedThumbnailFile = ""

        self.thumbnailFrame.pack(fill='both', side='left')
        self.thumbnailFrame.pack_propagate(0)

        # Current filename and rename button
        self.previewFilename = tk.StringVar()
        self.previewFilenameLabel = ttk.Label(frame, textvariable=self.previewFilename)

        renameButton = ttk.Button(frame, text="Rename file(s)", command=self.renameFiles)
        renameButton.pack(side='bottom')
        self.previewFilenameLabel.pack(side='bottom')

        self.toggleAutoDate()
        self.toggleRollFilm()
        self.toggleAppendix()
        self.updatePreviewFilename()

        frame.pack(expand=True, fill='both', side='top')
        window.resizable(False, False)
        window.title("Photograph Renamer")
        self.window = window

    # Ask the user for a folder and load it
    def chooseFolder(self):
        self.folder.set(filedialog.askdirectory())
        self.loadFolder()

    # Load the folder currently in the entry box 
    def loadFolder(self):
        # Clear the old file list
        for file in self.fileList.get_children():
            self.fileList.delete(file)

        # Grab all the files from the folder
        files = [f for f in listdir(self.folder.get()) if isfile(join(self.folder.get(), f))]

        # Add all image files to the file list
        for file in files:
            fileExtension = splitext(file)[1].upper()
            if fileExtension in IMAGE_EXTENSTIONS:
                date = datetime.fromtimestamp(getmtime(self.folder.get() + "/" + file))
                formattedDate = date.strftime('%y%m%d')
                displayDate = date.strftime('%b %d, %Y')
                self.fileList.insert("", 'end', text=file, values=(file, displayDate, formattedDate))

    # Select every file in the file list
    def selectAllFiles(self):
        for file in self.fileList.get_children():
            self.fileList.selection_add(file)

    # Create a thumbnail of the first selected file if it's not alredy done
    # This function is called when ever the selection of the file list changes
    # TODO update this so it's cleaner with the new filename code
    def updateThumbnail(self, event):
        # Check that we didn't just de-select all files, then grab the path of the first selected
        selectedFiles = self.fileList.selection()
        if selectedFiles:
            file = self.fileList.item(selectedFiles[0])['values'][0]

            if file != self.loadedThumbnailFile:
                self.loadedThumbnailFile = file
                filePath = self.getFilePath(file)

                extension = splitext(file)[1]
                if extension in RAW_EXTENSIONS:
                    with rawpy.imread(filePath) as raw:
                        rgb = raw.postprocess(use_camera_wb=True, half_size=True)
                        self.image = Image.fromarray(rgb)
                else:
                    self.image = Image.open(filePath)

                    # If it's a 16-bit grayscale tiff convert it to 8-bit
                    if self.image.format == 'TIFF' and self.image.mode == 'I;16':
                        array = np.array(self.image)
                        self.image = Image.fromarray((array/256).astype(np.uint8))

                self.thumbnailImage() 
                self.image = ImageTk.PhotoImage(self.image)
                self.thumbnail.configure(image=self.image)
        else:
            pass
            # Load default image

    # Resize the image file and pad with transparency to fit nicely in a square space
    def thumbnailImage(self):
        self.image.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE), Image.LANCZOS)
        background = Image.new('RGBA', (THUMBNAIL_SIZE, THUMBNAIL_SIZE), TRANSPARENT)
        imagePosition = (int(math.ceil((THUMBNAIL_SIZE - self.image.size[0]) / 2)),
                         int(math.ceil((THUMBNAIL_SIZE - self.image.size[1]) / 2)))
        background.paste(self.image, imagePosition)
        background.format = self.image.format
        self.image = background.convert('RGBA')

    # Enable or disable the UI for manual date entry
    def toggleAutoDate(self):
        if self.autoDating.get():
            for child in self.dateEntryFrame.winfo_children():
                child.configure(state='disable')
        else:
            for child in self.dateEntryFrame.winfo_children():
                child.configure(state='enable')

    # Enable or disable the UI for film roll letters
    def toggleRollFilm(self):
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

    # Check the entered data for its validity, return error message if it's not
    def checkFilenameEntries(self):
        error = ""
        if not self.autoDating.get():
            year = self.getFileYear()
            if not(year.isnumeric() and int(year) > 0):
                error += FILENAME_INVALID_YEAR + "\n"
            
            if int(self.getFileMonth()) == 0:
                error += FILENAME_NO_MONTH + "\n"
            
            day = self.getFileDay() 
            if not(day.isnumeric() and int(day) > 0 and int(day) <= 31): # TODO do a better check so the day actually exists
                error += FILENAME_INVALID_DAY + "\n"
            
        if self.rollFilm.get() and not(self.getRollLetter().isalpha()):
            error += FILENAME_INVALID_ROLL_LETTER + "\n"

        if not(self.startNumber.get().isnumeric()):
            error += FILENAME_INVALID_NUMBER + "\n"

        appendix = self.getAppendix() 
        if self.appendixing.get() and not(appendix.isalpha() and not appendix == ""):
            error += FILENAME_INVALID_APPENDIX + "\n"

        if error != "":
            return error
        else: 
            return FILENAME_VALID

    # Return a formatted version of the year entry box
    def getFileYear(self):
        return self.year.get().zfill(2)[-2:]

    # Return a numerical version of the month dropdown
    def getFileMonth(self):
        return str(self.month.current() + 1).zfill(2)

    # Return a formatted version of the day entry box
    def getFileDay(self):
        return self.day.get().zfill(2)
    
    # Return a formatted version of the roll letter entry box
    def getRollLetter(self):
        return self.rollLetter.get().upper()

    # Return a formatted version of the appendix entry box 
    def getAppendix(self):
        return self.appendix.get().lower()
    
    def getFilePath(self, filename):
        return self.folder.get() + "/" + filename

    def updatePreviewFilename(self):
        filename = ""
        filenameState = self.checkFilenameEntries()
        if filenameState == FILENAME_VALID and self.fileList.selection():
            firstFile = self.fileList.item(self.fileList.selection()[0])
            # Add date
            if not self.autoDating.get():
                filename += self.getFileYear() + self.getFileMonth() + self.getFileDay()
            else:
                filename += str(firstFile['values'][2])

            # Add dividier
            filename += DIVIDER

            # Add roll letter and two digit number if roll film
            numberPadding = 3
            if self.rollFilm.get():
                filename += self.getRollLetter()
                numberPadding = 2

            # Add sequence number
            filename += str(int(self.startNumber.get())).zfill(numberPadding)

            # Add appendix if its enabled
            if self.appendixing.get():
                filename += DIVIDER + self.getAppendix()

            # Add file extension
            filename += splitext(firstFile['values'][0])[1]

            self.previewFilename.set(filename)
        else: 
            self.previewFilename.set(filenameState) 

        self.previewFilenameLabel.after(20, self.updatePreviewFilename)

    def renameFiles(self):
        # Exit if we don't have the right data for proper file names
        if self.checkFilenameEntries() != FILENAME_VALID:
            return

        selectedFiles = self.fileList.selection()
        dateCounters = {}

        for file in selectedFiles:
            file = self.fileList.item(file)

            filename = ""

            # Date
            date = ""
            if not self.autoDating.get():
                date += self.getFileYear() + self.getFileMonth() + self.getFileDay()
            else:
                date += str(file['values'][2])

            if date not in dateCounters:
                dateCounters[date] = 0

            filename += date

            # Divider
            filename += DIVIDER

            # Roll letter
            numberPadding = 3
            if self.rollFilm.get():
                filename += self.getRollLetter()
                numberPadding = 2

            # Sequence number
            filename += str(int(self.startNumber.get()) + dateCounters[date]).zfill(numberPadding)

            # Appendix
            if self.appendixing.get():
                filename += DIVIDER + self.appendix.get()

            # File extension 
            filename += splitext(file['values'][0])[1]

            # Increment the date sequence
            dateCounters[date] += 1

            # Rename the file
            rename(self.getFilePath(file['values'][0]), self.getFilePath(filename))

        self.loadFolder()

if __name__ == "__main__":
    application = PhotographRenamer()
    application.window.mainloop()