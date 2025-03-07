import logging
import openai
from config import OPENAI_API_KEY

# Set API key
openai.api_key = OPENAI_API_KEY

# Standard GPT model - Custom GPTs aren't directly accessible via API
GPT_MODEL = "gpt-4o"

def generate_completion(user_message="", system_message="You are a helpful AI assistant.", assistant_message="", model="gpt-4o", temperature=0.7, max_tokens=500, **kwargs):
    """
    Generate a completion using OpenAI API with separated message fields.
    """
    try:
        # Always use gpt-4o as the model
        model = "gpt-4o"  # Force the model to be gpt-4o
            
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
            # Skip provider and Frequency Penalty parameters - they're not supported by OpenAI API
            if k in ['provider', 'Frequency Penalty']:
                continue
                
            # Handle known parameters with proper types
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

def call_jija_comp_gpt(message, temperature=0.7, max_tokens=1000):
    """
    Simulates JiJa Comp GPT with a standard GPT-4o model using a system prompt.
    """
    try:
        logging.info(f"Calling JiJa Comp simulation with message: {message[:100]}...")
        
        # Create a system prompt to simulate JiJa Comp GPT behavior
        system_prompt = """You are JiJa, an AI assistant specializing in business comparisons, analysis, and metrics. 
        Your primary function is to help users compare data, analyze business metrics, and provide insights.
        
        When responding to queries about comparisons:
        1. Be concise and focus on the key differences
        2. Present information in clear, structured formats (tables when relevant)
        3. Highlight important metrics and quantifiable data
        4. Provide context for why certain differences matter
        5. Be objective and balanced in your analysis
        
        Your tone should be professional, analytical, and helpful. Provide direct answers that are easy to understand.
        """
        
        # Create a formatted prompt that includes all message types
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,  # Use GPT-4o model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message["content"]
    except Exception as e:
        logging.error(f"Error calling JiJa simulation: {str(e)}")
        return f"Error calling JiJa simulation: {str(e)}"

def suggest_prompt_improvements(system_message="", user_message="", assistant_message="", model="gpt-3.5-turbo"):
    """
    Generate suggestions for improving prompts (system, user, and assistant messages).
    """
    try:
        if not model:
            model = "gpt-3.5-turbo"  # Default model if none provided
            
        # Validate inputs to prevent blank requests
        if not any([system_message, user_message, assistant_message]):
            logging.error("No message content provided for suggestions")
            return """
            SYSTEM: You are a helpful AI assistant that provides clear and concise responses.
            USER: Please help me with my task.
            ASSISTANT: I'd be happy to help you with your task. What specific information or assistance do you need?
            """
            
        # Create a formatted prompt that includes all message types
        suggestion_prompt = f"""
        I'm going to provide you with prompt components. Please analyze them and suggest 
        SIGNIFICANT improvements to make them more effective, clear, and likely to generate better results.
        
        Current System Message:
        {system_message}
        
        Current User Message:
        {user_message}
        
        Current Assistant Message:
        {assistant_message}
        
        Please suggest substantial and creative improvements to these prompts, focusing on:
        1. Clarity and specificity - make instructions much clearer and more detailed
        2. Structure and organization - improve how the information is structured
        3. Adding any missing context or instructions that would help
        4. Improving tone and language for better results
        5. Adding new capabilities or instructions that weren't in the original
        
        Your improvements should be substantial - not just minor edits!
        
        Return the improved prompts in this format:
        SYSTEM: [improved system message]
        USER: [improved user message]
        ASSISTANT: [improved assistant message]
        
        Don't include any explanations, just the improved messages.
        """
        
        logging.info(f"Generating prompt improvement suggestions with model: {model}")
        logging.info(f"System msg length: {len(system_message)}, User msg length: {len(user_message)}, Assistant msg length: {len(assistant_message)}")
        
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": suggestion_prompt}],
            temperature=0.8,
            max_tokens=2000
        )
        
        suggestion = response.choices[0].message["content"]
        
        # Validate output format
        if not ("SYSTEM:" in suggestion and "USER:" in suggestion and "ASSISTANT:" in suggestion):
            logging.warning("Suggestion response does not contain proper format. Reformatting...")
            # Add proper formatting if missing
            lines = suggestion.strip().split('\n')
            formatted_suggestion = f"SYSTEM: {system_message or lines[0]}\nUSER: {user_message or lines[min(1, len(lines)-1)]}\nASSISTANT: {assistant_message or lines[min(2, len(lines)-1)]}"
            return formatted_suggestion
        
        return suggestion
    except Exception as e:
        logging.error(f"Error suggesting improvements: {str(e)}")
        return f"""
        SYSTEM: {system_message}
        USER: {user_message}
        ASSISTANT: {assistant_message}
        """