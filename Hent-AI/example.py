import torch
import torch.nn as nn
import torch.optim as optim
import random
import numpy as np
from collections import deque

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 256)
        self.fc3 = nn.Linear(256, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# Hyperparameters
input_dim = GRID_WIDTH * GRID_HEIGHT  # Assuming the input is a flattened grid
output_dim = 4  # Up, Down, Left, Right
learning_rate = 0.001

# DQN instance
model = DQN(input_dim, output_dim)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

class ReplayMemory:
    def __init__(self, capacity):
        self.memory = deque(maxlen=capacity)

    def push(self, state, action, next_state, reward):
        self.memory.append((state, action, next_state, reward))

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

# Example usage
memory = ReplayMemory(10000)  # Adjust the capacity based on your needs

def train_model(model, memory, batch_size, optimizer, gamma):
    if len(memory) < batch_size:
        return

    batch = memory.sample(batch_size)
    states, actions, next_states, rewards = zip(*batch)

    states = torch.tensor(states, dtype=torch.float32)
    actions = torch.tensor(actions, dtype=torch.int64)
    next_states = torch.tensor(next_states, dtype=torch.float32)
    rewards = torch.tensor(rewards, dtype=torch.float32)

    # Compute Q(s_t, a) - model computes Q(s_t), then we select the columns of actions taken
    current_q_values = model(states).gather(1, actions.unsqueeze(1)).squeeze(1)

    # Compute V(s_{t+1}) for all next states.
    next_q_values = model(next_states).max(1)[0].detach()
    expected_q_values = rewards + gamma * next_q_values

    # Compute Huber loss
    loss = nn.functional.smooth_l1_loss(current_q_values, expected_q_values)

    # Optimize the model
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    
    # Saving the model
torch.save(model.state_dict(), 'dqn_model.pth')

# Loading the model
model.load_state_dict(torch.load('dqn_model.pth'))
model.eval()  # Set the model to evaluation mode


