import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from random import choice

runs_path = "../runs/"
def get_dirs():
    dirs = os.listdir(runs_path)
    try:
        dirs.remove(".DS_Store")
    except:
        pass

    return dirs


def get_run_paths(index):
    dirs = get_dirs()
    # we want to evaluate all runs of one setup
    dir = dirs[index]
    runs = os.listdir(runs_path + dir)
    return runs

def get_best_fitness(dir_index, runs, representation):
    best_fitness_list = []
    best_fitness_serie = []
    variance_serie = []

    dirs = get_dirs()
    dir = dirs[dir_index]


    if representation:
        fitness_index = 2
    else:
        fitness_index = 1
    variance_index = fitness_index +1 
    for run in runs:
        df = pd.read_csv(runs_path + dir + "/" +run, header=None)
        # plot the best fitness across generations
        temp = np.asarray(df.groupby([0])[fitness_index].min())
        best_fitness_serie.append(temp)

        var_tmp = np.asarray(df.groupby([0])[variance_index].min())
        variance_serie.append(var_tmp)

        # find best fitness of last generation
        # make list of N final best fitnesses of each setup
        # compare average fitness,
        best = temp[-1]
        best_fitness_list.append(best)

    return best_fitness_list, best_fitness_serie, variance_serie



def plot_whole_scatter(dir_index, run_index, runs, representation):

    best_fitness_list = []
    best_fitness_serie = []

    dirs = get_dirs()
    dir = dirs[dir_index]

    run = runs[run_index]
    df = pd.read_csv(runs_path + dir + "/" +run, header=None)

    if representation:
        fitness_index = 2
    else:
        fitness_index = 1

    # plot the best fitness across generations
    temp = np.asarray(df.groupby([0])[fitness_index].min())
    best_fitness_serie.append(temp)

    # find best fitness of last generation
    # make list of N final best fitnesses of each setup
    # compare average fitness,
    best = temp[-1]
    best_fitness_list.append(best)
    # plot all individuals fitness for each generation
    if representation:
        df = df.drop(columns=[1])
    df.plot.scatter(0, fitness_index, s=0.5)
