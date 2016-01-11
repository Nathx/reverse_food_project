
# coding: utf-8

# In[168]:

import numpy as np
import multiprocessing as mp
import json
import pymongo

# In[86]:

def extract_adj_mat(data, split=True):
    """
    Returns matrix with size (number of parts)*(number of claims).
    M[i,j] = 1 if part i in claim j
           = 0 otherwise.
    If split is true, duplicates the parts to treat repair and replace
    operations separately.
    """
    part_counts = get_part_count(data)

    n_claims = np.sum(part_counts.values())
    n_parts = len(part_counts.keys())
    output = np.zeros(((1+int(split))*n_parts, n_claims), dtype=bool)
    c = 0

    for j, claim in enumerate(data.itervalues()):
        if j % 10000 == 0:
            print "{0}k claims, {1} subparts processed.".format(j/1000, c)
        for part in claim["Parts"].keys():
            try:
                i = part_counts.keys().index(part)
            except:
                continue

            if split:
                method = claim["Parts"][part]["Method"]
                if method == 'Repair':
                    i += n_parts
            output[i, j] = 1
            c += 1

    keys = np.array(data.keys())[np.sum(output, axis=0).astype(bool)]
    output = output[:,np.sum(output, axis=0).astype(bool)]
    return output, keys



def get_part_count(data):
    """Extract ingredient and recipes indexes."""
    all_parts = {}
    total=len(data.keys())
    for i,item in enumerate(data.keys()):
        for part in data[item]['Parts']:
            if part.find("Other") == -1:
                try:
                    all_parts[part]+=1
                except KeyError:
                    all_parts[part]=1

    return all_parts
    

if __name__ == '__main__':
    split = True
    data = load_data('../data/data_cleaned.json')
    adj_mat, catalog = extract_adj_mat(data, split)
    if split:
        fn = 'data/adj_mat_split.pick'
    else:
        fn = 'data/adj_mat.pick'
    with open(fn, 'w') as matfile:
        cPickle.dump(adj_mat, matfile)
    with open('claim_catalog.pick', 'w') as key_file:
        cPickle.dump(catalog, key_file)


