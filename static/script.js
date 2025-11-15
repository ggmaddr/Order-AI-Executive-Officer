// Global state
// Persistent conversation ID using localStorage
let conversationId = localStorage.getItem('conversationId') || 'conv_' + Date.now();
localStorage.setItem('conversationId', conversationId);

// Store message IDs for editing
let messageIdMap = new Map(); // messageId -> MongoDB _id

let menuItemCounter = 0;
let cakeDesignCounter = 0;
let exampleCounter = 0;

// API base URL
const API_BASE = '/api';

// Load chat history on page load
document.addEventListener('DOMContentLoaded', function() {
    loadChatHistory();
});

async function loadChatHistory() {
    try {
        if (!conversationId) {
            conversationId = localStorage.getItem('conversationId') || 'conv_' + Date.now();
            localStorage.setItem('conversationId', conversationId);
        }
        
        const response = await fetch(`${API_BASE}/chat/history/${conversationId}`);
        
        if (!response.ok) {
            return;
        }
        
        const data = await response.json();
        
        if (data.messages && data.messages.length > 0) {
            const messagesContainer = document.getElementById('chat-messages');
            if (messagesContainer) {
                messagesContainer.innerHTML = '';
                
                data.messages.forEach(msg => {
                    if (msg.role === 'user') {
                        const msgId = addMessageToChat(msg.message, 'user', msg._id);
                        if (msg._id) {
                            messageIdMap.set(msgId, msg._id);
                        }
                    } else if (msg.role === 'bot') {
                        const botMessage = msg.response || msg.message || '...';
                        addMessageToChat(botMessage, 'bot', msg._id);
                    }
                });
                
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
    } catch (error) {
        // Silently handle errors - keep default welcome message
    }
}

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
    
    // Ensure conversation ID is set and persisted
    if (!conversationId) {
        conversationId = localStorage.getItem('conversationId') || 'conv_' + Date.now();
    }
    localStorage.setItem('conversationId', conversationId);
    
    // Add user message to chat (temporary, will be replaced with DB ID after save)
    const userMsgId = addMessageToChat(message, 'user');
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
        
        // Update conversation ID if returned from server
        if (data.conversation_id) {
            conversationId = data.conversation_id;
            localStorage.setItem('conversationId', conversationId);
        }
        
        // Remove loading message and add actual response
        removeMessage(loadingId);
        
        // Reload chat history to get proper message IDs
        await loadChatHistory();
    } catch (error) {
        removeMessage(loadingId);
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
    }
}

async function editMessage(messageElementId, dbMessageId, currentText) {
    const messageDiv = document.getElementById(messageElementId);
    if (!messageDiv) return;
    
    const messageContent = messageDiv.querySelector('.message-content p');
    if (!messageContent) return;
    
    // Create input field for editing
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentText;
    input.className = 'edit-message-input';
    input.style.width = '100%';
    input.style.padding = '8px';
    input.style.margin = '4px 0';
    input.style.border = '1px solid rgba(0, 255, 255, 0.3)';
    input.style.borderRadius = '4px';
    input.style.background = 'rgba(0, 0, 0, 0.3)';
    input.style.color = '#fff';
    
    // Replace content with input
    const originalText = messageContent.textContent;
    messageContent.style.display = 'none';
    messageContent.parentNode.insertBefore(input, messageContent);
    input.focus();
    input.select();
    
    // Create save and cancel buttons
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginTop = '8px';
    
    const saveBtn = document.createElement('button');
    saveBtn.textContent = 'Save & Regenerate';
    saveBtn.className = 'edit-save-btn';
    saveBtn.style.marginRight = '8px';
    saveBtn.style.padding = '6px 12px';
    saveBtn.style.background = 'rgba(0, 255, 255, 0.2)';
    saveBtn.style.border = '1px solid rgba(0, 255, 255, 0.3)';
    saveBtn.style.borderRadius = '4px';
    saveBtn.style.color = '#00ffff';
    saveBtn.style.cursor = 'pointer';
    
    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = 'Cancel';
    cancelBtn.className = 'edit-cancel-btn';
    cancelBtn.style.padding = '6px 12px';
    cancelBtn.style.background = 'rgba(255, 68, 68, 0.2)';
    cancelBtn.style.border = '1px solid rgba(255, 68, 68, 0.3)';
    cancelBtn.style.borderRadius = '4px';
    cancelBtn.style.color = '#ff6b6b';
    cancelBtn.style.cursor = 'pointer';
    
    buttonContainer.appendChild(saveBtn);
    buttonContainer.appendChild(cancelBtn);
    messageContent.parentNode.insertBefore(buttonContainer, messageContent.nextSibling);
    
    const cleanup = () => {
        input.remove();
        buttonContainer.remove();
        messageContent.style.display = '';
    };
    
    cancelBtn.onclick = cleanup;
    
    input.onkeydown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            saveBtn.click();
        } else if (e.key === 'Escape') {
            cleanup();
        }
    };
    
    saveBtn.onclick = async () => {
        const newText = input.value.trim();
        if (!newText || newText === originalText) {
            cleanup();
            return;
        }
        
        // Show loading
        saveBtn.disabled = true;
        saveBtn.textContent = 'Regenerating...';
        
        try {
            const response = await fetch(`${API_BASE}/chat/edit/${dbMessageId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: newText,
                    conversation_id: conversationId
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Reload chat history to show updated messages
                await loadChatHistory();
            } else {
                alert('Error updating message');
                cleanup();
            }
        } catch (error) {
            alert('Error updating message');
            cleanup();
        }
    };
}

function formatMessageContent(text) {
    // Split by code blocks (```language\ncode\n``` or ```\ncode\n```)
    const codeBlockRegex = /```(\w+)?\n?([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    
    while ((match = codeBlockRegex.exec(text)) !== null) {
        // Add text before code block
        if (match.index > lastIndex) {
            const textPart = text.substring(lastIndex, match.index);
            if (textPart.trim()) {
                parts.push({ type: 'text', content: textPart });
            }
        }
        
        // Add code block
        const language = match[1] || 'text';
        const code = match[2].trim();
        if (code) {
            parts.push({ type: 'code', language: language, content: code });
        }
        
        lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
        const textPart = text.substring(lastIndex);
        if (textPart.trim()) {
            parts.push({ type: 'text', content: textPart });
        }
    }
    
    // If no code blocks found, return original text
    if (parts.length === 0) {
        parts.push({ type: 'text', content: text });
    }
    
    return parts;
}

function addMessageToChat(message, type, dbId = null) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    const messageId = 'msg_' + Date.now() + '_' + Math.random();
    messageDiv.id = messageId;
    messageDiv.className = `message ${type}-message`;
    if (dbId) {
        messageDiv.setAttribute('data-db-id', dbId);
    }
    
    const messageContent = document.createElement('div');
    messageContent.className = 'message-content';
    
    // Format message content (handle code blocks for bot messages)
    if (type === 'bot' && message.includes('```')) {
        const parts = formatMessageContent(message);
        parts.forEach(part => {
            if (part.type === 'text') {
                // Format text with line breaks
                const textDiv = document.createElement('div');
                textDiv.className = 'message-text';
                const lines = part.content.split('\n');
                lines.forEach((line) => {
                    const p = document.createElement('p');
                    p.textContent = line || '\u00A0'; // Non-breaking space for empty lines
                    textDiv.appendChild(p);
                });
                messageContent.appendChild(textDiv);
            } else if (part.type === 'code') {
                // Create code block
                const codeContainer = document.createElement('div');
                codeContainer.className = 'code-block-container';
                
                const codeHeader = document.createElement('div');
                codeHeader.className = 'code-block-header';
                codeHeader.textContent = part.language || 'code';
                
                const codeBlock = document.createElement('pre');
                codeBlock.className = 'code-block';
                const codeElement = document.createElement('code');
                codeElement.textContent = part.content;
                codeBlock.appendChild(codeElement);
                
                codeContainer.appendChild(codeHeader);
                codeContainer.appendChild(codeBlock);
                messageContent.appendChild(codeContainer);
            }
        });
    } else {
        // Simple text message
        const messageText = document.createElement('div');
        messageText.className = 'message-text';
        const lines = message.split('\n');
        lines.forEach((line, index) => {
            const p = document.createElement('p');
            p.textContent = line || '\u00A0';
            messageText.appendChild(p);
        });
        messageContent.appendChild(messageText);
    }
    
    // Add edit button for user messages
    if (type === 'user' && dbId) {
        const editBtn = document.createElement('button');
        editBtn.className = 'edit-message-btn';
        editBtn.innerHTML = '✏️';
        editBtn.title = 'Edit message';
        editBtn.onclick = () => editMessage(messageId, dbId, message);
        messageContent.appendChild(editBtn);
    }
    
    messageDiv.appendChild(messageContent);
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
        const promptText = data.prompt || '';
        document.getElementById('system-prompt-text').value = promptText;
        
        // Show warning if prompt exists
        const warningDiv = document.getElementById('system-prompt-warning');
        if (warningDiv) {
            if (promptText.trim()) {
                warningDiv.style.display = 'block';
            } else {
                warningDiv.style.display = 'none';
            }
        }
    } catch (error) {
        showError('system-prompt-tab', 'Error loading system prompt');
        console.error('Error:', error);
    }
}

async function saveSystemPrompt() {
    const prompt = document.getElementById('system-prompt-text').value;
    
    // Confirm overwrite if there's existing content
    const currentPrompt = document.getElementById('system-prompt-text').value;
    if (currentPrompt.trim()) {
        const confirmOverwrite = confirm('⚠️ This will overwrite your existing system prompt. Continue?');
        if (!confirmOverwrite) {
            return;
        }
    }
    
    try {
        const response = await fetch(`${API_BASE}/system-prompt`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt })
        });
        
        const data = await response.json();
        showSuccess('system-prompt-tab', 'System prompt saved and overwritten successfully!');
        // Hide warning after successful save
        const warningDiv = document.getElementById('system-prompt-warning');
        if (warningDiv) {
            warningDiv.style.display = 'none';
        }
    } catch (error) {
        showError('system-prompt-tab', 'Error saving system prompt');
        console.error('Error:', error);
    }
}

function clearSystemPrompt() {
    if (confirm('Are you sure you want to clear the system prompt? This cannot be undone unless you have a backup.')) {
        document.getElementById('system-prompt-text').value = '';
        const warningDiv = document.getElementById('system-prompt-warning');
        if (warningDiv) {
            warningDiv.style.display = 'none';
        }
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
                addMenuItem(item);
            });
            menuItemCounter = data.items.length;
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
    // Application initialized
});

