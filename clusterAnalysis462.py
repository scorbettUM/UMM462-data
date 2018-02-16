# -*- coding: utf-8 -*-
"""
    Sean Corbett
    02/16/2018
    M462 - Theoretical Data analytics
    Homework 1: Problems 1 and 2


    IMPORTANT: Please install pandas before running this
               submission.
"""

import time, sys
from collections import namedtuple

import numpy as np
import pandas as pd
obsID = namedtuple('observation','Cluster Row')
import datetime
import matplotlib.pyplot as plt
from sys import argv

def getData(path):
    g = open(path, 'r')
    variables = g.readline().strip('\n').split(',')
    stocks = variables[1:]
    
    dataDict = {}
    dateDict = {}
    data = g.read().split('\n')
    for record in data:
        lst = record.split(',')
        x = [float(s) for s in lst[1:]]
        try:
            1/len(x)
            day = calculateDay(lst[0])
            dateDict[day] = lst[0]
            dataDict[day] = x
        except(ZeroDivisionError):
            pass
    
    days = list(dataDict.keys())
    nDays = len(dataDict)
    nStocks = len(dataDict[days[0]]) 
    X = np.zeros(shape = (nStocks, nDays))
    
    
    ''' Fill the matrix with values. Warning: days are NOT necessarily ordered sequentially'''
    ''' Therefore, we put them in order, and then build the matrices in sequential order:'''
    orderedDays = sorted(days)
    dates = [0]*nDays
    for i, day in enumerate(orderedDays):
        X[:, i] = dataDict[day]
        dates[i] = dateDict[day]
    
   
    ''' Scale each stock series to have mean 0 and standard deviation 1 '''
    ''' Using numpy, the operation: matrix / y divides each column of M by the corresponding element in y '''

    print('X shape = ', np.shape(X))    
    
    xTranspose = X.T
    Z = ( (xTranspose - np.mean(xTranspose, axis=0)) / np.std(xTranspose, axis=0) ).T    
    columnDict = {stock:i for i, stock in enumerate(stocks)}    
    
    return stocks, Z, columnDict, orderedDays, dates 
    
def plot(dataToPlot, dates):
    ''' Code for plotting  a time series '''
    ''' Set up time variable for x-axis '''
    x = [datetime.datetime.strptime(x, "%Y-%m-%d") for x in dates]
    plt.figure(figsize=(10, 5))
    legend = []
    for i in range(len(dataToPlot)):
        y = dataToPlot[i]    
        plt.plot(x,y) 
        legend.append('Cluster '+str(i))
    plt.xlabel('Date')
    plt.ylabel('Closing price ($)')
    plt.legend(loc='upper right')
    plt.legend(legend)
    #plt.savefig('/home/brian/M467/Figures/centroids.eps', format='eps',dpi = 1200)
    plt.show()

def calculateDay(string):
    ''' Day 0 = Dec 31, 2006 '''
    year = int(string[:4]) - 2007                   
    return time.strptime(string, "%Y-%m-%d").tm_yday + year*365

def createInitialAssigments(Z, nClusters, stocks):

    n, nDays = np.shape(Z)
    ''' compute the mean of the last 100 days for each stock '''
    means = np.mean(Z[:,nDays- 100:],axis = 1)
    orderVector = np.argsort(means)
    '''
    print('Sorted stocks according to last 100 day mean:')
    
    for i in range(n):
        print(stocks[orderVector[n-i-1]], '\t',means[orderVector[n-i-1]])
    '''
    ''' Initial assignments based on splitting the range of 100-day mean into intervals: '''
    splits = [(i+1)*int(n/nClusters) for i in range(nClusters-1)]
    splits.append(n)
    
    ''' Observations assigned to cluster: '''
    initialAssignments = [0] * n
    for i in range(n):
        initialAssignments[orderVector[i]]  = sum([j*(splits[j-1] < i <= splits[j]) for j in range(1,nClusters)] )

    ''' For reference: save the cluster assignment and row location (i) for each stock'''
    membershipDict = {stock : obsID(cluster, i) for i, (stock, cluster) in enumerate(zip(stocks, initialAssignments)) } 
    return membershipDict

def centroidComputer(membershipDict, Z):
    ''' Computes the centroid for each cluster using the data in Z '''
    ''' Iterate over stocks and aggregate the series, then divide to get the means '''
    
    ' Initialize empty dictionary :'''
    centroidDict = dict.fromkeys(range(nClusters))  
    
    ''' identifier identifies the current cluster membership of a stock '''
    ''' and the row of Z containing the series for the stock '''
    for stock, identifier in membershipDict.items():
        center = centroidDict[identifier.Cluster]
        
        try:
            center[0] += 1
            center[1] = [a+b for a, b in zip(center[1],Z[identifier.Row,:])]
        except(TypeError): 
            center =[1, Z[identifier.Row,:]]
        centroidDict[identifier.Cluster] = center
    
    ''' Divide values by the number of members in the respective cluster: '''  
    ''' centroidDict[i][0] is the number of members for cluster i '''
    ''' centroidDict[i][1] is the series of sums for cluster i '''
    
    for i in range(nClusters):
        centroidDict[i][1] = [x/centroidDict[i][0] for x in centroidDict[i][1]]
    return centroidDict


def kMeansCusters(Z, membershipDict, centroidDict):

    ''' Total SS is the error sums-of-squares with no clusters '''
    xbar = np.mean(Z, axis = 0)
    totalSS = sum([sum((z-xbar)**2) for z in Z])
    print('\nObj fn = ',round(totalSS,1))
    
    ''' Iterate until no observations (stocks) are relocated '''
    ''' Dumb algorithm --- rebuild the clusters according to the nearest centroid to '''
    ''' each observation '''
    
    repeat = True
    while repeat == True:
        updateDict = {}
        ''' Iterate over stocks '''
        for stock, ID  in membershipDict.items():
            minDist = 1E5 # Initialize the minimum obs-to-cluster distance.
            
            ''' Iterate over cluster and determine the nearest centroid/cluster'''
            for label, center in centroidDict.items():
                centroid = center[1]
                
                """
                    Sean Corbett
                    Modification: HW 1, Problem 2
                    Notes: Changed distance algorithm to cosine distance.
                """
                zToCenDist = 0.5*(1 - np.corrcoef(Z[ID.Row,:], centroid)[0,1])
                ''' Euclidean distance squared '''
                # zToCenDist = sum((Z[ID.Row,:] - centroid)**2)
                
    
                ''' Reassign membership if necessary:'''
                if zToCenDist < minDist: 
                    nearestCluster = label
                    minDist = zToCenDist          
                 
            ''' Save the results for the stock'''       
            updateDict[stock] = obsID(nearestCluster, ID.Row)     
    
        ''' Test whether there's been an update. '''
        ''' If so, recompute the centroids and the objective function '''
        
        if membershipDict != updateDict:
            ''' MUST use copy. Otherwise membershipDict and updateDict share the same address '''
            membershipDict = updateDict.copy()
            ''' Recompute the centroids:'''
            centroidDict = centroidComputer( membershipDict, Z)
            
            objFn = 0
            for cluster, row in membershipDict.values():
                """
                    Sean Corbett
                    Modification: HW 1, Problem 2
                    Notes: Updated objective function to reflect sum of all cosine distances.
                """
                objFn += 0.5 * (1 - np.corrcoef(Z[row,:], centroidDict[cluster][1])[0,1])
             
            print('UPDATE Obj fn = ', round(objFn,1))
        else:
            repeat = False    
            print('No UPDATE')
            
        for label, values in centroidDict.items():
            print('Cluster =', label,' Size = ',values[0])
    return membershipDict, centroidDict


def calculateClusterVariability(members, centroids, nClusters):
    """
        Sean Corbett
        Modification: HW 1, Problem 1
        Changes: This is the function written to calculate and report intracluster variability.
                 Note that, theoretically, as the number of clusters increases, the distances
                 between members of a cluster should make the distances between cluster members
                 small, and the distance between clusters much greater. In predicting stocks,
                 this increased granularity can assist us in identifying subtle differences in
                 stock perfromance of market segments, as well as better identify features unique
                 to these more granular groups. However, this increased segmentation comes at the
                 cost of the results of analysis being understandable and actionable, as we loose
                 the ability to discern what larger market segments exist. That is to say, we
                 can no longer determine which stocks perform similarly over longer periods of
                 time within a wider market segment, hindering future analysis of stock performance
                 behavior applicable to the larger industry or group of which a smaller segment 
                 would otherwise be a member of. Then in clustring analysis, we ought primarily 
                 aim to choose a lesser number of clusters, as to prevent over-segmentation of 
                 data and allow future analyses to have enough members from each cluster to 
                 act upon.
    """
    intraDict, zToCenDist = dict.fromkeys([i for i in range(nClusters)], 0), 0
    clusterData = [{'numberOfMembers': 0, 'stocks': [], 'observationsPerCluster': 0} for i in range(nClusters)]
    stocksData = {stock[0]: {'cluster': 0, 'observations': 0} for stock in membershipDict.items()}

    for stock, ID  in membershipDict.items():
        for label, center in centroidDict.items():
            centroid = center[1]
            
            ''' cos distance '''
            cosDistance = 0.5*(1 - np.corrcoef(Z[ID.Row,:], centroid)[0,1])/nClusters
            intraDict[ID.Cluster] += cosDistance
            zToCenDist += cosDistance
            clusterData[ID.Cluster]['observationsPerCluster'] += 1
            clusterData[ID.Cluster]['stocks'].append(stock)
            stocksData[stock]['cluster'] = ID.Cluster 
            stocksData[stock]['observations'] += 1

    for cluster in clusterData:
        cluster['stocks'] = set(cluster['stocks'])
        cluster['numberOfMembers'] = len(cluster['stocks'])
        
    data2Mtx = [sim for sim in list(intraDict.values())]
    intraDataFrame = pd.DataFrame(columns=['Variability'], data=data2Mtx, index=[i for i in range(0,nClusters)])
    intraDataFrame.index.name = 'Cluster'


    stocksDataDict = {'Cluster': [stock['cluster'] for stock in stocksData.values()], 'Observations': [stock['observations'] for stock in stocksData.values()]} 
    stocksDataFrame = pd.DataFrame(data=stocksDataDict, columns=['Cluster','Observations'], index=[stockName for stockName in stocksData.keys()])
    stocksDataFrame.index.name = 'Stock'
    stocksDataFrame.sort_index(inplace=True)

    print('\n\n------------------------------------------\n')
    print('Number of Clusters:',nClusters)
    print('\n------------------------------------------\n')
    print('\n\n------------------------------------------\n')
    print('Total Intracluster Variability:',zToCenDist)
    print('\n------------------------------------------\n')
    print('Intracluster Variability by Cluster:\n')
    print(intraDataFrame)
    print('\n------------------------------------------\n')

    print('\n\n------------------------------------------\n')
    print('Number of Stocks:',len(stocksData))
    print('\n\n------------------------------------------\n')
    print('Stock Clust and Observation Count:\n')
    print(stocksDataFrame)
    print("\n\n\n\n")

        

'''************************   Program starts here ************************'''         

"""
    Sean Corbett
    Modification: HW 1, Problem 1
    Notes: Changed main program code to repeatedly execute clustering 
           as to compute intracluster variability over three, four, 
           and five clusters respectively.
"""
clusters = [3,4,5]
path = './data/'
fileName = 'clusterData.txt'

path += fileName
stocks, Z, columnDict, days, dates  = getData(path)

n, nDays = np.shape(Z)
print('N days = ', nDays, '\nN stocks = ', n,'\nZ shape = ',n,'X', nDays,'\n')
nStocks = len(stocks)

for nClusters in clusters:
    ''' Initialize ... '''
    membershipDict = createInitialAssigments(Z, nClusters, stocks)

    ''' Compute centroids and plot a few '''
    centroidDict = centroidComputer( membershipDict, Z)
    dataToPlot= [centroidDict[0][1],centroidDict[1][1],centroidDict[2][1]  ]
    plot(dataToPlot, dates)

    '''  Call the k-means function '''
    membershipDict, centroidDict = kMeansCusters(Z, membershipDict, centroidDict)

    '''  Calculate intracluster variability via cosine similarity  '''
    calculateClusterVariability(membershipDict, centroidDict, nClusters)


    ''' Plot the new centroids '''
    dataToPlot= [centroidDict[0][1],centroidDict[1][1],centroidDict[2][1]  ]
    plot(dataToPlot, dates)

sys.exit()

    # intraDict = dict.fromkeys([i for i in range(nClusters)])
    # for stock, ID  in membershipDict.items():
    #             for label, center in centroidDict.items():
    #                 centroid = center[1]
                    
    #                 ''' cos distance '''
    #                 #zToCenDist = 0.5*(1 - np.corrcoef(Z[ID.Row,:], centroid)[0,1])