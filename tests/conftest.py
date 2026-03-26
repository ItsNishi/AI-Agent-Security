"""
Shared fixtures and import path setup for the AI Agent Security test suite.

Import strategy: patterns.py is imported from vet-repo's copy first.
Since all three skills have identical copies, the cached module in
sys.modules["patterns"] works for all subsequent skill imports.
"""

import sys
from pathlib import Path

import pytest

# Repo root (parent of tests/)
Repo_Root = Path(__file__).parent.parent

# Import patterns from vet-repo's copy (they're identical across skills)
Vet_Repo_Scripts = Repo_Root / ".claude" / "skills" / "vet-repo" / "scripts"
Scan_Skill_Scripts = Repo_Root / ".claude" / "skills" / "scan-skill" / "scripts"
Audit_Code_Scripts = Repo_Root / ".claude" / "skills" / "audit-code" / "scripts"

# Seed sys.path so patterns.py is importable
sys.path.insert(0, str(Vet_Repo_Scripts))


@pytest.fixture
def Repo_Root_Path() -> Path:
	"""Path to the repository root."""
	return Repo_Root


@pytest.fixture
def Examples_Dir() -> Path:
	"""Path to the examples/ directory."""
	return Repo_Root / "examples"


@pytest.fixture
def Skills_Dir() -> Path:
	"""Path to .claude/skills/ directory."""
	return Repo_Root / ".claude" / "skills"
