"""
semantic_analyzer.py
Performs semantic analysis and validation on the Boolean Expression AST:
1. Collects all unique identifiers/variables.
2. Validates supported operators and operand counts (arity).
3. Verifies variable binding / assignment coverage for evaluation.
4. Performs type checking on operand expressions.
5. Detects redundant/tautological expressions and contradictions.
"""

from typing import Set, Dict, List, Optional, Any
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

    VALID_BINARY_OPS = {
        "AND", "OR", "XOR", "NAND", "NOR", "XNOR", "IMPLIES", "IFF",
        "&&", "||", "^", "->", "<->"
    }
    VALID_UNARY_OPS = {"NOT", "!", "~"}

    def __init__(self):
        self.variables: Set[str] = set()
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def analyze(self, root: ASTNode) -> Dict[str, Any]:
        """
        Runs complete semantic validation on the AST root.
        Returns a dictionary containing extracted metadata and analysis results.
        """
        self.variables.clear()
        self.errors.clear()
        self.warnings.clear()

        if root is None:
            raise SemanticError("Expression tree is empty.")

        # Step 1: Traverse and validate AST nodes
        self._traverse(root)

        if self.errors:
            raise SemanticError("; \n".join(self.errors))

        return {
            "valid": True,
            "variables": sorted(list(self.variables)),
            "variable_count": len(self.variables),
            "is_constant": len(self.variables) == 0,
            "warnings": self.warnings
        }

    def _traverse(self, node: ASTNode) -> None:
        """Recursively checks node types, supported operators, symbols, and semantics."""
        if node is None:
            return

        if isinstance(node, BinaryOpNode):
            # 1. Operator validation
            if node.op not in self.VALID_BINARY_OPS:
                self.errors.append(
                    f"Unsupported binary operator '{node.op}' at line {node.line}, column {node.column}"
                )

            # 2. Arity check
            if node.left is None or node.right is None:
                self.errors.append(
                    f"Binary operator '{node.op}' requires two operands at line {node.line}, column {node.column}"
                )
            else:
                # 3. Detect redundant identical operands: (A AND A), (A OR A)
                if self._are_nodes_identical(node.left, node.right):
                    self.warnings.append(
                        f"Redundant operation '{node.op}' with identical operands at line {node.line}, column {node.column}"
                    )

                # 4. Detect contradiction / tautology: (A AND NOT A) or (A OR NOT A)
                if self._is_negation_pair(node.left, node.right):
                    if node.op in {"AND", "&&"}:
                        self.warnings.append(
                            f"Contradiction detected (always False) at line {node.line}, column {node.column}"
                        )
                    elif node.op in {"OR", "||"}:
                        self.warnings.append(
                            f"Tautology detected (always True) at line {node.line}, column {node.column}"
                        )

                self._traverse(node.left)
                self._traverse(node.right)

        elif isinstance(node, UnaryOpNode):
            # 1. Operator validation
            if node.op not in self.VALID_UNARY_OPS:
                self.errors.append(
                    f"Unsupported unary operator '{node.op}' at line {node.line}, column {node.column}"
                )

            # 2. Arity check
            if node.operand is None:
                self.errors.append(
                    f"Unary operator '{node.op}' requires an operand at line {node.line}, column {node.column}"
                )
            else:
                # 3. Double negation warning: !!A or ~~A
                if isinstance(node.operand, UnaryOpNode) and node.operand.op == node.op:
                    self.warnings.append(
                        f"Redundant double negation detected at line {node.line}, column {node.column}"
                    )

                self._traverse(node.operand)

        elif isinstance(node, VariableNode):
            if not node.name or not str(node.name).strip():
                self.errors.append(
                    f"Empty variable identifier found at line {node.line}, column {node.column}"
                )
            elif node.name[0].isdigit():
                self.errors.append(
                    f"Invalid variable identifier '{node.name}' cannot start with a digit at line {node.line}, column {node.column}"
                )
            else:
                self.variables.add(node.name)

        elif isinstance(node, LiteralNode):
            # Validate literal boolean value type
            if not isinstance(node.value, bool):
                self.errors.append(
                    f"Type mismatch: Expected boolean literal, got '{type(node.value).__name__}' ({node.value}) at line {node.line}, column {node.column}"
                )

        else:
            self.errors.append(f"Unknown AST node encountered: {type(node).__name__}")

    def _are_nodes_identical(self, left: ASTNode, right: ASTNode) -> bool:
        """Helper to determine if two subtrees represent identical operations."""
        if type(left) is not type(right):
            return False
        if isinstance(left, VariableNode):
            return left.name == right.name
        if isinstance(left, LiteralNode):
            return left.value == right.value
        return False

    def _is_negation_pair(self, left: ASTNode, right: ASTNode) -> bool:
        """Helper to detect if one node is the direct negation of the other (e.g., A and !A)."""
        if isinstance(right, UnaryOpNode) and right.op in self.VALID_UNARY_OPS:
            return self._are_nodes_identical(left, right.operand)
        if isinstance(left, UnaryOpNode) and left.op in self.VALID_UNARY_OPS:
            return self._are_nodes_identical(left.operand, right)
        return False

    def check_variable_bindings(self, root: ASTNode, env: Dict[str, bool]) -> None:
        """
        Ensures all variables in the expression have a corresponding value in the evaluation environment
        and that the bound values are valid booleans.
        """
        self.analyze(root)
        
        missing_vars = [var for var in self.variables if var not in env]
        if missing_vars:
            raise SemanticError(
                f"Missing boolean value assignments for variable(s): {', '.join(missing_vars)}"
            )

        # Type check the assigned values
        invalid_types = [
            var for var in self.variables 
            if var in env and not isinstance(env[var], bool)
        ]
        if invalid_types:
            raise SemanticError(
                f"Non-boolean values assigned to variable(s): {', '.join(invalid_types)}"
            )

    @staticmethod
    def get_symbols(root: ASTNode) -> List[str]:
        """Convenience method to retrieve all variable names in alphabetical order."""
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(root)
        return result["variables"]
