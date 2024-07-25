# Copyright (c) 2024 Charles Knell - All Rights Reserved
# This software is licensed under the GPL-3.0 license.
# See the LICENSE.md file in the GitHub repository at:
# https://github.com/CharlesKnell/YF-Analyzer/blob/main/LICENSE.md
# The imported package licenses are also listed in this file.

import tkinter as tk
from tkinter import filedialog
from yfsp_collect import collect
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
            if items[0] == "browser_full_path_filename":
                browser_full_path_file_filename = items[1].strip()
            elif items[0] == "export_download_link":
                export_download_link = items[1].strip()
            elif items[0] == "min_holding_years":
                min_holding_years = items[1].strip()
            elif items[0] == "download_folder":
                download_folder = items[1].strip()
        ini_file_items = [browser_full_path_file_filename, export_download_link, min_holding_years, download_folder]
    return ini_file_items


def handle_change_downloads_folder_button_click():
    downloads_file_path = filedialog.askdirectory()
    downloads_file_path = downloads_file_path.replace("/", "\\")
    entry_download_folder.delete(0, tk.END)
    entry_download_folder.insert(0, downloads_file_path)
    update_ini_file("download_folder", downloads_file_path)


def handle_browser_button_click():
    browser_file_path = filedialog.askopenfilename()
    print("browser fullpathfilename", browser_file_path)
    entry_browser.delete(0, tk.END)
    entry_browser.insert(0, browser_file_path)
    update_ini_file("browser_full_path_filename", entry_browser.get())
    # entry_browser_filepath = entry_browser.get()


def open_edge(browser):
    url = "https://finance.yahoo.com"
    browser_path = browser
    webbrowser.register('edge', None, webbrowser.BackgroundBrowser(browser_path))
    webbrowser.get('edge').open(url)


def minimize_edge():
    edge_windows = [w for w in gw.getWindowsWithTitle('Edge') if 'Edge' in w.title]
    if edge_windows:
        edge_windows[0].minimize()


def handle_collect_button_click():
    min_holding_years = entry_min_holding_years.get()
    folder_path = entry_download_folder.get()
    browser = entry_browser.get()
    export_link = entry_export_link.get()
    open_edge(browser)
    text_to_display = collect(min_holding_years, folder_path, browser, export_link)
    # clear output_text before inserting new text
    output_text.delete(1.0, tk.END)
    output_text.insert(tk.END, text_to_display)
    # lift root window to front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    # minimize the edge window
    minimize_edge()


def handle_save_yf_export_link_button_click():
    update_ini_file("export_download_link", entry_export_link.get())


def save_min_holding_years_button_click():
    update_ini_file("min_holding_years", entry_min_holding_years.get())


root = tk.Tk()
root.title("Yahoo Finance Stock Performance Analyzer 1.2.2")
root.geometry("780x780")

# Create some widgets to put in the grid
label_browser = tk.Label(root, text="Browser Path")
label_yfdl_link = tk.Label(root, text="Yahoo Finance Export Link")
button_browser = tk.Button(root, text="Change Path to MS Edge Browser", command=handle_browser_button_click)
button_yf_export_link = tk.Button(root, text="Save Yahoo Finance Export Link",
                                  command=handle_save_yf_export_link_button_click)

scrollbar = tk.Scrollbar(root)
collect_button = tk.Button(root, text="Collect Data", command=handle_collect_button_click)

label_download_folder = tk.Label(root, text="Downloads Folder")
button_download_folder = tk.Button(root, text="Change Path to Downloads Folder",
                                   command=handle_change_downloads_folder_button_click)

entry_download_folder = tk.Entry(root, width=120)
entry_download_folder.delete(0, tk.END)
entry_download_folder.insert(0, read_ini_file()[3])

entry_browser = tk.Entry(root, width=120)
entry_browser.delete(0, tk.END)
entry_browser.insert(0, read_ini_file()[0])

entry_export_link = tk.Entry(root, width=120)
# change color to light grey
# entry_export_link.config(fg="lightgrey")
entry_export_link.delete(0, tk.END)
entry_export_link.insert(0, read_ini_file()[1])

button_min_holding_years = tk.Button(root, text="Save Min Holding Years",
                                     command=save_min_holding_years_button_click)
label_min_holding_years = tk.Label(root, text="Min Holding Years")
entry_min_holding_years = tk.Entry(root, width=3)
entry_min_holding_years.delete(0, tk.END)
mhy = read_ini_file()[2]
entry_min_holding_years.insert(0, mhy)

label_collect_instructions1 = tk.Label(root, text="Using Microsoft Edge")
label_collect_instructions2 = tk.Label(root, text="Login to Your Yahoo Account")
label_collect_instructions3 = tk.Label(root, text="Before Collecting Data")

label_output_text1 = tk.Label(root, text="holding       annualized")
label_output_text2 = tk.Label(root, text="stock                   value              years            gain")
output_text = tk.Text(root, height=30, width=35)

# Use the grid manager to place the widgets in the grid
label_browser.grid(row=0, column=0, sticky="ws", padx=27, pady=5)

entry_browser.grid(row=1, column=0, columnspan=3, padx=30)
button_browser.grid(row=0, column=1, pady=5, sticky="w")

label_yfdl_link.grid(row=2, column=0, sticky="sw", padx=27, pady=5)
button_yf_export_link.grid(row=2, column=1, pady=5, columnspan=1, sticky="w")
entry_export_link.grid(row=3, column=0, columnspan=3, padx=30)

label_download_folder.grid(row=4, column=0, sticky="ws", padx=27, pady=5)
button_download_folder.grid(row=4, column=1, sticky="w", pady=5)
entry_download_folder.grid(row=5, column=0, columnspan=3, padx=30)

label_min_holding_years.grid(row=6, column=0, sticky="ws", padx=27, pady=5)
button_min_holding_years.grid(row=6, column=1, sticky="w", pady=5)
entry_min_holding_years.grid(row=7, column=0, sticky="w", padx=30)

label_output_text1.grid(row=8, column=1, sticky="nw", padx=143)
label_output_text2.grid(row=9, column=1, sticky="nw")
output_text.grid(row=10, column=1, sticky="nw")

collect_button.grid(row=10, column=0, pady=90, columnspan=1, sticky="nw", padx=30)

label_collect_instructions1.grid(row=10, column=0, columnspan=1, sticky="nw", padx=30, pady=20)
label_collect_instructions2.grid(row=10, column=0, columnspan=1, sticky="nw", padx=30, pady=40)
label_collect_instructions3.grid(row=10, column=0, columnspan=1, sticky="nw", padx=30, pady=60)

scrollbar.grid(row=10, column=1, sticky="ens", padx=150, pady=5)
output_text.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=output_text.yview)

root.mainloop()
