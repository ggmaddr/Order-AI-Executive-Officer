# Super Receptionist - AI Agent for Order Processing

An AI-powered order processing system that extracts information from order confirmation screenshots, converts them to structured JSON, and populates spreadsheets automatically.

## Features

### 1. Chatbot UI
- Interactive chat interface for communicating with the AI agent
- Image upload support for order confirmation screenshots
- Real-time conversation handling

### 2. Training Interfaces
The system provides four training interfaces for shop owners to customize the AI agent:

#### System Prompt Fine-tuning
- Customize how the AI agent behaves and responds
- Define the agent's role and instructions

#### Shop Menu Training
- Add menu items with names, descriptions, prices, and categories
- Train the AI to recognize products in orders

#### Personalized Cake Designs
- Add custom cake designs with IDs, names, descriptions, and images
- Help the AI identify specific design requests

#### Conversion Instructions
- Provide instructions on converting text screenshots to JSON format
- Add examples for better AI understanding
- Define how to populate spreadsheets with extracted data

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd SuperReceptionist
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file (optional, for API keys):
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Running the Application

Start the FastAPI server:
```bash
python app.py
```

Or using uvicorn directly:
```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

Then open your browser and navigate to:
```
http://localhost:8000
```

## Project Structure

```
SuperReceptionist/
├── app.py                 # Main FastAPI application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── static/               # Frontend files
│   ├── index.html        # Main UI
│   ├── styles.css        # Styling
│   └── script.js         # Frontend logic
└── data/                 # Data storage (created at runtime)
    └── training/         # Training data
        ├── system_prompt.json
        ├── menu.json
        ├── cake_designs.json
        └── conversion_instructions.json
```

## Workflow

Based on the workflow diagram:

1. **Input**: Order confirmation text screenshot (with sender confirmation and client name)
2. **AI Extraction**: AI agent extracts information and generates JSON Orders for Google Sheet
   - Columns: Customer, Total $$, Date-Time, Note, orderID
3. **Order Details**: From Note and orderID, generate JSON OrderDetails
   - Create order details matching orderID
   - Create summary (total products each type by date)
4. **Invoice Generation**: Generate PDF invoice with order details, datetime, name, address, style ID

## API Endpoints

### Chat
- `POST /api/chat` - Send a message to the chatbot
- `POST /api/upload-image` - Upload an image for processing

### Training
- `GET /api/system-prompt` - Get current system prompt
- `POST /api/system-prompt` - Update system prompt
- `GET /api/menu` - Get shop menu
- `POST /api/menu` - Update shop menu
- `GET /api/cake-designs` - Get cake designs
- `POST /api/cake-designs` - Update cake designs
- `GET /api/conversion-instructions` - Get conversion instructions
- `POST /api/conversion-instructions` - Update conversion instructions

## Next Steps

- [ ] Integrate with OpenAI/Anthropic API for actual AI responses
- [ ] Implement OCR for image processing
- [ ] Add Google Sheets integration
- [ ] Implement PDF invoice generation
- [ ] Add order processing workflow automation

## License

[Your License Here]

## Contributors

- Project Manager & Lead Software Engineer

