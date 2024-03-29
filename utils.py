import argparse
import itertools
import numpy as np
from scipy.stats import truncnorm


def draw(p) -> bool:
    return True if np.random.uniform() < p else False

def truncated_normal(mean=0.5, sd=1.0, low=0, upp=1):
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd).rvs()


class Inno:
    _ids = itertools.count(0)
    
    def __init__(self, args) -> None:
        self.id = next(self._ids)
        self.set_V(args)

        self.pop_his = list()
    
    def set_V(self, args):
        self.V = truncated_normal(args.mean_eVK, args.sd_eVK)

class Firm:
    def __init__(self, args, inno_pool: list) -> None:
        self.args = args
        self.K = truncated_normal()
        
        self.inno_pool = inno_pool
        self.inno = np.random.choice(self.inno_pool)
        self.inno_his = list() # with memory of the past M iterations
        self.n_ti = 0
        self.set_IS()

        self.outcome_his = list() # with memory of the past M iterations
        self.get_outcome_and_update() # t = 1
    
    def set_IS(self):
        if self.args.is_const_IS:
            self.I = self.args.const_I
            self.S = self.args.const_S
        else:
            self.I = truncated_normal(self.args.mean_IS, self.args.sd_IS)
            self.S = truncated_normal(self.args.mean_IS, self.args.sd_IS)

    def _get_outcome(self):
        e = truncated_normal()
        o = self.args.alpha * self.K + self.args.beta * self.inno.V + (1 - self.args.alpha - self.args.beta) * e
        return o

    def get_outcome_and_update(self):
        o = self._get_outcome()
        self.outcome_his.append(o)
        if len(self.outcome_his) == self.args.M:
            self.outcome_his.pop(0)
        assert len(self.outcome_his) <= self.args.M
        self.inno_his.append(self.inno.id)
        if len(self.inno_his) == self.args.M:
            self.inno_his.pop(0)
        assert len(self.inno_his) <= self.args.M
        self.n_ti = self.inno_his.count(self.inno.id)

    def get_outcome_his_avg(self):
        return np.mean([o for i, o in enumerate(self.outcome_his) if self.inno_his[i] == self.inno.id])

    def abandon(self, w: Inno, n_tw):
        o_fti = self.get_outcome_his_avg() 
        c_fti = 1 - self.I ** (self.args.lamb * self.n_ti) 
        prob = (1 - o_fti) * c_fti
        if draw(prob):
            self.adoption(w, n_tw)

    def _cal_tw(self, w: Inno):
        for i in range(1, len(self.inno_his)+1):
            if self.inno_his[-i] == w.id:
                return i - 1
        return -1

    def adoption(self, w: Inno, n_tw):
        if self.inno.id == w.id:
            self.inno = np.random.choice(self.inno_pool)
        else:
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
        Inno._ids = itertools.count(0)
        self.args = args
        print(args)

        self.innos = [Inno(args) for _ in range(self.args.n_inno)]
        self.firms = [Firm(args, self.innos) for _ in range(self.args.n_firm)]
        
        self.leading_inno_his = list()
        self.leading_inno_pop_list = list()

        self.winning_inno = np.random.choice(self.innos) 
        self.winning_inno_his = list()
        
        # the number of different firms that have won with winning between t and t - M
        self.n_tw = 0
    
    def _get_inno_popularity_list(self) -> list:
        pop = [0] * self.args.n_inno
        for f in self.firms:
            pop[f.inno.id] += 1
        return pop

    def _update_winning_inno_his(self):
        winning_firm_idx = np.argmax([f.outcome_his[-1] for f in self.firms])
        winning_inno_idx = self.firms[winning_firm_idx].inno.id
        self.winning_inno = self.innos[winning_inno_idx]
        self.winning_inno_his.append(winning_inno_idx)
        if len(self.winning_inno_his) == self.args.M:
            self.winning_inno_his.pop(0)
        self.n_tw = self.winning_inno_his.count(winning_inno_idx)
    
    def _update_leading_inno_pop_list(self):
        inno_pop_list = self._get_inno_popularity_list() 
        leading_inno_idx = np.argmax(inno_pop_list)
        self.leading_inno_his.append(leading_inno_idx)
        self.leading_inno_pop_list.append(inno_pop_list[leading_inno_idx])

        for inno_idx in range(self.args.n_inno):
            self.innos[inno_idx].pop_his.append(inno_pop_list[inno_idx])
    
    def update(self):
        self._update_winning_inno_his()
        self._update_leading_inno_pop_list()
    
    def simulate(self):
        for iter_idx in range(self.args.n_iter):
            # for inno_idx in range(self.args.n_inno):
            #     self.innos[inno_idx].set_V(self.args)
            for firm_idx in range(self.args.n_firm):
                self.firms[firm_idx].abandon(self.winning_inno, self.n_tw)
                self.firms[firm_idx].get_outcome_and_update()
            self.update()
            # print("iter {} | {} {}".format(iter_idx, self.leading_inno_his[-1], self.leading_inno_adopted_ctr[-1]/self.args.n_firm))

    def get_mean_popularity(self) -> float:
        return np.mean(self.leading_inno_pop_list)
    
    def get_turnover(self) -> float:
        turnover = 0
        current_inno = self.leading_inno_his[0]
        for inno_idx in range(1, len(self.leading_inno_his)):
            if current_inno != self.leading_inno_his[inno_idx]:
                turnover += 1
                current_inno = self.leading_inno_his[inno_idx]
        return turnover / len(self.leading_inno_his) * 100
    
    def get_leading_inno_popularity(self):
        assert len(self.leading_inno_his) == len(self.leading_inno_pop_list)

        pop_top6_inno_idx = np.argsort([sum(inno.pop_his[-100:]) for inno in self.innos])[-6:]
        inno_pop = np.array([self.innos[inno_idx].pop_his[-100:] for inno_idx in pop_top6_inno_idx]).astype("float")
        inno_pop[inno_pop == 0.0] = np.nan
        return inno_pop