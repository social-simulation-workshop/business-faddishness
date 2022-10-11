import argparse
import multiprocessing
import numpy as np
import os
import sys

from args import ArgsConfig
from utils import Simulation
from plot import PlotLinesHandler

def exp1_single_trail(trail_idx, args, pop_list, turn_list):
    print("trail {} started".format(trail_idx))
    demo = Simulation(args, args.random_seed + trail_idx)
    demo.simulate()
    pop_list.append(demo.get_mean_popularity())
    turn_list.append(demo.get_turnover())
    print(pop_list[-1], turn_list[-1])

    args_tmp = argsconfig.get_args()
    fn_suffix = "_".join(["randSeed_{}_n_iter_{}".format(args_tmp.random_seed + trail_idx, args_tmp.n_iter)])
    plot_handler = PlotLinesHandler(xlabel="Iteration",
                                    ylabel="Popularity",
                                    title=None,
                                    fn="exp1",
                                    x_lim=[98, 202], y_lim=[-2, 60], use_ylim=True,
                                    x_tick=[100, 200, 25], y_tick=[0, 60, 20],
                                    figure_ratio=748/1006)
    innos_pop = demo.get_leading_inno_popularity()
    for inno_pop in innos_pop:
        plot_handler.plot_line(inno_pop, data_log_v=1, linewidth=2, x_shift=101)
    plot_handler.save_fig(fn_suffix=fn_suffix)


def single_paramset(args, indep_var, pop_list, turn_list, n_trail=10):
    tmp_pop_list, tmp_turn_list = list(), list()
    for trail_idx in range(n_trail):
        demo = Simulation(args, args.random_seed + trail_idx)
        demo.simulate()
        tmp_pop_list.append(demo.get_mean_popularity())
        tmp_turn_list.append(demo.get_turnover())
    pop_list.append((indep_var, np.mean(tmp_pop_list)))
    turn_list.append((indep_var, np.mean(tmp_turn_list)))

def sort_list(l) -> list:
    return [val for (indep_var, val) in sorted(l, key=lambda x: x[0])]


if __name__ == "__main__":
    argsconfig = ArgsConfig()
    args = argsconfig.get_args()

    if args.exp == 1:
        pop_manager = multiprocessing.Manager()
        pop_list = pop_manager.list()
        turn_manager = multiprocessing.Manager()
        turn_list = turn_manager.list()
        
        args_list = []
        for trail_idx in range(args.n_trail):
            args = argsconfig.get_args()
            args_list.append([trail_idx, args, pop_list, turn_list])
        
        n_cpus = multiprocessing.cpu_count()
        print("cpu count: {}".format(n_cpus))
        pool = multiprocessing.Pool(n_cpus+2)
        pool.starmap(exp1_single_trail, args_list)
        
        sysout = sys.stdout
        args = argsconfig.get_args()
        fn = "_".join(["exp1_randSeed_{}_n_iter_{}_n_trail_{}.txt".format(
            args.random_seed, args.n_iter, args.n_trail)])
        f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), fn), 'w')
        sys.stdout = f
        print(args)
        print("pop_mean, pop_std = ({}, {})".format(np.mean(pop_list), np.std(pop_list)))
        print("turn_mean, turn_std = ({}, {})".format(np.mean(turn_list), np.std(turn_list)))
        f.close()
        sys.stdout = sysout
        
    
    if args.exp == 2:
        # skepticism
        pop_skep_manager = multiprocessing.Manager()
        pop_skep_list = pop_skep_manager.list()
        turn_skep_manager = multiprocessing.Manager()
        turn_skep_list = turn_skep_manager.list()

        args_skep_list = []
        for s in range(0, 101, 10):
            args = argsconfig.get_args()
            args.const_S = s / 100
            args_skep_list.append([args, s, pop_skep_list, turn_skep_list])
        
        n_cpus = multiprocessing.cpu_count()
        print("cpu count: {}".format(n_cpus))
        pool = multiprocessing.Pool(n_cpus+2)
        pool.starmap(single_paramset, args_skep_list)

        pop_skep_list = sort_list(pop_skep_list)
        turn_skep_list = sort_list(turn_skep_list) 

        # inert
        pop_inert_manager = multiprocessing.Manager()
        pop_inert_list = pop_inert_manager.list()
        turn_inert_manager = multiprocessing.Manager()
        turn_inert_list = turn_inert_manager.list()

        args_inert_list = []
        for i in range(0, 101, 10):
            args = argsconfig.get_args()
            args.const_I = i / 100
            args_inert_list.append([args, i, pop_inert_list, turn_inert_list])

        n_cpus = multiprocessing.cpu_count()
        print("cpu count: {}".format(n_cpus))
        pool = multiprocessing.Pool(n_cpus+2)
        pool.starmap(single_paramset, args_inert_list)

        pop_inert_list = sort_list(pop_inert_list)
        turn_inert_list = sort_list(turn_inert_list)

        # plot
        args_tmp = argsconfig.get_args()
        fn_suffix = "_".join(["randSeed_{}_n_iter_{}".format(args_tmp.random_seed, args_tmp.n_iter)])
        plot_handler = PlotLinesHandler(xlabel="Skepticism and Inertia",
                                        ylabel="",
                                        title=None,
                                        fn="exp2",
                                        x_lim=[-2, 102], y_lim=[-2, 102], use_ylim=True,
                                        x_tick=[0, 100, 10], y_tick=[0, 100, 10],
                                        figure_ratio=748/1006)
        plot_handler.plot_line(np.array(pop_skep_list), data_log_v=10, linewidth=2, format="k-")
        plot_handler.plot_line(np.array(turn_skep_list), data_log_v=10, linewidth=2, format="k--")
        plot_handler.plot_line(np.array(pop_inert_list), data_log_v=10, linewidth=2, format="k:")
        plot_handler.plot_line(np.array(turn_inert_list), data_log_v=10, linewidth=2, format="k-.")
        legend = ["Popularity by Skepticism",
                  "Turnover by Skepticism",
                  "Popularity by Inertia",
                  "Turnover by Inertia"]
        plot_handler.save_fig(legend, fn_suffix=fn_suffix)
    

    if args.exp == 3:
        # beta
        pop_beta_manager = multiprocessing.Manager()
        pop_beta_list = pop_beta_manager.list()
        turn_beta_manager = multiprocessing.Manager()
        turn_beta_list = turn_beta_manager.list()
        
        args_beta_list = []
        for b in range(0, 101, 10):
            args = argsconfig.get_args()
            args.beta = b
            args.is_const_IS = False
            args_beta_list.append([args, b, pop_beta_list, turn_beta_list])

        n_cpus = multiprocessing.cpu_count()
        print("cpu count: {}".format(n_cpus))
        pool = multiprocessing.Pool(n_cpus+2)
        pool.starmap(single_paramset, args_beta_list)

        pop_beta_list = sort_list(pop_beta_list)
        turn_beta_list = sort_list(turn_beta_list)
     
        # plot
        args_tmp = argsconfig.get_args()
        fn_suffix = "_".join(["randSeed_{}_n_iter_{}".format(args_tmp.random_seed, args_tmp.n_iter)])
        plot_handler = PlotLinesHandler(xlabel="Value of Innovation",
                                        ylabel="",
                                        title=None,
                                        fn="exp3",
                                        x_lim=[-2, 102], y_lim=[-2, 102], use_ylim=True,
                                        x_tick=[0, 100, 10], y_tick=[0, 100, 10],
                                        figure_ratio=748/1006)
        plot_handler.plot_line(np.array(pop_beta_list), data_log_v=10, linewidth=2, format="k-")
        plot_handler.plot_line(np.array(turn_beta_list), data_log_v=10, linewidth=2, format="k--")
        legend = ["Popularity",
                  "Turnover"]
        plot_handler.save_fig(legend, fn_suffix=fn_suffix)