"""
aco.py - Ant Colony Optimization Algorithm
==========================================
Many ants explore the graph, and shorter safer paths gain pheromone.
"""

import random


class ACO:
    def __init__(self, graph, num_ants=30, num_iterations=100,
                 alpha=1.0, beta=3.0, evaporation=0.5, Q=100):
        self.graph = graph
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.Q = Q

        self.pheromone = {}
        for node in graph:
            for neighbor, _dist in graph[node]:
                self.pheromone[(node, neighbor)] = 1.0

    def _get_pheromone(self, a, b):
        return self.pheromone.get((a, b), self.pheromone.get((b, a), 1.0))

    def _set_pheromone(self, a, b, value):
        self.pheromone[(a, b)] = value
        self.pheromone[(b, a)] = value

    def _choose_next(self, current, visited, danger_nodes):
        neighbors = self.graph.get(current, [])
        choices = []
        weights = []

        for neighbor, dist in neighbors:
            if neighbor in visited:
                continue
            if neighbor in danger_nodes:
                continue

            pheromone = self._get_pheromone(current, neighbor)
            desirability = 1.0 / dist
            weight = (pheromone ** self.alpha) * (desirability ** self.beta)

            choices.append(neighbor)
            weights.append(weight)

        if not choices:
            return None

        total = sum(weights)
        if total == 0:
            return random.choice(choices)

        r = random.uniform(0, total)
        cumulative = 0
        for node, weight in zip(choices, weights):
            cumulative += weight
            if r <= cumulative:
                return node

        return choices[-1]

    def _path_distance(self, path):
        total = 0
        for i in range(len(path) - 1):
            node_a = path[i]
            node_b = path[i + 1]
            for neighbor, dist in self.graph.get(node_a, []):
                if neighbor == node_b:
                    total += dist
                    break
        return total

    def _ant_walk(self, start, end, danger_nodes):
        if start in danger_nodes or end in danger_nodes:
            return None

        path = [start]
        visited = {start}
        current = start
        max_steps = len(self.graph) * 3

        for _ in range(max_steps):
            if current in danger_nodes:
                return None
            if current == end:
                return path

            next_node = self._choose_next(current, visited, danger_nodes)
            if next_node is None:
                return None

            path.append(next_node)
            visited.add(next_node)
            current = next_node

        return None

    def _update_pheromone(self, all_paths):
        for key in self.pheromone:
            self.pheromone[key] *= (1 - self.evaporation)
            if self.pheromone[key] < 0.01:
                self.pheromone[key] = 0.01

        for path, dist in all_paths:
            if path and dist > 0:
                deposit = self.Q / dist
                for i in range(len(path) - 1):
                    a, b = path[i], path[i + 1]
                    current_ph = self._get_pheromone(a, b)
                    self._set_pheromone(a, b, current_ph + deposit)

    def find_path(self, start, end, danger_nodes=None):
        if danger_nodes is None:
            danger_nodes = set()

        best_path = None
        best_dist = float("inf")

        print(f"[ACO] Running: {start} -> {end}")
        print(f"[ACO] Fire zones: {danger_nodes}")
        print(f"[ACO] Ants: {self.num_ants}, Iterations: {self.num_iterations}")

        for iteration in range(self.num_iterations):
            iteration_paths = []

            for _ant in range(self.num_ants):
                path = self._ant_walk(start, end, danger_nodes)
                if path:
                    dist = self._path_distance(path)
                    iteration_paths.append((path, dist))

                    if dist < best_dist:
                        best_dist = dist
                        best_path = path

            self._update_pheromone(iteration_paths)

            if (iteration + 1) % 20 == 0:
                found = len(iteration_paths)
                print(
                    f"  Iteration {iteration + 1}/{self.num_iterations} | "
                    f"Ants found path: {found}/{self.num_ants} | "
                    f"Best dist: {best_dist:.1f}m"
                )

        if best_path:
            print(f"[ACO] Best path found! Distance: {best_dist:.1f}m")
            print(f"[ACO] Path: {' -> '.join(best_path)}")
        else:
            print("[ACO] No path found (all routes blocked?)")

        return best_path, best_dist
