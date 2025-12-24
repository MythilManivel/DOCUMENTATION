// Add this function to show global error alerts
function showGlobalError(message) {
  const alertDiv = document.createElement("div");
  alertDiv.className = "global-error-alert";
  alertDiv.innerHTML = `
    <div class="alert-content">
      <div class="alert-icon">⚠️</div>
      <div class="alert-text">${message}</div>
      <button class="alert-close" onclick="this.parentElement.parentElement.remove()">✕</button>
    </div>
  `;
  document.body.insertBefore(alertDiv, document.body.firstChild);
  
  // Auto-remove after 8 seconds
  setTimeout(() => {
    if (alertDiv.parentElement) {
      alertDiv.remove();
    }
  }, 8000);
}

const API_BASE_URL = "http://127.0.0.1:5000";

// Application state
const appState = {
  documentLoaded: false,
  isProcessing: false,
  lastError: null
};

// Initialize file input change handler
document.addEventListener("DOMContentLoaded", function() {
  const fileInput = document.getElementById("file");
  const uploadLabel = document.querySelector(".upload-text");
  
  fileInput.addEventListener("change", function(e) {
    if (e.target.files.length > 0) {
      const fileName = e.target.files[0].name;
      const fileSize = (e.target.files[0].size / (1024 * 1024)).toFixed(2);
      uploadLabel.textContent = `Selected: ${fileName} (${fileSize}MB)`;
      
      // Clear previous error
      appState.lastError = null;
    }
  });
  
  // Check backend health on load
  checkBackendHealth();
});

// Check if backend is running
async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: "GET"
    });
    
    if (!response.ok) {
      showGlobalError("❌ Backend server is not responding. Make sure to run: python backend/app.py");
    } else {
      const data = await response.json();
      if (data.document_loaded) {
        appState.documentLoaded = true;
      }
      console.log("✅ Backend connected successfully");
    }
  } catch (error) {
    showGlobalError("❌ Cannot connect to backend. Please run in terminal:\ncd E:\\AI document simplify\\backend\npython app.py");
  }
}

async function uploadDocument() {
  const fileInput = document.getElementById("file");
  const uploadBtn = document.getElementById("uploadBtn");
  const uploadStatus = document.getElementById("uploadStatus");
  const fileInfo = document.getElementById("fileInfo");
  
  if (!fileInput.files || fileInput.files.length === 0) {
    showStatus(uploadStatus, "Please select a file first.", "error");
    return;
  }
  
  const file = fileInput.files[0];
  
  // Validate file size (50MB)
  const MAX_FILE_SIZE = 50 * 1024 * 1024;
  if (file.size > MAX_FILE_SIZE) {
    showStatus(uploadStatus, `File too large! Maximum size is 50MB. Your file is ${(file.size / (1024 * 1024)).toFixed(2)}MB.`, "error");
    return;
  }
  
  // Validate file type
  const allowedExtensions = ['pdf', 'doc', 'docx', 'txt'];
  const fileExtension = file.name.split('.').pop().toLowerCase();
  if (!allowedExtensions.includes(fileExtension)) {
    showStatus(uploadStatus, `Unsupported file type. Allowed: ${allowedExtensions.join(', ')}`, "error");
    return;
  }
  
  const formData = new FormData();
  formData.append("file", file);
  
  // Disable button and show loading
  uploadBtn.disabled = true;
  uploadBtn.innerHTML = '<span class="loading"></span> Uploading...';
  uploadStatus.className = "status-message";
  fileInfo.className = "file-info";
  appState.isProcessing = true;
  
  try {
    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData
    });
    
    const result = await response.json();
    
    if (response.ok) {
      showStatus(uploadStatus, result.message || "File uploaded successfully!", "success");
      fileInfo.className = "file-info show";
      fileInfo.innerHTML = `
        <strong>📄 File:</strong> ${result.filename || file.name}<br>
        <strong>📊 Size:</strong> ${result.char_count?.toLocaleString() || 'N/A'} characters
      `;
      
      // Update app state
      appState.documentLoaded = true;
      
      // Clear previous summary
      document.getElementById("summary").textContent = "";
      document.getElementById("summaryStats").className = "stats";
      
      // Notify chat about new document
      addMessageToChat(`✅ Document "${result.filename || file.name}" uploaded successfully! I'm ready to answer questions about it.`, false);
    } else {
      showStatus(uploadStatus, result.error || "Upload failed. Please try again.", "error");
      appState.lastError = result.error;
    }
  } catch (error) {
    const errorMsg = `Connection error: ${error.message}. Make sure the backend server is running: python backend/app.py`;
    showStatus(uploadStatus, errorMsg, "error");
    appState.lastError = errorMsg;
  } finally {
    uploadBtn.disabled = false;
    uploadBtn.innerHTML = '<span>Upload Document</span>';
    appState.isProcessing = false;
  }
}

async function getSummary() {
  const summaryBtn = document.getElementById("summaryBtn");
  const summaryDiv = document.getElementById("summary");
  const summaryStats = document.getElementById("summaryStats");
  
  if (!appState.documentLoaded) {
    showStatus(summaryDiv, "⚠️ Please upload a document first.", "error");
    return;
  }
  
  summaryBtn.disabled = true;
  summaryBtn.innerHTML = '<span class="loading"></span> Generating...';
  summaryDiv.textContent = "";
  summaryStats.className = "stats";
  appState.isProcessing = true;
  
  try {
    const response = await fetch(`${API_BASE_URL}/summary`);
    const data = await response.json();
    
    if (response.ok) {
      summaryDiv.textContent = data.summary || "No summary available.";
      summaryDiv.className = "content-display show";
      
      if (data.original_length && data.summary_length) {
        const compressionRatio = ((1 - data.summary_length / data.original_length) * 100).toFixed(1);
        summaryStats.className = "stats show";
        summaryStats.innerHTML = `
          <strong>📄 Original:</strong> ${data.original_length.toLocaleString()} characters | 
          <strong>✂️ Summary:</strong> ${data.summary_length.toLocaleString()} characters | 
          <strong>📉 Compressed:</strong> ${compressionRatio}%
        `;
      }
      
      addMessageToChat("I've generated a summary of your document. Check the Summary section above!", false);
    } else {
      const errorMsg = data.error || "Failed to generate summary. Please try again.";
      summaryDiv.textContent = errorMsg;
      summaryDiv.className = "content-display error";
      appState.lastError = errorMsg;
    }
  } catch (error) {
    const errorMsg = `Connection error: ${error.message}. Backend server might not be running.`;
    summaryDiv.textContent = errorMsg;
    summaryDiv.className = "content-display error";
    appState.lastError = errorMsg;
  } finally {
    summaryBtn.disabled = false;
    summaryBtn.innerHTML = '<span>Generate Summary</span>';
    appState.isProcessing = false;
  }
}

// Chat functionality
let chatHistory = [];

function addMessageToChat(message, isUser = false) {
  const chatMessages = document.getElementById("chatMessages");
  const messageDiv = document.createElement("div");
  messageDiv.className = `message ${isUser ? "user-message" : "bot-message"}`;
  
  const avatar = isUser ? "👤" : "🤖";
  const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  
  messageDiv.innerHTML = `
    <div class="message-avatar">${avatar}</div>
    <div class="message-content">
      <div class="message-text">${escapeHtml(message)}</div>
      <div class="message-time">${time}</div>
    </div>
  `;
  
  chatMessages.appendChild(messageDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  
  return messageDiv;
}

function showTypingIndicator() {
  const chatMessages = document.getElementById("chatMessages");
  const typingDiv = document.createElement("div");
  typingDiv.className = "message bot-message";
  typingDiv.id = "typingIndicator";
  typingDiv.innerHTML = `
    <div class="message-avatar">🤖</div>
    <div class="message-content">
      <div class="message-text typing-indicator">
        <span></span>
        <span></span>
        <span></span>
      </div>
    </div>
  `;
  chatMessages.appendChild(typingDiv);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
  const typingIndicator = document.getElementById("typingIndicator");
  if (typingIndicator) {
    typingIndicator.remove();
  }
}

function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

async function sendChatMessage() {
  const chatInput = document.getElementById("chatInput");
  const chatSendBtn = document.getElementById("chatSendBtn");
  const question = chatInput.value.trim();
  
  if (!question) {
    return;
  }
  
  if (!appState.documentLoaded) {
    addMessageToChat("⚠️ Please upload a document first before asking questions.", false);
    chatInput.value = "";
    return;
  }
  
  // Add user message to chat
  addMessageToChat(question, true);
  chatHistory.push({ role: "user", content: question });
  
  // Clear input and disable button
  chatInput.value = "";
  chatSendBtn.disabled = true;
  chatSendBtn.innerHTML = '<span class="loading"></span>';
  appState.isProcessing = true;
  
  // Show typing indicator
  showTypingIndicator();
  
  try {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ 
        question: question,
        history: chatHistory.slice(-6) // Send last 6 messages for context
      })
    });
    
    const data = await response.json();
    
    removeTypingIndicator();
    
    if (response.ok) {
      const answer = data.answer || "I couldn't find an answer to that question.";
      addMessageToChat(answer, false);
      chatHistory.push({ role: "assistant", content: answer });
    } else {
      const errorMsg = data.error || "Failed to get response. Please make sure a document is uploaded.";
      addMessageToChat(`❌ ${errorMsg}`, false);
      appState.lastError = errorMsg;
    }
  } catch (error) {
    removeTypingIndicator();
    const errorMsg = `Connection error: ${error.message}. Backend server might not be running.`;
    addMessageToChat(`❌ ${errorMsg}`, false);
    appState.lastError = errorMsg;
  } finally {
    chatSendBtn.disabled = false;
    chatSendBtn.innerHTML = '<span>Send</span>';
    chatInput.focus();
    appState.isProcessing = false;
  }
}

function handleChatKeyPress(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendChatMessage();
  }
}

function clearChat() {
  const chatMessages = document.getElementById("chatMessages");
  chatHistory = [];
  
  // Keep only the welcome message
  chatMessages.innerHTML = `
    <div class="message bot-message">
      <div class="message-avatar">🤖</div>
      <div class="message-content">
        <div class="message-text">
          Hello! I'm your AI documentation assistant. Upload a document and I'll help you understand it better. Ask me anything about the document!
        </div>
        <div class="message-time">Just now</div>
      </div>
    </div>
  `;
}

function showStatus(element, message, type) {
  element.textContent = message;
  element.className = `status-message ${type}`;
  
  // Auto-hide success messages after 5 seconds
  if (type === "success") {
    setTimeout(() => {
      element.className = "status-message";
    }, 5000);
  }
}

function showGlobalError(message) {
  const alertDiv = document.createElement("div");
  alertDiv.className = "global-error-alert";
  alertDiv.innerHTML = `
    <div class="alert-content">
      <span class="alert-icon">⚠️</span>
      <span class="alert-text">${escapeHtml(message)}</span>
      <button class="alert-close" onclick="this.parentElement.parentElement.remove()">✕</button>
    </div>
  `;
  document.body.insertBefore(alertDiv, document.body.firstChild);
}
