"""
Tests for the core pattern engine: patterns.py

Covers pattern compilation, Scan_Content, Format_Report,
Verify_Install_Findings, pattern groups, and enums.
"""

import re
import urllib.error
from unittest.mock import patch, MagicMock

from patterns import (
	Severity,
	Category,
	Pattern,
	Finding,
	Scan_Content,
	Format_Report,
	Verify_Install_Findings,
	Verify_Package,
	Skill_Injection_Patterns,
	Hook_Abuse_Patterns,
	Mcp_Config_Patterns,
	Instruction_Override_Patterns,
	Encoding_Obfuscation_Patterns,
	Secrets_Patterns,
	Dangerous_Call_Patterns,
	Exfiltration_Patterns,
	Supply_Chain_Patterns,
	File_Permission_Patterns,
	Vet_Repo_Patterns,
	Scan_Skill_Patterns,
	Audit_Code_Patterns,
)


# -- Pattern Compilation --

class Test_Pattern_Compilation:
	"""Verify all patterns compile without regex errors."""

	All_Groups = [
		("Skill_Injection", Skill_Injection_Patterns),
		("Hook_Abuse", Hook_Abuse_Patterns),
		("Mcp_Config", Mcp_Config_Patterns),
		("Instruction_Override", Instruction_Override_Patterns),
		("Encoding_Obfuscation", Encoding_Obfuscation_Patterns),
		("Secrets", Secrets_Patterns),
		("Dangerous_Call", Dangerous_Call_Patterns),
		("Exfiltration", Exfiltration_Patterns),
		("Supply_Chain", Supply_Chain_Patterns),
		("File_Permission", File_Permission_Patterns),
	]

	def Test_All_Individual_Patterns_Compile(self):
		"""Every pattern in every group has a compiled regex."""
		for group_name, patterns in self.All_Groups:
			for p in patterns:
				assert p.compiled is not None, (
					f"Pattern {p.name} in {group_name} failed to compile"
				)
				assert isinstance(p.compiled, re.Pattern), (
					f"Pattern {p.name} compiled field is not re.Pattern"
				)

	def Test_Vet_Repo_Patterns_Compile(self):
		for p in Vet_Repo_Patterns:
			assert p.compiled is not None, f"{p.name} failed"

	def Test_Scan_Skill_Patterns_Compile(self):
		for p in Scan_Skill_Patterns:
			assert p.compiled is not None, f"{p.name} failed"

	def Test_Audit_Code_Patterns_Compile(self):
		for p in Audit_Code_Patterns:
			assert p.compiled is not None, f"{p.name} failed"

	def Test_Pattern_Names_Are_Unique_Within_Groups(self):
		"""No duplicate pattern names within a single group."""
		for group_name, patterns in self.All_Groups:
			names = [p.name for p in patterns]
			dupes = [n for n in names if names.count(n) > 1]
			assert len(dupes) == 0, (
				f"Duplicate names in {group_name}: {set(dupes)}"
			)


# -- Pattern Groups --

class Test_Pattern_Groups:
	"""Verify composite pattern groups are properly composed."""

	def Test_Vet_Repo_Patterns_Non_Empty(self):
		assert len(Vet_Repo_Patterns) > 0

	def Test_Scan_Skill_Patterns_Non_Empty(self):
		assert len(Scan_Skill_Patterns) > 0

	def Test_Audit_Code_Patterns_Non_Empty(self):
		assert len(Audit_Code_Patterns) > 0

	def Test_All_Elements_Are_Pattern_Instances(self):
		for p in Vet_Repo_Patterns:
			assert isinstance(p, Pattern)
		for p in Scan_Skill_Patterns:
			assert isinstance(p, Pattern)
		for p in Audit_Code_Patterns:
			assert isinstance(p, Pattern)

	def Test_Composite_Groups_Contain_Expected_Categories(self):
		"""Each composite group includes its expected pattern categories."""
		vet_categories = {p.category for p in Vet_Repo_Patterns}
		assert Category.SKILL_INJECTION in vet_categories
		assert Category.HOOK_ABUSE in vet_categories
		assert Category.MCP_CONFIG in vet_categories

		scan_categories = {p.category for p in Scan_Skill_Patterns}
		assert Category.SKILL_INJECTION in scan_categories
		assert Category.DANGEROUS_CALLS in scan_categories
		assert Category.SUPPLY_CHAIN in scan_categories

		audit_categories = {p.category for p in Audit_Code_Patterns}
		assert Category.SECRETS in audit_categories
		assert Category.DANGEROUS_CALLS in audit_categories
		assert Category.EXFILTRATION in audit_categories


# -- Enums --

class Test_Enums:
	"""Verify enum values exist."""

	def Test_Severity_Values(self):
		assert Severity.CRITICAL.value == "CRITICAL"
		assert Severity.HIGH.value == "HIGH"
		assert Severity.MEDIUM.value == "MEDIUM"
		assert Severity.LOW.value == "LOW"
		assert Severity.INFO.value == "INFO"
		assert len(Severity) == 5

	def Test_Category_Values(self):
		expected = {
			"skill_injection", "hook_abuse", "mcp_config", "secrets",
			"dangerous_calls", "exfiltration", "encoding_obfuscation",
			"instruction_override", "supply_chain", "file_permissions",
			"code_before_review", "config_backdoor", "memory_corruption",
			"confused_delegation", "persistence",
		}
		actual = {c.value for c in Category}
		assert actual == expected


# -- Scan_Content --

class Test_Scan_Content:
	"""Test the core scanning function."""

	Simple_Pattern = [Pattern(
		name="test_eval",
		pattern=r"\beval\s*\(",
		severity=Severity.HIGH,
		description="eval() call detected",
		category=Category.DANGEROUS_CALLS,
	)]

	def Test_Empty_Content_Returns_Empty(self):
		findings = Scan_Content("", self.Simple_Pattern, "test.py")
		assert findings == []

	def Test_No_Match_Returns_Empty(self):
		findings = Scan_Content("print('hello')", self.Simple_Pattern, "test.py")
		assert findings == []

	def Test_Single_Match(self):
		findings = Scan_Content("x = eval(input())", self.Simple_Pattern, "test.py")
		assert len(findings) == 1
		assert findings[0].pattern_name == "test_eval"
		assert findings[0].severity == Severity.HIGH
		assert findings[0].category == Category.DANGEROUS_CALLS
		assert findings[0].file_path == "test.py"
		assert findings[0].line_number == 1

	def Test_Multiple_Lines_Correct_Line_Numbers(self):
		content = "line1\nline2\nresult = eval(data)\nline4"
		findings = Scan_Content(content, self.Simple_Pattern, "test.py")
		assert len(findings) == 1
		assert findings[0].line_number == 3

	def Test_Multiple_Matches(self):
		content = "eval(a)\nprint(b)\neval(c)"
		findings = Scan_Content(content, self.Simple_Pattern, "test.py")
		assert len(findings) == 2
		assert findings[0].line_number == 1
		assert findings[1].line_number == 3

	def Test_Matched_Text_Truncated_At_200(self):
		long_pattern = [Pattern(
			name="long_match",
			pattern=r"x+",
			severity=Severity.LOW,
			description="many x's",
			category=Category.DANGEROUS_CALLS,
		)]
		content = "x" * 300
		findings = Scan_Content(content, long_pattern, "test.py")
		assert len(findings) == 1
		assert len(findings[0].matched_text) <= 203  # 200 + "..."
		assert findings[0].matched_text.endswith("...")

	def Test_Context_Lines(self):
		content = "line1\nline2\neval(x)\nline4\nline5"
		findings = Scan_Content(content, self.Simple_Pattern, "test.py", context_lines=1)
		assert len(findings) == 1
		assert "line2" in findings[0].context
		assert "line4" in findings[0].context

	def Test_Case_Insensitive_Matching(self):
		content = "EVAL(x)"
		findings = Scan_Content(content, self.Simple_Pattern, "test.py")
		assert len(findings) == 1


# -- Format_Report --

class Test_Format_Report:
	"""Test report formatting."""

	def Test_No_Findings(self):
		report = Format_Report("test-skill", "/some/path", [])
		assert "No security issues detected" in report or "0 findings" in report.lower()

	def Test_Single_Finding_Included(self):
		findings = [Finding(
			pattern_name="test_pattern",
			severity=Severity.CRITICAL,
			category=Category.SECRETS,
			description="Found a secret",
			file_path="config.py",
			line_number=42,
			matched_text="AKIA1234567890",
		)]
		report = Format_Report("audit-code", "/project", findings)
		assert "CRITICAL" in report
		assert "test_pattern" in report
		assert "config.py" in report

	def Test_Severity_Ordering(self):
		"""CRITICAL findings appear before LOW findings in the report."""
		findings = [
			Finding("low_pat", Severity.LOW, Category.SECRETS, "low", "a.py", 1, "x"),
			Finding("crit_pat", Severity.CRITICAL, Category.SECRETS, "crit", "b.py", 2, "y"),
		]
		report = Format_Report("test", "/path", findings)
		crit_pos = report.find("CRITICAL")
		low_pos = report.find("LOW")
		assert crit_pos < low_pos, "CRITICAL should appear before LOW in report"

	def Test_Report_Contains_Title(self):
		report = Format_Report("vet-repo", "/repo", [])
		assert "vet-repo" in report


# -- Verify_Install_Findings --

class Test_Verify_Install_Findings:
	"""Test package verification with mocked network calls."""

	def _Make_Install_Finding(self, pattern_name: str, matched_text: str) -> Finding:
		return Finding(
			pattern_name=pattern_name,
			severity=Severity.INFO,
			category=Category.SUPPLY_CHAIN,
			description="Unknown package install",
			file_path="test.md",
			line_number=1,
			matched_text=matched_text,
		)

	def Test_No_Install_Findings_Passthrough(self):
		"""Non-install findings pass through unchanged."""
		findings = [Finding(
			pattern_name="eval_call",
			severity=Severity.HIGH,
			category=Category.DANGEROUS_CALLS,
			description="eval",
			file_path="test.py",
			line_number=1,
			matched_text="eval(x)",
		)]
		result = Verify_Install_Findings(findings)
		assert len(result) == 1
		assert result[0].pattern_name == "eval_call"

	@patch("patterns.Verify_Package")
	def Test_Package_Not_Found_Promotes_To_Critical(self, Mock_Verify):
		Mock_Verify.return_value = {
			"exists": False,
			"name": "nonexistent-pkg",
			"details": "Package does not exist on registry",
		}
		findings = [self._Make_Install_Finding("pip_install_unknown", "pip install nonexistent-pkg")]
		result = Verify_Install_Findings(findings)
		assert len(result) == 1
		assert result[0].severity == Severity.CRITICAL
		assert result[0].pattern_name == "package_not_found"

	@patch("patterns.Verify_Package")
	def Test_Package_Exists_Removes_Finding(self, Mock_Verify):
		Mock_Verify.return_value = {
			"exists": True,
			"name": "requests",
			"details": "v2.31.0 -- Python HTTP for Humans.",
		}
		findings = [self._Make_Install_Finding("pip_install_unknown", "pip install requests")]
		result = Verify_Install_Findings(findings)
		assert len(result) == 0

	@patch("patterns.Verify_Package")
	def Test_Network_Error_Produces_Medium(self, Mock_Verify):
		Mock_Verify.return_value = {
			"exists": None,
			"name": "some-pkg",
			"details": "ConnectionError: timed out",
		}
		findings = [self._Make_Install_Finding("pip_install_unknown", "pip install some-pkg")]
		result = Verify_Install_Findings(findings)
		assert len(result) == 1
		assert result[0].severity == Severity.MEDIUM
		assert result[0].pattern_name == "package_unverified"

	@patch("patterns.Verify_Package")
	def Test_Npm_Install_Finding(self, Mock_Verify):
		Mock_Verify.return_value = {
			"exists": False,
			"name": "react-codeshift",
			"details": "Package does not exist on registry",
		}
		findings = [self._Make_Install_Finding("npm_install_unknown", "npm install react-codeshift")]
		result = Verify_Install_Findings(findings)
		assert len(result) == 1
		assert result[0].severity == Severity.CRITICAL
		Mock_Verify.assert_called_once_with("npm", "react-codeshift")

	def Test_Mixed_Findings_Preserved(self):
		"""Non-install findings survive alongside install findings."""
		non_install = Finding(
			pattern_name="eval_call",
			severity=Severity.HIGH,
			category=Category.DANGEROUS_CALLS,
			description="eval",
			file_path="test.py",
			line_number=1,
			matched_text="eval(x)",
		)
		install = self._Make_Install_Finding("pip_install_unknown", "pip install requests")

		with patch("patterns.Verify_Package") as Mock_Verify:
			Mock_Verify.return_value = {"exists": True, "name": "requests", "details": "v2.31.0"}
			result = Verify_Install_Findings([non_install, install])

		assert len(result) == 1
		assert result[0].pattern_name == "eval_call"


# -- Finding Dataclass --

class Test_Finding_Dataclass:
	"""Verify Finding construction and fields."""

	def Test_Required_Fields(self):
		f = Finding(
			pattern_name="test",
			severity=Severity.HIGH,
			category=Category.SECRETS,
			description="desc",
			file_path="file.py",
			line_number=10,
			matched_text="match",
		)
		assert f.pattern_name == "test"
		assert f.context == ""  # default

	def Test_Optional_Context(self):
		f = Finding(
			pattern_name="test",
			severity=Severity.LOW,
			category=Category.SECRETS,
			description="desc",
			file_path="file.py",
			line_number=1,
			matched_text="m",
			context="surrounding code",
		)
		assert f.context == "surrounding code"


# -- Pattern Dataclass --

class Test_Pattern_Dataclass:
	"""Verify Pattern construction and auto-compilation."""

	def Test_Auto_Compiles(self):
		p = Pattern(
			name="test",
			pattern=r"\bfoo\b",
			severity=Severity.LOW,
			description="test",
			category=Category.SECRETS,
		)
		assert p.compiled is not None
		assert p.compiled.search("foo bar") is not None

	def Test_Case_Insensitive(self):
		p = Pattern(
			name="test",
			pattern=r"secret",
			severity=Severity.HIGH,
			description="test",
			category=Category.SECRETS,
		)
		assert p.compiled.search("SECRET") is not None
		assert p.compiled.search("Secret") is not None
