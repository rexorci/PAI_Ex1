import copy
import functools
import random
import time
from collections import defaultdict
from math import inf
from operator import itemgetter
from typing import Tuple

from config import *

AWARDS = defaultdict(lambda: 0)
AWARDS[CELL_RHUBARB] = AWARD_RHUBARB
AWARDS[CELL_GRASS] = AWARD_GRASS


def timed(func):
    """
    Decorator to time functions.

    Usage:
    >>> @timed
    ... def my_function(x):
    ...     for _ in range(x):
    ...         time.sleep(1)
    ...
    >>> my_function(5)
    [my_function] computation took 5.002752065658569s
    """
    @functools.wraps(func)
    def timed_wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("[{}] computation took {}s".format(func.__qualname__, end - start))
        return result
    return timed_wrapper


class Field(dict):
    def __init__(self, field):
        super().__init__()
        for y, row in enumerate(field):
            for x, cell in enumerate(row):
                self[(x, y)] = cell
        self.width = len(field[0])
        self.height = len(field)

    def get_neighbors(self, position):
        x, y = position

        neighbors = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1)
        ]

        for neighbor in neighbors:
            item = self.get(neighbor)
            if not item:
                continue
            if item == CELL_FENCE:
                continue
            if item == CELL_WOLF_1:
                continue
            if item == CELL_WOLF_2:
                continue

            yield neighbor

    def get_positions(self, *figures):
        return [k for k, v in self.items() if v in figures]

    def get_first_position(self, figure):
        try:
            return [k for k, v in self.items() if v == figure][0]
        except IndexError:
            return None

    def __str__(self):
        longest = max(len(str(x)) for x in self.values())
        return '\n'.join(' '.join(str(self[(x, y)]).ljust(longest) for x in range(self.width)) for y in range(self.height))

    @staticmethod
    def filled(value, width, height):
        return Field([[value for _ in range(width)] for _ in range(height)])


def get_move(pos1, pos2):
    x1, y1 = pos1
    x2, y2 = pos2

    delta_x = x1 - x2
    delta_y = y1 - y2
    if delta_x == -1:
        return MOVE_RIGHT
    elif delta_x == 1:
        return MOVE_LEFT
    elif delta_y == -1:
        return MOVE_DOWN
    elif delta_y == 1:
        return MOVE_UP
    else:
        return MOVE_NONE


def enemy(figure):
    if figure == CELL_SHEEP_1:
        return CELL_SHEEP_2
    elif figure == CELL_SHEEP_2:
        return CELL_SHEEP_1
    elif figure == CELL_WOLF_1:
        return CELL_WOLF_2
    elif figure== CELL_WOLF_2:
        return CELL_WOLF_1


def my_wolf(figure):
    return CELL_WOLF_1 if figure == CELL_SHEEP_1 else CELL_WOLF_2


def my_sheep(figure):
    return CELL_SHEEP_1 if figure == CELL_WOLF_1 else CELL_SHEEP_2


def manhattan_distance(xy1, xy2):
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])


def trace(target, predecessors):
    route = []
    predecessor = target
    while predecessor is not None:
        route.append(predecessor)
        predecessor = predecessors[predecessor]
    return list(reversed(route))


def bellman_ford(field: Field, source: Tuple[int, int], cost_function=lambda p1, p2, f: 1):
    distance = Field.filled(inf, field.width, field.height)
    predecessor = Field.filled(None, field.width, field.height)

    distance[source] = 0
    edges = [(position, neighbor) for position in field for neighbor in field.get_neighbors(position)]
    for _ in range(len(field)):
        for position, neighbor in edges:
            movement_cost = distance[position] + cost_function(position, neighbor, field)
            if movement_cost < distance[neighbor]:
                distance[neighbor] = movement_cost
                predecessor[neighbor] = position

    for position, neighbor in edges:
        movement_cost = distance[position] + cost_function(position, neighbor, field)
        if distance[position] + movement_cost < distance[neighbor]:
            raise ValueError("negative cycle")

    return distance, predecessor


def dijkstra(field: Field, source: Tuple[int, int], cost_function=lambda p1, p2, f: 1):
    distance = Field.filled(inf, field.width, field.height)
    predecessor = Field.filled(None, field.width, field.height)

    distance[source] = 0
    q = copy.deepcopy(field)

    # TODO use heapq
    while q:
        u = min(q, key=distance.get)
        q.pop(u)

        neighbors = list(field.get_neighbors(u))
        random.shuffle(neighbors)
        for v in neighbors:
            alt = distance[u] + cost_function(u, v, field)
            if alt < distance[v]:
                distance[v] = alt
                predecessor[v] = u

    return distance, predecessor


def a_star(start, goal, field, cost_function=lambda p1, p2, f: 1):

    def reconstruct_path(came_from, current):
        total_path = [current]
        while current in came_from:
            current = came_from[current]
            total_path.append(current)
        return total_path[:-1]

    closed_set = set()
    open_set = {start}
    came_from = {}

    g_score = defaultdict(lambda x: inf)
    g_score[start] = 0

    f_score = defaultdict(lambda x: inf)
    f_score[start] = manhattan_distance(start, goal)

    while open_set:
        _, current_position = min(((f_score[pos], pos) for pos in open_set), key=itemgetter(0))

        if current_position == goal:
            return reconstruct_path(came_from, current_position), f_score[goal]

        open_set.remove(current_position)
        closed_set.add(current_position)

        for neighbor in field.get_neighbors(current_position):
            if neighbor in closed_set:
                continue

            tentative_g_score = g_score[current_position] + cost_function(current_position, neighbor, field)

            if neighbor not in open_set:
                open_set.add(neighbor)
            elif tentative_g_score >= g_score[neighbor]:
                continue

            came_from[neighbor] = current_position
            g_score[neighbor] = tentative_g_score
            f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, goal)


def get_sheep_cost_function(enemy_sheep, enemy_wolf):
    def sheep_cost_function(move_from, move_to, field):
        cell_type = field[move_to]
        if cell_type == enemy_wolf or cell_type == enemy(enemy_wolf) or cell_type == enemy_sheep:
            return inf

        neighbors = list(field.get_neighbors(move_to))
        mobility = len(neighbors)
        wolf_position = field.get_first_position(enemy_wolf)
        wolf_distance = manhattan_distance(wolf_position, move_to)
        try:
            wolf_cost = 1 / (wolf_distance - 2)
        except ZeroDivisionError:
            wolf_cost = 100000

        value_cost = max(AWARDS.values()) - AWARDS.get(cell_type, 0)
        mobility_cost = 4 - mobility
        cost = 1 + value_cost + mobility_cost + 10 * wolf_cost
        return round(cost, 0)
    return sheep_cost_function


def get_wolf_cost_function(my_sheep):
    def wolf_cost_function(move_from, move_to, field):
        cell_type = field[move_to]

        try:
            my_sheep_position = field.get_first_position(my_sheep)
            enemy_sheep_position = field.get_first_position(enemy(my_sheep))

            distance_to_my_sheep = manhattan_distance(my_sheep_position, move_to)
            distance_to_enemy_sheep = manhattan_distance(enemy_sheep_position, move_to)

            modifier = distance_to_my_sheep - distance_to_enemy_sheep
        except IndexError:
            modifier = 1

        return 1 + -modifier * AWARDS.get(cell_type, 0)

    return wolf_cost_function


def route_towards_food(sheep, foods, field):
    enemy_sheep = enemy(sheep)
    wolf = my_wolf(sheep)
    enemy_wolf = enemy(wolf)
    distance, predecessor = dijkstra(field, field.get_first_position(sheep), get_sheep_cost_function(enemy_sheep, enemy_wolf))
    distance_enemy, predecessor_enemy = dijkstra(field, field.get_first_position(enemy_sheep), get_sheep_cost_function(sheep, wolf))

    print(distance)
    random.shuffle(foods)
    closest_distance = inf
    goal = None
    for food in foods:
        if distance[food] - AWARDS[field[food]] < closest_distance:
            closest_distance = distance[food] - AWARDS[field[food]]
            goal = food

    return list(trace(goal, predecessor))


def flee_from_wolf(sheep, field):
    my_position = field.get_first_position(sheep)
    distance, predecessor = dijkstra(field, my_position, get_sheep_cost_function(enemy(sheep), enemy(my_wolf(sheep))))
    distance.pop(my_position)
    for n in field.get_neighbors(my_position):
        distance.pop(n)

    route = trace(min(distance, key=distance.get), predecessor)
    move_from, move_to, *_ = route
    return get_move(move_from, move_to)


def get_class_name():
    return 'AwesomeAgent'


class AwesomeAgent:
    """Example class for a Kingsheep player"""

    def __init__(self):
        self.name = "Move, sheep, get out the way"
        self.uzh_shortname = "pduegg"
        self.player_number = None

    @property
    def my_wolf(self):
        return my_wolf(self.my_sheep)

    @property
    def enemy_wolf(self):
        return enemy(self.my_wolf)

    @property
    def my_sheep(self):
        return CELL_SHEEP_1 if self.player_number == 1 else CELL_SHEEP_2

    @property
    def enemy_sheep(self):
        return enemy(self.my_sheep)

    @timed
    def move_sheep(self, player_number: int, field):
        self.player_number = player_number
        field = Field(field)
        foods = field.get_positions(CELL_GRASS, CELL_RHUBARB)

        if foods:
            route = route_towards_food(self.my_sheep, foods, field)
            if route:
                move_from, move_to, *_ = route
                return get_move(move_from, move_to)

        return flee_from_wolf(self.my_sheep, field)

    @timed
    def move_wolf(self, player_number: int, field):
        self.player_number = player_number
        field = Field(field)

        goal = field.get_first_position(self.enemy_sheep)

        foods = field.get_positions(CELL_GRASS, CELL_RHUBARB)
        if foods:
            enemy_route = route_towards_food(self.enemy_sheep, foods, field)
            if enemy_route:
                goal = enemy_route[-1]

        me = self.my_wolf
        my_position = field.get_first_position(me)

        try:
            wolf_route, cost = a_star(my_position, goal, field, get_wolf_cost_function(self.my_sheep))
            next_position = wolf_route.pop()
            return get_move(my_position, next_position)
        except TypeError:  # No route to sheep
            return MOVE_NONE