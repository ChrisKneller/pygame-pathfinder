import pygame
import time
from priority_queue import PrioritySet, PriorityQueue, AStarQueue
from math import inf
import random

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (0, 111, 255)
ORANGE = (255, 128, 0)
PURPLE = (128, 0, 255)
YELLOW = (255, 255, 0)
GREY = (143, 143, 143)
BROWN = (186, 127, 50)
DARK_GREEN = (0, 128, 0)
DARKER_GREEN = (0, 50, 0)
DARK_BLUE = (0, 0, 128)

# For creating Buttons
class Button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.text = text

    def draw(self,win,outline=None):
        # Call this method to draw the Button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x,self.y,self.width,self.height),0)
            
        pygame.draw.rect(win, self.color, (self.x+1,self.y+1,self.width-1,self.height-1),0)
        
        if self.text != '':
            font = pygame.font.SysFont('arial', 20)
            text = font.render(self.text, 1, (0,0,0))
            win.blit(text, (self.x + int(self.width/2 - text.get_width()/2), self.y + int(self.height/2 - text.get_height()/2)))

    def isOver(self, pos):
        # Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

# Make it easier to add different node types
class Node():

    nodetypes = ['blank', 'start', 'end', 'wall', 'mud']

    colors = {  'regular': {'blank': WHITE, 'start': RED, 'end': LIGHT_BLUE, 'wall': BLACK, 'mud': BROWN},
                'visited': {'blank': GREEN, 'start': RED, 'end': LIGHT_BLUE, 'wall': BLACK, 'mud': DARK_GREEN},
                'path': {'blank': BLUE, 'start': RED, 'end': LIGHT_BLUE, 'wall': BLACK, 'mud': DARK_BLUE}
            }

    distance_modifiers = {'blank': 1, 'start': 1, 'end': 1, 'wall': inf, 'mud': 3}

    def __init__(self, nodetype, text='', colors=colors, dmf=distance_modifiers):
        self.nodetype = nodetype
        self.rcolor = colors['regular'][self.nodetype]
        self.vcolor = colors['visited'][self.nodetype]
        self.pcolor = colors['path'][self.nodetype]
        self.is_visited = True if nodetype == 'start' else True if nodetype == 'end' else False
        self.is_path = True if nodetype == 'start' else True if nodetype == 'end' else False
        self.distance_modifier = dmf[self.nodetype]
        self.color = self.pcolor if self.is_path else self.vcolor if self.is_visited else self.rcolor

    def update(self, nodetype=False, is_visited='unchanged', is_path='unchanged', colors=colors, dmf=distance_modifiers, nodetypes=nodetypes):
        if nodetype:
            assert nodetype in nodetypes, f"nodetype must be one of: {nodetypes}"
            if (self.nodetype == ('start' or 'end')) and (nodetype == ('wall' or 'mud')):
                pass
            else:
                self.nodetype = nodetype        

        if is_visited != 'unchanged':
            assert type(is_visited) == bool, "'is_visited' must be boolean: True or False" 
            self.is_visited = is_visited

        if is_path != 'unchanged':
            assert type(is_path) == bool, "'is_path' must be boolean: True or False" 
            self.is_path = is_path

        self.rcolor = colors['regular'][self.nodetype]
        self.vcolor = colors['visited'][self.nodetype]
        self.pcolor = colors['path'][self.nodetype]
        self.distance_modifier = dmf[self.nodetype]
        self.color = self.pcolor if self.is_path else self.vcolor if self.is_visited else self.rcolor

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 9
HEIGHT = WIDTH # so they are squares
BUTTON_HEIGHT = 50

# This sets the margin between each cell
MARGIN = 0

# Create a 2 dimensional array (a list of lists)
grid = []
ROWS = 69
# Iterate through every row and column, adding blank nodes
for row in range(ROWS):
    grid.append([])
    for column in range(ROWS):
        grid[row].append(Node('blank')) 

# Set start and end points for the pathfinder
START_POINT = (random.randrange(2,ROWS-1,2)-1,random.randrange(2,ROWS-1,2)-1)
END_POINT = (random.randrange(2,ROWS-1,2),random.randrange(2,ROWS-1,2))

grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')

DIAGONALS = False
VISUALISE = True

# Used for handling click & drag
mouse_drag = False
drag_start_point = False
drag_end_point = False

# Used for deciding what to do in different situations
path_found = False
algorithm_run = False

pygame.init()

# Set default font for nodes
FONT = pygame.font.SysFont('arial', 8)

# Set the width and height of the screen [width, height]
SCREEN_WIDTH = ROWS * (WIDTH + MARGIN) + MARGIN * 2
SCREEN_HEIGHT = SCREEN_WIDTH + BUTTON_HEIGHT * 3
WINDOW_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(WINDOW_SIZE)

# Make some Buttons
dijkstraButton = Button(GREY, 0, SCREEN_WIDTH, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Dijkstra")
dfsButton = Button(GREY, 0, SCREEN_WIDTH + BUTTON_HEIGHT, SCREEN_WIDTH/3, BUTTON_HEIGHT, "DFS")
astarButton = Button(GREY, 0, SCREEN_WIDTH + BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, "A*")
resetButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH, SCREEN_WIDTH/3, BUTTON_HEIGHT*2, "Reset")
mazeButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Random Maze")
vizmazeButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH + BUTTON_HEIGHT, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Random Maze (viz)")
terrainButton = Button(GREY, (SCREEN_WIDTH/3)*2, SCREEN_WIDTH + BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, "Random Terrain")
visToggleButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH + BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, f"Visualise: {str(VISUALISE)}")

pygame.display.set_caption("Pathfinder")
 
# Loop until the user clicks the close Button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# -------- Main Program Loop -----------
while not done:
    # --- Main event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            
            # Find out which keys have been pressed
            pressed = pygame.key.get_pressed()

            # If click is inside grid
            if pos[1] <= SCREEN_WIDTH-1:

                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)

                if (row,column) == START_POINT:
                    drag_start_point = True
                elif (row,column) == END_POINT:
                    drag_end_point = True
                else:
                    cell_updated = grid[row][column]
                    if pressed[pygame.K_LCTRL]:
                        update_cell_to = 'mud'
                    else:
                        update_cell_to = 'wall'
                    cell_updated.update(nodetype=update_cell_to)
                    mouse_drag = True
                    if algorithm_run and cell_updated.is_path == True:
                        path_found = update_path()
            
            # Note to reader:
            # After having to create so many if statements for the different buttons
            # I have realised that a better way to handle this may be to create an 
            # onClick method inside the button class, where treatment can be defined
            # when defining the button
            # TODO: try this out

            # When the Dijkstra Button is clicked
            elif dijkstraButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:    
                    pygame.display.flip()
                path_found = dijkstra(grid, START_POINT, END_POINT)
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'dijkstra'
            
            # When the DFS Button is clicked
            elif dfsButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = dfs(grid, START_POINT, END_POINT)
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'dfs'
            
            # When the A* Button is clicked
            elif astarButton.isOver(pos):
                clear_visited()
                update_gui(draw_background=False, draw_buttons=False)
                if VISUALISE:
                    pygame.display.flip()
                path_found = dijkstra(grid, START_POINT, END_POINT, astar=True)
                grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                algorithm_run = 'astar'

            # When the Reset Button is clicked
            elif resetButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)

            # When the Random Maze Button is clicked
            elif mazeButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)
                grid = prim()

            # When the Random Maze (Viz) Button is clicked
            elif vizmazeButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)
                grid = prim()
        
            # When the Random Terrain Button is clicked
            elif terrainButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column].update(nodetype='blank', is_visited=False, is_path=False)
                update_gui(draw_background=False, draw_buttons=False)
                random_terrain()

            # When the Visualisation Toggle Button is clicked
            elif visToggleButton.isOver(pos):
                if VISUALISE:
                    VISUALISE = False
                else:
                    VISUALISE = True

        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Turn off all mouse drags if mouse Button released
            mouse_drag = drag_end_point = drag_start_point = False
        
        elif event.type == pygame.MOUSEMOTION:

            # Boolean values saying whether left, middle and right mouse buttons are currently pressed
            left, middle, right = pygame.mouse.get_pressed()
            
            # Sometimes we get stuck in this loop if the mousebutton is released while not in the pygame screen
            # This acts to break out of that loop
            if not left:
                mouse_drag = drag_end_point = drag_start_point = False
                continue

            # User moves the mouse. Get the position
            pos = pygame.mouse.get_pos()
            
            # Change the x/y screen coordinates to grid coordinates
            column = pos[0] // (WIDTH + MARGIN)
            row = pos[1] // (HEIGHT + MARGIN)
            
            # Turn mouse_drag off if mouse goes outside of grid
            if pos[1] >= SCREEN_WIDTH-2 or pos[1] <= 2 or pos[0] >= SCREEN_WIDTH-2 or pos[0] <= 2:
                mouse_drag = False
                continue
            
            cell_updated = grid[row][column]

            # Add walls or sticky mud patches
            if mouse_drag == True:
                if (row,column) == START_POINT:
                    pass
                elif (row,column) == END_POINT:
                    pass
                else:
                    if pressed[pygame.K_LCTRL]:
                        update_cell_to = 'mud'
                    else:
                        update_cell_to = 'wall'
                    cell_updated.update(nodetype=update_cell_to)

                mouse_drag = True
                
                if algorithm_run:
                    if cell_updated.is_path == True:
                        path_found = update_path()
            
            # Move the start point
            elif drag_start_point == True:
                if grid[row][column].nodetype == "blank":
                    grid[START_POINT[0]][START_POINT[1]].update(nodetype='blank', is_path=False, is_visited=False)
                    START_POINT = (row,column)
                    grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
                    # If we have already run the algorithm, update it as the point is moved
                    if algorithm_run:
                        path_found = update_path()
                        grid[START_POINT[0]][START_POINT[1]].update(nodetype='start') 
            
            # Move the end point
            elif drag_end_point == True:
                if grid[row][column].nodetype == "blank":
                    grid[END_POINT[0]][END_POINT[1]].update(nodetype='blank', is_path=False, is_visited=False)
                    END_POINT = (row,column)
                    grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')
                    # If we have already run the algorithm, update it as the point is moved
                    if algorithm_run:
                        path_found = update_path()
                        grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')

            pygame.display.flip()


 
    # Game logic

    # Clear board, keeping excluded nodes
    def clear_visited():
        excluded_nodetypes = ['start', 'end', 'wall', 'mud']
        for row in range(ROWS):
            for column in range(ROWS):
                if grid[row][column].nodetype not in excluded_nodetypes:
                    grid[row][column].update(nodetype="blank", is_visited=False, is_path=False)
                else:
                     grid[row][column].update(is_visited=False, is_path=False)
        update_gui(draw_background=False, draw_buttons=False)

    def update_path(algorithm_run=algorithm_run):
        
        clear_visited()
        
        valid_algorithms = ['dijkstra', 'astar', 'dfs']

        assert algorithm_run in valid_algorithms, f"last algorithm used ({algorithm_run}) is not in valid algorithms: {valid_algorithms}"

        if algorithm_run == 'dijkstra':
            path_found = dijkstra(grid, START_POINT, END_POINT, visualise=False)
        elif algorithm_run == 'astar':
            path_found = dijkstra(grid, START_POINT, END_POINT, visualise=False, astar=True)
        elif algorithm_run == 'dfs':
            path_found = dfs(grid, START_POINT, END_POINT, visualise=False)
        else:
            path_found = False
        return path_found

    def random_terrain(mazearray=grid, num_patches=False, visualise=VISUALISE):
        if not num_patches:
            num_patches = random.randrange(int(ROWS/10),int(ROWS/4))

        terrain_nodes = set([])

        if VISUALISE:
            pygame.display.flip()

        for patch in range(num_patches+1):
            neighbour_cycles = 0
            centre_point = (random.randrange(1,ROWS-1),random.randrange(1,ROWS-1))
            patch_type = 'mud'
            terrain_nodes.add(centre_point)
            while len(terrain_nodes) > 0:
                node = terrain_nodes.pop()
                if grid[node[0]][node[1]].nodetype != 'start' and grid[node[0]][node[1]].nodetype != 'end':
                    grid[node[0]][node[1]].update(nodetype=patch_type)
                    draw_square(node[0],node[1])
                    if visualise:
                        update_square(node[0],node[1])
                        time.sleep(0.000001)
                neighbour_cycles += 1
                for node, ntype in get_neighbours(node):
                    if grid[node[0]][node[1]].nodetype == 'mud':
                        continue
                    threshold = 500-(neighbour_cycles*10)
                    if random.randrange(1,101) <= threshold:
                        terrain_nodes.add(node)


    # Function for moving an item between two dicts
    def dict_move(from_dict, to_dict, item):
        to_dict[item] = from_dict[item]
        from_dict.pop(item)
        return from_dict, to_dict

    # + represents non-diagonal neighbours, x diagonal neighbours
    def get_neighbours(node, max_dimension=ROWS-1, diagonals=DIAGONALS):
        if not diagonals:
            neighbours = (
                ((min(max_dimension,node[0]+1),node[1]),"+"),
                ((max(0,node[0]-1),node[1]),"+"),
                ((node[0],min(max_dimension,node[1]+1)),"+"),
                ((node[0],max(0,node[1]-1)),"+")
            )
        else:
            neighbours = (
                ((min(max_dimension,node[0]+1),node[1]),"+"),
                ((max(0,node[0]-1),node[1]),"+"),
                ((node[0],min(max_dimension,node[1]+1)),"+"),
                ((node[0],max(0,node[1]-1)),"+"),
                ((min(max_dimension,node[0]+1),min(max_dimension,node[1]+1)),"x"),
                ((min(max_dimension,node[0]+1),max(0,node[1]-1)),"x"),
                ((max(0,node[0]-1),min(max_dimension,node[1]+1)),"x"),
                ((max(0,node[0]-1),max(0,node[1]-1)),"x")
            )

        # return neighbours
        return (neighbour for neighbour in neighbours if neighbour[0] != node)

    # For Pygame: this draws a square in the given location (for when properties updated)
    def draw_square(row,column,grid=grid):
        pygame.draw.rect(
            screen,
            grid[row][column].color,
            [
                (MARGIN + HEIGHT) * column + MARGIN,
                (MARGIN + HEIGHT) * row + MARGIN,
                WIDTH,
                HEIGHT
            ]
        )
        pygame.event.pump()

    # For Pygame: this updates the screen for the given square
    def update_square(row,column):
        pygame.display.update(
            (MARGIN + WIDTH) * column + MARGIN,
            (MARGIN + HEIGHT) * row + MARGIN,
            WIDTH,
            HEIGHT
        )
        pygame.event.pump()

    # randomized Prim's algorithm for creating random mazes
    def prim(mazearray=False, start_point=False, visualise=VISUALISE):

        # If a maze isn't input, we just create a grid full of walls
        if not mazearray:
            mazearray = []
            for row in range(ROWS):
                mazearray.append([])
                for column in range(ROWS):
                    mazearray[row].append(Node('wall'))
                    if visualise:
                        draw_square(row,column,grid=mazearray)

        n = len(mazearray) - 1

        if not start_point:
            start_point = (random.randint(0,n),random.randint(0,n))
        #     START_POINT = start_point
        # mazearray[start_point[0]][start_point[1]].update(nodetype='start')
        
        if visualise:
            draw_square(start_point[0], start_point[1], grid=mazearray)
            pygame.display.flip()

        walls = set([])
        # visited = set([])
        # blanks = set([])

        # visited.add(start_point)

        neighbours = get_neighbours(start_point, n)

        for neighbour, ntype in neighbours:
            if mazearray[neighbour[0]][neighbour[1]].nodetype == 'wall':
                walls.add(neighbour)

        # While there are walls in the list:
        # Pick a random wall from the list. If only one of the cells that the wall divides is visited, then:
        # # Make the wall a passage and mark the unvisited cell as part of the maze.
        # # Add the neighboring walls of the cell to the wall list.
        # Remove the wall from the list.
        while len(walls) > 0:
            wall = random.choice(tuple(walls))
            wall_neighbours = get_neighbours(wall, n)
            neighbouring_walls = set([])
            count = 0
            for wall_neighbour, ntype in wall_neighbours:
                if wall_neighbour == (start_point or END_POINT):
                    continue
                elif mazearray[wall_neighbour[0]][wall_neighbour[1]].nodetype != 'wall':
                    count += 1
                else:
                    neighbouring_walls.add(wall_neighbour)
                
            if count <= 1:
                mazearray[wall[0]][wall[1]].update(nodetype='blank')
                if visualise:
                    draw_square(wall[0],wall[1],mazearray)
                    update_square(wall[0],wall[1])
                    time.sleep(0.000001)

                walls.update(neighbouring_walls)

            
            walls.remove(wall)            

        mazearray[END_POINT[0]][END_POINT[1]].update(nodetype='end')
        mazearray[START_POINT[0]][START_POINT[1]].update(nodetype='start')

        return mazearray

    # Dijkstra's pathfinding algorithm, with the option to switch to A* by adding a heuristic of expected distance to end node
    def dijkstra(mazearray, start_point=(0,0), goal_node=False, display=pygame.display, visualise=VISUALISE, diagonals=DIAGONALS, astar=False):

        heuristic = 0
        distance = 0

        # Get the dimensions of the (square) maze
        n = len(mazearray) - 1
        
        # Create the various data structures with speed in mind
        visited_nodes = set()
        unvisited_nodes = set([(x,y) for x in range(n+1) for y in range(n+1)])
        queue = AStarQueue()

        queue.push(distance+heuristic, distance, start_point)
        v_distances = {}

        # If a goal_node is not set, put it in the bottom right (1 square away from either edge)
        if not goal_node:
            goal_node = (n,n)
        priority, current_distance, current_node = queue.pop()
        start = time.perf_counter()
        
        # Main algorithm loop
        while current_node != goal_node and len(unvisited_nodes) > 0:
            if current_node in visited_nodes:
                if len(queue.show()) == 0:
                    return False
                else:
                    priority, current_distance, current_node = queue.pop()
                    continue
            
            # Call to check neighbours of the current node
            for neighbour in get_neighbours(current_node, n, diagonals=diagonals):
                neighbours_loop(
                    neighbour, 
                    mazearr=mazearray, 
                    visited_nodes=visited_nodes, 
                    unvisited_nodes=unvisited_nodes, 
                    queue=queue, 
                    v_distances=v_distances, 
                    current_node=current_node,
                    current_distance=current_distance,
                    astar=astar
                )

            # When we have checked the current node, add and remove appropriately
            visited_nodes.add(current_node)
            unvisited_nodes.discard(current_node)
            
            # Add the distance to the visited distances dictionary (used for traceback)
            v_distances[current_node] = current_distance
            
            # Pygame part: visited nodes mark visited nodes as green
            if (current_node[0],current_node[1]) != start_point:
                mazearray[current_node[0]][current_node[1]].update(is_visited = True)
                draw_square(current_node[0],current_node[1],grid=mazearray)

                # If we want to visualise it (rather than run instantly)
                # then we update the grid with each loop
                if visualise:
                    update_square(current_node[0],current_node[1])
                    time.sleep(0.000001)
            
            # If there are no nodes in the queue then we return False (no path)
            if len(queue.show()) == 0:
                return False
            # Otherwise we take the minimum distance as the new current node
            else:
                priority, current_distance, current_node = queue.pop()
        
        # TODO: update this line so it works properly
        v_distances[goal_node] = current_distance + (1 if not diagonals else 2**0.5)
        visited_nodes.add(goal_node)

        # Draw the path back from goal node to start node
        trace_back(goal_node, start_point, v_distances, visited_nodes, n, mazearray, diags=diagonals, visualise=visualise)

        end = time.perf_counter()
        num_visited = len(visited_nodes)
        time_taken = end-start

        # Print timings
        print(f"Program finished in {time_taken:.4f} seconds after checking {num_visited} nodes. That is {time_taken/num_visited:.8f} seconds per node.")
        
        # The commented out line returns the distance to the end node
        # return False if v_distances[goal_node] == float('inf') else v_distances[goal_node]
        return False if v_distances[goal_node] == float('inf') else True


    # (DIJKSTRA/A*) loop to check all neighbours of the "current node"
    def neighbours_loop(neighbour, mazearr, visited_nodes, unvisited_nodes, queue, v_distances, current_node, current_distance, diags=DIAGONALS, astar=False):
        
        neighbour, ntype = neighbour

        heuristic = 0

        if astar:
            heuristic += abs(END_POINT[0] - neighbour[0]) + abs(END_POINT[1] - neighbour[1])
            heuristic *= 1 # if this goes above 1 then the shortest path is not guaranteed, but the attempted route becomes more direct
        
        # If the neighbour has already been visited 
        if neighbour in visited_nodes:
            pass
        elif mazearr[neighbour[0]][neighbour[1]].nodetype == 'wall':
            visited_nodes.add(neighbour)
            unvisited_nodes.discard(neighbour)
        else:
            modifier = mazearr[neighbour[0]][neighbour[1]].distance_modifier
            if ntype == "+":
                queue.push(current_distance+(1*modifier)+heuristic, current_distance+(1*modifier), neighbour)
            elif ntype == "x": 
                queue.push(current_distance+((2**0.5)*modifier)+heuristic, current_distance+((2**0.5)*modifier), neighbour)

    # (DIJKSTRA/A*) trace a path back from the end node to the start node after the algorithm has been run
    def trace_back(goal_node, start_node, v_distances, visited_nodes, n, mazearray, diags=False, visualise=VISUALISE):
        
        # begin the list of nodes which will represent the path back, starting with the end node
        path = [goal_node]
        
        current_node = goal_node
        
        # Set the loop in motion until we get back to the start
        while current_node != start_node:
            # Start an empty priority queue for the current node to check all neighbours
            neighbour_distances = PriorityQueue()
            
            neighbours = get_neighbours(current_node, n, diags)

            # Had some errors during testing, not sure if this is still necessary
            try:
                distance = v_distances[current_node]
            except Exception as e:
                print(e)
            
            # For each neighbour of the current node, add its location and distance
            # to a priority queue
            for neighbour, ntype in neighbours:
                if neighbour in v_distances:
                    distance = v_distances[neighbour]
                    neighbour_distances.push(distance, neighbour)
            
            # Pop the lowest value off; that is the next node in our path
            distance, smallest_neighbour = neighbour_distances.pop()
            mazearray[smallest_neighbour[0]][smallest_neighbour[1]].update(is_path=True)
            
            # Update pygame display
            draw_square(smallest_neighbour[0],smallest_neighbour[1],grid=mazearray)
            # update_square(smallest_neighbour[0],smallest_neighbour[1])            
            
            path.append(smallest_neighbour)
            current_node = smallest_neighbour

        pygame.display.flip()

        mazearray[start_node[0]][start_node[1]].update(is_path=True)


    def dfs(mazearray, start_point, goal_node, display=pygame.display, visualise=VISUALISE, diagonals=DIAGONALS):
        
        # Get the dimensions of the (square) maze
        n = len(mazearray) - 1
        
        # Create the various data structures with speed in mind
        mystack = []
        mystack.append(start_point)
        visited_nodes = set([])
        path_dict = {start_point: None}

        # Main algorithm loop
        while len(mystack) > 0:
            current_node = mystack.pop()
          
            if current_node == goal_node:
                # Trace back to start using path_dict
                path_node = goal_node
                while True:
                    path_node = path_dict[path_node]
                    mazearray[path_node[0]][path_node[1]].update(is_path = True)
                    draw_square(path_node[0],path_node[1],grid=mazearray)
                    if visualise:
                        update_square(path_node[0],path_node[1])
                    if path_node == start_point:
                        return True
            
            if mazearray[current_node[0]][current_node[1]].nodetype == 'wall':
                continue
            
            if current_node not in visited_nodes:
                visited_nodes.add(current_node)
                mazearray[current_node[0]][current_node[1]].update(is_visited = True)
                draw_square(current_node[0],current_node[1],grid=mazearray)
                if visualise:
                    update_square(current_node[0],current_node[1])
                    time.sleep(0.001)
                
                for neighbour, ntype in get_neighbours(current_node, n):
                    mystack.append(neighbour)
                    # Used for tracing back
                    if neighbour not in visited_nodes:
                        path_dict[neighbour] = current_node
        pygame.display.flip()
        return False

    grid[START_POINT[0]][START_POINT[1]].update(nodetype='start')
    grid[END_POINT[0]][END_POINT[1]].update(nodetype='end')

    # Update the GUI 
    def update_gui(draw_background=True, draw_buttons=True, draw_grid=True):
        
        if draw_background:
            # Draw a black background to set everything on
            screen.fill(BLACK)
            pass

        if draw_buttons:
            visToggleButton = Button(GREY, SCREEN_WIDTH/3, SCREEN_WIDTH + BUTTON_HEIGHT*2, SCREEN_WIDTH/3, BUTTON_HEIGHT, f"Visualise: {str(VISUALISE)}")
            # Draw Button below grid
            dijkstraButton.draw(screen, (0,0,0))
            dfsButton.draw(screen, (0,0,0))
            astarButton.draw(screen, (0,0,0))
            resetButton.draw(screen, (0,0,0))
            mazeButton.draw(screen, (0,0,0))
            vizmazeButton.draw(screen, (0,0,0))
            terrainButton.draw(screen, (0,0,0))
            visToggleButton.draw(screen, (0,0,0))

        if draw_grid:
            # Draw the grid
            for row in range(ROWS):
                for column in range(ROWS):
                    color = grid[row][column].color
                    draw_square(row,column)

    # --- Drawing code should go here
    update_gui()

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()
