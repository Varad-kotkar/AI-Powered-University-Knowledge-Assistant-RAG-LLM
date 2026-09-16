// DOM Elements
const questionInput = document.getElementById('questionInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const sourcesSection = document.getElementById('sourcesSection');
const sourcesList = document.getElementById('sourcesList');
const actionChips = document.querySelectorAll('.action-chip');

// Context selectors
const programSelect = document.getElementById('program');
const branchSelect = document.getElementById('branch');
const yearSelect = document.getElementById('year');
const semesterSelect = document.getElementById('semester');

// API endpoint
const API_URL = '/query';

// Event Listeners
sendButton.addEventListener('click', handleSendQuestion);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSendQuestion();
    }
});

// Quick action chips
actionChips.forEach(chip => {
    chip.addEventListener('click', () => {
        const action = chip.dataset.action;
        handleQuickAction(action);
    });
});

// Handle quick action clicks
function handleQuickAction(action) {
    const actionPrompts = {
        syllabus: 'What is the syllabus for my current semester?',
        pyqs: 'Find previous-year question papers for my subjects.',
        notices: 'What are the latest examination notices?',
        academic: 'Ask an academic question about my program.'
    };
    
    questionInput.value = actionPrompts[action] || '';
    questionInput.focus();
}

// Get student context from selectors
function getStudentContext() {
    const program = programSelect.value || null;
    const branch = branchSelect.value || null;
    const year = yearSelect.value || null;
    const semester = semesterSelect.value || null;
    
    if (program || branch || year || semester) {
        return { program, branch, year, semester };
    }
    return null;
}

// Handle sending a question
async function handleSendQuestion() {
    const question = questionInput.value.trim();
    
    if (!question) {
        return;
    }
    
    // Disable input while processing
    questionInput.disabled = true;
    sendButton.disabled = true;
    
    // Add user message to chat
    addMessage(question, 'user');
    
    // Clear input
    questionInput.value = '';
    
    // Add thinking indicator
    addThinkingMessage();
    
    try {
        // Get student context
        const studentContext = getStudentContext();
        
        // Prepare request payload
        const payload = {
            question: question
        };
        
        if (studentContext) {
            payload.student_context = studentContext;
        }
        
        // Send request to API
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });
        
        // Remove thinking message
        removeThinkingMessage();
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Add assistant response
        addMessage(data.answer, 'assistant');
        
        // Display sources if available
        if (data.sources && data.sources.length > 0) {
            displaySources(data.sources);
        } else {
            sourcesSection.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Error:', error);
        removeThinkingMessage();
        addMessage('Sorry, I encountered an error processing your question. Please try again.', 'assistant');
        sourcesSection.style.display = 'none';
    } finally {
        // Re-enable input
        questionInput.disabled = false;
        sendButton.disabled = false;
        questionInput.focus();
    }
}

// Add a message to the chat
function addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = text;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Add thinking indicator
function addThinkingMessage() {
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'message thinking';
    thinkingDiv.id = 'thinking-message';
    thinkingDiv.textContent = 'Thinking...';
    chatMessages.appendChild(thinkingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Remove thinking indicator
function removeThinkingMessage() {
    const thinkingMessage = document.getElementById('thinking-message');
    if (thinkingMessage) {
        thinkingMessage.remove();
    }
}

// Display sources
function displaySources(sources) {
    sourcesSection.style.display = 'block';
    sourcesList.innerHTML = '';
    
    sources.forEach(source => {
        const sourceItem = document.createElement('div');
        sourceItem.className = 'source-item';
        
        sourceItem.innerHTML = `
            <div class="source-category">${source.category}</div>
            <div class="source-header">
                <span class="source-name">${source.source}</span>
                <span class="source-page">Page ${source.page}</span>
            </div>
            <div class="source-score">Relevance Score: ${(source.score * 100).toFixed(2)}%</div>
        `;
        
        sourcesList.appendChild(sourceItem);
    });
    
    // Scroll to sources
    sourcesSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    questionInput.focus();
});
