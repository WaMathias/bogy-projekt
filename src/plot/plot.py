import numpy as np
import matplotlib.pyplot as plt
from src.utils.utils import logger

def plot_pi_estimate(data, filename, method_sel):
    num_darts = np.array([row[3] for row in data], dtype=float)
    pi_estimates_send_receive = np.array([row[1] if row[5] == "send_receive" else None for row in data], dtype=float)
    pi_estimates_reduce = np.array([row[1] if row[5] == "reduce" else None for row in data], dtype=float)

    valid_send_receive = ~np.isnan(pi_estimates_send_receive)
    valid_reduce = ~np.isnan(pi_estimates_reduce)

    num_darts_interp = np.linspace(num_darts.min(), num_darts.max(), num=500)
    if method_sel in ["both", "send_receive"]:
        pi_estimates_send_receive_interp = np.interp(num_darts_interp, num_darts[valid_send_receive],
                                                     pi_estimates_send_receive[valid_send_receive])
    if method_sel in ["both", "reduce"]:
        pi_estimates_reduce_interp = np.interp(num_darts_interp, num_darts[valid_reduce], pi_estimates_reduce[valid_reduce])

    plt.figure(figsize=(10, 5))
    if method_sel in ["both", "send_receive"]:
        plt.plot(num_darts_interp, pi_estimates_send_receive_interp, color='blue', linestyle='-',
                 label='Pi Estimate (Send/Receive)')
    if method_sel in ["both", "reduce"]:
        plt.plot(num_darts_interp, pi_estimates_reduce_interp, color='red', linestyle='-', label='Pi Estimate (Reduce)')
    plt.xlabel('Number of Darts')
    plt.ylabel('Pi Estimate')
    plt.title('Estimation of Pi')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

def plot_pi_difference(data, filename, method_sel):
    num_darts = np.array([row[3] for row in data], dtype=float)
    pi_estimates_send_receive = np.array([row[1] if row[5] == "send_receive" else None for row in data], dtype=float)
    pi_estimates_reduce = np.array([row[1] if row[5] == "reduce" else None for row in data], dtype=float)

    valid_send_receive = ~np.isnan(pi_estimates_send_receive)
    valid_reduce = ~np.isnan(pi_estimates_reduce)

    pi_difference_send_receive = np.abs(np.pi - pi_estimates_send_receive)
    pi_difference_reduce = np.abs(np.pi - pi_estimates_reduce)

    num_darts_interp = np.linspace(num_darts.min(), num_darts.max(), num=500)
    if method_sel in ["both", "send_receive"]:
        pi_difference_send_receive_interp = np.interp(num_darts_interp, num_darts[valid_send_receive],
                                                      pi_difference_send_receive[valid_send_receive])
    if method_sel in ["both", "reduce"]:
        pi_difference_reduce_interp = np.interp(num_darts_interp, num_darts[valid_reduce], pi_difference_reduce[valid_reduce])

    plt.figure(figsize=(10, 5))
    if method_sel in ["both", "send_receive"]:
        plt.plot(num_darts_interp, pi_difference_send_receive_interp, color='blue', linestyle='-',
                 label='Pi Difference (Send/Receive)')
    if method_sel in ["both", "reduce"]:
        plt.plot(num_darts_interp, pi_difference_reduce_interp, color='red', linestyle='-', label='Pi Difference (Reduce)')
    plt.xlabel('Number of Darts')
    plt.ylabel('Absolute Pi Difference')
    plt.title('Difference from Pi Estimate')
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

def plot_time_taken(data, filename, method_sel):
    try:
        num_darts = np.array([row[3] for row in data], dtype=float)
        time_taken_send_receive = np.array([row[2] if row[5] == "send_receive" else None for row in data], dtype=float)
        time_taken_reduce = np.array([row[2] if row[5] == "reduce" else None for row in data], dtype=float)

        valid_send_receive = ~np.isnan(time_taken_send_receive)
        valid_reduce = ~np.isnan(time_taken_reduce)

        num_darts_interp = np.linspace(num_darts.min(), num_darts.max(), num=500)
        if method_sel in ["both", "send_receive"]:
            time_taken_send_receive_interp = np.interp(num_darts_interp, num_darts[valid_send_receive],
                                                       time_taken_send_receive[valid_send_receive])
        if method_sel in ["both", "reduce"]:
            time_taken_reduce_interp = np.interp(num_darts_interp, num_darts[valid_reduce], time_taken_reduce[valid_reduce])

        plt.figure(figsize=(10, 5))
        if method_sel in ["both", "send_receive"]:
            plt.plot(num_darts_interp, time_taken_send_receive_interp, color='blue', linestyle='-',
                     label='Time Taken (Send/Receive) (s)')
        if method_sel in ["both", "reduce"]:
            plt.plot(num_darts_interp, time_taken_reduce_interp, color='red', linestyle='-',
                     label='Time Taken (Reduce) (s)')
        plt.xlabel('Number of Darts')
        plt.ylabel('Time Taken (s)')
        plt.title('Time Taken for Estimation')
        plt.legend()
        plt.grid(True)
        plt.savefig(filename)
        plt.close()
    except Exception as e:
        logger(f"Error saving time taken plot: {e}", level='error')
