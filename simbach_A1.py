"""
Kingsheep Agent Template

This template is provided for the course 'Practical Artificial Intelligence' of the University of Zürich. 

Please edit the following things before you upload your agent:
    - change the name of your file to '[uzhshortname]_A1.py', where [uzhshortname] needs to be your uzh shortname
	- change the name of the class to a name of your choosing
	- change the def 'get_class_name()' to return the new name of your class
	- change the init of your class:
		- self.name can be an (anonymous) name of your choosing
		- self.uzh_shortname needs to be your UZH shortname

The results and rankings of the agents will be published on OLAT using your 'name', not 'uzh_shortname', 
so they are anonymous (and your 'name' is expected to be funny, no pressure).

"""

from config import *
import math
import operator
import os
import random


def get_class_name():
    return 'TouchMyTralala'


class TouchMyTralala():
    """Example class for a Kingsheep player"""

    def __init__(self):
        self.name = "TouchMyTralala"
        self.uzh_shortname = "simbach"
        self.grid_size_x = 5
        self.grid_size_y = 5
        self.grid_size_x_wolf = 3
        self.grid_size_y_wolf = 3

    def find_next_goal(self, player_number, field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
            wolf_position = self.get_player_position(CELL_WOLF_1, field)
            enemy_wolf_position = self.get_player_position(CELL_WOLF_2, field)
            enemy_sheep_position = self.get_player_position(CELL_SHEEP_2, field)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)
            wolf_position = self.get_player_position(CELL_WOLF_2, field)
            enemy_wolf_position = self.get_player_position(CELL_WOLF_1, field)
            enemy_sheep_position = self.get_player_position(CELL_SHEEP_1, field)

        if not self.food_present(field):
            return self.hunt_enemy_sheep_as_sheep(enemy_sheep_position, enemy_wolf_position, field)

        else:
            buckets = {}

            # extract all food items
            food_items = {}
            wolf_aura = self.get_wolf_aura(enemy_wolf_position)

            for y in range(FIELD_HEIGHT):
                for x in range(FIELD_WIDTH):
                    if (y, x) in wolf_aura:
                        continue
                    elif field[y][x] == CELL_RHUBARB:
                        food_items[(y, x)] = 10
                    elif field[y][x] == CELL_GRASS:
                        food_items[(y, x)] = 1

            # calculate the shortest distance to each food item
            distance_from_my_sheep = {}
            distance_from_my_wolf = {}
            distance_from_enemy_sheep = {}
            distance_from_enemy_wolf = {}

            for key, value in food_items.items():
                astar_graph1 = AStarGraph(field, player_number, True)
                distance_from_my_sheep[key] = len(AStarSearch(sheep_position, key, astar_graph1)[0])
                distance_from_my_wolf[key] = len(AStarSearch(wolf_position, key, astar_graph1)[0])
                astar_graph2 = AStarGraph(field, 2, True) if player_number == 1 else AStarGraph(field, 1, True)
                distance_from_enemy_sheep[key] = len(AStarSearch(enemy_sheep_position, key, astar_graph2)[0])
                distance_from_enemy_wolf[key] = len(AStarSearch(enemy_wolf_position, key, astar_graph2)[0])

            # create a grid over the entire field of predefined size buckets[(y-start, x-start)] = (y, x, value, dist_my_sheep, dist_my_wolf, dist_enemy_sheep, dist_enemy_wolf)
            for y in range(FIELD_HEIGHT - self.grid_size_y + 1):
                for x in range(FIELD_WIDTH - self.grid_size_x + 1):
                    buckets[(y, x)] = []
                    for j in range(self.grid_size_y):
                        for i in range(self.grid_size_x):
                            if (y + j, x + i) in wolf_aura:
                                continue
                            if field[y + j][x + i] == CELL_RHUBARB:
                                buckets[(y, x)].append((y + j, x + i, 10,
                                                        distance_from_my_sheep[(y + j, x + i)],
                                                        distance_from_my_wolf[(y + j, x + i)],
                                                        distance_from_enemy_sheep[(y + j, x + i)],
                                                        distance_from_enemy_wolf[(y + j, x + i)]))
                            elif field[y + j][x + i] == CELL_GRASS:
                                buckets[(y, x)].append((y + j, x + i, 1,
                                                        distance_from_my_sheep[(y + j, x + i)],
                                                        distance_from_my_wolf[(y + j, x + i)],
                                                        distance_from_enemy_sheep[(y + j, x + i)],
                                                        distance_from_enemy_wolf[(y + j, x + i)]))

            # calculate the estimated value of each bucket with respect to the average distance to the food items
            buckets_value = {}
            wolf_goal = self.find_next_goal_wolf(player_number, field)

            for key, value in buckets.items():
                total = 0
                distances_from_my_sheep = []
                distances_from_my_wolf = []
                distances_from_enemy_sheep = []
                distances_from_enemy_wolf = []

                for elem in value:
                    total += elem[2]
                    distances_from_my_sheep.append(elem[3])
                    distances_from_my_wolf.append(elem[4])
                    distances_from_enemy_sheep.append(elem[5])
                    distances_from_enemy_wolf.append(elem[6])

                buckets_value[key] = total

                for elem in value:
                    if wolf_goal[0] == elem[0] and wolf_goal[1] == elem[1]:
                        buckets_value[key] = buckets_value[key] * 0.00001

                # adjust the estimated value according to the relative distance to my sheep
                if (len(distances_from_my_sheep) > 0):
                    # usually number between 1 and 30
                    avg_distance_my_sheep = sum(distances_from_my_sheep) / len(distances_from_my_sheep)
                    buckets_value[key] = buckets_value[key] / ( avg_distance_my_sheep ** 3)

                # adjust the estimated value according to the relative distance of each sheep
                if (len(distances_from_my_sheep) > 0 and len(distances_from_enemy_sheep) > 0):
                    avg_distance_my_sheep = sum(distances_from_my_sheep) / len(distances_from_my_sheep)
                    avg_distance_enemy_sheep = sum(distances_from_enemy_sheep) / len(distances_from_enemy_sheep)
                    if (avg_distance_my_sheep >= avg_distance_enemy_sheep):
                        buckets_value[key] = buckets_value[key] * 0.1

                # adjust the estimated value according to the relative distance to the enemy wolf
                # if enemy wolf is closer to that grid, decrease the estimated value of that grid
                if (len(distances_from_my_sheep) > 0 and len(distances_from_enemy_wolf) > 0):
                    avg_distance_my_sheep = sum(distances_from_my_sheep) / len(distances_from_my_sheep)
                    avg_distance_enemy_wolf = sum(distances_from_enemy_wolf) / len(distances_from_enemy_wolf)
                    if (avg_distance_my_sheep > avg_distance_enemy_wolf * 2):
                        buckets_value[key] = buckets_value[key] * 0.1



            # find the closest item in the best bucket
            best_bucket = max(buckets_value.items(), key=operator.itemgetter(1))[0]
            best_cell_distance = 1000
            best_cell_cost = 10000000000000000
            best_cell = None

            for element in buckets[best_bucket]:
                astar_graph = AStarGraph(field, player_number)
                result = AStarSearch(sheep_position, (element[0], element[1]), astar_graph)
                dist = len(result[0])
                cost = result[1]
                value = element[2]

                if dist/value < best_cell_distance:
                    best_cell_distance = dist
                    best_cell_cost = cost
                    best_cell = (element[0], element[1])


            # print("bestbucket: {}".format((best_bucket)))
            # print("buckets value: {}".format(print_sparse_dict(buckets_value)))
            # print("buckets: {}".format(print_sparse_dict(buckets)))

            if best_cell_cost < 1000:
                return best_cell
            else:
                return self.hunt_enemy_sheep_as_sheep(enemy_sheep_position, enemy_wolf_position, field)

    def find_next_goal_wolf(self, player_number, field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
            wolf_position = self.get_player_position(CELL_WOLF_1, field)
            enemy_wolf_position = self.get_player_position(CELL_WOLF_2, field)
            enemy_sheep_position = self.get_player_position(CELL_SHEEP_2, field)

        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)
            wolf_position = self.get_player_position(CELL_WOLF_2, field)
            enemy_wolf_position = self.get_player_position(CELL_WOLF_1, field)
            enemy_sheep_position = self.get_player_position(CELL_SHEEP_1, field)

        # if no food item is left on the map walk towards the enemy sheep
        if not self.food_present(field):
            return self.hunt_enemy_sheep_as_wolf(enemy_sheep_position, enemy_wolf_position, field)
        else:
            buckets = {}
            # extract all food items
            food_items = {}
            wolf_aura = self.get_wolf_aura(enemy_wolf_position)

            # extract all food items on the map
            for y in range(FIELD_HEIGHT):
                for x in range(FIELD_WIDTH):
                    if (y, x) in wolf_aura:
                        continue
                    elif field[y][x] == CELL_RHUBARB:
                        food_items[(y, x)] = 7
                    elif field[y][x] == CELL_GRASS:
                        food_items[(y, x)] = 1

            # calculate the shortest distance to each food item
            distance_from_my_sheep = {}
            distance_from_my_wolf = {}
            distance_from_enemy_sheep = {}
            distance_from_enemy_wolf = {}

            for key, value in food_items.items():
                astar_graph1 = AStarGraph(field, player_number, True, True)
                distance_from_my_sheep[key] = len(AStarSearch(sheep_position, key, astar_graph1)[0])
                distance_from_my_wolf[key] = len(AStarSearch(wolf_position, key, astar_graph1)[0])
                astar_graph2 = AStarGraph(field, 2, True, True) if player_number == 1 else AStarGraph(field, 1, True,
                                                                                                      True)
                distance_from_enemy_sheep[key] = len(AStarSearch(enemy_sheep_position, key, astar_graph2)[0])
                distance_from_enemy_wolf[key] = len(AStarSearch(enemy_wolf_position, key, astar_graph2)[0])

            # create a grid over the map of size 3x3
            for y in range(FIELD_HEIGHT - self.grid_size_y_wolf):
                for x in range(FIELD_WIDTH - self.grid_size_x_wolf):
                    buckets[(y, x)] = []
                    for j in range(self.grid_size_y_wolf):
                        for i in range(self.grid_size_x_wolf):
                            if (y + j, x + i) in wolf_aura:
                                continue
                            if field[y + j][x + i] == CELL_RHUBARB:
                                buckets[(y, x)].append((y + j, x + i, 7,
                                                        distance_from_my_sheep[(y + j, x + i)],
                                                        distance_from_my_wolf[(y + j, x + i)],
                                                        distance_from_enemy_sheep[(y + j, x + i)],
                                                        distance_from_enemy_wolf[(y + j, x + i)]))
                            elif field[y + j][x + i] == CELL_GRASS:
                                buckets[(y, x)].append((y + j, x + i, 1,
                                                        distance_from_my_sheep[(y + j, x + i)],
                                                        distance_from_my_wolf[(y + j, x + i)],
                                                        distance_from_enemy_sheep[(y + j, x + i)],
                                                        distance_from_enemy_wolf[(y + j, x + i)]))

            # calculate the estimated value of each bucket with respect to the average distance to the food items
            buckets_value = {}

            for key, value in buckets.items():
                total = 0
                distances_from_my_sheep = []
                distances_from_my_wolf = []
                distances_from_enemy_sheep = []
                distances_from_enemy_wolf = []

                for elem in value:
                    if elem == CELL_FENCE:
                        total -= 1
                    total += elem[2]
                    distances_from_my_sheep.append(elem[3])
                    distances_from_my_wolf.append(elem[4])
                    distances_from_enemy_sheep.append(elem[5])
                    distances_from_enemy_wolf.append(elem[6])

                buckets_value[key] = total

                # adjust the estimated value according to the relative distance to the enemy wolf
                # if enemy sheep is closer to that grid, decrease the estimated value of that grid
                if len(distances_from_my_wolf) > 0 and len(distances_from_enemy_sheep) > 0:
                    avg_distance_my_wolf = sum(distances_from_my_wolf) / len(distances_from_my_wolf)
                    avg_distance_enemy_sheep = sum(distances_from_enemy_sheep) / len(distances_from_enemy_sheep)
                    if (avg_distance_my_wolf * 2 > avg_distance_enemy_sheep):
                        buckets_value[key] = buckets_value[key] * 0.1

                # prefer close grids
                if len(distances_from_my_wolf) > 0:
                    avg_distance_my_wolf = sum(distances_from_my_wolf) / len(distances_from_my_wolf)
                    if avg_distance_my_wolf < 4:
                        buckets_value[key] *= 2
                    # buckets_value[key] = buckets_value[key] / (avg_distance_my_wolf)

                # ignore grids close to my sheep
                if len(distances_from_my_sheep) > 0:
                    avg_distance_my_sheep = sum(distances_from_my_sheep) / len(distances_from_my_sheep)
                    buckets_value[key] = buckets_value[key] * (avg_distance_my_sheep/5)



            best_bucket = max(buckets_value.items(), key=operator.itemgetter(1))[0]
            best_y = None
            best_x = None
            # print("bestbucket: {}".format((best_bucket)))
            # print("buckets value: {}".format(print_sparse_dict(buckets_value)))
            # print("buckets: {}".format(print_sparse_dict(buckets)))
            # choose a cell of that bucket which can be reached
            enemy_wolf_symbol = field[enemy_wolf_position[0]][enemy_wolf_position[1]]
            for j in [1, 0, 2]:
                for i in [1, 0, 2]:
                    cell = field[j + best_bucket[0]][i + best_bucket[1]]
                    if cell != CELL_FENCE and cell != CELL_SHEEP_1 and cell != CELL_SHEEP_2 and cell != enemy_wolf_symbol and cell != CELL_RHUBARB and cell != CELL_GRASS:
                        best_y = j + best_bucket[0]
                        best_x = i + best_bucket[1]

            if best_x is None or best_y is None:
                best_y = 1 + best_bucket[0]
                best_x = 1 + best_bucket[1]

            # check if the best cell is reachable. Otherwise, hunt enemy
            graph = AStarGraph(field, player_number, False, True)
            # print("actual goal: ({}, {})".format(best_y, best_x))
            (path, cost) = AStarSearch(wolf_position, (best_y, best_y), graph)
            if cost < 100000:
                return (best_y, best_x)
            else:
                # print("cost: {}".format(cost))
                return self.hunt_enemy_sheep_as_wolf(enemy_sheep_position, enemy_wolf_position, field)

    def move_sheep(self, player_number, field):
        if player_number == 1:
            figure = CELL_SHEEP_1
        else:
            figure = CELL_SHEEP_2

        goal = self.find_next_goal(player_number, field)
        self.graph = AStarGraph(field, player_number)
        self.position = self.get_player_position(figure, field)
        # print("sheep goes to {}".format(goal))

        if goal != None:
            result = AStarSearch(self.position, goal, self.graph)[0]
            if len(result) > 1:
                return self.extract_move(self.position, result[1])
            else:
                return MOVE_NONE
        else:
            return MOVE_NONE

    def move_wolf(self, player_number, field):
        if player_number == 1:
            figure = CELL_WOLF_1
            enemy_sheep = CELL_SHEEP_2
        else:
            figure = CELL_WOLF_2
            enemy_sheep = CELL_SHEEP_1

        self.position = self.get_player_position(figure, field)
        self.enemy_sheep_position = self.get_player_position(enemy_sheep, field)
        self.graph = AStarGraph(field, player_number, ignore_wolf=False, is_wolf=True)
        goal = self.find_next_goal_wolf(player_number, field)

        # if enemy sheep is close by and can be eaten
        if self.is_enemy_sheep_eatable(self.position, self.enemy_sheep_position):
            return self.extract_move(self.position, self.enemy_sheep_position)

        # if the wolf is in a lucrative position to rest and wait
        elif goal == self.position:
            # print("wolf is waiting")
            return MOVE_NONE

        # if we are on the way to a lucrative position
        elif goal != None:
            # print("wolf is going to {}".format(goal))
            result = AStarSearch(self.position, goal, self.graph)[0]
            if len(result) > 1:
                return self.extract_move(self.position, result[1])
            else:
                return MOVE_NONE

        else:
            return MOVE_NONE

        # edit here incl. the return statement
        # walk to closest rhubarb
        return MOVE_NONE

    def is_in_field(self, y, x, field):
        return False if x > 18 or x < 0 or y > 14 or y < 0 or \
                        field[y][x] == CELL_FENCE or \
                        field[y][x] == CELL_SHEEP_1 or \
                        field[y][x] == CELL_WOLF_1 or \
                        field[y][x] == CELL_SHEEP_2 or \
                        field[y][x] == CELL_WOLF_2 else True

    def is_enemy_sheep_eatable(self, wolf_position, enemy_sheep_position):
        if wolf_position[0] == enemy_sheep_position[0] and abs(wolf_position[1] - enemy_sheep_position[1]) < 2:
            return True
        if wolf_position[1] == enemy_sheep_position[1] and abs(wolf_position[0] - enemy_sheep_position[0]) < 2:
            return True
        else:
            return False

    def get_wolf_aura(self, pos):
        return [(pos[0], pos[1] + 1), (pos[0] + 1, pos[1]), (pos[0], pos[1] - 1), (pos[0] - 1, pos[1])]

    def extract_move(self, start, next):
        if start[0] > next[0]:
            return MOVE_UP
        elif start[0] < next[0]:
            return MOVE_DOWN
        elif start[1] < next[1]:
            return MOVE_RIGHT
        elif start[1] > next[1]:
            return MOVE_LEFT
        return MOVE_NONE

    def is_in_wolf_aura(self, enemy_wolf_position, cell):
        aura = self.get_wolf_aura(enemy_wolf_position)
        if cell in aura:
            return True
        return False

    def hunt_enemy_sheep_as_wolf(self, enemy_sheep_position, enemy_wolf_position, field):
        # print("hunting enemy sheep")
        return enemy_sheep_position

    def hunt_enemy_sheep_as_sheep(self, enemy_sheep_position, enemy_wolf_position, field):
        choice = random.randint(0, 3)
        if choice == 0:
            if self.is_in_field(enemy_sheep_position[0], enemy_sheep_position[1] - 1, field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0], enemy_sheep_position[1] - 1)):
                return (enemy_sheep_position[0], enemy_sheep_position[1] - 1)

            elif self.is_in_field(enemy_sheep_position[0] - 1, enemy_sheep_position[1], field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0] + 1, enemy_sheep_position[1])):
                return (enemy_sheep_position[0] - 1, enemy_sheep_position[1])

            elif self.is_in_field(enemy_sheep_position[0] + 1, enemy_sheep_position[1], field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0] + 1, enemy_sheep_position[1])):
                return (enemy_sheep_position[0] + 1, enemy_sheep_position[1])

            elif self.is_in_field(enemy_sheep_position[0], enemy_sheep_position[1] + 1, field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0], enemy_sheep_position[1] + 1)):
                return (enemy_sheep_position[0], enemy_sheep_position[1] + 1)
            else:
                return self.get_random_walkable_cell(field, enemy_wolf_position)
        if choice == 1:
            if self.is_in_field(enemy_sheep_position[0] - 1, enemy_sheep_position[1], field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0] + 1, enemy_sheep_position[1])):
                return (enemy_sheep_position[0] - 1, enemy_sheep_position[1])

            elif self.is_in_field(enemy_sheep_position[0] + 1, enemy_sheep_position[1], field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0] + 1, enemy_sheep_position[1])):
                return (enemy_sheep_position[0] + 1, enemy_sheep_position[1])

            elif self.is_in_field(enemy_sheep_position[0], enemy_sheep_position[1] - 1, field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0], enemy_sheep_position[1] - 1)):
                return (enemy_sheep_position[0], enemy_sheep_position[1] - 1)

            elif self.is_in_field(enemy_sheep_position[0], enemy_sheep_position[1] + 1, field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0], enemy_sheep_position[1] + 1)):
                return (enemy_sheep_position[0], enemy_sheep_position[1] + 1)
            else:
                return self.get_random_walkable_cell(field, enemy_wolf_position)

        if choice == 2:
            if self.is_in_field(enemy_sheep_position[0] + 1, enemy_sheep_position[1], field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0] + 1, enemy_sheep_position[1])):
                return (enemy_sheep_position[0] + 1, enemy_sheep_position[1])

            elif self.is_in_field(enemy_sheep_position[0], enemy_sheep_position[1] + 1, field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0], enemy_sheep_position[1] + 1)):
                return (enemy_sheep_position[0], enemy_sheep_position[1] + 1)

            elif self.is_in_field(enemy_sheep_position[0], enemy_sheep_position[1] - 1, field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0], enemy_sheep_position[1] - 1)):
                return (enemy_sheep_position[0], enemy_sheep_position[1] - 1)

            elif self.is_in_field(enemy_sheep_position[0] - 1, enemy_sheep_position[1], field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0] + 1, enemy_sheep_position[1])):
                return (enemy_sheep_position[0] - 1, enemy_sheep_position[1])
            else:
                return self.get_random_walkable_cell(field, enemy_wolf_position)
        if choice == 3:
            if self.is_in_field(enemy_sheep_position[0], enemy_sheep_position[1] + 1, field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0], enemy_sheep_position[1] + 1)):
                return (enemy_sheep_position[0], enemy_sheep_position[1] + 1)
            elif self.is_in_field(enemy_sheep_position[0], enemy_sheep_position[1] - 1, field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0], enemy_sheep_position[1] - 1)):
                return (enemy_sheep_position[0], enemy_sheep_position[1] - 1)

            elif self.is_in_field(enemy_sheep_position[0] - 1, enemy_sheep_position[1], field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0] + 1, enemy_sheep_position[1])):
                return (enemy_sheep_position[0] - 1, enemy_sheep_position[1])
            elif self.is_in_field(enemy_sheep_position[0] + 1, enemy_sheep_position[1], field) \
                    and not self.is_in_wolf_aura(enemy_wolf_position,
                                                 (enemy_sheep_position[0] + 1, enemy_sheep_position[1])):
                return (enemy_sheep_position[0] + 1, enemy_sheep_position[1])
            else:
                return self.get_random_walkable_cell(field, enemy_wolf_position)

    def get_player_position(self, figure, field):
        x = [x for x in field if figure in x][0]
        return (field.index(x), x.index(figure))

    def food_present(self, field):
        for line in field:
            for item in line:
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    return True
        return False

    def get_random_walkable_cell(self, field, enemy_wolf_position):
        goal = None
        while goal != None:
            rand_y = random.randint(0, 14)
            rand_x = random.randint(0, 18)
            cell = field[y][x]
            wolf_aura = self.get_wolf_aura(enemy_wolf_position)
            if cell != CELL_SHEEP_1 and cell != CELL_SHEEP_2 and cell != CELL_WOLF_1 and cell != CELL_WOLF_2 and cell != CELL_FENCE and cell not in wolf_aura:
                return (rand_y, rand_x)


def AStarSearch(start, end, graph):
    G = {}  # Actual movement cost to each position from the start position
    F = {}  # Estimated movement cost of start to end going via this position

    # Initialize starting values
    G[start] = 0
    F[start] = graph.heuristic(start, end)

    closedVertices = set()
    openVertices = set([start])
    cameFrom = {}

    while len(openVertices) > 0:
        # Get the vertex in the open list with the lowest F score
        current = None
        currentFscore = None
        for pos in openVertices:
            if current is None or F[pos] < currentFscore:
                currentFscore = F[pos]
                currentGscore = G[pos]
                current = pos

        # Check if we have reached the goal
        if current == end:
            # Retrace our route backward
            path = [current]
            while current in cameFrom:
                current = cameFrom[current]
                path.append(current)
            path.reverse()
            return (path, currentGscore)  # Done!

        # Mark the current vertex as closed
        openVertices.remove(current)
        closedVertices.add(current)

        # Update scores for vertices near the current position
        for neighbour in graph.get_vertex_neighbours(current, graph):
            if neighbour in closedVertices:
                continue  # We have already processed this node exhaustively

            candidateG = G[current] + graph.move_cost(current, neighbour)

            if neighbour not in openVertices:
                openVertices.add(neighbour)  # Discovered a new vertex
            elif candidateG >= G[neighbour]:
                continue  # This G score is worse than previously found

            # Adopt this G score
            cameFrom[neighbour] = current
            G[neighbour] = candidateG
            H = graph.heuristic(neighbour, end)
            F[neighbour] = G[neighbour] + H

    raise RuntimeError("A* failed to find a solution")


class AStarGraph(object):
    # Define a class board like grid with two barriers

    def __init__(self, field, player_number, ignore_wolf=False, is_wolf=False):
        self.barriers = []
        self.grasses = []
        self.rhubarbs = []
        self.wolf_aura = []

        self.ignore_wolf = ignore_wolf
        self.is_wolf = is_wolf

        if player_number == 1:
            self.sheep = CELL_SHEEP_1
            self.enemy_wolf = CELL_WOLF_2
        else:
            self.sheep = CELL_SHEEP_2
            self.enemy_wolf = CELL_WOLF_1

        self.my_sheep = player_number
        self.barriers = self.set_barriers(field)
        self.grasses = self.set_grasses(field)
        self.rhubarbs = self.set_rhubarbs(field)
        self.wolf_aura = self.set_wolf_aura(field)

    def heuristic(self, start, goal):
        # Use Chebyshev distance heuristic if we can move one square either
        # adjacent or diagonal
        D = 1
        D2 = 1
        dx = abs(start[0] - goal[0])
        dy = abs(start[1] - goal[1])
        # return D * (dx + dy) + (D2 - 2 * D) * min(dx, dy)
        return (dx + dy)

    def get_vertex_neighbours(self, pos, graph):
        n = []
        # Moves allow link a chess king
        for dy, dx in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            y2 = pos[0] + dy
            x2 = pos[1] + dx
            if y2 < 0 or y2 > 14 or x2 < 0 or x2 > 18:
                continue
            if (y2, x2) in graph.barriers[0]:
                continue

            n.append((y2, x2))
        return n

    def move_cost(self, a, b):
        if b in self.barriers:
            return 100000000
        # else:
        #     return 1

        if self.is_wolf:
            if b in self.grasses:
                return 2
            if b in self.rhubarbs:
                return 10
            return 1

        else:
            if b in self.wolf_aura:
                return 1000000000
            if b in self.grasses:
                return 0.5
            if b in self.rhubarbs:
                return 0.2
            return 1

    def set_barriers(self, field):
        barriers = []
        for y, line in enumerate(field, 0):
            for x, cell in enumerate(line, 0):

                # add barriers around the wolf too in order not to step next to the wolf
                if cell == self.enemy_wolf:
                    barriers.append((y, x))

                elif cell != CELL_EMPTY and cell != self.sheep and cell != CELL_RHUBARB and cell != CELL_GRASS:
                    barriers.append((y, x))

        return barriers

    def set_grasses(self, field):
        grasses = []
        for y, line in enumerate(field, 0):
            for x, cell in enumerate(line, 0):
                if cell == CELL_GRASS:
                    grasses.append((y, x))
        return grasses

    def set_rhubarbs(self, field):
        rhubarbs = []
        for y, line in enumerate(field, 0):
            for x, cell in enumerate(line, 0):
                if cell == CELL_RHUBARB:
                    rhubarbs.append((y, x))
        return rhubarbs

    def set_wolf_aura(self, field):
        wolf_aura = []
        for y, line in enumerate(field, 0):
            for x, cell in enumerate(line, 0):
                if cell == self.enemy_wolf:
                    if y + 1 < 15:
                        wolf_aura.append((y, x + 1))
                    if x + 1 < 19:
                        wolf_aura.append((y + 1, x))
                    if y - 1 >= 0:
                        wolf_aura.append((y - 1, x))
                    if x - 1 >= 0:
                        wolf_aura.append((y, x - 1))
        return wolf_aura


def print_sparse_dict(d):
    filtered_dict = {}
    for key, value in d.items():
        if value != 0 and value != []:
            filtered_dict[key] = value

    return filtered_dict
