#!/usr/bin/env bash
# Security Verification Script for Resume MCP Server
# Checks dependencies, PII, and generates SBOM

set -euo pipefail

echo "🔒 Security Verification for Resume MCP Server"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
SECURITY_PASSED=true

# 1. Check Python dependencies for vulnerabilities
echo "1️⃣  Checking Python dependencies..."
if command -v pip-audit &> /dev/null; then
    echo "   Running pip-audit..."
    pip-audit || {
        echo -e "${YELLOW}   ⚠️  Some vulnerabilities found in dependencies${NC}"
        SECURITY_PASSED=false
    }
else
    echo "   Installing pip-audit..."
    pip install pip-audit --quiet
    pip-audit || {
        echo -e "${YELLOW}   ⚠️  Some vulnerabilities found in dependencies${NC}"
        SECURITY_PASSED=false
    }
fi
echo ""

# 2. Run PII detection tests
echo "2️⃣  Running PII detection tests..."
if [ -f "tests/test_pii_redaction.py" ]; then
    python tests/test_pii_redaction.py || {
        echo -e "${RED}   ❌ PII detected in files!${NC}"
        SECURITY_PASSED=false
    }
else
    echo -e "${YELLOW}   ⚠️  PII test file not found${NC}"
fi
echo ""

# 3. Check file permissions
echo "3️⃣  Checking file permissions..."
SENSITIVE_FILES=(
    "resume_data.json"
    "config/claude_desktop_config.json"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        perms=$(stat -f "%A" "$file" 2>/dev/null || stat -c "%a" "$file" 2>/dev/null || echo "unknown")
        if [ "$perms" != "unknown" ] && [ "$perms" -gt 644 ]; then
            echo -e "${YELLOW}   ⚠️  $file has overly permissive permissions: $perms${NC}"
            echo "      Recommended: chmod 644 $file"
            SECURITY_PASSED=false
        else
            echo -e "${GREEN}   ✅ $file permissions OK: $perms${NC}"
        fi
    fi
done
echo ""

# 4. Check for secrets in code
echo "4️⃣  Scanning for hardcoded secrets..."
SECRET_PATTERNS=(
    "api[_-]?key"
    "secret[_-]?key"
    "access[_-]?token"
    "private[_-]?key"
    "password"
    "passwd"
    "pwd"
)

FOUND_SECRETS=false
for pattern in "${SECRET_PATTERNS[@]}"; do
    # Search in Python files, excluding comments
    matches=$(grep -r -i "$pattern" --include="*.py" . 2>/dev/null | grep -v "^#" | grep -v "test" || true)
    if [ ! -z "$matches" ]; then
        # Check if it's a real secret (contains = with a value)
        if echo "$matches" | grep -E "=\s*['\"][^'\"]+['\"]" > /dev/null; then
            echo -e "${RED}   ❌ Potential secret found with pattern: $pattern${NC}"
            FOUND_SECRETS=true
        fi
    fi
done

if [ "$FOUND_SECRETS" = true ]; then
    SECURITY_PASSED=false
else
    echo -e "${GREEN}   ✅ No hardcoded secrets detected${NC}"
fi
echo ""

# 5. Generate Software Bill of Materials (SBOM)
echo "5️⃣  Generating Software Bill of Materials (SBOM)..."
if command -v pip-licenses &> /dev/null; then
    pip-licenses --format=json > sbom.json 2>/dev/null && \
        echo -e "${GREEN}   ✅ SBOM generated: sbom.json${NC}" || \
        echo -e "${YELLOW}   ⚠️  Could not generate SBOM${NC}"
else
    pip install pip-licenses --quiet
    pip-licenses --format=json > sbom.json 2>/dev/null && \
        echo -e "${GREEN}   ✅ SBOM generated: sbom.json${NC}" || \
        echo -e "${YELLOW}   ⚠️  Could not generate SBOM${NC}"
fi
echo ""

# 6. Check for unsafe file operations
echo "6️⃣  Checking for unsafe file operations..."
UNSAFE_PATTERNS=(
    "exec("
    "eval("
    "compile("
    "__import__"
    "os.system"
    "subprocess.call"
    "shell=True"
)

FOUND_UNSAFE=false
for pattern in "${UNSAFE_PATTERNS[@]}"; do
    matches=$(grep -r "$pattern" --include="*.py" . 2>/dev/null | grep -v "test" | grep -v "#" || true)
    if [ ! -z "$matches" ]; then
        echo -e "${YELLOW}   ⚠️  Potentially unsafe operation found: $pattern${NC}"
        FOUND_UNSAFE=true
    fi
done

if [ "$FOUND_UNSAFE" = false ]; then
    echo -e "${GREEN}   ✅ No unsafe operations detected${NC}"
fi
echo ""

# 7. Verify requirements.txt is pinned
echo "7️⃣  Checking dependency pinning..."
if [ -f "requirements.txt" ]; then
    unpinned=$(grep -E "^[^#].*[><=]" requirements.txt | grep -v "==" || true)
    if [ ! -z "$unpinned" ]; then
        echo -e "${YELLOW}   ⚠️  Unpinned dependencies found:${NC}"
        echo "$unpinned"
        echo "      Recommendation: Pin all dependencies with =="
    else
        echo -e "${GREEN}   ✅ All dependencies are pinned${NC}"
    fi
else
    echo -e "${YELLOW}   ⚠️  requirements.txt not found${NC}"
fi
echo ""

# 8. Calculate file hashes for integrity
echo "8️⃣  Calculating file integrity hashes..."
CRITICAL_FILES=(
    "server.py"
    "resume_data.json"
    "requirements.txt"
)

echo "   SHA256 Checksums:" > integrity.txt
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        if command -v sha256sum &> /dev/null; then
            hash=$(sha256sum "$file" | cut -d' ' -f1)
        else
            hash=$(shasum -a 256 "$file" | cut -d' ' -f1)
        fi
        echo "   $file: $hash" | tee -a integrity.txt
    fi
done
echo -e "${GREEN}   ✅ Integrity hashes saved to integrity.txt${NC}"
echo ""

# 9. Check for network calls
echo "9️⃣  Checking for outbound network calls..."
NETWORK_PATTERNS=(
    "requests.get"
    "requests.post"
    "urllib"
    "httpx"
    "aiohttp"
    "socket"
)

FOUND_NETWORK=false
for pattern in "${NETWORK_PATTERNS[@]}"; do
    matches=$(grep -r "$pattern" --include="*.py" . 2>/dev/null | grep -v "test" | grep -v "#" || true)
    if [ ! -z "$matches" ]; then
        echo -e "${YELLOW}   ⚠️  Network operation found: $pattern${NC}"
        FOUND_NETWORK=true
    fi
done

if [ "$FOUND_NETWORK" = false ]; then
    echo -e "${GREEN}   ✅ No outbound network calls detected (local-only)${NC}"
fi
echo ""

# 10. Summary
echo "=============================================="
echo "📊 SECURITY VERIFICATION SUMMARY"
echo "=============================================="

if [ "$SECURITY_PASSED" = true ] && [ "$FOUND_UNSAFE" = false ] && [ "$FOUND_NETWORK" = false ]; then
    echo -e "${GREEN}✅ All security checks passed!${NC}"
    echo ""
    echo "Your resume MCP server is:"
    echo "  • Free of PII (phone numbers)"
    echo "  • Using secure file permissions"
    echo "  • Free of hardcoded secrets"
    echo "  • Local-only (no network calls)"
    echo "  • Using safe operations"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some security considerations found${NC}"
    echo ""
    echo "Recommendations:"
    echo "  1. Run 'python tests/test_pii_redaction.py' to check PII"
    echo "  2. Review and fix any permission issues"
    echo "  3. Pin all dependencies in requirements.txt"
    echo "  4. Remove any hardcoded secrets"
    echo "  5. Consider the security implications of network calls"
    exit 1
fi