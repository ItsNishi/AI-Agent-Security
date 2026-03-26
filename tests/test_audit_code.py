"""
Tests for audit-code: Project code security reviewer.

Uses tmp_path for filesystem-dependent tests (env files, permissions, gitignore).
"""

import os
import stat
import sys
from pathlib import Path

import pytest

# Make audit_code importable
from conftest import Audit_Code_Scripts
sys.path.insert(0, str(Audit_Code_Scripts))

from audit_code import (
	Should_Scan,
	Is_Skipped_Dir,
	Find_Env_Files,
	Check_File_Permissions,
	Check_Gitignore_Coverage,
)
from patterns import Severity, Category


# -- Should_Scan --

class Test_Should_Scan:
	"""Test file extension and size filtering."""

	def Test_Python_File(self, tmp_path):
		f = tmp_path / "script.py"
		f.write_text("print('hello')")
		assert Should_Scan(f) is True

	def Test_Javascript_File(self, tmp_path):
		f = tmp_path / "app.js"
		f.write_text("console.log('hi')")
		assert Should_Scan(f) is True

	def Test_Shell_Script(self, tmp_path):
		f = tmp_path / "deploy.sh"
		f.write_text("#!/bin/bash")
		assert Should_Scan(f) is True

	def Test_Json_File(self, tmp_path):
		f = tmp_path / "config.json"
		f.write_text("{}")
		assert Should_Scan(f) is True

	def Test_Yaml_File(self, tmp_path):
		f = tmp_path / "config.yaml"
		f.write_text("key: value")
		assert Should_Scan(f) is True

	def Test_Env_File(self, tmp_path):
		f = tmp_path / ".env"
		f.write_text("SECRET=x")
		assert Should_Scan(f) is True

	def Test_Env_Local(self, tmp_path):
		f = tmp_path / ".env.local"
		f.write_text("SECRET=x")
		assert Should_Scan(f) is True

	def Test_Dockerfile(self, tmp_path):
		f = tmp_path / "Dockerfile"
		f.write_text("FROM python:3.12")
		assert Should_Scan(f) is True

	def Test_Makefile(self, tmp_path):
		f = tmp_path / "Makefile"
		f.write_text("all: build")
		assert Should_Scan(f) is True

	def Test_Image_File_Rejected(self, tmp_path):
		f = tmp_path / "logo.png"
		f.write_text("fake png data")
		assert Should_Scan(f) is False

	def Test_Binary_File_Rejected(self, tmp_path):
		f = tmp_path / "app.exe"
		f.write_text("fake binary")
		assert Should_Scan(f) is False

	def Test_Archive_Rejected(self, tmp_path):
		f = tmp_path / "backup.zip"
		f.write_text("fake zip")
		assert Should_Scan(f) is False

	def Test_Large_File_Rejected(self, tmp_path):
		f = tmp_path / "huge.py"
		f.write_text("x" * 1_100_000)  # >1MB
		assert Should_Scan(f) is False

	def Test_Nonexistent_File_Rejected(self, tmp_path):
		f = tmp_path / "missing.py"
		assert Should_Scan(f) is False


# -- Is_Skipped_Dir --

class Test_Is_Skipped_Dir:
	"""Test directory skip logic."""

	def Test_Git_Dir_Skipped(self, tmp_path):
		d = tmp_path / ".git"
		d.mkdir()
		assert Is_Skipped_Dir(d) is True

	def Test_Node_Modules_Skipped(self, tmp_path):
		d = tmp_path / "node_modules"
		d.mkdir()
		assert Is_Skipped_Dir(d) is True

	def Test_Pycache_Skipped(self, tmp_path):
		d = tmp_path / "__pycache__"
		d.mkdir()
		assert Is_Skipped_Dir(d) is True

	def Test_Venv_Skipped(self, tmp_path):
		d = tmp_path / ".venv"
		d.mkdir()
		assert Is_Skipped_Dir(d) is True

	def Test_Src_Not_Skipped(self, tmp_path):
		d = tmp_path / "src"
		d.mkdir()
		assert Is_Skipped_Dir(d) is False

	def Test_Lib_Not_Skipped(self, tmp_path):
		d = tmp_path / "lib"
		d.mkdir()
		assert Is_Skipped_Dir(d) is False

	def Test_Tests_Not_Skipped(self, tmp_path):
		d = tmp_path / "tests"
		d.mkdir()
		assert Is_Skipped_Dir(d) is False


# -- Find_Env_Files --

class Test_Find_Env_Files:
	"""Test .env file detection."""

	def Test_No_Env_Files(self, tmp_path):
		findings = Find_Env_Files(tmp_path)
		assert findings == []

	def Test_Detects_Dot_Env(self, tmp_path):
		env_file = tmp_path / ".env"
		env_file.write_text("DB_PASSWORD=secret123")
		findings = Find_Env_Files(tmp_path)
		assert any(f.pattern_name == "env_file_in_repo" for f in findings)
		assert any(f.severity == Severity.HIGH for f in findings)

	def Test_Skips_Env_Example(self, tmp_path):
		for name in (".env.example", ".env.template", ".env.sample"):
			safe = tmp_path / name
			safe.write_text("DB_PASSWORD=")
		findings = Find_Env_Files(tmp_path)
		env_repo_findings = [f for f in findings if f.pattern_name == "env_file_in_repo"]
		assert len(env_repo_findings) == 0

	def Test_Skips_Env_In_Node_Modules(self, tmp_path):
		nm = tmp_path / "node_modules" / "some-pkg"
		nm.mkdir(parents=True)
		env_file = nm / ".env"
		env_file.write_text("SECRET=x")
		findings = Find_Env_Files(tmp_path)
		assert findings == []

	def Test_Scans_Env_Contents_For_Secrets(self, tmp_path):
		env_file = tmp_path / ".env"
		env_file.write_text("AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY")
		findings = Find_Env_Files(tmp_path)
		# Should detect both env_file_in_repo AND the AWS key pattern
		assert len(findings) >= 2


# -- Check_File_Permissions --

class Test_Check_File_Permissions:
	"""Test file permission checks on sensitive files."""

	def Test_No_Sensitive_Files(self, tmp_path):
		normal = tmp_path / "app.py"
		normal.write_text("print('hi')")
		findings = Check_File_Permissions(tmp_path)
		assert findings == []

	def Test_World_Readable_Pem(self, tmp_path):
		pem = tmp_path / "server.pem"
		pem.write_text("-----BEGIN CERTIFICATE-----")
		os.chmod(pem, 0o644)  # owner rw, group r, other r
		findings = Check_File_Permissions(tmp_path)
		assert any(
			f.pattern_name == "sensitive_file_world_readable"
			for f in findings
		)

	def Test_World_Writable_Key(self, tmp_path):
		key = tmp_path / "private.key"
		key.write_text("-----BEGIN PRIVATE KEY-----")
		os.chmod(key, 0o666)  # everyone rw
		findings = Check_File_Permissions(tmp_path)
		assert any(
			f.pattern_name == "sensitive_file_world_writable"
			and f.severity == Severity.CRITICAL
			for f in findings
		)

	def Test_Restricted_Pem_No_Findings(self, tmp_path):
		pem = tmp_path / "server.pem"
		pem.write_text("cert data")
		os.chmod(pem, 0o600)  # owner rw only
		findings = Check_File_Permissions(tmp_path)
		assert findings == []

	def Test_Sensitive_File_Names(self, tmp_path):
		"""id_rsa, id_ed25519, id_ecdsa detected by name."""
		for name in ("id_rsa", "id_ed25519", "id_ecdsa"):
			f = tmp_path / name
			f.write_text("key content")
			os.chmod(f, 0o644)
		findings = Check_File_Permissions(tmp_path)
		assert len(findings) >= 3  # one per file

	def Test_Skips_Sensitive_In_Skip_Dirs(self, tmp_path):
		venv = tmp_path / ".venv" / "lib"
		venv.mkdir(parents=True)
		pem = venv / "cert.pem"
		pem.write_text("cert")
		os.chmod(pem, 0o644)
		findings = Check_File_Permissions(tmp_path)
		assert findings == []


# -- Check_Gitignore_Coverage --

class Test_Check_Gitignore_Coverage:
	"""Test .gitignore coverage checks."""

	def Test_Missing_Gitignore_In_Git_Repo(self, tmp_path):
		"""Git repo without .gitignore should warn."""
		git_dir = tmp_path / ".git"
		git_dir.mkdir()
		findings = Check_Gitignore_Coverage(tmp_path)
		assert any(f.pattern_name == "missing_gitignore" for f in findings)
		assert any(f.severity == Severity.MEDIUM for f in findings)

	def Test_Missing_Gitignore_No_Git_No_Warning(self, tmp_path):
		"""Non-git directory without .gitignore should not warn."""
		findings = Check_Gitignore_Coverage(tmp_path)
		assert findings == []

	def Test_Complete_Gitignore_No_Findings(self, tmp_path):
		git_dir = tmp_path / ".git"
		git_dir.mkdir()
		gitignore = tmp_path / ".gitignore"
		gitignore.write_text(".env\n*.pem\n*.key\n")
		findings = Check_Gitignore_Coverage(tmp_path)
		assert findings == []

	def Test_Missing_Env_Pattern(self, tmp_path):
		git_dir = tmp_path / ".git"
		git_dir.mkdir()
		gitignore = tmp_path / ".gitignore"
		gitignore.write_text("*.pem\n*.key\n")
		findings = Check_Gitignore_Coverage(tmp_path)
		assert any(
			f.pattern_name == "gitignore_missing_pattern"
			and ".env" in f.matched_text
			for f in findings
		)

	def Test_Missing_Pem_Pattern(self, tmp_path):
		git_dir = tmp_path / ".git"
		git_dir.mkdir()
		gitignore = tmp_path / ".gitignore"
		gitignore.write_text(".env\n*.key\n")
		findings = Check_Gitignore_Coverage(tmp_path)
		assert any(
			f.pattern_name == "gitignore_missing_pattern"
			and "*.pem" in f.matched_text
			for f in findings
		)
