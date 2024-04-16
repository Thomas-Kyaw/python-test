import sys
import re
import tkinter as tk
from queue import PriorityQueue
from time import sleep
import itertools

# Global counter for nodes insertion order
insertion_counter = itertools.count()
visited_nodes = 0 

# Function to read the input file
def read_input_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        content = [line.split('//')[0].strip() for line in content if line.strip() and not line.strip().startswith('//')]
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

# Function to extract grid dimensions
def extract_grid_dimensions(line):
    numbers = re.findall(r'\d+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    else:
        print("Error: The first line should contain at least two numbers.")
        sys.exit(1)

# Function to create an empty grid
def create_empty_grid(num_rows, num_cols, initial_state, goal_states):
    grid = [['-' for _ in range(num_cols)] for _ in range(num_rows)]
    grid[initial_state[1]][initial_state[0]] = 'R'
    for goal in goal_states:
        grid[goal[1]][goal[0]] = 'G'
    return grid

# Function to place blocks on the grid
def place_blocks(grid, blocks):
    for block in blocks:
        x, y, w, h = block
        for i in range(h):
            for j in range(w):
                if 0 <= y+i < len(grid) and 0 <= x+j < len(grid[0]):
                    grid[y+i][x+j] = 'X'

# Function to calculate the Manhattan distance
def manhattan_distance(start, goal):
    return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

# GUI elements
window = None
grid_frame = None

# Function to update the GUI
def update_gui(grid, current, open_set, path=[]):
    global grid_frame
    if grid_frame is None:
        return

    # Destroy all existing widgets in the grid frame
    for widget in grid_frame.winfo_children():
        widget.destroy()

    cell_size = 70
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            # Set the color of the cell based on its state
            if (x, y) in path:
                color = 'yellow'  # Highlight path in yellow
            elif grid[y][x] == 'X':
                color = 'black'  # Blocks are black
            elif grid[y][x] == 'R' or (x, y) == current:
                color = 'blue'  # The robot's position is blue
            elif grid[y][x] == 'G':
                color = 'green'  # Goal states are green
            elif (x, y) in [item[2] for item in open_set.queue]:
                color = 'orange'  # Cells in the open set are orange

            # Create a new cell in the grid frame
            cell = tk.Frame(grid_frame, width=cell_size, height=cell_size, bg=color, borderwidth=1, relief="solid")
            cell.grid(row=y, column=x)

    # Update the window to reflect the changes
    window.update()

# Function to perform the A* search
# Function to perform the A* search
def a_star_search(grid, start, goal_states):
    global visited_nodes  # Add this line to declare visited_nodes as global
    open_set = PriorityQueue()
    open_set.put((0, next(insertion_counter), start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: manhattan_distance(start, goal_states[0])}

    # Continue until there are no more cells to visit
    while not open_set.empty():
        _, _, current = open_set.get()
        visited_nodes += 1

        # If the current cell is a goal state, the path has been found
        if current in goal_states:
            path, directions = reconstruct_path(came_from, start, current)
            return True, path, directions

        # Visit all neighbors of the current cell
        for dx, dy in [(0, -1), (-1, 0), (0, 1), (1, 0)]:
            neighbor = (current[0] + dx, current[1] + dy)

            # If the neighbor is within the grid and not a block, consider it
            if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid) and grid[neighbor[1]][neighbor[0]] != 'X':
                tentative_g_score = g_score[current] + 1

                # If this path to the neighbor is better than any previous one, record it
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + manhattan_distance(neighbor, goal_states[0])

                    # If the neighbor is not in the open set, add it
                    if neighbor not in [item[2] for item in open_set.queue]:
                        open_set.put((f_score[neighbor], next(insertion_counter), neighbor))

        # Update the GUI to reflect the current state of the search
        update_gui(grid, current, open_set, [])
        sleep(0.5)

    # If the open set is empty and no path has been found, return failure
    return False, []

# Function to get the direction between two nodes
def get_direction(current, next_node):
    direction_map = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}
    dx = next_node[0] - current[0]
    dy = next_node[1] - current[1]
    return direction_map.get((dx, dy), 'unknown')

# Function to reconstruct the path and directions including the last step into the goal
def reconstruct_path(came_from, start, goal):
    path = []
    directions = []
    current = goal
    
    while current in came_from:  # Traverse back from goal to start
        next_node = came_from[current]
        direction = get_direction(next_node, current)
        directions.append(direction)
        current = next_node
        path.append(current)

    path.append(start)  # Optional, if you want to include the starting position in the path
    path.reverse()  # Reverse to get the path from start to goal
    directions.reverse()  # Directions need to be reversed as well
    
    # Add the last step which is moving into the goal state
    if path[-1] != goal:
        last_step_direction = get_direction(path[-1], goal)
        directions.append(last_step_direction)
        path.append(goal)  # Optional, explicitly add the goal position

    return path, directions

# Main function and entry point
def main(file_path, use_gui=False):
    global window, grid_frame
    if use_gui:
        window = tk.Tk()
        window.title("A* Pathfinding")
        grid_frame = tk.Frame(window)
        grid_frame.pack()

        def on_window_close():
            global window
            if window:
                window.quit()
                window = None

        window.protocol("WM_DELETE_WINDOW", on_window_close)

    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = tuple(map(int, re.findall(r'\d+', content[1])))
    goal_states = [tuple(map(int, re.findall(r'\d+', x))) for x in content[2].split('|')]
    blocks = [tuple(map(int, re.findall(r'\d+', x))) for x in content[3:]]

    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    def print_grid(grid, path):
        for y in range(len(grid)):
            for x in range(len(grid[0])):
                if (x, y) in path:
                    print('P', end=' ')
                elif grid[y][x] == 'X':
                    print('X', end=' ')
                elif grid[y][x] == 'R':
                    print('R', end=' ')
                elif grid[y][x] == 'G':
                    print('G', end=' ')
                else:
                    print('.', end=' ')
            print()

    if use_gui:
        found, path, directions = a_star_search(grid, initial_state, goal_states)  # Corrected to unpack three values
        if found:
            # Final update to draw the entire path in yellow
            update_gui(grid, None, PriorityQueue(), path)
            print_grid(grid, path)
            print("Path found with directions:")
            print(directions)
            print("Number of nodes visited:", visited_nodes)
        else:
            print("Path not found.")
        window.mainloop()
    else:
        found, path, directions = a_star_search(grid, initial_state, goal_states)  # Corrected to unpack three values
        if found:
            print_grid(grid, path)
            print("Path found with directions:")
            print(directions)
            print("Number of nodes visited:", visited_nodes)
        else:
            print("Path not found.")


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python as.py <file_path> [--gui]")
        sys.exit(1)

    use_gui = '--gui' in sys.argv
    file_path = sys.argv[1] if sys.argv[1] != '--gui' else sys.argv[2]
    main(file_path, use_gui)
