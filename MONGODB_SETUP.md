# MongoDB Setup Guide

## Overview

The Super Receptionist AI Agent now uses MongoDB to persist:
- ✅ Shop Menu Items
- ✅ Cake Designs (with images)
- ✅ Chat History (all conversations)

All data persists even after closing and restarting the application.

## MongoDB Installation

### Option 1: Local MongoDB Installation

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

**Windows:**
Download from: https://www.mongodb.com/try/download/community

### Option 2: MongoDB Atlas (Cloud - Recommended)

1. Sign up at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get your connection string
4. Add to `.env` file

## Configuration

### 1. Add MongoDB URL to `.env` file

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=super_receptionist

# OR for MongoDB Atlas (cloud):
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
# MONGODB_DB_NAME=super_receptionist
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `motor` - Async MongoDB driver
- `pymongo` - MongoDB Python driver

## Database Structure

### Collections

1. **`menu_items`** - Shop menu items
   ```json
   {
     "_id": "ObjectId",
     "name": "Panna Cotta",
     "description": "Creamy Italian dessert",
     "price": 4.50,
     "category": "Desserts"
   }
   ```

2. **`cake_designs`** - Cake designs with images
   ```json
   {
     "_id": "ObjectId",
     "design_id": "DESIGN001",
     "name": "Birthday Cake",
     "description": "Colorful birthday cake",
     "image_url": "data:image/png;base64,...",
     "image_data": "Binary data",
     "created_at": "2024-01-01T00:00:00Z",
     "updated_at": "2024-01-01T00:00:00Z"
   }
   ```

3. **`chat_history`** - Chat messages
   ```json
   {
     "_id": "ObjectId",
     "conversation_id": "conv_1234567890",
     "role": "user",
     "message": "Hello",
     "response": "Hi! How can I help?",
     "timestamp": "2024-01-01T00:00:00Z"
   }
   ```

## API Endpoints

### Menu
- `GET /api/menu` - Get all menu items from MongoDB
- `POST /api/menu` - Save menu items to MongoDB

### Cake Designs
- `GET /api/cake-designs` - Get all cake designs from MongoDB
- `POST /api/cake-designs` - Save cake designs to MongoDB (with images)

### Chat History
- `GET /api/chat/history/{conversation_id}` - Get chat history for a conversation
- `GET /api/chat/conversations` - Get all conversation IDs
- `DELETE /api/chat/history/{conversation_id}` - Delete a conversation

## Features

### ✅ Persistent Storage
- All data is saved to MongoDB
- Survives application restarts
- No data loss when closing the program

### ✅ Image Storage
- Cake design images stored as binary data in MongoDB
- Automatically converts base64 to binary on save
- Converts back to base64 on retrieval

### ✅ Chat History
- Every message is saved automatically
- Loads previous conversations on startup
- Supports multiple conversations

## Testing MongoDB Connection

### Check if MongoDB is running:
```bash
# macOS/Linux
mongosh

# Or check status
brew services list  # macOS
sudo systemctl status mongodb  # Linux
```

### Test connection in Python:
```python
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await client.admin.command('ping')
    print("✅ MongoDB connection successful!")

asyncio.run(test())
```

## Troubleshooting

### Connection Error
```
❌ Failed to connect to MongoDB
```

**Solutions:**
1. Check if MongoDB is running: `brew services list` or `sudo systemctl status mongodb`
2. Verify MongoDB URL in `.env` file
3. Check firewall settings
4. For Atlas: Verify network access and credentials

### Port Already in Use
```
Address already in use: 27017
```

**Solution:**
- Stop other MongoDB instances
- Or change MongoDB port in configuration

### Data Not Persisting
- Check MongoDB connection logs
- Verify database name in `.env`
- Check MongoDB logs: `tail -f /usr/local/var/log/mongodb/mongo.log`

## Migration from JSON Files

If you have existing data in JSON files:

1. **Menu Items:** The app will automatically migrate when you load/save menu
2. **Cake Designs:** Load and save through the UI to migrate
3. **Chat History:** New conversations will be saved automatically

Old JSON files in `data/training/` are kept as backup but no longer used.

## MongoDB Atlas Setup (Cloud)

1. **Create Account:** https://www.mongodb.com/cloud/atlas/register
2. **Create Cluster:** Choose free tier (M0)
3. **Create Database User:** Username/password
4. **Whitelist IP:** Add `0.0.0.0/0` for all IPs (or your specific IP)
5. **Get Connection String:** Click "Connect" → "Connect your application"
6. **Add to `.env`:**
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   ```

## Security Notes

⚠️ **Important:**
- Never commit `.env` file with credentials
- Use environment variables for production
- Restrict MongoDB network access in production
- Use strong passwords for database users
- Enable MongoDB authentication for production

## Next Steps

1. Install MongoDB (local or Atlas)
2. Add `MONGODB_URL` to `.env` file
3. Install dependencies: `pip install -r requirements.txt`
4. Start the application: `python3 app.py`
5. Check console for: `✅ Connected to MongoDB`

Your data will now persist forever! 🎉

