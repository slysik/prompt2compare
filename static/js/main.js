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
function handleError(error, userMessage = null) {
    console.error('Error:', error);
    const message = userMessage || (error.message ? `Error: ${error.message}` : 'An error occurred. Please try again.');
    alert(message);
}

// Format response for display
function formatResponseForDisplay(response) {
    if (!response) return '';
    
    // Split the response by lines
    const lines = response.split('\n');
    
    // Check for markdown table pattern
    // A markdown table has a header row, a separator row with dashes and pipes, and data rows
    const isMarkdownTable = lines.length >= 3 && 
                           lines[0].includes('|') && 
                           lines[1].includes('|') && 
                           lines[1].includes('-') &&
                           lines[2].includes('|');
    
    if (isMarkdownTable) {
        // Process as a markdown table
        try {
            // Find header row
            const headerRow = lines[0];
            // Extract column headers from the header row
            const headers = headerRow.split('|')
                .map(header => header.trim())
                .filter(header => header.length > 0);
            
            // Start building the HTML table
            let htmlTable = '<table class="response-table md-table">';
            
            // Add header row
            htmlTable += '<thead><tr>';
            headers.forEach(header => {
                htmlTable += `<th class="md-table-header">${header}</th>`;
            });
            htmlTable += '</tr></thead>';
            
            // Add table body
            htmlTable += '<tbody>';
            
            // Skip header row and separator row (lines[0] and lines[1])
            for (let i = 2; i < lines.length; i++) {
                const line = lines[i].trim();
                if (line && line.includes('|')) {
                    htmlTable += '<tr>';
                    
                    // Split the line by pipe and remove the empty first and last elements if any
                    const cells = line.split('|')
                        .map(cell => cell.trim())
                        .filter((cell, index, array) => 
                            // Keep only non-empty cells or those that represent genuine empty table cells
                            index > 0 && index < array.length - 1 || cell.length > 0
                        );
                    
                    cells.forEach(cell => {
                        htmlTable += `<td class="md-table-cell">${cell}</td>`;
                    });
                    
                    htmlTable += '</tr>';
                }
            }
            
            htmlTable += '</tbody></table>';
            return htmlTable;
            
        } catch (error) {
            console.error('Error parsing markdown table:', error);
            // Fall back to simple format if parsing fails
            return formatAsSimpleTable(response);
        }
    }
    
    // Check for list format
    const listItemPattern = /^\s*(\d+[\.\):]|\*|\-|\•)\s+/;
    const hasListItems = lines.some(line => listItemPattern.test(line));
    
    if (hasListItems) {
        return formatAsList(lines, listItemPattern);
    }
    
    // Default: format as simple table
    return formatAsSimpleTable(response);
}

// Format as list with two columns
function formatAsList(lines, listItemPattern) {
    let tableRows = '';
    
    lines.forEach(line => {
        if (line.trim()) {
            // Check if line starts with a number or bullet
            if (listItemPattern.test(line)) {
                // This is a new item - create a new row
                const match = line.match(listItemPattern);
                const prefix = match[1];
                const content = line.replace(listItemPattern, '');
                
                tableRows += `
                <tr>
                    <td class="response-cell-id">${prefix}</td>
                    <td class="response-cell-content">${content.replace(/  /g, '&nbsp;&nbsp;')}</td>
                </tr>`;
            } else {
                // This is a continuation of the previous item
                tableRows += `
                <tr>
                    <td class="response-cell-id"></td>
                    <td class="response-cell-content">${line.replace(/  /g, '&nbsp;&nbsp;')}</td>
                </tr>`;
            }
        }
    });
    
    return `
    <table class="response-table structured-table">
        <thead>
            <tr>
                <th class="response-header-id">#</th>
                <th class="response-header-content">Content</th>
            </tr>
        </thead>
        <tbody>
            ${tableRows}
        </tbody>
    </table>`;
}

// Format as simple table
function formatAsSimpleTable(response) {
    return `
    <table class="response-table">
        <tr>
            <td class="response-cell">${response
                .replace(/\n/g, '<br>')
                .replace(/  /g, '&nbsp;&nbsp;')}</td>
        </tr>
    </table>`;
}

// Copy to clipboard
function copyToClipboard(text) {
    if (!text) return;
    
    // Get plain text without HTML formatting
    const plainText = text.replace(/<br>/g, '\n').replace(/&nbsp;/g, ' ');
    
    navigator.clipboard.writeText(plainText).then(
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