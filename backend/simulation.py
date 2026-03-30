"""
simulation.py - Multi-Agent Evacuation Simulation
=================================================
Simulates multiple people evacuating from a building with dynamic routing.
"""

import random
import time
import heapq
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
import math


class Person:
    """Represents an evacuating person"""
    
    def __init__(self, person_id: int, start_room: str, position: Tuple[float, float] = None):
        self.id = person_id
        self.start_room = start_room
        self.current_node = start_room
        self.position = position or (0, 0)
        self.target_exit = None
        self.path = []
        self.path_index = 0
        self.distance_traveled = 0.0
        self.evacuated = False
        self.evacuation_time = None
        self.status = "waiting"  # waiting, moving, evacuated, blocked
    
    def move_to(self, node: str, distance: float, position: Tuple[float, float]):
        """Move person to next node"""
        self.current_node = node
        self.position = position
        self.distance_traveled += distance
        self.path_index += 1
    
    def complete_evacuation(self, exit_id: str):
        """Mark person as evacuated"""
        self.evacuated = True
        self.target_exit = exit_id
        self.status = "evacuated"
        self.evacuation_time = time.time()


class EvacuationSimulator:
    """Multi-agent evacuation simulation"""
    
    def __init__(self, layout: Dict, graph: Dict):
        self.layout = layout
        self.graph = graph
        self.people: List[Person] = []
        self.time_elapsed = 0.0
        self.congestion_map: Dict[str, float] = defaultdict(float)
        self.history: List[Dict] = []
        
    def add_people(self, rooms: List[str], capacity_per_room: int = None):
        """Add people to specified rooms"""
        person_id = len(self.people)
        
        for room_id in rooms:
            # Determine number of people in room
            if capacity_per_room:
                num_people = min(capacity_per_room, 10)  # Cap at 10 for simulation
            else:
                # Find room capacity from layout
                num_people = self._get_room_capacity(room_id)
            
            for i in range(num_people):
                person = Person(person_id, room_id)
                self.people.append(person)
                person_id += 1
        
        print(f"[Simulation] Added {len(self.people)} people to simulation")
    
    def _get_room_capacity(self, room_id: str) -> int:
        """Get room capacity from layout"""
        for room in self.layout.get("rooms", []):
            if room.get("id") == room_id:
                return min(room.get("capacity", 5), 10)  # Cap at 10 for simulation
        return 5
    
    def _find_exit(self, start: str, danger_nodes: Set[str] = None) -> Optional[str]:
        """Find nearest safe exit"""
        if danger_nodes is None:
            danger_nodes = set()
        
        exits = self.layout.get("exits", [])
        if not exits:
            return None
        
        best_exit = None
        best_dist = float("inf")
        
        for exit_info in exits:
            exit_id = exit_info.get("id")
            # Use Dijkstra to find distance
            dist = self._dijkstra_distance(start, exit_id, danger_nodes)
            if dist < best_dist:
                best_dist = dist
                best_exit = exit_id
        
        return best_exit
    
    def _dijkstra_distance(self, start: str, end: str, 
                          danger_nodes: Set[str] = None) -> float:
        """Find shortest path distance using Dijkstra"""
        if danger_nodes is None:
            danger_nodes = set()
        
        if start == end:
            return 0.0
        
        distances = {start: 0.0}
        queue = [(0.0, start)]
        visited = set()
        
        while queue:
            dist, node = heapq.heappop(queue)
            
            if node in visited:
                continue
            visited.add(node)
            
            if node == end:
                return dist
            
            for neighbor, edge_dist in self.graph.get(node, []):
                if neighbor in visited or neighbor in danger_nodes:
                    continue
                
                new_dist = dist + edge_dist
                if neighbor not in distances or new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(queue, (new_dist, neighbor))
        
        return float("inf")
    
    def _get_path_to_exit(self, start: str, exit_id: str, 
                          danger_nodes: Set[str] = None) -> Optional[List[str]]:
        """Get path from start to exit"""
        if danger_nodes is None:
            danger_nodes = set()
        
        # Simple BFS pathfinding
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            node, path = queue.pop(0)
            
            if node == exit_id:
                return path
            
            for neighbor, _ in self.graph.get(node, []):
                if neighbor in visited or neighbor in danger_nodes:
                    continue
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
        
        return None
    
    def initialize_paths(self, danger_nodes: Set[str] = None):
        """Initialize evacuation paths for all people"""
        if danger_nodes is None:
            danger_nodes = set()
        
        for person in self.people:
            exit_id = self._find_exit(person.current_node, danger_nodes)
            if exit_id:
                person.target_exit = exit_id
                path = self._get_path_to_exit(person.current_node, exit_id, danger_nodes)
                if path:
                    person.path = path
                    person.status = "ready"
                else:
                    person.status = "blocked"
            else:
                person.status = "blocked"
        
        blocked_count = sum(1 for p in self.people if p.status == "blocked")
        print(f"[Simulation] Paths initialized: {len(self.people) - blocked_count} ready, {blocked_count} blocked")
    
    def update_congestion(self):
        """Update congestion map based on current positions"""
        self.congestion_map.clear()
        
        for person in self.people:
            if not person.evacuated and person.current_node:
                self.congestion_map[person.current_node] += 1
        
        # Convert to weight (higher congestion = higher weight)
        max_congestion = max(self.congestion_map.values()) if self.congestion_map else 1
        if max_congestion > 0:
            for node in self.congestion_map:
                self.congestion_map[node] = self.congestion_map[node] / max_congestion
    
    def simulate_step(self, dt: float = 1.0, danger_nodes: Set[str] = None):
        """Simulate one time step"""
        if danger_nodes is None:
            danger_nodes = set()
        
        self.time_elapsed += dt
        self.update_congestion()
        
        evacuated_this_step = 0
        
        for person in self.people:
            if person.evacuated or person.status == "blocked":
                continue
            
            # Check if current path is still safe
            if person.path_index < len(person.path):
                current_target = person.path[person.path_index]
                if current_target in danger_nodes:
                    # Re-route
                    new_exit = self._find_exit(person.current_node, danger_nodes)
                    if new_exit:
                        new_path = self._get_path_to_exit(person.current_node, new_exit, danger_nodes)
                        if new_path:
                            person.path = new_path
                            person.path_index = 0
                            person.target_exit = new_exit
                        else:
                            person.status = "blocked"
                            continue
                    else:
                        person.status = "blocked"
                        continue
            
            # Move along path
            if person.path_index < len(person.path):
                target = person.path[person.path_index]
                
                # Calculate movement speed (slower in congested areas)
                congestion = self.congestion_map.get(target, 0)
                speed_factor = max(0.3, 1.0 - congestion * 0.5)  # Min 30% speed
                
                # Find distance to next node
                dist = self._get_distance(person.current_node, target)
                
                if dist <= 0:
                    # Already at target
                    person.move_to(target, 0, self._get_node_position(target))
                    if target == person.target_exit:
                        person.complete_evacuation(person.target_exit)
                        evacuated_this_step += 1
                else:
                    # Move towards target
                    move_dist = min(dt * 1.5 * speed_factor, dist)  # ~1.5 m/s walking speed
                    person.distance_traveled += move_dist
                    
                    if move_dist >= dist:
                        # Reached target
                        person.move_to(target, dist, self._get_node_position(target))
                        if target == person.target_exit:
                            person.complete_evacuation(person.target_exit)
                            evacuated_this_step += 1
        
        # Record history
        self.history.append({
            "time": self.time_elapsed,
            "evacuated": sum(1 for p in self.people if p.evacuated),
            "in_progress": sum(1 for p in self.people if not p.evacuated and p.status != "blocked"),
            "blocked": sum(1 for p in self.people if p.status == "blocked"),
            "congestion": dict(self.congestion_map)
        })
        
        return evacuated_this_step
    
    def _get_distance(self, node_a: str, node_b: str) -> float:
        """Get distance between two connected nodes"""
        for neighbor, dist in self.graph.get(node_a, []):
            if neighbor == node_b:
                return dist
        return 0.0
    
    def _get_node_position(self, node_id: str) -> Tuple[float, float]:
        """Get position of a node"""
        # Try waypoints
        for wp in self.layout.get("waypoints", []):
            if wp.get("id") == node_id:
                return (wp.get("x", 0), wp.get("y", 0))
        
        # Try exits
        for ex in self.layout.get("exits", []):
            if ex.get("id") == node_id:
                return (ex.get("x", 0) + ex.get("width", 0) / 2,
                        ex.get("y", 0) + ex.get("height", 0) / 2)
        
        return (0, 0)
    
    def run_simulation(self, max_time: float = 300.0,
                      danger_nodes: Set[str] = None,
                      dt: float = 1.0) -> Dict:
        """Run complete evacuation simulation"""
        if danger_nodes is None:
            danger_nodes = set()
        
        print(f"[Simulation] Starting simulation with {len(self.people)} people")
        print(f"[Simulation] Time limit: {max_time}s, Time step: {dt}s")
        
        self.time_elapsed = 0.0
        self.history = []
        
        self.initialize_paths(danger_nodes)
        
        step = 0
        while self.time_elapsed < max_time:
            evacuated = self.simulate_step(dt, danger_nodes)
            step += 1
            
            # Progress reporting
            if step % 10 == 0:
                total_evacuated = sum(1 for p in self.people if p.evacuated)
                print(f"  t={self.time_elapsed:.0f}s | Evacuated: {total_evacuated}/{len(self.people)}")
            
            # Check if all evacuated or blocked
            all_done = all(p.evacuated or p.status == "blocked" for p in self.people)
            if all_done:
                break
        
        return self.get_statistics()
    
    def get_statistics(self) -> Dict:
        """Get simulation statistics"""
        evacuated = [p for p in self.people if p.evacuated]
        blocked = [p for p in self.people if p.status == "blocked"]
        in_progress = [p for p in self.people if not p.evacuated and p.status != "blocked"]
        
        stats = {
            "total_people": len(self.people),
            "evacuated": len(evacuated),
            "blocked": len(blocked),
            "in_progress": len(in_progress),
            "evacuation_rate": len(evacuated) / len(self.people) if self.people else 0,
            "total_time": self.time_elapsed,
            "avg_evacuation_time": sum(p.evacuation_time for p in evacuated if p.evacuation_time) / len(evacuated) if evacuated else None,
            "max_evacuation_time": max((p.evacuation_time for p in evacuated if p.evacuation_time), default=0),
            "exit_usage": defaultdict(int),
            "history": self.history
        }
        
        # Count exit usage
        for person in evacuated:
            if person.target_exit:
                stats["exit_usage"][person.target_exit] += 1
        
        return stats


def run_demo_simulation(layout: Dict, graph: Dict,
                       rooms: List[str] = None,
                       danger_zones: List[str] = None) -> Dict:
    """Run a demo evacuation simulation"""
    simulator = EvacuationSimulator(layout, graph)
    
    if rooms is None:
        rooms = ["G01", "G02", "G07", "G11", "G13"]
    
    if danger_zones is None:
        danger_zones = []
    
    simulator.add_people(rooms)
    
    danger_nodes = set(danger_zones)
    
    print("=" * 50)
    print("EVACUATION SIMULATION RESULTS")
    print("=" * 50)
    
    results = simulator.run_simulation(danger_nodes=danger_nodes)
    
    print("\n--- Summary ---")
    print(f"Total People: {results['total_people']}")
    print(f"Evacuated: {results['evacuated']} ({results['evacuation_rate']*100:.1f}%)")
    print(f"Blocked: {results['blocked']}")
    print(f"Total Time: {results['total_time']:.1f}s")
    
    print("\n--- Exit Usage ---")
    for exit_id, count in results["exit_usage"].items():
        print(f"  {exit_id}: {count} people")
    
    return results


if __name__ == "__main__":
    import json
    
    # Load test layout
    try:
        with open("../data/building_layout.json", "r") as f:
            layout = json.load(f)
        
        # Build simple graph from edges
        graph = defaultdict(list)
        for edge in layout.get("graph_edges", []):
            if len(edge) >= 3:
                node_a, node_b, dist = edge[0], edge[1], edge[2]
                graph[node_a].append((node_b, dist))
                graph[node_b].append((node_a, dist))
        
        # Run simulation
        results = run_demo_simulation(
            layout, graph,
            rooms=["G01", "G02", "G03", "G07", "G11"],
            danger_zones=["C4A", "C5A"]
        )
        
    except FileNotFoundError:
        print("Layout file not found - run from backend directory")
