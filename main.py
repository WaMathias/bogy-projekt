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

    total_darts_inside_circle = comm.reduce(darts_inside_circle, op=MPI.SUM, root=0)
    total_darts_per_process = comm.reduce(num_darts_per_process, op=MPI.SUM, root=0)

    if comm.rank == 0:
        total_darts = total_darts_per_process * comm.size
        pi_estimate = 4 * total_darts_inside_circle / total_darts
        return pi_estimate
    else:
        return None


def main():
    comm = MPI.COMM_WORLD
    rank = comm.rank

    num_darts_per_process = 25000

    start_time = time.time()
    pi_estimate = estimate_pi(num_darts_per_process, comm)
    end_time = time.time()

    print("Output is from main.py")
    print("Estimation of pi with", num_darts_per_process * comm.size, "darts (", num_darts_per_process,
          "per process):", pi_estimate, "Took time:", end_time - start_time, "seconds", "on rank: ", rank)




if __name__ == "__main__":
    main()
