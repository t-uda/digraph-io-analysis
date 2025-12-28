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

To run a demo analysis on the provided TSV data in the `tsv/` directory:

```bash
uv run examples/demo_analysis.py
```

## Running Tests

To verify the logic and integration:

```bash
uv run python -m unittest discover tests
```

## Project Structure

- `src/digraph_inout_analysis/`: Core module containing the analysis logic.
- `tsv/`: Directory for input data files.
- `examples/`: Example scripts demonstrating usage.
- `tests/`: Unit tests for core logic and integration.
