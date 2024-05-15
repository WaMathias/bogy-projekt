import openpyxl
import os
from src.utils.utils import logger


def create_excel_sheet():
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Pi Estimation Data"
    sheet.append(["Iteration", "Pi Estimate", "Time Taken (s)", "Num Darts", "Dart Step", "Method"])
    return wb, sheet


def write_to_excel(sheet, data):
    for row in data:
        sheet.append(row)


def save_excel(wb, filename):
    try:
        if os.path.exists(filename):
            os.remove(filename)
        wb.save(filename)
        return True
    except Exception as e:
        logger(f"Error saving Excel file: {e}", level='error')
        return False
