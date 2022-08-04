import os
import psutil
import numpy as np

from multiprocessing import Process


def run_proc(cmd):
    os.system(cmd)

SPLIT = 2

cpus = psutil.Process().cpu_affinity()
split = [s.tolist() for s in np.array_split(cpus, SPLIT)]
strings = []
for cpu_list in split:
    str_cpu_list = [str(num) for num in cpu_list]
    strings.append(",".join(str_cpu_list))
    

command = "taskset --cpu-list {} video2numpy urls{}.txt --dest arrs/ --take-every-nth 25 --workers 6"

procs = []
for id_, cpus in enumerate(strings):
    cmd = command.format(cpus, id_+1)
    procs.append(Process(args=(cmd,), target=run_proc))


for p in procs:
    p.start()

for p in procs:
    p.join()
