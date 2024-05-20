import numpy as np
from mpi4py import MPI
import random
import time
import openpyxl
import datetime
import os
import matplotlib.pyplot as plt
import sys
import logging
from colorama import init, Fore

os.environ["XDG_SESSION_TYPE"] = "xcb"
debug_mode = False
init()

if os.path.exists('../app.log'):
    os.remove('../app.log')
    logging.basicConfig(filename='../app.log', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(filename='../app.log', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def throw_darts(num_darts):
    darts_inside_circle = sum(
        1 for _ in range(num_darts) if random.uniform(-1, 1) ** 2 + random.uniform(-1, 1) ** 2 <= 1)
    return darts_inside_circle


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


def estimate_pi_send_receive(num_darts_per_process, comm):
    darts_inside_circle = throw_darts(num_darts_per_process)

    if comm.rank == 0:
        total_darts_inside_circle, total_darts_per_process = gather_results(darts_inside_circle, num_darts_per_process,
                                                                            comm)
        total_darts = total_darts_per_process
        pi_estimate = 4 * total_darts_inside_circle / total_darts
        return pi_estimate
    else:
        send_results(darts_inside_circle, num_darts_per_process, comm)
        return None


def estimate_pi_reduce(num_darts_per_process, comm):
    darts_inside_circle = throw_darts(num_darts_per_process)

    total_darts_inside_circle = comm.reduce(darts_inside_circle, op=MPI.SUM, root=0)
    total_darts_per_process = comm.reduce(num_darts_per_process, op=MPI.SUM, root=0)

    if comm.rank == 0:
        total_darts = total_darts_per_process
        pi_estimate = 4 * total_darts_inside_circle / total_darts
        return pi_estimate
    else:
        return None


def gather_results(darts_inside_circle, num_darts_per_process, comm):
    total_darts_inside_circle = darts_inside_circle
    total_darts_per_process = num_darts_per_process
    for i in range(1, comm.size):
        received_darts_inside_circle = comm.recv(source=i)
        received_darts_per_process = comm.recv(source=i)
        total_darts_inside_circle += received_darts_inside_circle
        total_darts_per_process += received_darts_per_process
    return total_darts_inside_circle, total_darts_per_process


def send_results(darts_inside_circle, num_darts_per_process, comm):
    comm.send(darts_inside_circle, dest=0)
    comm.send(num_darts_per_process, dest=0)


def write_to_excel(sheet, data):
    for row in data:
        sheet.append(row)


def plot_pi_estimate(data, filename_send_receive, filename_reduce):
    num_darts = np.array([row[3] for row in data], dtype=float)
    pi_estimates_send_receive = np.array([row[1] if row[5] == "send_receive" else None for row in data], dtype=float)
    pi_estimates_reduce = np.array([row[1] if row[5] == "reduce" else None for row in data], dtype=float)

    valid_send_receive = ~np.isnan(pi_estimates_send_receive)
    valid_reduce = ~np.isnan(pi_estimates_reduce)

    num_darts_interp = np.linspace(num_darts.min(), num_darts.max(), num=500)
    pi_estimates_send_receive_interp = np.interp(num_darts_interp, num_darts[valid_send_receive],
                                                 pi_estimates_send_receive[valid_send_receive])
    pi_estimates_reduce_interp = np.interp(num_darts_interp, num_darts[valid_reduce], pi_estimates_reduce[valid_reduce])

    plt.figure(figsize=(10, 5))
    plt.plot(num_darts_interp, pi_estimates_send_receive_interp, color='blue', linestyle='-',
             label='Pi Estimate (Send/Receive)')
    plt.plot(num_darts_interp, pi_estimates_reduce_interp, color='red', linestyle='-', label='Pi Estimate (Reduce)')
    plt.xlabel('Number of Darts')
    plt.ylabel('Pi Estimate')
    plt.title('Estimation of Pi')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename_send_receive)
    plt.savefig(filename_reduce)
    plt.close()


def plot_pi_difference(data, filename_send_receive, filename_reduce):
    num_darts = np.array([row[3] for row in data], dtype=float)
    pi_estimates_send_receive = np.array([row[1] if row[5] == "send_receive" else None for row in data], dtype=float)
    pi_estimates_reduce = np.array([row[1] if row[5] == "reduce" else None for row in data], dtype=float)

    pi_difference_send_receive = []
    pi_difference_reduce = []

    for pi_estimate in pi_estimates_send_receive:
        if pi_estimate is not None:
            pi_difference_send_receive.append(abs(np.pi - pi_estimate))
        else:
            pi_difference_send_receive.append(None)

    for pi_estimate in pi_estimates_reduce:
        if pi_estimate is not None:
            pi_difference_reduce.append(abs(np.pi - pi_estimate))
        else:
            pi_difference_reduce.append(None)

    pi_difference_send_receive = np.array(pi_difference_send_receive, dtype=float)
    pi_difference_reduce = np.array(pi_difference_reduce, dtype=float)

    valid_send_receive = ~np.isnan(pi_difference_send_receive)
    valid_reduce = ~np.isnan(pi_difference_reduce)

    num_darts_interp = np.linspace(num_darts.min(), num_darts.max(), num=500)
    pi_difference_send_receive_interp = np.interp(num_darts_interp, num_darts[valid_send_receive],
                                                  pi_difference_send_receive[valid_send_receive])
    pi_difference_reduce_interp = np.interp(num_darts_interp, num_darts[valid_reduce],
                                            pi_difference_reduce[valid_reduce])

    plt.figure(figsize=(10, 5))
    plt.plot(num_darts_interp, pi_difference_send_receive_interp, color='blue', linestyle='-',
             label='Pi Difference (Send/Receive)')
    plt.plot(num_darts_interp, pi_difference_reduce_interp, color='red', linestyle='-', label='Pi Difference (Reduce)')
    plt.xlabel('Number of Darts')
    plt.ylabel('Pi Difference')
    plt.title('Difference from Pi Estimate')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename_send_receive)
    plt.savefig(filename_reduce)
    plt.close()


def plot_time_taken(data, filename_send_receive, filename_reduce):
    num_darts = np.array([row[3] for row in data], dtype=float)
    time_taken_send_receive = np.array([row[2] if row[5] == "send_receive" else None for row in data], dtype=float)
    time_taken_reduce = np.array([row[2] if row[5] == "reduce" else None for row in data], dtype=float)

    valid_send_receive = ~np.isnan(time_taken_send_receive)
    valid_reduce = ~np.isnan(time_taken_reduce)

    num_darts_interp = np.linspace(num_darts.min(), num_darts.max(), num=500)
    time_taken_send_receive_interp = np.interp(num_darts_interp, num_darts[valid_send_receive],
                                               time_taken_send_receive[valid_send_receive])
    time_taken_reduce_interp = np.interp(num_darts_interp, num_darts[valid_reduce], time_taken_reduce[valid_reduce])

    plt.figure(figsize=(10, 5))
    plt.plot(num_darts_interp, time_taken_send_receive_interp, color='blue', linestyle='-',
             label='Time Taken (Send/Receive) (s)')
    plt.plot(num_darts_interp, time_taken_reduce_interp, color='red', linestyle='-', label='Time Taken (Reduce) (s)')
    plt.xlabel('Number of Darts')
    plt.ylabel('Time Taken (s)')
    plt.title('Time Taken for Estimation')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename_send_receive)
    plt.savefig(filename_reduce)
    plt.close()


def create_excel_sheet():
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Pi Estimation Data"
    sheet.append(["Iteration", "Pi Estimate", "Time Taken (s)", "Num Darts", "Dart Step", "Method"])
    return wb, sheet


def save_excel(wb, filename):
    if os.path.exists(filename):
        os.remove(filename)
    wb.save(filename)


def generate_timestamp():
    return datetime.datetime.now().strftime("%Y-%d-%m_%H-%M-%S")


def logger(message, level='info'):
    if debug_mode:
        log_message = f"[{generate_timestamp()}] [{logging.getLogger(__name__)}] [{level.upper()}]: {message}"

        if level.lower() == 'info':
            logging.info(log_message)
            print(Fore.GREEN + log_message + Fore.RESET)
        elif level.lower() == 'warning':
            logging.warning(log_message)
            print(Fore.YELLOW + log_message + Fore.RESET)
        elif level.lower() == 'error':
            logging.error(log_message)
            print(Fore.RED + log_message + Fore.RESET)
        elif level.lower() == '':
            logging.info(log_message)
            print(Fore.WHITE + log_message + Fore.RESET)
        elif level.lower() == 'debug':
            logging.debug(log_message)
            print(Fore.BLUE + log_message + Fore.RESET)
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


def main(method_sel=None, max_darts=None, dart_step=None, duration=None):
    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size

    wb, sheet = create_excel_sheet()

    start_time = time.time()
    num_iterations = 0
    num_darts_per_process = dart_step if dart_step else 2500
    data = []

    while True:
        pi_estimate_send_receive = None
        pi_estimate_reduce = None

        method_start_time = time.time()

        if method_sel == "both":
            pi_estimate_send_receive = estimate_pi_send_receive(num_darts_per_process, comm)
            send_receive_time = time.time() - method_start_time

            method_start_time = time.time()

            pi_estimate_reduce = estimate_pi_reduce(num_darts_per_process, comm)
            reduce_time = time.time() - method_start_time
        elif method_sel == "send_receive":
            pi_estimate_send_receive = estimate_pi_send_receive(num_darts_per_process, comm)
            send_receive_time = time.time() - method_start_time
        elif method_sel == "reduce":
            pi_estimate_reduce = estimate_pi_reduce(num_darts_per_process, comm)
            reduce_time = time.time() - method_start_time

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

        if duration and time.time() - start_time >= duration:
            break

    if rank == 0:
        write_to_excel(sheet, data)

        timestamp = generate_timestamp()
        filename_excel = f"excel/pi_estimation_data_{timestamp}.xlsx"
        filename_pi_estimate_send_receive = f"././png/estimation/pi_estimate_plot_send_receive_{timestamp}.png"
        filename_pi_estimate_reduce = f"././png/estimation/pi_estimate_plot_reduce_{timestamp}.png"
        filename_pi_difference_send_receive = f"././png/pi_difference/pi_difference_plot_send_receive_{timestamp}.png"
        filename_pi_difference_reduce = f"././png/pi_difference/pi_difference_plot_reduce_{timestamp}.png"
        filename_time_taken_send_receive = f"././png/runtime/time_taken_plot_send_receive_{timestamp}.png"
        filename_time_taken_reduce = f"././png/runtime/time_taken_plot_reduce_{timestamp}.png"

        save_excel(wb, filename_excel)
        plot_pi_estimate(data, filename_pi_estimate_send_receive, filename_pi_estimate_reduce)
        plot_pi_difference(data, filename_pi_difference_send_receive, filename_pi_difference_reduce)
        plot_time_taken(data, filename_time_taken_send_receive, filename_time_taken_reduce)

        os.system(f"libreoffice --calc {filename_excel}")
        sys.exit()


if __name__ == "__main__":
    logger("Program has been started")
    print(sys.argv)

    if len(sys.argv) < 2:
        logger("FATAL ERROR; wrong usage: python3 main.py [method] [max_darts] [dart_step] [duration]")
        print("[method] should be 'send_receive', 'reduce', or 'both'")
        logger("[method] should be 'send_receive', 'reduce', or 'both'", level='error')
        sys.exit(1)

    method = sys.argv[1] if len(sys.argv) > 1 else "both"
    max_darts = int(sys.argv[2]) if len(sys.argv) > 2 else None
    dart_step = int(sys.argv[3]) if len(sys.argv) > 3 else 2500
    duration = int(sys.argv[4]) if len(sys.argv) > 4 else 10

    logger(f"Method is going to be used: {method}", level="debug")
    logger(f"Amounts are going to be used: {max_darts}", level="debug")
    logger(f"The amount of darts is getting in steps: {dart_step}", level="debug")
    logger(f"The duration of the program is going to be: {duration} seconds", level="debug")

    check_folder()
    main(method, max_darts, dart_step, duration)
