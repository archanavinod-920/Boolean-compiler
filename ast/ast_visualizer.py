"""
ast_visualizer.py
Provides utilities to visualize the Abstract Syntax Tree (AST):
1. Terminal / ASCII tree display.
2. JSON export for frontend rendering (e.g., D3.js / HTML canvas).
3. Graphviz DOT format generation for generating tree diagrams.
"""

import json
from typing import Any, Dict
from ast.ast_nodes import ASTNode, BinaryOpNode, UnaryOpNode, VariableNode, LiteralNode


class ASTVisualizer:
    """Helper class to visualize, format, and export AST nodes."""

    @staticmethod
    def to_ascii_tree(node: ASTNode, prefix: str = "", is_last: bool = True) -> str:
        """
        Renders an ASCII tree structure suitable for console/terminal logs.

        Example Output:
        └── OR
            ├── AND
            │   ├── Var(A)
            │   └── Var(B)
            └── Var(C)
        """
        marker = "└── " if is_last else "├── "

        if isinstance(node, BinaryOpNode):
            label = f"BinaryOp({node.op})"
            children = [node.left, node.right]
        elif isinstance(node, UnaryOpNode):
            label = f"UnaryOp({node.op})"
            children = [node.operand]
        elif isinstance(node, VariableNode):
            label = f"Var({node.name})"
            children = []
        elif isinstance(node, LiteralNode):
            label = f"Lit({node.value})"
            children = []
        else:
            label = str(node)
            children = []

        lines = [f"{prefix}{marker}{label}"]

        child_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(children):
            last_child = (i == len(children) - 1)
            lines.append(ASTVisualizer.to_ascii_tree(child, child_prefix, last_child))

        return "\n".join(lines)

    @staticmethod
    def to_json(node: ASTNode, indent: int = 2) -> str:
        """
        Serializes the AST into a JSON string formatted for web frontend consumption.
        """
        return json.dumps(node.to_dict(), indent=indent)

    @staticmethod
    def to_dot(node: ASTNode) -> str:
        """
        Converts the AST to Graphviz DOT format for SVG/PNG graph generation.
        """
        lines = [
            "digraph AST {",
            '  node [fontname="Helvetica", shape=box, style="rounded,filled", fillcolor="#f0f4f8"];',
            '  edge [fontname="Helvetica"];'
        ]
        counter = [0]

        def add_nodes(curr_node: ASTNode) -> int:
            counter[0] += 1
            node_id = counter[0]

            if isinstance(curr_node, BinaryOpNode):
                label = curr_node.op
                color = "#d1e7dd"  # Soft green
                lines.append(f'  node_{node_id} [label="{label}", fillcolor="{color}"];')
                left_id = add_nodes(curr_node.left)
                right_id = add_nodes(curr_node.right)
                lines.append(f"  node_{node_id} -> node_{left_id};")
                lines.append(f"  node_{node_id} -> node_{right_id};")

            elif isinstance(curr_node, UnaryOpNode):
                label = curr_node.op
                color = "#fff3cd"  # Soft yellow
                lines.append(f'  node_{node_id} [label="{label}", fillcolor="{color}"];')
                child_id = add_nodes(curr_node.operand)
                lines.append(f"  node_{node_id} -> node_{child_id};")

            elif isinstance(curr_node, VariableNode):
                label = f"Var: {curr_node.name}"
                color = "#cfe2ff"  # Soft blue
                lines.append(f'  node_{node_id} [label="{label}", fillcolor="{color}"];')

            elif isinstance(curr_node, LiteralNode):
                label = f"Lit: {curr_node.value}"
                color = "#e2e3e5"  # Soft gray
                lines.append(f'  node_{node_id} [label="{label}", fillcolor="{color}"];')

            return node_id

        add_nodes(node)
        lines.append("}")
        return "\n".join(lines)


def print_ast(node: ASTNode) -> None:
    """Convenience function to print the ASCII tree directly to console."""
    print(ASTVisualizer.to_ascii_tree(node))
