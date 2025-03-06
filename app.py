import os
import logging
import json
import datetime
import openai  # Import OpenAI directly for usage in routes
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file
from pathlib import Path

# Import utils
from utils.promptlayer_api import get_all_templates, get_template_details, check_api_connection
from utils.openai_api import generate_completion, suggest_prompt_improvements
from config import OPENAI_API_KEY

# Set the OpenAI API key globally for direct usage in routes
openai.api_key = OPENAI_API_KEY

# Import config
from config import PORT, PROMPTLAYER_API_KEY, OPENAI_API_KEY

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Check if API keys are set
if not PROMPTLAYER_API_KEY:
    logger.error("PromptLayer API key is not set")
    raise ValueError("PromptLayer API key is not set. Please set PROMPTLAYER_API_KEY in .env file.")

if not OPENAI_API_KEY:
    logger.error("OpenAI API key is not set")
    raise ValueError("OpenAI API key is not set. Please set OPENAI_API_KEY in .env file.")

# Check if PromptLayer API is accessible
if not check_api_connection():
    logger.error("PromptLayer API is not accessible")
    raise ConnectionError("PromptLayer API is not accessible. Please check your API key and connection.")

# Routes
@app.route('/')
def index():
    """Dashboard to view all prompt templates."""
    try:
        templates = get_all_templates()
        return render_template('index.html', templates=templates)
    except Exception as e:
        logger.error(f"Error loading dashboard: {str(e)}")
        return render_template('index.html', templates=[], error_message=f"Error: {str(e)}")

@app.route('/compare')
def compare():
    """Comparison playground interface."""
    try:
        # Get all templates for the dropdown
        templates = get_all_templates()
        return render_template('template_and_response_compare.html', templates=templates)
    except Exception as e:
        logger.error(f"Error loading comparison interface: {str(e)}")
        return render_template('template_and_response_compare.html', templates=[], error_message=f"Error: {str(e)}")

@app.route('/template/<template_name>')
def get_template(template_name):
    """Get template details."""
    try:
        template_details = get_template_details(template_name)
        return jsonify(template_details)
    except Exception as e:
        logger.error(f"Error getting template details: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate_response', methods=['POST'])
def generate_response():
    """Generate a single response for a template."""
    try:
        data = request.json
        system_message = data.get('system_message', '')
        user_message = data.get('user_message', '')
        assistant_message = data.get('assistant_message', '')
        model = data.get('model', 'gpt-3.5-turbo')
        temperature = float(data.get('temperature', 0.7))
        max_tokens = int(data.get('max_tokens', 500))
        
        # Get additional parameters
        params = {}
        for key, value in data.items():
            if key not in ['system_message', 'user_message', 'assistant_message', 'model', 'temperature', 'max_tokens']:
                # Make sure numeric values are properly typed
                if key in ['top_p', 'frequency_penalty', 'presence_penalty'] and value is not None:
                    try:
                        params[key] = float(value)
                    except (ValueError, TypeError):
                        # Skip problematic values
                        continue
                else:
                    params[key] = value
        
        # Generate response
        response = generate_completion(
            user_message=user_message,
            system_message=system_message,
            assistant_message=assistant_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            **params
        )
        
        return jsonify({
            'response': response
        })
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/suggest_improvements', methods=['POST'])
def suggest_improvements():
    """Suggest improvements for specific prompt components."""
    try:
        data = request.json
        system_message = data.get('system_message', '')
        user_message = data.get('user_message', '')
        assistant_message = data.get('assistant_message', '')
        model = data.get('model', 'gpt-3.5-turbo')
        message_type = data.get('message_type', 'all')  # Default to all if not specified
        
        logger.info(f"Generating prompt improvement suggestions for {message_type} message")
        
        # Create a response object with the original values
        improved = {
            'system_message': system_message,
            'user_message': user_message,
            'assistant_message': assistant_message
        }
        
        # If focusing on a specific message type, customize the prompt
        if message_type == 'system':
            # Get suggestion just for system message
            suggestion_prompt = f"""
            I need to improve a system message for an AI prompt. The system message sets the overall behavior and instructions for the AI.
            
            Current system message:
            {system_message}
            
            Please suggest an improved version of this system message that is more effective, clear, and specific.
            Return ONLY the improved system message with no additional commentary.
            """
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": suggestion_prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            improved['system_message'] = response.choices[0].message.content.strip()
            
        elif message_type == 'user':
            # Get suggestion just for user message
            suggestion_prompt = f"""
            I need to improve a user message for an AI prompt. The user message is the specific query or instruction.
            
            Current system context: {system_message}
            Current user message:
            {user_message}
            
            Please suggest an improved version of this user message that is more clear, specific, and likely to get a better response.
            Return ONLY the improved user message with no additional commentary.
            """
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": suggestion_prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            improved['user_message'] = response.choices[0].message.content.strip()
            
        elif message_type == 'assistant':
            # Get suggestion just for assistant message
            suggestion_prompt = f"""
            I need to improve an assistant message for an AI prompt. The assistant message is the example response or previous message from the AI.
            
            Current system context: {system_message}
            Current user context: {user_message}
            Current assistant message:
            {assistant_message}
            
            Please suggest an improved version of this assistant message that better sets up the conversation or provides a better example.
            Return ONLY the improved assistant message with no additional commentary.
            """
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": suggestion_prompt}],
                temperature=0.7,
                max_tokens=500
            )
            
            improved['assistant_message'] = response.choices[0].message.content.strip()
            
        else:
            # For "all", get suggestions for all messages
            suggestion = suggest_prompt_improvements(
                system_message=system_message,
                user_message=user_message,
                assistant_message=assistant_message,
                model=model
            )
            
            try:
                # Try to parse the suggestion into the different message types
                system_found = False
                user_found = False
                assistant_found = False
                
                for line in suggestion.split('\n'):
                    line = line.strip()
                    if line.startswith('SYSTEM:'):
                        improved['system_message'] = line[7:].strip()
                        system_found = True
                    elif line.startswith('USER:'):
                        improved['user_message'] = line[5:].strip()
                        user_found = True
                    elif line.startswith('ASSISTANT:'):
                        improved['assistant_message'] = line[10:].strip()
                        assistant_found = True
                
                # Ensure all messages are present
                if not (system_found and user_found and assistant_found):
                    logger.warning("Missing some message types in response, using defaults where needed")
                    if not system_found:
                        improved['system_message'] = system_message or "You are a helpful assistant."
                    if not user_found:
                        improved['user_message'] = user_message or "Please help me with my task."
                    if not assistant_found:
                        improved['assistant_message'] = assistant_message or "I'll help you with your task."
            except Exception as parse_error:
                logger.error(f"Error parsing suggestions: {str(parse_error)}")
                # If parsing fails, use the original messages
                improved['system_message'] = system_message or "You are a helpful assistant."
                improved['user_message'] = user_message or "Please help me with my task."
                improved['assistant_message'] = assistant_message or "I'll help you with your task."
        
        return jsonify(improved)
    except Exception as e:
        logger.error(f"Error suggesting improvements: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/export_comparison', methods=['POST'])
def export_comparison():
    """Export the comparison results to a markdown file."""
    try:
        data = request.json
        template_name = data.get('template_name', 'comparison')
        left_params = data.get('left_params', {})
        right_params = data.get('right_params', {})
        left_response = data.get('left_response', '')
        right_response = data.get('right_response', '')
        
        # Create markdown content
        markdown_content = f"""# Prompt Comparison: {template_name}

## Date
{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Left Side (Previous)
- **Model**: {left_params.get('model', 'gpt-3.5-turbo')}
- **Temperature**: {left_params.get('temperature', 0.7)}
- **Max Tokens**: {left_params.get('max_tokens', 500)}

### System Message
```
{left_params.get('system_message', '')}
```

### User Message
```
{left_params.get('user_message', '')}
```

### Assistant Message
```
{left_params.get('assistant_message', '')}
```

### Response
```
{left_response}
```

## Right Side (Current)
- **Model**: {right_params.get('model', 'gpt-3.5-turbo')}
- **Temperature**: {right_params.get('temperature', 0.7)}
- **Max Tokens**: {right_params.get('max_tokens', 500)}

### System Message
```
{right_params.get('system_message', '')}
```

### User Message
```
{right_params.get('user_message', '')}
```

### Assistant Message
```
{right_params.get('assistant_message', '')}
```

### Response
```
{right_response}
```
"""
        
        # Add additional parameters if any
        additional_left = False
        additional_right = False
        
        additional_content = "\n## Additional Parameters\n"
        
        additional_content += "\n### Left Side (Previous)\n"
        for key, value in left_params.items():
            if key not in ['system_message', 'user_message', 'assistant_message', 'model', 'temperature', 'max_tokens']:
                additional_content += f"- **{key}**: {value}\n"
                additional_left = True
        
        additional_content += "\n### Right Side (Current)\n"
        for key, value in right_params.items():
            if key not in ['system_message', 'user_message', 'assistant_message', 'model', 'temperature', 'max_tokens']:
                additional_content += f"- **{key}**: {value}\n"
                additional_right = True
        
        if additional_left or additional_right:
            markdown_content += additional_content
        
        # Create filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"comparison_{template_name.replace(' ', '_')}_{timestamp}.md"
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        
        # Write to file
        with open(filepath, 'w') as f:
            f.write(markdown_content)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': filepath
        })
    except Exception as e:
        logger.error(f"Error exporting comparison: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/download_comparison/<filename>')
def download_comparison(filename):
    """Download the exported comparison file."""
    try:
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading comparison: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)