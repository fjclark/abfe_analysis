"""Extract run times for all output"""

from .dir_paths import get_dir_paths
from ..save_data import mkdir_if_required

import glob 
import numpy as np

def get_av_speed(output_dir = "."):
    """Get the average simulation time from output files.

    Args:
        output_dir (str): Directory in which to check the output files.

    Returns:
        float: average simulation time, in ns / h
    """
    timestep = None
    ncycles = None
    nmoves = None
    total_time = []
    for fname in glob.glob(f"{output_dir}/somd-array-gpu*"):
        with open(fname, "rt") as f:
            for l in f.readlines():
                if l.startswith("timestep =="):
                    timestep = float(l.split()[-2]) # ps
                if l.startswith("ncycles =="):
                    ncycles = float(l.split()[-1])
                if l.startswith("nmoves =="):
                    nmoves = float(l.split()[-1])
                if l.startswith("Simulation took"):
                    total_time.append(float(l.split()[-2])) # s
    
    simtime = timestep * ncycles * nmoves # ps
    simtime /= 1000 # ns

    total_time = np.array(total_time)
    av_time = total_time.mean() # s
    av_time /= 60**2 # hours

    speed = simtime / av_time # ns /hour

    return speed


def get_av_speeds(run_nos = [1,2,3,4,5], leg = "bound"):
    """Calculate average simulation speed for all runs.

    Args:
        run_nos (list, optional): The run numbers over which to average. Defaults to [1,2,3,4,5].
        leg (str, optional): "free" or "bound". Defaults to "bound".
    """

    dir_paths = get_dir_paths(run_nos, leg)

    # Average over output directories
    av_speeds = {}
    for run_name in dir_paths:
        av_speeds[run_name] = {}
        for stage in dir_paths[run_name]:
            print(f"Calcuating Average Speed for {run_name} {stage}")
            av_speeds[run_name][stage] = get_av_speed(dir_paths[run_name][stage]["output"])

    # Now average over runs
    first_run_name = list(av_speeds.keys())[0] # Assume stages the same between runs
    av_speeds_stages = {k:{"values":0, "std":0} for k in av_speeds[first_run_name] if k != "test_restrain"}
    for stage in av_speeds_stages:
        av_speeds_stages[stage]["values"] = np.mean([av_speeds[run_name][stage] for run_name in av_speeds])
        av_speeds_stages[stage]["std"] = np.std([av_speeds[run_name][stage] for run_name in av_speeds])

    # Overall average speed
    av_speed = np.mean([av_speeds_stages[stage]["values"] for stage in av_speeds_stages])
    av_speed_std = np.std([av_speeds_stages[stage]["values"] for stage in av_speeds_stages])

    out_str = "######################################################################### \n"
    out_str += f"Average speed: {av_speed:.2f} +/- {av_speed_std:.2f} ns / hour \n"
    out_str += f"Average speed: {av_speed * 24:.2f} +/- {av_speed_std * 24:.2f} ns / day \n"
    out_str += "######################################################################### \n"
    out_str += "Per stage timings: \n"
    for stage in av_speeds_stages:
        out_str += f"{stage}: {av_speeds_stages[stage]['values']:.2f} +/- {av_speeds_stages[stage]['std']:.2f} ns / hour \n"
        out_str += f"{stage}: {av_speeds_stages[stage]['values'] * 24:.2f} +/- {av_speeds_stages[stage]['std'] * 24:.2f} ns / day \n"
    print(out_str)
    
    mkdir_if_required("analysis/simulation_speed")
    with open("analysis/simulation_speed/sim_times.dat", "wt") as f:
        f.write(out_str)