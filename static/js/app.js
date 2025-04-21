document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const themeToggle = document.getElementById('theme-toggle-btn');
    const temperatureSlider = document.getElementById('temperature');
    const tempValue = document.getElementById('temp-value');
    const structuredToggle = document.getElementById('structured');
    const toolsToggle = document.getElementById('tools');
    const queryInput = document.getElementById('query');
    const submitButton = document.getElementById('submit');
    const chatMessages = document.getElementById('chat-messages');
    const loadingIndicator = document.getElementById('loading');
    const exampleItems = document.querySelectorAll('.example-item');
    
    // Theme toggle functionality
    themeToggle.addEventListener('click', function() {
        const html = document.documentElement;
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
    
    // Load saved theme from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }
    
    // Temperature slider
    temperatureSlider.addEventListener('input', function() {
        tempValue.textContent = this.value;
    });
    
    // Example items
    exampleItems.forEach(item => {
        item.addEventListener('click', function() {
            const query = this.getAttribute('data-query');
            queryInput.value = query;
            queryInput.focus();
        });
    });
    
    // Auto-resize textarea
    queryInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
    
    // Submit on Enter (but allow Shift+Enter for new lines)
    queryInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            submitButton.click();
        }
    });
    
    // Submit button
    submitButton.addEventListener('click', async function() {
        const query = queryInput.value.trim();
        if (!query) return;
        
        // Add user message to chat
        addMessage(query, 'user');
        
        // Clear input and reset height
        queryInput.value = '';
        queryInput.style.height = '50px';
        
        // Disable input during processing
        submitButton.disabled = true;
        queryInput.disabled = true;
        loadingIndicator.style.display = 'flex';
        
        try {
            // Get settings
            const temperature = parseFloat(temperatureSlider.value);
            const structured_output = structuredToggle.checked;
            const use_tools = toolsToggle.checked;
            
            // Send request to API
            const response = await fetch('/api/reason', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query,
                    temperature,
                    structured_output,
                    use_tools
                })
            });
            
            if (!response.ok) {
                throw new Error(`Server responded with status: ${response.status}`);
            }
            
            const data = await response.json();
            
            // Process and display response
            processResponse(data.result);
            
        } catch (error) {
            console.error('Error:', error);
            addErrorMessage(error.message);
        } finally {
            // Re-enable input
            submitButton.disabled = false;
            queryInput.disabled = false;
            loadingIndicator.style.display = 'none';
            
            // Scroll to bottom
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    });
    
    // Add message to chat
    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        if (role === 'user') {
            messageDiv.textContent = content;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }
    
    // Add error message
    function addErrorMessage(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'message assistant-message error';
        errorDiv.innerHTML = `
            <div class="error-message">
                <i class="fa-solid fa-triangle-exclamation"></i>
                <span>Error: ${message}</span>
            </div>
            <div>Please try again or adjust your settings.</div>
        `;
        chatMessages.appendChild(errorDiv);
    }
    
    // Process and display response
    function processResponse(result) {
        const messageDiv = addMessage('', 'assistant');
        
        if (result.structured === false) {
            // Unstructured response
            messageDiv.innerHTML = `<div class="unstructured-content">${formatContent(result.content)}</div>`;
            return;
        }
        
        if (result.reasoning_steps && Array.isArray(result.reasoning_steps)) {
            // Structured response with reasoning steps
            const stepsHtml = result.reasoning_steps.map((step, index) => `
                <div class="step">
                    <div class="step-title">Step ${index + 1}: ${escapeHtml(step.title)}</div>
                    <div class="step-content">${formatContent(step.content)}</div>
                </div>
            `).join('');
            
            let finalAnswer = '';
            if (result.final_answer) {
                finalAnswer = `<div class="final-answer">${formatContent(result.final_answer)}</div>`;
            }
            
            messageDiv.innerHTML = stepsHtml + finalAnswer;
        } else if (result.content) {
            // Fallback to content field
            messageDiv.innerHTML = `<div class="unstructured-content">${formatContent(result.content)}</div>`;
        } else {
            // Unknown format
            messageDiv.textContent = 'Received an unexpected response format.';
        }
    }
    
    // Format content with basic markdown
    function formatContent(content) {
        if (!content) return '';
        
        // Escape HTML
        let formatted = escapeHtml(content);
        
        // Convert markdown-style formatting
        formatted = formatted
            // Bold
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // Italic
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            // Code
            .replace(/`(.*?)`/g, '<code>$1</code>')
            // Line breaks
            .replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    // Escape HTML to prevent XSS
    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
