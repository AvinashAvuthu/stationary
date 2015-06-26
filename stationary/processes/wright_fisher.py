"""
The Wright-Fisher process
"""

import numpy
from numpy import array, log, exp

from scipy.special import gammaln

from ..utils.math_helpers import kl_divergence, simplex_generator, one_step_indicies_generator, dot_product, normalize, q_divergence, kl_divergence_dict, logsumexp


def cache_M(N, num_types=3):
    """
    Caches multinomial coefficients.

    Parameters
    ----------
    N: int
        Population size / simplex divisor
    num_types: int, 3
        Number of types in population
    """

    M = numpy.zeros(shape=(N+1, N+1))
    for i, j, k in simplex_generator(N, d=num_types-1):
        M[i][j] = gammaln(N+1) - gammaln(i+1) - gammaln(j+1) - gammaln(k+1)
    return M

## Works but has enormous memory footprint, ~O(N^4)
def multivariate_transitions_sub(N, incentive, mu=0.001):
    """
    Computes transitions for dimension n=3 moran process given a game matrix.

    Parameters
    ----------
    N: int
        Population size / simplex divisor
    incentive: function
        An incentive function from incentives.py
    mu: float, 0.001
        The mutation rate of the process
    """

    def multinomial_probability(xs, ps):
        xs, ps = array(xs), array(ps)
        # Log-Binomial
        M = gammaln(N+1) - gammaln(xs[0] + 1) - gammaln(xs[1] + 1)
        result = M + sum(xs * log(ps))
        return exp(result)

    edges = []
    for current_state in simplex_generator(N, d=1):
        for next_state in simplex_generator(N, d=1):
            inc = incentive(current_state)
            ps = []
            s = float(sum(inc))
            r = dot_product(inc, [1. - mu, mu]) / s
            ps.append(r)
            r = dot_product(inc, [mu, 1. - mu]) / s
            ps.append(r)
            edges.append((current_state, next_state,
                          multinomial_probability(next_state, ps)))
    return edges


def multivariate_transitions(N, incentive, mu=0.001, num_types=3):
    """Computes transitions for the Wright-Fisher process. Since this can be a
    large matrix, this function returns a function that computes the transitions
    for any given two states.

    Parameters
    ----------
    N: int
        Population size / simplex divisor
    incentive: function
        An incentive function from incentives.py
    num_types: int, 3
        Number of types in population
    mu: float, 0.001
        The mutation rate of the process

    Returns
    -------
    edges: list, if n == 2
    edge_func: function, if n=3

    """

    if num_types == 2:
        return multivariate_transitions_sub(N, incentive, mu=mu)

    M = cache_M(N)

    def multinomial_probability(xs, ps):
        xs, ps = array(xs), array(ps)
        result = M[xs[0]][xs[1]] + sum(xs * log(ps))
        return exp(result)

    edges = numpy.zeros(shape=(N+1, N+1, N+1, N+1))
    for current_state in simplex_generator(N, num_types-1):
        for next_state in simplex_generator(N, num_types-1):
            inc = incentive(current_state)
            ps = []
            s = float(sum(inc))
            if s == 0:
                raise ValueError, "You need to use a Fermi incentive to prevent division by zero."""
            half_mu = mu / 2.
            r = dot_product(inc, [1 - mu, half_mu, half_mu]) / s
            ps.append(r)
            r = dot_product(inc, [half_mu, 1 - mu, half_mu]) / s
            ps.append(r)
            r = dot_product(inc, [half_mu, half_mu, 1 - mu]) / s
            ps.append(r)
            edges[current_state[0]][current_state[1]][next_state[0]][next_state[1]] = multinomial_probability(next_state, ps)

    def g(current_state, next_state):
        return edges[current_state[0]][current_state[1]][next_state[0]][next_state[1]]
    return g

def kl(N, edge_func, q_d=1):
    """
    Computes the KL-div of the expected state with the state, for all states.

    Parameters
    ----------
    edge_func, function
        Yields the transition probabilities between two states, edge_func(a,b)
    q_d: float, 1
        parameter that specifies which divergence function to use

    Returns
    -------
    Dictionary mapping states to D(E(state), state)
    """

    e = dict()
    dist = q_divergence(q_d)
    for x in simplex_generator(N):
        e[x] = 0.
        for y in simplex_generator(N):
            w = edge_func(x,y)
            # Could use the fact that E(x) = n p here instead for efficiency, but this is relatively fast compared to the stationary calculation already, and is a good check of the identity. This would require a rewrite using the transition functions.
            e[x] += numpy.array(y) * w
    d = dict()
    for (i, j, k), v in e.items():
        # KL doesn't play well with boundary states.
        if i * j * k == 0:
            continue
        d[(i, j, k)] = dist(normalize(v), normalize([i, j, k]))
    return d
