
# coding: utf-8

# In[1]:

import cPickle
import numpy as np
import multiprocessing as mp
import sys
from datetime import datetime

# In[57]:

def prob_vector(i, c=0.15, epsilon=0.5):
    """Probability vector for part i as defined in NF_exact."""
    n_adj_cols, n_adj_rows = adj_mat_normed
    k, n = n_adj_cols.shape
    q = np.zeros(k + n)
    q[i] = 1
    
    u = c*q
    delta = 1
    
    while delta > epsilon:
        u_next = (1-c)*np.concatenate((np.dot(n_adj_cols, u[k:]), np.dot(n_adj_rows, u[:k])))+c*q
        delta = np.linalg.norm(u_next - u, ord=1)
        u = u_next
        
    return u[:k]

def enum_prob_vector(i, c=0.15, epsilon=0.5):
    """Vector with index to retrieve order after async apply."""
    n_adj_cols, n_adj_rows = adj_mat_normed
    k, n = n_adj_cols.shape
    qc = np.zeros(k + n)
    qc[i] = c
    
    u = qc
    delta = 1
    
    while delta > epsilon:
        u_next = (1-c)*np.concatenate((np.dot(n_adj_cols, u[k:]), np.dot(n_adj_rows, u[:k]))) + qc
        delta = np.linalg.norm(u_next - u, ord=1)
        u = u_next
    
    return i, u[:k]

def prob_vector_wrapper(args):
    """Wrapper to pass to map function."""
    return prob_vector(*args)


# In[117]:

def col_norm(mat):
    """Norming matrix so that all columns sum to 1 (norm |x|).
    """
    norms = np.linalg.norm(mat, axis=0, ord=1).astype(float)
    normed_mat = np.nan_to_num(np.divide(mat, norms))
    return normed_mat

def calc_col_norm(adj_mat):
    """Norming adjacency matrix and it's transpose.
    """
    n_adj_cols = col_norm(adj_mat)
    n_adj_rows = col_norm(adj_mat.T)
    return n_adj_cols, n_adj_rows

# In[185]:

def relevance_matrix(n_parts=0, c=0.15, epsilon=.01, method='apply_async'):
    """
    Calculating relevance scores part-to-part.
    Testing different parallel methods.
    Results in comments underneath.

    """
    # try if adj_mat_normed is defined
    try:
        n_adj_cols, n_adj_rows = adj_mat_normed
    except:
        global adj_mat_normed
        adj_mat_normed = calc_col_norm(adj_mat)
        n_adj_cols, n_adj_rows = adj_mat_normed

    if n_parts == 0:
        n_parts = n_adj_cols.shape[0]
    
    rel_mat = np.zeros((n_parts, n_parts))

    
    pool = mp.Pool(processes=20)
    args = [(i, c, epsilon) for i in xrange(n_parts)]
    if method == 'map':
        result = pool.map(prob_vector_wrapper, args)
        pool.close()
        rel_mat = np.matrix(result).T
    
    elif method == 'map_async':
        result = pool.map_async(prob_vector_wrapper, args)
        pool.close()
        pool.join()
        rel_mat = np.matrix(result.get()).T


    elif method == 'apply_async':
        result = [pool.apply_async(enum_prob_vector, args=(i, c, epsilon)) for i in xrange(n_parts)]
        pool.close()
        pool.join()
        
        for p in result:
            i, u = p.get()
            rel_mat[:,i] = u
        rel_mat = np.matrix(rel_mat)
        
    return rel_mat



# relevance_matrix(50,method='map')
# CPU times: user 106 ms, sys: 828 ms, total: 934 ms
# Wall time: 1min 30s
# relevance_matrix(50,method='map_async')
# CPU times: user 106 ms, sys: 837 ms, total: 943 ms
# Wall time: 1min 29s
# relevance_matrix(50,method='apply_async')
# CPU times: user 82.4 ms, sys: 1.11 s, total: 1.19 s
# Wall time: 1min 24s


if __name__ == '__main__':
    # Calculating relevance matrix

    adj_fn = 'data/adj_mat.pick'
    with open(adj_fn) as matfile:
        adj_mat = cPickle.load(matfile)

    global adj_mat_normed
    adj_mat_normed = calc_col_norm(adj_mat)

    rel_mat = relevance_matrix()
    rel_fn = 'data/rel_mat.pick'
    with open(rel_fn, 'w') as relfile:
        cPickle.dump(rel_mat, relfile)





