#!/usr/bin/env python

import requests
import json
import sys
from config import PROMPTLAYER_API_KEY

def get_headers():
    """Return headers for API requests."""
    return {
        "X-API-KEY": PROMPTLAYER_API_KEY,
        "Content-Type": "application/json"
    }
    
def process_template_data(template_data):
    """Process and extract content from a template."""
    # Look for messages in different places
    if "prompt_template" in template_data:
        pt = template_data["prompt_template"]
        print("\nPROMPT TEMPLATE STRUCTURE:")
        print(json.dumps(pt, indent=2))
        
        if "messages" in pt:
            messages = pt["messages"]
            print(f"\nFound {len(messages)} messages")
            
            for i, msg in enumerate(messages):
                print(f"\nMessage {i}:")
                print(f"Role: {msg.get('role', 'unknown')}")
                
                if "content" in msg:
                    content = msg["content"]
                    print(f"Content type: {type(content).__name__}")
                    
                    if isinstance(content, str):
                        print(f"Content (string): {content[:100]}...")
                    elif isinstance(content, list):
                        print(f"Content (list of {len(content)} items)")
                        for j, item in enumerate(content[:3]):
                            if isinstance(item, dict) and "text" in item:
                                print(f"  Item {j}: {item['text'][:100]}...")
                            else:
                                print(f"  Item {j}: {str(item)[:100]}...")

def test_api():
    """Test the PromptLayer API"""
    # Try the direct endpoint
    workspace_id = 17053  # Your workspace ID
    url = f"https://api.promptlayer.com/workspace/{workspace_id}/prompts"
    response = requests.get(url, headers=get_headers())
    
    print(f"Endpoint: {url}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        print(json.dumps(data[:100], indent=2))  # Print part of the response
        
        if isinstance(data, list):
            templates = data
            print(f"Total templates: {len(templates)}")
            
            # Print template names and IDs - look specifically for template ID 41888
            if templates:
                print("\nTemplate names:")
                for i, t in enumerate(templates[:20]):  # Show more templates
                    template_id = t.get('id', 'unknown')
                    template_name = t.get('prompt_name', 'Unnamed')
                    print(f"{i+1}. {template_name} (ID: {template_id})")
                    
                    # If this is ID 41888 or contains "SRL" in name, print more details
                    if str(template_id) == "41888" or "SRL" in template_name:
                        print(f"FOUND TARGET TEMPLATE: {template_name}")
                        print(json.dumps(t, indent=2))
            else:
                print("No templates found")
        else:
            print("Response is not a list as expected")
            print(json.dumps(data, indent=2))
    else:
        print("Error response:", response.text)

def get_template_version(template_id):
    """Get a specific template version directly from PromptLayer API."""
    base_url = "https://api.promptlayer.com"
    workspace_id = 17053  # Your workspace ID
    
    # Try different endpoints to find the template 
    # First try the workspace template endpoint
    template_url = f"{base_url}/workspace/{workspace_id}/prompt/{template_id}"
    print(f"Requesting workspace template: {template_url}")
    
    template_response = requests.get(template_url, headers=get_headers())
    print(f"Direct template status: {template_response.status_code}")
    
    if template_response.status_code == 200:
        template_data = template_response.json()
        print(f"Direct template response keys: {list(template_data.keys())}")
        
        if "template" in template_data:
            print("\nDIRECT TEMPLATE STRUCTURE:")
            print(json.dumps(template_data["template"], indent=2))
            
            # Process the template data
            process_template_data(template_data["template"])
            return
    
    # If direct approach fails, try workspace versions endpoint
    version_url = f"{base_url}/workspace/{workspace_id}/prompt/{template_id}/version"
    print(f"\nRequesting versions: {version_url}")
    
    response = requests.get(version_url, headers=get_headers())
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        if "versions" in data and len(data["versions"]) > 0:
            # Sort versions to get the latest one
            versions = data["versions"]
            versions.sort(key=lambda x: x.get("version", 0), reverse=True)
            
            # Get the latest version
            latest_version = versions[0]
            print(f"Latest version: {latest_version.get('version', 'unknown')}")
            
            # Print the complete structure
            print("\nFULL TEMPLATE STRUCTURE:")
            print(json.dumps(latest_version, indent=2))
            
            # Process the template data
            process_template_data(latest_version)
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "list":
            test_api()
        elif command == "template" and len(sys.argv) > 2:
            get_template_version(sys.argv[2])
        else:
            print("Usage: python test_api.py [list|template TEMPLATE_ID]")
    else:
        # Default to the template ID in question
        get_template_version("41888")