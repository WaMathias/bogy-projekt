import sys
import os
import logging
from colorama import init, Fore
import datetime


def debug_mode():
    return os.getenv("DEBUG_MODE", "").lower() == "true"


def generate_timestamp():
    return datetime.datetime.now().strftime("%Y-%d-%m_%H-%M-%S")


def logger(message, level='info'):
    if debug_mode():
        log_message = f"[{generate_timestamp()}] [{logging.getLogger(__name__)}] [{level.upper()}]: {message}"

        if level.lower() == 'info':
            logging.info(log_message)
            print(Fore.GREEN + log_message + Fore.RESET)
        elif level.lower() == 'debug':
            logging.debug(log_message)
            print(Fore.MAGENTA + log_message + Fore.RESET)
        elif level.lower() == 'warning':
            logging.warning(log_message)
            print(Fore.YELLOW + log_message + Fore.RESET)
        elif level.lower() == 'error':
            logging.error(log_message)
            print(Fore.RED + log_message + Fore.RESET)
        elif level.lower() == '':
            logging.info(log_message)
            print(Fore.WHITE + log_message + Fore.RESET)
        else:
            logging.error("There is a misconfiguration with the logger")
    else:
        if level.lower() == 'debug':
            return
        elif level.lower() == 'info':
            return
        elif level.lower() == '':
            return
        else:
            log_message = f"[{generate_timestamp()}] [{logging.getLogger(__name__)}] [{level.upper()}]: {message}"
            if level.lower() == 'error':
                logging.error(log_message)
                print(Fore.RED + log_message + Fore.RESET)
            else:
                logging.error("There is a misconfiguration with the logger")


def check_folder():
    excel_folder = "././excel"
    png_folder = "././png"
    estimation_folder = "././png/estimation"
    pi_difference_folder = "././png/pi_difference"
    runtime_folder = "././png/runtime"

    if not os.path.exists(excel_folder):
        os.mkdir(excel_folder)
        logger(f"{excel_folder} folder created", level='warning')
    if not os.path.exists(png_folder):
        os.mkdir(png_folder)
        logger(f"{png_folder} folder created", level='warning')
    if not os.path.exists(estimation_folder):
        os.mkdir(estimation_folder)
        logger(f"{estimation_folder} folder created", level='warning')
    if not os.path.exists(pi_difference_folder):
        os.mkdir(pi_difference_folder)
        logger(f"{excel_folder} folder created", level='warning')
    if not os.path.exists(runtime_folder):
        os.mkdir(runtime_folder)
        logger(f"{excel_folder} folder created", level='warning')