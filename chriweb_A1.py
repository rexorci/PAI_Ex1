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
    def food_present(self, field):
        food_present = False

        for line in field:
            for item in line:
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    food_present = True
                    break
        return food_present

    def closest_goal(self, player_number, field):
        possible_goals = []

        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)

        # make list of possible goals

        # TODO speedup possible?
        # TODO rhabarber mehr gewichten (weil 5 punkte)
        y_position = 0
        for line in field:
            x_position = 0
            for item in line:
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    possible_goals.append((y_position, x_position))
                x_position += 1
            y_position += 1

        # determine closest item and return
        # TODO evtl. "gewicht" für fence (zählt distanz 2.5?)
        distance = 1000
        for possible_goal in possible_goals:
            if (abs(possible_goal[0] - sheep_position[0]) + abs(possible_goal[1] - sheep_position[1])) < distance:
                distance = abs(possible_goal[0] - sheep_position[0]) + abs(possible_goal[1] - sheep_position[1])
                final_goal = (possible_goal)

        return final_goal

    def gather_closest_goal(self, closest_goal, field, figure):
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

    def valid_move(self, figure, x_new, y_new, field):
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
            return self.gather_move_astar(field, figure, player_number)
            # return self.gather_closest_goal(self.closest_goal_astar(player_number,field),field,figure)
            # return self.gather_closest_goal(self.closest_goal(player_number,field),field,figure)
        else:
            return MOVE_NONE

    def gather_move_astar(self, field, figure, player_number):
        """
        1. get all targets
        2. calculate heuristics for all
        3. calculate real distance with a* on best heuristic
        4. repeat on all where real distance is bigger than heuristic
        """

        possible_goals = self.get_possible_goals(player_number, field)
        # TODO handle if no goals!
        best_heuristic_goal = possible_goals[0]
        # self.real_distance_astar(best_heuristic_goal, figure, field, 1)

        reverse_path, f_score = self.a_star_wiki((best_heuristic_goal[0], best_heuristic_goal[1]), figure, field)
        return self.determine_move_direction(reverse_path[-2], field, figure)


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

    class Node:
        def __init__(self, parent=None, position=None):
            self.parent = parent
            self.position = position

            self.g = 0
            self.h = 0
            self.f = 0

        def __eq__(self, other):
            return self.position == other.position

    def a_star_medium(self, goal, figure, field):
        start_node = self.Node(None, self.get_player_position(figure, field))
        start_node.g = start_node.h = start_node.f = 0
        end_node = self.Node(None, goal)
        end_node.g = end_node.h = end_node.f = 0

        open_list = []
        closed_list = []
        open_list.append(start_node)

        while open_list:
            current_node = min(open_list, key=lambda x: x.f)
            # current_index = 0
            # current_node_coord = min(open_list.keys(), key=lambda x: open_list[x][2])
            # current_node_val = open_list[current_node_coord]

            open_list.remove(current_node)
            # del open_list[current_node_coord]
            closed_list.append(current_node)
            # closed_list[current_node_coord] = current_node_val

            # if (goal[0] == current_node_coord[0]) and (goal[1] == current_node_coord[1]):
            if current_node == end_node:
                path = []
                print('success')
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1]  # Return reversed path

            children = []
            if self.valid_move(figure, current_node.position[0] - 1, current_node.position[1] - 1, field):
                children.append(self.Node(current_node, (current_node.position[0] - 1, current_node.position[1] - 1)))
            if self.valid_move(figure, current_node.position[0] + 1, current_node.position[1] - 1, field):
                children.append(self.Node(current_node, (current_node.position[0] + 1, current_node.position[1] - 1)))
            if self.valid_move(figure, current_node.position[0] - 1, current_node.position[1] + 1, field):
                children.append(self.Node(current_node, (current_node.position[0] - 1, current_node.position[1] + 1)))
            if self.valid_move(figure, current_node.position[0] + 1, current_node.position[1] + 1, field):
                children.append(self.Node(current_node, (current_node.position[0] + 1, current_node.position[1] + 1)))

            for child in children:
                # TODO value compare?
                if child in closed_list:
                    continue

                child.g = current_node.g + 1
                child.h = self.get_distance_heuristic(child.position[0], child.position[1], goal[0], goal[1])
                child.f = child.g + child.h

                # Child is already in the open list
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue

                # Add the child to the open list
                open_list.append(child)

    @staticmethod
    def reconstruct_path(came_from, current):
        reverse_path = [current]
        while current in came_from:
            current = came_from[current]
            reverse_path.append(current)
        return reverse_path

    def get_valid_moves(self, figure, position, field):
        valid_moves = []
        if self.valid_move(figure, position[0] - 1, position[1], field):
            valid_moves.append((position[0] - 1, position[1]))
        if self.valid_move(figure, position[0] + 1, position[1], field):
            valid_moves.append((position[0] + 1, position[1]))
        if self.valid_move(figure, position[0], position[1] + 1, field):
            valid_moves.append((position[0], position[1] + 1))
        if self.valid_move(figure, position[0], position[1] + 1, field):
            valid_moves.append((position[0], position[1] + 1))
        return valid_moves

    def a_star_wiki(self, goal, figure, field, cost_function=lambda x, y: 1):
        # start_node = self.Node(None, self.get_player_position(figure, field))

        start = self.get_player_position(figure, field)
        closed_set = set()
        open_set = {start}
        came_from = {}

        g_score = defaultdict(lambda x: 1000)
        g_score[start] = 0

        f_score = defaultdict(lambda x: 1000)
        f_score[start] = self.get_distance_heuristic(start, goal)

        # self.get_distance_heuristic(child.position[0], child.position[1], goal[0], goal[1])

        while open_set:
            _, current_position = min(((f_score[pos], pos) for pos in open_set), key=itemgetter(0))

            if current_position == goal:
                return self.reconstruct_path(came_from, current_position), f_score[goal]

            open_set.remove(current_position)
            closed_set.add(current_position)

            for neighbor in self.get_valid_moves(figure, current_position, field):
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


        print('should not be here') # TODO error here!
    # def a_star_wiki(self, start, goal, field, cost_function=lambda x, y: 1):
    #     closed_set = set()
    #     open_set = {start}
    #     came_from = {}
    #
    #     g_score = defaultdict(lambda x: 1000)
    #     g_score[start] = 0
    #
    #     f_score = defaultdict(lambda x: 1000)
    #     f_score[start] = manhattan_distance(start, goal)
    #
    #     while open_set:
    #         _, current_position = min(((f_score[pos], pos) for pos in open_set), key=itemgetter(0))
    #
    #         if current_position == goal:
    #             return reconstruct_path(came_from, current_position), f_score[goal]
    #
    #         open_set.remove(current_position)
    #         closed_set.add(current_position)
    #
    #         for neighbor in self.get_neighbors(field, current_position):
    #             if neighbor in closed_set:
    #                 continue
    #
    #             tentative_g_score = g_score[current_position] + cost_function(field, neighbor)
    #
    #             if neighbor not in open_set:
    #                 open_set.add(neighbor)
    #             elif tentative_g_score >= g_score[neighbor]:
    #                 continue
    #
    #             came_from[neighbor] = current_position
    #             g_score[neighbor] = tentative_g_score
    #             f_score[neighbor] = g_score[neighbor] + manhattan_distance(neighbor, goal)

    # defs for wolf
    def move_wolf(self, player_number, field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)
            return self.gather_closest_goal(sheep_position, field, CELL_WOLF_1)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
            return self.gather_closest_goal(sheep_position, field, CELL_WOLF_2)

        return MOVE_NONE

    def get_possible_goals(self, player_number, field):
        # constains y_pos, x_pos, heuristic
        possible_goals = []

        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1, field)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2, field)

        y_position = 0
        for line in field:
            x_position = 0
            for item in line:
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    # TODO evtl. "gewicht" für fence (zählt distanz 2.5/addiere distanz (was ist minimum um fence auszuweichen?)
                    possible_goals.append((y_position, x_position,
                                           self.get_distance_heuristic((y_position, x_position), sheep_position)))
                x_position += 1
            y_position += 1

        return sorted(possible_goals, key=itemgetter(2))

    @staticmethod
    def get_distance_heuristic(origin, goal):
        return abs(origin[0] - goal[0]) + abs(origin[1] - goal[1])

    # def closest_goal_astar(self, player_number, field):
    #     possible_goals = []
    #
    #     if player_number == 1:
    #         sheep_position = self.get_player_position(CELL_SHEEP_1, field)
    #     else:
    #         sheep_position = self.get_player_position(CELL_SHEEP_2, field)
    #
    #     # make list of possible goals
    #
    #     # TODO speedup possible?
    #     # TODO rhabarber mehr gewichten (weil 5 punkte)
    #     y_position = 0
    #     for line in field:
    #         x_position = 0
    #         for item in line:
    #             if item == CELL_RHUBARB or item == CELL_GRASS:
    #                 # TODO evtl. "gewicht" für fence (zählt distanz 2.5?)
    #                 possible_goals.append((y_position, x_position,
    #                                        (abs(y_position - sheep_position[0]) + abs(x_position - sheep_position[1]))))
    #             x_position += 1
    #         y_position += 1
    #
    #     # expand nearest node
    #     distance = 1000
    #     for possible_goal in possible_goals:
    #         if possible_goal[2] < distance:
    #             distance = possible_goal[2]
    #             temp_goal = (possible_goal)
    #
    #     final_goal = self.expand_node_astar(temp_goal, possible_goals, field)
    #     # # determine closest item and return
    #     # distance = 1000
    #     # for possible_goal in possible_goals:
    #     #     if (abs(possible_goal[0] - sheep_position[0]) + abs(possible_goal[1] - sheep_position[1])) < distance:
    #     #         distance = abs(possible_goal[0] - sheep_position[0]) + abs(possible_goal[1] - sheep_position[1])
    #     #         final_goal = (possible_goal)
    #
    #     return final_goal

    # def expand_node_astar(self, position, possible_goals_old, field):
    #     possible_goals = []
    #     y_position = 0
    #     # remove the eaten field to prevent loops
    #     field[position[0]][position[1]] = '.'
    #     for line in field:
    #         x_position = 0
    #         for item in line:
    #             if item == CELL_RHUBARB or item == CELL_GRASS:
    #                 # TODO evtl. "gewicht" für fence (zählt distanz 2.5?)
    #                 # use smaller value for astar
    #                 possible_goals_old
    #                 possible_goals.append((y_position, x_position, (abs(y_position - position[0]) + abs(x_position - position[1]))))
    #             x_position += 1
    #         y_position += 1
