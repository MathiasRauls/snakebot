import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import os

class Linear_QNet(nn.Module):
	def __init__(self, input_size, hidden_size, output_size):
		super().__init__()
		self.linear1 = nn.Linear(input_size, hidden_size)
		self.linear2 = nn.Linear(hidden_size, output_size)

	def forward(self, x):
		x = F.relu(self.linear1(x))
		x = self.linear2(x)
		return x

	def save(self, file_name="model.pth"):
		model_folder_path = "./model"
		if not os.path.exists(model_folder_path):
			os.makedirs(model_folder_path)
		file_name = os.path.join(model_folder_path, file_name)
		torch.save(self.state_dict(), file_name)

	def load(self, file_name="model.pth"):
		file_name = os.path.join("./model", file_name)
		if os.path.exists(file_name):
			self.load_state_dict(torch.load(file_name, weights_only=True))
			print(f"Model loaded from {file_name}")

class QTrainer:
	def __init__(self, model, lr, gamma):
		self.lr = lr
		self.gamma = gamma
		self.model = model
		self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
		self.criterion = nn.MSELoss()

	def train_step(self, state, action, reward, next_state, done):
		state = torch.from_numpy(np.array(state)).float()
		next_state = torch.from_numpy(np.array(next_state)).float()
		action = torch.from_numpy(np.array(action)).long()
		reward = torch.from_numpy(np.array(reward)).float()

		if len(state.shape) == 1:
			state = torch.unsqueeze(state, 0)
			next_state = torch.unsqueeze(next_state, 0)
			action = torch.unsqueeze(action, 0)
			reward = torch.unsqueeze(reward, 0)
			done = (done, )

		# 1: predicted Q values with the current state
		pred = self.model(state)

		# 2: compute target Q values in batch (no Python loop)
		target = pred.clone()
		with torch.no_grad():
			next_pred = self.model(next_state)
			next_max = torch.max(next_pred, dim=1)[0]

		done_t = torch.tensor(done, dtype=torch.bool)
		Q_new = reward.clone()
		Q_new[~done_t] += self.gamma * next_max[~done_t]

		action_indices = torch.argmax(action, dim=1)
		target[torch.arange(len(target)), action_indices] = Q_new

		self.optimizer.zero_grad()
		loss = self.criterion(target, pred)
		loss.backward()

		self.optimizer.step()

		# 2: Q_new = r + y * max(next_predicted  Q value)
		# pred.clone()
		# pred[argmax(action)] = Q_new