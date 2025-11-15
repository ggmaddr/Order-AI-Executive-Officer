#!/bin/bash

# Super Receptionist - Startup Script

echo "🚀 Starting Super Receptionist AI Agent..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/training

# Start the server
echo "🌟 Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop the server"
echo ""
python app.py

