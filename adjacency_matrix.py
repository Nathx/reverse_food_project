
# coding: utf-8

# In[168]:

import numpy as np
import pymongo
import cPickle
import scipy.sparse as sps

# In[86]:

def extract_adj_mat(rec_db, ing_db):
    
    n_rec = rec_db.count()
    n_ing = ing_db.count()
    url_ings = np.sort([ing for ing in rec_db.distinct('ingredients') if ing.find('food.com/about/') > -1])
    url_recs = np.sort([rec['url'] for rec in rec_db.find({}, {'url':1})])
    adj_mat = np.zeros((n_ing, n_rec))

    for i, rec in enumerate(rec_db.find()):
        if i%5000 == 0:
            print round(i*100.0/n_rec, 2) ,'%'
        if float(rec['rating']) > 0:
            ings = rec['ingredients']
            col = np.where(url_recs==rec['url'])[0]
            rows = np.where(np.in1d(url_ings, ings))[0]
            adj_mat[rows, col] = rec['rating']
        
    return adj_mat 
    

if __name__ == '__main__':
    
    client = pymongo.MongoClient()
    db = client.reverse_food
    rec_db = db.recipes
    ing_db = db.ingredients
    adj_mat = extract_adj_mat(rec_db, ing_db)
    
    adj_mat_csc = sps.csc_matrix(adj_mat)
    with open('adj_mat.pick', 'w') as matfile:
        cPickle.dump(adj_mat_csc, matfile)


