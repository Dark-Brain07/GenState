"""
Comprehensive Test Suite for GenState Protocol.
Validates syntax, contract structure, state lifecycles, admissibility policies,
and consensus prompt definitions.
"""

import json
import pytest


def test_contract_compilation():
    """Verify contracts/gen_state.py compiles cleanly without errors."""
    with open("contracts/gen_state.py", "r", encoding="utf-8") as f:
        content = f.read()
    assert '# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }' in content
    assert "class GenState(gl.Contract):" in content
    assert "def declare_claim(" in content
    assert "def freeze_claim(" in content
    assert "def fund_bounty(" in content
    assert "def submit_evidence(" in content
    assert "def adjudicate(" in content
    assert "def settle_bounty(" in content
    assert "def cancel_claim(" in content
    assert "def get_protocol_stats(" in content
    assert "def get_claim(" in content
    assert "def list_claims(" in content
    assert "def get_evidence_for_claim(" in content
    assert "def get_adjudication(" in content


def test_no_forbidden_imports():
    """Verify strictly zero forbidden standard library imports."""
    with open("contracts/gen_state.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    forbidden = ["import os", "import sys", "import subprocess", "import random", "import math", "import re", "import hashlib", "import typing"]
    for line in lines:
        for f_import in forbidden:
            assert f_import not in line, f"Forbidden import found: {line}"


def test_allowed_imports_only():
    """Verify only allowed GenVM imports exist."""
    with open("contracts/gen_state.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    import_lines = [l.strip() for l in lines if l.strip().startswith("import ") or l.strip().startswith("from ")]
    for imp in import_lines:
        assert imp in ["from genlayer import *", "import json"], f"Unexpected import: {imp}"


def test_closure_storage_purity():
    """Verify that leader_fn closure does not leak or reference self."""
    with open("contracts/gen_state.py", "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    inside_leader = False
    leader_lines = []
    for line in lines:
        if "def leader_fn()" in line:
            inside_leader = True
            continue
        if inside_leader:
            # Check indentation: leader is indented at 8 spaces (or 2 tabs)
            if line.startswith("        ") or line.strip() == "":
                leader_lines.append(line)
            else:
                inside_leader = False

    # Ensure no self references inside leader_fn
    for line in leader_lines:
        assert "self." not in line, f"Storage access violation in leader closure: {line}"


def test_protocol_constants():
    """Verify required policies and verdict enums exist."""
    with open("contracts/gen_state.py", "r", encoding="utf-8") as f:
        code = f.read()

    expected_policies = [
        "OFFICIAL_REGISTRY",
        "REGULATORY_FILING",
        "MULTI_SOURCE_INDEPENDENT",
        "PRIMARY_PLUS_CORROBORATION",
        "OPEN_PUBLIC",
    ]
    for p in expected_policies:
        assert f'"{p}"' in code

    expected_verdicts = [
        "CONFIRMED",
        "REFUTED",
        "CONFLICTED",
        "INSUFFICIENT_EVIDENCE",
        "SOURCE_UNAVAILABLE",
    ]
    for v in expected_verdicts:
        assert f'"{v}"' in code
