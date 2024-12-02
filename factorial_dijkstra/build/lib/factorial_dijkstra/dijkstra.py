# factorial_dijkstra/dijkstra.py

import heapq
from typing import List, Tuple, Dict

def dijkstra(graph: Dict[int, List[Tuple[int, int]]], start: int) -> Dict[int, int]:
    """
    Implements Dijkstra's shortest path algorithm.

    Args:
        graph (dict): A dictionary where keys are node ids, and values are lists of 
                      tuples (neighbor_node, edge_weight).
        start (int): The starting node.

    Returns:
        dict: A dictionary where keys are nodes, and values are the shortest distance 
              from the start node to that node.
    """
    # Priority queue: stores tuples of (distance, node)
    queue = [(0, start)]
    # Dictionary to store the shortest distance to each node
    distances = {start: 0}
    
    while queue:
        current_distance, current_node = heapq.heappop(queue)

        # Skip processing if we already found a shorter path
        if current_distance > distances.get(current_node, float('inf')):
            continue

        # Explore each neighbor of the current node
        for neighbor, weight in graph.get(current_node, []):
            distance = current_distance + weight

            # If a shorter path is found, update the distance and add to the queue
            if distance < distances.get(neighbor, float('inf')):
                distances[neighbor] = distance
                heapq.heappush(queue, (distance, neighbor))
    
    return distances
