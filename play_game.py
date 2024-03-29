from model import CaveNet, epsilon_greedy_action_selection
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np
Mymodel = CaveNet() 
import torch
PATH = 'model/model_4.pth'
Mymodel.load_state_dict(torch.load(PATH))

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    
Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)
GREEN = (0, 255, 0)

BLOCK_SIZE = 20
SPEED = 20

class SnakeGame:
    
    def __init__(self, w=640, h=480):
        self.w = w//2
        self.h = h//2
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake')
        self.clock = pygame.time.Clock()
        
        # init game state
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2, self.h/2)
        
        self.snake = [self.head]
        self.blocks = []

        self.score = 0
        self.food = None
        self._place_food()
        num_blocks = 3
        self.x_point = []
        self.y_point = []
        for _ in range(num_blocks):
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            block = Point(x, y)
            if block not in self.snake and block != self.food:
                self.blocks.append(block)
                self.x_point.append(x)
                self.y_point.append(y)


    def getFeature(self):
        '''
        features = [threat_up, threat_right, threat_down, threat_left, Is_food_up, Is_food_right,Is_food_down, Is_food_left ]
        '''
        
        threat_up = self.head.y == 0.0 or (self.head.x  in self.x_point and  self.head.y - BLOCK_SIZE in self.y_point )
        threat_right = self.head.x == self.w - BLOCK_SIZE or (self.head.y  in self.y_point and  self.head.x + BLOCK_SIZE in self.x_point )
        threat_down = self.head.y == self.h - BLOCK_SIZE or (self.head.x  in self.x_point and  self.head.y + BLOCK_SIZE in self.y_point )
        threat_left = self.head.x == 0.0  or (self.head.y  in self.y_point and  self.head.x - BLOCK_SIZE in self.x_point )
        Is_food_up = self.head.y > self.food.y
        Is_food_right = self.head.x < self.food.x
        Is_food_down = self.head.y < self.food.y
        Is_food_left = self.head.x > self.food.x
        return [threat_up, threat_right, threat_down, threat_left, Is_food_up, Is_food_right, Is_food_down, Is_food_left]
        

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE 
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()
    def _place_blocks(self, num_blocks):
        self.blocks = []
        for _ in range(num_blocks):
            x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            block = Point(x, y)
            if block not in self.snake and block != self.food:
                self.blocks.append(block)

    def _update_blocks(self):
        for block in self.blocks:
            pygame.draw.rect(self.display, GREEN, pygame.Rect(block.x, block.y, BLOCK_SIZE, BLOCK_SIZE))
    
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        observation = self.getFeature()        
        action = epsilon_greedy_action_selection(model=Mymodel,epsilon=0,sharpening_factor=2, observation=np.array(observation)) 
                
        
        if action == 3:
            self.direction = Direction.LEFT
            # 2. move
            self._move(self.direction) # update the head
            self.snake.insert(0, self.head)
            self.snake.pop()
        elif action == 1:
            self.direction = Direction.RIGHT
            # 2. move
            self._move(self.direction) # update the head
            self.snake.insert(0, self.head)
            self.snake.pop()

        elif action == 0:
            self.direction = Direction.UP
            # 2. move
            self._move(self.direction) # update the head
            self.snake.insert(0, self.head)
            self.snake.pop()

        elif action == 2:
            self.direction = Direction.DOWN
            # 2. move
            self._move(self.direction) # update the head
            self.snake.insert(0, self.head)
            self.snake.pop()
        

                

        
        
        
        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            self._place_food()
        
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        # hits boundary
        if self.head.x > self.w - BLOCK_SIZE or self.head.x < 0 or self.head.y > self.h - BLOCK_SIZE or self.head.y < 0:
            return True
        else:
            for wall in self.blocks:
                if self.head == wall:
                    return True
        
        return False
        
    def _update_ui(self):
        self.display.fill(BLACK)
        self._update_blocks()
        
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            
        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
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


            

if __name__ == '__main__':
    game = SnakeGame()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        #print(game.getFeature())
        if game_over == True:
            break
        
    print('Final Score', score)
        
        
    pygame.quit()