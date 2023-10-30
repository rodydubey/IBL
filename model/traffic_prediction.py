import torch
import numpy as np
from DatasetLoader import dataloader
from torch_geometric_temporal.signal import StaticGraphTemporalSignal
import seaborn as sns
import matplotlib.pyplot as plt 
from TemporalGNN import TemporalGNN
loader = dataloader()
num_timesteps = 4
dataset = loader.get_dataset(num_timesteps_in=num_timesteps, num_timesteps_out=num_timesteps)
print("Dataset type:  ", dataset)
# print("Number of samples / sequences: ",  len(set(dataset)))
print(next(iter(dataset)))


# # Visualize traffic over time
# sensor_number = 1
# hours = 24
# sensor_labels = [bucket.y[sensor_number][0].item() for bucket in list(dataset)[:hours]]
# sns.lineplot(data=sensor_labels)
# plt.show()

from torch_geometric_temporal.signal import temporal_signal_split
train_dataset, test_dataset = temporal_signal_split(dataset, train_ratio=0.8)

# # print("Number of train buckets: ", len(set(train_dataset)))
# # print("Number of test buckets: ", len(set(test_dataset)))
# # GPU support
device = torch.device('cpu') # cuda
subset = 2000

# Create model and optimizers
model = TemporalGNN(node_features=5, periods=num_timesteps).to(device)
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
model.train()

print("Running training...")
for epoch in range(500): 
    loss = 0
    step = 0
    for snapshot in train_dataset:
        snapshot = snapshot.to(device)
        # Get model predictions
        y_hat = model(snapshot.x, snapshot.edge_index)
        # Mean squared error
        loss = loss + torch.mean((y_hat-snapshot.y)**2) 
        step += 1
        if step > subset:
          break

    loss = loss / (step + 1)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
    print("Epoch {} train MSE: {:.4f}".format(epoch, loss.item()))
    if epoch%10 == 0:
        PATH = "trained_model/state_dict_model_" + str(epoch) + ".pt"
        figName = "trained_model/results/test_result_" + str(epoch) + ".png"
        torch.save(model.state_dict(), PATH)

        # perform the test
        model.eval()
        loss = 0
        step = 0
        horizon = num_timesteps*24

        # Store for analysis
        predictions = []
        labels = []

        for snapshot in test_dataset:
            snapshot = snapshot.to(device)
            # Get predictions
            y_hat = model(snapshot.x, snapshot.edge_index)
            # Mean squared error
            loss = loss + torch.mean((y_hat-snapshot.y)**2)
            # Store for analysis below
            labels.append(snapshot.y)
            predictions.append(y_hat)
            step += 1
            if step > horizon:
                break

        loss = loss / (step+1)
        loss = loss.item()
        print("Test MSE: {:.4f}".format(loss))

        sensor = 20  
        timestep = 1 
        preds = np.asarray([pred[sensor][timestep].detach().cpu().numpy() for pred in predictions])
        labs  = np.asarray([label[sensor][timestep].cpu().numpy() for label in labels])

        plt.figure(figsize=(20,5))
        sns.lineplot(data=preds, label="pred")
        sns.lineplot(data=labs, label="true")
        plt.savefig(figName)