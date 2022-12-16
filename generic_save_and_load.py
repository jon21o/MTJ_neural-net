import tkinter as tk
from tkinter import filedialog


def save_xrDataArray(xrDataArray, **options):
    """Save an Xarray DataArray to file"""
    # if option is given, use that as the path instead of opening a file dialog
    if "file_name_and_path" in options:
        file_name_and_path = options["file_name_and_path"]
    else:
        # open file dialog to save data to file
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        file_name_and_path = filedialog.asksaveasfilename()

    # Make sure the file name ends with .nc corresponding to a DataArray
    if not file_name_and_path.endswith(".nc"):
        file_name_and_path += ".nc"

    # Store the attributes in the DataArray as well
    if "attrs" in options:
        for key, value in options["attrs"].items():
            xrDataArray.attrs[key] = value

    xrDataArray.to_netcdf(file_name_and_path)


def load_xrDataArray():
    """Load an Xarray DataArray from file"""
    # Open file dialog, select file, and get path for opening
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    file_name_and_path = filedialog.askopenfilename()

    return file_name_and_path
