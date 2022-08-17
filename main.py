import argparse
import multiprocessing
import numpy as np
import os
import sys

from args import ArgsConfig
from utils import Simulation
from plot import PlotLinesHandler

EXP = 1
N_TRAIL = 1

if __name__ == "__main__":
    argsconfig = ArgsConfig()

    if EXP == 1 or EXP == 0:
        args_list = []
        pop_list = []
        turn_list = []
        for _ in range(N_TRAIL):
            args = argsconfig.get_args()
            args_list.append(args)
        for args_idx, args in enumerate(args_list):
            demo = Simulation(args, args.random_seed + args_idx)
            demo.simulate()
            pop_list.append(demo.get_mean_popularity())
            turn_list.append(demo.get_turnover())
            print(pop_list[-1], turn_list[-1])

            args_tmp = argsconfig.get_args()
            fn_suffix = "_".join(["randSeed_{}_n_iter_{}".format(args_tmp.random_seed + args_idx, args_tmp.n_iter)])
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
        
        sysout = sys.stdout
        fn = "_".join(["exp1_randSeed_{}_n_iter_{}".format(args_list[0].random_seed, args_list[0].n_iter)])
        f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), fn), 'w')
        sys.stdout = f
        print(args_list[0])
        print("pop_mean, pop_std = ({}, {})".format(np.mean(pop_list), np.std(pop_list)))
        print("turn_mean, turn_std = ({}, {})".format(np.mean(turn_list), np.std(turn_list)))
        f.close()
        sys.stdout = sysout
        
    
    if EXP == 2 or EXP == 0:
        args_skep_list = []
        pop_skep_list = []
        turn_skep_list = []
        for s in range(0, 101, 10):
            args = argsconfig.get_args()
            args.const_S = s
            args_skep_list.append(args)
        for args_idx, args in enumerate(args_skep_list):
            demo = Simulation(args, args.random_seed + args_idx)
            demo.simulate()
            pop_skep_list.append(demo.get_mean_popularity())
            turn_skep_list.append(demo.get_turnover())
            print(pop_skep_list[-1], turn_skep_list[-1])
        
        args_inert_list = []
        pop_inert_list = []
        turn_inert_list = []
        for i in range(0, 101, 10):
            args = argsconfig.get_args()
            args.const_I = i
            args_inert_list.append(args)
        for args_idx, args in enumerate(args_inert_list):
            demo = Simulation(args, args.random_seed + args_idx)
            demo.simulate()
            pop_inert_list.append(demo.get_mean_popularity())
            turn_inert_list.append(demo.get_turnover())
            print(pop_inert_list[-1], turn_inert_list[-1])

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
    

    if EXP == 3 or EXP == 0:
        args_beta_list = []
        pop_beta_list = []
        turn_beta_list = []
        for b in range(0, 101, 10):
            args = argsconfig.get_args()
            args.beta = b
            args.is_const_IS = False
            args_beta_list.append(args)
        for args_idx, args in enumerate(args_beta_list):
            demo = Simulation(args, args.random_seed + args_idx)
            demo.simulate()
            pop_beta_list.append(demo.get_mean_popularity())
            turn_beta_list.append(demo.get_turnover())
     
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