# Run complete set of default analyses 
import os

from .get_data import convergence_data, convergence_data_free # TODO: Make this a single module
from .get_data import get_results
from .comparitive_analysis import compare_conv
from .comparitive_analysis import compare_pmfs
from .comparitive_analysis import overlap
from .comparitive_analysis import indiv_pmf_conv
from .comparitive_analysis import dh_dlam
from .comparitive_analysis import boresch_dof
from .comparitive_analysis import rmsd
from .comparitive_analysis import av_waters

def run_analysis_bound(leg = "bound", run_nos=[1,2,3,4,5], calc_type="Boresch", timestep=4, nrg_freq=100,
percent_traj_dict = {"restrain":83.33333333, "discharge":83.33333333, "vanish":62.5}):

    print("###############################################################################################")
    print(f"Analysing the {leg} leg for runs: {run_nos} and calculation type = {calc_type}")
    print("Ensure you are in the base directory and the development version of biosimspace is activated")

    # Only calculate convergence data if this has not been done already
    if not os.path.isfile("analysis/convergence_data.pickle"):
        convergence_data.get_convergence_dict()

    get_results.write_results(leg, run_nos)
    compare_conv.plot_stages_conv("analysis/convergence_data.pickle", leg)
    compare_conv.plot_overall_conv("analysis/convergence_data.pickle", leg)
    compare_pmfs.plot_all_pmfs(run_nos, leg)
    overlap.plot_overlap_mats(leg, run_nos)
    indiv_pmf_conv.plot_pmfs_conv(leg, run_nos)
    dh_dlam.plot_grads(leg, run_nos, percent_traj_dict, timestep, nrg_freq)

    # Plot average waters within 8 A of CG2 in VAL and N in PRT on opposite sides of binding pocket.
    # This gives reasonable coverage of the pocket while excluding most waters outside.
    av_waters.plot_av_waters(leg, run_nos, stage="vanish", 
    percent_traj=percent_traj_dict["vanish"], index=1637,length=8, index2=34, length2=8)

    # Plot Boresch DOF for restrain lam = 0, restrain lam = 1, discharge lam = 1 and vanish lam =1
    plot_winds = [("restrain",0.000),("restrain",1.000),("discharge",1.000),("vanish",1.000)]
    selected_dof_list = ["r","thetaA","thetaB","phiA","phiB","phiC"]
    for wind in plot_winds:
        boresch_dof.plot_dof_hists(leg, run_nos, wind[0], wind[1], percent_traj_dict[wind[0]], selected_dof_list)
        boresch_dof.plot_dof_vals(leg, run_nos, wind[0], wind[1], percent_traj_dict[wind[0]], selected_dof_list)

    # RMSD for protein
    rmsd.plot_rmsds(leg, run_nos, percent_traj_dict, "protein")
    # RMSD for syn-anti interconversion of ligand (ignore phenol group which is rotatable and adds noise)
    rmsd.plot_rmsds(leg, run_nos, percent_traj_dict, "resname LIG and (not name H* OAA CAS CAD CAF CAG CAP CAE)")


    print("###############################################################################################")
    print("Analysis of bound leg successfully completed!")


#TODO: Combine these into one function

def run_analysis_free(leg = "free", run_nos=[1,2,3,4,5], timestep=4, nrg_freq=100,
percent_traj_dict = {"discharge":83.33333333, "vanish":83.3333333}):

    print("###############################################################################################")
    print(f"Analysing the {leg} leg for runs: {run_nos}")
    print("Ensure you are in the base directory and the development version of biosimspace is activated")
    
    # Only calculate convergence data if this has not been done already
    if not os.path.isfile("analysis/convergence_data.pickle"):
        convergence_data_free.get_convergence_dict()
    
    get_results.write_results(leg, run_nos)
    compare_conv.plot_stages_conv("analysis/convergence_data.pickle", leg)
    compare_conv.plot_overall_conv("analysis/convergence_data.pickle", leg)
    compare_pmfs.plot_all_pmfs(run_nos, leg)
    overlap.plot_overlap_mats(leg, run_nos)
    indiv_pmf_conv.plot_pmfs_conv(leg, run_nos)
    dh_dlam.plot_grads(leg, run_nos, percent_traj_dict, timestep, nrg_freq)

    # RMSD for syn-anti interconversion of ligand (ignore phenol group which is rotatable and adds noise)
    rmsd.plot_rmsds(leg, run_nos, percent_traj_dict, "resname LIG and (not name H* OAA CAS CAD CAF CAG CAP CAE)")

    print("###############################################################################################")
    print("Analysis of free leg successfully completed!")