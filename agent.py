from collections import deque
import heapq


class SearchAgent:
    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'  # Options: 'BFS', 'DFS', 'UCS'

    def get_neighbors(self, state, walls, grid_size):
        """Generates valid non-wall adjacent moves matching grid directions."""
        x, y = state
        width, height = grid_size
        moves = [
            ((x, y + 1), 'Up'),
            ((x, y - 1), 'Down'),
            ((x - 1, y), 'Left'),
            ((x + 1, y), 'Right')
        ]
        valid_neighbors = []
        for (nx, ny), action in moves:
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                valid_neighbors.append(((nx, ny), action))
        return valid_neighbors

    def bfs_search(self, start, goal, walls, grid_size):
        """FIFO Queue: Explores shallowest nodes first."""
        frontier = deque([(start, [])])
        reached = {start}

        while frontier:
            state, path = frontier.popleft()
            if state == goal:
                return path

            for next_state, action in self.get_neighbors(state, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    def dfs_search(self, start, goal, walls, grid_size):
        """LIFO Stack: Explores deepest nodes first."""
        frontier = [(start, [])]
        reached = set()

        while frontier:
            state, path = frontier.pop()
            if state == goal:
                return path

            if state not in reached:
                reached.add(state)
                for next_state, action in self.get_neighbors(state, walls, grid_size):
                    if next_state not in reached:
                        frontier.append((next_state, path + [action]))
        return []

    def ucs_search(self, start, goal, walls, grid_size):
        """Priority Queue ordered by path cost g(n)."""
        frontier = [(0, start, [])]
        cost_so_far = {start: 0}

        while frontier:
            cost, state, path = heapq.heappop(frontier)
            if state == goal:
                return path

            if cost > cost_so_far.get(state, float('inf')):
                continue

            for next_state, action in self.get_neighbors(state, walls, grid_size):
                new_cost = cost + 1  # Unit step cost = 1
                if next_state not in cost_so_far or new_cost < cost_so_far[next_state]:
                    cost_so_far[next_state] = new_cost
                    heapq.heappush(frontier, (new_cost, next_state, path + [action]))
        return []

    def sense_and_act(self, percept):
        # Step 1.3: If the plan is empty, plan offline to find the closest food
        if not self.plan:
            start = percept['agent_pos']
            foods = percept['all_food']
            if not foods:
                return 'Stay'

            # Target the nearest food pellet using Manhattan distance
            goal = min(foods, key=lambda f: abs(f[0] - start[0]) + abs(f[1] - start[1]))
            walls = set(percept['walls'])
            grid_size = percept['grid_size']

            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start, goal, walls, grid_size)

        # Return the first action from the precomputed plan
        if self.plan:
            return self.plan.pop(0)
        return 'Stay'