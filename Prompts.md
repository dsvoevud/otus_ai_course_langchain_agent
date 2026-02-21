You are a Python developer following the main best practices. You should create a sample API for a book storage. It should have 5 endpoints: 1) create a record about a book, 2) get a record about a book by id, 3) get a record about a book by name, 4) update a record by id, 5) delete a record. The book should have the following fields: id, author, name, year. Values should be stored in json, create some stub data. You should add Swagger and build and launch instructions. Place it in SampleAPI folder
Add gitignore for python to the root directory
Create a Langchain agent which will make requests to local model deepseek/deepseek-r1-0528-qwen3-8b deployed in localhost:1234
I get error "Traceback (most recent call last): File "E:\AI_Course\1_12\otus_ai_course_langchain_agent\agent.py", line 2, in <module> from langchain.agents import AgentExecutor, create_openai_tools_agent ImportError: cannot import name 'AgentExecutor' from 'langchain.agents' (E:\AI_Course\1_12\otus_ai_course_langchain_agent.venv\Lib\site-packages\langchain\agents_init_.py) when I run this script - тут то, про что я кидал ссылку в чате, с весии 1.2.x понадобилось импортить langchain-classic.
Add langchain-classic to requirements and use it in agent.py
Can we install a langchain package for lm studio and update the agent to use it? (сначала он ollama закинул в requirements)
Add to the agent a tool to search a book by author
Please add the line above for testing the llm connection separately to readme.md (добавил запрос для проверки коннекта к LLM к readme)
Add an endpoint to get all the books written by a specific author
Change search_books_by_author tool to use a new endpoint you've just created
Can I enter input into the agent in terminal?
The agent should give the response in the following format:
Status: (success / error)
Action: (description of the API called)
Data: result of the API request
If there were any errors during the request - list them in the Errors: section
Give the summary of the result in Data section and then Detailed output (тут пришлось позапрашивать, чтобы выдал в итоге так, как сейчас, краткий результат в Data и Detailed output потом)
I want a full list of agent's thoughts to be in Detailed output, each thought starting with a new line
Move http://localhost:8000/ url to a variable
Move model name, base url for llm and api key to variables too
Add to Readme.md detailed instructions on how to interact with the agent and its format of response