"""
MongoDB Database Connection and Models
Handles all database operations for menu, cake designs, and chat history
"""



from pymongo import AsyncMongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional, List, Dict
import os
from datetime import datetime
import base64
from io import BytesIO
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

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
        if not MONGODB_URL or MONGODB_URL.strip() == "":
            logger.warning("MongoDB connection string not configured")
            return False
        
        client = AsyncMongoClient(
            MONGODB_URL, 
            serverSelectionTimeoutMS=30000,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True
        )
        db = client.get_database(MONGODB_DB_NAME)
        
        await client.admin.command('ping')
        logger.info(f"SUCCESSULLY CONNECTED TO MongoDB: {MONGODB_DB_NAME}")
        return True
    except ConnectionFailure as e:
        logger.error(f"FAILED TO CONNECT TO MongoDB: {e}")
        return False
    except Exception as e:
        logger.error(f"MongoDB connection error: {e}")
        return False

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        await client.close()
        logger.info("MongoDB connection closed")

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

def get_orders_collection():
    """Get orders collection"""
    return db.get_collection("orders")

def get_order_details_collection():
    """Get order details collection"""
    return db.get_collection("order_details")

def get_order_summaries_collection():
    """Get order summaries collection"""
    return db.get_collection("order_summaries")

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
        logger.error(f"Error getting menu items: {e}")
        return []

async def save_menu_items(items: List[Dict]):
    """Save menu items (replace all)"""
    try:
        if db is None:
            logger.warning("MongoDB not connected. Menu items not saved.")
            return False
        collection = get_menu_collection()
        # Delete all existing items
        await collection.delete_many({})
        # Insert new items
        if items:
            await collection.insert_many(items)
        return True
    except Exception as e:
        logger.error(f"Error saving menu items: {e}")
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
        logger.error(f"Error getting cake designs: {e}")
        return []

async def save_cake_designs(designs: List[Dict]):
    """Save cake designs with image handling"""
    try:
        if db is None:
            logger.warning("MongoDB not connected. Cake designs not saved.")
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
                    logger.warning(f"Error processing image for design {design.get('design_id')}: {e}")
            
            designs_to_insert.append(design_doc)
        
        if designs_to_insert:
            await collection.insert_many(designs_to_insert)
        return True
    except Exception as e:
        logger.error(f"Error saving cake designs: {e}")
        return False

# Chat History Operations
async def save_chat_message(conversation_id: str, role: str, message: str, response: Optional[str] = None):
    """Save a chat message to history - ALWAYS saves to maintain full history"""
    try:
        if db is None:
            return False
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
        logger.error(f"Error saving chat message: {e}")
        return False

async def get_chat_history(conversation_id: str, limit: int = 10000) -> List[Dict]:
    """Get chat history for a conversation - returns ALL messages to maintain full history"""
    try:
        if db is None:
            return []
        collection = get_chat_history_collection()
        # Get ALL messages, sorted by timestamp - no limit to get complete history
        cursor = collection.find(
            {'conversation_id': conversation_id}
        ).sort('timestamp', 1)
        messages = await cursor.to_list(length=limit)  # Large limit to get all messages
        # Convert ObjectId to string and format for frontend
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                '_id': str(msg['_id']),
                'role': msg['role'],
                'message': msg['message'],
                'response': msg.get('response'),
                'timestamp': msg['timestamp'].isoformat() if 'timestamp' in msg else None
            })
        return formatted_messages
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
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
        logger.error(f"Error getting conversations: {e}")
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
        logger.error(f"Error deleting conversation: {e}")
        return False

async def update_chat_message(message_id: str, new_message: str) -> Optional[Dict]:
    """Update a chat message and return the updated message"""
    try:
        if db is None:
            return None
        from bson import ObjectId
        collection = get_chat_history_collection()
        
        # Update the message
        result = await collection.update_one(
            {'_id': ObjectId(message_id)},
            {'$set': {'message': new_message, 'updated_at': datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            # Get the updated message
            updated_msg = await collection.find_one({'_id': ObjectId(message_id)})
            if updated_msg:
                return {
                    '_id': str(updated_msg['_id']),
                    'role': updated_msg['role'],
                    'message': updated_msg['message'],
                    'response': updated_msg.get('response'),
                    'timestamp': updated_msg['timestamp'].isoformat() if 'timestamp' in updated_msg else None
                }
        return None
    except Exception as e:
        logger.error(f"Error updating chat message: {e}")
        return None

async def delete_messages_after(message_id: str, conversation_id: str) -> bool:
    """Delete all messages after a given message ID (for regeneration)"""
    try:
        if db is None:
            return False
        from bson import ObjectId
        collection = get_chat_history_collection()
        
        # Get the timestamp of the message to delete after
        message = await collection.find_one({'_id': ObjectId(message_id)})
        if not message:
            return False
        
        message_timestamp = message.get('timestamp')
        if not message_timestamp:
            return False
        
        # Delete all messages after this timestamp in the same conversation
        result = await collection.delete_many({
            'conversation_id': conversation_id,
            'timestamp': {'$gt': message_timestamp}
        })
        
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting messages after: {e}")
        return False

# ============================================================================
# ORDERS OPERATIONS
# ============================================================================
# TODO: Review and implement order operations based on mongodb_schemas.py

async def create_order(order_data: Dict) -> bool:
    """Create a new order"""
    try:
        if db is None:
            logger.warning("MongoDB not connected. Order not saved.")
            return False
        collection = get_orders_collection()
        # Add timestamps
        order_data['created_at'] = datetime.utcnow()
        order_data['updated_at'] = datetime.utcnow()
        await collection.insert_one(order_data)
        return True
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return False

async def get_order(order_id: str) -> Optional[Dict]:
    """Get a specific order by order_id"""
    try:
        if db is None:
            return None
        collection = get_orders_collection()
        order = await collection.find_one({'order_id': order_id})
        if order:
            order['_id'] = str(order['_id'])
        return order
    except Exception as e:
        logger.error(f"Error getting order: {e}")
        return None

async def get_all_orders(limit: int = 1000) -> List[Dict]:
    """Get all orders"""
    try:
        if db is None:
            return []
        collection = get_orders_collection()
        cursor = collection.find({}).sort('date_time', -1).limit(limit)
        orders = await cursor.to_list(length=limit)
        for order in orders:
            order['_id'] = str(order['_id'])
        return orders
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        return []

# ============================================================================
# ORDER DETAILS OPERATIONS
# ============================================================================
# TODO: Review and implement order details operations based on mongodb_schemas.py

async def create_order_details(order_details: List[Dict]) -> bool:
    """Create order details for an order"""
    try:
        if db is None:
            logger.warning("MongoDB not connected. Order details not saved.")
            return False
        collection = get_order_details_collection()
        # Add timestamps
        for detail in order_details:
            detail['created_at'] = datetime.utcnow()
        await collection.insert_many(order_details)
        return True
    except Exception as e:
        logger.error(f"Error creating order details: {e}")
        return False

async def get_order_details_by_order_id(order_id: str) -> List[Dict]:
    """Get all order details for a specific order"""
    try:
        if db is None:
            return []
        collection = get_order_details_collection()
        cursor = collection.find({'order_id': order_id})
        details = await cursor.to_list(length=1000)
        for detail in details:
            detail['_id'] = str(detail['_id'])
        return details
    except Exception as e:
        logger.error(f"Error getting order details: {e}")
        return []

async def create_order_summary(summary_data: Dict) -> bool:
    """Create or update order summary"""
    try:
        if db is None:
            logger.warning("MongoDB not connected. Summary not saved.")
            return False
        collection = get_order_summaries_collection()
        # Use upsert to update if exists, insert if not
        await collection.update_one(
            {
                'summary_date': summary_data['summary_date'],
                'product_type': summary_data['product_type']
            },
            {'$set': summary_data},
            upsert=True
        )
        return True
    except Exception as e:
        logger.error(f"Error creating order summary: {e}")
        return False

async def get_order_summaries_by_date(start_date: datetime, end_date: datetime) -> List[Dict]:
    """Get order summaries for a date range"""
    try:
        if db is None:
            return []
        collection = get_order_summaries_collection()
        cursor = collection.find({
            'summary_date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('summary_date', 1)
        summaries = await cursor.to_list(length=1000)
        for summary in summaries:
            summary['_id'] = str(summary['_id'])
        return summaries
    except Exception as e:
        logger.error(f"Error getting order summaries: {e}")
        return []

