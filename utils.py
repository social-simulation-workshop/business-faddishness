import argparse
import itertools
import numpy as np
import sys


def draw(p) -> bool:
    return True if np.random.uniform() < p else False

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def truncated_normal(mean=0.0, sd=1.0) -> float:
    # TODO: unclear explication of truncated normal
    rnt = np.random.normal(loc=mean, scale=sd)
    while rnt > 1.0 or rnt < 0.0:
        rnt = np.random.normal(loc=mean, scale=sd)
    return rnt


class Inno:
    _ids = itertools.count(0)
    
    def __init__(self) -> None:
        self.id = next(self._ids)
        self.V = truncated_normal()

class Firm:
    def __init__(self, args, inno_pool) -> None:
        self.args = args
        self.K = truncated_normal()
        self.outcome_his = [0]
        
        self.inno = np.random.choice(inno_pool)
        self.inno_pool = inno_pool
        self.inno_his = [self.inno]
        self.n_ti = 0
        self.set_IS()
    
    def set_IS(self):
        if self.args.is_const_IS:
            self.I = self.S = self.args.const_IS
        else:
            self.I = truncated_normal(self.args.mean_IS, self.args.sd_IS)
            self.S = truncated_normal(self.args.mean_IS, self.args.sd_IS)

    def get_outcome(self):
        e = truncated_normal() 
        o = self.args.alpha * self.K + self.args.beta * self.inno.V + (1 - self.args.alpha - self.args.beta) * e
        return o

    def get_outcome_and_update(self):
        o = self.get_outcome()
        self.outcome_his.append(o)
        self.inno_his.append(self.inno)

        self.n_ti = 0
        while self.inno_his[-(self.n_ti+1)].id == self.inno.id and (self.n_ti+1) < len(self.inno_his):
            self.n_ti += 1

    def get_outcome_his_avg(self):
        window_size = min(self.args.M, len(self.outcome_his))
        return sum(self.outcome_his[-window_size:]) / window_size 

    def abandon(self, w: Inno, n_tw):
        o_fti = self.get_outcome_his_avg() 
        c_fti = 1 - self.I ** (self.args.lamb * self.n_ti) 
        prob = (1 - o_fti) * c_fti
        if draw(prob):
            self.adoption(w, n_tw)

    def _cal_tw(self, w: Inno):
        for i in range(1, min(self.args.M, len(self.inno_his))):
            if self.inno_his[-i].id == w.id:
                return i - 1
        return -1

    def adoption(self, w: Inno, n_tw):
        r_ext_fw = 1 - self.S ** (self.args.lamb * n_tw)

        tw = self._cal_tw(w)
        if tw == -1:
            r_int_fw = 1
        else:
            r_int_fw = 1 - self.S ** (self.args.lamb * tw)
        
        prob = r_ext_fw * r_int_fw
        if draw(prob):
            self.inno = w
        else:
            self.inno = np.random.choice(self.inno_pool)
        
    

class Simulation:
    def __init__(self, args: argparse.ArgumentParser, random_seed) -> None:
        np.random.seed(random_seed)
        print(args)

        self.args = args
        self.innos = [Inno() for _ in range(self.args.n_inno)]
        self.firms = [Firm(args, self.innos) for _ in range(self.args.n_firm)]
        self.innos_adopted_ctr = [0 for _ in range(self.args.n_inno)]
        for f in self.firms:
            self.innos_adopted_ctr[f.inno.id] += 1
        
        self.leading_inno_his = list()
        self.leading_inno_adopted_ctr = list()

        self.winning_inno_his = list()
        
        # the number of different firms that have won with winning between t and t - M
        self.n_tw = None
    
    def _update_winning_inno_his(self):
        best_firm_idx = np.argmax([f.outcome_his[-1] for f in self.firms])
        self.winning_inno_his.append(self.firms[best_firm_idx].inno)
        self.n_tw = sum([1 for i in range(1, min(self.args.M, len(self.winning_inno_his)) + 1)
            if self.winning_inno_his[-i] == self.winning_inno_his[-1]])
    
    def _update_leading_inno_adopted_ctr(self):
        self.innos_adopted_ctr = [0 for _ in range(self.args.n_inno)]
        for f in self.firms:
            self.innos_adopted_ctr[f.inno.id] += 1
        best_inno_idx = np.argmax(self.innos_adopted_ctr)
        self.leading_inno_his.append(best_inno_idx)
        self.leading_inno_adopted_ctr.append(self.innos_adopted_ctr[best_inno_idx])
    
    def update(self):
        self._update_winning_inno_his()
        self._update_leading_inno_adopted_ctr()
    
    def simulate(self):
        self.update()
        for iter_idx in range(self.args.n_iter):
            for firm_idx in range(self.args.n_firm):
                self.firms[firm_idx].abandon(self.winning_inno_his[-1], self.n_tw)
                self.firms[firm_idx].get_outcome_and_update()
            self.update()
            print("iter {} | {} {}".format(iter_idx, self.leading_inno_his[-1], self.leading_inno_adopted_ctr[-1]/self.args.n_firm))

    def get_popularity(self) -> float:
        return np.mean(self.leading_inno_adopted_ctr) / self.args.n_firm 
    
    def get_turnover(self) -> float:
        turnover = 0
        current_inno = self.leading_inno_his[0]
        for inno_idx in range(1, len(self.leading_inno_his)):
            if current_inno != self.leading_inno_his[inno_idx]:
                turnover += 1
                current_inno = self.leading_inno_his[inno_idx]
        return turnover
        
