"""
astar.py - A* Pathfinding Algorithm
====================================
Fast pathfinding with heuristic guidance.
Used as fallback when ACO is too slow or as primary algorithm for simple cases.
"""

import heapq
import math
from typing import Dict, List, Tuple, Set, Optional, Callable


class AStar:
    """A* Pathfinding Algorithm with multiple heuristics"""
    
    def __init__(self, graph: Dict, heuristic: str = "euclidean"):
        self.graph = graph
        self.heuristic_name = heuristic
        self.stats = {
            "nodes_explored": 0,
            "max_open_set_size": 0,
            "path_length": 0
        }
    
    def heuristic_euclidean(self, node_id: str, target_id: str,
                           node_coords: Dict[str, Tuple[float, float]],
                           target_coords: Dict[str, Tuple[float, float]]) -> float:
        """Euclidean distance heuristic"""
        if node_id in node_coords and target_id in target_coords:
            nx, ny = node_coords[node_id]
            tx, ty = target_coords[target_id]
            return math.sqrt((tx - nx) ** 2 + (ty - ny) ** 2)
        return 0.0
    
    def heuristic_manhattan(self, node_id: str, target_id: str,
                           node_coords: Dict[str, Tuple[float, float]],
                           target_coords: Dict[str, Tuple[float, float]]) -> float:
        """Manhattan distance heuristic"""
        if node_id in node_coords and target_id in target_coords:
            nx, ny = node_coords[node_id]
            tx, ty = target_coords[target_id]
            return abs(tx - nx) + abs(ty - ny)
        return 0.0
    
    def heuristic_zero(self, node_id: str, target_id: str, **kwargs) -> float:
        """Zero heuristic (equivalent to Dijkstra)"""
        return 0.0
    
    def get_heuristic(self, name: str) -> Callable:
        """Get heuristic function by name"""
        heuristics = {
            "euclidean": self.heuristic_euclidean,
            "manhattan": self.heuristic_manhattan,
            "zero": self.heuristic_zero,
            "dijkstra": self.heuristic_zero
        }
        return heuristics.get(name, self.heuristic_euclidean)
    
    def find_path(self, start: str, end: str,
                  danger_nodes: Set[str] = None,
                  node_coords: Dict[str, Tuple[float, float]] = None,
                  weights: Dict[str, float] = None) -> Tuple[Optional[List[str]], float]:
        """Find shortest path using A* algorithm"""
        if danger_nodes is None:
            danger_nodes = set()
        
        if start in danger_nodes or end in danger_nodes:
            return None, float("inf")
        
        if start not in self.graph or end not in self.graph:
            return None, float("inf")
        
        heuristic = self.get_heuristic(self.heuristic_name)
        
        # Priority queue: (f_score, g_score, node, path)
        open_set = [(0.0, 0.0, start, [start])]
        closed_set = set()
        g_scores = {start: 0.0}
        
        self.stats["nodes_explored"] = 0
        self.stats["max_open_set_size"] = 0
        
        while open_set:
            # Track max open set size
            self.stats["max_open_set_size"] = max(
                self.stats["max_open_set_size"], 
                len(open_set)
            )
            
            # Get node with lowest f_score
            f_score, g_score, current, path = heapq.heappop(open_set)
            
            if current == end:
                self.stats["path_length"] = len(path)
                print(f"[A*] Path found: {len(path)} nodes, distance: {g_score:.1f}m")
                return path, g_score
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            self.stats["nodes_explored"] += 1
            
            # Explore neighbors
            for neighbor, dist in self.graph.get(current, []):
                if neighbor in danger_nodes or neighbor in closed_set:
                    continue
                
                # Apply weights for congestion
                weight_multiplier = 1.0
                if weights and neighbor in weights:
                    weight_multiplier = 1.0 + weights[neighbor]
                
                adjusted_dist = dist * weight_multiplier
                tentative_g = g_score + adjusted_dist
                
                if neighbor not in g_scores or tentative_g < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g
                    
                    # Calculate f_score with heuristic
                    h_score = heuristic(neighbor, end, 
                                      node_coords or {}, 
                                      node_coords or {})
                    
                    f = tentative_g + h_score
                    
                    heapq.heappush(open_set, (f, tentative_g, neighbor, path + [neighbor]))
        
        print(f"[A*] No path found from {start} to {end}")
        return None, float("inf")
    
    def get_statistics(self) -> Dict:
        """Get algorithm statistics"""
        return self.stats.copy()


def astar_find_path(graph: Dict, start: str, end: str,
                    danger_nodes: Set[str] = None,
                    node_coords: Dict[str, Tuple[float, float]] = None,
                    weights: Dict[str, float] = None,
                    heuristic: str = "euclidean") -> Tuple[Optional[List[str]], float]:
    """Convenience function for A* pathfinding"""
    astar = AStar(graph, heuristic)
    return astar.find_path(start, end, danger_nodes, node_coords, weights)


if __name__ == "__main__":
    # Test with sample graph
    test_graph = {
        "A": [("B", 1.0), ("C", 2.0)],
        "B": [("A", 1.0), ("D", 1.5), ("E", 2.0)],
        "C": [("A", 2.0), ("D", 1.0)],
        "D": [("B", 1.5), ("C", 1.0), ("E", 1.0)],
        "E": [("B", 2.0), ("D", 1.0)]
    }
    
    # Test coordinates
    coords = {
        "A": (0, 0),
        "B": (1, 0),
        "C": (0, 2),
        "D": (1, 1),
        "E": (2, 1)
    }
    
    print("Testing A* Algorithm:")
    
    for heuristic in ["euclidean", "manhattan", "dijkstra"]:
        print(f"\n  Heuristic: {heuristic}")
        path, dist = astar_find_path(test_graph, "A", "E", 
                                     node_coords=coords,
                                     heuristic=heuristic)
        print(f"  Result: {' -> '.join(path)}, Distance: {dist:.1f}m")
