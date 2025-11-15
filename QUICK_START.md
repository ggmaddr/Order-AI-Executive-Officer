# Quick Start Guide - Super Receptionist AI Agent

## 🚀 Complete Setup in 3 Steps

### Step 1: Install MongoDB (Choose One)

#### Option A: MongoDB Atlas (Cloud - Easiest) ⭐ Recommended
1. Go to https://www.mongodb.com/cloud/atlas/register
2. Create a free account
3. Create a free cluster (M0)
4. Create database user (username/password)
5. Add IP address: `0.0.0.0/0` (allow all IPs)
6. Click "Connect" → "Connect your application"
7. Copy the connection string
8. Add to `.env`:
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

#### Option B: Local MongoDB
```bash
# macOS
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community

# Linux (Ubuntu/Debian)
sudo apt-get install mongodb
sudo systemctl start mongodb

# Windows
# Download from: https://www.mongodb.com/try/download/community
```

### Step 2: Run Setup Script
```bash
./setup_mongodb.sh
```

This will:
- ✅ Check MongoDB installation
- ✅ Install Python dependencies
- ✅ Configure `.env` file

### Step 3: Start the Application
```bash
python3 app.py
```

You should see:
```
✅ Connected to MongoDB: super_receptionist
```

## ✅ What's Already Done

- ✅ MongoDB Python packages installed (`motor`, `pymongo`)
- ✅ Database connection configured
- ✅ Persistent conversation IDs (using localStorage)
- ✅ Chat history auto-loads on page refresh
- ✅ Menu items saved to MongoDB
- ✅ Cake designs with images saved to MongoDB
- ✅ All chat messages saved automatically

## 🎯 Features Now Working

### Persistent Storage
- **Menu Items**: Saved forever in MongoDB
- **Cake Designs**: Images stored in MongoDB
- **Chat History**: All conversations persist across restarts

### Chat Features
- **Persistent Conversations**: Same conversation ID across sessions
- **Auto-Load History**: Previous messages load on page refresh
- **Multiple Conversations**: Each conversation has unique ID

## 🔧 Troubleshooting

### MongoDB Connection Failed
```
❌ Failed to connect to MongoDB
```

**Solutions:**
1. **Check MongoDB is running:**
   ```bash
   # macOS
   brew services list
   
   # Linux
   sudo systemctl status mongodb
   ```

2. **Test connection:**
   ```bash
   mongosh  # Should connect to MongoDB shell
   ```

3. **For MongoDB Atlas:**
   - Verify connection string in `.env`
   - Check network access (IP whitelist)
   - Verify username/password

### Data Not Persisting
- Check console for MongoDB connection message
- Verify `.env` has correct `MONGODB_URL`
- Check MongoDB logs for errors

### Port Already in Use
```bash
# Kill process on port 8891
lsof -ti :8891 | xargs kill -9
```

## 📝 Environment Variables

Your `.env` file should have:
```env
# AI Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
AI_PROVIDER=openai

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=super_receptionist

# Server Configuration
PORT=8891
```

## 🎉 You're Ready!

1. ✅ MongoDB configured
2. ✅ Dependencies installed
3. ✅ Persistent storage working
4. ✅ Chat history persists
5. ✅ Menu & cake designs saved

**Start chatting and your data will persist forever!** 🚀

## 📚 Additional Documentation

- `MONGODB_SETUP.md` - Detailed MongoDB setup
- `API_KEY_SETUP.md` - AI API key configuration
- `PORT_MANAGEMENT.md` - Port management guide

