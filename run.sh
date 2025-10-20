#!/bin/bash

# Quick Start Script for Live 3D AI Agent Backend
# Run this from the Backend directory

cd "$(dirname "$0")"

echo "🚀 Live 3D AI Agent Backend - Quick Start"
echo "==========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found. Please run this script from the Backend directory."
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check/Create virtual environment
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo ""
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"

# Check .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  Warning: .env file not found"
    echo "Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "⚠️  Please edit .env with your API keys!"
    fi
fi

echo ""
echo "==========================================="
echo "🎉 Starting Backend Server"
echo "==========================================="
echo ""
echo "📡 Server URL: http://localhost:8000"
echo "📚 API Docs:   http://localhost:8000/docs"
echo "📖 ReDoc:      http://localhost:8000/redoc"
echo ""
echo "Press CTRL+C to stop the server"
echo ""
echo "==========================================="
echo ""

# Start server with the correct command
uvicorn main:app --reload --host 0.0.0.0 --port 8000
