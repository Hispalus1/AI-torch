import gym
import torch
import torch.nn as nn
import torch.optim as optim

env = gym.make('CartPole-v1')

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(env.observation_space.shape[0], 128), 
            nn.ReLU(),
            nn.Linear(128, env.action_space.n)
        )

    def forward(self, x):
        return self.fc(x)

    
net = Net()
optimizer = optim.Adam(net.parameters(), lr=0.001)

for episode in range(1000):  # Number of episodes
    state = env.reset()
    total_reward = 0

    while True:
        state_tensor = torch.from_numpy(state).float()
        action_probs = net(state_tensor)
        action = torch.argmax(action_probs).item()

        next_state, reward, done, _ = env.step(action)
        total_reward += reward

        # Update your network here based on the state transition

        if done:
            break

        state = next_state

    print(f"Episode {episode} Total Reward: {total_reward}")




