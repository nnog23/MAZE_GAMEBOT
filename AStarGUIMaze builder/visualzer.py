# Import necessary libraries and modules
import pygame  # Import the pygame library for creating a game window
import math  # Import the math library for mathematical operations
from queue import PriorityQueue  # Import the PriorityQueue data structure
import os  # Import the os library for file operations
import PySimpleGUI as sg  # Import the PySimpleGUI library for creating a GUI interface
import time  # Import the time library for handling time-related functions



def start_animation(grid, start, end):
    # Declare global variables to track time and steps
    global time_start, time_end, total_time, steps

    # Record the start time for performance measurement
    time_start = time.time()

    # Update neighbors for each spot in the grid
    for row in grid:
        for spot in row:
            spot.update_neighbors(grid)

    # Run the pathfinding algorithm and count the number of steps taken
    steps = algorithm(lambda: draw(WIN, grid, ROWS, WIDTH), grid, start, end)

    # Record the end time for performance measurement
    time_end = time.time()

    # Calculate the total time taken for the algorithm
    total_time = time_end - time_start

    # Draw the final result for the number of steps taken
    for _ in range(steps):
        draw(WIN, grid, ROWS, WIDTH)

    # Create a GUI window to display algorithm statistics
    layout = [
        [sg.Text(f"Expanded Nodes: {expanded_nodes}")],
        [sg.Text(f"Time: {total_time:.4f} seconds")],
        [sg.Text(f"Steps: {steps}")],
        [sg.Button("OK")]
    ]

    window = sg.Window('Algorithm Statistics', layout, keep_on_top=True, grab_anywhere=True)
    print("Total time: ",total_time)  # Print the total time to the console

    while True:
        event, values = window.read()

        # Close the window when the user clicks OK or closes the window
        if event in (sg.WIN_CLOSED, 'OK'):
            break

    window.close()








def get_valid_maze_size():
    # Loop until a valid maze size is entered by the user
    while True:
        layout = [
            [sg.Text("Enter the size of the maze (between 8 and 64):")],
            [sg.InputText(key='n')],
            [sg.Submit(), sg.Cancel()]
        ]

        window = sg.Window('Maze Size Input', layout)

        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel'):
            pygame.quit()
            exit()  # Terminate the program if the user cancels or closes the window

        try:
            n = int(values['n'])
            if 8 <= n <= 64:  # Check if the entered size is within the valid range
                window.close()
                return n  # Return the valid maze size
            else:
                sg.popup_error("Please enter a valid size between 8 and 64.")
        except ValueError:
            sg.popup_error("Please enter a valid integer value.")
        finally:
            window.close()  # Close the input window after processing

            
def get_maze_file():
    # Create a GUI window for loading a maze file
    layout = [
        [sg.Text("Select a maze file to load:")],
        [sg.InputText(key='file_path', enable_events=True), sg.FileBrowse()],
        [sg.Submit(), sg.Cancel()]
    ]

    window = sg.Window('Load Maze File', layout)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel'):
            window.close()
            return None  # Return None if the user cancels or closes the window

        if event == 'Submit':
            file_path = values['file_path']
            window.close()
            return file_path  # Return the selected file path when the user submits

    window.close()




# Get a valid maze size from the user
n = get_valid_maze_size()

# Constants for the maze size
WIDTH = 800
ROWS = n
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

MIN_N = 8
MAX_N = 64

expanded_nodes = 0
steps = 0

# Create a Pygame window and set its title

WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Path Finding Algorithm")

# Define color constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# Define maze symbols
WALL = '#'      # Symbol for walls in the maze
OPEN = '.'      # Symbol for open paths in the maze
START = 'S'     # Symbol for the starting point
GOAL = 'G'      # Symbol for the goal or destination
VISITED = 'V'   # Symbol to mark visited cells during pathfinding
PATH = 'P'      # Symbol to mark the final path

def play_sound(soundprompt):
    # Define the directory where sound files are located
    dir = "..\\assets"

    # Initialize the Pygame library and mixer
    pygame.init()
    pygame.mixer.init()

    # Create Pygame mixer channels
    chan1 = pygame.mixer.Channel(1)
    chan0 = pygame.mixer.Channel(0)

    # Play different sounds based on the provided soundprompt
    if soundprompt == "aespa":
        aespa = pygame.mixer.Sound(dir + "\\aespa - Better Things.mp3")
        aespa.set_volume(0.01)
        chan0.queue(aespa)
    if soundprompt == "watersports":
        sound2 = pygame.mixer.Sound(dir + "\\waterdrop.mp3")
        chan1.queue(sound2)
    if soundprompt == "woodworks":
        sound3 = pygame.mixer.Sound(dir + "\\openspace.mp3")
        chan1.queue(sound3)
    if soundprompt == "start":
        sound4 = pygame.mixer.Sound(dir + "\\start.mp3")
        chan1.queue(sound4)
    if soundprompt == "goal":
        sound5 = pygame.mixer.Sound(dir + "\\goal.mp3")
        chan1.queue(sound5)
    if soundprompt == "solve":
        sound6 = pygame.mixer.Sound(dir + "\\space.mp3")
        chan1.queue(sound6)
    if soundprompt == "solulu":
        sound7 = pygame.mixer.Sound(dir + "\\pathfound.mp3")
        chan1.queue(sound7)
    if soundprompt == "browsefile":
        sound8 = pygame.mixer.Sound(dir + "\\fileopen.mp3")
        chan1.queue(sound8)
    if soundprompt == "loadfile":
        sound9 = pygame.mixer.Sound(dir + "\\fileload.mp3")
        chan1.queue(sound9)


class Node:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE  # Initialize spot color as white
        self.neighbors = []  # Initialize the list of neighboring spots
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE  # Reset the spot's color to white

    def make_start(self):
        self.color = ORANGE  # Set the spot's color to orange (start)

    def make_closed(self):
        self.color = RED  # Set the spot's color to red (closed)

    def make_open(self):
        self.color = GREEN  # Set the spot's color to green (open)

    def make_barrier(self):
        self.color = BLACK  # Set the spot's color to black (barrier)

    def make_end(self):
        self.color = TURQUOISE  # Set the spot's color to turquoise (end)

    def make_path(self):
        self.color = PURPLE  # Set the spot's color to purple (path)

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        # Add neighboring spots to the list, checking for barriers
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False

def h(p1, p2):
    # Calculate the Manhattan distance (heuristic) between two points p1 and p2
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    step_count = 0

    while current in came_from:
        current = came_from[current]
        current.make_path()
        step_count += 1
        draw()

    play_sound("solulu")  # Play a sound to indicate the path has been found
    return step_count


def algorithm(draw, grid, start, end):
    global expanded_nodes, steps  # Declare as global variables
    expanded_nodes = 0
    steps = 0

    play_sound("solve")  # Play a sound to indicate the algorithm is solving

    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        current = open_set.get()[2]
        open_set_hash.remove(current)
        expanded_nodes += 1  # Increment the number of expanded nodes

        if current == end:
            steps = reconstruct_path(came_from, end, draw)
            end.make_end()
            return steps

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()  # Call the draw function to update the visualization

        if current != start:
            current.make_closed()

    return steps  # Return the number of steps taken to find the path


def make_grid(rows, width):
    # Create a grid of spots based on the given number of rows and width
    grid = []
    gap = width // rows

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Node(i, j, gap, rows)
            grid[i].append(spot)

    return grid



def draw_grid(win, rows, width):
    # Draw the grid lines on the Pygame window
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)  # Fill the Pygame window with a white background

    for row in grid:
        for spot in row:
            spot.draw(win)  # Draw each spot on the window

    draw_grid(win, rows, width)  # Draw the grid lines
    pygame.display.update()  # Update the Pygame display to show the changes


def get_clicked_pos(pos, rows, width):
    # Calculate the row and column of a spot based on the mouse click position
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col
# Import necessary libraries or modules (pygame and other dependencies) here
# ...

def main(win, width):
    # Initialize grid, sound, and drawing mode variables
    grid = make_grid(ROWS, width)
    sound = "aespa"
    play_sound(sound)
    start = None
    end = None
    draw_mode = None  # Variable to keep track of the current drawing mode
    run = True
    edit_mode = True  # Set to True initially to enable editing

    # Main game loop
    while run:
        draw(win, grid, ROWS, width)  # Render the grid on the window

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False  # Exit the main loop if the window is closed

            if edit_mode:
                if event.type == pygame.KEYDOWN:
                    if event.type == pygame.KEYDOWN and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        if event.key == pygame.K_o:
                            # Load a maze from a file
                            play_sound("browsefile")
                            grid = load_maze("filename", ROWS, width)
                            print("Loaded the maze from 'maze.txt'")
                            play_sound("aespa")

                    if event.key == pygame.K_SPACE and start and end:
                        # Start pathfinding animation
                        edit_mode = False  # Stop edit mode and start animation
                        for row in grid:
                            for spot in row:
                                spot.update_neighbors(grid)
                        start_animation(grid, start, end)
                        edit_mode = False  # Stop edit mode and start animation

                    # Set the current drawing mode
                    if event.key == pygame.K_w:
                        draw_mode = "wall"
                        print("Draw walls mode: Left-click to draw walls")
                    if event.key == pygame.K_s:
                        draw_mode = "start"
                        print("Set Start mode: Right-click to set the Start position")
                    if event.key == pygame.K_g:
                        draw_mode = "goal"
                        print("Set Goal mode: Right-click to set the Goal position")
                    if event.key == pygame.K_o:
                        draw_mode = "open"
                        print("Set Open space mode: Right-click to set an Open space")
                    if event.key == pygame.K_c:
                        # Clear the maze
                        start = None
                        end = None
                        grid = make_grid(ROWS, width)
                        edit_mode = True  # Reset the edit mode
                        print("Cleared the maze")

            if event.type == pygame.KEYDOWN and pygame.key.get_mods() & pygame.KMOD_CTRL:
                if event.key == pygame.K_s:
                    # Save the maze to a file
                    save_maze(grid, "maze.txt")
                    print("Saved the maze to 'maze.txt'")
                if event.key == pygame.K_o:
                    # Load a maze from a user-selected file
                    maze_file = get_maze_file()
                    if maze_file:
                        grid, start, end = load_maze(maze_file, ROWS, width)
                        print(f"Loaded the maze from '{maze_file}'")
                        draw_mode = None  # Clear the drawing mode

            if pygame.mouse.get_pressed()[0]:  # LEFT mouse button
                if draw_mode == "wall":
                    # Draw walls when left-clicked
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    spot.make_barrier()
                    play_sound("watersports")

            elif pygame.mouse.get_pressed()[2]:  # RIGHT mouse button
                if draw_mode == "start":
                    # Set the Start position when right-clicked
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    if not start and spot != end:
                        start = spot
                        start.make_start()
                    elif spot != end:
                        start.reset()
                        start = spot
                        start.make_start()
                    play_sound("start")

                elif draw_mode == "goal":
                    # Set the Goal position when right-clicked
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    if not end and spot != start:
                        end = spot
                        end.make_end()
                    elif spot != start:
                        end.reset()
                        end = spot
                        end.make_end()
                    play_sound("goal")

                elif draw_mode == "open":
                    # Clear a spot when right-clicked to make it an open space
                    pos = pygame.mouse.get_pos()
                    row, col = get_clicked_pos(pos, ROWS, width)
                    spot = grid[row][col]
                    spot.reset()
                    play_sound("woodworks")

        if not run:
            pygame.quit()  # Properly close the Pygame window
    


def save_maze(grid, filename):
    # Open the specified file for writing
    with open(filename, 'w') as f:
        # Iterate over each row in the grid
        for row in grid:
            # Convert each cell's color in the row to symbols
            row_symbols = [
                WALL if spot.color == BLACK else
                OPEN if spot.color == WHITE else
                START if spot.color == ORANGE else
                GOAL if spot.color == TURQUOISE else
                '' for spot in row
            ]
            # Write the row of symbols to the file and add a newline
            f.write("".join(row_symbols) + "\n")


def load_maze(filename, rows, width):
    # Check if the file with the specified filename exists
    if os.path.exists(filename):
        # Open the file for reading
        with open(filename, 'r') as f:
            # Read the maze data from the file and remove leading/trailing whitespaces
            maze_data = [line.strip() for line in f.readlines()]

        # Create a new grid with the specified number of rows and width
        grid = make_grid(rows, width)
        start = None
        end = None

        # Iterate through the loaded maze data
        for row_idx, row_symbols in enumerate(maze_data):
            for col_idx, symbol in enumerate(row_symbols):
                spot = grid[row_idx][col_idx]

                # Check the symbol and configure the cell accordingly
                if symbol == WALL:
                    spot.make_barrier()
                elif symbol == OPEN:
                    spot.reset()
                elif symbol == START:
                    if start is None:
                        start = spot
                        start.make_start()
                elif symbol == GOAL:
                    if end is None:
                        end = spot
                        end.make_end()

        # Play a sound to indicate that the file was successfully loaded
        play_sound("loadfile")

        # Return the grid and the start and end positions
        return grid, start, end

    # If the file does not exist, create a new grid and return it with no start and end positions
    return make_grid(rows, width), None, None


if __name__ == "__main__":
    # Print instructions for using the Maze Builder Controls
    print("Maze Builder Controls:")
    print("  - Click and drag to draw walls (left mouse button)")
    print("  - Click to set the Start (blue) and Goal (green) positions (right mouse button)")
    print("  - Use the spacebar to solve the maze (stop edit mode and start animation)")
    print("  - Press 'w' to set the wall drawing mode")
    print("  - Press 's' to set the Start drawing mode")
    print("  - Press 'g' to set the Goal drawing mode")
    print("  - Press 'o' to set the Open space drawing mode")
    print("  - Press 'c' to clear the maze")
    print("  - Press 'Ctrl + s' to save the maze to a text file")
    print("  - Press 'Ctrl + o' to load a maze from a text file")

    # Initialize the Pygame window
    WIN = pygame.display.set_mode((WIDTH, WIDTH))
    pygame.display.set_caption("A* Search Path Finding Algorithm")

    # Get a valid maze size from the user (It appears to be commented out)
    # n = get_valid_maze_size()

    # Update the number of rows
    ROWS = n

    # Create the grid using the specified number of rows and width
    grid = make_grid(ROWS, WIDTH)

    # Start the PySimpleGUI event loop to get the maze size and manage user interactions
    main(WIN, WIDTH)

