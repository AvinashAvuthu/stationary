import os
import pickle
import subprocess

from matplotlib import pyplot as plt
from scipy.misc import comb
import ternary

from stationary.utils.edges import enumerate_states_from_edges
from stationary.processes.incentives import linear_fitness_landscape, fermi
from stationary.processes.incentive_process import (
    multivariate_transitions_gen)


def num_states(N, n=3):
    """
    Returns the number of states in the discretization of the simplex.
    """

    return comb(N+n-1, n-1, exact=True)


def pickle_inv_enumeration(inv_enum, pickle_filename="inv_enum.pickle"):
    """
    Pickle the inverse enumeration of states, needed to import the exported
    stationary calculation.
    """

    with open(pickle_filename, 'wb') as output_file:
        pickle.dump(inv_enum, output_file)


def output_enumerated_edges(N, n, edges, filename="enumerated_edges.csv"):
    """
    Writes the graph underlying to the Markov process to disk. This is used to
    export the computation to a C++ implementation if the number of nodes is
    very large.
    """

    edges = list(edges)

    # Collect all the states from the list of edges
    all_states, enum, inv_enum = enumerate_states_from_edges(edges, inverse=True)

    # Output enumerated_edges
    with open(filename, 'w') as outfile:
        outfile.write(str(num_states(N, n)) + "\n")
        outfile.write(str(n) + "\n")
        for (source, target, weight) in list(edges):
            row = [str(enum[source]), str(enum[target]), str.format('%.50f' % weight)]
            outfile.write(",".join(row) + "\n")
    return inv_enum


def load_pickled_inv_enum(filename="inv_enum.pickle"):
    """
    Load the pickled inverse enumerate to translate the stationary states
    from the exported calculation.
    """

    with open(filename, 'rb') as input_file:
        inv_enum = pickle.load(input_file)
    return inv_enum


def load_stationary_gen(filename="enumerated_stationary.txt"):
    """
    Loads the computed stationary distribution from the exported calculation.
    The states are still enumerated.
    """

    with open(filename) as input_file:
        for line in input_file:
            line = line.strip()
            state, value = line.split(',')
            yield (int(state), float(value))


def stationary_gen(filename="enumerated_stationary.txt",
                   pickle_filename="inv_enum.pickle"):
    """
    Loads the stationary distribution computed by the C++ implementation and
    reverses the enumeration.
    """

    inv_enum = load_pickled_inv_enum(filename=pickle_filename)
    gen = load_stationary_gen(filename=filename)
    for enum_state, value in gen:
        state = inv_enum[enum_state]
        yield (state, value)


def remove_boundary(s):
    """Removes the boundary, which improves some stationary plots visually."""
    s1 = dict()
    for k, v in s.items():
        a, b, c = k
        if a * b * c != 0:
            s1[k] = v
    return s1


def render_stationary(s):
    """
    Renders a stationary distribution.
    """

    # Put the stationary distribution into a dictionary
    d = dict()
    for state, value in s:
        d[state] = value
    N = sum(list(d.keys())[0])
    # Plot it
    figure, tax = ternary.figure(scale=N)
    tax.heatmap(remove_boundary(d), scientific=True, style='triangular',
                cmap="jet")
    return tax


def stationary_max_min(filename="enumerated_stationary.txt"):
    min_ = 1.
    max_ = 0.
    gen = load_stationary_gen(filename=filename)
    for enum_state, value in gen:
        if value > max_:
            max_ = value
        if value < min_:
            min_ = value
    return max_, min_


def full_example(N, m, mu, beta=1., pickle_filename="inv_enum.pickle",
                 filename="enumerated_edges.csv"):
    """
    Full example of exporting the stationary calculation to C++.
    """

    print("Computing graph of the Markov process.")
    if not mu:
        mu = 3. / 2 * 1. / N
    if m is None:
        m = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    iterations = 200 * N

    num_types = len(m[0])
    fitness_landscape = linear_fitness_landscape(m)
    incentive = fermi(fitness_landscape, beta=beta)
    edges_gen = multivariate_transitions_gen(
        N, incentive, num_types=num_types, mu=mu)

    print("Outputting graph to %s" % filename)
    inv_enum = output_enumerated_edges(
        N, num_types, edges_gen, filename=filename)
    print("Saving inverse enumeration to %s" % pickle_filename)
    pickle_inv_enumeration(inv_enum, pickle_filename="inv_enum.pickle")

    print("Running C++ Calculation")
    cwd = os.getcwd()
    executable = os.path.join(cwd, "a.out")
    subprocess.call([executable, filename, str(iterations)])

    print("Rendering stationary to SVG")
    vmax, vmin = stationary_max_min()
    s = list(stationary_gen(
        filename="enumerated_stationary.txt",
        pickle_filename="inv_enum.pickle"))
    ternary.svg_heatmap(s, N, "stationary.svg", vmax=vmax, vmin=vmin, style='h')

    print("Rendering stationary")
    tax = render_stationary(s)
    tax.ticks(axis='lbr', linewidth=1, multiple=N//3, offset=0.015)
    tax.clear_matplotlib_ticks()
    plt.show()


if __name__ == '__main__':
    N = 180
    mu = 1. / N
    m = [[0, 1, -1], [-1, 0, 1], [1, -1, 0]]
    full_example(N=N, m=m, mu=mu, beta=1.5)


