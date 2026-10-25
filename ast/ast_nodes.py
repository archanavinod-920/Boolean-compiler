"""
ast_nodes.py
Defines the Abstract Syntax Tree (AST) node structures, 
tree serialization for the frontend, and terminal display utilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class ASTNode(ABC):
    """Base class for all Abstract Syntax Tree nodes."""

    def __init__(self, line: int = 1, column: int = 1):
        self.line = line
        self.column = column

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serializes the node into a dictionary for JSON/frontend visualization."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Returns a string representation of the node."""
        pass


class BinaryOpNode(ASTNode):
    """Represents binary boolean operations (e.g., AND, OR, XOR, NAND, NOR, IMPLIES)."""

    def __init__(self, left: ASTNode, op: str, right: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.left = left
        self.op = op.upper()
        self.right = right

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "BinaryOp",
            "name": self.op,
            "operator": self.op,
            "children": [
                self.left.to_dict(),
                self.right.to_dict()
            ],
            "line": self.line,
            "column": self.column
        }

    def __str__(self) -> str:
        return f"BinaryOp({self.left} {self.op} {self.right})"


class UnaryOpNode(ASTNode):
    """Represents unary boolean operations (e.g., NOT)."""

    def __init__(self, op: str, operand: ASTNode, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.op = op.upper()
        self.operand = operand

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "UnaryOp",
            "name": self.op,
            "operator": self.op,
            "children": [
                self.operand.to_dict()
            ],
            "line": self.line,
            "column": self.column
        }

    def __str__(self) -> str:
        return f"UnaryOp({self.op} {self.operand})"


class VariableNode(ASTNode):
    """Represents variable identifiers (e.g., A, B, X, Y)."""

    def __init__(self, name: str, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.name = name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Variable",
            "name": self.name,
            "children": [],
            "line": self.line,
            "column": self.column
        }

    def __str__(self) -> str:
        return f"Var({self.name})"


class LiteralNode(ASTNode):
    """Represents boolean constants (e.g., True/False, 1/0)."""

    def __init__(self, value: bool, line: int = 1, column: int = 1):
        super().__init__(line, column)
        self.value = bool(value)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "Literal",
            "name": str(self.value),
            "value": self.value,
            "children": [],
            "line": self.line,
            "column": self.column
        }

    def __str__(self) -> str:
        return f"Lit({self.value})"


def display_ast(node: ASTNode, prefix: str = "", is_last: bool = True) -> str:
    """
    Renders an ASCII tree representation of the AST for CLI / debugging.
    
    Example:
    ├── OR
    │   ├── AND
    │   │   ├── Var(A)
    │   │   └── Var(B)
    │   └── Var(C)
    """
    marker = "└── " if is_last else "├── "
    
    if isinstance(node, BinaryOpNode):
        display_name = node.op
        children = [node.left, node.right]
    elif isinstance(node, UnaryOpNode):
        display_name = node.op
        children = [node.operand]
    elif isinstance(node, VariableNode):
        display_name = f"Var({node.name})"
        children = []
    elif isinstance(node, LiteralNode):
        display_name = f"Lit({node.value})"
        children = []
    else:
        display_name = str(node)
        children = []

    lines = [f"{prefix}{marker}{display_name}"]
    
    child_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(children):
        last = (i == len(children) - 1)
        lines.append(display_ast(child, child_prefix, last))

    return "\n".join(lines)
