import os

from matplotlib import pyplot
import numpy
from numpy import cumprod, cumsum

#from entropy_rate import compute_entropy_rate
from stationary import entropy_rate
from math_helpers import kl_divergence, normalize, dot_product

# Font config for plots
import matplotlib
font = {'size': 22}
matplotlib.rc('font', **font)

def ensure_directory(directory):
    if not os.path.isdir(directory):
        os.mkdir(directory)

def ensure_digits(num, s):
    """Prepends a string s with zeros to enforce a set num of digits."""
    if len(s) < num:
        return "0"*(num - len(s)) + s
    return s

def exp_var_kl(ups, downs):
    N = len(ups) - 1
    es = []
    ss = []
    vs = []
    for i in range(0, N+1):
        if i == 0 :
            up = ups[i]
            down = 0
        elif i == N:
            up = 0
            down = downs[i]
        else:
            up = ups[i]
            down = downs[i]
        stay = 1. - up - down
        x_a = up*(i+1) + down*(i-1) + stay*i
        x_b = up*(N-i-1) + down*(N-i+1) + stay*(N-i)
        e = normalize([x_a, x_b])
        es.append(e)
        #s = kl_divergence(e, normalize([i, N-i]))
        s = kl_divergence(normalize([i, N-i]), e)
        ss.append(s)
        v = (up*(i+1)**2 + down*(i-1)**2 + stay*i**2)/(N**2) - (float(x_a)/N)**2 
        vs.append(v)
    return (es, vs, ss)

# For Incentive process
def transitions_figure(N, m, mu=0.01, k=1., mutations='uniform', process="moran", incentive="replicator", q=1., eta=None):
    """Plot transition entropies and stationary distributions."""
    (e, s, d) = compute_entropy_rate(N, m=m, mutations=mutations, mu_ab=mu, mu_ba=k*mu, verbose=False, report=True, q=q, eta=eta)

    ups = []
    downs = []
    for i in range(0, N+1):
        if i != N:
            ups.append(d[(i,i+1)])
        else:
            ups.append(0)
        if i != 0:
            downs.append(d[(i, i-1)])
        else:
            downs.append(0)
    evens = []
    for i in range(0, N+1):
        evens.append(1.-ups[i]-downs[i])

    pyplot.subplot(311)
    xs = range(0, N+1)
    pyplot.plot(xs, ups)
    pyplot.plot(xs, downs)
    pyplot.title("Transition Probabilities")

    ax = pyplot.subplot(312)
    ee, vs, ss = exp_var_kl(ups, downs)

    pyplot.plot(xs[1:N], ss[1:N])
    pyplot.xlim(0,N)
    pyplot.title("Relative Entropy")
    ax.ticklabel_format(style='sci', scilimits=(0,0), axis='y')

    pyplot.subplot(313)
    pyplot.plot(xs, s)
    pyplot.title("Stationary Distribution")
    pyplot.xlabel("Number of A individuals (i)")

# For Wright-Fisher and k-fold incentive
def transitions_figure_N(N, m, mu=0.01, k=1., mutations='uniform', process="wright-fisher", incentive="replicator", q=1., eta=None):
    """Plot transition entropies and stationary distributions."""
    (e, s, d) = compute_entropy_rate(N, m=m, mutations=mutations, mu_ab=mu, mu_ba=k*mu, verbose=False, report=True, q=q, process=process, eta=eta)
    pyplot.subplot(311)

    #from numpy import linalg as LA
    #print list(sorted(LA.eigvals(d)))

    xs = range(0, N+1)
    ups = [d[i][i+1] for i in range(0, N)]
    ups.append(0)
    downs = [0]
    downs.extend([d[i][i-1] for i in range(1, N+1)])

    pyplot.plot(xs, ups)
    pyplot.plot(xs, downs)
    pyplot.title("Transition Probabilities")


    pyplot.subplot(312)

    expected_states = []    
    for i in xs:
        x_a = 0.
        x_b = 0
        for j in range(0, N+1):
            x_a += j * d[i][j]
            x_b += (N-j) * d[i][j]
        expected_states.append(kl_divergence(normalize([x_a, x_b]), normalize([i, N-i])))
        #expected_states.append(kl_divergence( normalize([i, N-i]), normalize([x_a, x_b])))

    argmin = 1+ numpy.argmin(expected_states[1:N])
    print "ekl min at i =", argmin

    pyplot.plot(xs[1:N], expected_states[1:N])
    pyplot.xlim(0,N)
    pyplot.title("Relative Entropy")
        #pyplot.ylim(0, (N*math.sqrt(3)/2) + 2)

    pyplot.subplot(313)

    print "stationary max:", numpy.argmax(s)
    #pyplot.plot(range(1, N), s[1:N])
    pyplot.plot(xs, s)
    pyplot.title("Stationary Distribution")
    pyplot.xlabel("Number of A individuals (i)")


#def look_for_counterexample(directory="counterexamples"):
    #ensure_directory(directory)
    #ms = []
    #ms.append([[1,1],[1,1]])
    #ms.append([[2,2],[1,1]])
    #ms.append([[3,3],[1,1]])
    #ms.append([[1,2],[2,1]])
    #ms.append([[1,2],[5,1]])
    #ms.append([[20,1],[7,10]])

    #i = 0
    #e = 0
    #for N in [20,50,100,500,100]:
        #for m in ms:
            #for mu in [0.1, 0.01, 0.001]:
                #for k in [0.01, 0.1, 1, 10, 100]:
                    #for q in [-1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5]:
                        #for mutations in ["boundary", "uniform"]:
                            #for incentive in ["replicator", "logit"]:
                                    #try:
                                        #print i, N, mu, k, q, mutations, incentive, m, e
                                        #pyplot.clf()
                                        #transitions_figure_N(N, m, mu=mu, q=q, k=k, mutations=mutations, incentive=incentive, process="wright-fisher")
                                        ##transitions_figure(N, m, mu=mu, q=q, k=k, mutations=mutations, incentive=incentive, process="moran")
                                        #pyplot.savefig(os.path.join(directory, ensure_digits(6, str(i)) + ".png"))
                                    #except:
                                        #i+=1
                                        #continue
                                    #i += 1

if __name__ == '__main__':    
    # Paper "figure_1.eps"
    N= 100
    mu = 1./1000
    k = 1
    q = 1

    mutations = "uniform"
    incentive = "replicator"
    m = [[1, 2], [3, 1]]
    (e, s, d) = compute_entropy_rate(N, m=m, mutations=mutations, mu_ab=mu, mu_ba=k*mu, verbose=False, report=True, q=q, process="moran")
    
    transitions_figure(N, m, mu=mu, q=q, k=k, mutations=mutations, incentive=incentive, process="moran")
    pyplot.show()
    exit()
    
    ## basic examples

    N = 400
    #m = [[1,2],[2,1]]
    #m = [[1,1],[1,1]]
    ###m = [[2,2],[1,1]]
    #m = [[1,2],[5,1]]
    m = [[20,1],[7,10]]

    ##transitions_figure(N, m, mu=0.001, q=1., k=1, incentive="replicator")
    #transitions_figure_N(N, m, mu=0.001, q=1., k=1, incentive="replicator", process="n-fold-moran")

    ###transitions_figure(N, m, mu=0.01, q=2., k=10, incentive="replicator")
    ###transitions_figure_N(N, m, mu=0.01, q=2., k=10, incentive="replicator", process="n-fold-moran")
    
    transitions_figure_N(N, m, mu=0.1, q=2., k=2., incentive="replicator", process="wright-fisher")
    transitions_figure_N(N, m, mu=0.01, q=0.9, k=2., incentive="replicator", process="wright-fisher")
    transitions_figure_N(N, m, mu=0.01, q=0., k=1., incentive="replicator", process="wright-fisher")
    