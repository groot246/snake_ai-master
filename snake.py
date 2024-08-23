import pygame
import random
from datetime import datetime, timedelta
import sys
import pickle
import os

pygame.init()

# 전역변수 선언
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
size = [400, 400]
screen = pygame.display.set_mode(size)

done = False
clock = pygame.time.Clock()
last_moved_time = datetime.now()

KEY_DIRECTION = {
    pygame.K_UP: 'N',
    pygame.K_DOWN: 'S',
    pygame.K_LEFT: 'W',
    pygame.K_RIGHT: 'E',
}

OPPOSITE_DIRECTION = {
    'N': 'S',
    'S': 'N',
    'W': 'E',
    'E': 'W',
}

def draw_block(screen, color, position):
    block = pygame.Rect((position[1] * 20, position[0] * 20), (20, 20))
    pygame.draw.rect(screen, color, block)

class Snake:
    def __init__(self):
        self.positions = [(0, 2), (0, 1), (0, 0)]
        self.direction = 'E'
        self.growing = False

    def draw(self):
        for position in self.positions:
            draw_block(screen, GREEN, position)

    def move(self):
        head_position = self.positions[0]
        y, x = head_position
        if self.direction == 'N':
            new_position = (y - 1, x)
        elif self.direction == 'S':
            new_position = (y + 1, x)
        elif self.direction == 'W':
            new_position = (y, x - 1)
        elif self.direction == 'E':
            new_position = (y, x + 1)
        
        if not self.growing:
            self.positions = [new_position] + self.positions[:-1]
        else:
            self.positions = [new_position] + self.positions
            self.growing = False

    def grow(self):
        self.growing = True

    def check_collision(self):
        head_position = self.positions[0]
        if head_position[0] < 0 or head_position[0] >= 20 or head_position[1] < 0 or head_position[1] >= 20:
            return True
        if head_position in self.positions[1:]:
            return True
        return False

class Apple:
    def __init__(self, position=(5, 5)):
        self.position = position

    def draw(self):
        draw_block(screen, RED, self.position)

    def respawn(self):
        self.position = (random.randint(0, 19), random.randint(0, 19))

class MinimaxAI:
    def __init__(self, snake, apple, depth=3):
        self.snake = snake
        self.apple = apple
        self.depth = depth
        self.load_knowledge()

    def get_next_move(self):
        best_score = -sys.maxsize
        best_move = self.snake.direction

        for direction in ['N', 'S', 'W', 'E']:
            # 반대 방향으로 이동하려는 경우 무시
            if direction == OPPOSITE_DIRECTION[self.snake.direction]:
                continue

            new_positions = self.get_new_positions(self.snake.positions, direction)
            if not self.is_safe(new_positions[0]):
                continue

            score = self.minimax(new_positions, direction, self.depth, False)
            if score > best_score:
                best_score = score
                best_move = direction

        # 학습 데이터 저장
        self.save_knowledge(best_move, best_score)
        return best_move

    def minimax(self, positions, direction, depth, maximizing_player):
        if depth == 0 or self.is_terminal_state(positions):
            return self.evaluate(positions)

        if maximizing_player:
            max_eval = -sys.maxsize
            for direction in ['N', 'S', 'W', 'E']:
                new_positions = self.get_new_positions(positions, direction)
                if not self.is_safe(new_positions[0]):
                    continue
                eval = self.minimax(new_positions, direction, depth - 1, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = sys.maxsize
            for direction in ['N', 'S', 'W', 'E']:
                new_positions = self.get_new_positions(positions, direction)
                if not self.is_safe(new_positions[0]):
                    continue
                eval = self.minimax(new_positions, direction, depth - 1, True)
                min_eval = min(min_eval, eval)
            return min_eval

    def get_new_positions(self, positions, direction):
        head_position = positions[0]
        y, x = head_position
        if direction == 'N':
            new_position = (y - 1, x)
        elif direction == 'S':
            new_position = (y + 1, x)
        elif direction == 'W':
            new_position = (y, x - 1)
        elif direction == 'E':
            new_position = (y, x + 1)

        new_positions = [new_position] + positions[:-1]
        return new_positions

    def is_safe(self, position):
        y, x = position
        if y < 0 or y >= 20 or x < 0 or x >= 20:
            return False
        if position in self.snake.positions:
            return False
        return True

    def is_terminal_state(self, positions):
        return not self.is_safe(positions[0])

    def evaluate(self, positions):
        head_position = positions[0]
        apple_position = self.apple.position
        distance = abs(head_position[0] - apple_position[0]) + abs(head_position[1] - apple_position[1])
        return -distance

    def save_knowledge(self, move, score):
        # 텍스트 파일에 학습 내용 저장
        with open('minimax_knowledge.txt', 'a') as f:
            f.write(f"{move},{score}\n")

    def load_knowledge(self):
        # 텍스트 파일에서 학습 내용 불러오기
        if os.path.exists('minimax_knowledge.txt'):
            with open('minimax_knowledge.txt', 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1]
                    last_move, last_score = last_line.split(',')
                    self.snake.direction = last_move.strip()

def game_over():
    font = pygame.font.Font(None, 36)
    text = font.render("Game Over", True, (0, 0, 0))
    screen.blit(text, [size[0] // 2 - 50, size[1] // 2 - 20])
    pygame.display.flip()
    pygame.time.wait(2000)

def runGame():
    global done, last_moved_time
    snake = Snake()
    apple = Apple()
    ai = MinimaxAI(snake, apple)

    while not done:
        clock.tick(10)
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        snake.direction = ai.get_next_move()

        if timedelta(seconds=0.1) <= datetime.now() - last_moved_time:
            snake.move()
            last_moved_time = datetime.now()

        if snake.positions[0] == apple.position:
            snake.grow()
            apple.respawn()

        if snake.check_collision():
            game_over()
            runGame()  # 무한 학습을 위해 게임 재시작
            return

        snake.draw()
        apple.draw()
        pygame.display.update()

runGame()
pygame.quit()
