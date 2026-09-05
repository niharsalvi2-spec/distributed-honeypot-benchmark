"""
Research Integrity Test: Strict Ground Truth Isolation
Ensures that no production algorithm (collectors, distributed engines, correlation algorithms,
sequence reconstruction) imports or accesses ground truth manifests or oracle modules.
"""
import os
import ast
import pytest

def get_python_files(directory: str):
    py_files = []
    if not os.path.exists(directory):
        return py_files
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files

def check_file_for_leakage(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    tree = ast.parse(content, filename=file_path)
    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "ground_truth" in alias.name:
                    violations.append((node.lineno, f"import {alias.name}"))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if "ground_truth" in module:
                violations.append((node.lineno, f"from {module} import ..."))

    return violations

def test_no_ground_truth_imports_in_production_algorithms():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    production_dirs = [
        os.path.join(base_dir, "collectors"),
        os.path.join(base_dir, "distributed"),
        os.path.join(base_dir, "correlation"),
        os.path.join(base_dir, "sequence_reconstruction"),
    ]

    all_violations = {}
    for pdir in production_dirs:
        for py_file in get_python_files(pdir):
            violations = check_file_for_leakage(py_file)
            if violations:
                rel_path = os.path.relpath(py_file, base_dir)
                all_violations[rel_path] = violations

    assert not all_violations, f"Ground-truth leakage detected in production code: {all_violations}"
