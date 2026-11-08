# Security Policy

## Security Maintainer

- **Lead Security Maintainer:** [@bonneyx](https://github.com/bonneyx)
- **Scope:** AST parsing & symbolic expression simplification pass (`mba_simplifier.py`) when processing untrusted binary/IR inputs.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

When analyzing untrusted obfuscated expressions extracted from malware samples, parser safety is critical (`ast.parse` without `eval()`). Please report any input-handling vulnerabilities privately via [GitHub Security Advisories](https://github.com/bonneyx/mba-ir-deobfuscator/security/advisories/new).
