# mpi_echo

```shell
# linux
echo 0 | sudo tee /proc/sys/kernel/yama/ptrace_scope
mpiexec --oversubscribe -n 10 python3 mpi_echo.py
mpirun --oversubscribe -n 10 python3 mpi_echo.py

# windows
mpiexec -n 10 python mpi_echo.py
```

## modified echo algorithm

* the father knows his children
* nodes exchange messages in the Spanning Tree to calculate hops and distance from root for each node and the height of the Spanning Tree 
