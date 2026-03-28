"""
pathfinder.py - Converts Building Layout to Graph & Generates Directions
=========================================================================
Reads the JSON building model, builds a graph, and returns a safe path.
"""

import json
import heapq
import math
from aco import ACO


def load_layout(filepath="data/building_layout.json"):
    """Load the building layout from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def iter_all_elements(layout):
    """Yield all drawable architectural elements in a consistent format."""
    for collection_name, element_type in (
        ("rooms", "room"),
        ("corridors", "corridor"),
        ("stairs", "stair"),
        ("lifts", "lift"),
        ("exits", "exit"),
    ):
        for item in layout.get(collection_name, []):
            merged = dict(item)
            merged["type"] = merged.get("type", element_type)
            yield merged


def find_element(layout, element_id):
    """Find an element by id across rooms, corridors, stairs, lifts, and exits."""
    for item in iter_all_elements(layout):
        if item.get("id") == element_id:
            return item
    return None


def element_center(element):
    """Return the center point of a rectangular element."""
    return (
        element["x"] + element.get("width", 0) / 2,
        element["y"] + element.get("height", 0) / 2,
    )


def point_to_rect_distance(px, py, rect):
    """Shortest Euclidean distance from a point to an axis-aligned rectangle."""
    x1 = rect["x"]
    y1 = rect["y"]
    x2 = rect["x"] + rect.get("width", 0)
    y2 = rect["y"] + rect.get("height", 0)
    dx = max(x1 - px, 0, px - x2)
    dy = max(y1 - py, 0, py - y2)
    return math.sqrt(dx * dx + dy * dy)


def build_graph(layout):
    """
    Convert the JSON layout into an adjacency list for ACO.
    """
    graph = {}

    for wp in layout["waypoints"]:
        graph[wp["id"]] = []
    for ex in layout["exits"]:
        graph[ex["id"]] = []

    for node_a, node_b, dist in layout["graph_edges"]:
        graph.setdefault(node_a, []).append((node_b, dist))
        graph.setdefault(node_b, []).append((node_a, dist))

    meters_per_unit = layout.get("building", {}).get("meters_per_unit", 1.0)

    # Connect exits to the nearest waypoint when the JSON omits the final link.
    for ex in layout["exits"]:
        exit_id = ex["id"]
        if graph.get(exit_id):
            continue

        exit_center_x = ex["x"] + ex.get("width", 0) / 2
        exit_center_y = ex["y"] + ex.get("height", 0) / 2
        nearest_wp = None
        nearest_dist_px = float("inf")

        for wp in layout["waypoints"]:
            dx = wp["x"] - exit_center_x
            dy = wp["y"] - exit_center_y
            dist_px = math.sqrt(dx * dx + dy * dy)
            if dist_px < nearest_dist_px:
                nearest_dist_px = dist_px
                nearest_wp = wp["id"]

        if nearest_wp:
            dist_m = round(nearest_dist_px * meters_per_unit, 1)
            graph[exit_id].append((nearest_wp, dist_m))
            graph.setdefault(nearest_wp, []).append((exit_id, dist_m))

    return graph


def get_room_connection_waypoint(layout, room_id):
    """Return the architecturally assigned waypoint for a room door if available."""
    room_connections = layout.get("connections", {}).get("room_to_corridor", [])
    for connection in room_connections:
        if connection.get("room_id") == room_id:
            return connection.get("waypoint_id")
    return None


def get_corridor_waypoints(layout, corridor_id):
    """Return corridor junction and door waypoints attached to a corridor."""
    waypoint_ids = set()

    for connection in layout.get("connections", {}).get("room_to_corridor", []):
        if connection.get("corridor_id") == corridor_id:
            waypoint_ids.add(connection.get("waypoint_id"))

    for connection in layout.get("connections", {}).get("corridor_to_corridor", []):
        if connection.get("from") == corridor_id or connection.get("to") == corridor_id:
            waypoint_ids.add(connection.get("waypoint_id"))

    for connection in layout.get("connections", {}).get("corridor_to_vertical_egress", []):
        if connection.get("corridor_id") == corridor_id:
            waypoint_ids.add(connection.get("waypoint_id"))

    return {wp_id for wp_id in waypoint_ids if wp_id}


def fire_sources_to_hazards(layout, fire_sources):
    """
    Convert room/corridor fire sources into blocked elements, hazard zones, and blocked waypoints.
    """
    radius_m = layout.get("fire_safety", {}).get("hazard_radius_m", 3)
    blocked_elements = set()
    blocked_waypoints = set()
    hazard_zones = []

    for source_id in fire_sources:
        element = find_element(layout, source_id)
        if not element:
            continue

        source_type = element.get("type")
        blocked_elements.add(source_id)
        center_x, center_y = element_center(element)

        hazard_zones.append({
            "id": f"HZ_{source_id}",
            "source_id": source_id,
            "x": max(0, center_x - radius_m),
            "y": max(0, center_y - radius_m),
            "width": radius_m * 2,
            "height": radius_m * 2,
            "radius_m": radius_m,
            "type": "hazard_zone",
        })

        if source_type == "room":
            room_wp = get_room_connection_waypoint(layout, source_id)
            if room_wp:
                blocked_waypoints.add(room_wp)

        if source_type == "corridor":
            blocked_waypoints.update(get_corridor_waypoints(layout, source_id))

        for item in iter_all_elements(layout):
            if item.get("id") == source_id:
                continue
            if item.get("type") not in {"room", "corridor"}:
                continue
            if source_type == "corridor" and item.get("type") == "corridor":
                continue
            if point_to_rect_distance(center_x, center_y, item) <= radius_m:
                blocked_elements.add(item["id"])
                if item.get("type") == "room":
                    room_wp = get_room_connection_waypoint(layout, item["id"])
                    if room_wp:
                        blocked_waypoints.add(room_wp)
                if item.get("type") == "corridor":
                    blocked_waypoints.update(get_corridor_waypoints(layout, item["id"]))

        for wp in layout.get("waypoints", []):
            wp_dist = math.sqrt((wp["x"] - center_x) ** 2 + (wp["y"] - center_y) ** 2)
            if wp_dist <= radius_m:
                blocked_waypoints.add(wp["id"])

    return {
        "blocked_elements": sorted(blocked_elements),
        "blocked_waypoints": blocked_waypoints,
        "hazard_zones": hazard_zones,
    }


def get_waypoint_coords(layout, node_id):
    """Get the x,y coordinates of a waypoint or exit."""
    for wp in layout["waypoints"]:
        if wp["id"] == node_id:
            return wp["x"], wp["y"]
    for ex in layout["exits"]:
        if ex["id"] == node_id:
            return ex["x"] + ex.get("width", 0) / 2, ex["y"] + ex.get("height", 0) / 2
    return None, None


def get_waypoint_label(layout, node_id):
    """Get the human-readable label of a waypoint or exit."""
    for wp in layout["waypoints"]:
        if wp["id"] == node_id:
            return wp.get("label", node_id)
    for ex in layout["exits"]:
        if ex["id"] == node_id:
            return ex.get("name", node_id)
    return node_id


def room_to_waypoints(layout, room_id):
    """
    Map a room to its nearest waypoint based on room-center distance.
    """
    explicit_waypoint = get_room_connection_waypoint(layout, room_id)
    if explicit_waypoint:
        return explicit_waypoint

    room = next((r for r in layout["rooms"] if r["id"] == room_id), None)
    if not room:
        return None

    room_center_x = room["x"] + room["width"] / 2
    room_center_y = room["y"] + room["height"] / 2
    best_waypoint = None
    best_distance = float("inf")

    for wp in layout["waypoints"]:
        dx = wp["x"] - room_center_x
        dy = wp["y"] - room_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < best_distance:
            best_distance = distance
            best_waypoint = wp["id"]

    return best_waypoint


def find_nearest_exit(layout, graph, start_wp, danger_nodes):
    """
    Try each exit and return the shortest safe path.
    """
    best_path = None
    best_dist = float("inf")
    best_exit = None

    for exit_point in layout["exits"]:
        exit_id = exit_point["id"]
        aco = ACO(
            graph,
            num_ants=20,
            num_iterations=60,
            alpha=1.0,
            beta=3.0,
            evaporation=0.5,
            Q=100,
        )
        path, dist = aco.find_path(start_wp, exit_id, danger_nodes)
        if not path:
            path, dist = shortest_safe_path(graph, start_wp, exit_id, danger_nodes)

        if path and dist < best_dist:
            best_dist = dist
            best_path = path
            best_exit = exit_id

    return best_path, best_dist, best_exit


def shortest_safe_path(graph, start, end, danger_nodes):
    """Deterministic fallback when the ant search gets trapped in dead-end branches."""
    if start in danger_nodes or end in danger_nodes:
      return None, float("inf")

    queue = [(0.0, start, [start])]
    best_dist = {start: 0.0}

    while queue:
        dist_so_far, node, path = heapq.heappop(queue)
        if node == end:
            return path, dist_so_far
        if dist_so_far > best_dist.get(node, float("inf")):
            continue

        for neighbor, edge_dist in graph.get(node, []):
            if neighbor in danger_nodes:
                continue
            new_dist = dist_so_far + edge_dist
            if new_dist < best_dist.get(neighbor, float("inf")):
                best_dist[neighbor] = new_dist
                heapq.heappush(queue, (new_dist, neighbor, path + [neighbor]))

    return None, float("inf")


def generate_directions(path, layout):
    """
    Convert node IDs into human-readable directions.
    """
    directions = []
    meters_per_unit = layout.get("building", {}).get("meters_per_unit", 1.0)

    for i in range(len(path) - 1):
        curr = path[i]
        next_n = path[i + 1]

        cx, cy = get_waypoint_coords(layout, curr)
        nx, ny = get_waypoint_coords(layout, next_n)
        if cx is None or nx is None:
            continue

        dist_m = round(math.sqrt((nx - cx) ** 2 + (ny - cy) ** 2) * meters_per_unit, 1)
        dx = nx - cx
        dy = ny - cy

        if abs(dx) > abs(dy):
            direction = "East (->)" if dx > 0 else "West (<-)"
        else:
            direction = "South (v)" if dy > 0 else "North (^)"

        curr_label = get_waypoint_label(layout, curr)
        next_label = get_waypoint_label(layout, next_n)

        if next_n.startswith("E"):
            step = f"Walk {dist_m}m {direction} -> EVACUATE through {next_label}!"
        elif "Stair" in next_label:
            step = f"Walk {dist_m}m {direction} -> Take {next_label} down to ground floor"
        else:
            step = f"Walk {dist_m}m {direction} -> {next_label}"

        directions.append(
            {
                "step": i + 1,
                "instruction": step,
                "from": curr_label,
                "to": next_label,
                "distance_m": dist_m,
                "direction": direction,
            }
        )

    return directions


def run_pathfinder(start_room, fire_rooms, layout_path="data/building_layout.json"):
    """
    Main function called by the Flask API.
    """
    layout = load_layout(layout_path)
    graph = build_graph(layout)

    start_wp = room_to_waypoints(layout, start_room)
    if not start_wp:
        return {"error": f"Invalid start room: {start_room}"}

    hazard_info = fire_sources_to_hazards(layout, fire_rooms)
    danger_nodes = set(hazard_info["blocked_waypoints"])

    print(f"\n{'=' * 50}")
    print(f"PATHFINDER: {start_room} -> Nearest Exit")
    print(f"Fire zones: {fire_rooms}")
    print(f"Danger waypoints: {danger_nodes}")
    print(f"{'=' * 50}")

    if start_room in hazard_info["blocked_elements"] or start_wp in danger_nodes:
        return {
            "success": False,
            "error": "The selected start room is inside a blocked fire zone.",
            "start_room": start_room,
            "fire_rooms": fire_rooms,
            "blocked_elements": hazard_info["blocked_elements"],
            "hazard_zones": hazard_info["hazard_zones"],
        }

    best_path, best_dist, best_exit = find_nearest_exit(layout, graph, start_wp, danger_nodes)

    if not best_path:
        return {
            "success": False,
            "error": "No safe path found from the selected room to any exit.",
            "start_room": start_room,
            "fire_rooms": fire_rooms,
            "blocked_elements": hazard_info["blocked_elements"],
            "hazard_zones": hazard_info["hazard_zones"],
            }

    directions = generate_directions(best_path, layout)

    path_coords = []
    for node_id in best_path:
        x, y = get_waypoint_coords(layout, node_id)
        if x is not None:
            path_coords.append({"id": node_id, "x": x, "y": y})

    return {
        "success": True,
        "start_room": start_room,
        "fire_rooms": fire_rooms,
        "best_exit": best_exit,
        "path_nodes": best_path,
        "path_coords": path_coords,
        "total_distance_m": round(best_dist, 1),
        "danger_nodes": list(danger_nodes),
        "blocked_elements": hazard_info["blocked_elements"],
        "hazard_zones": hazard_info["hazard_zones"],
        "directions": directions,
        "total_steps": len(directions),
    }


if __name__ == "__main__":
    result = run_pathfinder("G07", ["G17"])
    print("\nRESULT:")
    print(f"Start: {result['start_room']}")
    print(f"Exit: {result.get('best_exit')}")
    print(f"Distance: {result.get('total_distance_m')}m")
    print("\nDIRECTIONS:")
    for d in result.get("directions", []):
        print(f"  Step {d['step']}: {d['instruction']}")
