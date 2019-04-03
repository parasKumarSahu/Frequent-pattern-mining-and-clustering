'''
2016CSB1047
PARAS KUMAR
'''
import xml.etree.ElementTree as ET  
import itertools
from collections import defaultdict
import time
import math

# Load data from xml file
def load_data(filename):
	D = []
	Authors = []
	tree = ET.parse(filename)  
	root = tree.getroot()
	for article in root:
		d = []
		for author in article.findall('author'):
			d.append(author.text)
			Authors.append(author.text)
		D.append(set(d))
	Authors = set(Authors)
	return D, Authors

# Hashing L2 values to optimize Apriori algo
def Apriori_optimize(D, Authors):
	i = 1
	L2_approx = defaultdict(int)
	for transaction in D:
		authors = list(transaction)
		for i in range(len(authors)):
			for j in range(i):
				hash_key = authors[i]+authors[j]
				L2_approx[hash_key] += 1

	return L2_approx			 

#Printing frequent itemsets
def print_freq_itemsets(k, Lk):
	print("\nFrequent itemsets of length ", k, "are: ")
	for itemsets in Lk:
		for item in itemsets:
			print(item, end=", ")
		print()	

# Apriori algorithm 
def Apriori(D, Authors, support, output):
	result = {}	
	L1 = defaultdict(int)
	L2_approx = Apriori_optimize(D, Authors)

	for transaction in D:
		for author in transaction:
			L1[author] += 1
	for x in list(L1):
		if L1[x] < support:
			L1.pop(x)

	Lk = L1
	k = 1
	while len(Lk) > 1:
		k += 1
		x = list(Lk.keys())
		Lk = defaultdict(int)
		for i in range(len(x)):
			for j in range(i):
				if type(x[i]) is str:
					hash_key = x[i]+x[j]
					hash_key2 = x[j]+x[i]
					if L2_approx[hash_key] < support and L2_approx[hash_key2] < support:
						continue
					s = {x[i], x[j]}
				else:
					s = set(x[i]).union(set(x[j]))
				if len(s) == k:
					for transaction in D:
						if transaction.issuperset(s):
							Lk[frozenset(s)] += 1

		for x in list(Lk):
			if Lk[x] < support:
				Lk.pop(x)

		if len(Lk) > 0:
			if output:
				print_freq_itemsets(k, Lk)		
			for itemset in Lk:
				result[itemset] = Lk[itemset]

	return result		

#ECLAT algorithm
def ECLAT(D, Authors, support, output):
	result = {}
	L_trans = {}
	trans_id = 0
	for transaction in D:
		trans_id += 1
		for author in transaction:
			if author in L_trans:
				L_trans[author].add(trans_id)
			else:
				L_trans[author] = {trans_id}
	for x in list(L_trans):
		if len(L_trans[x]) < support:
			L_trans.pop(x)

	Lk = L_trans
	k = 1
	while len(Lk) > 1:
		k += 1
		x = list(Lk.keys())
		Lk = defaultdict(int)
		for i in range(len(x)):
			for j in range(i):
				if type(x[i]) is str:
					s = {x[i], x[j]}
				else:
					s = set(x[i]).union(set(x[j]))
				if len(s) == k:
					local_trans = set() 
					for si in s:
						if len(local_trans) == 0:
							local_trans = L_trans[si]
						else:	
							local_trans = local_trans.intersection(L_trans[si])
						if len(local_trans) == 0:
							break
					if len(local_trans) >= support:
						Lk[frozenset(s)] = len(local_trans)

		if len(Lk) > 0:
			if output:
				print_freq_itemsets(k, Lk)		
			for itemset in Lk:
				result[itemset] = Lk[itemset]

	return result		

				
    
if __name__ == "__main__":
	#D = Dataset and Authors = set of authors
	D, Authors = load_data('dblp20888.xml')
	print("Number of transactions:", len(D))
	print("Number of Authors:", len(Authors))
	print()
	print("T1 and T2")
	print("=========")

	support = 0
	while(support < 2):
		support = float(input("Enter min support in percentage: "))
		support = int((support/100)*len(D))
		if support < 2:
			print("Try using a larger min support value")
		if support == 2:
			print("Warning: Apriori may fail for this value if there is not enough memory")	

	print("Min number of occurences allowed = ", support)
	n = int(input("Press 1 to run Apriori or 2 to run ECLAT: "))

	start = time.time()

	if n == 1:
		result = Apriori(D, Authors, support, True)
	else:
		result = ECLAT(D, Authors, support, True)

	print("\nRunning Time:", time.time()-start, "seconds")

	result = ECLAT(D, Authors, support, False)
	print()
	print("T3, T4 and T5")
	print("=============")
	confidence = float(input("Enter confidence threshold in percentage: "))
	larger_sets = {}
	largest_size = 0

	for x in result:
		if len(x) >= 4:
			larger_sets[x] = result[x]
			if len(x) > largest_size:
				largest_size = len(x)

	for x in larger_sets:
		itemsets = []
		for set_size in range(2, largest_size):
			if set_size <= len(x)-2:
				itemsets = itemsets + list(itertools.combinations(set(x), set_size))
		for i in range(len(itemsets)):
			for j in range(len(itemsets)):
				item1 = set(itemsets[i])
				item2 = set(itemsets[j])
				if len(item1.intersection(item2)) == 0:
					if (result[frozenset(x)]*100)/result[frozenset(item1)] >= confidence:
						print(item1, " =>", item2)
						print("Support: ", float(result[frozenset(x)]*100)/len(D), "%")
						print("Confidence: ", 
							(result[frozenset(x)]*100)/result[frozenset(item1)], "%")
						itemLen1Mul2 = result[frozenset(item1)]*result[frozenset(item2)]
						cosine = float(result[frozenset(x)])/math.sqrt(itemLen1Mul2)
						print("Cosine value: ", cosine)
						if cosine < 1:
							print("Negatively Correlated!")
						elif cosine >1:
							print("Positively Correlated!")
						else:
							print("Not Correlated!")	
	
