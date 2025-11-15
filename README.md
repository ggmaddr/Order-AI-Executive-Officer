# Super Receptionist - AI Agent for Order Processing

An AI-powered order processing system that extracts information from order confirmation screenshots, converts them to structured JSON, and populates spreadsheets automatically.

## ✨ Features

### 🤖 AI Chatbot
- Interactive chat interface with persistent conversation history
- Image upload support for order confirmation screenshots
- Real-time conversation handling with AI agent

### 📊 Persistent Data Storage (MongoDB)
- **Menu Items**: Saved forever in MongoDB
- **Cake Designs**: Images stored in MongoDB with binary data support
- **Chat History**: All conversations persist across restarts
- **Persistent Conversations**: Same conversation ID across sessions

### 🎓 Training Interfaces
Four training interfaces for shop owners to customize the AI agent:

1. **System Prompt Fine-tuning** - Customize AI behavior
2. **Shop Menu Training** - Add menu items with prices and categories
3. **Personalized Cake Designs** - Add custom designs with images
4. **Conversion Instructions** - Define screenshot-to-JSON conversion rules

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (local or Atlas cloud)
- OpenAI API key (or Anthropic)

### Installation

1. **Clone and setup:**
   ```bash
   cd SuperReceptionist
   ./setup_mongodb.sh
   ```

2. **Configure `.env` file:**
   ```env
   # AI Configuration
   OPENAI_API_KEY=sk-your-key-here
   OPENAI_MODEL=gpt-4o-mini
   AI_PROVIDER=openai

   # MongoDB Configuration
   MONGODB_URL=mongodb://localhost:27017
   MONGODB_DB_NAME=super_receptionist

   # Server
   PORT=8891
   ```

3. **Start the application:**
   ```bash
   python3 app.py
   ```

4. **Open in browser:**
   ```
   http://localhost:8891
   ```

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Complete setup guide
- **[MONGODB_SETUP.md](MONGODB_SETUP.md)** - MongoDB installation and configuration
- **[API_KEY_SETUP.md](API_KEY_SETUP.md)** - AI API key configuration
- **[PORT_MANAGEMENT.md](PORT_MANAGEMENT.md)** - Port management guide

## 🏗️ Project Structure

```
SuperReceptionist/
├── app.py                 # Main FastAPI application
├── database.py            # MongoDB database operations
├── requirements.txt       # Python dependencies
├── setup_mongodb.sh       # MongoDB setup script
├── static/               # Frontend files
│   ├── index.html        # Main UI
│   ├── styles.css        # Dark modern scientific theme
│   └── script.js         # Frontend logic with localStorage
└── data/                 # Local data (backup, not used with MongoDB)
    └── training/         # Training data (legacy JSON files)
```

## 🔌 API Endpoints

### Chat
- `POST /api/chat` - Send message to chatbot
- `GET /api/chat/history/{conversation_id}` - Get chat history
- `GET /api/chat/conversations` - List all conversations
- `DELETE /api/chat/history/{conversation_id}` - Delete conversation
- `POST /api/upload-image` - Upload image for processing

### Training
- `GET/POST /api/system-prompt` - System prompt management
- `GET/POST /api/menu` - Menu items (MongoDB)
- `GET/POST /api/cake-designs` - Cake designs (MongoDB)
- `GET/POST /api/conversion-instructions` - Conversion instructions

## 💾 Data Persistence

All data is stored in MongoDB:
- **Collections**: `menu_items`, `cake_designs`, `chat_history`
- **Images**: Stored as binary data in MongoDB
- **Conversations**: Persistent across sessions using localStorage

## 🎨 UI Features

- **Dark Modern Scientific Theme** - Professional dark UI with cyan accents
- **Responsive Design** - Works on desktop and mobile
- **Real-time Updates** - Instant feedback on all operations
- **Chat History** - Auto-loads previous conversations

## 🔧 Troubleshooting

### MongoDB Connection Failed
- Check MongoDB is running: `brew services list` (macOS) or `sudo systemctl status mongodb` (Linux)
- Verify `MONGODB_URL` in `.env`
- For Atlas: Check network access and credentials

### Port Already in Use
```bash
lsof -ti :8891 | xargs kill -9
```

### Data Not Persisting
- Check console for MongoDB connection message
- Verify `.env` configuration
- Check MongoDB logs

## 📝 Workflow

Based on the workflow diagram:

1. **Input**: Order confirmation text screenshot
2. **AI Extraction**: Extract info and generate JSON Orders for Google Sheet
   - Columns: Customer, Total $$, Date-Time, Note, orderID
3. **Order Details**: Generate JSON OrderDetails from Note and orderID
   - Create order details matching orderID
   - Create summary (total products each type by date)
4. **Invoice Generation**: Generate PDF invoice with order details

## 🚧 Next Steps

- [ ] Integrate Google Sheets API
- [ ] Implement OCR for image processing
- [ ] Add PDF invoice generation
- [ ] Implement order processing workflow automation

## 📄 License

[Your License Here]

## 👥 Contributors

- Project Manager & Lead Software Engineer

---

**Made with ❤️ for efficient order processing**
