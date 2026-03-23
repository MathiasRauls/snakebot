import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('./micro.ttf', 40)

class Direction(Enum):
	RIGHT = 1
	LEFT = 2
	UP = 3
	DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
GREEN = (255, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0,0,0)
SCREEN = {
	"backlight": (0, 0, 1)
}

# snake color
# @dataclass
# class Color:
#     r: int
#     g: int
#     b: int
SNAKE_COLOR = (255, 255, 5)

BLOCK_SIZE = 4
SPEED = 15
TRAIN_SPEED = 0  # 0 = unlimited FPS for training

class SnakeGame:

	def __init__(self, w=640, h=480, training=False):
		self.w = w
		self.h = h
		self.training = training
		self.internal_w = w // BLOCK_SIZE
		self.internal_h = h // BLOCK_SIZE
		self.display = pygame.display.set_mode((self.w, self.h))
		self.game_surface = pygame.Surface((self.internal_w, self.internal_h))
		self.frame = 0

		pygame.display.set_caption('Snake 🐍')
		self.clock = pygame.time.Clock()

		self.reset()

	def reset(self):
		"""Initializes the Game State"""
		self.direction = Direction.RIGHT

		self.head = Point(self.internal_w // 2, self.internal_h // 2)

		self.snake = [
			self.head,
			Point(self.head.x-BLOCK_SIZE, self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y),
			Point(self.head.x-(2*BLOCK_SIZE), self.head.y)
		]

		self.score = 0
		self.food: Point
		self._place_food()
		self.frame_iter = 0

		self.scanlines = self._create_scanline_overlay()
		self.vignette = self._create_vignette()

	def _create_scanline_overlay(self):
		overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
		for y in range(0, self.h, 4):
			pygame.draw.line(overlay, (0, 0, 0, 50), (0, y), (self.w, y))
		return overlay

	def _create_vignette(self):
		vignette = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
		cx, cy = self.w // 2, self.h // 2
		max_dist = (cx**2 + cy**2) ** 0.5
		for x in range(0, self.w, 4):
			for y in range(0, self.h, 4):
				dist = ((x - cx)**2 + (y - cy)**2) ** 0.5
				alpha = int(min(255, (dist / max_dist) * 215))
				pygame.draw.rect(vignette, (0, 0, 0, alpha), (x, y, 4, 4))
		return vignette

	def _create_glow(self):
		small = pygame.transform.smoothscale(self.display, (self.w // 8, self.h // 8))
		glow = pygame.transform.smoothscale(small, (self.w, self.h))
		glow.set_alpha(60)
		return glow

	def _place_food(self):
		x = random.randint(0, (self.internal_w // BLOCK_SIZE) - 1) * BLOCK_SIZE
		y = random.randint(0, (self.internal_h // BLOCK_SIZE) - 1) * BLOCK_SIZE
		self.food = Point(x, y)
		if self.food in self.snake:
			self._place_food()

	def play_step(self, action=None):
		self.frame_iter += 1
		reward = 0
		game_over = False

		# 1. collect user input
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if action is None and event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
					self.direction = Direction.LEFT
				elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
					self.direction = Direction.RIGHT
				elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
					self.direction = Direction.UP
				elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
					self.direction = Direction.DOWN

		# 2. move
		self._move(action) # update the head using the AI action
		self.snake.insert(0, self.head)

		# 3. check if game over
		if self.is_collision() or self.frame_iter > 100*len(self.snake):
			game_over = True
			reward = -10
			return reward, game_over, self.score

		# 4. place new food or just move
		if self.head == self.food:
			self.score += 1
			reward += 10
			self._place_food()
		else:
			self.snake.pop()

		# 5. update ui and clock
		self._update_ui()
		if self.training:
			self.clock.tick(TRAIN_SPEED)
		else:
			self.clock.tick(SPEED)
		# 6. return game over and score
		return reward, game_over, self.score

	def is_collision(self, pt=None):
		if pt is None:
			pt = self.head
		if pt.x > self.internal_w - BLOCK_SIZE or pt.x < 0 or pt.y > self.internal_h - BLOCK_SIZE or pt.y < 0:
			return True
		if pt in self.snake[1:]:
			return True
		return False

	def _calc_food_dist(self) -> int:
		dx = self.food.x - self.head.x
		dy = self.food.y - self.head.y
		self.head
		import math
		return int(math.sqrt(dx**2 + dy**2) // BLOCK_SIZE)

	def _get_snake_color(self, i: int, size: int, color: tuple[int, ...], food_dist: int) -> tuple[int, ...]:
		change_color = SNAKE_COLOR[1]
		if change_color > 0:
			idx = i+1
			slope = (255 // idx) * max(0, min(255, size - food_dist))  # Invert: use (size - food_dist)
			new_b = max(0, change_color - slope)
			# print(idx, slope, (color[0], int(new_b), color[2]))
			return (color[0], int(new_b), color[2])
		return color

	def _blur_text(self, text_surface, blur_amount=2):
		"""Blur text by downscaling and upscaling"""
		w, h = text_surface.get_size()
		small = pygame.transform.smoothscale(text_surface, (w // blur_amount, h // blur_amount))
		blurred = pygame.transform.smoothscale(small, (w, h))
		return blurred

	def _update_ui(self):
		import math
		self.frame += 1
		self.game_surface.fill(SCREEN["backlight"])

		food_dist = self._calc_food_dist()

		for idx, pt in enumerate(self.snake):
			size: int = len(self.snake)
			snake_color = self._get_snake_color(idx, size, SNAKE_COLOR, food_dist)
			pygame.draw.rect(self.game_surface, snake_color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

		pygame.draw.rect(self.game_surface, WHITE, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

		# scale up with hard pixel edges
		scaled = pygame.transform.scale(self.game_surface, (self.w, self.h))

		# draw score on the scaled surface so the font can be a normal size
		text = font.render("Score: " + str(self.score), True, GREEN)
		text.set_colorkey(WHITE)

		if self.training:
			# Fast path: skip expensive post-processing during training
			self.display.blit(scaled, (0, 0))
			self.display.blit(text, [15, 5])
			pygame.display.flip()
			return

		blurred_text = self._blur_text(text, blur_amount=3)
		blurred_text.set_alpha(90)
		scaled.blit(text, [15, 5])
		scaled.blit(blurred_text, [15, 5])

		# wobble: shift each row by a sine offset
		wobbled = pygame.Surface((self.w, self.h))
		wobbled.fill(BLACK)
		for y in range(self.h):
			offset = int(math.sin((y * 0.05) + (self.frame * 0.1)) * 2)
			wobbled.blit(scaled, (offset, y), (0, y, self.w, 1))

		# apply overlays
		glow = pygame.transform.smoothscale(wobbled, (self.w // 6, self.h // 6))
		glow = pygame.transform.smoothscale(glow, (self.w + 5, self.h + 5))
		glow.set_alpha(90)
		tint = pygame.transform.smoothscale(wobbled, (self.w // 3, self.h // 3))
		tint = pygame.transform.smoothscale(tint, (self.w + 5, self.h + 5))
		tint = pygame.Surface((self.w + 5, self.h + 5))
		tint.fill((40, 7, 227))
		tint.set_alpha(50)
		tint.blit(tint, (0, 0))

		self.display.blit(text, [15, 5])
		self.display.blit(wobbled, (0, 0))
		self.display.blit(glow, (0, 0))
		self.display.blit(tint, (0, 0))
		self.display.blit(self.scanlines, (0, 0))
		self.display.blit(self.vignette, (0, 0))

		pygame.display.flip()

	def _move(self, action=None):

		# [straight, right, left]

		clock = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
		idx = clock.index(self.direction)

		if action is not None:
			if np.array_equal(action, [1,0,0]):
				new_dir = clock[idx] # no change
			elif np.array_equal(action, [0,1,0]):
				next_idx = (idx + 1) % 4
				new_dir = clock[next_idx] # right turn
			else:
				next_idx = (idx - 1) % 4
				new_dir = clock[next_idx] # left turn
			self.direction = new_dir

		x = self.head.x
		y = self.head.y
		match self.direction:
			case Direction.RIGHT:
				x += BLOCK_SIZE
			case Direction.LEFT:
				x -= BLOCK_SIZE
			case Direction.DOWN:
				y += BLOCK_SIZE
			case Direction.UP:
				y -= BLOCK_SIZE
		self.head = Point(x, y)


def main():
	game = SnakeGame()

	# game loop
	while True:
		reward, game_over, score = game.play_step()

		if game_over:
			print('Final Score', score)
			game.reset()

	pygame.quit()

if __name__ == '__main__':
    main()