import torch
import torch.nn as nn
import torch.optim as optim

class MazeNet(nn.Module):
    def __init__(self, input_size):
        super(MazeNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)  # First hidden layer
        self.fc2 = nn.Linear(128, 64)          # Second hidden layer
        self.fc3 = nn.Linear(64, 4)            # Output layer

    def forward(self, x):
        x = torch.relu(self.fc1(x))  # Activation function for hidden layers
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)              # No activation function for output layer
        return x

# Example initialization
input_size = GRID_WIDTH * GRID_HEIGHT  # Assuming a flattened grid representation
model = MazeNet(input_size)

# Loss function and optimizer
loss_function = nn.CrossEntropyLoss()  # Suitable for classification tasks
optimizer = optim.Adam(model.parameters(), lr=0.001)
