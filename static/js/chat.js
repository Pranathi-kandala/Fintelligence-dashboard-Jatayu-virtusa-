/**
 * Fintelligence - Chat JavaScript
 * Handles AI assistant chat functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chatContainer');
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');
    const sessionId = document.getElementById('sessionId')?.value;
    
    if (!chatContainer || !chatForm || !chatInput || !sessionId) return;
    
    // Scroll chat to bottom initially
    scrollChatToBottom();
    
    // Setup chat form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        addMessageToChat(message, true);
        
        // Clear input field
        chatInput.value = '';
        
        // Add loading indicator for AI response
        const loadingElement = addLoadingIndicator();
        
        // Send message to server
        sendChatMessage(message, sessionId, loadingElement);
    });
    
    /**
     * Add a message to the chat container
     * @param {string} message - Message text
     * @param {boolean} isUser - Whether the message is from user (true) or AI (false)
     * @return {HTMLElement} The message element that was added
     */
    function addMessageToChat(message, isUser) {
        const messageElement = document.createElement('div');
        messageElement.className = isUser 
            ? 'chat-message chat-message-user' 
            : 'chat-message chat-message-ai';
        
        // Format message content
        if (!isUser) {
            // Process links in AI messages
            message = message.replace(
                /(https?:\/\/[^\s]+)/g, 
                '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
            );
            
            // Convert markdown-style formatting
            message = message
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
                .replace(/`([^`]+)`/g, '<code>$1</code>');
        }
        
        messageElement.innerHTML = message;
        chatContainer.appendChild(messageElement);
        
        // Scroll to bottom
        scrollChatToBottom();
        
        return messageElement;
    }
    
    /**
     * Add loading indicator while waiting for AI response
     * @return {HTMLElement} The loading indicator element
     */
    function addLoadingIndicator() {
        const loadingElement = document.createElement('div');
        loadingElement.className = 'chat-message chat-message-ai';
        loadingElement.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
        chatContainer.appendChild(loadingElement);
        
        // Scroll to bottom
        scrollChatToBottom();
        
        return loadingElement;
    }
    
    /**
     * Send chat message to server
     * @param {string} message - User message
     * @param {string} sessionId - Chat session ID
     * @param {HTMLElement} loadingElement - Loading indicator element to replace
     */
    function sendChatMessage(message, sessionId, loadingElement) {
        // Create form data
        const formData = new FormData();
        formData.append('message', message);
        formData.append('session_id', sessionId);
        
        // Send message to server
        fetch('/send_message', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove loading indicator
            if (loadingElement) {
                chatContainer.removeChild(loadingElement);
            }
            
            // Add AI response to chat
            if (data.success && data.ai_message) {
                addMessageToChat(data.ai_message.content, false);
            } else if (data.error) {
                addMessageToChat('Sorry, I encountered an error: ' + data.error, false);
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
            
            // Remove loading indicator
            if (loadingElement) {
                chatContainer.removeChild(loadingElement);
            }
            
            // Add error message
            addMessageToChat('Sorry, there was an error processing your request. Please try again.', false);
        });
    }
    
    /**
     * Scroll chat container to bottom
     */
    function scrollChatToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    // Add basic auto-resize functionality to chat input
    chatInput.addEventListener('input', function() {
        // Reset height
        this.style.height = 'auto';
        
        // Set new height based on content
        const newHeight = Math.min(this.scrollHeight, 150);
        this.style.height = newHeight + 'px';
    });
});
