"""
pathfinder.py - Multi-emergency dynamic pathfinding with ACO + fallback shortest path
"""

import heapq
import json
import math
from aco import ACO

SUPPORTED_TYPES = {"FIRE", "SMOKE", "BLOCKAGE", "CROWD", "GAS"}
DEFAULT_EMERGENCY_RULES = {
    "FIRE": {"block": True, "radius": 2},
    "SMOKE": {"block": False, "weight": 5},
    "BLOCKAGE": {"block": True},
    "CROWD": {"block": False, "weight": 3},
    "GAS": {"block": True, "radius": 3},
}


def load_layout(filepath="data/building_layout.json"):
    with open(filepath, "r", encoding="utf-8") as file_obj:
        return json.load(file_obj)


def iter_all_elements(layout):
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
    for item in iter_all_elements(layout):
        if item.get("id") == element_id:
            return item
    return None


def element_center(element):
    return (
        element["x"] + element.get("width", 0) / 2,
        element["y"] + element.get("height", 0) / 2,
    )


def point_to_rect_distance(px, py, rect):
    x1 = rect["x"]
    y1 = rect["y"]
    x2 = rect["x"] + rect.get("width", 0)
    y2 = rect["y"] + rect.get("height", 0)
    dx = max(x1 - px, 0, px - x2)
    dy = max(y1 - py, 0, py - y2)
    return math.sqrt(dx * dx + dy * dy)


def point_in_rect(px, py, rect):
    return (
        rect["x"] <= px <= rect["x"] + rect.get("width", 0)
        and rect["y"] <= py <= rect["y"] + rect.get("height", 0)
    )


def _orientation(ax, ay, bx, by, cx, cy):
    value = (by - ay) * (cx - bx) - (bx - ax) * (cy - by)
    if abs(value) < 1e-9:
        return 0
    return 1 if value > 0 else 2


def _on_segment(ax, ay, bx, by, cx, cy):
    return min(ax, cx) <= bx <= max(ax, cx) and min(ay, cy) <= by <= max(ay, cy)


def segments_intersect(ax, ay, bx, by, cx, cy, dx, dy):
    o1 = _orientation(ax, ay, bx, by, cx, cy)
    o2 = _orientation(ax, ay, bx, by, dx, dy)
    o3 = _orientation(cx, cy, dx, dy, ax, ay)
    o4 = _orientation(cx, cy, dx, dy, bx, by)

    if o1 != o2 and o3 != o4:
        return True
    if o1 == 0 and _on_segment(ax, ay, cx, cy, bx, by):
        return True
    if o2 == 0 and _on_segment(ax, ay, dx, dy, bx, by):
        return True
    if o3 == 0 and _on_segment(cx, cy, ax, ay, dx, dy):
        return True
    if o4 == 0 and _on_segment(cx, cy, bx, by, dx, dy):
        return True
    return False


def segment_intersects_rect(ax, ay, bx, by, rect):
    x1 = rect["x"]
    y1 = rect["y"]
    x2 = rect["x"] + rect.get("width", 0)
    y2 = rect["y"] + rect.get("height", 0)

    if point_in_rect(ax, ay, rect) or point_in_rect(bx, by, rect):
        return True

    return any(
        segments_intersect(ax, ay, bx, by, sx1, sy1, sx2, sy2)
        for sx1, sy1, sx2, sy2 in (
            (x1, y1, x2, y1),
            (x2, y1, x2, y2),
            (x2, y2, x1, y2),
            (x1, y2, x1, y1),
        )
    )


def build_graph(layout):
    graph = {}

    def add_edge(node_a, node_b, dist):
        neighbors_a = graph.setdefault(node_a, [])
        neighbors_b = graph.setdefault(node_b, [])

        if not any(existing_id == node_b for existing_id, _ in neighbors_a):
            neighbors_a.append((node_b, dist))
        if not any(existing_id == node_a for existing_id, _ in neighbors_b):
            neighbors_b.append((node_a, dist))

    for wp in layout["waypoints"]:
        graph[wp["id"]] = []
    for ex in layout["exits"]:
        graph[ex["id"]] = []

    for node_a, node_b, dist in layout["graph_edges"]:
        add_edge(node_a, node_b, dist)

    meters_per_unit = layout.get("building", {}).get("meters_per_unit", 1.0)
    room_waypoint_ids = {
        connection.get("waypoint_id")
        for connection in layout.get("connections", {}).get("room_to_corridor", [])
        if connection.get("waypoint_id")
    }

    corridor_lookup = {corridor["id"]: corridor for corridor in layout.get("corridors", [])}

    for connection in layout.get("connections", {}).get("room_to_corridor", []):
        room_wp = connection.get("waypoint_id")
        corridor = corridor_lookup.get(connection.get("corridor_id"))
        if not room_wp or not corridor or room_wp not in graph:
            continue

        room_x, room_y = get_waypoint_coords(layout, room_wp)
        if room_x is None:
            continue

        for waypoint in layout.get("waypoints", []):
            target_id = waypoint["id"]
            if target_id == room_wp or target_id in room_waypoint_ids:
                continue
            if not point_in_rect(waypoint["x"], waypoint["y"], corridor):
                continue

            dist_m = round(
                math.sqrt((waypoint["x"] - room_x) ** 2 + (waypoint["y"] - room_y) ** 2) * meters_per_unit,
                1,
            )
            add_edge(room_wp, target_id, dist_m)

    for ex in layout["exits"]:
        exit_id = ex["id"]
        if graph.get(exit_id):
            continue

        exit_center_x = ex["x"] + ex.get("width", 0) / 2
        exit_center_y = ex["y"] + ex.get("height", 0) / 2
        nearest_wp = None
        nearest_dist_px = float("inf")

        for waypoint in layout["waypoints"]:
            dx = waypoint["x"] - exit_center_x
            dy = waypoint["y"] - exit_center_y
            dist_px = math.sqrt(dx * dx + dy * dy)
            if dist_px < nearest_dist_px:
                nearest_dist_px = dist_px
                nearest_wp = waypoint["id"]

        if nearest_wp:
            dist_m = round(nearest_dist_px * meters_per_unit, 1)
            add_edge(exit_id, nearest_wp, dist_m)

    return graph


def get_room_connection_waypoint(layout, room_id):
    for connection in layout.get("connections", {}).get("room_to_corridor", []):
        if connection.get("room_id") == room_id:
            return connection.get("waypoint_id")
    return None


def get_corridor_waypoints(layout, corridor_id):
    waypoint_ids = set()
    corridor = find_element(layout, corridor_id)

    for connection in layout.get("connections", {}).get("room_to_corridor", []):
        if connection.get("corridor_id") == corridor_id:
            waypoint_ids.add(connection.get("waypoint_id"))

    for connection in layout.get("connections", {}).get("corridor_to_vertical_egress", []):
        if connection.get("corridor_id") == corridor_id:
            waypoint_ids.add(connection.get("waypoint_id"))

    if corridor and corridor.get("type") == "corridor":
        for waypoint in layout.get("waypoints", []):
            if point_in_rect(waypoint["x"], waypoint["y"], corridor):
                waypoint_ids.add(waypoint["id"])

    return {waypoint_id for waypoint_id in waypoint_ids if waypoint_id}


def get_emergency_rules(layout):
    rules = {}
    rules.update(DEFAULT_EMERGENCY_RULES)
    rules.update(layout.get("emergency_rules", {}))
    return rules


def zone_for_element(element, emergency_type, location_id, block=False, weight=0, radius=0):
    if radius and radius > 0:
        center_x, center_y = element_center(element)
        zone_rect = {
            "x": max(0, center_x - radius),
            "y": max(0, center_y - radius),
            "width": radius * 2,
            "height": radius * 2,
        }
    else:
        zone_rect = {
            "x": element["x"],
            "y": element["y"],
            "width": element.get("width", 0),
            "height": element.get("height", 0),
        }

    return {
        "id": f"ZONE_{emergency_type}_{location_id}",
        "source_id": location_id,
        "type": emergency_type,
        "block": bool(block),
        "weight": float(weight or 0),
        "radius": float(radius or 0),
        "x": zone_rect["x"],
        "y": zone_rect["y"],
        "width": zone_rect["width"],
        "height": zone_rect["height"],
        "severity": "blocked" if block else "weighted",
    }


def normalize_emergencies(layout, emergencies):
    normalized = []
    seen = set()

    for item in emergencies or []:
        location = str(item.get("location", "")).strip()
        emergency_type = str(item.get("type", "")).strip().upper()
        if not location or emergency_type not in SUPPORTED_TYPES:
            continue
        if not find_element(layout, location):
            continue

        key = (location, emergency_type)
        if key in seen:
            continue
        seen.add(key)
        normalized.append({"location": location, "type": emergency_type})

    return normalized


def emergency_sources_to_hazards(layout, emergencies):
    rules = get_emergency_rules(layout)

    blocked_elements = set()
    blocked_waypoints = set()
    weighted_waypoints = {}
    blocked_zones = []
    weighted_zones = []

    normalized_emergencies = normalize_emergencies(layout, emergencies)


    # Precompute which corridors are blocked
    blocked_corridors = set()
    for emergency in normalized_emergencies:
        location_id = emergency["location"]
        emergency_type = emergency["type"]
        element = find_element(layout, location_id)
        if not element:
            continue
        rule = rules.get(emergency_type, {})
        block = bool(rule.get("block", False))
        if block and element.get("type") == "corridor":
            blocked_corridors.add(location_id)

    # Map intersection waypoints to all connected corridors
    intersection_to_corridors = {}
    for corridor in layout.get("corridors", []):
        for wp_id in get_corridor_waypoints(layout, corridor["id"]):
            if wp_id.startswith("J_"):
                intersection_to_corridors.setdefault(wp_id, set()).add(corridor["id"])

    for emergency in normalized_emergencies:
        location_id = emergency["location"]
        emergency_type = emergency["type"]
        element = find_element(layout, location_id)
        if not element:
            continue

        rule = rules.get(emergency_type, {})
        block = bool(rule.get("block", False))
        radius = float(rule.get("radius", 0) or 0)
        weight = float(rule.get("weight", 0) or 0)
        
        element_type = element.get("type")

        if block:
            blocked_elements.add(location_id)

        if element_type == "room":
            room_waypoint = get_room_connection_waypoint(layout, location_id)
            if room_waypoint:
                if weight:
                    weighted_waypoints[room_waypoint] = max(weighted_waypoints.get(room_waypoint, 0), weight)

        if element_type == "corridor":
            for waypoint_id in get_corridor_waypoints(layout, location_id):
                waypoint = next((wp for wp in layout.get("waypoints", []) if wp.get("id") == waypoint_id), None)
                if not waypoint:
                    continue
                if waypoint_id.startswith("J_"):
                    # Only block intersection if all connected corridors are blocked
                    connected_corrs = intersection_to_corridors.get(waypoint_id, set())
                    if block and connected_corrs and connected_corrs.issubset(blocked_corridors):
                        blocked_waypoints.add(waypoint_id)
                    else:
                        if weight or block:
                            weighted_waypoints[waypoint_id] = max(weighted_waypoints.get(waypoint_id, 0), weight if weight else 2.0)
                    continue
                if block:
                    blocked_waypoints.add(waypoint_id)
                elif weight:
                    weighted_waypoints[waypoint_id] = max(weighted_waypoints.get(waypoint_id, 0), weight)

        zone = zone_for_element(element, emergency_type, location_id, block=block, weight=weight, radius=radius)
        if block and element_type != "room":
            blocked_zones.append(zone)
        else:
            weighted_zones.append(zone)

        if radius <= 0:
            continue

        center_x, center_y = element_center(element)


        for candidate in iter_all_elements(layout):
            if candidate.get("id") == location_id:
                continue
            if candidate.get("type") not in {"room", "corridor"}:
                continue
            if point_to_rect_distance(center_x, center_y, candidate) > radius:
                continue

            cand_id = candidate.get("id")
            cand_type = candidate.get("type")

            # Do NOT block neighbor corridors, only apply weight penalty
            if cand_type == "room":
                room_wp = get_room_connection_waypoint(layout, cand_id)
                if room_wp:
                    weighted_waypoints[room_wp] = max(weighted_waypoints.get(room_wp, 0), 3.0)
            elif cand_type == "corridor":
                for wp_id in get_corridor_waypoints(layout, cand_id):
                    if wp_id.startswith("J_"):
                        weighted_waypoints[wp_id] = max(weighted_waypoints.get(wp_id, 0), 2.0)
                    else:
                        weighted_waypoints[wp_id] = max(weighted_waypoints.get(wp_id, 0), weight if weight else 2.0)

        for waypoint in layout.get("waypoints", []):
            waypoint_dist = math.sqrt((waypoint["x"] - center_x) ** 2 + (waypoint["y"] - center_y) ** 2)
            if waypoint_dist > radius:
                continue

            waypoint_id = waypoint["id"]
            if waypoint_id.startswith("J_"):
                weighted_waypoints[waypoint_id] = max(weighted_waypoints.get(waypoint_id, 0), 2.0)
            elif block:
                blocked_waypoints.add(waypoint_id)
            else:
                weighted_waypoints[waypoint_id] = max(weighted_waypoints.get(waypoint_id, 0), weight)

    return {
        "normalized_emergencies": normalized_emergencies,
        "blocked_elements": sorted(blocked_elements),
        "blocked_waypoints": blocked_waypoints,
        "weighted_waypoints": weighted_waypoints,
        "blocked_zones": blocked_zones,
        "weighted_zones": weighted_zones,
    }


def get_blocked_rects(layout, blocked_elements, blocked_zones):
    blocked_rects = []
    for element_id in blocked_elements:
        element = find_element(layout, element_id)
        if element and element.get("type") in {"room", "corridor"}:
            blocked_rects.append(element)
    blocked_rects.extend(blocked_zones)
    return blocked_rects


def build_safe_graph(layout, graph, blocked_elements, danger_nodes, blocked_zones, weighted_zones, weighted_waypoints):
    blocked_rects = get_blocked_rects(layout, blocked_elements, blocked_zones)
    safe_graph = {node_id: [] for node_id in graph if node_id not in danger_nodes}
    
    room_waypoint_ids = {
        conn.get("waypoint_id")
        for conn in layout.get("connections", {}).get("room_to_corridor", [])
        if conn.get("waypoint_id")
    }

    for node_id, neighbors in graph.items():
        if node_id in danger_nodes:
            continue

        ax, ay = get_waypoint_coords(layout, node_id)
        for neighbor_id, dist in neighbors:
            if neighbor_id in danger_nodes or neighbor_id not in safe_graph:
                continue

            bx, by = get_waypoint_coords(layout, neighbor_id)
            if ax is None or bx is None:
                continue
            
            is_room_waypoint_edge = node_id in room_waypoint_ids or neighbor_id in room_waypoint_ids
            is_node_room_wp = node_id in room_waypoint_ids
            is_neighbor_room_wp = neighbor_id in room_waypoint_ids
            
            should_skip_edge = False
            room_wp_penalized = False
            
            for rect in blocked_rects:
                if not segment_intersects_rect(ax, ay, bx, by, rect):
                    continue
                
                node_in_rect = point_in_rect(ax, ay, rect)
                neighbor_in_rect = point_in_rect(bx, by, rect)
                
                if is_node_room_wp and node_in_rect:
                    room_wp_penalized = True
                    continue
                if is_neighbor_room_wp and neighbor_in_rect:
                    room_wp_penalized = True
                    continue
                
                should_skip_edge = True
                break
            
            if should_skip_edge:
                continue
            
            if room_wp_penalized:
                penalty = 10.0
                adjusted_dist = round(max(0.1, float(dist) + penalty), 2)
                safe_graph[node_id].append((neighbor_id, adjusted_dist))
                continue

            node_penalty = 0.5 * (
                weighted_waypoints.get(node_id, 0.0) + weighted_waypoints.get(neighbor_id, 0.0)
            )
            zone_penalty = 0.0
            for zone in weighted_zones:
                if segment_intersects_rect(ax, ay, bx, by, zone):
                    zone_penalty += float(zone.get("weight", 0))

            adjusted_dist = round(max(0.1, float(dist) + node_penalty + zone_penalty), 2)
            safe_graph[node_id].append((neighbor_id, adjusted_dist))

    return safe_graph


def orthogonal_edge_points(ax, ay, bx, by, blocked_rects):
    if ax == bx or ay == by:
        return [(ax, ay), (bx, by)]

    candidates = [
        [(ax, ay), (ax, by), (bx, by)],
        [(ax, ay), (bx, ay), (bx, by)],
    ]

    def segment_blocked(points):
        for index in range(len(points) - 1):
            sx, sy = points[index]
            ex, ey = points[index + 1]
            for rect in blocked_rects:
                if segment_intersects_rect(sx, sy, ex, ey, rect):
                    return True
        return False

    for points in candidates:
        if not segment_blocked(points):
            return points

    return [(ax, ay), (bx, by)]


def build_display_path(layout, path_nodes, blocked_elements, blocked_zones):
    blocked_rects = get_blocked_rects(layout, blocked_elements, blocked_zones)
    coords = []

    for index, node_id in enumerate(path_nodes):
        ax, ay = get_waypoint_coords(layout, node_id)
        if ax is None:
            continue

        if index == 0:
            coords.append({"id": node_id, "x": ax, "y": ay})
            continue

        prev_id = path_nodes[index - 1]
        px, py = get_waypoint_coords(layout, prev_id)
        if px is None:
            coords.append({"id": node_id, "x": ax, "y": ay})
            continue

        polyline = orthogonal_edge_points(px, py, ax, ay, blocked_rects)
        for bend_index, (x, y) in enumerate(polyline[1:], start=1):
            point_id = node_id if bend_index == len(polyline) - 1 else f"{prev_id}_{node_id}_B{bend_index}"
            if coords and coords[-1]["x"] == x and coords[-1]["y"] == y:
                continue
            coords.append({"id": point_id, "x": x, "y": y})

    return coords


def get_waypoint_coords(layout, node_id):
    for waypoint in layout["waypoints"]:
        if waypoint["id"] == node_id:
            return waypoint["x"], waypoint["y"]
    for ex in layout["exits"]:
        if ex["id"] == node_id:
            return ex["x"] + ex.get("width", 0) / 2, ex["y"] + ex.get("height", 0) / 2
    return None, None


def get_waypoint_label(layout, node_id):
    for waypoint in layout["waypoints"]:
        if waypoint["id"] == node_id:
            return waypoint.get("label", node_id)
    for ex in layout["exits"]:
        if ex["id"] == node_id:
            return ex.get("name", node_id)
    return node_id


def room_to_waypoints(layout, room_id):
    explicit_waypoint = get_room_connection_waypoint(layout, room_id)
    if explicit_waypoint:
        return explicit_waypoint

    room = next((room for room in layout["rooms"] if room["id"] == room_id), None)
    if not room:
        return None

    room_center_x = room["x"] + room["width"] / 2
    room_center_y = room["y"] + room["height"] / 2
    best_waypoint = None
    best_distance = float("inf")

    for waypoint in layout["waypoints"]:
        dx = waypoint["x"] - room_center_x
        dy = waypoint["y"] - room_center_y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < best_distance:
            best_distance = distance
            best_waypoint = waypoint["id"]

    return best_waypoint


def shortest_safe_path(graph, start, end, danger_nodes):
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


def find_nearest_exit(layout, graph, start_wp, danger_nodes):
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
        aco_path, aco_dist = aco.find_path(start_wp, exit_id, danger_nodes)
        dijkstra_path, dijkstra_dist = shortest_safe_path(graph, start_wp, exit_id, danger_nodes)

        if dijkstra_path and (not aco_path or dijkstra_dist <= aco_dist):
            path, dist = dijkstra_path, dijkstra_dist
        else:
            path, dist = aco_path, aco_dist

        if path and dist < best_dist:
            best_dist = dist
            best_path = path
            best_exit = exit_id

    return best_path, best_dist, best_exit


def generate_directions(path, layout):
    directions = []
    meters_per_unit = layout.get("building", {}).get("meters_per_unit", 1.0)

    for index in range(len(path) - 1):
        curr = path[index]
        next_node = path[index + 1]

        cx, cy = get_waypoint_coords(layout, curr)
        nx, ny = get_waypoint_coords(layout, next_node)
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
        next_label = get_waypoint_label(layout, next_node)

        if next_node.startswith("E"):
            step = f"Walk {dist_m}m {direction} -> EVACUATE through {next_label}!"
        elif "Stair" in next_label:
            step = f"Walk {dist_m}m {direction} -> Take {next_label} down to ground floor"
        else:
            step = f"Walk {dist_m}m {direction} -> {next_label}"

        directions.append(
            {
                "step": index + 1,
                "instruction": step,
                "from": curr_label,
                "to": next_label,
                "distance_m": dist_m,
                "direction": direction,
            }
        )

    return directions


def simplify_path_nodes(path, graph):
    # Remove all cycles and repeated nodes from the path
    node_to_index = {}
    i = 0
    while i < len(path):
        node = path[i]
        if node in node_to_index:
            # Cycle detected: remove all nodes between previous occurrence and now
            prev_index = node_to_index[node]
            path = path[:prev_index + 1] + path[i:]
            # Restart from the previous node
            i = prev_index
            node_to_index = {n: idx for idx, n in enumerate(path[:i+1])}
        else:
            node_to_index[node] = i
            i += 1
    return path


def run_pathfinder(start_room, emergencies, layout_path="data/building_layout.json"):
    layout = load_layout(layout_path)
    graph = build_graph(layout)

    start_wp = room_to_waypoints(layout, start_room)
    if not start_wp:
        return {"success": False, "error": f"Invalid start room: {start_room}"}

    hazard_info = emergency_sources_to_hazards(layout, emergencies)
    danger_nodes = set(hazard_info["blocked_waypoints"])
    
    if start_wp in danger_nodes:
        danger_nodes.discard(start_wp)

    safe_graph = build_safe_graph(
        layout,
        graph,
        hazard_info["blocked_elements"],
        danger_nodes,
        hazard_info["blocked_zones"],
        hazard_info["weighted_zones"],
        hazard_info["weighted_waypoints"],
    )

    print("\n" + "=" * 56)
    print(f"PATHFINDER | start={start_room}")
    print(f"Emergencies: {hazard_info['normalized_emergencies']}")
    print(f"Blocked elements: {hazard_info['blocked_elements']}")
    print(f"Blocked waypoints: {sorted(danger_nodes)}")
    print("=" * 56)

    if start_room in hazard_info["blocked_elements"] and start_wp in danger_nodes:
        return {
            "success": False,
            "error": "The selected start room is inside a blocked emergency zone.",
            "start_room": start_room,
            "emergencies": hazard_info["normalized_emergencies"],
            "blocked_elements": hazard_info["blocked_elements"],
            "hazard_zones": hazard_info["blocked_zones"],
            "weighted_zones": hazard_info["weighted_zones"],
        }

    best_path, best_dist, best_exit = find_nearest_exit(layout, safe_graph, start_wp, danger_nodes)

    if not best_path:
        return {
            "success": False,
            "error": "No safe path found from the selected room to any exit.",
            "start_room": start_room,
            "emergencies": hazard_info["normalized_emergencies"],
            "blocked_elements": hazard_info["blocked_elements"],
            "hazard_zones": hazard_info["blocked_zones"],
            "weighted_zones": hazard_info["weighted_zones"],
        }

    best_path = simplify_path_nodes(best_path, safe_graph)
    directions = generate_directions(best_path, layout)
    path_coords = build_display_path(
        layout,
        best_path,
        hazard_info["blocked_elements"],
        hazard_info["blocked_zones"],
    )

    return {
        "success": True,
        "start_room": start_room,
        "emergencies": hazard_info["normalized_emergencies"],
        "best_exit": best_exit,
        "path_nodes": best_path,
        "path_coords": path_coords,
        "total_distance_m": round(best_dist, 1),
        "danger_nodes": sorted(danger_nodes),
        "blocked_elements": hazard_info["blocked_elements"],
        "hazard_zones": hazard_info["blocked_zones"],
        "weighted_zones": hazard_info["weighted_zones"],
        "directions": directions,
        "total_steps": len(directions),
    }


if __name__ == "__main__":
    demo_emergencies = [
        {"location": "C1A", "type": "FIRE"},
        {"location": "C2B", "type": "BLOCKAGE"},
        {"location": "C5A", "type": "SMOKE"},
    ]
    result = run_pathfinder("G07", demo_emergencies)
    print("\nRESULT:")
    print(result)
