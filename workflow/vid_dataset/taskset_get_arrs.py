import os
import psutil
import tempfile
import numpy as np

from multiprocessing import Process


def run_proc(cmd):
    os.system(cmd)

SPLIT = 3
URLS = "urls.txt" # txt file with urls to download and process as lines
# Split up URLS:
with open(URLS, "r") as f:
    lines = f.read().splitlines()

split_lines = [s.tolist() for s in np.array_split(lines, SPLIT)]

with tempfile.TemporaryDirectory() as tmpdirname:
    url_pths = []
    for i, ls in enumerate(split_lines):
        url_pth = os.path.join(tmpdirname, f"urls{i}.txt") 
        with open(url_pth, "w") as f:
            for line in ls:
                f.write(line + '\n')
        url_pths.append(url_pth)

    cpus = psutil.Process().cpu_affinity()
    split = [s.tolist() for s in np.array_split(cpus, SPLIT)]
    strings = []
    for cpu_list in split:
        str_cpu_list = [str(num) for num in cpu_list]
        strings.append(",".join(str_cpu_list))
        

    command = "taskset --cpu-list {} video2numpy {} --dest arrs/ --take-every-nth 25 --workers {}"

    procs = []
    for i, cpus in enumerate(strings):
        cmd = command.format(cpus, url_pths[i], len(cpus.split(",")))
        print(cmd)
        procs.append(Process(args=(cmd,), target=run_proc))

    print("STARTING READING...")

    for p in procs:
        p.start()

    for p in procs:
        p.join()

    print("DONE READING")
