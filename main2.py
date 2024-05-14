from mpi4py import MPI
import random
import time
import openpyxl
import datetime
import os
import matplotlib.pyplot as plt
import sys

os.environ["XDG_SESSION_TYPE"] = "xcb"


def throw_darts(num_darts):
    darts_inside_circle = sum(
        1 for _ in range(num_darts) if random.uniform(-1, 1) ** 2 + random.uniform(-1, 1) ** 2 <= 1)
    return darts_inside_circle


def estimate_pi_send_receive(num_darts_per_process, comm):
    darts_inside_circle = throw_darts(num_darts_per_process)

    if comm.rank == 0:
        total_darts_inside_circle, total_darts_per_process = gather_results(darts_inside_circle, num_darts_per_process,
                                                                            comm)
        total_darts = total_darts_per_process * comm.size
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
        total_darts = total_darts_per_process * comm.size
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


def plot_pi_estimate(data, filename):
    num_darts = [row[3] for row in data]
    pi_estimates = [row[1] for row in data]

    plt.figure(figsize=(10, 5))
    plt.plot(num_darts, pi_estimates, marker='o', label='Pi Estimate')
    plt.xlabel('Number of Darts')
    plt.ylabel('Pi Estimate')
    plt.title('Estimation of Pi')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()


def plot_pi_difference(data, filename):
    num_darts = [row[3] for row in data]
    pi_estimates = [row[1] for row in data]
    pi_difference = [
        abs(3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651328230664709384460955058223172535940812848111745028410270193852110555964462294895493038196 - pi_estimate)
        for pi_estimate in pi_estimates]

    plt.figure(figsize=(10, 5))
    plt.plot(num_darts, pi_difference, marker='o', label='Pi Difference')
    plt.xlabel('Number of Darts')
    plt.ylabel('Pi Difference')
    plt.title('Difference from Pi Estimate')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()


def plot_time_taken(data, filename):
    num_darts = [row[3] for row in data]
    time_taken = [row[2] for row in data]

    plt.figure(figsize=(10, 5))
    plt.plot(num_darts, time_taken, marker='o', label='Time Taken (s)')
    plt.xlabel('Number of Darts')
    plt.ylabel('Time Taken (s)')
    plt.title('Time Taken for Estimation')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()


def create_excel_sheet():
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Pi Estimation Data"
    sheet.append(["Iteration", "Pi Estimate", "Time Taken (s)", "Num Darts"])
    return wb, sheet


def save_excel(wb, filename):
    if os.path.exists(filename):
        os.remove(filename)
    wb.save(filename)


def generate_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def main(method):
    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size

    wb, sheet = create_excel_sheet()

    start_time = time.time()
    num_iterations = 0
    num_darts_per_process = 2500
    data = []

    while time.time() - start_time < 10:
        iteration_start_time = time.time()
        if method == "send_receive":
            pi_estimate = estimate_pi_send_receive(num_darts_per_process, comm)
        elif method == "reduce":
            pi_estimate = estimate_pi_reduce(num_darts_per_process, comm)
        else:
            raise ValueError("Invalid method. Use 'send_receive' or 'reduce'.")

        iteration_end_time = time.time()
        time_taken = iteration_end_time - iteration_start_time

        if rank == 0:
            data.append([num_iterations, pi_estimate, time_taken, num_darts_per_process * size])

        num_iterations += 1
        num_darts_per_process += 2500

    if rank == 0:
        write_to_excel(sheet, data)

        timestamp = generate_timestamp()
        filename_excel = f"excel/pi_estimation_data_{timestamp}.xlsx"
        filename_pi_estimate = f"png/estimation/pi_estimate_plot_{timestamp}.png"
        filename_pi_difference = f"png/pi_difference/pi_difference_plot_{timestamp}.png"
        filename_time_taken = f"png/runtime/time_taken_plot_{timestamp}.png"

        save_excel(wb, filename_excel)
        plot_pi_estimate(data, filename_pi_estimate)
        plot_pi_difference(data, filename_pi_difference)
        plot_time_taken(data, filename_time_taken)

        os.system(f"libreoffice --calc {filename_excel}")

    wb.close()


if __name__ == "__main__":
    print(generate_timestamp())
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <method>")
        print("<method> should be either 'send_receive' or 'reduce'.")
        sys.exit(1)

    method = sys.argv[1]
    main(method)
