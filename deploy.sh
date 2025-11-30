#!/bin/bash

# Deployment Helper Script
# Helps prepare and deploy Super Receptionist to various platforms

echo "🚀 Super Receptionist - Deployment Helper"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating template .env file..."
    cat > .env << EOF
# AI Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4o-mini
AI_PROVIDER=openai

# MongoDB Configuration (Use MongoDB Atlas for production)
MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/dbname
MONGODB_DB_NAME=super_receptionist

# Server
PORT=8000
EOF
    echo "✅ Created .env template. Please fill in your values!"
    echo ""
fi

echo "Select deployment platform:"
echo "1) Render.com (Recommended - Free tier)"
echo "2) Railway.app (Fast deployment)"
echo "3) Fly.io (Docker-based)"
echo "4) Docker (Local/Any platform)"
echo "5) Test locally first"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "📋 Render.com Deployment Steps:"
        echo "1. Go to https://render.com and sign up"
        echo "2. Click 'New +' → 'Web Service'"
        echo "3. Connect your GitHub repository"
        echo "4. Configure:"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: python app.py"
        echo "5. Add environment variables from your .env file"
        echo "6. Deploy!"
        echo ""
        echo "Your app will be live at: https://your-app-name.onrender.com"
        ;;
    2)
        echo ""
        echo "📋 Railway.app Deployment Steps:"
        echo "1. Go to https://railway.app and sign up"
        echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
        echo "3. Select your repository"
        echo "4. Go to 'Variables' tab and add environment variables"
        echo "5. Railway auto-deploys!"
        echo ""
        echo "Your app will be live at: https://your-app-name.railway.app"
        ;;
    3)
        echo ""
        echo "📋 Fly.io Deployment Steps:"
        echo "1. Install Fly CLI: curl -L https://fly.io/install.sh | sh"
        echo "2. Login: fly auth login"
        echo "3. Launch: fly launch"
        echo "4. Set secrets: fly secrets set KEY=value"
        echo "5. Deploy: fly deploy"
        echo ""
        echo "Your app will be live at: https://your-app-name.fly.dev"
        ;;
    4)
        echo ""
        echo "🐳 Building Docker image..."
        docker build -t super-receptionist .
        if [ $? -eq 0 ]; then
            echo "✅ Docker image built successfully!"
            echo ""
            echo "To run locally:"
            echo "  docker run -p 8000:8000 --env-file .env super-receptionist"
            echo ""
            echo "Or use docker-compose:"
            echo "  docker-compose up -d"
        else
            echo "❌ Docker build failed!"
        fi
        ;;
    5)
        echo ""
        echo "🧪 Testing locally..."
        if [ ! -d "venv" ]; then
            echo "Creating virtual environment..."
            python3 -m venv venv
        fi
        source venv/bin/activate
        pip install -q -r requirements.txt
        echo ""
        echo "Starting server on http://localhost:8000"
        echo "Press Ctrl+C to stop"
        echo ""
        python app.py
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "📚 For detailed instructions, see DEPLOYMENT.md"

