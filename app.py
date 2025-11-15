"""
Super Receptionist - AI Agent for Order Processing
Main FastAPI application with chatbot and training interfaces
"""

# Fix DNS resolution issue for MongoDB Atlas connections
# This must be done BEFORE importing pymongo/database
# Fixes issue where dnspython tries to open /etc/resolv.conf
import dns.resolver
dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers = ['8.8.8.8']

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Connect to MongoDB
    await database.connect_to_mongo()
    yield
    # Shutdown: Close MongoDB connection
    await database.close_mongo_connection()

app = FastAPI(title="Super Receptionist AI Agent", lifespan=lifespan)

# ============================================================================
# AI AGENT API KEY CONFIGURATION
# ============================================================================
# Add your AI provider API key here. You can use:
# - OpenAI: OPENAI_API_KEY
# - Anthropic: ANTHROPIC_API_KEY
# - Or any other AI provider

# Option 1: Load from environment variable (RECOMMENDED)
AI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("AI_API_KEY")

# Option 2: Or set directly here (NOT RECOMMENDED for production)
# AI_API_KEY = "your-api-key-here"

# AI Provider selection
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # Options: "openai", "anthropic", "custom"

if not AI_API_KEY:
    logger.warning("AI_API_KEY not found in environment variables")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Data directories
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
TRAINING_DIR = DATA_DIR / "training"
TRAINING_DIR.mkdir(exist_ok=True)

# Request/Response models
class ChatMessage(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

class SystemPromptUpdate(BaseModel):
    prompt: str

class MenuItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None

class MenuUpdate(BaseModel):
    items: List[MenuItem]

class CakeDesign(BaseModel):
    design_id: str
    name: str
    description: str
    image_url: Optional[str] = None

class CakeDesignsUpdate(BaseModel):
    designs: List[CakeDesign]

class ConversionInstructions(BaseModel):
    instructions: str
    examples: Optional[List[Dict]] = None

# Load configuration files
def load_json_file(filepath: Path, default: dict = None):
    """Load JSON file or return default"""
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default or {}

def save_json_file(filepath: Path, data: dict):
    """Save data to JSON file"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Initialize default files
SYSTEM_PROMPT_FILE = TRAINING_DIR / "system_prompt.json"
MENU_FILE = TRAINING_DIR / "menu.json"
CAKE_DESIGNS_FILE = TRAINING_DIR / "cake_designs.json"
CONVERSION_INSTRUCTIONS_FILE = TRAINING_DIR / "conversion_instructions.json"

# Initialize default system prompt
if not SYSTEM_PROMPT_FILE.exists():
    default_prompt = {
        "prompt": """You are an AI assistant for order processing. Your role is to:
1. Extract order information from text screenshots
2. Convert order details to structured JSON format
3. Help populate spreadsheets with order data
4. Generate invoices from order information

Be helpful, accurate, and follow the shop owner's specific instructions for order processing."""
    }
    save_json_file(SYSTEM_PROMPT_FILE, default_prompt)

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main UI"""
    html_file = Path(__file__).parent / "static" / "index.html"
    if html_file.exists():
        with open(html_file, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Super Receptionist AI Agent</h1><p>Please ensure index.html exists in static folder</p>")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """
    Chat endpoint - Main chatbot interface
    This is where users interact with the AI agent
    """
    conversation_id = message.conversation_id or "default"
    
    # Load system prompt for context
    system_prompt_data = load_json_file(SYSTEM_PROMPT_FILE, {})
    system_prompt = system_prompt_data.get("prompt", "")
    
    # Load training data for context from MongoDB
    menu_items = await database.get_all_menu_items()
    cake_designs = await database.get_all_cake_designs()
    conversion_instructions_data = load_json_file(CONVERSION_INSTRUCTIONS_FILE, {})
    
    # Save user message to chat history
    await database.save_chat_message(conversation_id, "user", message.message)
    
    # ============================================================================
    # AI AGENT INTEGRATION - Add your AI API calls here
    # ============================================================================
    
    if not AI_API_KEY:
        # Fallback response when API key is not configured
        response_text = (
            f"I received your message: '{message.message}'. "
            "⚠️ AI API key not configured. Please add your API key to use the AI agent."
        )
        # Save fallback response to history
        await database.save_chat_message(conversation_id, "bot", message.message, response_text)
    else:
        # ========================================================================
        # EXAMPLE: OpenAI Integration
        # ========================================================================
        if AI_PROVIDER.lower() == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=AI_API_KEY)
                
                # Build context from training data
                context = f"""
System Prompt: {system_prompt}

Shop Menu: {json.dumps(menu_items, indent=2)}
Cake Designs: {json.dumps(cake_designs, indent=2)}
Conversion Instructions: {conversion_instructions_data.get('instructions', '')}
"""
                
                # Model selection - Use fast/cost-effective models for quick responses
                # Valid models: "gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"
                # Note: "gpt-4" is deprecated/not available - use "gpt-4o" or "gpt-4-turbo" instead
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                
                # Fallback to valid model if invalid model specified
                valid_models = ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo", "gpt-4o-2024-05-13"]
                if model not in valid_models and not model.startswith("gpt-3.5") and not model.startswith("gpt-4o"):
                    logger.warning(f"Model '{model}' may not be valid. Using 'gpt-4o-mini' as fallback.")
                    model = "gpt-4o-mini"
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": context},
                        {"role": "user", "content": message.message}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                response_text = response.choices[0].message.content
                
                # Save bot response to chat history
                await database.save_chat_message(conversation_id, "bot", message.message, response_text)
                
            except Exception as e:
                error_msg = str(e)
                if "model_not_found" in error_msg or "does not exist" in error_msg:
                    response_text = (
                        f"❌ Model Error: The model '{model}' is not available or you don't have access.\n\n"
                        f"✅ Valid models you can use:\n"
                        f"   • gpt-4o-mini (fast, cheap) - RECOMMENDED\n"
                        f"   • gpt-3.5-turbo (very fast, cheapest)\n"
                        f"   • gpt-4o (better quality)\n"
                        f"   • gpt-4-turbo (high quality)\n\n"
                        f"Update OPENAI_MODEL in your .env file and restart the server."
                    )
                else:
                    response_text = f"Error calling AI API: {error_msg}"
                # Save error response to history - ALWAYS save to maintain full history
                await database.save_chat_message(conversation_id, "bot", message.message, response_text)
        
        # ========================================================================
        # EXAMPLE: Anthropic Integration
        # ========================================================================
        elif AI_PROVIDER.lower() == "anthropic":
            try:
                try:
                    import anthropic
                except ImportError:
                    response_text = "Anthropic package not installed. Run: pip install anthropic"
                    return ChatResponse(response=response_text, conversation_id=conversation_id)
                
                client = anthropic.Anthropic(api_key=AI_API_KEY)
                
                # Build context from training data
                context = f"""
System Prompt: {system_prompt}

Shop Menu: {json.dumps(menu_items, indent=2)}
Cake Designs: {json.dumps(cake_designs, indent=2)}
Conversion Instructions: {conversion_instructions_data.get('instructions', '')}
"""
                
                response = client.messages.create(
                    model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
                    max_tokens=1000,
                    system=context,
                    messages=[
                        {"role": "user", "content": message.message}
                    ]
                )
                response_text = response.content[0].text
                
                # Save bot response to chat history - ALWAYS save to maintain full history
                await database.save_chat_message(conversation_id, "bot", message.message, response_text)
                
            except Exception as e:
                response_text = f"Error calling AI API: {str(e)}"
                # Save error response to history
                await database.save_chat_message(conversation_id, "bot", message.message, response_text)
        
        # ========================================================================
        # Add your custom AI provider here
        # ========================================================================
        else:
            response_text = (
                f"AI Provider '{AI_PROVIDER}' not implemented. "
                "Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY, "
                "or implement your custom provider."
            )
            # Save error response to history
            await database.save_chat_message(conversation_id, "bot", message.message, response_text)
    
    return ChatResponse(
        response=response_text,
        conversation_id=conversation_id
    )

@app.get("/api/system-prompt")
async def get_system_prompt():
    """Get current system prompt"""
    return load_json_file(SYSTEM_PROMPT_FILE, {"prompt": ""})

@app.post("/api/system-prompt")
async def update_system_prompt(update: SystemPromptUpdate):
    """Update system prompt for fine-tuning - overwrites existing prompt"""
    save_json_file(SYSTEM_PROMPT_FILE, {"prompt": update.prompt})
    return {"status": "success", "message": "System prompt updated successfully"}

@app.get("/api/system-prompt/history")
async def get_system_prompt_history():
    """Get system prompt history/versions (if you want to track changes)"""
    # TODO: Implement prompt version history if needed
    # For now, just return current prompt
    current = load_json_file(SYSTEM_PROMPT_FILE, {"prompt": ""})
    return {"history": [{"version": 1, "prompt": current.get("prompt", ""), "updated_at": "current"}]}

@app.get("/api/menu")
async def get_menu():
    """Get shop menu from MongoDB"""
    try:
        items = await database.get_all_menu_items()
        return {"items": items}
    except Exception as e:
        logger.error(f"Error getting menu: {e}")
        return {"items": []}

@app.post("/api/menu")
async def update_menu(update: MenuUpdate):
    """Update shop menu in MongoDB"""
    try:
        items = [item.dict() for item in update.items]
        success = await database.save_menu_items(items)
        if success:
            return {"status": "success", "message": "Menu updated successfully in MongoDB"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save menu")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating menu: {str(e)}")

@app.get("/api/cake-designs")
async def get_cake_designs():
    """Get personalized cake designs from MongoDB"""
    try:
        designs = await database.get_all_cake_designs()
        return {"designs": designs}
    except Exception as e:
        logger.error(f"Error getting cake designs: {e}")
        return {"designs": []}

@app.post("/api/cake-designs")
async def update_cake_designs(update: CakeDesignsUpdate):
    """Update personalized cake designs in MongoDB"""
    try:
        designs = [design.dict() for design in update.designs]
        success = await database.save_cake_designs(designs)
        if success:
            return {"status": "success", "message": "Cake designs updated successfully in MongoDB"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save cake designs")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating cake designs: {str(e)}")

@app.get("/api/conversion-instructions")
async def get_conversion_instructions():
    """Get instructions for screenshot-to-JSON conversion"""
    return load_json_file(CONVERSION_INSTRUCTIONS_FILE, {"instructions": "", "examples": []})

@app.post("/api/conversion-instructions")
async def update_conversion_instructions(update: ConversionInstructions):
    """Update conversion instructions"""
    instructions_data = {
        "instructions": update.instructions,
        "examples": update.examples or []
    }
    save_json_file(CONVERSION_INSTRUCTIONS_FILE, instructions_data)
    return {"status": "success", "message": "Conversion instructions updated successfully"}

@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image for processing (screenshot of order confirmation)"""
    # TODO: Implement image processing and OCR
    return {
        "status": "success",
        "message": "Image uploaded successfully",
        "filename": file.filename
    }

# Chat History Endpoints
@app.get("/api/chat/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Get chat history for a conversation - returns ALL messages to maintain full history"""
    try:
        messages = await database.get_chat_history(conversation_id, limit=10000)  # Get all messages
        return {"messages": messages, "count": len(messages), "conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat history: {str(e)}")

@app.post("/api/chat/edit/{message_id}")
async def edit_chat_message(message_id: str, edit_request: Dict):
    """Edit a chat message and regenerate AI response"""
    try:
        new_message = edit_request.get("message")
        conversation_id = edit_request.get("conversation_id")
        
        if not new_message or not conversation_id:
            raise HTTPException(status_code=400, detail="Message and conversation_id required")
        
        # Update the message in database
        updated_msg = await database.update_chat_message(message_id, new_message)
        if not updated_msg:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # Delete all messages after this one (to regenerate from this point)
        await database.delete_messages_after(message_id, conversation_id)
        
        # Regenerate AI response
        # Load system prompt and training data
        system_prompt_data = load_json_file(SYSTEM_PROMPT_FILE, {})
        system_prompt = system_prompt_data.get("prompt", "")
        menu_items = await database.get_all_menu_items()
        cake_designs = await database.get_all_cake_designs()
        conversion_instructions_data = load_json_file(CONVERSION_INSTRUCTIONS_FILE, {})
        
        # Build context
        context = f"""
System Prompt: {system_prompt}

Shop Menu: {json.dumps(menu_items, indent=2)}
Cake Designs: {json.dumps(cake_designs, indent=2)}
Conversion Instructions: {conversion_instructions_data.get('instructions', '')}
"""
        
        # Generate new response
        response_text = ""
        if not AI_API_KEY:
            response_text = (
                f"I received your message: '{new_message}'. "
                "⚠️ AI API key not configured. Please add your API key to use the AI agent."
            )
            await database.save_chat_message(conversation_id, "bot", new_message, response_text)
        else:
            if AI_PROVIDER.lower() == "openai":
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=AI_API_KEY)
                    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                    
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": context},
                            {"role": "user", "content": new_message}
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    response_text = response.choices[0].message.content
                    await database.save_chat_message(conversation_id, "bot", new_message, response_text)
                except Exception as e:
                    error_msg = str(e)
                    if "model_not_found" in error_msg or "does not exist" in error_msg:
                        response_text = (
                            f"❌ Model Error: The model '{model}' is not available.\n\n"
                            f"✅ Valid models: gpt-4o-mini, gpt-3.5-turbo, gpt-4o, gpt-4-turbo"
                        )
                    else:
                        response_text = f"Error calling AI API: {error_msg}"
                    await database.save_chat_message(conversation_id, "bot", new_message, response_text)
            elif AI_PROVIDER.lower() == "anthropic":
                try:
                    import anthropic
                    client = anthropic.Anthropic(api_key=AI_API_KEY)
                    response = client.messages.create(
                        model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
                        max_tokens=1000,
                        system=context,
                        messages=[
                            {"role": "user", "content": new_message}
                        ]
                    )
                    response_text = response.content[0].text
                    await database.save_chat_message(conversation_id, "bot", new_message, response_text)
                except Exception as e:
                    response_text = f"Error calling AI API: {str(e)}"
                    await database.save_chat_message(conversation_id, "bot", new_message, response_text)
            else:
                response_text = (
                    f"AI Provider '{AI_PROVIDER}' not implemented. "
                    "Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY."
                )
                await database.save_chat_message(conversation_id, "bot", new_message, response_text)
        
        # Get updated history
        messages = await database.get_chat_history(conversation_id, limit=10000)
        
        return {
            "status": "success",
            "updated_message": updated_msg,
            "new_response": response_text,
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Error editing chat message: {e}")
        raise HTTPException(status_code=500, detail=f"Error editing message: {str(e)}")

@app.get("/api/chat/conversations")
async def get_all_conversations():
    """Get all conversation IDs"""
    try:
        conversations = await database.get_all_conversations()
        return {"conversations": conversations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting conversations: {str(e)}")

@app.delete("/api/chat/history/{conversation_id}")
async def delete_chat_history(conversation_id: str):
    """Delete a conversation"""
    try:
        success = await database.delete_conversation(conversation_id)
        if success:
            return {"status": "success", "message": "Conversation deleted"}
        else:
            raise HTTPException(status_code=404, detail="Conversation not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting conversation: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8891"))
    uvicorn.run(app, host="0.0.0.0", port=port)

