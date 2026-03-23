import torch
import random
import numpy as np
from collections import deque
from game import SnakeGame, Direction, Point, BLOCK_SIZE
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
	def __init__(self):
		self.n_games = 0
		self.epsilon = 0 # randomness
		self.gamma = 0.9 # discount rate - must be smaller than 1
		self.memory = deque(maxlen=MAX_MEMORY) # popleft()
		self.model = Linear_QNet(11, 256, 3)
		self.model.load()
		self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

	def get_game_state(self, game):
		head = game.snake[0]
		point_l = Point(head.x - BLOCK_SIZE, head.y)
		point_r = Point(head.x + BLOCK_SIZE, head.y)
		point_u = Point(head.x, head.y - BLOCK_SIZE)
		point_d = Point(head.x, head.y + BLOCK_SIZE)

		dir_l = game.direction == Direction.LEFT
		dir_r = game.direction == Direction.RIGHT
		dir_u = game.direction == Direction.UP
		dir_d = game.direction == Direction.DOWN

		state = [
			# Danger Straight
			(dir_r and game.is_collision(point_r)) or
			(dir_l and game.is_collision(point_l)) or
			(dir_u and game.is_collision(point_u)) or
			(dir_d and game.is_collision(point_d)),

			# Danger Right
			(dir_u and game.is_collision(point_r)) or
			(dir_d and game.is_collision(point_l)) or
			(dir_l and game.is_collision(point_u)) or
			(dir_r and game.is_collision(point_d)),

			# Danger Left
			(dir_d and game.is_collision(point_r)) or
			(dir_u and game.is_collision(point_l)) or
			(dir_r and game.is_collision(point_u)) or
			(dir_l and game.is_collision(point_d)),

			# Move Dirrections
			dir_l,
			dir_r,
			dir_u,
			dir_d,

			#  Food Locations
			game.food.x < game.head.x, # Food is left of head
			game.food.x > game.head.x, # Food is right of head
			game.food.y < game.head.y, # Food is above head
			game.food.y > game.head.y # Food is below head
		]

		return np.array(state, dtype=int)

	def get_game_action(self, state):
		# random moves: tradeoff exploration / exploitation
		self.epsilon = 80 - self.n_games
		fin_move = [0,0,0]
		if random.randint(0,200) < self.epsilon:
			move = random.randint(0, 2)
			fin_move[move] = 1
		else:
			state0 = torch.tensor(state, dtype=torch.float)
			prediction = self.model(state0)
			move = torch.argmax(prediction).item()
			fin_move[move] = 1
		return fin_move

	def remember(self, state, action, reward, next_state, done):
		self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

	def train_long_mem(self):
		if len(self.memory) > BATCH_SIZE:
			mini_sample = random.sample(self.memory, BATCH_SIZE) # List of tuples
		else:
			mini_sample = self.memory

		states, actions, rewards, next_states, dones = zip(*mini_sample)
		self.trainer.train_step(states, actions, rewards, next_states, dones)

	def train_short_mem(self, state, action, reward, next_state, done):
		self.trainer.train_step(state, action, reward, next_state, done)

def train():
	plot_scores = []
	plot_mean_scores = []
	total_score = 0
	record = 0
	print("1: creating agent")
	agent = Agent()
	print("2: creating game")
	game = SnakeGame(training=True)
	print("3: starting loop")
	while True:
		o_state = agent.get_game_state(game) # get old state
		fin_move = agent.get_game_action(o_state) # get move
		reward, done, score = game.play_step(fin_move) # perform move and get new state
		n_state = agent.get_game_state(game) # set new state
		agent.train_short_mem(
			o_state,
			fin_move,
			reward,
			n_state,
			done
		) # train short memory
		agent.remember(
			o_state,
			fin_move,
			reward,
			n_state,
			done
		)

		if done:
			# train long memory (experienced replay memory)
			# trains again on all games prev played
			# plot result
			game.reset()
			agent.n_games += 1
			agent.train_long_mem()

			if score > record:
				record = score
				agent.model.save()

			print(f"{agent.n_games=}, {score=}, {record=}")

			plot_scores.append(score)
			total_score += score
			mean_score = total_score / agent.n_games
			plot_mean_scores.append(mean_score)
			plot(plot_scores, plot_mean_scores)

if __name__ == "__main__":
	train()