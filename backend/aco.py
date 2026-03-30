"""
aco.py - Enhanced Ant Colony Optimization Algorithm
====================================================
Features:
- Auto-tuning based on building complexity
- Adaptive pheromone evaporation
- Multiple algorithm modes (fast, balanced, thorough)
- Enhanced pheromone deposit strategies
- Early termination for faster convergence
"""

import random
import math
import time
from typing import List, Tuple, Dict, Set, Optional


class ACOConfig:
    """ACO Configuration with auto-tuning capabilities"""
    
    # Preset configurations
    PRESETS = {
        "fast": {
            "num_ants": 15,
            "num_iterations": 30,
            "alpha": 1.0,
            "beta": 3.0,
            "evaporation": 0.6,
            "Q": 80,
            "early_termination": True,
            "early_termination_threshold": 0.1
        },
        "balanced": {
            "num_ants": 30,
            "num_iterations": 100,
            "alpha": 1.0,
            "beta": 3.0,
            "evaporation": 0.5,
            "Q": 100,
            "early_termination": True,
            "early_termination_threshold": 0.05
        },
        "thorough": {
            "num_ants": 50,
            "num_iterations": 150,
            "alpha": 1.2,
            "beta": 2.5,
            "evaporation": 0.4,
            "Q": 120,
            "early_termination": False,
            "early_termination_threshold": 0.0
        }
    }
    
    def __init__(self, graph: Dict, mode: str = "balanced", 
                 num_ants: int = None, num_iterations: int = None,
                 alpha: float = None, beta: float = None,
                 evaporation: float = None, Q: float = None,
                 early_termination: bool = None, 
                 early_termination_threshold: float = None):
        self.graph = graph
        
        # Use preset or custom values
        preset = self.PRESETS.get(mode, self.PRESETS["balanced"])
        
        self.num_ants = num_ants if num_ants is not None else preset["num_ants"]
        self.num_iterations = num_iterations if num_iterations is not None else preset["num_iterations"]
        self.alpha = alpha if alpha is not None else preset["alpha"]
        self.beta = beta if beta is not None else preset["beta"]
        self.evaporation = evaporation if evaporation is not None else preset["evaporation"]
        self.Q = Q if Q is not None else preset["Q"]
        self.early_termination = early_termination if early_termination is not None else preset["early_termination"]
        self.early_termination_threshold = early_termination_threshold if early_termination_threshold is not None else preset["early_termination_threshold"]
        
        # Initialize pheromone trails
        self.pheromone = {}
        for node in graph:
            for neighbor, _dist in graph[node]:
                self.pheromone[(node, neighbor)] = 1.0
                self.pheromone[(neighbor, node)] = 1.0
        
        # Statistics
        self.stats = {
            "iterations_completed": 0,
            "best_distance": float("inf"),
            "convergence_history": [],
            "execution_time_ms": 0
        }
    
    @classmethod
    def auto_config(cls, graph: Dict, building_size: str = "medium") -> "ACOConfig":
        """Auto-configure ACO based on building size"""
        size_map = {
            "small": "fast",      # < 30 nodes
            "medium": "balanced",  # 30-60 nodes
            "large": "thorough"    # > 60 nodes
        }
        mode = size_map.get(building_size, "balanced")
        return cls(graph, mode=mode)
    
    @classmethod
    def adaptive_config(cls, graph: Dict, node_count: int = None) -> "ACOConfig":
        """Auto-configure based on graph complexity"""
        if node_count is None:
            node_count = len(graph)
        
        if node_count < 30:
            return cls(graph, mode="fast")
        elif node_count < 60:
            return cls(graph, mode="balanced")
        else:
            return cls(graph, mode="thorough")


class EnhancedACO:
    """Enhanced ACO with adaptive features"""
    
    def __init__(self, graph: Dict, config: ACOConfig = None, **kwargs):
        if config is None:
            config = ACOConfig(graph, **kwargs)
        
        self.config = config
        self.graph = graph
        self.pheromone = config.pheromone
        self.stats = config.stats
    
    def _get_pheromone(self, a: str, b: str) -> float:
        """Get pheromone level between two nodes"""
        return self.pheromone.get((a, b), self.pheromone.get((b, a), 1.0))
    
    def _set_pheromone(self, a: str, b: str, value: float):
        """Set pheromone level between two nodes"""
        self.pheromone[(a, b)] = value
        self.pheromone[(b, a)] = value
    
    def _heuristic(self, dist: float) -> float:
        """Calculate heuristic desirability"""
        return 1.0 / (dist + 0.1)
    
    def _choose_next(self, current: str, visited: Set[str], 
                     danger_nodes: Set[str], weights: Dict[str, float] = None) -> Optional[str]:
        """Choose next node using probabilistic selection"""
        neighbors = self.graph.get(current, [])
        if not neighbors:
            return None
        
        choices = []
        weights_list = []
        
        for neighbor, dist in neighbors:
            if neighbor in visited:
                continue
            if neighbor in danger_nodes:
                continue
            
            pheromone = self._get_pheromone(current, neighbor)
            heuristic = self._heuristic(dist)
            
            # Apply weights for congestion/crowding
            weight_multiplier = 1.0
            if weights and neighbor in weights:
                weight_multiplier = 1.0 / (1.0 + weights[neighbor])
            
            combined_weight = (
                (pheromone ** self.config.alpha) * 
                (heuristic ** self.config.beta) * 
                weight_multiplier
            )
            
            choices.append(neighbor)
            weights_list.append(combined_weight)
        
        if not choices:
            return None
        
        # Probabilistic selection
        total = sum(weights_list)
        if total == 0:
            return random.choice(choices)
        
        r = random.uniform(0, total)
        cumulative = 0
        for node, weight in zip(choices, weights_list):
            cumulative += weight
            if r <= cumulative:
                return node
        
        return choices[-1]
    
    def _path_distance(self, path: List[str]) -> float:
        """Calculate total distance of a path"""
        total = 0
        for i in range(len(path) - 1):
            node_a = path[i]
            node_b = path[i + 1]
            for neighbor, dist in self.graph.get(node_a, []):
                if neighbor == node_b:
                    total += dist
                    break
        return total
    
    def _ant_walk(self, start: str, end: str, danger_nodes: Set[str],
                  weights: Dict[str, float] = None) -> Optional[List[str]]:
        """Simulate single ant's path exploration"""
        if start in danger_nodes or end in danger_nodes:
            return None
        
        path = [start]
        visited = {start}
        current = start
        max_steps = len(self.graph) * 3
        
        for _ in range(max_steps):
            if current == end:
                return path
            
            next_node = self._choose_next(current, visited, danger_nodes, weights)
            if next_node is None:
                return None
            
            path.append(next_node)
            visited.add(next_node)
            current = next_node
        
        return None
    
    def _update_pheromone(self, all_paths: List[Tuple[List[str], float]]):
        """Update pheromone trails based on found paths"""
        evaporation = self.config.evaporation
        
        # Evaporate pheromones
        for key in list(self.pheromone.keys()):
            self.pheromone[key] *= (1 - evaporation)
            if self.pheromone[key] < 0.01:
                self.pheromone[key] = 0.01
        
        # Deposit pheromones on successful paths
        for path, dist in all_paths:
            if path and dist > 0:
                deposit = self.config.Q / dist
                
                # Apply elitist reinforcement for best paths
                if dist == self.stats["best_distance"]:
                    deposit *= 1.5
                
                for i in range(len(path) - 1):
                    a, b = path[i], path[i + 1]
                    current_ph = self._get_pheromone(a, b)
                    self._set_pheromone(a, b, current_ph + deposit)
    
    def find_path(self, start: str, end: str, 
                  danger_nodes: Set[str] = None,
                  weights: Dict[str, float] = None) -> Tuple[Optional[List[str]], float]:
        """Find best path using ACO"""
        if danger_nodes is None:
            danger_nodes = set()
        
        start_time = time.time()
        
        best_path = None
        best_dist = float("inf")
        no_improvement_count = 0
        
        print(f"[Enhanced ACO] Running: {start} -> {end}")
        print(f"[Enhanced ACO] Mode: balanced | Ants: {self.config.num_ants} | Iterations: {self.config.num_iterations}")
        print(f"[Enhanced ACO] Fire zones: {danger_nodes}")
        
        for iteration in range(self.config.num_iterations):
            iteration_paths = []
            
            for _ant in range(self.config.num_ants):
                path = self._ant_walk(start, end, danger_nodes, weights)
                if path:
                    dist = self._path_distance(path)
                    iteration_paths.append((path, dist))
                    
                    if dist < best_dist:
                        best_dist = dist
                        best_path = path
                        no_improvement_count = 0
            
            self._update_pheromone(iteration_paths)
            self.stats["iterations_completed"] = iteration + 1
            self.stats["convergence_history"].append(best_dist)
            
            # Early termination check
            if self.config.early_termination and no_improvement_count >= 10:
                improvement = (iteration_paths[0][1] if iteration_paths else float("inf") - best_dist)
                if best_dist > 0 and improvement / best_dist < self.config.early_termination_threshold:
                    print(f"[Enhanced ACO] Early termination at iteration {iteration + 1}")
                    break
            
            no_improvement_count += 1
            
            # Progress reporting
            if (iteration + 1) % 20 == 0:
                found = len(iteration_paths)
                print(f"  Iteration {iteration + 1}/{self.config.num_iterations} | "
                      f"Found: {found}/{self.config.num_ants} | "
                      f"Best: {best_dist:.1f}m | "
                      f"No improvement: {no_improvement_count}")
        
        self.stats["execution_time_ms"] = (time.time() - start_time) * 1000
        self.stats["best_distance"] = best_dist
        
        if best_path:
            print(f"[Enhanced ACO] Best path: {best_dist:.1f}m | "
                  f"Time: {self.stats['execution_time_ms']:.1f}ms | "
                  f"Path: {' -> '.join(best_path)}")
        else:
            print("[Enhanced ACO] No path found")
        
        return best_path, best_dist
    
    def get_statistics(self) -> Dict:
        """Get ACO execution statistics"""
        return self.stats.copy()


# Backwards compatibility
class ACO(EnhancedACO):
    """Legacy ACO class - uses balanced preset by default"""
    
    def __init__(self, graph: Dict, num_ants: int = 30, num_iterations: int = 100,
                 alpha: float = 1.0, beta: float = 3.0, 
                 evaporation: float = 0.5, Q: float = 100):
        super().__init__(
            graph, 
            ACOConfig(
                graph,
                num_ants=num_ants,
                num_iterations=num_iterations,
                alpha=alpha,
                beta=beta,
                evaporation=evaporation,
                Q=Q
            )
        )


def create_aco(graph: Dict, mode: str = "balanced", 
               building_size: str = None) -> EnhancedACO:
    """Factory function to create ACO instance"""
    if building_size:
        config = ACOConfig.auto_config(graph, building_size)
    else:
        config = ACOConfig(graph, mode=mode)
    
    return EnhancedACO(graph, config)


if __name__ == "__main__":
    # Test with sample graph
    test_graph = {
        "A": [("B", 1.0), ("C", 2.0)],
        "B": [("A", 1.0), ("D", 1.5)],
        "C": [("A", 2.0), ("D", 1.0)],
        "D": [("B", 1.5), ("C", 1.0), ("E", 1.0)],
        "E": [("D", 1.0)]
    }
    
    print("Testing Enhanced ACO:")
    aco = create_aco(test_graph, mode="balanced")
    path, dist = aco.find_path("A", "E")
    
    print(f"\nResult: {path}, Distance: {dist}")
    print(f"Statistics: {aco.get_statistics()}")
