import csv, os, sys, ctypes, traceback
import pywintypes
import win32com.client as win32   # pip install pywin32

XL_OPENXML_WORKBOOK = 51  # xlOpenXMLWorkbook -> .xlsx


def error_window(message, title="Error"):
    MB_ICONERROR = 0x10
    ctypes.windll.user32.MessageBoxW(0, message, title, MB_ICONERROR)


def find_template(name):
    """Look for the template next to this script, then in Excel's XLSTART folder."""
    if os.path.isabs(name):
        return name if os.path.isfile(name) else None
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(here, name),
        os.path.join(os.environ.get("APPDATA", ""), "Microsoft", "Excel", "XLSTART", name),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def to_number(value):
    """Turn numeric strings into numbers so Excel stores them as numbers, not text."""
    try:
        return float(value)
    except ValueError:
        return value


def display_data(data,
                 header="Stock,Lot Value,Holding Years,Annualized Gain,Acnt Type",
                 template="Book.xltx"):

    # --- Step 1: parse input (header split on commas, data on whitespace) ---
    columns = [c.strip() for c in header.strip().split(",")]

    # maxsplit keeps a multi-word last field (e.g. "Roth IRA") together
    rows = [line.split(maxsplit=len(columns) - 1)
            for line in data.splitlines() if line.strip()]
    bad = [r for r in rows if len(r) != len(columns)]
    if bad:
        error_window(f"{len(bad)} row(s) don't have {len(columns)} fields.\n\n"
                     f"First bad row:\n{' '.join(bad[0])}",
                     "Bad input")
        sys.exit(1)

    # --- Step 2: write data.csv to a local folder OneDrive doesn't sync ---
    out_dir = os.path.join(os.environ["LOCALAPPDATA"], "YF-Analyzer")
    os.makedirs(out_dir, exist_ok=True)
    xlsx_path = os.path.join(out_dir, "data.xlsx")
    csv_path = os.path.join(out_dir, "data.csv")
    print("Output file:", xlsx_path)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)   # e.g. "Lot Value" stays one column
        writer.writerows(rows)

    # --- Step 3: locate the Excel template ---
    template_path = find_template(template)
    if not template_path:
        error_window(f"Couldn't find the template '{template}'.\n\n"
                     "Put it next to this script or in "
                     "%APPDATA%\\Microsoft\\Excel\\XLSTART.",
                     "Template not found")
        sys.exit(1)

    # --- Step 4: create a workbook from the template, fill it, save as data.xlsx ---
    try:
        excel = win32.Dispatch("Excel.Application")
        excel.Visible = True

        # Close any open data.xlsx so it can be replaced
        # (Excel can't have two workbooks with the same name open)
        for open_wb in list(excel.Workbooks):
            if open_wb.Name.lower() == "data.xlsx":
                open_wb.Close(SaveChanges=False)

        wb = excel.Workbooks.Add(template_path)   # new workbook based on Book.xltx
        ws = wb.Worksheets(1)

        values = [columns] + [[to_number(v) for v in r] for r in rows]
        n_rows, n_cols = len(values), len(columns)
        ws.Range(ws.Cells(1, 1), ws.Cells(n_rows, n_cols)).Value = \
            tuple(tuple(r) for r in values)

        excel.DisplayAlerts = False   # lets SaveAs overwrite without a prompt
        try:
            wb.SaveAs(xlsx_path, FileFormat=XL_OPENXML_WORKBOOK)
        finally:
            excel.DisplayAlerts = True

    except Exception as e:
        detail = traceback.format_exc()
        if isinstance(e, pywintypes.com_error):
            hresult, strerror, excepinfo, _ = e.args
            excel_msg = excepinfo[2] if excepinfo else strerror
            detail = f"Excel says: {excel_msg}\n\nHRESULT: {hresult}\n\n" + detail
        print(detail)
        error_window(f"Couldn't create the workbook in Excel.\n\n{detail}", "Excel error")
        sys.exit(1)


if __name__ == "__main__":
    sample = """
AAPL   15230.500  3.2   12.4  IRA
MSFT   8420.00   1.5   18.9  Taxable
VTI    22100.75  6.0   9.7   Roth IRA
"""
    display_data(sample)
