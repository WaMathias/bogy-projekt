from mpi4py import MPI
import random
import time


def throw_darts(num_darts):
    darts_inside_circle = 0
    for _ in range(num_darts):
        x = random.uniform(-1, 1)
        y = random.uniform(-1, 1)
        if x ** 2 + y ** 2 <= 1:
            darts_inside_circle += 1
    return darts_inside_circle


def estimate_pi(num_darts_per_process, comm):
    darts_inside_circle = throw_darts(num_darts_per_process)

    if comm.rank == 0:
        total_darts_inside_circle = darts_inside_circle
        total_darts_per_process = num_darts_per_process
        for i in range(1, comm.size):
            received_darts_inside_circle = comm.recv(source=i)
            received_darts_per_process = comm.recv(source=i)
            total_darts_inside_circle += received_darts_inside_circle
            total_darts_per_process += received_darts_per_process
    else:
        comm.send(darts_inside_circle, dest=0)
        comm.send(num_darts_per_process, dest=0)

    if comm.rank == 0:
        total_darts = total_darts_per_process * comm.size
        pi_estimate = 4 * total_darts_inside_circle / total_darts
        return pi_estimate
    else:
        return None


def main():
    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size

    num_darts_per_process = 25000  # darts per process

    start_time = time.time()
    pi_estimate = estimate_pi(num_darts_per_process, comm)
    end_time = time.time()

    if rank == 0:
        print("Estimation of pi with", num_darts_per_process * comm.size, "darts (", num_darts_per_process,
              "per process):", pi_estimate, "Took time:", end_time - start_time)


if __name__ == "__main__":
    main()
