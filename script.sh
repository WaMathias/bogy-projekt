#!/bin/bash

echo "This script will execute the Python script with custom parameters."
echo "Please provide the following inputs:"

echo "How many slots do you want to use: "
read slots
echo -e "\e[1;34m$slots are going to be used\e[0m"

echo "Enter method (send_receive, reduce, or both): "
read method
echo -e "\e[1;34m$method method(s) is/are going to be used\e[0m"

echo "Enter the maximum number of darts (or press Enter to skip): "
read max_darts

echo "Enter the dart step (or press Enter to skip): "
read dart_step

echo "Enter the duration (or press Enter to skip): "
read duration

echo "Do you want to enable debug mode (True/False):"
read debug_mode
echo -e "\e[1;34mDebug Mode: $debug_mode\e[0m"

export DEBUG_MODE=$debug_mode

echo "The following command is going to be executed: mpirun -n $slots --hostfile hostfile --map-by :OVERSUBSCRIBE python3 ./src/main.py $method $max_darts $dart_step $duration"
mpirun -n $slots --hostfile hostfile --map-by :OVERSUBSCRIBE python3 ./src/main.py $method $max_darts $dart_step $duration
