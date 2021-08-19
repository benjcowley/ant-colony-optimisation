from sys import maxsize
import numpy as np
from numpy.lib.utils import deprecate
from pandas.core.indexing import need_slice
from scipy.spatial import distance_matrix
from matplotlib import pyplot as plt

towns = 20
townsLocation = np.random.randint(0,999, size=(towns,2))
maxIter = 100
ants = 5
pInfluence = 3 # Too low and we run into exploration only, too high and cover the same paths
dInfluence = 12 # Too low and we run into a greedy search, too high and the search stagnates
pheromonePotentency = 1
pheromoneEvaporation = 0.3
pheromoneMatrix = np.full((towns,towns), 0.1) # Starts on 1 as to avoid 0 probability errors
distanceMatrix = distance_matrix(townsLocation,townsLocation)
bestTour = 0
bestRoute = []

def selectorEquation(a, b):
    return (float(a)*pInfluence)*(float(b)*dInfluence) 

def proabilityEquation(totals):
    sum = np.sum(totals)
    returnList = []
    for i in totals:
        returnList.append(i/sum)
    return returnList

def routeSelection(currentLocation, pMatrix, dMatrix):
    distanceRange = dMatrix[currentLocation,:].astype(float) # returns all of a ROW 
    pheromoneRange = pMatrix[currentLocation,:] # Sub Set of availble routes from total pheromone Matrix
    distanceRange = np.delete(distanceRange, currentLocation)
    pheromoneRange = np.delete(pheromoneRange, currentLocation)
    visitbility = np.reciprocal(distanceRange, where=distanceRange>0)
    vfunc = np.vectorize(selectorEquation) # think there is something wrong with this implimentation
    totals = vfunc(pheromoneRange, visitbility) 
    probability = np.array(proabilityEquation(totals)).astype(float) # List of all probabilites based of travelling to each availible route.
    chance = np.random.choice(distanceRange,1, p=probability) # Random Number Generator to select next node.
    outcome = int(np.where(distanceRange==chance)[0])
    if outcome >= currentLocation:
        outcome += 1
    return outcome # All we're returning here is one selection from the slice

def pheromoneUpdate(distancePlot, townVists):
    global pheromoneMatrix, pheromoneEvaporation, pheromonePotentency
    pheromone2 = np.ones_like(pheromoneMatrix).astype(float)
    #np.multiply(pheromoneMatrix, (1-pheromoneEvaporation), where=pheromoneMatrix*(1-pheromoneEvaporation)>1, out=pheromone2) # Evaporate trails if not default
    np.multiply(pheromoneMatrix, (1-pheromoneEvaporation),out=pheromone2) # Evaporate trails if not default
    pheromoneMatrix = pheromone2
    deposits = []
    for i in distancePlot: # Amount of pheromone to be deposits, inversely proportional. Longer route = Less Deposit
        i = pheromonePotentency/i
        deposits.append(i)
    for index, tour in enumerate(townVists):
        for visit in tour:
            pheromoneMatrix[visit[0],visit[1]] += deposits[index]
    return


class Ants():

    def __init__(self, pheromones, nodes, currentLocation, distance, townsLeft):
        self.pheromones = pheromones
        self.nodes = nodes
        self.currentLocation = currentLocation 
        self.distance = distance
        self.townsLeft = townsLeft-1
        self.totalTravel = 0
        self.travelList = [0]
        self.currentGlobal = 0

    def travelOnce(self):
        nextNode = routeSelection(self.currentLocation, self.pheromones, self.distance)
        route = (self.currentLocation, nextNode) 
        x = self.distance[route]
        y = np.where(distanceMatrix == x)
        if self.currentLocation < nextNode:
            self.currentGlobal = y[1][0]
        elif self.currentLocation > nextNode: #
            self.currentGlobal = y[1][1]
        self.travelList.append(self.currentGlobal)
        self.distance = np.delete(self.distance, self.currentLocation,0)
        self.distance = np.delete(self.distance, self.currentLocation,1)
        self.pheromones = np.delete(self.pheromones, self.currentLocation,0)
        self.pheromones = np.delete(self.pheromones, self.currentLocation,1)
        if self.currentLocation < nextNode: 
            self.currentLocation = nextNode-1
        else:
            self.currentLocation = nextNode
        self.totalTravel += x
        self.townsLeft -= 1 
        return 

    def returnHome(self):
        route = distanceMatrix[self.currentGlobal,0]
        self.totalTravel += route
        self.travelList.append(0)
        return

    def antTour(self):
        while self.townsLeft >= 1:
            self.travelOnce()
        self.returnHome()
        return self.totalTravel, self.travelList

distancePlot = []
bestTour = 0
bestRoute = []
for j in range(maxIter):
    distanceMap = []
    townVists = []
    for i in range(ants):
        i = Ants(pheromoneMatrix, townsLocation, 0, distanceMatrix, towns)
        tourLength, tourList = i.antTour()
        distancePlot.append(tourLength)
        distanceMap.append(tourLength)
        compound = []
        counter = 0
        for i in range(len(tourList)-1): # Collection of routes that were travelled, EG 0:3, 3:4, 4:2 etc
            compound.append(tourList[counter:counter+2])
            counter += 1
        townVists.append(compound)
        if len(bestRoute) == 0:
            bestTour = tourLength
            bestRoute =  tourList
        elif tourLength < bestTour:
            bestTour = tourLength
            bestRoute =  tourList
    pheromoneUpdate(distanceMap, townVists)

print(bestTour)
print(bestRoute)
print(pheromoneMatrix)
plt.plot(distancePlot)
plt.show()