# Lexi 💬
> Run local, uncensored LLMs with automatic Wikipedia tool calling right from your CLI or web browser.

## Why Lexi? 🧠
Running models locally on your own machine is fantastic for privacy, customizability, and escaping subscription fees. But local models are stuck in a sandbox—they cannot look up facts, verify details, or correct spelling mistakes in real time.

Lexi gives your local models a window to the outer world. It connects LM Studio to a web interface or a terminal screen, letting the model automatically search Wikipedia, extract the exact introduction of the correct article, and use it to form a response. It does this with a minimal footprint: no massive vector stores, no complex agent orchestration libraries. Just a lightweight Django backend, standard Python library calls, and clean OpenAI-compatible tool definitions.

## Key Features 🛠️
- Connects directly to LM Studio's local server API.
- Employs function calling to auto-retrieve Wikipedia abstracts for real-time grounding.
- Streams model outputs token-by-token directly to the UI.
- Keeps track of chat history per user session using Django’s built-in session storage and SQLite.
- Customizes model behavior with custom system prompts built directly into the UI.

## Quick Start 🚀

### Prerequisites
1. **LM Studio**: Download and install it.
2. **Download a Model**: Get an LLM (like `llama-3.1-8b-lexi-uncensored-v2` or similar).
3. **Start the Local Server**: Toggle the local server option on in LM Studio (usually runs on port `1234`).

### CLI Version
If you just want a terminal-based chatbot with spinner effects and Wikipedia searching:

1. Install the OpenAI Python SDK:
   ```bash
   pip install openai
   ```
2. Open `pro1/code.py` and set your local server base URL and the model name:
   ```python
   client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
   MODEL = "llama-3.1-8b-lexi-uncensored-v2"
   ```
3. Run the script:
   ```bash
   python pro1/code.py
   ```

### Web App Version
To run the full Django interface with session logging and system prompt controls:

1. Install Django and the OpenAI SDK:
   ```bash
   pip install django openai
   ```
2. Open `pro1/chatai/views.py` and adjust the API URL and model:
   ```python
   client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
   model = "llama-3.1-8b-lexi-uncensored-v2"
   ```
3. Run migrations to initialize the SQLite database:
   ```bash
   python pro1/manage.py migrate
   ```
4. Start the Django development server:
   ```bash
   python pro1/manage.py runserver
   ```
5. Open your browser and navigate to `http://127.0.0.1:8000/`.

## Contributing 🤝
Got ideas to make Lexi smarter or want to add more tools (like duckduckgo search, local file reading, or math solver)? Pull requests are incredibly welcome!

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/cool-new-tool`).
3. Commit your changes (`git commit -m 'Add duckduckgo tool'`).
4. Push to the branch (`git push origin feature/cool-new-tool`).
5. Open a Pull Request and let's talk about it!
