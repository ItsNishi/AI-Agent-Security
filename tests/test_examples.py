"""
Integration tests: run pattern engine against examples/ directory fixtures.

Validates that malicious examples trigger expected findings and
clean examples produce minimal/no critical findings.

Note: Example files describe attack techniques in prose and code blocks.
Patterns will match text inside documentation (expected self-detection).
Tests assert on minimum expected findings and specific pattern names,
not exact counts.
"""

import sys
from pathlib import Path

import pytest

from conftest import Scan_Skill_Scripts
sys.path.insert(0, str(Scan_Skill_Scripts))

from scan_skill import Check_Html_Comments

from patterns import (
	Severity,
	Category,
	Scan_Content,
	Skill_Injection_Patterns,
	Scan_Skill_Patterns,
	Mcp_Config_Patterns,
	Exfiltration_Patterns,
	Instruction_Override_Patterns,
	Encoding_Obfuscation_Patterns,
	Audit_Code_Patterns,
)


# -- Example 01: Hidden Comment Injection --

class Test_Example_01_Hidden_Comment_Injection:
	"""Validate detection of hidden HTML comment injection."""

	@pytest.fixture
	def Malicious_Content(self, Examples_Dir) -> str:
		path = Examples_Dir / "01_Hidden_Comment_Injection" / "malicious_skill.md"
		return path.read_text(encoding="utf-8")

	@pytest.fixture
	def Sanitized_Content(self, Examples_Dir) -> str:
		path = Examples_Dir / "01_Hidden_Comment_Injection" / "sanitized_skill.md"
		return path.read_text(encoding="utf-8")

	def Test_Malicious_Triggers_Critical(self, Malicious_Content):
		"""Malicious skill must trigger at least one CRITICAL finding."""
		findings = Scan_Content(
			Malicious_Content, Skill_Injection_Patterns, "malicious_skill.md"
		)
		critical = [f for f in findings if f.severity == Severity.CRITICAL]
		assert len(critical) > 0, "Malicious skill should trigger CRITICAL findings"

	def Test_Malicious_Detects_Html_Comment(self, Malicious_Content):
		"""Must detect HTML comment with shell commands."""
		findings = Scan_Content(
			Malicious_Content, Skill_Injection_Patterns, "malicious_skill.md"
		)
		names = {f.pattern_name for f in findings}
		assert "html_comment_with_commands" in names

	def Test_Malicious_Detects_Pipe_To_Shell(self, Malicious_Content):
		"""Must detect curl | bash pattern."""
		findings = Scan_Content(
			Malicious_Content, Skill_Injection_Patterns, "malicious_skill.md"
		)
		names = {f.pattern_name for f in findings}
		assert "pipe_to_shell" in names

	def Test_Malicious_Detects_Persistence_Trigger(self, Malicious_Content):
		"""Must detect 'ALWAYS run this' persistence trigger."""
		findings = Scan_Content(
			Malicious_Content, Skill_Injection_Patterns, "malicious_skill.md"
		)
		names = {f.pattern_name for f in findings}
		assert "persistence_trigger_always" in names

	def Test_Malicious_Html_Comment_Analysis(self, Malicious_Content):
		"""Check_Html_Comments should find imperative/command patterns."""
		findings = Check_Html_Comments(Malicious_Content, "malicious_skill.md")
		assert len(findings) > 0
		assert all(f.severity == Severity.CRITICAL for f in findings)

	def Test_Sanitized_No_Critical_Injection(self, Sanitized_Content):
		"""Sanitized skill should have zero CRITICAL injection findings.

		Note: The sanitized file references 'curl | bash' in a comparison table
		describing the malicious version. pipe_to_shell matches this documentation
		reference. We exclude it since the match is in prose, not a payload.
		"""
		findings = Scan_Content(
			Sanitized_Content, Skill_Injection_Patterns, "sanitized_skill.md"
		)
		# Filter out documentation self-references (comparison table on line 78)
		payload_critical = [
			f for f in findings
			if f.severity == Severity.CRITICAL
			and f.pattern_name != "pipe_to_shell"
		]
		assert len(payload_critical) == 0, (
			f"Sanitized skill should not trigger CRITICAL injection findings "
			f"(excluding documentation references), "
			f"but got: {[f.pattern_name for f in payload_critical]}"
		)

	def Test_Sanitized_No_Html_Comments(self, Sanitized_Content):
		"""Sanitized skill should have no hidden HTML comment findings."""
		findings = Check_Html_Comments(Sanitized_Content, "sanitized_skill.md")
		assert findings == []


# -- Example 02: Indirect Prompt Injection --

class Test_Example_02_Indirect_Prompt_Injection:
	"""Validate detection of indirect prompt injection payloads."""

	@pytest.fixture
	def Content(self, Examples_Dir) -> str:
		path = Examples_Dir / "02_Indirect_Prompt_Injection" / "examples.md"
		return path.read_text(encoding="utf-8")

	def Test_Detects_Html_Comment_Injection(self, Content):
		findings = Scan_Content(Content, Skill_Injection_Patterns, "examples.md")
		names = {f.pattern_name for f in findings}
		assert "html_comment_with_commands" in names

	def Test_Detects_Injection_Patterns_Broadly(self, Content):
		"""Should detect injection-related patterns in the examples."""
		# Example 02 uses [INJECTED] markers and hidden HTML comments,
		# not literal "ignore previous instructions" phrases.
		# Test with the broader Scan_Skill_Patterns composite.
		findings = Scan_Content(Content, Scan_Skill_Patterns, "examples.md")
		names = {f.pattern_name for f in findings}
		# Should detect HTML comment injection and supply chain patterns
		assert len(findings) > 0
		assert "html_comment_with_commands" in names

	def Test_Has_Critical_Findings(self, Content):
		findings = Scan_Content(Content, Scan_Skill_Patterns, "examples.md")
		critical = [f for f in findings if f.severity == Severity.CRITICAL]
		assert len(critical) > 0


# -- Example 03: Data Exfiltration Via Agent --

class Test_Example_03_Data_Exfiltration:
	"""Validate detection of data exfiltration patterns."""

	@pytest.fixture
	def Content(self, Examples_Dir) -> str:
		path = Examples_Dir / "03_Data_Exfiltration_Via_Agent" / "examples.md"
		return path.read_text(encoding="utf-8")

	def Test_Detects_Html_Comment_Injection(self, Content):
		findings = Scan_Content(Content, Skill_Injection_Patterns, "examples.md")
		names = {f.pattern_name for f in findings}
		assert "html_comment_with_commands" in names

	def Test_Detects_Exfiltration_Patterns(self, Content):
		findings = Scan_Content(Content, Exfiltration_Patterns, "examples.md")
		assert len(findings) > 0
		names = {f.pattern_name for f in findings}
		# Should detect at least some exfiltration indicators
		exfil_patterns = {
			"sensitive_file_read", "credential_path_access",
			"markdown_image_exfil", "env_dump",
			"curl_post_sensitive_file", "dns_exfiltration",
		}
		detected = names & exfil_patterns
		assert len(detected) > 0, (
			f"Expected at least one exfiltration pattern, got: {names}"
		)

	def Test_Has_Critical_Findings(self, Content):
		findings = Scan_Content(Content, Scan_Skill_Patterns, "examples.md")
		critical = [f for f in findings if f.severity == Severity.CRITICAL]
		assert len(critical) > 0


# -- Example 04: Hallucinated Package Skill Injection --

class Test_Example_04_Hallucinated_Package:
	"""Validate detection of hallucinated package references."""

	@pytest.fixture
	def Content(self, Examples_Dir) -> str:
		path = Examples_Dir / "04_Hallucinated_Package_Skill_Injection" / "README.md"
		return path.read_text(encoding="utf-8")

	def Test_Has_Findings(self, Content):
		"""README documents the attack -- patterns should match references."""
		findings = Scan_Content(Content, Scan_Skill_Patterns, "README.md")
		assert len(findings) > 0

	def Test_No_False_Pipe_To_Shell(self, Content):
		"""Example 04 has no curl|bash -- pipe_to_shell should not match."""
		findings = Scan_Content(Content, Skill_Injection_Patterns, "README.md")
		names = {f.pattern_name for f in findings}
		assert "pipe_to_shell" not in names


# -- Example 05: MCP Tool Poisoning --

class Test_Example_05_MCP_Tool_Poisoning:
	"""Validate detection of MCP tool description poisoning."""

	@pytest.fixture
	def Server_Config(self, Examples_Dir) -> str:
		path = Examples_Dir / "05_MCP_Tool_Poisoning" / "malicious_server.json"
		return path.read_text(encoding="utf-8")

	@pytest.fixture
	def Detection_Doc(self, Examples_Dir) -> str:
		path = Examples_Dir / "05_MCP_Tool_Poisoning" / "detection.md"
		return path.read_text(encoding="utf-8")

	def Test_Server_Config_Triggers_Mcp_Patterns(self, Server_Config):
		findings = Scan_Content(Server_Config, Mcp_Config_Patterns, "malicious_server.json")
		assert len(findings) > 0

	def Test_Server_Config_Detects_Description_Injection(self, Server_Config):
		findings = Scan_Content(
			Server_Config,
			Mcp_Config_Patterns + Instruction_Override_Patterns,
			"malicious_server.json",
		)
		names = {f.pattern_name for f in findings}
		# Should detect description injection or instruction override
		assert len(names) > 0

	def Test_Server_Config_Detects_Exfiltration_Indicators(self, Server_Config):
		findings = Scan_Content(Server_Config, Exfiltration_Patterns, "malicious_server.json")
		assert len(findings) > 0
		names = {f.pattern_name for f in findings}
		# Should detect sensitive path access and/or env dump patterns
		exfil_patterns = {
			"credential_path_access", "env_dump",
			"curl_post_sensitive_file", "sensitive_file_read",
		}
		detected = names & exfil_patterns
		assert len(detected) > 0, (
			f"Expected exfiltration patterns in MCP config, got: {names}"
		)

	def Test_Server_Config_Has_High_Or_Above_Findings(self, Server_Config):
		"""MCP config should trigger at least HIGH findings.

		The malicious JSON uses defanged URLs and natural language descriptions
		rather than literal attack commands, so patterns match at HIGH/MEDIUM
		(mcp_overly_broad_tools, credential_path_access) rather than CRITICAL.
		"""
		all_patterns = (
			Mcp_Config_Patterns
			+ Instruction_Override_Patterns
			+ Exfiltration_Patterns
			+ Encoding_Obfuscation_Patterns
		)
		findings = Scan_Content(Server_Config, all_patterns, "malicious_server.json")
		high_or_above = [
			f for f in findings
			if f.severity in (Severity.CRITICAL, Severity.HIGH)
		]
		assert len(high_or_above) > 0, (
			f"MCP config should trigger HIGH+ findings, got: "
			f"{[(f.pattern_name, f.severity.value) for f in findings]}"
		)

	def Test_Detection_Doc_Has_Findings(self, Detection_Doc):
		"""The detection doc describes attacks -- patterns should self-detect."""
		findings = Scan_Content(Detection_Doc, Scan_Skill_Patterns, "detection.md")
		assert len(findings) > 0


# -- Cross-Example: Severity Distribution --

class Test_Example_Severity_Distribution:
	"""Validate that malicious examples produce higher severity than clean examples."""

	def Test_Malicious_Vs_Sanitized_Severity_Gap(self, Examples_Dir):
		"""Malicious example should have more CRITICAL findings than sanitized."""
		malicious = (
			Examples_Dir / "01_Hidden_Comment_Injection" / "malicious_skill.md"
		).read_text(encoding="utf-8")
		sanitized = (
			Examples_Dir / "01_Hidden_Comment_Injection" / "sanitized_skill.md"
		).read_text(encoding="utf-8")

		mal_findings = Scan_Content(malicious, Skill_Injection_Patterns, "malicious.md")
		san_findings = Scan_Content(sanitized, Skill_Injection_Patterns, "sanitized.md")

		mal_critical = len([f for f in mal_findings if f.severity == Severity.CRITICAL])
		san_critical = len([f for f in san_findings if f.severity == Severity.CRITICAL])

		assert mal_critical > san_critical, (
			f"Malicious ({mal_critical} CRITICAL) should exceed "
			f"sanitized ({san_critical} CRITICAL)"
		)
