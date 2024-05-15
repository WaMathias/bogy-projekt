import sys
import time
import os
import logging
from colorama import init, Fore
from mpi4py import MPI

project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_dir)

from utils.utils import generate_timestamp, logger, check_folder
from estimation.estimation import estimate_pi_send_receive, estimate_pi_reduce, gather_results, send_results, \
    throw_darts
from excel.excel import create_excel_sheet, save_excel, write_to_excel
from plot.plot import plot_pi_estimate, plot_pi_difference, plot_time_taken

os.environ["XDG_SESSION_TYPE"] = "xcb"
init()

logging.basicConfig(filename='../app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def main(method_sel=None, max_darts=None, dart_step=None, duration=None, debug_mode=True):
    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size

    wb, sheet = create_excel_sheet()

    start_time = time.monotonic()
    num_iterations = 0
    num_darts_per_process = dart_step if dart_step else 2500
    data = []

    while True:
        pi_estimate_send_receive = None
        pi_estimate_reduce = None

        method_start_time = time.monotonic()

        if method_sel == "both":
            pi_estimate_send_receive = estimate_pi_send_receive(num_darts_per_process, comm)
            send_receive_time = time.monotonic() - method_start_time

            method_start_time = time.monotonic()

            pi_estimate_reduce = estimate_pi_reduce(num_darts_per_process, comm)
            reduce_time = time.monotonic() - method_start_time
        elif method_sel == "send_receive":
            pi_estimate_send_receive = estimate_pi_send_receive(num_darts_per_process, comm)
            send_receive_time = time.monotonic() - method_start_time
        elif method_sel == "reduce":
            pi_estimate_reduce = estimate_pi_reduce(num_darts_per_process, comm)
            reduce_time = time.monotonic() - method_start_time

        if pi_estimate_send_receive:
            data.append([num_iterations, pi_estimate_send_receive, send_receive_time, num_darts_per_process * size,
                         num_darts_per_process, "send_receive"])
        if pi_estimate_reduce:
            data.append([num_iterations, pi_estimate_reduce, reduce_time, num_darts_per_process * size,
                         num_darts_per_process, "reduce"])

        num_iterations += 1

        if max_darts and num_darts_per_process * size >= max_darts:
            break

        num_darts_per_process += dart_step if dart_step else 2500

        if duration and time.monotonic() - start_time >= duration:
            break

    if rank == 0:
        write_to_excel(sheet, data)

        timestamp = generate_timestamp()
        excel_dir = os.path.join(".", "excel")
        estimation_dir = os.path.join(".", "png", "estimation")
        difference_dir = os.path.join(".",  "png", "pi_difference")
        runtime_dir = os.path.join(".", "png", "runtime")

        os.makedirs(excel_dir, exist_ok=True)
        os.makedirs(estimation_dir, exist_ok=True)
        os.makedirs(difference_dir, exist_ok=True)
        os.makedirs(runtime_dir, exist_ok=True)

        filename_excel = os.path.join(excel_dir, f"pi_estimation_data_{timestamp}.xlsx")
        filename_pi_estimate = os.path.join(estimation_dir, f"pi_estimate_plot_{timestamp}.png")
        filename_pi_difference = os.path.join(difference_dir, f"pi_difference_plot_{timestamp}.png")
        filename_time_taken = os.path.join(runtime_dir, f"time_taken_plot_{timestamp}.png")

        try:
            save_excel(wb, filename_excel)
            logger(f"Excel file saved successfully saved at: {filename_excel}")
            plot_pi_estimate(data, filename_pi_estimate)
            logger(f"Estimation_pi graph successfully saved at: {filename_pi_estimate}")
            plot_pi_difference(data, filename_pi_difference)
            logger(f"Pi Difference graph successfully saved at: {filename_pi_difference}")
            plot_time_taken(data, filename_time_taken)
            logger(f"Runtime graph successfully saved at: {filename_time_taken}")

            logger("Excel file and plots saved successfully.")
        except Exception as e:
            logger(f"Error saving Excel file or plots: {e}", level='error')
            logging.exception("Error occurred while saving Excel file or plots.")

        os.system(f"libreoffice --calc {filename_excel}")
        sys.exit()


if __name__ == "__main__":
    logger("Program has been started")

    if len(sys.argv) < 2:
        logger("FATAL ERROR; wrong usage: python3 main.py [method] [max_darts] [dart_step] [duration] [debug_mode]", level="error")
        logger("[method] should be 'send_receive', 'reduce', or 'both'", level='error')
        logger("[debug_mode] should be 'True' or 'False'", level="error")
        sys.exit(1)

    check_folder()

    method = sys.argv[1] if len(sys.argv) > 1 else "both"
    max_darts = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
    dart_step = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else 2500
    duration = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4].isdigit() else 10
    debug_mode = sys.argv[5].lower() == 'true' if len(sys.argv) > 5 else True

    if debug_mode:
        logger(f"Method is going to be used: {method}", level="debug")
        logger(f"Amounts are going to be used: {max_darts}", level="debug")
        logger(f"The amount of darts is getting in steps: {dart_step}", level="debug")
        logger(f"The duration of the program is going to be: {duration} seconds", level="debug")
        logger(f"Debug Mode is {debug_mode}", level="debug")

        if len(sys.argv) < 2:
            logger("FATAL ERROR; wrong usage: python3 main.py [method] [max_darts] [dart_step] [duration] [debug_mode]",
                   level="error")
            logger("[method] should be 'send_receive', 'reduce', or 'both'", level='error')
            logger("[debug_mode] should be 'True' or 'False'", level="error")
            sys.exit(1)

    print(sys.argv)

    main(method, max_darts, dart_step, duration, debug_mode)

