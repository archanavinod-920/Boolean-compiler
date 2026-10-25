"""
semantic_analyzer.py
Performs semantic analysis and validation on the Boolean Expression AST:
1. Collects all unique identifiers/variables.
2. Validates supported operators and operand counts (arity).
3. Verifies variable binding / assignment coverage for evaluation.
4. Detects constant / tautological expressions (optional optimization).
"""

from typing import Set, Dict, List, Optional
from ast.ast_nodes import ASTNode, BinaryOpNode, UnaryOpNode, VariableNode, LiteralNode


class SemanticError(Exception):
    """Custom exception raised when semantic checks fail."""
    def __init__(self, message: str, line: int = 1, column: int = 1):
        super().__init__(f"Semantic Error [Line {line}, Col {column}]: {message}")
        self.message = message
        self.line = line
        self.column = column


class SemanticAnalyzer:
    """Performs semantic analysis on a parsed boolean AST."""

    # Supported operations in the boolean compiler
    VALID_BINARY_OPS = {
        "AND", "OR", "XOR", "NAND", "NOR", "XNOR", "IMPLIES", "IFF",
        "&&", "||", "^", "->", "<->"
    }
    VALID_UNARY_OPS = {"NOT", "!", "~"}

    def __init__(self):
        self.variables: Set[str] = set()
        self.errors: List[str] = []

    def analyze(self, root: ASTNode) -> Dict[str, any]:
        """
        Runs complete semantic validation on the AST root.
        Returns a dictionary containing extracted metadata and analysis results.
        """
        self.variables.clear()
        self.errors.clear()

        # Step 1: Traverse and collect identifiers + validate operators
        self._traverse(root)

        if self.errors:
            raise SemanticError("; ".join(self.errors))

        return {
            "valid": True,
            "variables": sorted(list(self.variables)),
            "variable_count": len(self.variables),
            "is_constant": len(self.variables) == 0
        }

    def _traverse(self, node: ASTNode) -> None:
        """Recursively checks node types, supported operators, and symbols."""
        if isinstance(node, BinaryOpNode):
            if node.op not in self.VALID_BINARY_OPS:
                self.errors.append(
                    f"Unsupported binary operator '{node.op}' at line {node.line}, column {node.column}"
                )
            if node.left is None or node.right is None:
                self.errors.append(
                    f"Binary operator '{node.op}' requires two operands at line {node.line}, column {node.column}"
                )
            if node.left:
                self._traverse(node.left)
            if node.right:
                self._traverse(node.right)

        elif isinstance(node, UnaryOpNode):
            if node.op not in self.VALID_UNARY_OPS:
                self.errors.append(
                    f"Unsupported unary operator '{node.op}' at line {node.line}, column {node.column}"
                )
            if node.operand is None:
                self.errors.append(
                    f"Unary operator '{node.op}' requires an operand at line {node.line}, column {node.column}"
                )
            else:
                self._traverse(node.operand)

        elif isinstance(node, VariableNode):
            if not node.name or not node.name.strip():
                self.errors.append(
                    f"Empty variable identifier found at line {node.line}, column {node.column}"
                )
            else:
                self.variables.add(node.name)

        elif isinstance(node, LiteralNode):
            # Literals are valid boolean values
            pass

        else:
            self.errors.append(f"Unknown AST node encountered: {type(node).__name__}")

    def check_variable_bindings(self, root: ASTNode, env: Dict[str, bool]) -> None:
        """
        Ensures all variables in the expression have a corresponding value in the evaluation environment.
        Useful when generating truth tables or evaluating values.
        """
        self.analyze(root)
        missing_vars = [var for var in self.variables if var not in env]

        if missing_vars:
            raise SemanticError(
                f"Missing boolean value assignments for variable(s): {', '.join(missing_vars)}"
            )

    @staticmethod
    def get_symbols(root: ASTNode) -> List[str]:
        """Convenience method to retrieve all variable names in alphabetical order."""
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(root)
        return result["variables"]
