#!/usr/bin/env python3
"""
mba_simplifier.py
Static Mixed Boolean-Arithmetic (MBA) AST simplification pass for analyzing
obfuscated VM handlers in defensive binary research.
"""

from __future__ import annotations
import ast
from typing import Dict, List, Tuple

BIT_MASK = 0xFFFFFFFF


def eval_expr_mod32(node: ast.AST, env: Dict[str, int]) -> int:
    """Evaluate a 32-bit modular arithmetic/bitwise AST node against a test vector."""
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value & BIT_MASK
    if isinstance(node, ast.Name):
        return env[node.id] & BIT_MASK
    if isinstance(node, ast.UnaryOp):
        operand = eval_expr_mod32(node.operand, env)
        if isinstance(node.op, ast.Invert):
            return (~operand) & BIT_MASK
        if isinstance(node.op, ast.USub):
            return (-operand) & BIT_MASK
    if isinstance(node, ast.BinOp):
        left = eval_expr_mod32(node.left, env)
        right = eval_expr_mod32(node.right, env)
        if isinstance(node.op, ast.Add):
            return (left + right) & BIT_MASK
        if isinstance(node.op, ast.Sub):
            return (left - right) & BIT_MASK
        if isinstance(node.op, ast.Mult):
            return (left * right) & BIT_MASK
        if isinstance(node.op, ast.BitXor):
            return (left ^ right) & BIT_MASK
        if isinstance(node.op, ast.BitAnd):
            return (left & right) & BIT_MASK
        if isinstance(node.op, ast.BitOr):
            return (left | right) & BIT_MASK
    raise ValueError(f"Unsupported AST construct: {ast.dump(node)}")


class MBACanonicalizer:
    """Synthesizes canonical expressions by matching evaluation vectors over sample points."""

    SAMPLE_VECTORS: List[Tuple[int, int]] = [
        (0x00000000, 0x00000000),
        (0x00000001, 0x00000001),
        (0x00000001, 0x00000000),
        (0x00000000, 0x00000001),
        (0x13579BDF, 0x2468ACE0),
        (0xCAFEBABE, 0xDEADBEEF),
        (0xFFFFFFFF, 0x00000001),
        (0x7FFFFFFF, 0x80000000),
    ]

    CANONICAL_CANDIDATES: List[str] = [
        "0",
        "1",
        "x",
        "y",
        "~x",
        "~y",
        "-x",
        "-y",
        "x + y",
        "x - y",
        "y - x",
        "x ^ y",
        "x & y",
        "x | y",
        "~(x ^ y)",
        "~(x & y)",
        "~(x | y)",
        "(x & ~y)",
        "(~x & y)",
        "x + 1",
        "y + 1",
        "x - 1",
        "y - 1",
    ]

    def __init__(self) -> None:
        self._signature_table: Dict[Tuple[int, ...], str] = {}
        self._build_lookup_table()

    def _compute_signature(self, tree: ast.AST) -> Tuple[int, ...]:
        sig = []
        for vx, vy in self.SAMPLE_VECTORS:
            val = eval_expr_mod32(tree, {"x": vx, "y": vy})
            sig.append(val)
        return tuple(sig)

    def _build_lookup_table(self) -> None:
        for candidate in self.CANONICAL_CANDIDATES:
            parsed = ast.parse(candidate, mode="eval").body
            sig = self._compute_signature(parsed)
            if sig not in self._signature_table:
                self._signature_table[sig] = candidate

    def simplify(self, expr_str: str) -> str:
        parsed = ast.parse(expr_str, mode="eval").body
        rewritten = self._rewrite_node(parsed)
        return ast.unparse(rewritten)

    def _rewrite_node(self, node: ast.AST) -> ast.AST:
        if isinstance(node, ast.BinOp):
            node.left = self._rewrite_node(node.left)
            node.right = self._rewrite_node(node.right)
        elif isinstance(node, ast.UnaryOp):
            node.operand = self._rewrite_node(node.operand)

        try:
            sig = self._compute_signature(node)
            if sig in self._signature_table:
                canonical = self._signature_table[sig]
                return ast.parse(canonical, mode="eval").body
        except ValueError:
            pass
        return node


def run_self_test() -> None:
    simplifier = MBACanonicalizer()
    test_cases = [
        "((x ^ y) + 2 * (x & y))",
        "((x | y) + (x & y))",
        "((x | y) - (x ^ y))",
        "((x + y) - (2 * (x & y)))",
        "(x - ~y - 1)",
        "(~(~x | ~y))",
        "((x & ~y) | (~x & y))",
    ]
    for expr in test_cases:
        result = simplifier.simplify(expr)
        print(f"[Original]   {expr}")
        print(f"[Simplified] ({result})\n")


if __name__ == "__main__":
    run_self_test()
