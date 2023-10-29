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
from os import listdir
from os.path import isfile, join, getmtime, splitext 
from datetime import datetime

FILENAME_VALID = "Valid"
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

        self.fileList = ttk.Treeview(fileListFrame, columns=('filename', 'dateCreated'))
        self.fileList.config(selectmode='extended')
        self.fileList['show'] = 'headings'
        self.fileList.heading("filename", text="File name", anchor='w')
        self.fileList.heading("dateCreated", text="Date created", anchor='w')
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
        autoDatingCheckbox = ttk.Checkbutton(filenameOptionsFrame)
        autoDatingCheckbox.configure(text="Grab date from metadata", variable=self.autoDating, command=self.toggleAutoDate)
        autoDatingCheckbox.pack(side='left')

        # Roll letter option
        self.rollFilm = tk.BooleanVar()
        self.rollFilm.set(False)
        rollFilmCheckbox = ttk.Checkbutton(filenameOptionsFrame)
        rollFilmCheckbox.configure(text="Roll film", variable=self.rollFilm, command=self.togglRollFilm)
        rollFilmCheckbox.pack(side='left')

        self.appendixing = tk.BooleanVar()
        self.appendixing.set(False)
        appendixingCheckbox = ttk.Checkbutton(filenameOptionsFrame)
        appendixingCheckbox.configure(text="Add appendix", variable=self.appendixing, command=self.toggleAppendix)
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
        dayEntry = ttk.Entry(self.dateEntryFrame, textvariable="", width=3)
        dayEntry.pack(side='left')

        self.dateEntryFrame.pack(fill='x', side='left')

        # Roll letter
        self.rollLetterEntryFrame = ttk.Frame(filenameEntriesFrame)

        self.rollLetter = tk.StringVar()
        rollLetterEntryLabel = ttk.Label(self.rollLetterEntryFrame, text="Roll letter: ")
        rollLetterEntryLabel.pack(side='left')
        rollLetterEntry = ttk.Entry(self.rollLetterEntryFrame, textvariable="", width=3)
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
        self.appendixEntry = ttk.Entry(self.appendixEntryFrame, textvariable="" , width=10)
        self.appendixEntry.pack(side='left')

        self.appendixEntryFrame.pack(fill='x', side='left')

        filenameEntriesFrame.pack(fill='x', side='top')
        constructFilenameFrame.pack(fill='x', side='top')

        # Image preview
        self.thumbnailFrame = ttk.LabelFrame(frame, width=410, height=425, text="Image preview")

        self.image = Image.open("../test_images/cat.jpeg")
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
        self.updatePreviewFilename()

        renameButton = ttk.Button(frame, text="Rename file(s)", command=self.renameFiles)
        renameButton.pack(side='bottom')
        self.previewFilenameLabel.pack(side='bottom')

        self.toggleAutoDate()
        self.togglRollFilm()
        self.toggleAppendix()

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
                creationDate = datetime.fromtimestamp(getmtime(self.folder.get() + "/" + file))
                self.fileList.insert("", 'end', text=file, values=(file, creationDate))

    # Select every file in the file list
    def selectAllFiles(self):
        for file in self.fileList.get_children():
            self.fileList.selection_add(file)

    # Create a thumbnail of the first selected file if it's not alredy done
    # This function is called when ever the selection of the file list changes
    def updateThumbnail(self, event):
        # Check that we didn't just de-select all files, then grab the path of the first selected
        selectedFiles = self.fileList.selection()
        if selectedFiles:
            file = self.fileList.item(selectedFiles[0])['values'][0]

            if file != self.loadedThumbnailFile:
                self.loadedThumbnailFile = file
                filePath = self.folder.get() + "/" + file

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

    def getFilename(self, sequenceCounter):
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
            filename += str(int(self.startNumber.get()) + sequenceCounter).zfill(numberPadding)

            # Add appendix if its enabled
            if self.appendixing.get():
                filename += "_" + self.appendix.get()

            # TODO Add file extension

        else: 
            filename += filenameState
        
        return filename
    
    # Update the preview filename with the first item selected in the list
    def updatePreviewFilename(self):
        self.previewFilename.set(self.getFilename(0))
        self.previewFilenameLabel.after(5, self.updatePreviewFilename)

    def renameFiles(self):
        self.updatePreviewFilename()

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

    def getFileYear(self, selectionIndex):
        if self.autoDating.get(): 
            pass
        else:
            return self.year.get().zfill(2)[-2:]

    def getFileMonth(self):
        return str(self.month.current() + 1).zfill(2)

    def getFileDay(self):
        return self.day.get().zfill(2)
    
    def getRollLetter(self):
        return self.rollLetter.get().upper()

if __name__ == "__main__":
    application = PhotographRenamer()
    application.window.mainloop()