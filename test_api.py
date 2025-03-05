import requests
import json

API_KEY = "pl_84f2bb2a619d611ac8bbae7abd831454"
WORKSPACE_ID = 17053

def test_api():
    """Test the PromptLayer API"""
    headers = {"X-API-KEY": API_KEY}
    
    # Try the direct endpoint
    url = "https://api.promptlayer.com/prompt-templates"
    response = requests.get(url, headers=headers)
    
    print(f"Endpoint: {url}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if "data" in data:
            templates = data["data"]
            workspace_templates = [t for t in templates if t.get("workspace_id") == WORKSPACE_ID]
            
            print(f"Total templates: {len(templates)}")
            print(f"Workspace templates: {len(workspace_templates)}")
            
            # Print workspace template names
            if workspace_templates:
                print("\nWorkspace template names:")
                for i, t in enumerate(workspace_templates):
                    print(f"{i+1}. {t.get('name', 'Unnamed')}")
                
                # Print full template details for the first one
                print("\nFirst template details:")
                print(json.dumps(workspace_templates[0], indent=2))
            else:
                print("No templates found for workspace ID:", WORKSPACE_ID)
        else:
            print("No data field in response")
            print(json.dumps(data, indent=2))
    else:
        print("Error response:", response.text)

    # Try to get a specific template
    template_name = "Steve"
    url = f"https://api.promptlayer.com/prompt-template?name={template_name}"
    response = requests.get(url, headers=headers)
    
    print(f"\nSpecific template endpoint: {url}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print("Error response:", response.text)

if __name__ == "__main__":
    test_api()