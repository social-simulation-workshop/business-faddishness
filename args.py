import argparse

class ArgsConfig(object):
    
    def __init__(self) -> None:
        super().__init__()
    
        parser = argparse.ArgumentParser()

        parser.add_argument("--alpha", type=float, default=0.0,
            help="")
        parser.add_argument("--beta", type=float, default=0.0, 
            help="")
        parser.add_argument("--M", type=int, default=10,
            help="")
        parser.add_argument("--lamb", type=float, default=0.25,
            help="")
        parser.add_argument("--n_firm", type=int, default=100,
            help="")
        parser.add_argument("--n_inno", type=int, default=1000,
            help="")
        parser.add_argument("--n_iter", type=int, default=200,
            help="")
        parser.add_argument("--is_const_IS", type=bool, default=True,
            help="")
        parser.add_argument("--const_I", type=float, default=0.0,
            help="")
        parser.add_argument("--const_S", type=float, default=0.0,
            help="")
        parser.add_argument("--mean_IS", type=float, default=0.5,
            help="")
        parser.add_argument("--sd_IS", type=float, default=1.0, 
            help="")
        parser.add_argument("--random_seed", type=int, default=4025, 
            help="")

        self.parser = parser

    def get_args(self):
        args = self.parser.parse_args()
        return args
