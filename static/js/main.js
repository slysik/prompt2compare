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
    
    console.log('Formatting response:', response);
    
    // Split the response by lines
    const lines = response.split('\n');
    
    // More aggressive table detection - check for any content with pipe characters
    // that might be a table
    const tablePattern = /\|.*\|/;
    const hasPipes = lines.some(line => tablePattern.test(line));
    
    // A markdown table ideally has a header row, a separator row with dashes and pipes, and data rows
    const isMarkdownTable = lines.length >= 3 && 
                            lines[0].includes('|') && 
                            lines[1].includes('|') && 
                            lines[1].includes('-') &&
                            lines[2].includes('|');
    
    // If we detect a well-formed markdown table OR any content with pipes that might be a table
    if (isMarkdownTable || hasPipes) {
        console.log('Detected markdown table format');
        // Process as a markdown table
        try {
            // First, let's clean up the table format if it's not perfectly formatted
            let cleanLines = [...lines];
            
            // If the first line doesn't have pipes but subsequent lines do, we might
            // have a table with text before it
            if (!cleanLines[0].includes('|') && cleanLines.some(line => line.includes('|'))) {
                // Find the first line with a pipe
                const firstTableLineIndex = cleanLines.findIndex(line => line.includes('|'));
                if (firstTableLineIndex > 0) {
                    // Keep any text before the table separately
                    const textBeforeTable = cleanLines.slice(0, firstTableLineIndex).join('<br>');
                    cleanLines = cleanLines.slice(firstTableLineIndex);
                    
                    // If we couldn't properly extract a table, return the original text
                    if (cleanLines.length < 2) {
                        return formatAsSimpleTable(response);
                    }
                }
            }
            
            // Try to find the header row
            let headerRowIndex = 0;
            while (headerRowIndex < cleanLines.length && !cleanLines[headerRowIndex].includes('|')) {
                headerRowIndex++;
            }
            
            // If we couldn't find a header row with pipes, this isn't a table
            if (headerRowIndex >= cleanLines.length) {
                return formatAsSimpleTable(response);
            }
            
            // Extract column headers from the header row
            const headerRow = cleanLines[headerRowIndex];
            const rawHeaders = headerRow.split('|');
            // Filter out empty headers
            const headers = rawHeaders
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
            
            // Determine where to start looking for data rows
            let dataStartIndex = headerRowIndex + 1;
            
            // If there's a separator row (with dashes), skip it
            if (dataStartIndex < cleanLines.length && 
                cleanLines[dataStartIndex].includes('|') && 
                cleanLines[dataStartIndex].includes('-')) {
                dataStartIndex++;
            }
            
            // Process data rows
            for (let i = dataStartIndex; i < cleanLines.length; i++) {
                const line = cleanLines[i].trim();
                if (line && line.includes('|')) {
                    htmlTable += '<tr>';
                    
                    // Split the line by pipe
                    const cellValues = line.split('|');
                    
                    // Process cells - skip first and last if they're empty (common in markdown tables)
                    const processedCells = [];
                    for (let j = 0; j < cellValues.length; j++) {
                        const cell = cellValues[j].trim();
                        // First or last cell might be empty due to leading/trailing pipe
                        if ((j === 0 || j === cellValues.length - 1) && cell === '') {
                            continue;
                        }
                        processedCells.push(cell);
                    }
                    
                    // Add cells to row
                    processedCells.forEach(cell => {
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
    let currentItem = null;
    let currentContent = '';
    
    lines.forEach(line => {
        const trimmedLine = line.trim();
        if (trimmedLine) {
            // Check if line starts with a number or bullet
            if (listItemPattern.test(trimmedLine)) {
                // If we already have an item, add it to the table rows
                if (currentItem !== null) {
                    tableRows += `
                    <tr>
                        <td class="response-cell-id">${currentItem}</td>
                        <td class="response-cell-content">${currentContent}</td>
                    </tr>`;
                }
                
                // Start a new item
                const match = trimmedLine.match(listItemPattern);
                currentItem = match[1];
                currentContent = trimmedLine.replace(listItemPattern, '').replace(/  /g, '&nbsp;&nbsp;');
            } else if (currentItem !== null) {
                // This is a continuation of the previous item
                currentContent += '<br>' + trimmedLine.replace(/  /g, '&nbsp;&nbsp;');
            } else {
                // This is text before any list item - add as a row with no item marker
                tableRows += `
                <tr>
                    <td class="response-cell-id"></td>
                    <td class="response-cell-content">${trimmedLine.replace(/  /g, '&nbsp;&nbsp;')}</td>
                </tr>`;
            }
        }
    });
    
    // Add the last item if there is one
    if (currentItem !== null) {
        tableRows += `
        <tr>
            <td class="response-cell-id">${currentItem}</td>
            <td class="response-cell-content">${currentContent}</td>
        </tr>`;
    }
    
    return `
    <table class="response-table structured-table">
        <thead>
            <tr>
                <th class="response-header-id" width="40">#</th>
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
    // Replace code blocks with properly formatted code
    const codeBlockRegex = /```([\s\S]*?)```/g;
    const formattedResponse = response.replace(codeBlockRegex, (match, codeContent) => {
        return `<pre class="code-block"><code>${codeContent.trim()}</code></pre>`;
    });
    
    return `
    <div class="formatted-response">
        ${formattedResponse.replace(/\n/g, '<br>').replace(/  /g, '&nbsp;&nbsp;')}
    </div>`;
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