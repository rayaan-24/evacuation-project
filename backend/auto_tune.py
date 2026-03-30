"""
auto_tune.py - ACO Parameter Auto-Tuning Module
==============================================
Automatically tunes ACO parameters based on building characteristics.
"""

import json
import math
from typing import Dict, List, Tuple, Optional
from aco import ACO, ACOConfig, EnhancedACO, create_aco


class ACOAutoTuner:
    """Automatically tune ACO parameters"""
    
    def __init__(self, graph: Dict, layout: Dict):
        self.graph = graph
        self.layout = layout
        self.node_count = len(graph)
        self.building_info = layout.get("building", {})
        
    def get_building_complexity(self) -> str:
        """Determine building complexity based on node count"""
        if self.node_count < 30:
            return "small"
        elif self.node_count < 60:
            return "medium"
        else:
            return "large"
    
    def get_building_size(self) -> Tuple[float, float]:
        """Get building dimensions"""
        width = self.building_info.get("width", 100)
        height = self.building_info.get("height", 100)
        return width, height
    
    def calculate_building_area(self) -> float:
        """Calculate approximate building area"""
        width, height = self.get_building_size()
        return width * height
    
    def estimate_exit_count(self) -> int:
        """Count available exits"""
        return len(self.layout.get("exits", []))
    
    def estimate_room_count(self) -> int:
        """Count total rooms"""
        return len(self.layout.get("rooms", []))
    
    def get_tuning_recommendations(self) -> Dict:
        """Get parameter tuning recommendations"""
        complexity = self.get_building_complexity()
        node_count = self.node_count
        exit_count = self.estimate_exit_count()
        room_count = self.estimate_room_count()
        
        # Calculate base parameters
        recommendations = {
            "complexity": complexity,
            "node_count": node_count,
            "exit_count": exit_count,
            "room_count": room_count,
            "suggested_mode": "balanced",
            "parameters": {}
        }
        
        # Adjust based on complexity
        if complexity == "small":
            recommendations["suggested_mode"] = "fast"
            recommendations["parameters"] = {
                "num_ants": 15,
                "num_iterations": 30,
                "alpha": 1.0,
                "beta": 3.5,
                "evaporation": 0.6,
                "early_termination": True
            }
        elif complexity == "medium":
            recommendations["suggested_mode"] = "balanced"
            recommendations["parameters"] = {
                "num_ants": 30,
                "num_iterations": 80,
                "alpha": 1.0,
                "beta": 3.0,
                "evaporation": 0.5,
                "early_termination": True
            }
        else:  # large
            recommendations["suggested_mode"] = "thorough"
            recommendations["parameters"] = {
                "num_ants": 50,
                "num_iterations": 120,
                "alpha": 1.2,
                "beta": 2.5,
                "evaporation": 0.4,
                "early_termination": False
            }
        
        # Adjust based on exit density
        exit_density = exit_count / (node_count / 10) if node_count > 0 else 0.1
        if exit_density > 0.5:
            # Many exits - can be faster
            recommendations["parameters"]["num_ants"] *= 0.8
            recommendations["parameters"]["num_iterations"] *= 0.7
        
        # Adjust for graph density
        avg_connections = sum(len(neighbors) for neighbors in self.graph.values()) / node_count if node_count > 0 else 0
        if avg_connections < 2:
            # Sparse graph - needs more exploration
            recommendations["parameters"]["num_ants"] *= 1.3
            recommendations["parameters"]["beta"] *= 0.9
        
        return recommendations
    
    def create_optimized_aco(self, mode: str = None) -> EnhancedACO:
        """Create optimized ACO instance"""
        if mode is None:
            recommendations = self.get_tuning_recommendations()
            mode = recommendations["suggested_mode"]
        
        return create_aco(self.graph, mode=mode)
    
    def benchmark_modes(self) -> Dict:
        """Benchmark different ACO modes"""
        # Select sample start/end points
        exits = self.layout.get("exits", [])
        waypoints = self.layout.get("waypoints", [])
        
        if not exits or not waypoints:
            return {"error": "Insufficient data for benchmarking"}
        
        sample_start = waypoints[0].get("id") if waypoints else "J_NW"
        sample_end = exits[0].get("id") if exits else "E1"
        
        results = {}
        
        for mode in ["fast", "balanced", "thorough"]:
            print(f"\n[Benchmark] Testing {mode} mode...")
            
            aco = create_aco(self.graph, mode=mode)
            path, distance = aco.find_path(sample_start, sample_end, danger_nodes=set())
            
            stats = aco.get_statistics()
            
            results[mode] = {
                "path_found": path is not None,
                "distance": distance,
                "execution_time_ms": stats["execution_time_ms"],
                "iterations_completed": stats["iterations_completed"],
                "nodes_explored_estimate": len(path) if path else 0
            }
            
            print(f"  {mode}: {distance:.1f}m in {stats['execution_time_ms']:.1f}ms")
        
        # Determine best mode
        best_mode = min(results.keys(), 
                       key=lambda m: results[m]["execution_time_ms"])
        
        results["recommended_mode"] = best_mode
        results["recommended_config"] = self.get_tuning_recommendations()
        
        return results


def tune_for_building(layout_path: str = "data/building_layout.json") -> Dict:
    """Run auto-tuning for a building"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(layout_path) if os.path.dirname(layout_path) else ".")
    
    from pathfinder import load_layout, build_graph
    
    layout = load_layout(layout_path)
    graph = build_graph(layout)
    
    tuner = ACOAutoTuner(graph, layout)
    
    print("=" * 60)
    print("ACO AUTO-TUNING RESULTS")
    print("=" * 60)
    
    recommendations = tuner.get_tuning_recommendations()
    print(f"\nBuilding Complexity: {recommendations['complexity']}")
    print(f"Nodes: {recommendations['node_count']}")
    print(f"Exits: {recommendations['exit_count']}")
    print(f"Rooms: {recommendations['room_count']}")
    print(f"\nRecommended Mode: {recommendations['suggested_mode']}")
    print("\nParameters:")
    for key, value in recommendations["parameters"].items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 60)
    
    return recommendations


if __name__ == "__main__":
    import os
    
    # Try to find layout file
    possible_paths = [
        "../data/building_layout.json",
        "data/building_layout.json",
        "../data/building_layout.json",
        "building_layout.json"
    ]
    
    layout_path = None
    for path in possible_paths:
        if os.path.exists(path):
            layout_path = path
            break
    
    if layout_path:
        results = tune_for_building(layout_path)
    else:
        print("Layout file not found - testing with sample data")
        
        # Test with sample graph
        sample_graph = {
            "A": [("B", 1.0), ("C", 2.0)],
            "B": [("A", 1.0), ("D", 1.5), ("E", 2.0)],
            "C": [("A", 2.0), ("D", 1.0)],
            "D": [("B", 1.5), ("C", 1.0), ("E", 1.0)],
            "E": [("B", 2.0), ("D", 1.0), ("EXIT", 1.0)]
        }
        
        sample_layout = {
            "building": {"width": 10, "height": 10},
            "exits": [{"id": "EXIT"}],
            "rooms": [{"id": "R1"}, {"id": "R2"}],
            "waypoints": []
        }
        
        tuner = ACOAutoTuner(sample_graph, sample_layout)
        print("\nSample Graph Results:")
        print(json.dumps(tuner.get_tuning_recommendations(), indent=2))
