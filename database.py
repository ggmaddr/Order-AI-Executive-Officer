"""
MongoDB Database Connection and Models
Handles all database operations for menu, cake designs, and chat history
"""

# Fix DNS resolution issue for MongoDB Atlas connections
# This must be done BEFORE importing pymongo
# Fixes issue where dnspython tries to open /etc/resolv.conf
import dns.resolver
import dns.asyncresolver

# Configure sync DNS resolver to use Google DNS instead of reading /etc/resolv.conf
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

# Configure async DNS resolver (used by pymongo's AsyncMongoClient)
try:
    dns.asyncresolver.default_resolver = dns.asyncresolver.Resolver(configure=False)
    dns.asyncresolver.default_resolver.nameservers = ['8.8.8.8']
except:
    # If asyncresolver doesn't exist or fails, continue
    pass

# Patch Resolver.__init__ to ALWAYS use our configured nameservers
# This ensures ANY resolver created (including by pymongo) uses our DNS servers
_original_resolver_init = dns.resolver.Resolver.__init__

def _patched_resolver_init(self, filename=None, configure=True):
    """Patched resolver init that ensures nameservers are always set from our config"""
    # Always call with configure=False to avoid reading /etc/resolv.conf
    _original_resolver_init(self, filename, configure=False)
    # Force set nameservers from our pre-configured resolver
    self.nameservers = ['8.8.8.8']
    # Set reasonable defaults
    if not hasattr(self, 'timeout') or self.timeout is None:
        self.timeout = 5.0
    if not hasattr(self, 'lifetime') or self.lifetime is None:
        self.lifetime = 10.0

dns.resolver.Resolver.__init__ = _patched_resolver_init

# Patch asyncresolver.Resolver.__init__ as well
try:
    _original_async_resolver_init = dns.asyncresolver.Resolver.__init__
    def _patched_async_resolver_init(self, filename=None, configure=True):
        """Patched async resolver init"""
        _original_async_resolver_init(self, filename, configure=False)
        self.nameservers = ['8.8.8.8']
        if not hasattr(self, 'timeout') or self.timeout is None:
            self.timeout = 5.0
        if not hasattr(self, 'lifetime') or self.lifetime is None:
            self.lifetime = 10.0
    dns.asyncresolver.Resolver.__init__ = _patched_async_resolver_init
except:
    pass

from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional, List, Dict
import os
from datetime import datetime
import base64
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "super_receptionist")  # Default fallback

# Global database connection
client: Optional[AsyncMongoClient] = None
db = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    try:
        # Check if connection string is configured
        if not MONGODB_URL or MONGODB_URL.strip() == "":
            print("⚠️  MongoDB connection string not configured!")
            print(f"   Please set MONGODB_URL in .env file")
            print(f"   Example: MONGODB_URL=mongodb://localhost:27018")
            print(f"   Or MongoDB Atlas: MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/")
            return False
        
        # Show connection attempt (hide password)
        display_url = MONGODB_URL.split('@')[-1] if '@' in MONGODB_URL else MONGODB_URL[:30] + "..."
        print(f"🔌 Connecting to MongoDB: {display_url}")
        print(f"   Database: {MONGODB_DB_NAME}")
        
        # Create client with SSL certificate verification disabled for development
        # In production, you should use proper SSL certificates
        client = AsyncMongoClient(
            MONGODB_URL, 
            serverSelectionTimeoutMS=30000,
            tlsAllowInvalidCertificates=True,  # Allow invalid certificates (development only)
            tlsAllowInvalidHostnames=True      # Allow invalid hostnames (development only)
        )
        db = client.get_database(MONGODB_DB_NAME)
        
        # Test connection
        await client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {MONGODB_DB_NAME}")
        return True
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return False

        

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        await client.close()
        print("MongoDB connection closed")

# Collections
def get_menu_collection():
    """Get menu items collection"""
    return db.get_collection("menu_items")

def get_cake_designs_collection():
    """Get cake designs collection"""
    return db.get_collection("cake_designs")

def get_chat_history_collection():
    """Get chat history collection"""
    return db.get_collection("chat_history")

def get_images_collection():
    """Get GridFS collection for images"""
    return db.get_collection("images")

# Menu Operations
async def get_all_menu_items() -> List[Dict]:
    """Get all menu items"""
    try:
        if db is None:
            return []
        collection = get_menu_collection()
        cursor = collection.find({})
        items = await cursor.to_list(length=1000)
        # Convert ObjectId to string
        for item in items:
            item['_id'] = str(item['_id'])
        return items
    except Exception as e:
        print(f"Error getting menu items: {e}")
        return []

async def save_menu_items(items: List[Dict]):
    """Save menu items (replace all)"""
    try:
        if db is None:
            print("⚠️  MongoDB not connected. Menu items not saved.")
            return False
        collection = get_menu_collection()
        # Delete all existing items
        await collection.delete_many({})
        # Insert new items
        if items:
            await collection.insert_many(items)
        return True
    except Exception as e:
        print(f"Error saving menu items: {e}")
        return False

# Cake Designs Operations
async def get_all_cake_designs() -> List[Dict]:
    """Get all cake designs"""
    try:
        if db is None:
            return []
        collection = get_cake_designs_collection()
        cursor = collection.find({})
        designs = await cursor.to_list(length=1000)
        # Convert ObjectId to string and handle image data
        for design in designs:
            design['_id'] = str(design['_id'])
            # If image is stored as binary, convert to base64
            if 'image_data' in design and design['image_data']:
                design['image_url'] = f"data:image/png;base64,{base64.b64encode(design['image_data']).decode()}"
        return designs
    except Exception as e:
        print(f"Error getting cake designs: {e}")
        return []

async def save_cake_designs(designs: List[Dict]):
    """Save cake designs with image handling"""
    try:
        if db is None:
            print("⚠️  MongoDB not connected. Cake designs not saved.")
            return False
        collection = get_cake_designs_collection()
        # Delete all existing designs
        await collection.delete_many({})
        # Process each design
        designs_to_insert = []
        for design in designs:
            design_doc = {
                'design_id': design.get('design_id'),
                'name': design.get('name'),
                'description': design.get('description'),
                'image_url': design.get('image_url'),
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            # If image_url is a base64 data URL, extract and store binary
            if design.get('image_url') and design['image_url'].startswith('data:image'):
                try:
                    # Extract base64 data
                    header, encoded = design['image_url'].split(',', 1)
                    image_data = base64.b64decode(encoded)
                    design_doc['image_data'] = image_data
                    design_doc['image_url'] = None  # Don't store URL if we have binary
                except Exception as e:
                    print(f"Error processing image for design {design.get('design_id')}: {e}")
            
            designs_to_insert.append(design_doc)
        
        if designs_to_insert:
            await collection.insert_many(designs_to_insert)
        return True
    except Exception as e:
        print(f"Error saving cake designs: {e}")
        return False

# Chat History Operations
async def save_chat_message(conversation_id: str, role: str, message: str, response: Optional[str] = None):
    """Save a chat message to history"""
    try:
        if db is None:
            return False  # Silently fail if MongoDB not connected
        collection = get_chat_history_collection()
        chat_doc = {
            'conversation_id': conversation_id,
            'role': role,  # 'user' or 'bot'
            'message': message,
            'response': response,
            'timestamp': datetime.utcnow()
        }
        await collection.insert_one(chat_doc)
        return True
    except Exception as e:
        print(f"Error saving chat message: {e}")
        return False

async def get_chat_history(conversation_id: str, limit: int = 100) -> List[Dict]:
    """Get chat history for a conversation"""
    try:
        if db is None:
            return []
        collection = get_chat_history_collection()
        cursor = collection.find(
            {'conversation_id': conversation_id}
        ).sort('timestamp', 1).limit(limit)
        messages = await cursor.to_list(length=limit)
        # Convert ObjectId to string and format for frontend
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'role': msg['role'],
                'message': msg['message'],
                'response': msg.get('response'),
                'timestamp': msg['timestamp'].isoformat() if 'timestamp' in msg else None
            })
        return formatted_messages
    except Exception as e:
        print(f"Error getting chat history: {e}")
        return []

async def get_all_conversations() -> List[str]:
    """Get all unique conversation IDs"""
    try:
        if db is None:
            return []
        collection = get_chat_history_collection()
        conversations = await collection.distinct('conversation_id')
        return conversations
    except Exception as e:
        print(f"Error getting conversations: {e}")
        return []

async def delete_conversation(conversation_id: str):
    """Delete a conversation"""
    try:
        if db is None:
            return False
        collection = get_chat_history_collection()
        result = await collection.delete_many({'conversation_id': conversation_id})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting conversation: {e}")
        return False

