from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
np.set_printoptions(threshold=np.inf)
map1 = np.loadtxt("./text.txt", dtype=str) 

for x in range(map1.shape[0]):
	for y in range(map1.shape[1]):
		if map1[x][y] == '1.0':
			flag = False
			for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
				x2 = x + dx
				y2 = y + dy
				if x2 < 0 or x2 > 100 or y2 < 0 or y2 > 100: ## modify boundary
					continue
				if map1[x2][y2] == '1.0':
					flag = True
					break
			if not flag:
				map1[x][y] = '0.0'
				
mapList = []
for x in range(map1.shape[0]):
	for y in range(map1.shape[1]):
		if int(float(map1[x][y])) == 1:
			for i in range (26):
				mapList.append((x-13+i,y-13))
			for i in range (26):
				mapList.append((x+13,y-13+i))
			for i in range (26):
				mapList.append((x+13-i,y+13))
			for i in range (26):
				mapList.append((x-13,y+13-i))
					
#for barrier in mapList:   
#    plt.scatter(barrier[0], barrier[1])
    
class AStarGraph(object):
	#Define a class board like grid with two barriers
 #[(0,3),(0,4),(1,4),(2,4),(2,3),(1,3),(0,3),(5,2),(5,3),(6,3),(7,3),(8,3),(8,2),(7,2),(6,2),(5,2)]
	def __init__(self):
		self.barriers = []
		self.barriers.append(mapList) ## modify to add barrier
	def heuristic(self, start, goal):
		#Use Chebyshev distance heuristic if we can move one square either
		#adjacent or diagonal
		D = 1
		D2 = 1
		dx = abs(start[0] - goal[0])
		dy = abs(start[1] - goal[1])
		return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)
 
	def get_vertex_neighbours(self, pos):
		n = []
		#Moves allow link a chess king
		for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
			x2 = pos[0] + dx
			y2 = pos[1] + dy
			if x2 < 0 or x2 > 100 or y2 < 0 or y2 > 100: ## modify boundary
				continue
			n.append((x2, y2))
		return n
 
	def move_cost(self, a, b):
		for barrier in self.barriers:
			if b in barrier:
				return 100 #Extremely high cost to enter barrier squares
		return 1 #Normal movement cost
 
def AStarSearch(start, end, graph):
 
	G = {} #Actual movement cost to each position from the start position
	F = {} #Estimated movement cost of start to end going via this position
 
	#Initialize starting values
	G[start] = 0 
	F[start] = graph.heuristic(start, end)
 
	closedVertices = set()
	openVertices = set([start])
	cameFrom = {}
 
	while len(openVertices) > 0:
		#Get the vertex in the open list with the lowest F score
		current = None
		currentFscore = None
		for pos in openVertices:
			if current is None or F[pos] < currentFscore:
				currentFscore = F[pos]
				current = pos
 
		#Check if we have reached the goal
		if current == end:
			#Retrace our route backward
			path = [current]
			while current in cameFrom:
				current = cameFrom[current]
				path.append(current)
			path.reverse()
			return path, F[end] #Done!
 
		#Mark the current vertex as closed
		openVertices.remove(current)
		closedVertices.add(current)
 
		#Update scores for vertices near the current position
		for neighbour in graph.get_vertex_neighbours(current):
			if neighbour in closedVertices: 
				continue #We have already processed this node exhaustively
			candidateG = G[current] + graph.move_cost(current, neighbour)
 
			if neighbour not in openVertices:
				openVertices.add(neighbour) #Discovered a new vertex
			elif candidateG >= G[neighbour]:
				continue #This G score is worse than previously found
 
			#Adopt this G score
			cameFrom[neighbour] = current
			G[neighbour] = candidateG
			H = graph.heuristic(neighbour, end)
			F[neighbour] = G[neighbour] + H
 
	raise RuntimeError("A* failed to find a solution")
 
if __name__=="__main__":
    graph = AStarGraph()
    result, cost = AStarSearch((100,50), (4,90), graph) # setup starting point
    print ("route", result)
    print ("cost", cost)
    plt.plot([v[0] for v in result], [v[1] for v in result])
    for barrier in graph.barriers:
        plt.plot([v[0] for v in barrier], [v[1] for v in barrier])
    #plt.xlim(-1,8)
    #plt.ylim(-1,8)
    plt.savefig('findpath.png')
    plt.show()




