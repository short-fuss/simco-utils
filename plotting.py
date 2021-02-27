import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import datetime
import GPy

prop_cycle = plt.rcParams['axes.prop_cycle']
shades = {'Normal': 'green', 'Recession': 'orange', 'Boom': 'purple'}

def gp_smoother(ps, quality, set_mean=False, lengthscale=None):
    t0 = ps['Time'].values[0]
    y = ps.iloc[:,quality+1].values
    mask = np.isnan(y)==False
    X = np.array([np.timedelta64(t - t0, 'h') / np.timedelta64(1, 'h') for t in ps['Time'].values[mask]])
    Y = np.array(y[mask])
    
    kern = GPy.kern.Matern52(1, lengthscale=lengthscale)
    kern.lengthscale.fix()

    if set_mean:
        Ymean = Y.mean()
        mf = GPy.core.Mapping(1,1)
        mf.f = lambda x: Ymean
        mf.update_gradients = lambda a,b: 0
        mf.gradients_X = lambda a,b: 0
    else:
        mf = None
        
    likelihood = GPy.likelihoods.Gaussian()
    model = GPy.core.GP(X[:,None], Y[:,None], kern, likelihood, mean_function=mf)
    model.optimize()
    return model, X
    
def filter_trace(values, q):
    locs = np.where([np.isfinite(v) for v in values[:, q+1]])[0]
    if len(locs) < 2:
        return None, None, None
    #print(q, len(locs))
    t = values[locs, 0]
    pr = values[locs, q+1]
    tr = [(ti - t[0]).total_seconds() for ti in t]
    
    return tr, pr, t

def compute_stats(tr, pr):
    E_p_x = np.trapz(pr, x=tr) / (tr[-1] - tr[0])
    E_p_x2 = np.trapz(pr**2, x=tr) / (tr[-1] - tr[0])
    sig_p = np.sqrt(E_p_x2 - E_p_x**2)
    current = pr[-1]
    z_score = (current - E_p_x) / sig_p if sig_p > 0.0 else np.infty
    
    return current, E_p_x, sig_p, z_score

class Prices:
    def __init__(self, initial_time=np.datetime64('2020-10-08T15')):
        self.history = []
        for file_name in glob.glob('CommodityPrices/*.csv'):
            df = pd.read_csv(file_name, index_col=0, low_memory=False)
            datetime_str = file_name.split('\\')[1].replace('.csv','')
            timestamp = datetime.datetime.strptime(datetime_str, "%Y%m%d-%H%M%S")
            df.insert(0, 'Time', timestamp)
            if timestamp > initial_time:
                self.history.append(df)
        print(f'Loaded {len(self.history)} files')

        self.colors = prop_cycle.by_key()['color']
        self.t0 = initial_time
        self.economy_history = [
            [np.datetime64('2020-10-08T15'), 'Normal'], 
            [np.datetime64('2020-11-27T15'), 'Boom'],
            [np.datetime64('2020-12-11T15'), 'Normal'],
            [np.datetime64('2020-12-18T15'), 'Boom'],
            [np.datetime64('2020-12-25T15'), 'Normal'],
            [np.datetime64('2021-01-29T15'), 'Recession'],
            [np.datetime64('2021-02-05T15'), 'Normal'],
        ]
        #self.economy_history = [eh for eh in self.economy_history if eh[0] > self.t0]
        self.economy_history.append([np.datetime64(datetime.datetime.now()), self.economy_history[-1][1]])

    def get_commodity(self, commodity, maximum_quality=None):
        rows = [df.loc[commodity] for df in self.history]
        df = pd.DataFrame(rows)
        #df = df.dropna(axis=1)
        if maximum_quality is None:
            return df
        else:
            return df.iloc[:,:maximum_quality+2]

    def plot_commodity(self, commodity, qs, ax=None, ylims=None):
        ph = self.get_commodity(commodity, maximum_quality=np.max(qs))
        if ax is None:
            ax = plt.subplot()
        for q in qs:
            ax.scatter(x=ph['Time'].values, y=ph.iloc[:,q+1].values, s=4, c=self.colors[q], label=f'Q{q}')
            mh, X = gp_smoother(ph, q, set_mean=True, lengthscale=50)
            Xs = np.linspace(X[0], X[-1], 150)
            Ts = [np.timedelta64(int(x), 'h') for x in Xs] + ph['Time'].values[0]
            ymean, yvar = mh.predict(Xs[:,None])
            ystd = np.sqrt(yvar)
            ax.plot(Ts, ymean, c=self.colors[q])
            ax.fill_between(Ts, np.squeeze(ymean-ystd), np.squeeze(ymean+ystd), alpha=0.1, color=self.colors[q])
            ax.set_title(commodity)
            if ylims:
                ax.set_ylim(ylims)
            for tick in ax.get_xticklabels():
                tick.set_rotation(45)
        #ax.legend()

        economy = self.economy_history
        es, indices = np.unique([e[1] for e in self.economy_history], return_index=True)
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        for i in range(len(economy) - 1):
            label = economy[i][1] if i in indices else None
            ax.fill_between([economy[i][0], economy[i+1][0]], ylim[0]*np.ones(2), 
                (0.03*ylim[1]+0.97*ylim[0])*np.ones(2), color=shades[economy[i][1]], label=label
            )
        ax.set_xlim(xlim)
        ax.legend(loc='upper left')

    def get_stats(self, com, qmax=4):
        #print(com)
        values = self.get_commodity(com, maximum_quality=qmax).values
        stats = []
        for q in range(values.shape[1] - 1):
            tr, pr, _ = filter_trace(values, q)
            if tr is None:
                continue
            current, E_p_x, sig_p, z_score = compute_stats(tr, pr)
            stats.append((q, current, E_p_x, sig_p, z_score))
            
        df = pd.DataFrame(stats, columns=['Q', 'Current', 'Mean', 'Std', 'z'])
        df.insert(0, 'Commodity', com)
        return df

    def plot_stats(self, com, q):
        values = self.get_commodity(com, maximum_quality=q).values
        tr, pr, t = filter_trace(values, q)
        current, E_p_x, sig_p, z_score = compute_stats(tr, pr)
        
        f = plt.figure(figsize=(8,4))
        ax = plt.subplot()
        ax.scatter(t, pr, s=10, zorder=1)
        xlim = ax.get_xlim()
        ax.plot(xlim, [E_p_x, E_p_x], 'k--', zorder=0)
        ax.fill_between(xlim, E_p_x - 1.96*sig_p, E_p_x + 1.96*sig_p, color='k', zorder=-1, alpha=0.1)
        for tick in ax.get_xticklabels():
            tick.set_rotation(45)
        sns.despine()