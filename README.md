# OTUS AI Course LangChain Agent

## Installation

1. Install Python 3.12 using uv:

```bash
uv python install 3.12.12
```

2. Create a virtual environment with Python 3.12:

```bash
uv venv --python 3.12.12
```

3. Install the required packages:

```bash
uv pip install -r requirements.txt
```

## Sample API

A sample FastAPI application for book storage is included in the `SampleAPI` folder. It provides CRUD operations for books with fields: id, author, name, year.

### Endpoints

- `POST /books` - Create a new book
- `GET /books/{id}` - Get a book by ID
- `GET /books?name={name}` - Get a book by name
- `GET /books/author/{author}` - Get all books by a specific author
- `GET /books/search?author={author}&name={name}` - Search books by author and/or name
- `PUT /books/{id}` - Update a book by ID
- `DELETE /books/{id}` - Delete a book by ID

### Running the Sample API

1. Navigate to the SampleAPI folder:

```bash
cd SampleAPI
```

2. Run the API:

```bash
uv run uvicorn main:app --reload
```

3. Open your browser to `http://localhost:8000/docs` for Swagger UI.

### Data Storage

Books are stored in `data.json` in the SampleAPI folder. Initial stub data is provided.

## LangChain Agent

The project includes a LangChain agent that interacts with the local book API and uses a local LLM (e.g., via LM Studio).

### Running the Agent

1. Ensure the Sample API is running (see above).
2. Ensure your local LLM server (e.g., LM Studio) is running on `localhost:1234` with an OpenAI-compatible API.
3. Test the LLM connection separately:

```bash
uv run python -c "from langchain_openai import ChatOpenAI; llm = ChatOpenAI(model='deepseek/deepseek-r1-0528-qwen3-8b', base_url='http://localhost:1234/v1', api_key='dummy'); print(llm.invoke('Hello'))"
```

4. Run the agent:

```bash
uv run python agent.py
```

The agent can search for books by name, author, or ID, and create new books.