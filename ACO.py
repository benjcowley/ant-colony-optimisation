import numpy as np
from scipy.spatial import distance_matrix
from matplotlib import pyplot as plt

townsLocation = np.array([[-0.0000000400893815, 0.0000000358808126],[-28.8732862244731230, -0.0000008724121069],[-79.2915791686897506, 21.4033307581457670],[-14.6577381710829471, 43.3895496964974043],[-64.7472605264735108, -21.8981713360336698],[-29.0584693142401171, 43.2167287683090606],[-72.0785319657452987, -0.1815834632498404],[-36.0366489745023770, 21.6135482886620949],[-50.4808382862985496, -7.3744722432402208],[-50.5859026832315024, 21.5881966132975371],[-0.1358203773809326, 28.7292896751977480],[-65.0865638413727368, 36.0624693073746769],[-21.4983260706612533, -7.3194159498090388],[-57.5687244704708050, 43.2505562436354225],[-43.0700258454450875, -14.5548396888330487]])
towns = len(townsLocation)
maxIter = 100
ants = 17
pInfluence = 35 # Too low and we run into exploration only, too high and cover the same paths
dInfluence = 36 # Too low and we run into a greedy search, too high and the search stagnates
pheromonePotentency = 1
pheromoneEvaporation = 0.5
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
    distanceRangeIndex = np.arange(len(distanceRange))
    pheromoneRange = np.delete(pheromoneRange, currentLocation)
    visitbility = np.reciprocal(distanceRange, where=distanceRange>0) # inverse probability
    vfunc = np.vectorize(selectorEquation) 
    totals = vfunc(pheromoneRange, visitbility) 
    probability = np.array(proabilityEquation(totals)).astype(float) # List of all probabilites based of travelling to each availible route.
    outcome = np.random.choice(distanceRangeIndex,1, p=probability) # Random Number Generator to select next node.
    if outcome >= currentLocation:
        outcome += 1
    return outcome # All we're returning here is one selection from the slice

def pheromoneUpdate(distancePlot, townVists):
    global pheromoneMatrix, pheromoneEvaporation, pheromonePotentency
    pheromone2 = np.ones_like(pheromoneMatrix).astype(float)
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
        route = distanceMatrix[self.currentGlobal,0] # Travel from the last location, back to the starting node
        self.totalTravel += route
        self.travelList.append(0)
        return

    def antTour(self):
        while self.townsLeft >= 1:
            self.travelOnce()
        self.returnHome()
        return self.totalTravel, self.travelList

def completeTour():
    distancePlot = []
    bestTourPlot = []
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
    plt.plot(distancePlot)
    plt.show()
    return

if __name__ == "__main__":
	completeTour()