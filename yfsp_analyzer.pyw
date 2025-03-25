# Copyright (c) 2024 Charles Knell - All Rights Reserved
# This software is licensed under the GPL-3.0 license.
# See the LICENSE.md file in the GitHub repository at:
# https://github.com/CharlesKnell/YF-Analyzer/blob/main/LICENSE.md
# The imported package licenses are also listed in this file.

import tkinter as tk
from tkinter import filedialog
from yfsp_collect import collect
from yfsp_collect import prepare_downloads_folder
from send2trash import send2trash
import os
import webbrowser
import pygetwindow as gw


def update_ini_file(key, value):
    if os.path.exists("yfsp_new.ini"):
        send2trash("yfsp_new.ini")
    with open("yfsp.ini", "r") as f_old:
        for line_old in f_old:
            items_old = line_old.split("==")
            with open("yfsp_new.ini", "a") as f_new:
                if key == items_old[0]:
                    record_to_update = key + "==" + value + "\n"
                    f_new.write(record_to_update)
                else:
                    f_new.write(line_old)

    if os.path.exists("yfsp.ini"):
        send2trash("yfsp.ini")

    os.rename("yfsp_new.ini", "yfsp.ini")


def read_ini_file():
    with open("yfsp.ini", "r") as f:
        for line in f:
            items = line.split("==")
            if items[0] == "min_holding_years":
                min_holding_years = items[1].strip()
            elif items[0] == "download_folder":
                download_folder = items[1].strip()
        ini_file_items = [min_holding_years, download_folder]
    return ini_file_items


def handle_change_downloads_folder_button_click():
    downloads_file_path = filedialog.askdirectory()
    downloads_file_path = downloads_file_path.replace("/", "\\")
    entry_download_folder.delete(0, tk.END)
    entry_download_folder.insert(0, downloads_file_path)
    update_ini_file("download_folder", downloads_file_path)


def handle_collect_button_click():
    min_holding_years = entry_min_holding_years.get()
    folder_path = entry_download_folder.get() + "\\portfolio.csv"
    text_to_display = collect(min_holding_years, folder_path)
    # clear output_text before inserting new text
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, text_to_display)
    # lift root window to front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)


def handle_prepare_button_click():
    folder_path = entry_download_folder.get()
    prepare_downloads_folder(folder_path)
    print("Downloads folder prepared")


def save_min_holding_years_button_click():
    update_ini_file("min_holding_years", entry_min_holding_years.get())


root = tk.Tk()
root.title("Yahoo Finance Stock Performance Analyzer 1.3.0")
root.geometry("780x780")

scrollbar = tk.Scrollbar(root)
collect_button = tk.Button(root, text="3. Collect Data", command=handle_collect_button_click)
prepare_button = tk.Button(root, text="1. Prepare Downloads Folder", command=handle_prepare_button_click)
label_download_folder = tk.Label(root, text="Downloads Folder")
button_download_folder = tk.Button(root, text="Change Path to Downloads Folder",
                                   command=handle_change_downloads_folder_button_click)

entry_download_folder = tk.Entry(root, width=120)
entry_download_folder.delete(0, tk.END)
entry_download_folder.insert(0, read_ini_file()[1])

button_min_holding_years = tk.Button(root, text="Save Min Holding Years",
                                     command=save_min_holding_years_button_click)
label_min_holding_years = tk.Label(root, text="Min Holding Years")
entry_min_holding_years = tk.Entry(root, width=3)
entry_min_holding_years.delete(0, tk.END)
mhy = read_ini_file()[0]
entry_min_holding_years.insert(0, mhy)

label_instructions1 = tk.Label(root, text="2. Download Yahoo Finance Portfolio")
label_instructions2 = tk.Label(root, text="    using the Yahoo Finance window")

label_output_text1 = tk.Label(root, text="holding       annualized")
label_output_text2 = tk.Label(root, text="stock                   value              years            gain")
output_text = tk.Text(root, height=30, width=35)

label_download_folder.grid(row=4, column=0, sticky="ws", padx=27, pady=5)
button_download_folder.grid(row=4, column=1, sticky="w", pady=5)
entry_download_folder.grid(row=5, column=0, columnspan=3, padx=30)

label_min_holding_years.grid(row=6, column=0, sticky="ws", padx=27, pady=5)
button_min_holding_years.grid(row=6, column=1, sticky="w", pady=5)
entry_min_holding_years.grid(row=7, column=0, sticky="w", padx=30)

label_output_text1.grid(row=8, column=1, sticky="nw", padx=143)
label_output_text2.grid(row=9, column=1, sticky="nw")
output_text.grid(row=10, column=1, sticky="nw")

prepare_button.grid(row=10, column=0,  columnspan=1, sticky="nw", padx=30, pady=45)
label_instructions1.grid(row=10, column=0, columnspan=1, sticky="nw", padx=30, pady=80)
label_instructions2.grid(row=10, column=0, columnspan=1, sticky="nw", padx=30, pady=100)
collect_button.grid(row=10, column=0, columnspan=1, sticky="nw", padx=30, pady=125)

scrollbar.grid(row=10, column=1, sticky="ens", padx=150, pady=5)
output_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=output_text.yview)

root.mainloop()
