import pygame
import random
from enum import Enum
from collections import namedtuple

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

class SnakeGame:

	def __init__(self, w=640, h=480):
		self.w = w
		self.h = h
		self.internal_w = w // 4
		self.internal_h = h // 4
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
		self.food = None
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
		x = random.randint(BLOCK_SIZE, (self.internal_w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
		y = random.randint(BLOCK_SIZE, (self.internal_h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
		self.food = Point(x, y)
		if self.food in self.snake:
			self._place_food()

	def play_step(self):
		game_ctrl = {"game_over": False, "quit": False}

		# 1. collect user input
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
					self.direction = Direction.LEFT
					break
				elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
					self.direction = Direction.RIGHT
					break
				elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
					self.direction = Direction.UP
					break
				elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
					self.direction = Direction.DOWN
					break
				elif event.key == pygame.K_r:
					game_ctrl["game_over"] = True
					return game_ctrl, self.score
				elif event.key == pygame.K_q:
					game_ctrl["quit"] = True
					return game_ctrl, self.score

		# 2. move
		self._move(self.direction) # update the head
		self.snake.insert(0, self.head)

		# 3. check if game over
		# game_ctrl["game_over"] = False
		if self._is_collision():
			game_ctrl["game_over"] = True
			return game_ctrl, self.score

		# 4. place new food or just move
		if self.head == self.food:
			self.score += 1
			self._place_food()
		else:
			self.snake.pop()

		# 5. update ui and clock
		self._update_ui()
		self.clock.tick(SPEED)
		# 6. return game over and score
		return game_ctrl, self.score

	def _is_collision(self):
		if self.head.x > self.internal_w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.internal_h - BLOCK_SIZE or self.head.y < 0:
			return True
		if self.head in self.snake[1:]:
			return True
		return False

	def _calc_food_dist(self) -> int:
		dx = self.food.x - self.head.x
		dy = self.food.y - self.head.y
		self.head
		import math
		return math.sqrt(dx**2 + dy**2) // BLOCK_SIZE

	def _get_snake_color(self, i: int, size: int, color: tuple[int], food_dist: int) -> tuple[int]:
		change_color = SNAKE_COLOR[1]
		if change_color > 0:
			idx = i+1
			slope = (255 // idx) * max(0, min(255, size - food_dist))  # Invert: use (size - food_dist)
			new_b = max(0, change_color - slope)
			print(idx, slope, (color[0], int(new_b), color[2]))
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
			# print(f"idx: {json.dumps(idx, indent=4)}\n" f"pt: {json.dumps(pt, indent=4)}")
			size: int = len(self.snake)
			snake_color = self._get_snake_color(idx, size, SNAKE_COLOR, food_dist)
			pygame.draw.rect(self.game_surface, snake_color, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))

		pygame.draw.rect(self.game_surface, WHITE, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

		# scale up with hard pixel edges
		scaled = pygame.transform.scale(self.game_surface, (self.w, self.h))

		# draw score on the scaled surface so the font can be a normal size
		text = font.render("Score: " + str(self.score), True, GREEN)
		text.set_colorkey(WHITE)
		blurred_text = self._blur_text(text, blur_amount=3)  # Adjust blur_amount for more/less blur
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

	def _move(self, direction):
		x = self.head.x
		y = self.head.y
		if direction == Direction.RIGHT:
			x += BLOCK_SIZE
		elif direction == Direction.LEFT:
			x -= BLOCK_SIZE
		elif direction == Direction.DOWN:
			y += BLOCK_SIZE
		elif direction == Direction.UP:
			y -= BLOCK_SIZE

		self.head = Point(x, y)


def main():
	game = SnakeGame()

	# game loop
	while True:
		game_ctrl, score = game.play_step()

		if game_ctrl.get("quit", None) is True:
			print('Final Score', score)
			break

		if game_ctrl["game_over"] is True:
			print('Final Score', score)
			game = SnakeGame()

	pygame.quit()

if __name__ == '__main__':
    main()