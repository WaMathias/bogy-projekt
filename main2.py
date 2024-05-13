from mpi4py import MPI
import random
import time
import openpyxl
import datetime
import os


def throw_darts(num_darts):
    darts_inside_circle = sum(
        1 for _ in range(num_darts) if random.uniform(-1, 1) ** 2 + random.uniform(-1, 1) ** 2 <= 1)
    return darts_inside_circle


def estimate_pi(num_darts_per_process, comm):
    darts_inside_circle = throw_darts(num_darts_per_process)

    if comm.rank == 0:
        total_darts_inside_circle, total_darts_per_process = gather_results(darts_inside_circle, num_darts_per_process,
                                                                            comm)
        total_darts = total_darts_per_process
        pi_estimate = 4 * total_darts_inside_circle / total_darts
        return pi_estimate, total_darts_per_process
    else:
        send_results(darts_inside_circle, num_darts_per_process, comm)
        return 0, num_darts_per_process


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


def write_to_excel(sheet, num_iterations, pi_estimate, time_taken, num_darts_per_process, size):
    sheet.append([num_iterations, pi_estimate, time_taken, num_darts_per_process * size])


def main():
    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Pi Estimation Data"
    sheet.append(["Iteration", "Pi Estimate", "Time Taken (s)", "Num Darts"])

    start_time = time.time()
    num_iterations = 0
    num_darts_per_process = 2500

    while time.time() - start_time < 10:
        iteration_start_time = time.time()
        pi_estimate, _ = estimate_pi(num_darts_per_process, comm)
        iteration_end_time = time.time()
        time_taken = iteration_end_time - iteration_start_time

        if rank == 0:
            write_to_excel(sheet, num_iterations, pi_estimate, time_taken, num_darts_per_process, size)

        num_iterations += 1
        num_darts_per_process += 2500

    if rank == 0:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"excel/pi_estimation_data_{timestamp}.xlsx"
        if os.path.exists(filename):
            os.remove(filename)
        wb.save(filename)


if __name__ == "__main__":
    print(datetime.datetime.now())
    main()
