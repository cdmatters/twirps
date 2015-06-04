import numpy as np 
from sklearn.feature_extraction import DictVectorizer
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
output to .csv"""


    dv = DictVectorizer(sparse=True)

    MPnames = []
    MPdata = []

    with open(filename, 'r') as f:
        raw = json.load(f)

        for MP in raw:
            MPnames.append(MP)
            MPdata.append(raw[MP])

    sparse_array = dv.fit_transform(MPdata)

    print sparse_array.get_shape()

        
        


if __name__ == '__main__':
    if sys.argv[1] == 'naive_cluster':
        naive_clustering(sys.argv[2])
    else:
        print 'arguments error'

