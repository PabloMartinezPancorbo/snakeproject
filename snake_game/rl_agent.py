import random
import pygame
import sys
import numpy as np
from snake import screen, screen_width, screen_height, clock, draw_snake, draw_food, snake_pos, snake_body, food_pos

# Initialize Q-table with random values
Q_table = {}
learning_rate = 0.1
discount_factor = 0.9
exploration_rate = 1.0
exploration_decay = 0.995
min_exploration_rate = 0.01

def get_state(snake_pos, snake_body, food_pos):
    # Simplified state representation
    return (snake_pos[0], snake_pos[1], food_pos[0], food_pos[1])

def choose_action(state, valid_actions):
    if random.uniform(0, 1) < exploration_rate:
        # Explore: Choose a random action
        return random.choice(valid_actions)
    else:
        # Exploit: Choose the action with the highest Q-value
        return max(Q_table.get(state, {}), key=Q_table.get(state, {}).get, default=random.choice(valid_actions))

def update_q_table(state, action, reward, next_state):
    current_q = Q_table.get(state, {}).get(action, 0)
    max_future_q = max(Q_table.get(next_state, {}).values(), default=0)
    
    # Q-learning update rule
    new_q = current_q + learning_rate * (reward + discount_factor * max_future_q - current_q)
    
    if state not in Q_table:
        Q_table[state] = {}
    Q_table[state][action] = new_q

def rl_main():
    global snake_pos, snake_body, food_pos, exploration_rate
    
    score = 0
    snake_direction = "RIGHT"
    food_spawn = True

    while True:
        state = get_state(snake_pos, snake_body, food_pos)
        valid_actions = ["UP", "DOWN", "LEFT", "RIGHT"]

        # Prevent the snake from reversing direction
        if snake_direction == "UP":
            valid_actions.remove("DOWN")
        elif snake_direction == "DOWN":
            valid_actions.remove("UP")
        elif snake_direction == "LEFT":
            valid_actions.remove("RIGHT")
        elif snake_direction == "RIGHT":
            valid_actions.remove("LEFT")

        action = choose_action(state, valid_actions)
        snake_direction = action

        # Move the snake
        if snake_direction == "UP":
            snake_pos[1] -= 10
        if snake_direction == "DOWN":
            snake_pos[1] += 10
        if snake_direction == "LEFT":
            snake_pos[0] -= 10
        if snake_direction == "RIGHT":
            snake_pos[0] += 10

        # Snake body growing mechanism
        snake_body.insert(0, list(snake_pos))
        if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
            score += 1
            reward = 10  # Positive reward for eating food
            food_spawn = False
        else:
            snake_body.pop()
            reward = -0.1  # Small penalty for each move

        if not food_spawn:
            food_pos = [random.randrange(1, (screen_width // 10)) * 10, random.randrange(1, (screen_height // 10)) * 10]
        food_spawn = True

        # Check for game over conditions
        if (snake_pos[0] < 0 or snake_pos[0] >= screen_width or
            snake_pos[1] < 0 or snake_pos[1] >= screen_height or
            snake_pos in snake_body[1:]):
            reward = -100  # Negative reward for dying
            print("Game Over! Agent's score:", score)
            pygame.quit()
            sys.exit()

        next_state = get_state(snake_pos, snake_body, food_pos)
        update_q_table(state, action, reward, next_state)

        # Decay exploration rate
        exploration_rate = max(min_exploration_rate, exploration_rate * exploration_decay)

        # Draw elements on the screen
        screen.fill((0, 0, 0))
        draw_snake(snake_body)
        draw_food(food_pos)

        pygame.display.update()
        clock.tick(10)
