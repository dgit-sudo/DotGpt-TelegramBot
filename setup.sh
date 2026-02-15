#!/bin/bash

# DotGPT Shop Bot - Quick Setup Script
# This script automates the setup process

set -e

echo "🤖 DotGPT Shop Bot - Quick Setup"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python $python_version found"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment created"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Dependencies installed"

# Setup environment file
echo ""
echo "⚙️  Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your:${NC}"
    echo "   - BOT_TOKEN (from @BotFather)"
    echo "   - ADMIN_IDS (your Telegram ID)"
    echo ""
    echo "Edit .env and run: python init_sample_data.py && python main.py"
else
    echo -e "${GREEN}✓${NC} .env file already exists"
fi

# Initialize database
echo ""
echo "💾 Initializing database..."
python init_sample_data.py
echo -e "${GREEN}✓${NC} Database initialized with sample data"

echo ""
echo "=================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "=================================="
echo ""
echo "🚀 Next steps:"
echo "   1. Edit .env file with your BOT_TOKEN and ADMIN_IDS"
echo "   2. Run: python main.py"
echo "   3. Find your bot on Telegram and send /start"
echo ""
echo "📚 Documentation:"
echo "   - README.md      - Overview and setup"
echo "   - FEATURES.md    - Complete feature list"
echo "   - DEPLOYMENT.md  - Production deployment"
echo "   - DEVELOPER.md   - Developer guide"
echo ""
