// Common JavaScript functions for PromptComp

// Show loading spinner
function showLoading(element, text = 'Loading...') {
    const originalText = element.innerHTML;
    element.disabled = true;
    element.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> ${text}`;
    return originalText;
}

// Hide loading spinner
function hideLoading(element, originalText) {
    element.disabled = false;
    element.innerHTML = originalText;
}

// Format error message
function handleError(error, userMessage = 'An error occurred. Please try again.') {
    console.error('Error:', error);
    alert(userMessage);
}

// Format response for display
function formatResponseForDisplay(response) {
    if (!response) return '';
    
    // Convert newlines to <br> and preserve spaces
    return response
        .replace(/\n/g, '<br>')
        .replace(/  /g, '&nbsp;&nbsp;');
}

// Copy to clipboard
function copyToClipboard(text) {
    if (!text) return;
    
    navigator.clipboard.writeText(text).then(
        function() {
            // Show notification
            const notification = document.createElement('div');
            notification.className = 'copy-notification';
            notification.textContent = 'Copied to clipboard!';
            document.body.appendChild(notification);
            
            // Remove notification after 2 seconds
            setTimeout(function() {
                document.body.removeChild(notification);
            }, 2000);
        },
        function(err) {
            console.error('Could not copy text: ', err);
            handleError(err, 'Failed to copy to clipboard.');
        }
    );
}