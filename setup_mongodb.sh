#!/bin/bash

# MongoDB Setup Script for Super Receptionist
echo "🚀 Setting up MongoDB for Super Receptionist..."

# Check if MongoDB is installed
if command -v mongod &> /dev/null; then
    echo "✅ MongoDB is installed"
    
    # Check if MongoDB is running
    if pgrep -x mongod > /dev/null; then
        echo "✅ MongoDB is already running"
    else
        echo "📦 Starting MongoDB..."
        # Try to start MongoDB (macOS)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start mongodb-community 2>/dev/null || mongod --dbpath ~/data/db --fork --logpath ~/data/db/mongod.log 2>/dev/null || echo "⚠️  Please start MongoDB manually"
        else
            sudo systemctl start mongodb 2>/dev/null || echo "⚠️  Please start MongoDB manually: sudo systemctl start mongodb"
        fi
    fi
else
    echo "❌ MongoDB is not installed"
    echo ""
    echo "Installation options:"
    echo ""
    echo "Option 1: Local MongoDB"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  macOS: brew tap mongodb/brew && brew install mongodb-community"
    else
        echo "  Linux: sudo apt-get install mongodb"
    fi
    echo ""
    echo "Option 2: MongoDB Atlas (Cloud - Recommended)"
    echo "  1. Sign up at https://www.mongodb.com/cloud/atlas"
    echo "  2. Create free cluster"
    echo "  3. Get connection string"
    echo "  4. Add to .env: MONGODB_URL=mongodb+srv://..."
    echo ""
fi

# Check Python dependencies
echo ""
echo "📦 Checking Python dependencies..."
if python3 -c "import motor" 2>/dev/null && python3 -c "import pymongo" 2>/dev/null; then
    echo "✅ MongoDB Python packages installed"
else
    echo "📥 Installing MongoDB Python packages..."
    pip3 install motor pymongo
fi

# Check .env file
echo ""
echo "📝 Checking .env configuration..."
if [ -f .env ]; then
    if grep -q "MONGODB_URL" .env; then
        echo "✅ MONGODB_URL found in .env"
        grep "MONGODB_URL" .env | head -1
    else
        echo "⚠️  MONGODB_URL not found in .env"
        echo ""
        echo "Adding default MongoDB configuration..."
        echo "" >> .env
        echo "# MongoDB Configuration" >> .env
        echo "MONGODB_URL=mongodb://localhost:27017" >> .env
        echo "MONGODB_DB_NAME=super_receptionist" >> .env
        echo "✅ Added MongoDB config to .env"
    fi
else
    echo "⚠️  .env file not found, creating with MongoDB config..."
    echo "# MongoDB Configuration" > .env
    echo "MONGODB_URL=mongodb://localhost:27017" >> .env
    echo "MONGODB_DB_NAME=super_receptionist" >> .env
    echo "✅ Created .env with MongoDB config"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure MongoDB is running"
echo "2. Update MONGODB_URL in .env if using MongoDB Atlas"
echo "3. Start the app: python3 app.py"
echo "4. Check console for: ✅ Connected to MongoDB"

