"""
Super Receptionist - AI Agent for Order Processing
Main FastAPI application with chatbot and training interfaces
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Super Receptionist AI Agent")

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
    print("⚠️  WARNING: AI_API_KEY not found in environment variables!")
    print("   Please set OPENAI_API_KEY, ANTHROPIC_API_KEY, or AI_API_KEY in your .env file")
    print("   The chatbot will work but with placeholder responses.")

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
    
    # Load training data for context
    menu_data = load_json_file(MENU_FILE, {})
    cake_designs_data = load_json_file(CAKE_DESIGNS_FILE, {})
    conversion_instructions_data = load_json_file(CONVERSION_INSTRUCTIONS_FILE, {})
    
    # ============================================================================
    # AI AGENT INTEGRATION - Add your AI API calls here
    # ============================================================================
    
    if not AI_API_KEY:
        # Fallback response when API key is not configured
        response_text = (
            f"I received your message: '{message.message}'. "
            "⚠️ AI API key not configured. Please add your API key to use the AI agent."
        )
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

Shop Menu: {json.dumps(menu_data.get('items', []), indent=2)}
Cake Designs: {json.dumps(cake_designs_data.get('designs', []), indent=2)}
Conversion Instructions: {conversion_instructions_data.get('instructions', '')}
"""
                
                # Model selection - Use fast/cost-effective models for quick responses
                # Options: "gpt-4o-mini" (fast, cheap), "gpt-3.5-turbo" (very fast), "gpt-4o" (better quality)
                model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                
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
                
            except Exception as e:
                response_text = f"Error calling AI API: {str(e)}"
        
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

Shop Menu: {json.dumps(menu_data.get('items', []), indent=2)}
Cake Designs: {json.dumps(cake_designs_data.get('designs', []), indent=2)}
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
                
            except Exception as e:
                response_text = f"Error calling AI API: {str(e)}"
        
        # ========================================================================
        # Add your custom AI provider here
        # ========================================================================
        else:
            response_text = (
                f"AI Provider '{AI_PROVIDER}' not implemented. "
                "Please configure OPENAI_API_KEY or ANTHROPIC_API_KEY, "
                "or implement your custom provider."
            )
    
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
    """Update system prompt for fine-tuning"""
    save_json_file(SYSTEM_PROMPT_FILE, {"prompt": update.prompt})
    return {"status": "success", "message": "System prompt updated successfully"}

@app.get("/api/menu")
async def get_menu():
    """Get shop menu"""
    return load_json_file(MENU_FILE, {"items": []})

@app.post("/api/menu")
async def update_menu(update: MenuUpdate):
    """Update shop menu"""
    menu_data = {"items": [item.dict() for item in update.items]}
    save_json_file(MENU_FILE, menu_data)
    return {"status": "success", "message": "Menu updated successfully"}

@app.get("/api/cake-designs")
async def get_cake_designs():
    """Get personalized cake designs"""
    return load_json_file(CAKE_DESIGNS_FILE, {"designs": []})

@app.post("/api/cake-designs")
async def update_cake_designs(update: CakeDesignsUpdate):
    """Update personalized cake designs"""
    designs_data = {"designs": [design.dict() for design in update.designs]}
    save_json_file(CAKE_DESIGNS_FILE, designs_data)
    return {"status": "success", "message": "Cake designs updated successfully"}

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

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", "8891"))
    uvicorn.run(app, host="0.0.0.0", port=port)

