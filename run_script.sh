# mpirun -n 4 --hostfile hostfile --map-by :OVERSUBSCRIBE python3 main.py

mpirun -n 2 --hostfile hostfile --map-by :OVERSUBSCRIBE python3 main2.py reduce

# mpirun -n 2 --map-by :OVERSUBSCRIBE python3 main2.py

# mpirun -n 1 --hostfile hostfile --map-by :OVERSUBSCRIBE python3 main3.py
