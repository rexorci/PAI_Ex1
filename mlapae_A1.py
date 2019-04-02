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

def get_class_name():
    return 'Bublik'

class Bublik():
    """Example class for a Kingsheep player"""

    def __init__(self):
        self.name = "Bublik"
        self.uzh_shortname = "mlapae"
        self.index = 0 
        self.depth = 1
        self.number_of_agents=2




###copyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

    def maxvalue(self ,state, agentIndex, currentdepth, alpha, beta, figure,field):
      v = (float("-inf"), MOVE_NONE)

      for move in state.list_of_valid_moves(figure,field):
        v = max([v, (self.value(state.generateSuccessor(move, figure), (currentdepth+1) % self.number_of_agents, currentdepth+1, alpha, beta, figure,field), move)], key=lambda item:item[0])

        if v[0] > beta:
          return v
        alpha = max(alpha, v[0])
      return v



    def minvalue(self, state, agentIndex, currentdepth, alpha, beta, figure,field):
      v = (float("inf"), MOVE_NONE)
      for move in state.list_of_valid_moves(figure,field):
        v = min([v, (self.value(state.generateSuccessor(move, figure), (currentdepth+1) % self.number_of_agents, currentdepth+1, alpha, beta, figure,field), move)], key=lambda item:item[0])
        if v[0] < alpha:
          return v
        beta = min(beta, v[0])
      return v

    def value(self, state, agentIndex, currentdepth, alpha, beta, figure,field):

      if state.isWin(agentIndex) or state.isLose(agentIndex) or currentdepth >= self.depth*self.number_of_agents:
        return self.evaluationFunction(state)
      if (agentIndex == 0):
        return self.maxvalue(state, agentIndex, currentdepth, alpha, beta, figure,field)[0]  
      else:
        return self.minvalue(state, agentIndex, currentdepth, alpha, beta, figure,field)[0]

    def evaluationFunction(self, currentGameState):
        
        return currentGameState.my_score


    def move_sheep(self, player_number, field):
        if player_number == 1:
            figure = CELL_SHEEP_1
        elif player_number == 2:
            figure = CELL_SHEEP_2

        field_ini=GameState(MOVE_NONE, 0, field)
        alpha = float("-inf")
        beta  = float("inf")
        path2 = self.maxvalue(field_ini,0,0,alpha,beta, figure,field)
        


        return path2[1]


    def move_wolf(self, player_number, field):
        if player_number == 1:
            figure = CELL_WOLF_1
        elif player_number == 2:
            figure = CELL_WOLF_2   

        field_ini=GameState(MOVE_NONE, 0, field)
        alpha = float("-inf")
        beta  = float("inf")
        path2 = self.maxvalue(field_ini,0,0,alpha,beta, figure,field)
        return path2[1]

###copyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy

class GameState:
    """
    A GameState holds the (x,y) coordinate of a character, along with its
    traveling direction.
    The convention for positions, like a graph, is that (0,0) is the lower left corner, x increases
    horizontally and y increases vertically.  Therefore, north is the direction of increasing y, or (0,1).
    """

    def __init__(self, direction, my_score,field):
        self.direction = direction
        self.my_score=my_score
        self.field=field

    
    def isWin(self, agentIndex):

        if (agentIndex== 0):
            x = [x for x in self.field if CELL_SHEEP_2 in x]
            return len(x)==0

        if (agentIndex== 1):
            x = [x for x in self.field if CELL_SHEEP_1 in x]
            return len(x)==0
        # print ('NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
        return False


    def isLose(self, agentIndex):

        if (agentIndex== 0):
            x = [x for x in self.field if CELL_SHEEP_1 in x]
            return len(x)==0


        if (agentIndex== 1):
            x = [x for x in self.field if CELL_SHEEP_2 in x]
            return len(x)==0
        # print ('NOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOo2!!!')
        return False


    def list_of_valid_moves(self, figure, field):
        field=self.field
        figure_position = self.get_player_position(figure,field)
        
        list_of_valid_move = []
        if self.valid_move(figure,figure_position[0]-1,figure_position[1], field):
            list_of_valid_move.append(MOVE_UP)          
        if self.valid_move(figure,figure_position[0]+1,figure_position[1], field):
            list_of_valid_move.append(MOVE_DOWN)         
        if self.valid_move(figure,figure_position[0],figure_position[1]+1, field):
            list_of_valid_move.append(MOVE_RIGHT)
        if self.valid_move(figure,figure_position[0],figure_position[1]-1, field):
            list_of_valid_move.append(MOVE_LEFT)

        return list_of_valid_move



    def valid_move(self, figure, x_new, y_new, field):
         # Neither the sheep nor the wolf, can step on a square outside the map. Imagine the map is surrounded by fences.
        field=self.field
        if x_new > FIELD_HEIGHT - 1:
            return False
        elif x_new < 0:
            return False
        elif y_new > FIELD_WIDTH -1:
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
                field[x_new][y_new] == CELL_WOLF_1 or field[x_new][y_new] == CELL_WOLF_2:
                return False
        elif figure == CELL_SHEEP_2:
            if field[x_new][y_new] == CELL_SHEEP_1 or \
                    field[x_new][y_new] == CELL_WOLF_2 or field[x_new][y_new] == CELL_WOLF_1:
                return False

        return True

    def get_player_position(self,figure,field):
        x = [x for x in self.field if figure in x][0]
        return (self.field.index(x), x.index(figure))

    def generateSuccessor(self, move,figure):
        """
        Generates a new GameState reached by translating the current
        GameState by the action vector.  This is a low-level call and does
        not attempt to respect the legality of the movement.
        Actions are movement vectors.
        """
        figure_position = self.get_player_position(figure,self.field)
        field=self.field
        direction = move
        dx=0
        dy=0

        if move==MOVE_UP:
            dy=dy-1
        elif move==MOVE_DOWN:
            dy=1
        elif move==MOVE_RIGHT:
            dx=dx+1
        elif move==MOVE_LEFT:
            dx=dx-1
        else:
            direction=MOVE_NONE
       
        if direction == MOVE_NONE:
            direction = self.direction # There is no stop direction


        next_step_score=self.my_score
        next_step_field=[row[:] for row in self.field]




        next_step_score+=self.get_next_step_score (figure_position,figure_position[0]+dy, figure_position[1] + dx, next_step_field, figure)


        next_step_field[figure_position[0]][figure_position[1]]=CELL_EMPTY
        next_step_field[figure_position[0]+dy][figure_position[1] + dx]=figure
       
       # take into account the length of the way to the final goal
        next_step_score-=15


        return GameState(direction, next_step_score,next_step_field)

    def get_next_step_score (self, current_pos, next_step_y,next_step_x, next_step_field, figure):
        
        next_step_score=0
# FOOOOOOOOOOOOOOOOOOOOOOR WWWWWWWWWWWWWWWOLLLLLLLLLLLLLLLLLLLLLLLF      
        if figure==CELL_WOLF_1:  
                if next_step_field[next_step_y][next_step_x] == CELL_SHEEP_2:
                    next_step_score +=1000
                    return next_step_score
                my_sheep_position = self.get_player_position(CELL_SHEEP_1,next_step_field)
                opponent_sheep_position=self.get_player_position(CELL_SHEEP_2,next_step_field)
                distance_to_food_my_sheep= (my_sheep_position[0],my_sheep_position[1],next_step_field)
                distance_to_food_op_sheep= (opponent_sheep_position[0],opponent_sheep_position[1],next_step_field)

                food_distance=self.dist_to_closest_food(next_step_y,next_step_x, next_step_field)

           #     next_step_score -=self.dist_to_closest_food(next_step_y,next_step_x, next_step_field)

        if figure==CELL_WOLF_2:  
                if next_step_field[next_step_y][next_step_x] == CELL_SHEEP_1:
                    next_step_score +=1000
                    return next_step_score


        if figure==CELL_WOLF_1 or figure==CELL_WOLF_2:  
                if self.distance_to_op_sheep(figure,next_step_field)<3:
                    next_step_score +=10
                next_step_score -=self.distance_to_op_sheep(figure,next_step_field)


                if next_step_field[next_step_y][next_step_x]== CELL_RHUBARB:
                    next_step_score += 10
                elif next_step_field[next_step_y][next_step_x] == CELL_GRASS:
                    next_step_score += 5



        if figure==CELL_SHEEP_1 or figure==CELL_SHEEP_2:  
            # add score if there is food at next_step cell
            if next_step_field[next_step_y][next_step_x]== CELL_RHUBARB:
                next_step_score += 500
            elif next_step_field[next_step_y][next_step_x] == CELL_GRASS:
                next_step_score += 100
            else:
                next_step_score -=self.dist_to_closest_food(next_step_y,next_step_x, next_step_field)

            # add score if there is food at neighbours of the next_step cell
            neighbour_CELL_RHUBARB_award=15
            neighbour_CELL_GRASS_award=5
            award=next_step_score


            if self.valid_move(figure,next_step_y+1,next_step_x, next_step_field) and next_step_field[next_step_y+1][next_step_x]== CELL_RHUBARB:
                next_step_score += neighbour_CELL_RHUBARB_award
            if self.valid_move(figure,next_step_y+1,next_step_x, next_step_field) and next_step_field[next_step_y+1][next_step_x]== CELL_GRASS:
                next_step_score += neighbour_CELL_GRASS_award
            if self.valid_move(figure,next_step_y-1,next_step_x, next_step_field) and next_step_field[next_step_y-1][next_step_x]== CELL_RHUBARB:
                next_step_score += neighbour_CELL_RHUBARB_award
            if self.valid_move(figure,next_step_y-1,next_step_x, next_step_field) and next_step_field[next_step_y-1][next_step_x]== CELL_GRASS:
                next_step_score += neighbour_CELL_GRASS_award
            if self.valid_move(figure,next_step_y,next_step_x+1, next_step_field) and next_step_field[next_step_y][next_step_x+1]== CELL_RHUBARB:
                next_step_score += neighbour_CELL_RHUBARB_award
            if self.valid_move(figure,next_step_y,next_step_x+1, next_step_field) and next_step_field[next_step_y][next_step_x+1]== CELL_GRASS:
                next_step_score += neighbour_CELL_GRASS_award
            if self.valid_move(figure,next_step_y,next_step_x-1, next_step_field) and next_step_field[next_step_y][next_step_x-1]== CELL_RHUBARB:
                next_step_score += neighbour_CELL_RHUBARB_award
            if self.valid_move(figure,next_step_y,next_step_x-1, next_step_field) and next_step_field[next_step_y][next_step_x-1]== CELL_GRASS:
                next_step_score += neighbour_CELL_GRASS_award
            #if next_step_score==award:

                        # there is no food  at neighbors of the next_step cell. Try to find the next step for the closest food
                        

            
            # subtract score if opponent wolf is really close      
            if self.opponent_wolf_is_really_close(figure,next_step_field):
                    next_step_score -= 200
            # print('final_score for (',next_step_y,',',next_step_x,')=======', next_step_score)

        return next_step_score

 

    def distance_between_figures(first_goal, second_goal, field):
        distance = abs(first_goal[0]-second_goal[0])+abs(first_goal[1]-second_goal[1])
        return distance


    def dist_to_closest_food(self,next_step_y,next_step_x, field):
        


        possible_goals = self.food_on_map(field)

        sheep_position = (next_step_y, next_step_x)

        if len(possible_goals)==0:
            return 0
        #determine closest item and return
        distance = 1000
        for possible_goal in possible_goals:
            if (abs(possible_goal[0]-sheep_position[0])+abs(possible_goal[1]-sheep_position[1])) < distance:
                distance = abs(possible_goal[0]-sheep_position[0])+abs(possible_goal[1]-sheep_position[1])
                
                if possible_goal[0]>sheep_position[0]: a=-1
                else: a=1

                for dif_cell_y in range (possible_goal[0],sheep_position[0]+1, a):
                    if field[dif_cell_y][sheep_position[1]]==CELL_RHUBARB:
                        distance+=1
                    ###add oponent wolf?

                if possible_goal[1]>sheep_position[1]: b=-1
                else: b=1

                for dif_cell_x in range (possible_goal[1],sheep_position[1]+1, b):
                    if field[sheep_position[0]][dif_cell_x]==CELL_RHUBARB:
                        distance+=1
                    ###add oponent wolf?
                
        return distance


    def food_on_map (self, field):
        possible_goals = []
        y_position = 0
        for line in field:
            x_position = 0
            for item in line:
                if item == CELL_RHUBARB or item == CELL_GRASS:
                    possible_goals.append((y_position,x_position))
                x_position += 1
            y_position += 1
        return possible_goals

    def opponent_wolf_is_really_close(self,figure,next_step_field):
        if figure == CELL_SHEEP_1:
            sheep_position = self.get_player_position(CELL_SHEEP_1,next_step_field)
            wolf_position = self.get_player_position(CELL_WOLF_2,next_step_field)
        elif figure == CELL_SHEEP_2:
            sheep_position = self.get_player_position(CELL_SHEEP_2,next_step_field)
            wolf_position = self.get_player_position(CELL_WOLF_1,next_step_field)

        if (abs(sheep_position[0]-wolf_position[0]) <= 1 and abs(sheep_position[1]-wolf_position[1]) <= 1):
            #print('wolf is close')
            return True
        return False

    def distance_to_op_sheep(self,figure,next_step_field):
        


        if figure == CELL_WOLF_2:
            sheep_position = self.get_player_position(CELL_SHEEP_1,next_step_field)
            wolf_position = self.get_player_position(CELL_WOLF_2,next_step_field)
        elif figure == CELL_WOLF_1:
            sheep_position = self.get_player_position(CELL_SHEEP_2,next_step_field)
            wolf_position = self.get_player_position(CELL_WOLF_1,next_step_field)

        y=abs(sheep_position[0]-wolf_position[0])
        x=abs(sheep_position[1]-wolf_position[1])
        dist_sum=x+y
        return dist_sum