import numpy as np
from collections import namedtuple

def logistic(x):
    return softPlusP(x)

def logisticP(x):
    return logistic(x)*(1- logistic(x))

def softPlusP(x):
    return 1/(1 + np.exp(-x) )

def tanhP(x):
    return 1 - np.tanh(x)**2

def RMSProp(smoothGrad, currGrad):
    rho = 0.9
    smoothGrad = np.sqrt( rho*np.power(smoothGrad, 2)  + (1 - rho)*np.power(currGrad, 2) )
    return smoothGrad

def getSample(D, sampleID, k):
    n = len(sampleID)

    sIndex = [i for i in range(n) if sampleID[i] == k]
    rIndex = [i for i in range(n) if sampleID[i] != k]

    partition = namedtuple('data', 'R E')
    data = namedtuple('data','X Y labels')

    if D.labels is None:
        split = partition(data(D.X[rIndex,:], D.Y[rIndex,:], None ),
                          data(D.X[sIndex,:], D.Y[sIndex,:], None ))
    else:
        split = partition(data(D.X[rIndex,:], D.Y[rIndex,:], [D.labels[i] for i in rIndex]),
                          data(D.X[sIndex,:], D.Y[sIndex,:], [D.labels[i] for i in sIndex]))

    return split

def dEdyhatSqr(Y, yHat):
    return -2 * (Y - yHat)

def rmse(Y, yHat):
    n, s = np.shape(yHat)
    dEyHat = float(sum([sum(np.multiply(Y[:, i] - yHat[:, i],
    Y[:, i] - yHat[:, i])) for i in range(s)])/n)
    return dEyHat

def dEdyhatCE(Y, yHat):
    return -np.multiply(Y - yHat, 1/np.multiply(yHat+1e-16, (1 - yHat-1e-16)))

def crossEntropy(Y, yHat):
    n, s = np.shape(yHat)
    return -np.sum( np.multiply(Y, np.log(yHat+1e-16)) + np.multiply(1 - Y, np.log(1 - yHat+1e-16)) )/n
