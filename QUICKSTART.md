# Quick Start Guide - Super Receptionist AI Agent

## How to Run the App

### Method 1: Direct Python Command (Recommended)
```bash
cd /Users/gradyta/GResources/SuperReceptionist
python3 app.py
```

### Method 2: Using the Startup Script
```bash
cd /Users/gradyta/GResources/SuperReceptionist
./run.sh
```

### Method 3: Using uvicorn directly
```bash
cd /Users/gradyta/GResources/SuperReceptionist
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

## Access the Application

Once the server starts, you'll see output like:
```
INFO:     Started server process [XXXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Open in Your Browser:
1. Open your web browser (Chrome, Firefox, Safari, etc.)
2. Navigate to: **http://localhost:8000**
3. You should see the Super Receptionist AI Agent interface

## What You'll See

### Main Interface
- **Header**: "🤖 Super Receptionist AI Agent" with navigation buttons
- **Chat Tab**: Interactive chatbot interface (default view)
- **Training Tab**: Access to all training interfaces

### Chat Interface
- Message history area (shows conversation)
- Text input field at the bottom
- Send button and image upload button (📷)

### Training Interface (Click "Training" tab)
Four training sections:
1. **System Prompt**: Fine-tune AI behavior
2. **Shop Menu**: Add menu items
3. **Cake Designs**: Add personalized designs
4. **Conversion Instructions**: Configure screenshot-to-JSON conversion

## Testing the App

### Test Chat:
1. Type a message in the chat input
2. Click "Send" or press Enter
3. You should see your message and a response

### Test Training:
1. Click the "Training" tab
2. Click "System Prompt" tab
3. Modify the text in the textarea
4. Click "Save Prompt"
5. You should see a success message

## Troubleshooting

### Port Already in Use
If you see "address already in use" error:
```bash
# Find what's using the port
lsof -i :8000

# Kill the process or use a different port
PORT=8001 python3 app.py
```

### Dependencies Not Installed
```bash
pip3 install -r requirements.txt
```

### Server Not Starting
Check Python version:
```bash
python3 --version  # Should be 3.7+
```

## Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

Or find and kill the process:
```bash
pkill -f "python.*app.py"
```

