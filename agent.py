from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
import requests

# Define tools to interact with the local book API

@tool
def get_book_by_name(name: str) -> str:
    """Get a book by its name from the local book API."""
    try:
        response = requests.get(f"http://localhost:8000/books?name={name}")
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
        response = requests.post("http://localhost:8000/books", json={"author": author, "name": name, "year": year})
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
        response = requests.get(f"http://localhost:8000/books/author/{author}")
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
    model="deepseek/deepseek-r1-0528-qwen3-8b",  # Use the model name as configured in LM Studio
    base_url="http://localhost:1234/v1",
    api_key="dummy"  # LM Studio doesn't require a real API key
)

# Define the tools list
tools = [get_book_by_name, create_book, search_books_by_author]

# Create the prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can manage books using the available tools. Use the tools to interact with the local book storage API."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Create the agent
agent = create_openai_tools_agent(llm, tools, prompt)

# Create the agent executor
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

if __name__ == "__main__":
    # Example usage
    result = agent_executor.invoke({"input": "Search for a book called 1984"})
    
    # Format the output to human-readable string
    output_lines = []
    output_lines.append(f"Input: {result['input']}")
    output_lines.append(f"Final Answer: {result['output']}")
    
    for i, (action, observation) in enumerate(result.get('intermediate_steps', []), 1):
        # Each thought starts on a new line
        thoughts = action.log.split('\n')
        for thought in thoughts:
            if thought.strip():
                output_lines.append(f"Thought {i}: {thought.strip()}")
        output_lines.append(f"Action {i}: {action.tool} with input {action.tool_input}")
        output_lines.append(f"Observation {i}: {observation}")
    
    # Print the formatted output
    print('\n'.join(output_lines))