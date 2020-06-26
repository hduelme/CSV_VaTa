# CSV_VaTa
A tool to validate CSV-files based on a config file.

## Function describtion
- The tool displays csv-files as a table and validates the loaded values.
- The table could be splitted into multiple pages with a predefined number of lines based on the config file.
- The first validation will happen when loading the file. The User will be informed of every error while validating.
- After the file is loaded you will see all lines with error are gray and the fields with errors are red.
- When hovering over an error-field a text will show up and describes the error (notice at the moment these texts are coded in German only).
* The following functions are available:
  * load csv-file
  * save to csv-file
  * validate data:
    * current Page
    * on loading
    * on save
  * add new row
  * delete row
 
## Run the program
Before you can run the tool from command line you have to fulfill the preconditions (see below). Then just run `python .\gui.py` in the project folder.

If you want to use a compiled version under Windows, you can find the executable program here in the release section.

## Dependencies
To run the polarogram on command line you need [python Version 3](https://www.python.org/downloads/) and PyQt5.
PyQt5 can be installed with `pip install PyQt5`.

## Compiling for Windows
For compiling the program yourself for windows, you need all preconditions (described before) and `auto-pip-to-exe`. To install auto-pip-to-exe, run `pip install auto-py-to-exe`.

Then compile it with `auto-py-to-exe`, set the reference for icon and set the compiler to `One-File` and `Window Based'.
