import numpy as np
import torch
from torch_geometric.utils import dense_to_sparse

# adj_mat = np.load('C:\\Users\\rodubey\\Downloads\\METR-LA\\adj_mat.npy')
# print(len(adj_mat))
# adj_mat = torch.from_numpy(adj_mat)
# edge_indices, values = dense_to_sparse(adj_mat)
# edge_indices = edge_indices.numpy()
# edge_weights  = values.numpy()

# print(edge_indices[0])
# print(len(edge_weights))
# print(edge_indices.shape)
# print(edge_weights.shape)
# node_values = np.load('C:\\Users\\rodubey\\Downloads\\METR-LA\\node_values.npy')
# print((node_values.shape))
# print((node_values[5000]))
# print(node_values[1, :])

#timestamp per day = 24*(60/12) = 288 Data recorded every 5 minutes
#four months = 119 days after cleaning. Therefore the len of node_values is 34272 . Features (Speed, and time)

