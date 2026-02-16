"""Helper functions for graph input/output and validation."""


def load_graph(file_path):
    """Load a graph from an adjacency list file."""
    graph = {}
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            node, *neighbors = line.split()
            graph[node] = neighbors
    return graph


def validate_graph(graph):
    """Validate the graph structure (basic checks)."""
    if not graph:
        raise ValueError("Graph is empty")
    for node, neighbors in graph.items():
        if node not in neighbors and node not in graph.get(node, []):
            continue  # Self-loops are allowed
        for neighbor in neighbors:
            if neighbor not in graph:
                raise ValueError(f"Node {neighbor} not found in graph")
