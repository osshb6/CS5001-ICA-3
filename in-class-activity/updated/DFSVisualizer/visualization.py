"""Tree visualization functions."""


def visualize_tree(tree, format_type="text"):
    """Visualize the DFS tree in the specified format."""
    if format_type == "text":
        return visualize_text(tree)
    elif format_type == "dot":
        return visualize_dot(tree)
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def visualize_text(tree):
    """Generate a text-based visualization of the tree."""
    lines = []
    for node, children in tree.items():
        lines.append(f"{node} -> {', '.join(children)}")
    return "\n".join(lines)


def visualize_dot(tree):
    """Generate a DOT format visualization of the tree."""
    lines = ["digraph Tree {", "  rankdir=TB;"]
    for node, children in tree.items():
        for child in children:
            lines.append(f"  {node} -> {child};")
    lines.append("}")
    return "\n".join(lines)
