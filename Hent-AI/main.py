import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np



class MazeEnvironment:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = (0, 0)  
        self.goal = (width - 1, height - 1)  

    def reset(self):
        self.state = (0, 0)

    def step(self, action):
        x, y = self.state

        if action == 0:  
            y = max(0, y - 1)
        elif action == 1:  
            y = min(self.height - 1, y + 1)
        elif action == 2:  
            x = max(0, x - 1)
        elif action == 3:  
            x = min(self.width - 1, x + 1)

        self.state = (x, y)
        done = (self.state == self.goal)
        reward = 1 if done else 0
        return self.state, reward, done


class QNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, 128)
        self.fc2 = nn.Linear(128, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


