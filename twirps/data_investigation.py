import numpy as np 
import scipy as sp
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import normalize 

import json, sys , sets

np.set_printoptions(threshold=1e9)


""" basic implementation of kmeans:
create MATRIX M: (370 x 30000)   [= (MP x Words), say] 
let CENTROIDS be C: (30000 x k)   [k= centroid no]

to find distances:
    - M.dot(C) gives effective distances = D (k x 370) (both M, C NORMALIZED) 
    - then find largest & take column index to cluster.
to find mean of cluster:
    - take rows in cluster (normalized) & generate from this

when cluster and centroids not changing finish algo.

finally: run multiple times, and find ratio of sumsquare distances
"""


def naive_clustering(filename, k):
    """perform kmeans clustering on a single assimilated frequency json file. 
output to json for d3 visual exploration"""

    dv = DictVectorizer(sparse=True)
    
    with open(filename, 'r') as f:
        raw = json.load(f)
        MPnames, MPrawdata = [],[]
        
        for MP in raw:
            MPnames.append(MP)
            MPrawdata.append(raw[MP])

    sparse_array = dv.fit_transform(MPrawdata)
    data_points = normalize(sparse_array, axis=1) #should this be normalized? hashtag ratios or absolute?
    
    mp_no , dim = data_points.get_shape()

    initial_centroids = normalize(sp.sparse.rand(dim, k , density=0.1), axis=0)
    centroids = initial_centroids.tocsc()

    count, clusters = 0, []
    

    while old_clusters != clusters: 
        old_clusters = clusters

        distances = kmeans_find_distance(data_points, centroids)
        clusters = kmeans_find_cluster(distances)
        centroids = kmeans_find_centroid(data_points, clusters, k)
    
    variance_ratio = kmeans_find_variance_ratio(distances, clusters, data_points)

    result = { MP:{'cluster': clusters[i]} for i, MP in enumerate(MPnames) }
    return (variance_ratio, result)
    #print_json(result)


def kmeans_find_distance(M,C):
    """Return a matrix with distance of each datapoint (matrix M) from each centroid (matrix C)"""
    return M.dot(C)
    

def kmeans_find_cluster(D):
    """Return a list assigning each twirp (a row in data matrix), to a cluster"""
    i = 0
    cluster = []
    while i < D.get_shape()[0]:
        row = D.getrow(i).todense()
        cluster.append(np.argmax(row))  
        i+=1
    return cluster

def kmeans_find_centroid(M, clusters, k):
    """Return a matrix of centroids (as columns)"""
    i = 0
    clust_indices = []
    centroid_list = []
    
    while i< k:
        clust_array = np.array(clusters)
        clust_indices = np.where( clust_array == i )[0]

        A = M[clust_indices] #matrix of clusters
        centroid_list.append(sp.sparse.csr_matrix(A.mean(axis=0)))
        i+=1
    
    #print centroid_list

    C = sp.sparse.vstack(centroid_list).transpose()
    C = np.round(C, decimals=5)
    return C

def kmeans_find_variance_ratio(distances, clusters, M):
    """Return the sum of sumsquares of cosine distances within clusters, 
compared to overall sumsquare of cosine distances"""
    internal_variance = 0 
    
    for i, c in enumerate(clusters):
        internal_variance += (distances[i, c])**2

    #find total variance compared to mean by running for 1 centroid   
    single_centroid = kmeans_find_centroid(M, [0]*len(clusters), 1 )
    single_dist = kmeans_find_distance(M, single_centroid)

    total_var = sum(map(lambda x:x**2, single_dist))
    
    print internal_variance/total_var[0,0]
    return internal_variance/total_var[0,0]


def print_json(results, title):
    "add archipelago & twirp info to results, and write full results to JSON"
    with open('data_analysis_vis/basic_info.json', 'r+') as b:
        basix = json.load(b)

    for i,data in enumerate(basix):
        if data['handle'] in results.keys():
            data.update(results[data['handle']])

    with open('data_analysis_vis/kmeans_%s.json'%title, 'w+') as f:
        f.write(json.dumps(basix))

# def identify_clusters(setdictA, setdictB):
#     """return correspondingly equivalent cluster numbers between two different clustering results"""
#     mapping = {}
#     #print type(setdictA), type(setdictA[1])
#     for setA in setdictA:
#         overlap = []
#         correspondence = {}
#         for setB in setdictB:
#             if len(setdictB[setB] & setdictA[setA]) > len(overlap):
#                 overlap = (setdictB[setB] & setdictA[setA])
#                 correspondence = {setA: setB}
#                 #print correspondence, overlap
#         mapping.update(correspondence)
#     return mapping


def run_multiple_clusterings(filename, N, k, title):
    """run kmeans on given file, N times and print averages to JSON"""
    best_ratio = 0
    for i in range(N):
        print i, 
        var_ratio, results = naive_clustering(filename, k)
        if var_ratio > best_ratio:
            best_ratio = var_ratio
            final_results = results

    title = title+ str(best_ratio).replace('.','_')
    print_json(final_results, title)
    print best_ratio



if __name__ == '__main__':
    if sys.argv[1] == 'naive_cluster':
        run_multiple_clusterings(sys.argv[2], 50, int(sys.argv[3]), sys.argv[4])
    else:
        print 'arguments error'

