import argparse
import multiprocessing
import numpy as np
import os
import sys

from args import ArgsConfig
from utils import Simulation


if __name__ == "__main__":
    argsconfig = ArgsConfig()
    args = argsconfig.get_args()
    
    demo = Simulation(args, args.random_seed)
    demo.simulate()

    print("popularity: {}".format(demo.get_popularity()))
    print("turnover  : {}".format(demo.get_turnover()))
