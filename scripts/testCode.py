import numpy as np
import torch
from torch_geometric.utils import dense_to_sparse
import pandas as pd
import math
import matplotlib.pyplot as plt
# adj_mat = np.load('C:\\Users\\rodubey\\Downloads\\METR-LA\\adj_mat.npy')
# adj_mat = torch.from_numpy(adj_mat)
# print(len(adj_mat[0]))
# edge_indices, values = dense_to_sparse(adj_mat)
# edge_indices = edge_indices.numpy()
# edge_weights  = values.numpy()
# np.savetxt("test.csv", adj_mat, delimiter=",")

# print(len(edge_indices[0]))
# print(len(edge_weights))
# print(edge_indices.shape)
# print(edge_weights.shape)
# node_values = np.load('C:\\Users\\rodubey\\Downloads\\METR-LA\\node_values.npy')
# # print((node_values.shape))
# print(node_values[0, 0, :])
# print(node_values[289, 0, :])
# print(node_values[1, 0, :])
# print(node_values[2, 0, :])
# print(node_values[3, 0, :])
# print(node_values[4, 0, :])
# print(node_values[34270, 0, :])
# print(node_values[34271, 0, :])

# plt.plot(node_values[:,0,1])
# plt.show()
# df = pd.read_hdf('C:\\Users\\rodubey\\Downloads\\METR-LA\\metr-la.h5')
# print(df.shape)
# print(df.iloc[0])
# # print(df.iloc[287])
# # print(node_values[1, :])
# # print(node_values[2, :])
# # print(node_values[34270, :])
# print(df.iloc[-1])
# np.savetxt("nodeFeatures.csv", node_values, delimiter=",")

#timestamp per day = 24*12 = 288 Data recorded every 5 minutes
#four months = 119 days after cleaning. Therefore the len of node_values is 34272 . Features (Speed, and time)
# 288*280,8
#node_features = []
# node_features = np.zeros((288,280,8))

# mean = 100
# # print(math.exp(-(100/(4*mean))))
# # print(math.exp(-(200/(4*mean))))
# # print(math.exp(-(100/(2*mean))))

# print(math.exp(-math.sqrt(4*100/mean)))
# print(math.exp(-math.sqrt(4*200/mean)))
# print(math.exp(-math.sqrt(2*100/mean)))
# data = np.genfromtxt('..\\dataset\\adj.csv', delimiter=',')
# np.save('..\\dataset\\adj.npy', data)

node_values = np.load('..\\dataset\\nodeFeatures.npy')
rrReshaped = node_values.reshape(node_values.shape[0], -1)
# saving reshaped array to file.
np.savetxt("test.csv", rrReshaped, delimiter=",")
print((node_values.shape))
print(node_values[60, :, :])
