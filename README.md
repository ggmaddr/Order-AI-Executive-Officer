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
   PORT=8000
   ```

3. **Start the application:**
   ```bash
   python3 app.py
   ```

4. **Open in browser:**
   ```
   http://localhost:8000
   ```

## 🌐 Deployment

### Option 1: Render.com (Recommended - Free Tier Available)

1. **Create account** at [render.com](https://render.com)

2. **Create new Web Service:**
   - Connect your GitHub repository
   - Select "Web Service"
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`

3. **Set Environment Variables** in Render dashboard:
   ```
   PORT=8000
   MONGODB_URL=your_mongodb_atlas_connection_string
   MONGODB_DB_NAME=super_receptionist
   OPENAI_API_KEY=your_openai_key
   OPENAI_MODEL=gpt-4o-mini
   AI_PROVIDER=openai
   ```

4. **Deploy** - Render will automatically deploy on every push to main branch

### Option 2: Railway.app

1. **Create account** at [railway.app](https://railway.app)

2. **Deploy from GitHub:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Add Environment Variables:**
   - Click on your service → Variables
   - Add all variables from `.env` file

4. **Deploy** - Railway auto-detects Python and deploys automatically

### Option 3: Docker Deployment

1. **Build Docker image:**
   ```bash
   docker build -t super-receptionist .
   ```

2. **Run container:**
   ```bash
   docker run -p 8000:8000 \
     -e MONGODB_URL=your_mongodb_url \
     -e MONGODB_DB_NAME=super_receptionist \
     -e OPENAI_API_KEY=your_key \
     -e OPENAI_MODEL=gpt-4o-mini \
     super-receptionist
   ```

3. **Or use docker-compose:**
   ```yaml
   version: '3.8'
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - MONGODB_URL=${MONGODB_URL}
         - MONGODB_DB_NAME=${MONGODB_DB_NAME}
         - OPENAI_API_KEY=${OPENAI_API_KEY}
         - OPENAI_MODEL=${OPENAI_MODEL}
   ```

### Option 4: Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login and create app:**
   ```bash
   fly auth login
   fly launch
   ```

3. **Set secrets:**
   ```bash
   fly secrets set MONGODB_URL=your_url
   fly secrets set OPENAI_API_KEY=your_key
   ```

4. **Deploy:**
   ```bash
   fly deploy
   ```

### Environment Variables Required

All platforms need these environment variables:

```env
# MongoDB (Required)
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/dbname
MONGODB_DB_NAME=super_receptionist

# AI Provider (Required)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
AI_PROVIDER=openai

# Server (Optional - defaults to 8000)
PORT=8000
```

**Note:** For production, use MongoDB Atlas (cloud) instead of local MongoDB.

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
lsof -ti :8000 | xargs kill -9
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
