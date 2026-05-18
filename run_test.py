import os
from dotenv import load_dotenv

load_dotenv()

from autodoc.core.agents.coordinator import run_coordinator

if __name__ == "__main__":
    project_path = os.path.abspath("test_project")
    print(f"Running AutoDoc on {project_path}...")
    
    # Check for Azure OpenAI environment variables
    azure_vars = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT_NAME"]
    missing_vars = [var for var in azure_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Warning: Missing Azure OpenAI variables: {', '.join(missing_vars)}. Agent calls will fail.")
    else:
        print("All required Azure OpenAI variables are set.")
    
    try:
        result = run_coordinator(project_path)
        print("\n--- Documentation Generation Complete ---")
        print(f"Stack: {result.get('stack')}")
        print(f"Documentation: {result.get('documentation')}")
        print(f"Diagrams: {result.get('diagram_paths')}")
    except Exception as e:
        print(f"Error: {str(e)}")
