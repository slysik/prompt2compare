# PromptComp

PromptComp is a web application that helps users compare ChatGPT responses from current and previous prompt template information. This tool is designed to make prompt engineering easier by providing a side-by-side comparison of different prompt versions and their responses.

## Features

1. **Dashboard**: View all prompt templates with hoverable parameter information
2. **Template Comparison**: Side-by-side comparison of previous and current template parameters and responses
3. **Response Generation**: Generate responses from both previous and current template versions
4. **Prompt Improvement Suggestions**: AI-powered suggestions to improve your prompts
5. **Export Functionality**: Download comparison reports in Markdown format

## Requirements

- Python 3.8 or higher
- PromptLayer API Key
- OpenAI API Key

## Installation

1. Clone this repository
2. Create a virtual environment (recommended)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```
   pip install -r requirements.txt
   ```
4. Set up your API keys
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file to add your API keys

## Usage

1. Run the application
   ```
   ./run.sh
   ```
   Or manually with:
   ```
   python app.py
   ```

2. Access the application in your browser at `http://localhost:9999`

3. Select a template from the dashboard to compare and modify

4. Make changes to the current template parameters as needed

5. Generate responses to see the difference between versions

6. Download a comparison report when you're satisfied with your results

## API Integration

This application integrates with two external APIs:

1. **PromptLayer API**: Used to retrieve prompt templates and their parameters
2. **OpenAI API**: Used to generate text completions and prompt improvement suggestions

## Security

- API keys are stored in environment variables and never exposed to clients
- All sensitive information is properly handled and not logged

## License

This project is licensed under the MIT License - see the LICENSE file for details.