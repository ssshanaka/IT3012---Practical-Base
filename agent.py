# agent.py
import math
import random
from collections import deque
import heapq

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

class SearchAgent:
    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def manhattan_distance(self, pos, goal):
        #Calculate the Manhattan distance between two positions.
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

    def _get_neighbors(self, state, percept):
        x, y = state
        width, height = percept['grid_size']
        walls = set(percept['walls'])
        
        neighbors = []
        # Try actions in a fixed order
        for action in self.actions_pool:
            nx, ny = x, y
            if action == 'Up':
                ny += 1
            elif action == 'Down':
                ny -= 1
            elif action == 'Left':
                nx -= 1
            elif action == 'Right':
                nx += 1
            
            # Check boundaries and walls
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                neighbors.append((action, (nx, ny)))
        return neighbors

    def bfs_search(self, start, goal, percept):
        queue = deque([(start, [])])
        reached = set([start])

        while queue:
            current, path = queue.popleft()
            
            if current == goal:
                return path

            for action, neighbor in self._get_neighbors(current, percept):
                if neighbor not in reached:
                    reached.add(neighbor)
                    queue.append((neighbor, path + [action]))
        return []

    def dfs_search(self, start, goal, percept):
        stack = [(start, [])]
        reached = set()

        while stack:
            current, path = stack.pop()
            
            if current == goal:
                return path

            if current not in reached:
                reached.add(current)
                for action, neighbor in self._get_neighbors(current, percept):
                    if neighbor not in reached:
                        stack.append((neighbor, path + [action]))
        return []

    def ucs_search(self, start, goal, percept):
        frontier = []
        heapq.heappush(frontier, (0, start, []))
        reached = {start: 0}

        while frontier:
            cost, current, path = heapq.heappop(frontier)

            if current == goal:
                return path
            
            if cost > reached.get(current, float('inf')):
                continue

            for action, neighbor in self._get_neighbors(current, percept):
                new_cost = cost + 1
                if new_cost < reached.get(neighbor, float('inf')):
                    reached[neighbor] = new_cost
                    heapq.heappush(frontier, (new_cost, neighbor, path + [action]))
        return []

    def sense_and_act(self, percept: dict) -> str:
        if not self.plan:
            agent_pos = tuple(percept['agent_pos'])
            all_food = percept['all_food']
            
            if not all_food:
                return random.choice(self.actions_pool)
            
            # Find closest food using Manhattan distance
            closest_food = min(all_food, key=lambda f: abs(f[0] - agent_pos[0]) + abs(f[1] - agent_pos[1]))
            
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(agent_pos, closest_food, percept)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(agent_pos, closest_food, percept)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(agent_pos, closest_food, percept)
                
            if not self.plan:
                return random.choice(self.actions_pool)

        return self.plan.pop(0)

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        """
        A* Search Algorithm combining path cost g(n) and heuristic estimate h(n):
        f(n) = g(n) + h(n)
        """
        start = tuple(start_pos)
        goal = tuple(goal_pos)
        walls_set = set(walls)
        width, height = grid_size

        # Choose heuristic function based on heuristic_type parameter
        if heuristic_type == 'euclidean':
            h_fn = self.euclidean_distance
        else:
            h_fn = self.manhattan_distance

        # Initialize priority queue and reached dictionary (or set)
        frontier = []
        h_start = h_fn(start, goal)
        heapq.heappush(frontier, (h_start, 0, start, []))
        reached = {start: 0}

        while frontier:
            f_cost, g_cost, current, path = heapq.heappop(frontier)

            # Goal check
            if current == goal:
                return path

            if g_cost > reached.get(current, float('inf')):
                continue

            # Node expansion: 4-way movement
            x, y = current
            moves = [
                ('Up', (x, y + 1)),
                ('Down', (x, y - 1)),
                ('Left', (x - 1, y)),
                ('Right', (x + 1, y))
            ]

            for action, (nx, ny) in moves:
                # Boundary and wall checks
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls_set:
                    neighbor = (nx, ny)
                    g_new = g_cost + 1
                    
                    if g_new < reached.get(neighbor, float('inf')):
                        reached[neighbor] = g_new
                        h_new = h_fn(neighbor, goal)
                        f_new = g_new + h_new
                        heapq.heappush(frontier, (f_new, g_new, neighbor, path + [action]))

        return []  # Return empty list if no path exists
