# mba-ir-deobfuscator

Static **Mixed Boolean-Arithmetic (MBA)** expression simplifier and virtualized bytecode handler analysis toolkit for defensive malware reverse engineering.

## Background

Modern malware families frequently employ custom virtualization-based obfuscators and Mixed Boolean-Arithmetic (MBA) transformations to obscure control flow and hinder static signature generation. For example, a simple addition `x + y` may be expanded into linear combinations of bitwise identities:

```text
(x ^ y) + 2 * (x & y)
((x | y) + (x & y))
(x - ~y - 1)
```

`mba-ir-deobfuscator` provides a lightweight Python AST rewriting pass and truth-table equivalence verifier to canonicalize obfuscated expressions encountered in virtualized VM handlers during malware triage.

## Features

- **Truth-Table Signature Synthesis:** Computes 2-variable and 3-variable boolean/modular truth vectors to identify canonical bitwise/arithmetic equivalents in $O(1)$ lookup time.
- **Recursive AST Rewriting:** Simplifies nested bitwise/arithmetic Python AST nodes into minimal canonical forms.
- **VM Handler Slice Lifting:** Normalizes redundant stack push/pop and dead flag computations typical of stack-based virtual machines.

## Quick Start

```bash
python3 mba_simplifier.py
```

### Example Output

```text
[Original]   ((x ^ y) + 2 * (x & y))
[Simplified] (x + y)

[Original]   ((x | y) - (x ^ y))
[Simplified] (x & y)

[Original]   ((x + y) - (2 * (x & y)))
[Simplified] (x ^ y)
```

> **Note:** Research prototype for defensive binary auditing and malware de-obfuscation studies. External PRs are not actively tracked.

## License

MIT License

