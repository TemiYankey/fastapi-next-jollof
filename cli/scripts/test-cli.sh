#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧪 Testing create-jollof-app CLI${NC}\n"

# Create temp directory for test
TEST_DIR="/tmp/test-jollof-cli-$$"
mkdir -p "$TEST_DIR"
cd "$TEST_DIR"

echo -e "${YELLOW}📁 Test directory: $TEST_DIR${NC}\n"

# Build CLI
CLI_DIR="/Users/engryankey/Desktop/Work/APPS/fastapi-next-jollof/cli"
echo -e "${YELLOW}🔨 Building CLI...${NC}"
cd "$CLI_DIR"
npm run build > /dev/null 2>&1
echo -e "${GREEN}✓ CLI built successfully${NC}\n"

# Test 1: Generate with Stripe + Resend
echo -e "${YELLOW}Test 1: Stripe + Resend${NC}"
TEST1_DIR="$TEST_DIR/test1"
mkdir -p "$TEST1_DIR"
cd "$TEST1_DIR"

node "$CLI_DIR/dist/index.js" \
  -t blue \
  -p stripe \
  -e resend \
  --no-git \
  --no-install \
  test-stripe-resend 2>/dev/null || true

# Verify Stripe + Resend
if [ -f "$TEST1_DIR/test-stripe-resend/backend/app/billing/providers/stripe.py" ] && \
   [ ! -f "$TEST1_DIR/test-stripe-resend/backend/app/billing/providers/nomba.py" ] && \
   [ ! -f "$TEST1_DIR/test-stripe-resend/backend/app/billing/providers/paystack.py" ] && \
   [ -f "$TEST1_DIR/test-stripe-resend/backend/app/emails/providers/resend.py" ] && \
   [ ! -f "$TEST1_DIR/test-stripe-resend/backend/app/emails/providers/brevo.py" ]; then
  echo -e "${GREEN}✓ Test 1 passed: Only Stripe and Resend files present${NC}"
else
  echo -e "${RED}✗ Test 1 failed: Wrong provider files${NC}"
  ls -la "$TEST1_DIR/test-stripe-resend/backend/app/billing/providers/" 2>/dev/null || echo "Billing providers dir not found"
  ls -la "$TEST1_DIR/test-stripe-resend/backend/app/emails/providers/" 2>/dev/null || echo "Email providers dir not found"
  exit 1
fi

# Check config.py only has stripe and resend
if grep -q "stripe_secret_key" "$TEST1_DIR/test-stripe-resend/backend/app/core/config.py" && \
   grep -q "resend_api_key" "$TEST1_DIR/test-stripe-resend/backend/app/core/config.py" && \
   ! grep -q "nomba" "$TEST1_DIR/test-stripe-resend/backend/app/core/config.py" && \
   ! grep -q "paystack" "$TEST1_DIR/test-stripe-resend/backend/app/core/config.py" && \
   ! grep -q "brevo" "$TEST1_DIR/test-stripe-resend/backend/app/core/config.py"; then
  echo -e "${GREEN}✓ Test 1 config.py: Only Stripe and Resend config${NC}"
else
  echo -e "${RED}✗ Test 1 config.py: Wrong config entries${NC}"
  exit 1
fi

# Test 2: Generate with Nomba + Brevo
echo -e "\n${YELLOW}Test 2: Nomba + Brevo${NC}"
TEST2_DIR="$TEST_DIR/test2"
mkdir -p "$TEST2_DIR"
cd "$TEST2_DIR"

node "$CLI_DIR/dist/index.js" \
  -t emerald \
  -p nomba \
  -e brevo \
  --no-git \
  --no-install \
  test-nomba-brevo 2>/dev/null || true

# Verify Nomba + Brevo
if [ -f "$TEST2_DIR/test-nomba-brevo/backend/app/billing/providers/nomba.py" ] && \
   [ ! -f "$TEST2_DIR/test-nomba-brevo/backend/app/billing/providers/stripe.py" ] && \
   [ ! -f "$TEST2_DIR/test-nomba-brevo/backend/app/billing/providers/paystack.py" ] && \
   [ -f "$TEST2_DIR/test-nomba-brevo/backend/app/emails/providers/brevo.py" ] && \
   [ ! -f "$TEST2_DIR/test-nomba-brevo/backend/app/emails/providers/resend.py" ]; then
  echo -e "${GREEN}✓ Test 2 passed: Only Nomba and Brevo files present${NC}"
else
  echo -e "${RED}✗ Test 2 failed: Wrong provider files${NC}"
  exit 1
fi

# Check email service only imports brevo
if grep -q "BrevoProvider" "$TEST2_DIR/test-nomba-brevo/backend/app/emails/service.py" && \
   ! grep -q "ResendProvider" "$TEST2_DIR/test-nomba-brevo/backend/app/emails/service.py"; then
  echo -e "${GREEN}✓ Test 2 email service: Only Brevo import${NC}"
else
  echo -e "${RED}✗ Test 2 email service: Wrong imports${NC}"
  exit 1
fi

# Test 3: Generate with Paystack + No Email
echo -e "\n${YELLOW}Test 3: Paystack + No Email${NC}"
TEST3_DIR="$TEST_DIR/test3"
mkdir -p "$TEST3_DIR"
cd "$TEST3_DIR"

node "$CLI_DIR/dist/index.js" \
  -t orange \
  -p paystack \
  -e none \
  --no-git \
  --no-install \
  test-paystack 2>/dev/null || true

# Verify Paystack + No email
if [ -f "$TEST3_DIR/test-paystack/backend/app/billing/providers/paystack.py" ] && \
   [ ! -f "$TEST3_DIR/test-paystack/backend/app/billing/providers/stripe.py" ] && \
   [ ! -f "$TEST3_DIR/test-paystack/backend/app/billing/providers/nomba.py" ] && \
   [ ! -f "$TEST3_DIR/test-paystack/backend/app/emails/providers/resend.py" ] && \
   [ ! -f "$TEST3_DIR/test-paystack/backend/app/emails/providers/brevo.py" ]; then
  echo -e "${GREEN}✓ Test 3 passed: Only Paystack, no email providers${NC}"
else
  echo -e "${RED}✗ Test 3 failed: Wrong provider files${NC}"
  exit 1
fi

# Check requirements.txt has no stripe (paystack uses httpx, not SDK)
if ! grep -q "stripe" "$TEST3_DIR/test-paystack/backend/requirements.txt"; then
  echo -e "${GREEN}✓ Test 3 requirements.txt: No unnecessary Stripe package${NC}"
else
  echo -e "${RED}✗ Test 3 requirements.txt: Stripe should not be present for Paystack${NC}"
  exit 1
fi

# Test 4: Verify Python syntax in generated files
echo -e "\n${YELLOW}Test 4: Python Syntax Validation${NC}"
cd "$TEST1_DIR/test-stripe-resend/backend"

# Create venv and check syntax
python3 -c "
import ast
import sys
from pathlib import Path

files_to_check = [
    'app/core/config.py',
    'app/billing/enums.py',
    'app/billing/models.py',
    'app/billing/routes.py',
    'app/billing/providers/__init__.py',
    'app/emails/enums.py',
    'app/emails/service.py',
    'app/emails/providers/__init__.py',
]

errors = []
for f in files_to_check:
    try:
        with open(f) as fp:
            ast.parse(fp.read())
    except SyntaxError as e:
        errors.append(f'{f}: {e}')

if errors:
    print('Syntax errors found:')
    for e in errors:
        print(f'  {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ Test 4 passed: All Python files have valid syntax${NC}"
else
  echo -e "${RED}✗ Test 4 failed: Python syntax errors${NC}"
  exit 1
fi

# Cleanup
echo -e "\n${YELLOW}🧹 Cleaning up test directory...${NC}"
rm -rf "$TEST_DIR"

echo -e "\n${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ All CLI tests passed!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
