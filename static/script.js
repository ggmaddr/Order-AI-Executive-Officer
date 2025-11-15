// Global state
let conversationId = 'conv_' + Date.now();
let menuItemCounter = 0;
let cakeDesignCounter = 0;
let exampleCounter = 0;

// API base URL
const API_BASE = '/api';

// Navigation
function showSection(section) {
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    
    if (section === 'chat') {
        document.getElementById('chat-section').classList.add('active');
        document.querySelectorAll('.nav-btn')[0].classList.add('active');
    } else if (section === 'training') {
        document.getElementById('training-section').classList.add('active');
        document.querySelectorAll('.nav-btn')[1].classList.add('active');
        // Load all training data when switching to training section
        loadSystemPrompt();
        loadMenu();
        loadCakeDesigns();
        loadConversionInstructions();
    }
}

// Training tabs
function showTrainingTab(tab) {
    document.querySelectorAll('.training-tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById(tab + '-tab').classList.add('active');
    event.target.classList.add('active');
}

// Chat functionality
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addMessageToChat(message, 'user');
    input.value = '';
    
    // Show loading indicator
    const loadingId = addMessageToChat('Thinking...', 'bot');
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });
        
        const data = await response.json();
        
        // Remove loading message and add actual response
        removeMessage(loadingId);
        addMessageToChat(data.response, 'bot');
    } catch (error) {
        removeMessage(loadingId);
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Error:', error);
    }
}

function addMessageToChat(message, type) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    const messageId = 'msg_' + Date.now() + '_' + Math.random();
    messageDiv.id = messageId;
    messageDiv.className = `message ${type}-message`;
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${escapeHtml(message)}</p>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageId;
}

function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    addMessageToChat(`Uploading ${file.name}...`, 'user');
    const loadingId = addMessageToChat('Processing image...', 'bot');
    
    try {
        const response = await fetch(`${API_BASE}/upload-image`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        removeMessage(loadingId);
        addMessageToChat(`Image uploaded successfully: ${data.filename}`, 'bot');
    } catch (error) {
        removeMessage(loadingId);
        addMessageToChat('Error uploading image. Please try again.', 'bot');
        console.error('Error:', error);
    }
}

// System Prompt functions
async function loadSystemPrompt() {
    try {
        const response = await fetch(`${API_BASE}/system-prompt`);
        const data = await response.json();
        document.getElementById('system-prompt-text').value = data.prompt || '';
    } catch (error) {
        showError('system-prompt-tab', 'Error loading system prompt');
        console.error('Error:', error);
    }
}

async function saveSystemPrompt() {
    const prompt = document.getElementById('system-prompt-text').value;
    
    try {
        const response = await fetch(`${API_BASE}/system-prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt })
        });
        
        const data = await response.json();
        showSuccess('system-prompt-tab', 'System prompt saved successfully!');
    } catch (error) {
        showError('system-prompt-tab', 'Error saving system prompt');
        console.error('Error:', error);
    }
}

// Menu functions
async function loadMenu() {
    try {
        const response = await fetch(`${API_BASE}/menu`);
        const data = await response.json();
        const container = document.getElementById('menu-items-container');
        container.innerHTML = '';
        menuItemCounter = 0;
        
        if (data.items && data.items.length > 0) {
            data.items.forEach(item => {
                addMenuItemToUI(item);
            });
        }
    } catch (error) {
        showError('menu-tab', 'Error loading menu');
        console.error('Error:', error);
    }
}

function addMenuItem(item = null) {
    const container = document.getElementById('menu-items-container');
    const itemId = menuItemCounter++;
    
    const itemDiv = document.createElement('div');
    itemDiv.className = 'item-card';
    itemDiv.id = `menu-item-${itemId}`;
    
    itemDiv.innerHTML = `
        <input type="text" placeholder="Item Name" value="${item?.name || ''}" id="menu-name-${itemId}">
        <input type="text" placeholder="Description (optional)" value="${item?.description || ''}" id="menu-desc-${itemId}">
        <input type="number" placeholder="Price (optional)" value="${item?.price || ''}" id="menu-price-${itemId}" step="0.01">
        <input type="text" placeholder="Category (optional)" value="${item?.category || ''}" id="menu-category-${itemId}">
        <button class="remove-btn" onclick="removeMenuItem(${itemId})">Remove</button>
    `;
    
    container.appendChild(itemDiv);
}

function removeMenuItem(id) {
    const item = document.getElementById(`menu-item-${id}`);
    if (item) {
        item.remove();
    }
}

async function saveMenu() {
    const items = [];
    const itemCards = document.querySelectorAll('.item-card');
    
    itemCards.forEach(card => {
        const id = card.id.replace('menu-item-', '');
        const name = document.getElementById(`menu-name-${id}`).value.trim();
        if (name) {
            items.push({
                name: name,
                description: document.getElementById(`menu-desc-${id}`).value.trim() || null,
                price: parseFloat(document.getElementById(`menu-price-${id}`).value) || null,
                category: document.getElementById(`menu-category-${id}`).value.trim() || null
            });
        }
    });
    
    try {
        const response = await fetch(`${API_BASE}/menu`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ items: items })
        });
        
        const data = await response.json();
        showSuccess('menu-tab', 'Menu saved successfully!');
    } catch (error) {
        showError('menu-tab', 'Error saving menu');
        console.error('Error:', error);
    }
}

// Cake Designs functions
async function loadCakeDesigns() {
    try {
        const response = await fetch(`${API_BASE}/cake-designs`);
        const data = await response.json();
        const container = document.getElementById('cake-designs-container');
        container.innerHTML = '';
        cakeDesignCounter = 0;
        
        if (data.designs && data.designs.length > 0) {
            data.designs.forEach(design => {
                addCakeDesignToUI(design);
            });
        }
    } catch (error) {
        showError('cake-designs-tab', 'Error loading cake designs');
        console.error('Error:', error);
    }
}

function addCakeDesign(design = null) {
    const container = document.getElementById('cake-designs-container');
    const designId = cakeDesignCounter++;
    
    const designDiv = document.createElement('div');
    designDiv.className = 'design-card';
    designDiv.id = `cake-design-${designId}`;
    
    designDiv.innerHTML = `
        <input type="text" placeholder="Design ID" value="${design?.design_id || ''}" id="design-id-${designId}">
        <input type="text" placeholder="Design Name" value="${design?.name || ''}" id="design-name-${designId}">
        <textarea placeholder="Description" id="design-desc-${designId}" rows="3">${design?.description || ''}</textarea>
        <input type="text" placeholder="Image URL (optional)" value="${design?.image_url || ''}" id="design-image-${designId}">
        <button class="remove-btn" onclick="removeCakeDesign(${designId})">Remove</button>
    `;
    
    container.appendChild(designDiv);
}

function addCakeDesignToUI(design) {
    addCakeDesign(design);
}

function removeCakeDesign(id) {
    const design = document.getElementById(`cake-design-${id}`);
    if (design) {
        design.remove();
    }
}

async function saveCakeDesigns() {
    const designs = [];
    const designCards = document.querySelectorAll('.design-card');
    
    designCards.forEach(card => {
        const id = card.id.replace('cake-design-', '');
        const designId = document.getElementById(`design-id-${id}`).value.trim();
        const name = document.getElementById(`design-name-${id}`).value.trim();
        
        if (designId && name) {
            designs.push({
                design_id: designId,
                name: name,
                description: document.getElementById(`design-desc-${id}`).value.trim(),
                image_url: document.getElementById(`design-image-${id}`).value.trim() || null
            });
        }
    });
    
    try {
        const response = await fetch(`${API_BASE}/cake-designs`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ designs: designs })
        });
        
        const data = await response.json();
        showSuccess('cake-designs-tab', 'Cake designs saved successfully!');
    } catch (error) {
        showError('cake-designs-tab', 'Error saving cake designs');
        console.error('Error:', error);
    }
}

// Conversion Instructions functions
async function loadConversionInstructions() {
    try {
        const response = await fetch(`${API_BASE}/conversion-instructions`);
        const data = await response.json();
        document.getElementById('conversion-instructions-text').value = data.instructions || '';
        
        const container = document.getElementById('examples-container');
        container.innerHTML = '';
        exampleCounter = 0;
        
        if (data.examples && data.examples.length > 0) {
            data.examples.forEach(example => {
                addExampleToUI(example);
            });
        }
    } catch (error) {
        showError('conversion-tab', 'Error loading conversion instructions');
        console.error('Error:', error);
    }
}

function addExample(example = null) {
    const container = document.getElementById('examples-container');
    const exampleId = exampleCounter++;
    
    const exampleDiv = document.createElement('div');
    exampleDiv.className = 'example-card';
    exampleDiv.id = `example-${exampleId}`;
    
    const exampleText = example ? JSON.stringify(example, null, 2) : '';
    
    exampleDiv.innerHTML = `
        <textarea placeholder="Example JSON or text" id="example-text-${exampleId}" rows="5">${exampleText}</textarea>
        <button class="remove-btn" onclick="removeExample(${exampleId})">Remove</button>
    `;
    
    container.appendChild(exampleDiv);
}

function addExampleToUI(example) {
    addExample(example);
}

function removeExample(id) {
    const example = document.getElementById(`example-${id}`);
    if (example) {
        example.remove();
    }
}

async function saveConversionInstructions() {
    const instructions = document.getElementById('conversion-instructions-text').value;
    const examples = [];
    const exampleCards = document.querySelectorAll('.example-card');
    
    exampleCards.forEach(card => {
        const id = card.id.replace('example-', '');
        const exampleText = document.getElementById(`example-text-${id}`).value.trim();
        if (exampleText) {
            try {
                // Try to parse as JSON, if fails, store as string
                const parsed = JSON.parse(exampleText);
                examples.push(parsed);
            } catch (e) {
                examples.push(exampleText);
            }
        }
    });
    
    try {
        const response = await fetch(`${API_BASE}/conversion-instructions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                instructions: instructions,
                examples: examples
            })
        });
        
        const data = await response.json();
        showSuccess('conversion-tab', 'Conversion instructions saved successfully!');
    } catch (error) {
        showError('conversion-tab', 'Error saving conversion instructions');
        console.error('Error:', error);
    }
}

// Utility functions
function showSuccess(tabId, message) {
    const tab = document.getElementById(tabId);
    let successDiv = tab.querySelector('.success-message');
    
    if (!successDiv) {
        successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        tab.appendChild(successDiv);
    }
    
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    
    setTimeout(() => {
        successDiv.style.display = 'none';
    }, 3000);
}

function showError(tabId, message) {
    const tab = document.getElementById(tabId);
    let errorDiv = tab.querySelector('.error-message');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        tab.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    console.log('Super Receptionist AI Agent initialized');
});

