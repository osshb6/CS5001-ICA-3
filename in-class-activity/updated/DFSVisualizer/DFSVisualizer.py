# DFS Tree Generator and Visualizer
# Entry module for the DFS visualizer application.

import argparse
from graph_utils import load_graph, validate_graph
from visualization import visualize_tree


def main():
    """Main entry point for the DFS visualizer CLI."""
    parser = argparse.ArgumentParser(description="DFS Tree Generator and Visualizer")
    parser.add_argument("--input", type=str, default="graph.txt", help="Path to the input graph file (adjacency list)")
    parser.add_argument("--output", type=str, default="output.txt", help="Path to the output visualization file")
    parser.add_argument("--format", type=str, default="text", choices=["text", "dot"], help="Output format: text or dot")
    
    args = parser.parse_args()
    
    # Load and validate the graph
    graph = load_graph(args.input)
    validate_graph(graph)
    
    # Perform DFS and visualize
    traversal_order, tree = perform_dfs(graph)
    visualization = visualize_tree(tree, args.format)
    
    # Write output
    with open(args.output, "w") as f:
        f.write(visualization)
    
    print(f"DFS visualization saved to {args.output}")


def perform_dfs(graph):
    """Perform DFS traversal and return traversal order and tree structure."""
    visited = set()
    traversal_order = []
    tree = {}
    
    def dfs(node, parent):
        if node in visited:
            return
        visited.add(node)
        traversal_order.append(node)
        tree[node] = []
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                tree[node].append(neighbor)
                dfs(neighbor, node)
    
    # Start DFS from the first node in the graph
    start_node = next(iter(graph))
    dfs(start_node, None)
    
    return traversal_order, tree


if __name__ == "__main__":
    main()
