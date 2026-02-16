# DFS Tree Generator and Visualizer

A simple Python tool to perform Depth-First Search (DFS) on a graph and visualize the resulting tree structure.

## Features

- Perform DFS traversal on a graph
- Visualize the DFS tree in text or DOT format
- Support for adjacency list input

## Installation

No external dependencies are required. The tool uses only Python standard library modules.

## Usage

### Input Format

The input graph should be provided as an adjacency list in a text file. Each line represents a node and its neighbors:

```
A B C
B A D
C A E
D B
E C
```

### Running the Visualizer

```bash
python DFSVisualizer.py --input graph.txt --output output.txt --format text
```

### Command Line Options

- `--input`: Path to the input graph file (default: `graph.txt`)
- `--output`: Path to the output visualization file (default: `output.txt`)
- `--format`: Output format (`text` or `dot`, default: `text`)

### Example

Given the input graph:

```
A B C
B A D
C A E
D B
E C
```

Running the visualizer with `--format text` produces:

```
A -> B, C
B -> D
C -> E
D ->
E ->
```

Running with `--format dot` produces a DOT format file that can be rendered with Graphviz.

## License

This project is open source and available under the MIT License.
