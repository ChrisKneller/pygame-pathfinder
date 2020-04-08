import pygame
import asyncio
import time
from heapq import heapify, heappush, heappop
from priority_queue import PrioritySet

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WALL = (143,143,143)


# For creating buttons
class button():
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.text = text

    def draw(self,win,outline=None):
        # Call this method to draw the button on the screen
        if outline:
            pygame.draw.rect(win, outline, (self.x-2,self.y-2,self.width+4,self.height+4),0)
            
        pygame.draw.rect(win, self.color, (self.x,self.y,self.width,self.height),0)
        
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

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 5
HEIGHT = WIDTH # so they are squares
 
# This sets the margin between each cell
MARGIN = 1

# Create a 2 dimensional array (a list of lists)
grid = []
ROWS = 120
for row in range(ROWS):
    # Add an empty array that will hold each cell
    grid.append([])
    for column in range(ROWS):
        grid[row].append(0)  # Append a cell

# Set start and end points for the pathfinder
START_POINT=(1,1)
END_POINT=(ROWS-2,ROWS-2)

grid[START_POINT[0]][START_POINT[1]] = 'S'
grid[END_POINT[0]][END_POINT[1]] = 'E'

# Used for handling click & drag
mouse_drag = False
drag_start_point = False
drag_end_point = False

# Used for deciding what to do in different situations
path_found = False
algorithm_run = False

pygame.init()
 
# Set the width and height of the screen [width, height]
SCREEN_WIDTH = ROWS * (WIDTH + MARGIN) + MARGIN
SCREEN_HEIGHT = SCREEN_WIDTH + 50
WINDOW_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(WINDOW_SIZE)

# Make some buttons
goButton = button(WALL, 0, SCREEN_WIDTH, SCREEN_WIDTH/2, 50, "Go")
resetButton = button(WALL, SCREEN_WIDTH/2, SCREEN_WIDTH, SCREEN_WIDTH/2, 50, "Reset")

pygame.display.set_caption("Pathfinder")
 
# Loop until the user clicks the close button.
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
            
            # If click is inside grid
            if pos[1] <= SCREEN_WIDTH-1:
                # Change the x/y screen coordinates to grid coordinates
                column = pos[0] // (WIDTH + MARGIN)
                row = pos[1] // (HEIGHT + MARGIN)
                # Set click and drag treatment depending on where is clicked
                if (row,column) == START_POINT:
                    drag_start_point = True
                elif (row,column) == END_POINT:
                    drag_end_point = True
                else:
                    cell_updated = grid[row][column]
                    grid[row][column] = 'W'
                    mouse_drag = True
                    if algorithm_run and cell_updated != 'V':
                        path_found = update_path()
            
            # When the Go button is clicked
            elif goButton.isOver(pos):
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT and grid[row][column] != 'W':
                            grid[row][column] = 0
                update_gui(draw_background=False, draw_buttons=False)
                path_found = asyncio.run(path_finder(grid, START_POINT, END_POINT))
                grid[START_POINT[0]][START_POINT[1]] = 'S'
                algorithm_run = True
            
            # When the Reset button is clicked
            elif resetButton.isOver(pos):
                path_found = False
                algorithm_run = False
                for row in range(ROWS):
                    for column in range(ROWS):
                        if (row,column) != START_POINT and (row,column) != END_POINT:
                            grid[row][column] = 0
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Turn off all mouse drags if mouse button released
            mouse_drag = drag_end_point = drag_start_point = False
        
        elif event.type == pygame.MOUSEMOTION: 
            # User clicks the mouse. Get the position
            pos = pygame.mouse.get_pos()
            
            # Change the x/y screen coordinates to grid coordinates
            column = pos[0] // (WIDTH + MARGIN)
            row = pos[1] // (HEIGHT + MARGIN)
            
            # Turn mouse_drag off if mouse goes outside of grid
            if pos[1] >= SCREEN_WIDTH-2 or pos[1] <= 2 or pos[0] >= SCREEN_WIDTH-2 or pos[0] <= 2:
                mouse_drag = False
                continue
            
            # Build walls
            if mouse_drag == True:
                if (row,column) != START_POINT and (row,column) != END_POINT:
                    cell_updated = grid[row][column]
                    grid[row][column] = 'W'
                    if algorithm_run and cell_updated == 'X':
                        path_found = update_path()
            
            # Move the start point
            elif drag_start_point == True:
                grid[START_POINT[0]][START_POINT[1]] = 0
                START_POINT = (row,column)
                # If we have already run the algorithm, update it as the point is moved
                if algorithm_run:
                    path_found = update_path()
                grid[START_POINT[0]][START_POINT[1]] = 'S'
            
            # Move the end point
            elif drag_end_point == True:
                grid[END_POINT[0]][END_POINT[1]] = 0
                END_POINT = (row,column)
                grid[END_POINT[0]][END_POINT[1]] = 'E'
                # If we have already run the algorithm, update it as the point is moved
                if algorithm_run:
                    path_found = update_path()
                    grid[START_POINT[0]][START_POINT[1]] = 'S'

 
    # Game logic

    # Clear board, keeping start, end and wall nodes
    def clear_visited():
        for row in range(ROWS):
            for column in range(ROWS):
                if (row,column) != START_POINT and (row,column) != END_POINT and grid[row][column] != 'W':
                    grid[row][column] = 0
        update_gui(draw_background=False, draw_buttons=False)

    def update_path():
        clear_visited()
        path_found = asyncio.run(path_finder(grid, START_POINT, END_POINT, visualise=False))
        return path_found

    # Function for moving an item between two dicts
    def dict_move(from_dict, to_dict, item):
        to_dict[item] = from_dict[item]
        from_dict.pop(item)
        return from_dict, to_dict

    # Run Dijkstra's algorithm
    async def path_finder(mazearray, start_point=(0,0), goal_node=False, display=pygame.display, visualise=True):

        # Get the dimensions of the (square) maze
        n = len(mazearray) - 1
        
        # Create the various data structures with speed in mind
        visited_nodes = set()
        unvisited_nodes = set([(x,y) for x in range(n+1) for y in range(n+1)])
        # distances = {(x,y):float("inf") for x in range(n+1) for y in range(n+1)}
        queue = PrioritySet()
        queue.push(0, start_point)
        v_distances = {}

        # If a goal_node is not set, put it in the bottom right (1 square away from either edge)
        if not goal_node:
            goal_node = (n,n)
        current_distance, current_node = queue.pop()
        
        # Main algorithm loop
        while current_node != goal_node and len(unvisited_nodes) > 0:
            # print(f"Testing {current_node} with distance of {current_distance}")
            # print(f"Current queue is: {queue.show()}")
            # time.sleep(1)
            
            if current_node in visited_nodes:
                current_distance, current_node = queue.pop()
                continue
            
            # Neighbours defined as 1 square above, below, left or right
            neighbours = (
                (min(n,current_node[0]+1),current_node[1]),
                (max(0,current_node[0]-1),current_node[1]),
                (current_node[0],min(n,current_node[1]+1)),
                (current_node[0],max(0,current_node[1]-1))
                )

            diag_neighbours = (
                (min(n,current_node[0]+1),min(n,current_node[1]+1)),
                (min(n,current_node[0]+1),max(0,current_node[1]-1)),
                (max(0,current_node[0]-1),min(n,current_node[1]+1)),
                (max(0,current_node[0]-1),max(0,current_node[1]-1))
            )

            await asyncio.gather(*(neighbours_loop(
                neighbour, 
                mazearr=mazearray, 
                visited_nodes=visited_nodes, 
                unvisited_nodes=unvisited_nodes, 
                queue=queue, 
                v_distances=v_distances, 
                current_node=current_node,
                current_distance=current_distance,
                diags=True
                ) for neighbour in diag_neighbours))

            # Asynchronous call to check neighbours of the current node
            await asyncio.gather(*(neighbours_loop(
                neighbour, 
                mazearr=mazearray, 
                visited_nodes=visited_nodes, 
                unvisited_nodes=unvisited_nodes, 
                queue=queue, 
                v_distances=v_distances, 
                current_node=current_node,
                current_distance=current_distance
                ) for neighbour in neighbours))
        

            # When we have checked the current node, add and remove appropriately
            visited_nodes.add(current_node)
            unvisited_nodes.discard(current_node)
            
            # Move the visited node with its distance between the two dicts
            v_distances[current_node] = current_distance
            # distances, v_distances = dict_move(distances, v_distances, current_node)
            
            # Pygame part: visited nodes mark visited nodes as green
            if (current_node[0],current_node[1]) != start_point:
                mazearray[current_node[0]][current_node[1]] = "V"
                pygame.draw.rect(
                    screen,
                    GREEN,
                    [
                    (MARGIN + WIDTH) * current_node[1] + MARGIN,
                    (MARGIN + HEIGHT) * current_node[0] + MARGIN,
                    WIDTH,
                    HEIGHT
                    ]
                    )
                # If we want to visualise it (rather than run instantly)
                # then we update the grid with each loop
                if visualise:
                    pygame.display.update()
                    time.sleep(0.00001)
            
            # Try here in case distances dict is empty
            if len(queue.show()) == 0:
                return False
            else:
                current_distance, current_node = queue.pop()


        # Mark the goal node as a goal node again after it will have
        # temporarily been switched to a current node
        if current_node == goal_node:
            mazearray[goal_node[0]][goal_node[1]] = "E"
        
        v_distances[goal_node] = current_distance

        # Draw the path back from goal node to start node
        trace_back(goal_node, start_point, v_distances, n, mazearray)

        # The commented out line returns the distance to the end node
        # return False if v_distances[goal_node] == float('inf') else v_distances[goal_node]
        return False if v_distances[goal_node] == float('inf') else True


    # asyncronous loop to check all neighbours of the "current node"
    async def neighbours_loop(neighbour, mazearr, visited_nodes, unvisited_nodes, queue, v_distances, current_node, current_distance, diags=False):
        if neighbour in visited_nodes:
            pass
        elif mazearr[neighbour[0]][neighbour[1]] == 'W':
            visited_nodes.add(neighbour)
            unvisited_nodes.discard(neighbour)
            # distances, v_distances = dict_move(distances, v_distances, neighbour)
        else:
            if not diags:
                queue.push(current_distance+1, neighbour)
            else: 
                queue.push(current_distance+(2**0.5), neighbour)

    # trace a path back from the end node to the start node after the algorithm has been run
    def trace_back(goal_node, start_node, v_distances, n, mazearray):
        path = [goal_node]
        current_node = goal_node
        distance = v_distances[goal_node]
        while current_node != start_node:
            neighbours = (
                (min(n,current_node[0]+1),current_node[1]),
                (max(0,current_node[0]-1),current_node[1]),
                (current_node[0],min(n,current_node[1]+1)),
                (current_node[0],max(0,current_node[1]-1)),
                (min(n,current_node[0]+1),min(n,current_node[1]+1)),
                (min(n,current_node[0]+1),max(0,current_node[1]-1)),
                (max(0,current_node[0]-1),min(n,current_node[1]+1)),
                (max(0,current_node[0]-1),max(0,current_node[1]-1))
                )
            try:
                distance = v_distances[current_node]
            except Exception as e:
                print(e)
            for neighbour in neighbours:
                if neighbour == current_node:
                    continue
                elif neighbour in v_distances and v_distances[neighbour] <= distance - 1:
                    distance = v_distances[neighbour]
                    mazearray[current_node[0]][current_node[1]] = "X"
                    path.append(neighbour)
                    current_node = neighbour

        mazearray[start_node[0]][start_node[1]] = "X"


    # Update the GUI 
    def update_gui(draw_background=True, draw_buttons=True, draw_grid=True):
        
        if draw_background:
            # Draw a black background to set everything on
            screen.fill(BLACK)

        if draw_buttons:
            # Draw button below grid
            goButton.draw(screen, (0,0,0))
            resetButton.draw(screen, (0,0,0))

        if draw_grid:
            # Draw the grid
            for row in range(ROWS):
                for column in range(ROWS):
                    color = WHITE
                    if grid[row][column] == 'V':
                        color = GREEN
                    elif grid[row][column] == 'W':
                        color = WALL
                    elif grid[row][column] == 'S' or grid[row][column] == 'E' or grid[row][column] == 'X':
                        color = BLUE
                    pygame.draw.rect(
                        screen,
                        color,
                        [
                        (MARGIN + WIDTH) * column + MARGIN,
                        (MARGIN + HEIGHT) * row + MARGIN,
                        WIDTH,
                        HEIGHT
                        ]
                        )
 
    # --- Drawing code should go here
    update_gui()

    # --- Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
    # --- Limit to 60 frames per second
    clock.tick(60)
 
# Close the window and quit.
pygame.quit()
