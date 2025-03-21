# Copyright (c) 2024 Charles Knell - All Rights Reserved
# This software is licensed under the GPL-3.0 license.
# See the LICENSE.md file in the GitHub repository at:
# https://github.com/CharlesKnell/YF-Analyzer/blob/main/LICENSE.md
# The imported package licenses are also listed in this file.

import sys
import csv
import datetime
import os
import time
from send2trash import send2trash
import subprocess
import tkinter as tk
from tkinter import messagebox


def prepare_downloads_folder(folder_path):
    # delete the quotes.csv and family files and download a quotes.csv file
    # folder_path = "C:\\Users\\charl\\Downloads\\"
    folder_path = folder_path + "\\"
    # print("download_my_portfolio line 11", folder_path)
    file_list = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    # file_list is a list of files in the folder_path folder

    # delete the quotes.csv, quotes (1).csv, quotes (2).csv etc. files
    # delete the portfolio.csv, portfolio (1).csv, etc. files
    for afile in file_list:
        if (afile.startswith("quotes") or afile.startswith("portfolio")) and afile.endswith(".csv"):
            file_to_delete = folder_path + afile
            print("move to recycle bin:", file_to_delete)
            send2trash(file_to_delete)
    time.sleep(2)  # 2 sec delay


def collect(min_holding_years, filepath):
    ctr = 0
    while True:
        if not os.path.exists(filepath):
            seconds_of_delay = 2
            time.sleep(seconds_of_delay)
            print(seconds_of_delay, "Sec Delay (allowing for file to appear in download folder)")
            ctr += 1
            if ctr == 4:
                sys.exit(1)
            continue
        else:
            break

    lot_rows = []
    with open(filepath, "r") as csvfile:
        csvreader = csv.reader(csvfile)

        # Skip header row (if any)
        next(csvreader, None)

        # Read each row of CSV file into a list
        for row in csvreader:
            lot_rows.append(row)

    stock_lots_dict = {}  # records how many lots a stock has
    for row in lot_rows:
        stockname = row[0]
        if stockname not in stock_lots_dict:
            stock_lots_dict[stockname] = 1
        else:
            stock_lots_dict[stockname] += 1

    # sort the stock_lots_dict in alphabetical order
    sorted_stock_lots_dict = {}
    for key, value in sorted(stock_lots_dict.items(), key=lambda item1: item1[0]):
        sorted_stock_lots_dict[key] = value
    stock_lots_dict = sorted_stock_lots_dict

    stock_dict = {}  # for each stock, records a list of lists of lot information

    for stock in stock_lots_dict:
        lotlist = list()
        for row in lot_rows:
            if stock == row[0]:
                lot = row[1:]
                lotlist.append(lot)
        stock_dict[stock] = lotlist

    # for each stock, for each lot, compute annualized gain; record stock_ann_gain_dict
    stock_ann_gain_lol = []
    for stock in stock_dict:
        if not stock.startswith("$$"):
            lotlist = stock_dict[stock]
            for lotnum in range(stock_lots_dict[stock]):
                current_price = lotlist[lotnum][0]
                trade_date = lotlist[lotnum][8]
                shares = float(lotlist[lotnum][10])
                purchase_price = lotlist[lotnum][9]
                current_date_dto = datetime.datetime.now()
                td_format_str = '%Y%m%d'
                trade_date_dto = datetime.datetime.strptime(trade_date, td_format_str)
                # td_dateonly = trade_date_dto.date()

                holding_timedelta_obj = current_date_dto - trade_date_dto
                holding_years = holding_timedelta_obj.total_seconds() / (365.2425 * 24 * 60 * 60)

                if current_price == '':  # this happens when a stock is delisted
                    current_price = '0'
                current_value = float(current_price) * shares
                purchase_value = float(purchase_price) * shares

                annualized_gain_in_percent = (((current_value / purchase_value) ** (1/holding_years)) - 1.0) * 100

                # print(f'{stock} {current_value:.2f} {holding_years:.2f} {annualized_gain_in_percent:.2f}')

                if holding_years > float(min_holding_years):
                    stock_ann_gain_lol.append([stock, current_value, holding_years, annualized_gain_in_percent])

    # output stock, value, years held, and annualized gain for stock held for more than the minimum holding years
    output_str = ""
    for list_of_data in stock_ann_gain_lol:
        ctr = 1
        for item in list_of_data:
            if ctr == 1:
                len_item = len(f'{item}')
                rs_spacer = ""
                for x in range(7 - len_item):
                    rs_spacer += " "
                # print(f'{item}', rs_spacer, end='')
                output_str += f'{item}' + rs_spacer
            else:
                item_str = f'{item:.2f}'
                len_item = len(item_str)

                if ctr == 2:
                    ls_spacer = ""
                    for y in range(9 - len_item):
                        ls_spacer += " "
                    output_str += ls_spacer + item_str

                if ctr == 3:
                    ls_spacer = ""
                    for x in range(7 - len_item):
                        ls_spacer += " "
                    output_str += ls_spacer + item_str
                if ctr == 4:
                    ls_spacer = ""
                    for x in range(8 - len_item):
                        ls_spacer += " "
                    output_str += ls_spacer + item_str + "\n"
            ctr += 1

    return output_str

