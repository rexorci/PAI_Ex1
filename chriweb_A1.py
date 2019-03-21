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
from collections import defaultdict
from operator import itemgetter

from config import *


def get_class_name():
    return 'IntrepidIbex'


class IntrepidIbex():
    """Example class for a Kingsheep player"""

    def __init__(self):
        self.name = "Intrepid Ibex"
        self.uzh_shortname = "chriweb"

    def get_player_position(self, figure, field):
        x = [x for x in field if figure in x][0]
        return (field.index(x), x.index(figure))

    # defs for sheep
    def move_sheep(self, player_number, field):
        if player_number == 1:
            figure = CELL_SHEEP_1
        else:
            figure = CELL_SHEEP_2

        if self.wolf_close(player_number, field):
            # print('wolf close move')
            return self.run_from_wolf(player_number, field)
        elif self.food_present(field):
            # print('gather food move')
            return self.gather_move_sheep(field, figure, player_number)
        else:
            return MOVE_NONE

    def wolf_close(self, player_number, field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
            wolf_position = self.get_player_position(CELL_WOLF_2, field)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)
            wolf_position = self.get_player_position(CELL_WOLF_1, field)

        if (abs(sheep_position[0] - wolf_position[0]) <= 2 and abs(sheep_position[1] - wolf_position[1]) <= 2):
            # print('wolf is close')
            return True
        return False

    def run_from_wolf(self, player_number, field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
            wolf_position = self.get_player_position(CELL_WOLF_2, field)
            sheep = CELL_SHEEP_1
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)
            wolf_position = self.get_player_position(CELL_WOLF_1, field)
            sheep = CELL_SHEEP_2

        distance_x = sheep_position[1] - wolf_position[1]
        abs_distance_x = abs(sheep_position[1] - wolf_position[1])
        distance_y = sheep_position[0] - wolf_position[0]
        abs_distance_y = abs(sheep_position[0] - wolf_position[0])

        # TODO maybe distance bigger than 1 to flee earlier
        # print('player_number %i' %player_number)
        # print('running from wolf')
        # if the wolf is close vertically
        if abs_distance_y == 1 and distance_x == 0:
            # print('wolf is close vertically')
            # if it's above the sheep, move down if possible
            if distance_y > 0:
                if self.valid_move(sheep, sheep_position[0] + 1, sheep_position[1], field):
                    return MOVE_DOWN
            else:  # it's below the sheep, move up if possible
                if self.valid_move(sheep, sheep_position[0] - 1, sheep_position[1], field):
                    return MOVE_UP
            # if this is not possible, flee to the right or left
            if self.valid_move(sheep, sheep_position[0], sheep_position[1] + 1, field):
                return MOVE_RIGHT
            elif self.valid_move(sheep, sheep_position[0], sheep_position[1] - 1, field):
                return MOVE_LEFT
            else:  # nowhere to go
                return MOVE_NONE

        # else if the wolf is close horizontally
        elif abs_distance_x == 1 and distance_y == 0:
            # print('wolf is close horizontally')
            # if it's to the left, move to the right if possible
            if distance_x > 0:
                if self.valid_move(sheep, sheep_position[0], sheep_position[1] - 1, field):
                    return MOVE_RIGHT
            else:  # it's to the right, move left if possible
                if self.valid_move(sheep, sheep_position[0], sheep_position[1] + 1, field):
                    return MOVE_RIGHT
            # if this is not possible, flee up or down
            if self.valid_move(sheep, sheep_position[0] - 1, sheep_position[1], field):
                return MOVE_UP
            elif self.valid_move(sheep, sheep_position[0] + 1, sheep_position[1], field):
                return MOVE_DOWN
            else:  # nowhere to go
                return MOVE_NONE

        elif abs_distance_x == 1 and abs_distance_y == 1:
            # print('wolf is in my surroundings')
            # wolf is left and up
            if distance_x > 0 and distance_y > 0:
                # move right or down
                if self.valid_move(sheep, sheep_position[0], sheep_position[1] + 1, field):
                    return MOVE_RIGHT
                else:
                    return MOVE_DOWN
            # wolf is left and down
            if distance_x > 0 and distance_y < 0:
                # move right or up
                if self.valid_move(sheep, sheep_position[0], sheep_position[1] + 1, field):
                    return MOVE_RIGHT
                else:
                    return MOVE_UP
            # wolf is right and up
            if distance_x < 0 and distance_y > 0:
                # move left or down
                if self.valid_move(sheep, sheep_position[0], sheep_position[1] - 1, field):
                    return MOVE_LEFT
                else:
                    return MOVE_DOWN
            # wolf is right and down
            if distance_x < 0 and distance_y < 0:
                # move left and up
                if self.valid_move(sheep, sheep_position[0], sheep_position[1] - 1, field):
                    return MOVE_LEFT
                else:
                    return MOVE_UP
        else:  # this method was wrongly called
            return MOVE_NONE

    def food_present(self, field):
        food_present = False

        for line in field:
            for item in line:
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    food_present = True
                    break
        return food_present

    def gather_move_sheep(self, field, figure, player_number):
        """
        1. get all targets
        2. calculate heuristics for all
        3. calculate real distance with a* on best heuristic
        4. repeat on all where real distance is bigger than heuristic
        """

        possible_goals = self.get_possible_sheep_goals(player_number, field)
        best_heuristic_goal = possible_goals[0]

        reverse_path, f_score = self.a_star_wiki((best_heuristic_goal[0], best_heuristic_goal[1]), figure, field)
        return self.determine_move_direction(reverse_path[-2], field, figure)

    def get_possible_sheep_goals(self, player_number, field):
        # contains y_pos, x_pos, heuristic
        possible_goals = []

        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)

        y_position = 0
        for line in field:
            x_position = 0
            for item in line:
                # TODO rhabarber mehr gewichten (weil 5 punkte)
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    # TODO evtl. "gewicht" für fence (zählt distanz 2.5/addiere distanz (was ist minimum um fence auszuweichen?)
                    possible_goals.append((y_position, x_position,
                                           self.get_distance_heuristic((y_position, x_position), sheep_position)))
                x_position += 1
            y_position += 1

        return sorted(possible_goals, key=itemgetter(2))

    # defs for wolf
    def move_wolf(self, player_number, field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)
            return self.determine_wolf_action(sheep_position, field, CELL_WOLF_1)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
            return self.determine_wolf_action(sheep_position, field, CELL_WOLF_2)

        return MOVE_NONE

    def determine_wolf_action(self, closest_goal, field, figure):
        figure_position = self.get_player_position(figure, field)

        distance_x = figure_position[1] - closest_goal[1]
        distance_y = figure_position[0] - closest_goal[0]

        if distance_x == 0:
            # print('item right above/below me')
            if distance_y > 0:
                if self.valid_move(figure, figure_position[0] - 1, figure_position[1], field):
                    return MOVE_UP
                else:
                    return MOVE_RIGHT
            else:
                if self.valid_move(figure, figure_position[0] + 1, figure_position[1], field):
                    return MOVE_DOWN
                else:
                    return MOVE_RIGHT
        elif distance_y == 0:
            # print('item right beside me')
            if distance_x > 0:
                if self.valid_move(figure, figure_position[0], figure_position[1] - 1, field):

                    return MOVE_LEFT
                else:
                    return MOVE_UP
            else:
                if self.valid_move(figure, figure_position[0], figure_position[1] + 1, field):
                    return MOVE_RIGHT
                else:
                    return MOVE_UP

        else:
            # go left or up
            if distance_x > 0 and distance_y > 0:
                if self.valid_move(figure, figure_position[0], figure_position[1] - 1, field):
                    return MOVE_LEFT
                else:
                    return MOVE_UP

            # go left or down
            elif distance_x > 0 and distance_y < 0:
                if self.valid_move(figure, figure_position[0], figure_position[1] - 1, field):
                    return MOVE_LEFT
                else:
                    return MOVE_DOWN

            # go right or up
            elif distance_x < 0 and distance_y > 0:
                if self.valid_move(figure, figure_position[0], figure_position[1] + 1, field):
                    return MOVE_RIGHT
                else:
                    return MOVE_UP

            # go right or down
            elif distance_x < 0 and distance_y < 0:
                if self.valid_move(figure, figure_position[0], figure_position[1] + 1, field):
                    return MOVE_RIGHT
                else:
                    return MOVE_DOWN

            else:
                print('fail')
                return MOVE_NONE

    # neutral defs
    def a_star_wiki(self, goal, figure, field, cost_function=lambda x, y: 1):
        start = self.get_player_position(figure, field)
        closed_set = set()
        open_set = {start}
        came_from = {}

        g_score = defaultdict(lambda x: 1000)
        g_score[start] = 0

        f_score = defaultdict(lambda x: 1000)
        f_score[start] = self.get_distance_heuristic(start, goal)

        while open_set:
            _, current_position = min(((f_score[pos], pos) for pos in open_set), key=itemgetter(0))

            if current_position == goal:
                return self.reconstruct_path(came_from, current_position), f_score[goal]

            open_set.remove(current_position)
            closed_set.add(current_position)

            neighbors = self.get_valid_moves(figure, current_position, field)
            for neighbor in neighbors:
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current_position] + cost_function(field, neighbor)

                if neighbor not in open_set:
                    open_set.add(neighbor)
                elif tentative_g_score >= g_score[neighbor]:
                    continue

                came_from[neighbor] = current_position
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + self.get_distance_heuristic(neighbor, goal)

    def determine_move_direction(self, coord, field, figure):
        figure_position = self.get_player_position(figure, field)

        distance_x = figure_position[1] - coord[1]
        distance_y = figure_position[0] - coord[0]

        if distance_x == 1:
            return MOVE_LEFT
        elif distance_x == -1:
            return MOVE_RIGHT
        elif distance_y == 1:
            return MOVE_UP
        elif distance_y == -1:
            return MOVE_DOWN
        else:
            return MOVE_NONE

    def get_valid_moves(self, figure, position, field):
        valid_moves = []
        if self.valid_move(figure, position[0] - 1, position[1], field):
            valid_moves.append((position[0] - 1, position[1]))
        if self.valid_move(figure, position[0] + 1, position[1], field):
            valid_moves.append((position[0] + 1, position[1]))
        if self.valid_move(figure, position[0], position[1] + 1, field):
            valid_moves.append((position[0], position[1] + 1))
        if self.valid_move(figure, position[0], position[1] - 1, field):
            valid_moves.append((position[0], position[1] - 1))
        return valid_moves

    @staticmethod
    def reconstruct_path(came_from, current):
        reverse_path = [current]
        while current in came_from:
            current = came_from[current]
            reverse_path.append(current)
        return reverse_path

    @staticmethod
    def get_distance_heuristic(origin, goal):
        return abs(origin[0] - goal[0]) + abs(origin[1] - goal[1])

    @staticmethod
    def valid_move(figure, x_new, y_new, field):
        # Neither the sheep nor the wolf, can step on a square outside the map. Imagine the map is surrounded by fences.
        if x_new > FIELD_HEIGHT - 1:
            return False
        elif x_new < 0:
            return False
        elif y_new > FIELD_WIDTH - 1:
            return False
        elif y_new < 0:
            return False

        # Neither the sheep nor the wolf, can enter a square with a fence on.
        if field[x_new][y_new] == CELL_FENCE:
            return False

        # Wolfs can not step on squares occupied by the opponents wolf (wolfs block each other).
        # Wolfs can not step on squares occupied by the sheep of the same player .
        if figure == CELL_WOLF_1:
            if field[x_new][y_new] == CELL_WOLF_2:
                return False
            elif field[x_new][y_new] == CELL_SHEEP_1:
                return False
        elif figure == CELL_WOLF_2:
            if field[x_new][y_new] == CELL_WOLF_1:
                return False
            elif field[x_new][y_new] == CELL_SHEEP_2:
                return False

        # Sheep can not step on squares occupied by the wolf of the same player.
        # Sheep can not step on squares occupied by the opposite sheep.
        if figure == CELL_SHEEP_1:
            if field[x_new][y_new] == CELL_SHEEP_2 or \
                    field[x_new][y_new] == CELL_WOLF_1:
                return False
        elif figure == CELL_SHEEP_2:
            if field[x_new][y_new] == CELL_SHEEP_1 or \
                    field[x_new][y_new] == CELL_WOLF_2:
                return False

        return True
