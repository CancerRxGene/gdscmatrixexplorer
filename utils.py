import numpy as np


def viability_curve(x, xmid, slope):
    return 1 - (1 / (1 + np.exp(-(x - xmid)/slope)))


def x_to_conc(x, maxc):
    return maxc * np.power(2, (x - 9)) / 1000000


def conc_to_x(conc, maxc):
    return (np.log(conc / maxc) / np.log(2)) + 9