#2016csb1047
#Paras Kumar
#Assignment-3

import matplotlib.pyplot as plt
import random as rnd
import math 
from collections import defaultdict
from collections import OrderedDict
import operator

#List of user ids
User_ids = []
#List of latitudes
Latitudes = []
#List of longitudes
Longitudes = []

#Load data for a given id, sampling = 0 for no loss
#Sampling used only in Task-6
def load_data(id, sampling):
	User_ids.clear()
	Latitudes.clear()
	Longitudes.clear()
	print("Reading data, please wait...")
	f = open("Brightkite_totalCheckins.txt")
	for i in f:
		l = i.split()
		if len(l) == 5 and rnd.randint(0, sampling) == 0:
			if id == -1 or  id == int(l[0]):
				User_ids.append(int(l[0]))
				Latitudes.append(float(l[2]))		
				Longitudes.append(float(l[3]))		
	print(len(User_ids), "entries read from the file Brightkite_totalCheckins.txt")	

def plot_graph(title, x, y):
	plt.title(title)
	plt.scatter(x, y)
	plt.xlabel("Latitudes")
	plt.ylabel("Longitudes")

#Used by K-means()
def centroid(Cluster):
	x = 0
	y = 0
	for i in Cluster:
		x += Latitudes[i]
		y += Longitudes[i]
	return x/len(Cluster), y/len(Cluster)	  

def Kmeans(k):
	print("Running K-means with k =", k)
	centroids_lat = []
	centroids_long = []
	clusters = []
	dist_from_clusters = []

	for i in range(k):
		clusters.append([])
		rn = rnd.randint(int(len(User_ids)*i/k), int(len(User_ids)*(i+1)/k))
		centroids_lat.append(Latitudes[rn])
		centroids_long.append(Longitudes[rn])
		dist_from_clusters.append(9999.9999)

	for it in range(10):
		for i in range(k):
			clusters[i].clear()
		for i in range(len(User_ids)):
			for j in range(k):
				dist_from_clusters[j] = math.sqrt( (centroids_lat[j]-Latitudes[i])**2 
					+ (centroids_long[j]-Longitudes[i])**2)
			min_index = dist_from_clusters.index(min(dist_from_clusters))
			clusters[min_index].append(i)	
		for i in range(k):
			if len(clusters[i]) > 0:
				centroids_lat[i], centroids_long[i] = centroid(clusters[i])
	for i in range(k):		
		plot_graph("K-means "+"K = "+str(k), 
			[Latitudes[k] for k in clusters[i]],
			[Longitudes[k] for k in clusters[i]])
	plt.savefig("T2/K="+str(k)+".png")
	plt.close()
	print("Figure T2/K="+str(k)+".png saved!")	

#Used by DBSCAN()
def neighbourhood_points(n, epsilon):
	points = []
	for i in range(len(User_ids)):
		if i != n:
			if epsilon >= math.sqrt( (Latitudes[n]-Latitudes[i])**2
				+ (Longitudes[n]-Longitudes[i])**2 ):
				points.append(i)
	return points			

def DBSCAN(epsilon, min_points, diff_dir):
	print("Running DBSCAN with epsilon=", epsilon, " min_points=", min_points)
	visited = [0 for i in range(len(User_ids))]
	noise = []
	for i in range(len(visited)):
		if visited[i] == 0:
			points = neighbourhood_points(i, epsilon)
			if len(points) < min_points:
				visited[i] = -1
				noise.append(i)
			else:
				cluster = []
				for j in range(len(points)):
					if visited[points[j]] == 0:
						visited[points[j]] = 1
						points2 = neighbourhood_points(points[j], epsilon)
						if len(points2) >= min_points:
							points = points + points2
					if	visited[points[j]] == 1:
						visited[points[j]] = 2
						cluster.append(points[j])							
				plot_graph("DBSCAN epsilon = "+str(epsilon)+" min_points = "
					+str(min_points), [Latitudes[k] for k in cluster],
					[Longitudes[k] for k in cluster])
	if diff_dir == -1:		
		plt.savefig("T3/eps="+str(epsilon)+"minPts="+str(min_points)+".png")
		plt.close()
		print("figure","T3/eps="+str(epsilon)+"minPts="+str(min_points)+".png", "saved!")		
	else:
		plt.savefig("T6/user_id"+str(diff_dir)+".png")
		plt.close()
		print("figure","T6/user_id"+str(diff_dir)+".png", "saved!")		

#Used by AGENES()
def AGENES_linkage(linkage_type, dist_matrix):
	if linkage_type == "single":
		min_row_index = -1
		min_col_index = -1
		min_val = 99999
		for i in range(len(dist_matrix)):
			for j in range(len(dist_matrix)):
				if i!=j and min_val > dist_matrix[i][j]:
					min_val = dist_matrix[i][j]
					min_row_index = i
					min_col_index = j
		return min_row_index, min_col_index, min_val
	else:			
		max_row_index = -1
		max_col_index = -1
		max_val = -1
		for i in range(len(dist_matrix)):
			for j in range(len(dist_matrix)):
				if i!=j and max_val < dist_matrix[i][j]:
					max_val = dist_matrix[i][j]
					max_row_index = i
					max_col_index = j
		return max_row_index, max_col_index, max_val

def AGENES(threshold, linkage_type):
	print("Running", linkage_type, "link agglomerative clustering threshold=", threshold)
	clusters = []
	for i in range(len(User_ids)):
		tmp = set()
		tmp.add(i)
		clusters.append(tmp)
	dist_matrix = []
	for i in range(len(User_ids)):
		l = []
		for j in range(len(User_ids)):
			l.append( math.sqrt( (Latitudes[i]-Latitudes[j])**2
		    	+ (Longitudes[i]-Longitudes[j])**2 ) )
		dist_matrix.append(l)	
	while len(clusters) > 1:
		row_index, col_index, val = AGENES_linkage(linkage_type, dist_matrix)
		if (val > threshold and linkage_type == "single") or (val < threshold and linkage_type == "complete" ):
			for i in clusters:
				plot_graph("AGENES "+linkage_type+" threshold="+str(threshold), 
					[Latitudes[k] for k in i],
					[Longitudes[k] for k in i])
			plt.savefig("T5/"+linkage_type+"-threshold"+str(threshold)+".png")	
			plt.close()
			print("T5/"+linkage_type+"-threshold"+str(threshold), "saved!")
			break
		a = min(row_index, col_index)
		b = max(row_index, col_index)
		clusters[a] = clusters[a].union(clusters[b])
		del clusters[b]	
		for i in range(len(dist_matrix[a])):
			if linkage_type == "single":
				dist_matrix[a][i] = min(dist_matrix[a][i], dist_matrix[b][i])
			else:
				dist_matrix[a][i] = max(dist_matrix[a][i], dist_matrix[b][i])
		del dist_matrix[b]		
		for i in range(len(dist_matrix)):
			if linkage_type == "single":
				dist_matrix[i][a] = min(dist_matrix[i][a], dist_matrix[i][b]) 		
			else:
				dist_matrix[i][a] = max(dist_matrix[i][a], dist_matrix[i][b])
			del dist_matrix[i][b]		 		

#Code of task-6 in a seperate function						
def Task6(ref_id):
	load_data(-1, 5)
	Dictionary = defaultdict(list)
	Dictionary2 = {}
	for i in range(len(User_ids)):
		Dictionary[User_ids[i]].append(i)
	for i in Dictionary:
		sum_dist = 0
		if i != ref_id:
			for j in Dictionary[i]:
				for k in Dictionary[ref_id]:
					sum_dist += math.sqrt( (Latitudes[j]-Latitudes[k])**2
						+ (Longitudes[j]-Longitudes[k])**2 )
			Dictionary2[i] = sum_dist/len(Dictionary[i])
	sorted_x = sorted(Dictionary2.items(), key=operator.itemgetter(1))
	Dictionary2 = OrderedDict(sorted_x)
	closest_5 = []
	count = 0
	for i in Dictionary2:
		count += 1
		closest_5.append(i)
		if count == 5:
			break
	for i in closest_5:
		load_data(i, 0)
		plot_graph("ID="+str(i)+" Distance="+str(Dictionary2[i])
			+" (Top 5 closest to "+str(ref_id)+")",
			Latitudes, Longitudes)
		DBSCAN(0.1, 10, i)			




##############################################################################
#Main function

load_data(7611, 0)

print("T2")
print("===")
for i in range(2, 7):
	Kmeans(i)
print("T3")
print("===")
DBSCAN(0.01, 10, -1)
DBSCAN(0.1, 10, -1)
DBSCAN(1, 10, -1)
DBSCAN(0.1, 2, -1)
DBSCAN(0.1, 100, -1)

print("T5")
print("===")
AGENES(10, "single")
AGENES(1, "single") 
AGENES(0.2, "single") 
AGENES(0.3, "single") 

AGENES(51, "complete")
AGENES(52, "complete")
AGENES(52.5, "complete")
AGENES(53.3, "complete")

print("T6")
print("===")
Task6(7611)
