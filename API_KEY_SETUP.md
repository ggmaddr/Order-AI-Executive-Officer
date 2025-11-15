# AI Agent API Key Setup Guide

## Where to Add Your API Key

### Option 1: Using .env File (RECOMMENDED)

1. Create a `.env` file in the project root directory:
```bash
touch .env
```

2. Add your API key to the `.env` file:
```env
# For OpenAI
OPENAI_API_KEY=sk-your-openai-api-key-here
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4

# OR for Anthropic
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
AI_PROVIDER=anthropic
ANTHROPIC_MODEL=claude-3-opus-20240229

# OR use a generic key name
AI_API_KEY=your-api-key-here
AI_PROVIDER=openai
```

3. The `.env` file is already in `.gitignore`, so your API key won't be committed to git.

### Option 2: Set Environment Variable Directly

**On macOS/Linux:**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
export AI_PROVIDER="openai"
```

**On Windows:**
```cmd
set OPENAI_API_KEY=sk-your-api-key-here
set AI_PROVIDER=openai
```

### Option 3: Directly in Code (NOT RECOMMENDED)

You can also set it directly in `app.py` at **line 34**, but this is NOT recommended for production:

```python
# Option 2: Or set directly here (NOT RECOMMENDED for production)
AI_API_KEY = "your-api-key-here"
```

## Code Locations

### API Key Configuration
**File:** `app.py`  
**Lines:** 22-42

```python
# ============================================================================
# AI AGENT API KEY CONFIGURATION
# ============================================================================
AI_API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") or os.getenv("AI_API_KEY")
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
```

### AI Integration Code
**File:** `app.py`  
**Lines:** 139-241

The chat endpoint (`/api/chat`) uses the API key to call your chosen AI provider.

## Supported AI Providers

### OpenAI
- **Environment Variable:** `OPENAI_API_KEY`
- **Model Variable:** `OPENAI_MODEL` (default: "gpt-4")
- **Get API Key:** https://platform.openai.com/api-keys

### Anthropic (Claude)
- **Environment Variable:** `ANTHROPIC_API_KEY`
- **Model Variable:** `ANTHROPIC_MODEL` (default: "claude-3-opus-20240229")
- **Get API Key:** https://console.anthropic.com/

### Custom Provider
Add your custom AI provider integration in the `chat()` function starting at line 228.

## Testing Your Setup

1. Start the server:
```bash
python app.py
```

2. Check the console output. You should see:
   - ✅ No warning if API key is found
   - ⚠️ Warning message if API key is missing

3. Test in the UI:
   - Open http://localhost:8891
   - Go to the Chat tab
   - Send a message
   - If configured correctly, you'll get AI responses
   - If not configured, you'll see a warning message

## Troubleshooting

### "AI_API_KEY not found" Warning
- Make sure your `.env` file is in the project root
- Check that the variable name matches exactly (case-sensitive)
- Restart the server after adding/changing the `.env` file

### "Error calling AI API"
- Verify your API key is valid
- Check your API provider account has credits/quota
- Ensure you have the required Python packages installed:
  ```bash
  pip install openai  # For OpenAI
  pip install anthropic  # For Anthropic
  ```

### API Key Not Working
- Double-check the API key has no extra spaces
- Verify the API provider is correct (`AI_PROVIDER` setting)
- Check API provider status page for outages

