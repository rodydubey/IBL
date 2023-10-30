import os
import urllib
import zipfile
import numpy as np
import torch
from torch_geometric.utils import dense_to_sparse
from torch_geometric_temporal.signal import StaticGraphTemporalSignal


class dataloader(object):
 
    def __init__(self, raw_data_dir=os.path.join(os.getcwd(), 'dataset\\')):
        super(dataloader, self).__init__()
        self.raw_data_dir = raw_data_dir
        self._read_data()

    def _read_data(self):      
        A = np.load(os.path.join(self.raw_data_dir, "adj_large.npy"))
        adj_mat = torch.from_numpy(A)
        # adj_mat[np.isnan(adj_mat)] = 0
        print(len(adj_mat[0]))

        node_feature = np.load(os.path.join(self.raw_data_dir, "node_values_20_Days.npy"))
        # node_feature[np.isnan(node_feature)] = 0
        # node_feature = node_feature[:,:,:-1]
        X = node_feature.transpose((1, 2, 0))
      
        
        X = X.astype(np.float32)

        #Normalise as in DCRNN paper (via Z-Score Method)
        means = np.mean(X, axis=(0, 2))
        X = X - means.reshape(1, -1, 1)
        stds = np.std(X, axis=(0, 2))
        X = X / stds.reshape(1, -1, 1)

        self.A = torch.from_numpy(A)
        self.X = torch.from_numpy(X)

    def _get_edges_and_weights(self):
        edge_indices, values = dense_to_sparse(self.A)
        edge_indices = edge_indices.numpy()
        values = values.numpy()
        self.edges = edge_indices
        self.edge_weights = values

    def _generate_task(self, num_timesteps_in: int = 4, num_timesteps_out: int = 4):
        """Uses the node features of the graph and generates a feature/target
        relationship of the shape
        (num_nodes, num_node_features, num_timesteps_in) -> (num_nodes, num_timesteps_out)
        predicting the average traffic speed using num_timesteps_in to predict the
        traffic conditions in the next num_timesteps_out

        Args:
            num_timesteps_in (int): number of timesteps the sequence model sees
            num_timesteps_out (int): number of timesteps the sequence model has to predict
        """
        indices = [
            (i, i + (num_timesteps_in + num_timesteps_out))
            for i in range(self.X.shape[2] - (num_timesteps_in + num_timesteps_out) + 1)
        ]

        # Generate observations
        features, target = [], []
        print(self.X.shape)
        for i, j in indices:
            features.append((self.X[:, :, i : i + num_timesteps_in]).numpy())
            target.append((self.X[:, 2, i + num_timesteps_in : j]).numpy())

        self.features = features
        self.targets = target
        # print(features)

    def get_dataset(
            self, num_timesteps_in: int = 4, num_timesteps_out: int = 4
        ) -> StaticGraphTemporalSignal:
            """Returns data iterator for dataset as an instance of the
            static graph temporal signal class.

            Return types:
                * **dataset** *(StaticGraphTemporalSignal)* - The traffic
                    forecasting dataset.
            """
            self._get_edges_and_weights()
            self._generate_task(num_timesteps_in, num_timesteps_out)
            dataset = StaticGraphTemporalSignal(
                self.edges, self.edge_weights, self.features, self.targets
            )

            return dataset