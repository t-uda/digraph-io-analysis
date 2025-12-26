# Digraph I/O-Degree Entropy Analysis

Understanding Discrete Dynamics via Topological Flow Data Analysis.

## Overview

This project analyzes discrete dynamical systems represented as words (COT representation) derived from 2D incompressible flow streamlines. The goal is to analyze the "fluctuation" of in-degree vs. out-degree transitions using Shannon entropy.

## Requirements

- [uv](https://github.com/astral-sh/uv) (for Python package management)

## Setup

Initialize the environment and install dependencies:

```bash
uv sync
```

## Running the Analysis

To run a test analysis on the provided TSV data in the `tsv/` directory:

```bash
uv run examples/test_analysis.py
```

This will:
1. Load data from the TSV file (skipping "error" entries).
2. Build a directed graph of state transitions.
3. Calculate Shannon entropy for each transition.
4. Export the resulting graph to `transition_digraph.gexf`.

## Visualization

The output file `transition_digraph.gexf` can be opened in [Gephi](https://gephi.org/) for interactive visualization and further analysis.

## Project Structure

- `src/digraph_inout_analysis/`: Core module containing the analysis logic.
- `tsv/`: Directory for input data files.
- `examples/`: Example scripts demonstrating usage.
