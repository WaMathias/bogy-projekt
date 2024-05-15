import numpy as np
from mpi4py import MPI
import random


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


def throw_darts(num_darts):
    darts_inside_circle = sum(
        1 for _ in range(num_darts) if random.uniform(-1, 1) ** 2 + random.uniform(-1, 1) ** 2 <= 1)
    return darts_inside_circle
