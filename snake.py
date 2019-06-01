# imports

import pygame
import pygameMenu
import sys
import os
import random
import math
from pygameMenu.locals import *
from lib_nn.nn import NeuralNetwork

# show display in the middle of the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'


class GameInfo(object):
    """
    Game info is a class with all of the global information about the game
    like the display the Score...
    """

    def __init__(self):
        self.screen_width = 600
        self.screen_height = 600
        self.Score = 0
        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()


class Snake(GameInfo):
    def __init__(self, x=300, y=300):
        super().__init__()
        # default x,y
        self.x = int(x)
        self.y = int(y)
        self.body_width = 10
        self.body_height = 10
        self.color = (0, 255, 0)
        self.speed = 10
        self.body = [[self.x, self.y]]
        self.dir = 'left'
        self.pause = False
        # AI
        self.Fitness = 0
        self.food_dist = 0

    def draw(self):
        # moving the body + drawing it
        index = 0
        moveto = []
        for element in self.body:

            if index == 0:
                moveto.append([self.body[0][0], self.body[0][1]])
                if self.dir == 'left':
                    self.body[0][0] -= self.speed

                elif self.dir == 'right':
                    self.body[0][0] += self.speed

                elif self.dir == 'up':
                    self.body[0][1] -= self.speed

                elif self.dir == 'down':
                    self.body[0][1] += self.speed
            else:
                moveto.append([element[0], element[1]])
                element = moveto[len(moveto) - 2]
                self.body[index] = element

            pygame.draw.rect(self.display, self.color, (element[0], element[1], self.body_width, self.body_height))

            index += 1

    def move(self, menu):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            keys = pygame.key.get_pressed()

            for _ in keys:
                if keys[pygame.K_LEFT] and self.dir != 'right':

                    self.dir = 'left'

                elif keys[pygame.K_RIGHT] and self.dir != 'left':

                    self.dir = 'right'

                elif keys[pygame.K_UP] and self.dir != 'down':

                    self.dir = 'up'

                elif keys[pygame.K_DOWN] and self.dir != 'up':

                    self.dir = 'down'

                elif keys[pygame.K_ESCAPE]:
                    menu.enable()

    def ai(self, nn, food, menu):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            keys = pygame.key.get_pressed()

            for _ in keys:
                if keys[pygame.K_ESCAPE]:
                    menu.enable()

        input = [
                 # eight wall inputs
                 self.wall_dist_up(),
                 self.wall_dist_up_right(),
                 self.wall_dist_right(),
                 self.wall_dist_right_down(),
                 self.wall_dist_down(),
                 self.wall_dist_down_left(),
                 self.wall_dist_left(),
                 self.wall_dist_left_up(),

                 # eight body inputs
                 self.body_dist_up(),
                 self.body_dist_up_right(),
                 self.body_dist_down(),
                 self.body_dist_right_down(),
                 self.body_dist_right(),
                 self.body_dist_down_left(),
                 self.body_dist_left(),
                 self.body_dist_left_up(),

                 # eight food distance inputs
                 self.food_dist_up(food),
                 self.food_dist_up_right(food),
                 self.food_dist_right(food),
                 self.food_dist_right_down(food),
                 self.food_dist_down(food),
                 self.food_dist_down_left(food),
                 self.food_dist_left(food),
                 self.food_dist_left_up(food)
        ]

        """print("UP: ", self.wall_dist_up(), '\n',
              "UP-RIGHT: ", self.wall_dist_up_right(), '\n',
              "RIGHT: ", self.wall_dist_right(), '\n',
              "RIGHT-DONW: ", self.wall_dist_right_down(), '\n',
              "DOWN: ", self.wall_dist_down(), '\n',
              "DOWN-LEFT: ", self.wall_dist_down_left(), '\n',
              "LEFT: ", self.wall_dist_left(), '\n',
              "LEFT-UP: ", self.wall_dist_left_up(), '\n',
              "ANGLE: ", self.food_angle(food), '\n',
              "DISTANCE: ", self.distance_from_food(food))"""

        # add the inputs to the neural network (feed forward function)

        output = nn.feed_forward(input)

        index = 0
        current_val = 2
        dir_index = None
        for val in output:
            if val < current_val:
                dir_index = index
            current_val = val
            index += 1
        # neural network will give three outputs if forward or right or left
        # forward doesn't change anything in the current game state
        # so 1 is right and 2 is left

        if dir_index == 1:
            if self.dir == "up":
                self.dir = "right"
            elif self.dir == "right":
                self.dir = "down"
            elif self.dir == "down":
                self.dir = "right"
            elif self.dir == "left":
                self.dir = "up"

        elif dir_index == 2:
            if self.dir == "up":
                self.dir = "left"
            elif self.dir == "right":
                self.dir = "up"
            elif self.dir == "down":
                self.dir = "left"
            elif self.dir == "left":
                self.dir = "down"

    def eat(self, x, y):
        if x == self.body[0][0] and y == self.body[0][1]:
            if self.dir == 'left':
                x, y = self.body[len(self.body) - 1]
                self.body.append([x + self.speed, y])
            elif self.dir == 'right':
                x, y = self.body[len(self.body) - 1]
                self.body.append([x - self.speed, y])
            elif self.dir == 'up':
                x, y = self.body[len(self.body) - 1]
                self.body.append([x, y + self.speed])
            elif self.dir == 'down':
                x, y = self.body[len(self.body) - 1]
                self.body.append([x, y - self.speed])

            return True

    def hit(self):
        x, y = self.body[0]

        index = 0
        for element in self.body:
            if index != 0:
                if x == element[0] and y == element[1]:
                    return True
            if x < 0 or x >= 600 or y >= 600 or y < 0:
                return True
            index += 1
        return False

    # Input for AI

    def food_angle(self, food):
        del_x = self.body[0][0] - food.x
        del_y = self.body[0][1] - food.y
        degree = math.degrees(math.atan2(del_x, del_y))
        if 0 > degree:
            return (360 + degree) / 360
        else:
            return degree / 360

    # WALL
    def wall_dist_left(self):
        return 1 - ((self.body[0][0] + 10) / 610)

    def wall_dist_right(self):
        return 1 - ((self.screen_height - self.body[0][0]) / 600)

    def wall_dist_up(self):
        return 1 - ((self.body[0][1] + 10) / 610)

    def wall_dist_down(self):
        return 1 - ((self.screen_height - self.body[0][1]) / 600)

    def wall_dist_up_right(self):
        return 1 - ((1 / 2) ** (self.wall_dist_up() ** 2 + self.wall_dist_right() ** 2))

    def wall_dist_right_down(self):
        return 1 - ((1 / 2) ** (self.wall_dist_right() ** 2 + self.wall_dist_down() ** 2))

    def wall_dist_down_left(self):
        return 1 - ((1 / 2) ** (self.wall_dist_down() ** 2 + self.wall_dist_left() ** 2))

    def wall_dist_left_up(self):
        return 1 - ((1 / 2) ** (self.wall_dist_left() ** 2 + self.wall_dist_up() ** 2))

    # FOOD
    def distance_from_food(self, food):
        return (math.hypot(food.x - self.body[0][0], food.y - self.body[0][1])) / 841

    def food_dist_up_right(self, food):
        x, y = self.body[0]
        if food.x - x == y - food.y and food.x > x:

            return 1 - ((math.hypot(food.x - x, food.y - y)) / 841)
        else:
            return -1

    def food_dist_right_down(self, food):
        x, y = self.body[0]
        if food.x - food.y == x - y and food.x > x:

            return 1 - ((math.hypot(food.x - x, food.y - y)) / 841)
        else:
            return -1

    def food_dist_down_left(self, food):
        x, y = self.body[0]
        if food.x - x == y - food.y and food.x < x:

            return 1 - ((math.hypot(food.x - x, food.y - y)) / 841)
        else:
            return -1

    def food_dist_left_up(self, food):
        x, y = self.body[0]
        if - food.y + food.x == - y + x and food.x < x:

            return 1 - ((math.hypot(food.x - x, food.y - y)) / 841)
        else:
            return -1

    def food_dist_right(self, food):
        x, y = self.body[0]
        if food.y == y and food.x > x:
            return 1 - ((food.x - x) / 600)
        else:
            return -1

    def food_dist_left(self, food):
        x, y = self.body[0]
        if food.y == y and food.x < x:
            return 1 - ((x - food.x) / 600)
        else:
            return -1

    def food_dist_up(self, food):
        x, y = self.body[0]
        if food.x == x and food.y < y:
            return 1 - ((y - food.y) / 600)
        else:
            return -1

    def food_dist_down(self, food):
        x, y = self.body[0]
        if food.x == x and food.y > y:
            return 1 - ((food.y - y) / 600)
        else:
            return -1

    # BODY
    def body_dist_left(self):
        x, y = self.body[0]
        index = 0

        for element in self.body:
            if index != 0:
                if y == element[1] and x > element[0]:

                    return 1 - ((x - element[0]) / 600)

            index += 1
        return -1

    def body_dist_right(self):
        x, y = self.body[0]
        index = 0

        for element in self.body:
            if index != 0:
                if y == element[1] and x < element[0]:

                    return 1 - ((element[0] - x) / 600)

            index += 1
        return -1

    def body_dist_up(self):
        x, y = self.body[0]
        index = 1

        for element in self.body:
            if index != 0:
                if x == element[0] and y > element[1]:

                    return 1 - ((y - element[1]) / 600)

            index += 1
        return -1

    def body_dist_down(self):
        x, y = self.body[0]
        index = 0

        for element in self.body:
            if index != 0:
                if x == element[0] and y < element[1]:

                    return 1 - ((element[1] - y) / 600)

            index += 1
        return -1

    def body_dist_up_right(self):
        x, y = self.body[0]
        index = 0

        for element in self.body:
            if index != 0:
                if element[0] - x == y - element[1] and element[0] > x:
                    return 1 - ((math.hypot(x - element[0], y - element[1])) / 841)

            index += 1
        return -1

    def body_dist_right_down(self):
        x, y = self.body[0]
        index = 0

        for element in self.body:
            if index != 0:
                if element[0] - element[1] == x - y and element[0] > x:
                    return 1 - ((math.hypot(x - element[0], y - element[1])) / 841)

            index += 1
        return -1

    def body_dist_down_left(self):
        x, y = self.body[0]
        index = 0

        for element in self.body:
            if index != 0:
                if element[0] - x == y - element[1] and element[0] < x:
                    return 1 - ((math.hypot(x - element[0], y - element[1])) / 841)

            index += 1
        return -1

    def body_dist_left_up(self):
        x, y = self.body[0]
        index = 0

        for element in self.body:
            if index != 0:
                if - element[1] + element[0] == - y + x and element[0] < x:
                    return 1 - ((math.hypot(x - element[0], y - element[1])) / 841)

            index += 1
        return -1


class Food(GameInfo):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.color = (255, 0, 0)
        self.width = 10
        self.height = 10
        self.index = 1

    def draw(self):
        pygame.draw.rect(self.display, self.color, (self.x, self.y, self.width, self.height))


class Game(object):
    """
    The main game class
    """

    def __init__(self, population=None):
        self.game = GameInfo()

        if population is None:

            self.snake = Snake()
            self.food = Food(random.randint(1, 59) * self.snake.speed, random.randint(1, 59) * self.snake.speed)

        else:
            self.all_food_pos = []

            self.all_food = []
            self.snake = Snake()
            self.all_snake = []
            for r in range(100):
                self.all_food_pos.append(
                    (random.randint(1, 59) * self.snake.speed, random.randint(1, 59) * self.snake.speed))

            for _ in population:
                self.all_snake.append(Snake())
                self.all_food.append(
                    Food(self.all_food_pos[0][0], self.all_food_pos[0][1]))
        # self.food = Food(random.randint(1, 59) * self.snake.speed, random.randint(1, 59) * self.snake.speed)
        self.population = population

    def main_menu_background(self):
        """
        Background color of the main menu, on this function user can plot
        images, play sounds, etc.
        """
        self.game.display.fill((40, 0, 40))

    def game_loop(self, show=True, max_turns=300, delay=50, gen=None):
        global Play_normal
        Play_normal = "None"
        pygame.init()
        white = (255, 255, 255)
        if self.population is None:
            AI = False
        else:
            AI = True

        # -----------------------------------------------------------------------------
        # Main menu, pauses execution of the application

        def main_menu_background():
            """
            Background color of the main menu, on this function user can plot
            images, play sounds, etc.
            """
            game.game.display.fill((216, 216, 216))

        def play():
            global Play_normal
            Play_normal = "Player"

        def train_ai():
            global Play_normal
            Play_normal = "AI"
            print("Here")

        menu = pygameMenu.Menu(self.game.display,
                               bgfun=main_menu_background,
                               enabled=False,
                               font=pygameMenu.fonts.FONT_NEVIS,
                               menu_alpha=90,
                               onclose=PYGAME_MENU_CLOSE,
                               title='Main Menu',
                               title_offsety=5,
                               window_height=int(self.game.screen_height),
                               window_width=int(self.game.screen_width)
                               )

        menu.add_option("New Game", play)
        menu.add_option("Train AI", train_ai)
        menu.add_option("Player vs Best AI", train_ai)
        menu.add_option('Exit', PYGAME_MENU_EXIT)

        # -----------------------------------------------------------------------------

        pygame.display.set_caption("snake")

        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        my_font = pygame.font.SysFont('Comic Sans MS', 15)
        if not show:
            pygame.display.iconify()

        All_fitness = []
        next_puplation = []
        turns = 0

        # frame rate + delay after every frame
        FPS = 12
        delay = delay
        while True:
            events = pygame.event.get()

            self.game.display.fill(white)
            pygame.time.delay(delay)
            self.game.clock.tick(FPS)

            if AI:
                # UI
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    keys = pygame.key.get_pressed()

                    for _ in keys:

                        if keys[pygame.K_ESCAPE]:
                            menu.enable()

                remove_s = []
                remove_f = []
                remove_nn = []
                index = 0

                for nn in self.population:

                    self.all_food[index].draw()
                    self.all_snake[index].ai(nn, self.all_food[index], menu)
                    self.all_snake[index].draw()

                    if self.all_snake[index].food_dist > self.all_snake[index].distance_from_food(self.all_food[index]):
                        self.all_snake[index].Fitness += 1

                    else:
                        self.all_snake[index].Fitness -= 1

                    self.all_snake[index].food_dist = self.all_snake[index].distance_from_food(self.all_food[index])
                    if turns >= max_turns:
                        remove_s = []
                        remove_f = []
                        remove_nn = []
                        for snake in self.all_snake:
                            remove_s.append(snake)
                        for food in self.all_food:
                            remove_f.append(food)
                        for n in self.population:
                            remove_nn.append(n)
                        break

                    if self.all_snake[index].hit():
                        self.game.DEATH = True
                        self.all_snake[index].Fitness -= max_turns
                        remove_s.append(self.all_snake[index])
                        remove_f.append(self.all_food[index])
                        remove_nn.append(nn)

                    if self.all_snake[index].eat(self.all_food[index].x, self.all_food[index].y):
                        self.game.Score += 1
                        self.all_food[index] = Food(self.all_food_pos[self.all_food[index].index][0],
                                                    self.all_food_pos[self.all_food[index].index][1])
                        self.all_food[index].index += 1
                        self.game.display.fill(white)
                        self.all_snake[index].Fitness += max_turns

                    index += 1
                for r in remove_s:
                    # print(r.Fitness)
                    All_fitness.append(r.Fitness)
                    self.all_snake.remove(r)
                for r in remove_f:
                    self.all_food.remove(r)
                for r in remove_nn:
                    next_puplation.append(r)
                    self.population.remove(r)
                menu.mainloop(events)

                # self.game.display.fill(white)
                text_surface2 = my_font.render('Loading: ' + str(turns) + ' / ' + str(max_turns), False, (255, 0, 0))
                text_surface = my_font.render('Generation: ' + str(gen), False, (255, 0, 0))
                self.game.display.blit(text_surface2, (230, 250))
                self.game.display.blit(text_surface, (230, 200))
                pygame.display.flip()
                turns += 1

                # showing the best player and mixing gen poll
                if len(self.all_snake) == 0:

                    # sorting from biggest to smallest
                    All_fitness_sorted = []
                    next_puplation_sorted = []
                    while All_fitness:
                        # find index of maximum item
                        max_index = All_fitness.index(max(All_fitness))

                        # remove item with pop() and append to sorted list
                        next_puplation_sorted.append(next_puplation[max_index])
                        next_puplation.remove(next_puplation[max_index])
                        All_fitness_sorted.append(All_fitness[max_index])
                        All_fitness.remove(All_fitness[max_index])

                    # breading the best and killing the worst
                    all_percent = []
                    current_percent = 100
                    one_percent = 100 / len(next_puplation_sorted)
                    for _ in next_puplation_sorted:
                        all_percent.append(current_percent / 100)
                        current_percent -= one_percent

                    index = 0
                    expected = len(next_puplation_sorted)

                    remove = []
                    for percent in all_percent:
                        r = random.randint(0, 10000) / 10000

                        if r > percent:
                            remove.append(next_puplation_sorted[index])
                        index += 1

                    for r in remove:
                        next_puplation_sorted.remove(r)
                    # mutating and creating new population

                    current_population = NeuralNetwork.cross_over(next_puplation_sorted, expected)

                    return current_population, All_fitness_sorted

            else:
                text_surface = my_font.render('Score:  ' + str(self.game.Score), False, (255, 0, 0))
                self.game.display.blit(text_surface, (10, 10))
                self.food.draw()
                self.snake.move(menu)
                self.snake.draw()
                # print("UP: ", self.snake.food_dist_up(self.food))
                # print("DOWN: ", self.snake.food_dist_down(self.food))
                # print("RIGHT: ", self.snake.food_dist_right(self.food))
                # print("LEFT: ", self.snake.food_dist_left(self.food))
                # print("UP-RIGHT: ", self.snake.body_dist_up_right())
                # print("RIGHT-DOWN: ", self.snake.body_dist_right_down())
                # print("DOWN-LEFT: ", self.snake.body_dist_down_left())
                # print("LEFT-UP: ", self.snake.body_dist_left_up())

                if self.snake.eat(self.food.x, self.food.y):
                    self.game.Score += 1
                    self.food = Food(random.randint(1, 59) * self.snake.speed, random.randint(1, 59) * self.snake.speed)
                    self.game.display.fill(white)

                if self.snake.hit():
                    return None

                menu.mainloop(events)
                pygame.display.flip()

            if Play_normal != "None":
                return Play_normal

    def simulate(self, nn, fitness="unknown"):
        global Play_normal
        Play_normal = "None"
        pygame.init()
        white = (255, 255, 255)
        self.snake = Snake()
        self.food = Food(self.all_food_pos[0][0], self.all_food_pos[0][1])
        simulate_nn = nn[0]

        # -----------------------------------------------------------------------------
        # Main menu, pauses execution of the application

        def main_menu_background():
            """
            Background color of the main menu, on this function user can plot
            images, play sounds, etc.
            """
            game.game.display.fill((216, 216, 216))

        def play():
            global Play_normal
            Play_normal = "Player"

        def train_ai():
            global Play_normal
            Play_normal = "AI"

        menu = pygameMenu.Menu(self.game.display,
                               bgfun=main_menu_background,
                               enabled=False,
                               font=pygameMenu.fonts.FONT_NEVIS,
                               menu_alpha=90,
                               onclose=PYGAME_MENU_CLOSE,
                               title='Main Menu',
                               title_offsety=5,
                               window_height=int(self.game.screen_height),
                               window_width=int(self.game.screen_width)
                               )

        menu.add_option("New Game", play)
        menu.add_option("Train AI", train_ai)
        menu.add_option("Player vs Best AI", train_ai)
        menu.add_option('Exit', PYGAME_MENU_EXIT)

        # -----------------------------------------------------------------------------

        pygame.display.set_caption("snake")

        pygame.font.init()  # you have to call this at the start,
        # if you want to use this module.
        my_font = pygame.font.SysFont('Comic Sans MS', 15)

        # frame rate + delay after every frame
        fps = 12
        delay = 50
        turn = 0
        while True:
            if turn != 1500:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                    keys = pygame.key.get_pressed()

                    for _ in keys:
                        if keys[pygame.K_ESCAPE]:
                            menu.enable()

                events = pygame.event.get()
                self.game.display.fill(white)
                all_fit = 0
                for fit in fitness:
                    all_fit += fit
                average = all_fit / len(fitness)
                text_surface = my_font.render('Best Fitness:  ' + str(fitness[0]),
                                              False, (100, 200, 24))
                text_surface2 = my_font.render("Average Fitness: " + str(average), False, (100, 200, 24))
                self.game.display.blit(text_surface, (10, 10))
                self.game.display.blit(text_surface2, (10, 40))

                pygame.time.delay(delay)
                self.game.clock.tick(fps)

                self.food.draw()
                self.snake.ai(simulate_nn, self.food, menu)
                self.snake.draw()

                if self.snake.hit():
                    for n in nn:
                        n.mutate(0.01)
                    return None

                if self.snake.eat(self.food.x, self.food.y):
                    self.game.Score += 1
                    self.food = Food(self.all_food_pos[self.food.index][0], self.all_food_pos[self.food.index][1])
                    self.food.index += 1
                    self.game.display.fill(white)

                menu.mainloop(events)

                pygame.display.flip()

                if Play_normal != "None":
                    return Play_normal
            else:
                return None
            turn += 1


# initial population
# params
population_num = 2000
input = 24
hidden = [16]
output = 3
turns_in_simulation = 600

population = NeuralNetwork.initial_population(population_num, input, hidden, output)
gen = 1

prev_a = 0
prev_best = 0
if __name__ == '__main__':
    while True:
        game = Game(population)

        population = game.game_loop(True, turns_in_simulation, 0, gen)

        if population == "Player":
            population = None
        elif population == "AI":
            population = NeuralNetwork.initial_population(population_num, input, hidden, output)
        elif population is not None:
            print("Gen: ", gen)
            all_fit = 0
            for fit in population[1]:
                all_fit += fit
            print("Average Fitness: ", all_fit/len(population[1]))
            print("improvement: ", all_fit/len(population[1])-prev_a)
            print("Best Fitness:", population[1][0])
            print("improvement: ", population[1][0] - prev_best)
            # print("Fitness: ", population[1])
            print('\n')
            game.simulate(population[0], population[1])
            population = population[0]
            prev_a = all_fit/len(population[1][0])
            prev_best = population[1][0]
        gen += 1
