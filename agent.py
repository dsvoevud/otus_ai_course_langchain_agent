from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
import requests

# Base URL for the book API
BASE_URL = "http://localhost:8000"

# LLM configuration
LLM_MODEL = ""
LLM_BASE_URL = ""
LLM_API_KEY = ""

# Define tools to interact with the local book API

@tool
def get_book_by_name(name: str) -> str:
    """Get a book by its name from the local book API."""
    try:
        response = requests.get(f"{BASE_URL}/books?name={name}")
        if response.status_code == 200:
            book = response.json()
            return f"Book found: {book['name']} by {book['author']} ({book['year']})"
        else:
            return "Book not found"
    except Exception as e:
        return f"Error accessing API: {str(e)}"

@tool
def create_book(author: str, name: str, year: int) -> str:
    """Create a new book in the local book API."""
    try:
        response = requests.post(f"{BASE_URL}/books", json={"author": author, "name": name, "year": year})
        if response.status_code == 200:
            book = response.json()
            return f"Book created: {book['name']} by {book['author']} ({book['year']})"
        else:
            return "Failed to create book"
    except Exception as e:
        return f"Error accessing API: {str(e)}"

@tool
def search_books_by_author(author: str) -> str:
    """Search for books by author from the local book API."""
    try:
        response = requests.get(f"{BASE_URL}/books/author/{author}")
        if response.status_code == 200:
            books = response.json()
            if books:
                result = f"Found {len(books)} book(s) by author '{author}':\n"
                for book in books:
                    result += f"- {book['name']} ({book['year']})\n"
                return result.strip()
            else:
                return f"No books found by author '{author}'"
        else:
            return "Error searching books"
    except Exception as e:
        return f"Error accessing API: {str(e)}"

# Set up the LLM to connect to the local LM Studio server
llm = ChatOpenAI(
    model=LLM_MODEL,
    base_url=LLM_BASE_URL,
    api_key=LLM_API_KEY
)

# Define the tools list
tools = [get_book_by_name, create_book, search_books_by_author]

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can manage books. Use the available tools to interact with the local book storage API. Based on the tool results, provide a natural language response to the user's query."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create the agent
agent = create_openai_tools_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)

if __name__ == "__main__":
    # Interactive input
    user_input = input("Enter your query: ")
    result = agent_executor.invoke({"input": user_input})
    
    # Determine status
    status = "success"
    errors = []
    for action, observation in result.get('intermediate_steps', []):
        if "error" in observation.lower() or "failed" in observation.lower():
            status = "error"
            errors.append(observation)
    
    # Extract action description from the first tool call or input
    action_desc = result['input']
    if result.get('intermediate_steps'):
        first_action = result['intermediate_steps'][0][0]
        action_desc = f"Called {first_action.tool} with {first_action.tool_input}"
      
    # Create summary for Data: extract the final answer, ignoring <think> tags
    output = result['output']
    # Remove <think> blocks
    import re
    output = re.sub(r'<think>.*?</think>', '', output, flags=re.DOTALL).strip()
    summary = output
    
    # Format the response
    print(f"Status: {status}")
    print(f"Action: {action_desc}")
    print(f"Data: {summary}")
    print("Detailed output:")
    for i, (action, observation) in enumerate(result.get('intermediate_steps', []), 1):
        thoughts = action.log.split('\n')
        for thought in thoughts:
            if thought.strip():
                print(thought.strip())  # Each thought on a new line
        print(f"Action {i}: {action.tool} with input {action.tool_input}")
        print(f"Observation {i}: {observation}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"- {error}")