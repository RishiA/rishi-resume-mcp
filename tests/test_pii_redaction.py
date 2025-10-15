#!/usr/bin/env python3
"""
Automated PII Detection Tests
Ensures no phone numbers or sensitive information in resume data
"""

import re
import json
import sys
from pathlib import Path
from typing import List, Tuple, Dict


class PIIDetector:
    """Detect PII in resume files"""

    # Phone number patterns
    PHONE_PATTERNS = [
        # US phone formats
        r'(?<!\d)(?:\+?1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}(?!\d)',
        # Spaced format
        r'\d\s\d\s\d\s\d\s\d\s\d\s\d\s\d\s\d\s\d',
        # International formats
        r'\+\d{1,3}[\s.-]?\d{2,4}[\s.-]?\d{3,4}[\s.-]?\d{4}',
        # Generic 10-digit
        r'(?<!\d)\d{10}(?!\d)',
        # With extensions
        r'(?<!\d)(?:\+?1[\s.-]?)?(?:\(\d{3}\)|\d{3})[\s.-]?\d{3}[\s.-]?\d{4}(?:\s*(?:ext|x|extension)[\s.:]*\d{1,5})?(?!\d)'
    ]

    # SSN patterns (should never be in resume)
    SSN_PATTERNS = [
        r'(?<!\d)\d{3}[-\s]?\d{2}[-\s]?\d{4}(?!\d)',
        r'(?<!\d)\d{9}(?!\d)'
    ]

    # Credit card patterns (should never be in resume)
    CC_PATTERNS = [
        r'(?<!\d)\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}(?!\d)',
        r'(?<!\d)\d{16}(?!\d)'
    ]

    def __init__(self):
        self.issues_found = []

    def check_text(self, text: str, filename: str) -> List[Dict]:
        """Check text for PII patterns"""
        issues = []

        # Check for phone numbers
        for pattern in self.PHONE_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                # Filter out false positives (like years or percentages)
                real_phones = [m for m in matches if not self._is_false_positive(m)]
                if real_phones:
                    issues.append({
                        "type": "phone_number",
                        "file": filename,
                        "pattern": pattern,
                        "matches": real_phones,
                        "severity": "HIGH"
                    })

        # Check for SSN
        for pattern in self.SSN_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                # Filter out false positives
                real_ssns = [m for m in matches if self._looks_like_ssn(m)]
                if real_ssns:
                    issues.append({
                        "type": "ssn",
                        "file": filename,
                        "pattern": pattern,
                        "matches": real_ssns,
                        "severity": "CRITICAL"
                    })

        # Check for credit cards
        for pattern in self.CC_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                if any(self._luhn_check(m.replace(" ", "").replace("-", "")) for m in matches):
                    issues.append({
                        "type": "credit_card",
                        "file": filename,
                        "pattern": pattern,
                        "matches": matches,
                        "severity": "CRITICAL"
                    })

        return issues

    def _is_false_positive(self, match: str) -> bool:
        """Check if a phone pattern match is actually something else"""
        # Remove non-digits
        digits_only = re.sub(r'\D', '', match)

        # Years (1900-2099)
        if 1900 <= int(digits_only[:4]) <= 2099 and len(digits_only) == 4:
            return True

        # Percentages or metrics (like "92% accuracy")
        if len(digits_only) <= 3:
            return True

        # Version numbers
        if '.' in match and len(digits_only) <= 6:
            return True

        return False

    def _looks_like_ssn(self, match: str) -> bool:
        """Check if pattern really looks like SSN"""
        digits_only = re.sub(r'\D', '', match)
        if len(digits_only) != 9:
            return False

        # SSN rules: first 3 digits not 000, 666, or 900-999
        first_three = int(digits_only[:3])
        if first_three == 0 or first_three == 666 or first_three >= 900:
            return False

        return True

    def _luhn_check(self, number: str) -> bool:
        """Luhn algorithm to validate credit card numbers"""
        try:
            digits = [int(d) for d in number]
            checksum = 0
            for i, digit in enumerate(reversed(digits[:-1])):
                if i % 2 == 0:
                    digit *= 2
                    if digit > 9:
                        digit -= 9
                checksum += digit
            return (checksum + digits[-1]) % 10 == 0
        except:
            return False

    def check_file(self, filepath: Path) -> List[Dict]:
        """Check a file for PII"""
        try:
            if filepath.suffix == '.json':
                with open(filepath, 'r') as f:
                    # Check both raw JSON and string values
                    content = f.read()
                    issues = self.check_text(content, str(filepath))

                    # Also check parsed JSON values
                    f.seek(0)
                    data = json.load(f)
                    json_text = json.dumps(data, indent=2)
                    issues.extend(self.check_text(json_text, f"{filepath} (parsed)"))

            else:
                with open(filepath, 'r') as f:
                    content = f.read()
                    issues = self.check_text(content, str(filepath))

            return issues
        except Exception as e:
            print(f"Error checking {filepath}: {e}")
            return []

    def check_directory(self, directory: Path) -> Tuple[bool, List[Dict]]:
        """Check all relevant files in directory"""
        all_issues = []

        # Files to check
        patterns = ['*.json', '*.md', '*.py', '*.txt']
        for pattern in patterns:
            for filepath in directory.rglob(pattern):
                # Skip test files and node_modules
                if 'node_modules' in str(filepath) or '__pycache__' in str(filepath):
                    continue

                issues = self.check_file(filepath)
                all_issues.extend(issues)

        return len(all_issues) == 0, all_issues


def test_no_phone_numbers():
    """Test that no phone numbers exist in resume files"""
    detector = PIIDetector()
    project_root = Path(__file__).parent.parent

    # Check specific resume files
    resume_files = [
        project_root / "resume.md",
        project_root / "resume_data.json",
        project_root / "README.md"
    ]

    all_issues = []
    for filepath in resume_files:
        if filepath.exists():
            issues = detector.check_file(filepath)
            all_issues.extend(issues)

    # Filter to just phone numbers
    phone_issues = [i for i in all_issues if i['type'] == 'phone_number']

    if phone_issues:
        print("❌ PHONE NUMBERS DETECTED:")
        for issue in phone_issues:
            print(f"  File: {issue['file']}")
            print(f"  Matches: {issue['matches']}")
        assert False, f"Found {len(phone_issues)} phone number(s) in resume files"

    print("✅ No phone numbers detected")


def test_no_ssn():
    """Test that no SSNs exist in any files"""
    detector = PIIDetector()
    project_root = Path(__file__).parent.parent

    passed, all_issues = detector.check_directory(project_root)

    ssn_issues = [i for i in all_issues if i['type'] == 'ssn']

    if ssn_issues:
        print("❌ SSN PATTERN DETECTED:")
        for issue in ssn_issues:
            print(f"  File: {issue['file']}")
            print(f"  Matches: {issue['matches']}")
        assert False, f"Found {len(ssn_issues)} SSN pattern(s)"

    print("✅ No SSN patterns detected")


def test_no_credit_cards():
    """Test that no credit card numbers exist"""
    detector = PIIDetector()
    project_root = Path(__file__).parent.parent

    passed, all_issues = detector.check_directory(project_root)

    cc_issues = [i for i in all_issues if i['type'] == 'credit_card']

    if cc_issues:
        print("❌ CREDIT CARD PATTERN DETECTED:")
        for issue in cc_issues:
            print(f"  File: {issue['file']}")
        assert False, f"Found {len(cc_issues)} credit card pattern(s)"

    print("✅ No credit card patterns detected")


def test_email_allowed():
    """Test that email addresses ARE allowed (not PII for professional use)"""
    project_root = Path(__file__).parent.parent
    readme = project_root / "README.md"

    if readme.exists():
        with open(readme, 'r') as f:
            content = f.read()

        # Email pattern
        email_pattern = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
        matches = re.findall(email_pattern, content)

        # Note: We removed email from README, but this test shows emails are OK if present
        print(f"ℹ️  Emails are allowed. Found {len(matches)} email(s)")


def run_all_tests():
    """Run all PII detection tests"""
    print("🔍 Running PII Detection Tests")
    print("=" * 50)

    tests = [
        ("Phone Numbers", test_no_phone_numbers),
        ("SSN Patterns", test_no_ssn),
        ("Credit Cards", test_no_credit_cards),
        ("Email Policy", test_email_allowed)
    ]

    failed = []
    for test_name, test_func in tests:
        print(f"\nTesting: {test_name}")
        try:
            test_func()
        except AssertionError as e:
            failed.append((test_name, str(e)))
            print(f"  ❌ FAILED: {e}")

    print("\n" + "=" * 50)
    if failed:
        print(f"❌ {len(failed)} test(s) failed:")
        for name, error in failed:
            print(f"  - {name}: {error}")
        return False
    else:
        print("✅ All PII detection tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)