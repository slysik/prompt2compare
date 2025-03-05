import logging
import openai
from config import OPENAI_API_KEY

# Set API key
openai.api_key = OPENAI_API_KEY

def generate_completion(user_message="", system_message="You are a helpful AI assistant.", assistant_message="", model="gpt-3.5-turbo", temperature=0.7, max_tokens=500, **kwargs):
    """
    Generate a completion using OpenAI API with separated message fields.
    """
    try:
        if not model:
            model = "gpt-3.5-turbo"  # Default model if none provided
            
        messages = []
        
        # Add system message if provided
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        # Add user message if provided
        if user_message:
            messages.append({"role": "user", "content": user_message})
        
        # Add assistant message if provided
        if assistant_message:
            messages.append({"role": "assistant", "content": assistant_message})
            
        # If no messages were added, add a default user message
        if not messages:
            messages.append({"role": "user", "content": "Hello, can you help me?"})
        
        # Remove problematic parameters that might cause issues
        clean_kwargs = {}
        for k, v in kwargs.items():
            if k in ['top_p', 'frequency_penalty', 'presence_penalty']:
                if not isinstance(v, str) and v is not None:
                    clean_kwargs[k] = float(v)
            else:
                clean_kwargs[k] = v
        
        logging.info(f"Generating completion with model: {model}")
        logging.info(f"Parameters: temp={temperature}, max_tokens={max_tokens}")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **clean_kwargs
        )
        
        return response.choices[0].message["content"]
    except Exception as e:
        logging.error(f"Error generating completion: {str(e)}")
        return f"Error generating response: {str(e)}"

def suggest_prompt_improvements(system_message="", user_message="", assistant_message="", model="gpt-3.5-turbo"):
    """
    Generate suggestions for improving prompts (system, user, and assistant messages).
    """
    try:
        if not model:
            model = "gpt-3.5-turbo"  # Default model if none provided
            
        # Create a formatted prompt that includes all message types
        suggestion_prompt = f"""
        I'm going to provide you with prompt components. Please analyze them and suggest 
        improvements to make them more effective, clear, and likely to generate better results.
        
        Current System Message:
        {system_message}
        
        Current User Message:
        {user_message}
        
        Current Assistant Message:
        {assistant_message}
        
        Please suggest specific improvements to these prompts, focusing on:
        1. Clarity and specificity
        2. Structure and organization
        3. Any missing context or instructions
        4. Tone and language
        
        Return the improved prompts in this format:
        SYSTEM: [improved system message]
        USER: [improved user message]
        ASSISTANT: [improved assistant message]
        
        Don't include any explanations, just the improved messages.
        """
        
        logging.info(f"Generating prompt improvement suggestions with model: {model}")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": suggestion_prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        
        suggestion = response.choices[0].message["content"]
        
        return suggestion
    except Exception as e:
        logging.error(f"Error suggesting improvements: {str(e)}")
        return f"Error generating suggestions: {str(e)}"