# TODO:
# Thumbnail generation needs polish
# Proper startup image
# Do a proper check for a day existing in the month
# Favicon
# Build system

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as filedialog
import numpy, rawpy, math, base64
from PIL import Image, ImageTk
import os
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

FAVICON_BASE64="iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANiSURBVDhPVVNLbFtFFD0z75uXOnbAcZImdRIngQZXETSUtkKVsiASIgsoqwpVFYJNd0gsWSB2sEJs2LBBtEhIbGkR4VOlUn4LQHyc0ripm9hJnts4iT/v+fl9ZoZ5gBBc6Y40unPOzJl7LsF/QgiQ/ZXp+USvf5lo0XlK+DBlRPBIVEJHWXNr9FpmvvhNfPRvBPAvQfHrieHj/fr1tdut2aYT4PFcFy7MyTKnWF4IsV/yYWkKnjuT+v7+lnPlzNWyHeNovNz7YvxENs2WjWPR7K9FD6JLRT5vgoSyGHFMPmXCowJLhTYM03shO0iXbn+YHYyxRL6FNH6YvJXMBLNCagiEgTvVBCzdwfiQD2ISbJYMeE0LY2YDqsoguEB5RyzkX6+8qLzy6eT88FD0jhAc9ZqKR/RNvPdRDZ9ct/HShTwcdwCvXt3DPTuHqafn4Ng/o6ubgKqYmJtKLylvXep5N5Hk074vsLpxCjQ9j+zICE7PzIDpE3B5Hk+cPI2ZZ58B1wZQKJSQzdRBKcdBnYU0jMJzQSClMqDm+Pj9tw2Evg/D0LC38wiVbRvHLBOddhvr6/fR4ZHsFkEUAUzws2Tt4353NKdaiR4VD2wFny9m0QzSSHZzvPz8DphPcfPHYRw1BUy6h0vndzEyyFA/4LhTDA/Jd+9nmmNZmkhnVECjKFcjEMPEUFZBd08EFjK09jWUyxxBx8NIvwIu5T60Gf4ohUe03sB2oyoZywzEBUYzGrLpCKk+Bi2twkzpsAy5tzo40Se77gkcVBiaDzlabbKtVutitccQpyKfoe1wmL0Uux5DcJfIG5jUyjH4mAqNc+R6NQR1hkaL49CLEGOVfK77UNP5G8QQaEtXeIzA9RTpVRM7NpU919HXo8F3GXjc6g5kcuzUOTYq7G1lZb1dGT+unVU0TLqRkKwMhZKHxZ+amBpToKk+vlo8hBtyyP+HEzDsO8DdMrv52S3nAyW2Y8rQvm122Lyu0z5dVxDnYYthYdnFL8UQlkVwcrQLVI5G7UhK2/ILR0fJi0Xbaf9FsFkN2smU8WV1n0233GgiiggSloYuncBQCYYGDOnICNu7DJuV6EagpC7eWLVrMfZ/4xzHzJPds6YavmYZ6jlB2BiR88FBt3yfLTOY11bXWyv/HJUB/AkmcKji8cPSlQAAAABJRU5ErkJggg=="
THUMBNAIL_SIZE = 400
TRANSPARENT = (0, 0, 0, 0)
PADX = 5
PADY = 5

class photograph_renamer:
	# Set up the UI
	def __init__(self, master=None):
		# Create main window and frame
		window = tk.Tk()
		frame = ttk.Frame(window)

		# Favicon
		window.iconphoto(True, tk.PhotoImage(data=FAVICON_BASE64))
		# temporary_file = "favicon.ico"
		# favicon_file = open(temporary_file, 'wb')
		# favicon_file.write(base64.b64decode(FAVICON_BASE64))
		# favicon_file.close()
		# window.wm_iconbitmap(temporary_file)
		# os.remove(temporary_file)
		

		# Choose folder -----------------------------------------------------------------------------------------------------------------------------
		choose_folder_frame = ttk.LabelFrame(frame, text="Choose folder")
		self.folder = tk.StringVar()
		folder_entry = ttk.Entry(choose_folder_frame, textvariable=self.folder)
		folder_entry.pack(expand=True, fill='x', side='left', padx=PADX, pady=PADY)
		choose_folder_button = ttk.Button(choose_folder_frame, text=" Choose folder ", command=self.choose_folder)
		choose_folder_button.pack(side='left', padx=(0, PADX), pady=PADY)
		choose_folder_frame.pack(fill='x', side='top')

		# Select files --------------------------------------------------------------------------------------------------------------------------
		select_files_frame = ttk.LabelFrame(frame, text="Select files")

		# Treeview and scrollbar
		file_list_frame = ttk.Frame(select_files_frame)

		self.file_list = ttk.Treeview(file_list_frame, columns=('filename', 'display_date', 'formatted_date'))
		self.file_list['displaycolumns'] = ('filename', 'display_date')
		self.file_list.config(selectmode='extended')
		self.file_list['show'] = 'headings'
		self.file_list.heading("filename", text="File name", anchor='w')
		self.file_list.heading("display_date", text="Date created/modified", anchor='w')
		self.file_list.bind('<<TreeviewSelect>>', self.update_thumbnail)
		self.file_list.pack(expand=True, fill='x', side='left', padx=PADX, pady=PADY)

		file_list_scrollbar = ttk.Scrollbar(file_list_frame, orient="vertical")
		file_list_scrollbar.configure(command = self.file_list.yview)
		self.file_list.config(yscrollcommand=file_list_scrollbar.set)
		file_list_scrollbar.pack(side='left', fill='both')

		file_list_frame.pack(side='top', fill='x')

		# Select all and refresh controls
		file_list_controls_frame = ttk.Frame(select_files_frame)
		select_all_files_button = ttk.Button(file_list_controls_frame, text=" Select all ", command=self.select_all_files)
		select_all_files_button.pack(side='left', padx=(0, PADX))
		refresh_folder_button = ttk.Button(file_list_controls_frame, text=" Refresh folder ", command=self.load_folder)
		refresh_folder_button.pack(side='left')
		file_list_controls_frame.pack(side='top', fill='x', padx=PADX, pady=(0, PADY))

		select_files_frame.pack(fill='x', side='top')

		# Filename construction ---------------------------------------------------------------------------------------
		construct_filename_frame = ttk.LabelFrame(frame, text="Construct filename")

		# Construction options
		filename_options_frame = ttk.Frame(construct_filename_frame)

		# Auto date option
		self.auto_dating = tk.BooleanVar()
		self.auto_dating.set(True)
		auto_dating_checkbox = ttk.Checkbutton(filename_options_frame, text="Grab date from metadata", variable=self.auto_dating, command=self.toggle_auto_date)
		auto_dating_checkbox.pack(side='left')

		# Roll letter option
		self.roll_film = tk.BooleanVar()
		self.roll_film.set(False)
		roll_film_checkbox = ttk.Checkbutton(filename_options_frame, text="Roll film", variable=self.roll_film, command=self.toggle_roll_film)
		roll_film_checkbox.pack(side='left', padx=(PADX, 0))

		self.appendixing = tk.BooleanVar()
		self.appendixing.set(False)
		appendixing_checkbox = ttk.Checkbutton(filename_options_frame, text="Add appendix", variable=self.appendixing, command=self.toggle_appendix)
		appendixing_checkbox.pack(side='left', padx=(PADX, 0))

		filename_options_frame.pack(fill='x', side='top', padx=PADX, pady=(PADY, 0))

		# Data entry --------------------------------------------------------------------------------------------------------------------------------
		filename_entries_frame = ttk.Frame(construct_filename_frame)

		self.date_entry_frame = ttk.Frame(filename_entries_frame)

		# Year
		self.year = tk.StringVar()
		year_entry_label = ttk.Label(self.date_entry_frame, text="Year:")
		year_entry_label.pack(side='left')
		year_entry = ttk.Entry(self.date_entry_frame, textvariable=self.year, width=5)
		year_entry.pack(side='left')

		# Month
		month_entry_label = ttk.Label(self.date_entry_frame, text="Month:")
		month_entry_label.pack(side='left', padx=(PADX, 0))
		self.month = ttk.Combobox(self.date_entry_frame, state='readonly', width=10,
			values=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
		self.month.pack(side='left')

		# Day 
		self.day = tk.StringVar()
		day_entry_label = ttk.Label(self.date_entry_frame, text="Day:")
		day_entry_label.pack(side='left', padx=(PADX, 0))
		day_entry = ttk.Entry(self.date_entry_frame, textvariable=self.day, width=3)
		day_entry.pack(side='left')

		self.date_entry_frame.pack(fill='x', side='left')

		# Roll letter
		self.roll_letter_entry_frame = ttk.Frame(filename_entries_frame)

		self.roll_letter = tk.StringVar()
		roll_letter_entry_label = ttk.Label(self.roll_letter_entry_frame, text="Roll letter:")
		roll_letter_entry_label.pack(side='left')
		roll_letter_entry = ttk.Entry(self.roll_letter_entry_frame, textvariable=self.roll_letter, width=3)
		roll_letter_entry.pack(side='left')
		self.roll_letter_empty = ttk.Label(self.roll_letter_entry_frame, text="")

		self.roll_letter_entry_frame.pack(fill='x', side='left', padx=(PADX, 0))

		# Start number 
		self.start_number_entry_frame = ttk.Frame(filename_entries_frame)

		self.start_number = tk.StringVar()
		self.start_number.set("1")
		start_number_entry_label = ttk.Label(self.start_number_entry_frame, text="Start number:")
		start_number_entry_label.pack(side='left')
		start_number_entry = ttk.Entry(self.start_number_entry_frame, textvariable=self.start_number, width=4)
		start_number_entry.pack(side='left')

		self.start_number_entry_frame.pack(fill='x', side='left', padx=(PADX, 0))

		# Appendix entry
		self.appendix_entry_frame = ttk.Frame(filename_entries_frame)

		self.appendix = tk.StringVar()
		appendix_entry_label = ttk.Label(self.appendix_entry_frame, text="Appendix:")
		appendix_entry_label.pack(side='left', padx=3)
		appendix_entry = ttk.Entry(self.appendix_entry_frame, textvariable=self.appendix , width=10)
		appendix_entry.pack(side='left')

		self.appendix_entry_frame.pack(fill='x', side='left', padx=(PADX, 0))

		filename_entries_frame.pack(fill='x', side='top', padx=PADX, pady=PADY)
		construct_filename_frame.pack(fill='x', side='top')

		# Image preview -----------------------------------------------------------------------------------------------------------------------------
		thumbnail_frame = ttk.LabelFrame(frame, width=410, height=425, text="Image preview")

		self.image = None
		self.loaded_thumbnail_file = None
		self.thumbnail = ttk.Label(thumbnail_frame, image=self.image)
		self.load_blank_thumbnail()
		self.thumbnail.pack(fill="both", anchor='center')

		thumbnail_frame.pack(fill='both', side='left')
		thumbnail_frame.pack_propagate(False)

		# Current filename and rename button
		rename_files_button = ttk.Button(frame, text=" Rename file(s) ", command=self.rename_files)
		rename_files_button.pack(side='bottom', padx=PADX, pady=PADY)
		self.preview_filename_label = ttk.Label(frame, text="")
		self.preview_filename_label.pack(side='bottom')

		self.toggle_auto_date()
		self.toggle_roll_film()
		self.toggle_appendix()
		self.update_preview_filename()

		frame.pack(expand=True, fill='both', side='top', padx=5, pady=5)
		window.geometry("600x855")
		window.resizable(False, False)
		window.title("Photograph Renamer")
		self.window = window

	# Ask the user for a folder and load it
	def choose_folder(self):
		self.folder.set(filedialog.askdirectory())
		self.load_folder()

	# Load the folder currently in the entry box 
	def load_folder(self):
		# Clear the old file list
		for file in self.file_list.get_children():
			self.file_list.delete(file)

		# Grab all the files from the folder
		files = [f for f in os.listdir(self.folder.get()) if isfile(join(self.folder.get(), f))]

		# Add all image files to the file list
		for file in files:
			file_extension = splitext(file)[1].upper()
			if file_extension in IMAGE_EXTENSTIONS:
				date = datetime.fromtimestamp(getmtime(self.folder.get() + "/" + file))
				formatted_date = date.strftime('%y%m%d')
				display_date = date.strftime('%b %d, %Y')
				self.file_list.insert("", 'end', text=file, values=(file, display_date, formatted_date))

	# Select every file in the file list
	def select_all_files(self):
		for file in self.file_list.get_children():
			self.file_list.selection_add(file)

	# Enable or disable the UI for manual date entry
	def toggle_auto_date(self):
		if self.auto_dating.get():
			for child in self.date_entry_frame.winfo_children():
				child.configure(state='disable')
		else:
			for child in self.date_entry_frame.winfo_children():
				child.configure(state='enable')

	# Enable or disable the UI for film roll letters
	def toggle_roll_film(self):
		if self.roll_film.get():
			for child in self.roll_letter_entry_frame.winfo_children():
				child.pack(side='left')
			self.roll_letter_empty.pack_forget()
		else:
			for child in self.roll_letter_entry_frame.winfo_children():
				child.pack_forget()
			self.roll_letter_empty.pack(side='left')

	# Enable or disable the UI for appendices
	def toggle_appendix(self):
		if self.appendixing.get():
			for child in self.appendix_entry_frame.winfo_children():
				child.pack(side='left')
		else:
			for child in self.appendix_entry_frame.winfo_children():
				child.pack_forget()

	# Create a thumbnail of the first selected file if it's not alredy done
	# This function is called when ever the selection of the file list changes
	def update_thumbnail(self, event):
		# Check that at least one file is selected
		selected_files = self.file_list.selection()
		if selected_files:

			# Get the filename and file path of the first selected file
			first_selected_filename = self.file_list.item(selected_files[0])['values'][0]
			file_path = self.get_file_path(first_selected_filename)

			# Check the thumbnail for this file is not already loaded 
			if file_path != self.loaded_thumbnail_file:
				self.loaded_thumbnail_file = file_path

				# Get the file type
				file_extension = splitext(first_selected_filename)[1]

				# Use rawlib to process and any raw files
				if file_extension in RAW_EXTENSIONS:
					with rawpy.imread(file_path) as raw:
						# Generate an image scaled down using the camera's white balance setting, everything else auto
						rgb = raw.postprocess(use_camera_wb=True, half_size=True)
						self.image = Image.fromarray(rgb)
				# Use PIL to process any standard image (JPG, PNG, TIFF)
				else:
					self.image = Image.open(file_path)

					# If it's a 16-bit grayscale tiff convert it to 8-bit
					if self.image.format == 'TIFF' and self.image.mode == 'I;16':
						array = numpy.array(self.image)
						self.image = Image.fromarray((array/256).astype(numpy.uint8))

				# Process the image data into a thumbnail and plug it into the UI	
				self.thumbnail_image() 
				self.image = ImageTk.PhotoImage(self.image)
				self.thumbnail.configure(image=self.image)

		else: # if no files are selected load a blank thumbnail
			self.load_blank_thumbnail()

	def load_blank_thumbnail(self):
		self.image = Image.new('RGBA', (THUMBNAIL_SIZE, THUMBNAIL_SIZE), TRANSPARENT)
		self.image = ImageTk.PhotoImage(self.image)
		self.thumbnail.configure(image=self.image)
		self.loaded_thumbnail_file = ""

	# Resize the image file and pad with transparency to fit nicely in a square space
	def thumbnail_image(self):
		# Resize the image, keeping aspect ratio
		self.image.thumbnail((THUMBNAIL_SIZE, THUMBNAIL_SIZE), Image.LANCZOS)

		# Generate a transparent background
		background = Image.new('RGBA', (THUMBNAIL_SIZE, THUMBNAIL_SIZE), TRANSPARENT)

		# Put the image in the center of the background
		image_position = (int(math.ceil((THUMBNAIL_SIZE - self.image.size[0]) / 2)),
						 int(math.ceil((THUMBNAIL_SIZE - self.image.size[1]) / 2)))
		background.paste(self.image, image_position)
		background.format = self.image.format

		self.image = background.convert('RGBA')

	# Create a filename for the first file selected or an error message if data needs fixing
	def update_preview_filename(self):
		filename = ""

		# If at least one file is selected and the data to make a filename is correct
		selected_files = self.file_list.selection()
		filename_state = self.check_filename_entries()
		if selected_files and filename_state == FILENAME_VALID:
			first_selected_file = self.file_list.item(selected_files[0])

			# Add date
			if not self.auto_dating.get():
				filename += self.get_year() + self.get_month() + self.get_day()
			else:
				filename += str(first_selected_file['values'][2])

			# Add dividier
			filename += DIVIDER

			# Add roll letter and two digit number if roll film
			number_padding = 3
			if self.roll_film.get():
				filename += self.get_roll_letter()
				number_padding = 2

			# Add sequence number
			filename += str(int(self.start_number.get())).zfill(number_padding)

			# Add appendix if its enabled
			if self.appendixing.get():
				filename += DIVIDER + self.get_appendix()

			# Add file extension
			filename += splitext(first_selected_file['values'][0])[1]

			self.preview_filename_label.configure(text=filename)
		else: 
			# Print an error if the filename data was not valid
			self.preview_filename_label.configure(text=filename_state) 

		# Call this function again in 25ms
		self.preview_filename_label.after(25, self.update_preview_filename)

	# Rename all selected files with entered data and/or an automatic date
	def rename_files(self):
		# Exit if we don't have the right data for proper file names
		if self.check_filename_entries() != FILENAME_VALID:
			return

		selected_files = self.file_list.selection()
		date_counters = {}

		for file in selected_files:
			file = self.file_list.item(file)
			filename = ""

			# Date
			date = ""
			if not self.auto_dating.get():
				date = self.get_year() + self.get_month() + self.get_day()
			else:
				date = str(file['values'][2])

			if date not in date_counters:
				date_counters[date] = 0

			filename += date

			# Divider
			filename += DIVIDER

			# Roll letter
			number_padding = 3
			if self.roll_film.get():
				filename += self.get_roll_letter()
				number_padding = 2

			# Sequence number
			filename += str(int(self.start_number.get()) + date_counters[date]).zfill(number_padding)

			# Appendix
			if self.appendixing.get():
				filename += DIVIDER + self.appendix.get()

			# File extension 
			filename += splitext(file['values'][0])[1]

			# Increment the date sequence
			date_counters[date] += 1

			# Rename the file
			os.rename(self.get_file_path(file['values'][0]), self.get_file_path(filename))

		self.load_folder()

	# Check the entered data for its validity, return error message if it's not
	def check_filename_entries(self):
		error = ""

		# Date
		if not self.auto_dating.get():
			year = self.get_year()
			if not(year.isnumeric() and int(year) > 0):
				error += FILENAME_INVALID_YEAR + "\n"
			
			if int(self.get_month()) == 0:
				error += FILENAME_NO_MONTH + "\n"
			
			day = self.get_day() 
			if not(day.isnumeric() and int(day) > 0 and int(day) <= 31): 
				error += FILENAME_INVALID_DAY + "\n"

		# Roll letter			
		if self.roll_film.get() and not(self.get_roll_letter().isalpha()):
			error += FILENAME_INVALID_ROLL_LETTER + "\n"

		# Start number for sequencing
		if not(self.start_number.get().isnumeric()):
			error += FILENAME_INVALID_NUMBER + "\n"

		# Appendix
		appendix = self.get_appendix() 
		if self.appendixing.get() and not(appendix.isalpha() and not appendix == ""):
			error += FILENAME_INVALID_APPENDIX + "\n"

		if error != "":
			return error
		else: 
			return FILENAME_VALID

	# Return a formatted version of the year entry box
	def get_year(self):
		return self.year.get().zfill(2)[-2:]

	# Return a numerical version of the month dropdown
	def get_month(self):
		return str(self.month.current() + 1).zfill(2)

	# Return a formatted version of the day entry box
	def get_day(self):
		return self.day.get().zfill(2)
	
	# Return a formatted version of the roll letter entry box
	def get_roll_letter(self):
		return self.roll_letter.get().upper()

	# Return a formatted version of the appendix entry box 
	def get_appendix(self):
		return self.appendix.get().lower()

	# Append the current open folder to the passed filename	
	def get_file_path(self, filename):
		return self.folder.get() + "/" + filename

if __name__ == "__main__":
	application = photograph_renamer()
	application.window.mainloop()