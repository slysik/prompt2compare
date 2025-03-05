import requests
import logging
import json
from config import PROMPTLAYER_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API constants
API_KEY = PROMPTLAYER_API_KEY
WORKSPACE_ID = 17053  # Specific workspace ID
BASE_URL = "https://api.promptlayer.com"

def get_headers():
    """Return headers for API requests."""
    return {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

def check_api_connection():
    """Check if the PromptLayer API is accessible."""
    try:
        # Try a basic API endpoint
        response = requests.get(f"{BASE_URL}/prompt-templates", headers=get_headers())
        return response.status_code == 200
    except Exception as e:
        logger.error(f"API connection check failed: {str(e)}")
        return False

def get_all_templates():
    """
    Get all prompt templates from PromptLayer API.
    
    Returns:
        list: A list of template objects
    """
    try:
        # Use the main API endpoint for templates
        url = f"{BASE_URL}/prompt-templates"
        response = requests.get(url, headers=get_headers())
        
        logger.info(f"API URL: {url}")
        logger.info(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if the response has the expected structure
            if "items" in data:
                templates = data["items"]
                logger.info(f"Found {len(templates)} templates in API response")
                
                # Create formatted list of templates
                formatted_templates = []
                for template in templates:
                    name = template.get("prompt_name", "Unnamed Template")
                    
                    # Extract model information
                    model = "gpt-3.5-turbo"  # Default
                    temperature = 0.7  # Default
                    max_tokens = 500  # Default
                    
                    metadata = template.get("metadata", {})
                    if metadata and "model" in metadata:
                        model_info = metadata["model"]
                        model = model_info.get("name", model)
                        
                        # Get parameters if available
                        if "parameters" in model_info:
                            params = model_info["parameters"]
                            temperature = params.get("temperature", temperature)
                            # Max tokens might not be specified
                            if "max_tokens" in params:
                                max_tokens = params.get("max_tokens")
                    
                    formatted_template = {
                        "name": name,
                        "id": str(template.get("id", "")),
                        "model": model,
                        "temperature": temperature,
                        "max_tokens": max_tokens
                    }
                    
                    formatted_templates.append(formatted_template)
                
                logger.info(f"Processed {len(formatted_templates)} templates")
                return formatted_templates
            
            logger.error("Unexpected API response structure")
            logger.info(f"API response keys: {data.keys()}")
        
        logger.error(f"Failed to get templates: {response.status_code}")
        return []
        
    except Exception as e:
        logger.error(f"Error fetching templates: {str(e)}")
        return []

def get_template_details(template_name):
    """
    Get specific template details from PromptLayer API.
    
    Args:
        template_name (str): Name of the template to retrieve
        
    Returns:
        dict: Template details including parameters
    """
    try:
        # Get all templates first since we need to find by name
        url = f"{BASE_URL}/prompt-templates"
        response = requests.get(url, headers=get_headers())
        
        logger.info(f"Template detail API URL: {url}")
        logger.info(f"Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we have items in the response
            if "items" in data:
                # Find the template with matching name
                matching_template = None
                for template in data["items"]:
                    if template.get("prompt_name") == template_name:
                        matching_template = template
                        break
                
                if matching_template:
                    logger.info(f"Found template: {template_name}")
                    
                    # Extract model information
                    model = "gpt-3.5-turbo"  # Default
                    temperature = 0.7  # Default
                    max_tokens = 500  # Default
                    top_p = 1.0
                    frequency_penalty = 0.0
                    presence_penalty = 0.0
                    
                    # Extract from metadata if available
                    metadata = matching_template.get("metadata", {})
                    if metadata and "model" in metadata:
                        model_info = metadata["model"]
                        model = model_info.get("name", model)
                        
                        # Get parameters if available
                        if "parameters" in model_info:
                            params = model_info["parameters"]
                            temperature = params.get("temperature", temperature)
                            top_p = params.get("top_p", top_p)
                            frequency_penalty = params.get("frequency_penalty", frequency_penalty)
                            presence_penalty = params.get("presence_penalty", presence_penalty)
                            if "max_tokens" in params:
                                max_tokens = params.get("max_tokens")
                    
                    # Process the prompt template
                    prompt_template = matching_template.get("prompt_template", {})
                    
                    # Initialize message fields
                    system_message = ""
                    user_message = ""
                    assistant_message = ""
                    
                    # Extract messages if available
                    if "messages" in prompt_template:
                        messages = prompt_template["messages"]
                        
                        for msg in messages:
                            role = msg.get("role")
                            
                            # Extract content from message
                            content_text = ""
                            if "content" in msg:
                                content = msg["content"]
                                for content_item in content:
                                    if "text" in content_item:
                                        content_text += content_item["text"]
                            
                            # Assign to appropriate message field
                            if role == "system":
                                system_message = content_text
                            elif role == "user":
                                user_message = content_text
                            elif role == "assistant":
                                assistant_message = content_text
                    
                    # Create the final template object
                    template_details = {
                        "system_message": system_message,
                        "user_message": user_message,
                        "assistant_message": assistant_message,
                        "model": model,
                        "temperature": float(temperature),
                        "max_tokens": int(max_tokens),
                        "top_p": float(top_p),
                        "frequency_penalty": float(frequency_penalty),
                        "presence_penalty": float(presence_penalty)
                    }
                    
                    logger.info(f"Extracted template details successfully")
                    return template_details
            
            logger.error("Template not found or unexpected response structure")
        
        logger.error(f"Failed to get template details: {response.status_code}")
        return {
            "system_message": "You are a helpful AI assistant.",
            "user_message": "Please provide information about this topic.",
            "assistant_message": "",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }
        
    except Exception as e:
        logger.error(f"Error fetching template details: {str(e)}")
        return {
            "system_message": "You are a helpful AI assistant.",
            "user_message": "Please provide information about this topic.",
            "assistant_message": "",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 500,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        }