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

"""
в основе гриди, ищет ближайшую еду не по прямой,а нормально(с учетом препятствий)
в подсчете цены еды учитывает наличие еды вокруг, расстояние 
до овцы противника до этой еды и расстояние своей овцы до этой еды

когда убегает от волка, делает это не произвольно, а  пытается съесть ближайшую 
еду в сторону от волка: 
вызывает функцию съесть еду и передает туда не всё поле, а подполе без волка

волк при выборе шага для погони за овцой считает расстояние до нее не по прямой,
а с учетом препятствий

убегать от волка если расстояние <=  2 шага (раньше если было =2, овца стояла 
на месте)
добавлена функция distance, которая считает расстояние между двумя клетками
"""

import numpy as np

from collections import deque
from config import *

class Node(object):
    def __init__(self,pos_y,pos_x,move,distance):
        self.position = (pos_y, pos_x)
        self.move = move
        self.distance = distance
        self.children = []
    def add_children(self, obj):
        self.children.append(obj)

# field = [[0 for x in range(5)] for y in range(6)]


def get_class_name():
    return 'Barash'

class Barash():
    """Example class for a Kingsheep player"""

    def __init__(self):
        self.name = "Barash"
        self.uzh_shortname = "imovse"

    def get_player_position(self,figure,field):
        x = [x for x in field if figure in x]
        if len(x) == 0:
            return (-1,-1)
        x = x[0]
        return (field.index(x), x.index(figure))

    def food_present(self,field):
        food_present = False

        for line in field: 
            for item in line:
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    food_present = True
                    break
        return food_present

    def distance(self,to_position,from_position,field):
        
        queue = deque()
        marked = []
        move = 'p'
        tree = Node(from_position[0],from_position[1],move,0)
        queue.append(tree)
        marked.append(tree.position)

        while queue:
            parent = queue.popleft()
            if parent.position == to_position:
                return parent.distance

            if (not (parent.position[0]-1, parent.position[1]) in marked) and self.no_obstacles(parent.position[0]-1, parent.position[1],field):
                new_node = Node(parent.position[0]-1, parent.position[1],move,parent.distance+1)
                marked.append((parent.position[0]-1, parent.position[1]))
                queue.append(new_node)
                parent.add_children(new_node)
            if (not (parent.position[0]+1, parent.position[1]) in marked) and self.no_obstacles(parent.position[0]+1, parent.position[1],field):
                new_node = Node(parent.position[0]+1, parent.position[1],move,parent.distance+1)
                marked.append((parent.position[0]+1, parent.position[1]))
                queue.append(new_node)    
                parent.add_children(new_node)
            if (not (parent.position[0], parent.position[1]-1) in marked) and self.no_obstacles(parent.position[0], parent.position[1]-1,field):
                new_node = Node(parent.position[0], parent.position[1]-1,move,parent.distance+1)
                marked.append((parent.position[0], parent.position[1]-1))
                queue.append(new_node)   
                parent.add_children(new_node)
            if (not (parent.position[0], parent.position[1]+1) in marked) and self.no_obstacles(parent.position[0], parent.position[1]+1,field):
                new_node = Node(parent.position[0], parent.position[1]+1,move,parent.distance+1)
                marked.append((parent.position[0], parent.position[1]+1))
                queue.append(new_node)    
                parent.add_children(new_node)
        

    def closest_goal(self,player_number,field):
        
        
        if player_number == 1:
            figure = CELL_SHEEP_1
            sheep_position = self.get_player_position(CELL_SHEEP_1,field)
            opponent_sheep_position = self.get_player_position(CELL_SHEEP_2, field)
        else:
            figure = CELL_SHEEP_2
            sheep_position = self.get_player_position(CELL_SHEEP_2,field)
            opponent_sheep_position = self.get_player_position(CELL_SHEEP_1, field)

        #make list of possible goals
        #with their total cost = cost + cost of neighbours

        goals_and_cost = {}
        opponent_goals_distance = {}
        y_position = 0
        for line in field:
            x_position = 0
            for item in line:
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    if item == CELL_RHUBARB:
                        item_cost = AWARD_RHUBARB
                    else:
                        item_cost = AWARD_GRASS
                    if self.valid_move(figure, y_position+1, x_position, field):
                        if field[y_position+1][x_position] == CELL_RHUBARB: 
                            item_cost += AWARD_RHUBARB
                        elif field[y_position+1][x_position] == CELL_GRASS: 
                            item_cost += AWARD_GRASS
                    if self.valid_move(figure, y_position-1, x_position, field):
                        if field[y_position-1][x_position] == CELL_RHUBARB: 
                            item_cost += AWARD_RHUBARB
                        elif field[y_position-1][x_position] == CELL_GRASS: 
                            item_cost += AWARD_GRASS
                    if self.valid_move(figure, y_position, x_position+1, field):
                        if field[y_position][x_position+1] == CELL_RHUBARB: 
                            item_cost += AWARD_RHUBARB
                        elif field[y_position][x_position+1] == CELL_GRASS: 
                            item_cost += AWARD_GRASS
                    if self.valid_move(figure, y_position, x_position-1, field):
                        if field[y_position][x_position-1] == CELL_RHUBARB: 
                            item_cost += AWARD_RHUBARB
                        elif field[y_position][x_position-1] == CELL_GRASS: 
                            item_cost += AWARD_GRASS

                    if self.valid_move(figure, y_position+1, x_position+1, field):
                        if field[y_position+1][x_position+1] == CELL_RHUBARB: 
                            item_cost += AWARD_RHUBARB
                        elif field[y_position+1][x_position+1] == CELL_GRASS: 
                            item_cost += AWARD_GRASS
                    if self.valid_move(figure, y_position-1, x_position-1, field):
                        if field[y_position-1][x_position-1] == CELL_RHUBARB: 
                            item_cost += AWARD_RHUBARB
                        elif field[y_position-1][x_position-1] == CELL_GRASS: 
                            item_cost += AWARD_GRASS
                    if self.valid_move(figure, y_position-1, x_position+1, field):
                        if field[y_position-1][x_position+1] == CELL_RHUBARB: 
                            item_cost += AWARD_RHUBARB
                        elif field[y_position-1][x_position+1] == CELL_GRASS: 
                            item_cost += AWARD_GRASS
                    if self.valid_move(figure, y_position+1, x_position-1, field):
                        if field[y_position+1][x_position-1] == CELL_RHUBARB: 
                            item_cost += AWARD_RHUBARB
                        elif field[y_position+1][x_position-1] == CELL_GRASS: 
                            item_cost += AWARD_GRASS

                    goals_and_cost.update({(y_position,x_position): item_cost})
                    opponent_goals_distance.update({(y_position,x_position): 1})
                x_position += 1
            y_position += 1

        #find the distances from opponent sheep to every food
        ################
        if opponent_sheep_position != (-1, -1):
            queue = deque()
            marked = []
            move = 'p'
            tree = Node(opponent_sheep_position[0], opponent_sheep_position[1],move,0)
            queue.append(tree)
            marked.append(tree.position)

            while queue:
                parent = queue.popleft()
                if parent.position in opponent_goals_distance.keys():
                    opponent_goals_distance[(parent.position)] = parent.distance


                if (not (parent.position[0]-1, parent.position[1]) in marked) and self.valid_move(figure, parent.position[0]-1, parent.position[1],field):
                    new_node = Node(parent.position[0]-1, parent.position[1],move,parent.distance+1)
                    marked.append((parent.position[0]-1, parent.position[1]))
                    queue.append(new_node)
                    parent.add_children(new_node)
                if (not (parent.position[0]+1, parent.position[1]) in marked) and self.valid_move(figure, parent.position[0]+1, parent.position[1],field):
                    new_node = Node(parent.position[0]+1, parent.position[1],move,parent.distance+1)
                    marked.append((parent.position[0]+1, parent.position[1]))
                    queue.append(new_node)    
                    parent.add_children(new_node)
                if (not (parent.position[0], parent.position[1]-1) in marked) and self.valid_move(figure, parent.position[0], parent.position[1]-1,field):
                    new_node = Node(parent.position[0], parent.position[1]-1,move,parent.distance+1)
                    marked.append((parent.position[0], parent.position[1]-1))
                    queue.append(new_node)   
                    parent.add_children(new_node)
                if (not (parent.position[0], parent.position[1]+1) in marked) and self.valid_move(figure, parent.position[0], parent.position[1]+1,field):
                    new_node = Node(parent.position[0], parent.position[1]+1,move,parent.distance+1)
                    marked.append((parent.position[0], parent.position[1]+1))
                    queue.append(new_node)    
                    parent.add_children(new_node)

        ###############


        #determine closest item and return
        
        moves = {}
        queue = deque()
        marked = []
        tree = Node(sheep_position[0], sheep_position[1],'p',0)
        queue.append(tree)
        marked.append(tree.position)

        while queue:
            # print('************************')
            # for a in queue:
                # print(a.position)
                # print('  ')
            parent = queue.popleft()
            # print(parent.position[0],parent.position[1])
            # print(parent.move)
            if parent.position in goals_and_cost.keys():
                goals_and_cost[(parent.position)] += ((opponent_goals_distance[(parent.position)]-parent.distance) - parent.distance)
                # goals_and_cost[(parent.position)] *= (opponent_goals_distance[(parent.position)]/parent.distance)
                moves.update({(parent.position): parent.move})

                # closest = (parent.position[0], parent.position[1],parent.move)
                
            if parent.move == 'p':
                valid = self.valid_move;
            else:
                valid = self.future_valid_move;

            if (not (parent.position[0]-1, parent.position[1]) in marked) and valid(figure, parent.position[0]-1, parent.position[1],field):
                if parent.move == 'p':
                    move = 'u'
                else:
                    move = parent.move
                new_node = Node(parent.position[0]-1, parent.position[1],move,parent.distance+1)
                marked.append((parent.position[0]-1, parent.position[1]))
                queue.append(new_node)
                parent.add_children(new_node)
            if (not (parent.position[0]+1, parent.position[1]) in marked) and valid(figure, parent.position[0]+1, parent.position[1],field):
                if parent.move == 'p':
                    move = 'd'
                else:
                    move = parent.move
                new_node = Node(parent.position[0]+1, parent.position[1],move,parent.distance+1)
                marked.append((parent.position[0]+1, parent.position[1]))
                queue.append(new_node)    
                parent.add_children(new_node)
            if (not (parent.position[0], parent.position[1]-1) in marked) and valid(figure, parent.position[0], parent.position[1]-1,field):
                if parent.move == 'p':
                    move = 'l'
                else:
                    move = parent.move
                new_node = Node(parent.position[0], parent.position[1]-1,move,parent.distance+1)
                marked.append((parent.position[0], parent.position[1]-1))
                queue.append(new_node)   
                parent.add_children(new_node)
            if (not (parent.position[0], parent.position[1]+1) in marked) and valid(figure, parent.position[0], parent.position[1]+1,field):
                if parent.move == 'p':
                    move = 'r'
                else:
                    move = parent.move
                new_node = Node(parent.position[0], parent.position[1]+1,move,parent.distance+1)
                marked.append((parent.position[0], parent.position[1]+1))
                queue.append(new_node)    
                parent.add_children(new_node)
        
        best_goal = max(goals_and_cost, key=goals_and_cost.get)
        closest = (best_goal[0], best_goal[1], moves[best_goal])
        return closest        

    def gather_goal(self,closest_goal,field,figure):
        move = closest_goal[2]
        if move == 'u':
            return MOVE_UP
        elif move == 'd':
            return MOVE_DOWN
        elif move == 'l':
            return MOVE_LEFT
        elif move == 'r':
            return MOVE_RIGHT
        else:
            return MOVE_NONE

    def gather_closest_goal(self,closest_goal,field,figure):
        figure_position = self.get_player_position(figure,field)

        next_move = MOVE_NONE
        queue = deque()
        marked = []
        tree = Node(figure_position[0], figure_position[1],'p',0)
        queue.append(tree)
        marked.append(tree.position)

        while queue:
            parent = queue.popleft()
            if parent.position == closest_goal:
                next_move = parent.move
                break

            if parent.move == 'p':
                valid = self.valid_move;
            else:
                valid = self.future_valid_move;

            if (not (parent.position[0]-1, parent.position[1]) in marked) and valid(figure, parent.position[0]-1, parent.position[1],field):
                if parent.move == 'p':
                    move = 'u'
                else:
                    move = parent.move
                new_node = Node(parent.position[0]-1, parent.position[1],move,parent.distance+1)
                marked.append((parent.position[0]-1, parent.position[1]))
                queue.append(new_node)
                parent.add_children(new_node)
            if (not (parent.position[0]+1, parent.position[1]) in marked) and valid(figure, parent.position[0]+1, parent.position[1],field):
                if parent.move == 'p':
                    move = 'd'
                else:
                    move = parent.move
                new_node = Node(parent.position[0]+1, parent.position[1],move,parent.distance+1)
                marked.append((parent.position[0]+1, parent.position[1]))
                queue.append(new_node)    
                parent.add_children(new_node)
            if (not (parent.position[0], parent.position[1]-1) in marked) and valid(figure, parent.position[0], parent.position[1]-1,field):
                if parent.move == 'p':
                    move = 'l'
                else:
                    move = parent.move
                new_node = Node(parent.position[0], parent.position[1]-1,move,parent.distance+1)
                marked.append((parent.position[0], parent.position[1]-1))
                queue.append(new_node)   
                parent.add_children(new_node)
            if (not (parent.position[0], parent.position[1]+1) in marked) and valid(figure, parent.position[0], parent.position[1]+1,field):
                if parent.move == 'p':
                    move = 'r'
                else:
                    move = parent.move
                new_node = Node(parent.position[0], parent.position[1]+1,move,parent.distance+1)
                marked.append((parent.position[0], parent.position[1]+1))
                queue.append(new_node)    
                parent.add_children(new_node)
        if next_move == 'u':
            return MOVE_UP
        if next_move == 'd':
            return MOVE_DOWN
        if next_move == 'r':
            return MOVE_RIGHT
        if next_move == 'l':
            return MOVE_LEFT

        return next_move    


    def wolf_close(self,player_number,field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1,field)
            wolf_position = self.get_player_position(CELL_WOLF_2,field)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2,field)
            wolf_position = self.get_player_position(CELL_WOLF_1,field)

        if (abs(sheep_position[0]-wolf_position[0]) <= 2 and abs(sheep_position[1]-wolf_position[1]) <= 2):
            #print('wolf is close')
            return True
        return False

    def valid_move(self, figure, x_new, y_new, field):
        
        if len(field) == FIELD_HEIGHT and len(field[0]) == FIELD_WIDTH:
            height = FIELD_HEIGHT
            width = FIELD_WIDTH
        else:
            height = len(field)
            width = len(field[0])

         # Neither the sheep nor the wolf, can step on a square outside the map. Imagine the map is surrounded by fences.
        if x_new > height - 1:
            return False
        elif x_new < 0:
            return False
        elif y_new > width -1:
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

    def future_valid_move(self, figure, x_new, y_new, field):
        
        if len(field) == FIELD_HEIGHT and len(field[0]) == FIELD_WIDTH:
            height = FIELD_HEIGHT
            width = FIELD_WIDTH
        else:
            height = len(field)
            width = len(field[0])

         # Neither the sheep nor the wolf, can step on a square outside the map. Imagine the map is surrounded by fences.
        if x_new > height - 1:
            return False
        elif x_new < 0:
            return False
        elif y_new > width -1:
            return False
        elif y_new < 0:
            return False

        # Neither the sheep nor the wolf, can enter a square with a fence on.
        if field[x_new][y_new] == CELL_FENCE:
            return False

        return True

    def no_obstacles(self, x_new, y_new, field):
        
        if len(field) == FIELD_HEIGHT and len(field[0]) == FIELD_WIDTH:
            height = FIELD_HEIGHT
            width = FIELD_WIDTH
        else:
            height = len(field)
            width = len(field[0])

         # Neither the sheep nor the wolf, can step on a square outside the map. Imagine the map is surrounded by fences.
        if x_new > height - 1:
            return False
        elif x_new < 0:
            return False
        elif y_new > width -1:
            return False
        elif y_new < 0:
            return False

        # Neither the sheep nor the wolf, can enter a square with a fence on.
        if field[x_new][y_new] == CELL_FENCE:
            return False

        return True

    def run_from_wolf(self,player_number,field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_1,field)
            wolf_position = self.get_player_position(CELL_WOLF_2,field)
            sheep = CELL_SHEEP_1
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_2,field)
            wolf_position = self.get_player_position(CELL_WOLF_1,field)
            sheep = CELL_SHEEP_2

        distance_x = sheep_position[1] - wolf_position[1]
        abs_distance_x = abs(sheep_position[1] - wolf_position[1])
        distance_y = sheep_position[0] - wolf_position[0]
        abs_distance_y = abs(sheep_position[0] - wolf_position[0])

        #print('player_number %i' %player_number)
        #print('running from wolf')
        #if the wolf is close vertically
        if abs_distance_y in (1,2) and distance_x == 0:
            #print('wolf is close vertically')
            #if it's above the sheep, move down if possible
            if distance_y > 0:
                # print("up=================================")
                #go from wolf and to food if possible
                subfield = np.array(field)[sheep_position[0]:, :].tolist()
                if len(subfield) != 0:
                    if self.food_present(subfield):
                        return self.gather_goal(self.closest_goal(player_number,subfield),subfield,sheep)
                ##no food availible, just go from woolf
                if self.valid_move(sheep,sheep_position[0]+1,sheep_position[1], field):
                    return MOVE_DOWN
            else: #it's below the sheep, move up if possible
                # print("down=================================")
                #go from wolf and to food if possible
                subfield = np.array(field)[:sheep_position[0]+1, :].tolist()
                if len(subfield) != 0:
                    if self.food_present(subfield):
                        return self.gather_goal(self.closest_goal(player_number,subfield),subfield,sheep)
                ##no food availible, just go from woolf
                if self.valid_move(sheep,sheep_position[0]-1,sheep_position[1], field):
                    return MOVE_UP            
            # if this is not possible, flee to the right or left
            if self.valid_move(sheep,sheep_position[0],sheep_position[1]+1, field):
                return MOVE_RIGHT
            elif self.valid_move(sheep,sheep_position[0],sheep_position[1]-1, field):
                return MOVE_LEFT
            else: #nowhere to go
                return MOVE_NONE

        #else if the wolf is close horizontally
        elif abs_distance_x in (1,2) and distance_y == 0:
            #print('wolf is close horizontally')
            #if it's to the left, move to the right if possible
            if distance_x > 0:
                # print("left=================================")
                #go from wolf and to food if possible
                subfield = np.array(field)[:, sheep_position[1]:].tolist()
                if len(subfield) != 0:
                    if self.food_present(subfield):
                        return self.gather_goal(self.closest_goal(player_number,subfield),subfield,sheep)
                ##no food availible, just go from woolf
                if self.valid_move(sheep,sheep_position[0],sheep_position[1]+1, field):
                    return MOVE_RIGHT
            else: #it's to the right, move left if possible
                # print("right=================================")
                #go from wolf and to food if possible
                subfield = np.array(field)[:, :sheep_position[1]+1].tolist()
                if len(subfield) != 0:
                    if self.food_present(subfield):
                        return self.gather_goal(self.closest_goal(player_number,subfield),subfield,sheep)
                #no food availible, just go from woolf
                if self.valid_move(sheep,sheep_position[0],sheep_position[1]-1, field):
                    return MOVE_LEFT
            #if this is not possible, flee up or down
            if self.valid_move(sheep,sheep_position[0]-1,sheep_position[1], field):
                return MOVE_UP
            elif self.valid_move(sheep,sheep_position[0]+1,sheep_position[1], field):
                return MOVE_DOWN
            else: #nowhere to go
                return MOVE_NONE

        elif abs_distance_x in (1,2) and abs_distance_y in (1,2):
            #print('wolf is in my surroundings')
            #wolf is left and up
            if distance_x > 0 and distance_y > 0:
                # print("left up=================================")
                #go from wolf and to food if possible
                subfield = np.array(field)[sheep_position[0]:, sheep_position[1]:].tolist()
                if len(subfield) != 0:
                    if self.food_present(subfield):
                        return self.gather_goal(self.closest_goal(player_number,subfield),subfield,sheep)
                ##no food availible, just go from woolf
                #move right or down
                if self.valid_move(sheep,sheep_position[0],sheep_position[1]+1, field):
                    return MOVE_RIGHT
                else:
                    return MOVE_DOWN
            #wolf is left and down
            if distance_x > 0 and distance_y < 0:
                # print("left down=================================")
                #go from wolf and to food if possible
                subfield = np.array(field)[:sheep_position[0]+1, sheep_position[1]:].tolist()
                if len(subfield) != 0:
                    if self.food_present(subfield):
                        return self.gather_goal(self.closest_goal(player_number,subfield),subfield,sheep)
                ##no food availible, just go from woolf
                #move right or up
                if self.valid_move(sheep,sheep_position[0],sheep_position[1]+1, field):
                    return MOVE_RIGHT
                else:
                    return MOVE_UP
            #wolf is right and up
            if distance_x < 0 and distance_y > 0:
                # print("right up=================================")
                #go from wolf and to food if possible
                subfield = np.array(field)[sheep_position[0]:, :sheep_position[1]+1].tolist()
                if len(subfield) != 0:
                    if self.food_present(subfield):
                        return self.gather_goal(self.closest_goal(player_number,subfield),subfield,sheep)
                ##no food availible, just go from woolf
                #move left or down
                if self.valid_move(sheep,sheep_position[0],sheep_position[1]-1, field):
                    return MOVE_LEFT
                else:
                    return MOVE_DOWN
            #wolf is right and down
            if distance_x < 0 and distance_y < 0:
                # print("right down=================================")
                #go from wolf and to food if possible
                subfield = np.array(field)[:sheep_position[0]+1, :sheep_position[1]+1].tolist()
                if len(subfield) != 0:
                    if self.food_present(subfield):
                        return self.gather_goal(self.closest_goal(player_number,subfield),subfield,sheep)
                ##no food availible, just go from woolf
                #move left and up
                if self.valid_move(sheep,sheep_position[0],sheep_position[1]-1, field):
                    return MOVE_LEFT
                else:
                    return MOVE_UP


        else: #this method was wrongly called
            return MOVE_NONE

    def move_sheep(self,player_number,field):
        if player_number == 1:
            figure = CELL_SHEEP_1
        else:
            figure = CELL_SHEEP_2

        if self.wolf_close(player_number,field):
            # print('wolf close move')
            # print("WOLF close==========================")
            return self.run_from_wolf(player_number,field)
        elif self.food_present(field):
            #print('gather food move')
            return self.gather_goal(self.closest_goal(player_number,field),field,figure)
        else:
            return MOVE_NONE

    #defs for wolf
    def move_wolf(self,player_number,field):
        if player_number == 1:
            sheep_position = self.get_player_position(CELL_SHEEP_2,field)
            barash_position = self.get_player_position(CELL_SHEEP_1, field)
            # print(self.distance(sheep_position,barash_position,field))
            return self.gather_closest_goal(sheep_position,field,CELL_WOLF_1)
        else:
            sheep_position = self.get_player_position(CELL_SHEEP_1,field)
            barash_position = self.get_player_position(CELL_SHEEP_2, field)
            return self.gather_closest_goal(sheep_position,field,CELL_WOLF_2)


