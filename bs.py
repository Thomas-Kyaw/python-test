import sys
import re
import tkinter as tk
from queue import Queue
import time

def read_input_file(file_path):
    # Reads an input file, filtering out comments and blank lines.
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
        content = [line.split('//')[0].strip() for line in content if line.strip() and not line.strip().startswith('//')]
        return content
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)

def extract_grid_dimensions(line):
    # Extracts the number of rows and columns for the grid from the first line of the input.
    numbers = re.findall(r'\d+', line)
    if len(numbers) >= 2:
        return int(numbers[0]), int(numbers[1])
    else:
        print("Error: The first line should contain at least two numbers.")
        sys.exit(1)

def create_empty_grid(num_rows, num_cols, initial_state, goal_states):
    # Creates an empty grid and marks the initial and goal positions.
    grid = [['-' for _ in range(num_cols)] for _ in range(num_rows)]
    grid[initial_state[1]][initial_state[0]] = 'R'
    for goal in goal_states:
        grid[goal[1]][goal[0]] = 'G'
    return grid

def place_blocks(grid, blocks):
    # Places obstacles ('X') on the grid as specified in the input.
    for block in blocks:
        x, y, w, h = block
        for i in range(h):
            for j in range(w):
                if 0 <= y+i < len(grid) and 0 <= x+j < len(grid[0]):
                    grid[y+i][x+j] = 'X'

def print_grid(grid, path=[], nodes_visited=set(), goal_node=None):
    direction_symbols = {(0, -1): 'up', (0, 1): 'down', (-1, 0): 'left', (1, 0): 'right'}
    for y in range(len(grid)):
        row = ''
        for x in range(len(grid[0])):
            char = grid[y][x]
            if (x, y) == goal_node:
                char = 'G'
            elif (x, y) in path:
                next_node = path[path.index((x, y)) + 1] if path.index((x, y)) + 1 < len(path) else None
                if next_node:
                    dx, dy = next_node[0] - x, next_node[1] - y
                    char = direction_symbols.get((dx, dy), 'P')
            elif (x, y) in nodes_visited:
                char = '*'
            row += f'{char} '
        print(row.strip())

def get_neighbors(position, grid):
    # Returns valid, non-obstacle neighbors of a given position with UP, LEFT, DOWN, RIGHT priority.
    x, y = position
    neighbors = []
    directions = [(-1, 0), (0, -1), (1, 0), (0, 1)]  # UP, LEFT, DOWN, RIGHT
    for dy, dx in directions:  # Adjusted to reflect priority order
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] != 'X':
            neighbors.append((nx, ny))
    return neighbors

def print_direction_path(path):
    if not path:
        print("Direction path: None")
        return

    direction_symbols = {
        (0, -1): 'up', (0, 1): 'down',
        (-1, 0): 'left', (1, 0): 'right'
    }
    directions = []
    for i in range(1, len(path)):
        dx, dy = path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]
        # Debugging information
        if (dx, dy) not in direction_symbols:
            print(f"Unexpected movement from {path[i-1]} to {path[i]} with delta ({dx}, {dy})")
        direction = direction_symbols.get((dx, dy), 'unknown')
        directions.append(direction)

    print("Direction path:", '; '.join(directions))

# GUI setup
def setup_gui(grid):
    global window, canvas
    window = tk.Tk()
    window.title("Bidirectional Search Visualization")
    
    canvas_size = 500
    cell_size = canvas_size // max(len(grid), len(grid[0]))
    canvas = tk.Canvas(window, width=len(grid[0])*cell_size, height=len(grid)*cell_size)
    canvas.pack()

    draw_grid(grid, cell_size)
    window.update()
    return cell_size

def draw_grid(grid, cell_size):
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            color = 'white'
            if grid[y][x] == 'X':
                color = 'black'
            elif grid[y][x] == 'R':
                color = 'blue'
            elif grid[y][x] == 'G':
                color = 'green'
            canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, fill=color, outline='gray')

def update_gui(path_from_start, path_from_goal, cell_size):
    for position in path_from_start:
        x, y = position
        canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, fill='light blue', outline='gray')

    for position in path_from_goal:
        x, y = position
        canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, fill='pink', outline='gray')
    
    window.update()

def reconstruct_path(visited, current):
    # Reconstructs the path from visited nodes
    path = []
    while current is not None:
        if path and current == path[-1]:  # Avoid adding the same node twice
            print(f"Skipping duplicate node: {current}")
            break
        path.append(current)
        current = visited[current]
    return path[::-1]  # Return reversed path

def draw_final_path(path, cell_size):
    for position in path:
        x, y = position
        canvas.create_rectangle(x*cell_size, y*cell_size, (x+1)*cell_size, (y+1)*cell_size, fill='yellow', outline='gray')
    window.update_idletasks()
    window.update()

def parse_tuple(s):
    # Extracts numbers from a string and returns them as a tuple of integers
    return tuple(map(int, re.findall(r'\d+', s)))

def bidirectional_search_unified(grid, start, goal, update_func=None, cell_size=None):
    queue_start = Queue()
    queue_goal = Queue()

    queue_start.put((start, [start]))
    queue_goal.put((goal, [goal]))

    visited_start = {start: None}
    visited_goal = {goal: None}

    nodes_visited_from_start = set()
    nodes_visited_from_goal = set()

    while not queue_start.empty() and not queue_goal.empty():
        if not queue_start.empty():
            current_start, path_start = queue_start.get()
            nodes_visited_from_start.add(current_start)
            if current_start in visited_goal:
                # Properly merge paths without duplicating the meeting point
                path_from_start = reconstruct_path(visited_start, current_start)[:-1]  # Exclude last node to avoid duplication
                path_from_goal = reconstruct_path(visited_goal, current_start)
                final_path = path_from_start + path_from_goal[::-1]  # Reverse goal path and concatenate
                return True, final_path, nodes_visited_from_start, nodes_visited_from_goal
            for neighbor in get_neighbors(current_start, grid):
                if neighbor not in visited_start:
                    visited_start[neighbor] = current_start
                    queue_start.put((neighbor, path_start + [neighbor]))
                    if update_func:
                        update_func(path_start, [], cell_size)

        if not queue_goal.empty():
            current_goal, path_goal = queue_goal.get()
            nodes_visited_from_goal.add(current_goal)
            if current_goal in visited_start:
                final_path = reconstruct_path(visited_start, current_goal) + reconstruct_path(visited_goal, current_goal)[::-1]
                return True, final_path, nodes_visited_from_start, nodes_visited_from_goal
            for neighbor in get_neighbors(current_goal, grid):
                if neighbor not in visited_goal:
                    visited_goal[neighbor] = current_goal
                    queue_goal.put((neighbor, path_goal + [neighbor]))
                    if update_func:
                        update_func([], path_goal, cell_size)

        if update_func:
            time.sleep(0.5)

    return False, [], nodes_visited_from_start, nodes_visited_from_goal


def main(file_path, use_gui=False):
    content = read_input_file(file_path)
    num_rows, num_cols = extract_grid_dimensions(content[0])
    initial_state = parse_tuple(content[1])
    goal_states = [parse_tuple(goal_state) for goal_state in content[2].split('|')]
    blocks = [parse_tuple(block) for block in content[3:]]

    grid = create_empty_grid(num_rows, num_cols, initial_state, goal_states)
    place_blocks(grid, blocks)

    if use_gui:
        cell_size = setup_gui(grid)
        window.update_idletasks()

    goal_state = goal_states[0] if goal_states else None
    if goal_state:
        success, path, nodes_visited_from_start, nodes_visited_from_goal = bidirectional_search_unified(
            grid, initial_state, goal_state, update_gui if use_gui else None, cell_size if use_gui else None
        )
        if success:
            print("Path found!")
            print(f"Goal node: {goal_state}")
            print("Total nodes visited:", len(nodes_visited_from_start | nodes_visited_from_goal))
            print_direction_path(path)
            if use_gui:
                draw_final_path(path, cell_size)
                window.mainloop()
        else:
            print("No path found.")
    else:
        print("Error: No goal state provided.")

if __name__ == "__main__":
    use_gui = '--gui' in sys.argv
    file_path = None
    for arg in sys.argv[1:]:
        if arg != '--gui':
            file_path = arg
            break

    if file_path is None:
        print("Usage: python script.py <file_path> [--gui]")
        sys.exit(1)

    main(file_path, use_gui)
    