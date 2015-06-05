import numpy as np 
import scipy as sp
from sklearn.feature_extraction import DictVectorizer
from sklearn.preprocessing import normalize 

import json, sys 

np.set_printoptions(threshold=1e9)


""" basic implementation of kmeans:
create MATRIX M: (370 x 30000)   [= (MP x Words), say] 
let CENTROIDS be C: (k x 30000)   [k= centroid no]

to find distances:
    - C.dot(M.transpose) gives effective distances = D (k x 370) 
    - then find largest & take column index to cluster.
to find mean of cluster:
    - take rows in cluster (normalized) & generate from this

when cluster and centroids not changing finish algo.
"""


def naive_clustering(filename):
    """perform kmeans clustering on a single assimilated frequency json file. 
output to json for d3 visual exploration"""
    
    k = 2

    dv = DictVectorizer(sparse=True)
    
    with open(filename, 'r') as f:
        raw = json.load(f)
        MPnames, MPrawdata = [],[]
        
        for MP in raw:
            MPnames.append(MP)
            MPrawdata.append(raw[MP])

    sparse_array = dv.fit_transform(MPrawdata)
    data_points = sparse_array #should this be normalized? hashtag ratios or absolute?
    
    mp_no , dim = data_points.get_shape()

    initial_centroids = normalize(sp.sparse.rand(dim, k , density=0.1), axis=0)
    centroids = initial_centroids.tocsc()

    count, clusters = 0, []
    

    while count < 3: 
        old_clusters = clusters

        distances = kmeans_find_distance(data_points, centroids)
        clusters = kmeans_find_cluster(distances)
        centroids = kmeans_find_centroid(data_points, clusters, k)

        if old_clusters == clusters: #no convergence with centroids?
            count +=1

    #note: no averages done yet
    def print_json():
         
        with open('data_analysis_vis/kmeans_naive.json', 'w+') as f:
            f.write(json.dumps(  [{'name':MP, 'cluster': clusters[i]} for i, MP in enumerate(MPnames) ] ) )
    
    print_json()


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
    
    print centroid_list

    C = sp.sparse.vstack(centroid_list).transpose()
    C = np.round(C, decimals=5)
    return C



if __name__ == '__main__':
    if sys.argv[1] == 'naive_cluster':
        naive_clustering(sys.argv[2])
    else:
        print 'arguments error'

