# NLP Study Assistant

A beginner-friendly AI chatbot that helps students learn Natural Language Processing (NLP) concepts using the Gemini API.

The assistant can explain NLP concepts, generate practice questions, provide feedback on answers, and maintain conversation continuity. It also includes streaming responses, conversation history management, input validation, and error handling with retry logic.

## Features

* **NLP concept explanations** - Explains NLP concepts in a beginner-friendly way with examples and practical use cases.
* **Practice mode** - Generates NLP practice questions and waits for the student's answer.
* **Answer feedback** - Reviews the student's answer and provides constructive explanations and guidance.
* **Streaming responses** - Displays the assistant's response as it is received from the Gemini API.
* **Conversation continuity** - Maintains context across interactions using Gemini interaction IDs.
* **Conversation history** - Stores user and assistant messages during the session.
* **Conversation summary** - Shows the number of stored messages and an approximate token count.
* **History management** - Allows the user to view, clear, and trim conversation history.
* **Input validation** - Handles empty or invalid user inputs.
* **Error handling** - Handles API errors and provides user-friendly error messages.
* **Retry mechanism** - Automatically retries certain temporary API errors using exponential backoff.
* **Environment variables** - Keeps the Gemini API key in a `.env` file rather than directly in the source code.

## Technologies Used

* **Python 3.14+** - Core programming language
* **Gemini API** - Provides the AI capabilities
* **Google GenAI SDK** - Connects the Python application to the Gemini API
* **python-dotenv** - Loads the API key from the `.env` file
* **VS Code** - Development environment

## Project Structure

```text
nlp-study-assistant/
├── main.py              # Runs the chatbot and handles user commands
├── chatbot.py           # Handles Gemini API requests, streaming, history, and errors
├── prompts.py           # Contains the system prompt and reusable prompt templates
├── config.py            # Loads the Gemini API key from environment variables
├── requirements.txt     # Lists the Python dependencies
├── README.md            # Project documentation
├── DEBUGGING.md         # Development and debugging notes
├── .env                 # Stores the Gemini API key locally
├── .gitignore           # Specifies files that should not be tracked by Git
└── .venv/               # Python virtual environment
```

## Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/adrikachowdhury/NLP-Study-Assistant.git
cd nlp-study-assistant
```

### 2. Create a virtual environment

```bash
py -3.14 -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

Create a file named `.env` in the project root directory:

```text
GEMINI_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your own Gemini API key.

Do not share your API key or commit the `.env` file to GitHub.

### 5. Run the application

```bash
python main.py
```

## Usage

After starting the application with:

```bash
python main.py
```

The assistant will display a welcome message and wait for user input.

### Available Commands

| Command     | Description                                                               |
| ----------- | ------------------------------------------------------------------------- |
| `/help`     | Show available commands                                                   |
| `/practice` | Start an NLP practice question                                            |
| `/summary`  | Show conversation summary, including message count and approximate tokens |
| `/clear`    | Clear the conversation history and start a fresh conversation             |
| `/trim`     | Keep only the specified number of recent messages                         |
| `/history`  | Show the current conversation history                                     |
| `/quit`     | Exit the assistant                                                        |

You can also type a normal NLP question without using a command. The assistant will send it to Gemini and return a streaming response.

## How It Works

The application follows a simple flow:

1. **User input** - The user enters an NLP question or selects a command.
2. **Input validation** - The application checks whether the input is valid before processing it.
3. **Prompt generation** - For practice and feedback modes, reusable prompt templates generate the appropriate instructions.
4. **Gemini API request** - The application sends the request to Gemini using the Google GenAI SDK.
5. **Streaming response** - Gemini's response is received and displayed incrementally as it is generated.
6. **Conversation continuity** - Gemini interaction IDs are used to maintain context across conversations.
7. **History management** - User and assistant messages are stored locally and can be viewed, summarised, trimmed, or cleared.
8. **Error handling** - Temporary API errors are retried automatically, while other errors are reported with user-friendly messages.

## Error Handling

The application includes error handling for common input and API-related problems.

* **Empty input** - Prevents empty or whitespace-only questions from being submitted.
* **Invalid `/trim` input** - Handles non-numeric or invalid values when specifying the number of messages to keep.
* **Temporary API errors** - Retries certain errors such as rate limits, service unavailability, and temporary high-demand responses.
* **Exponential backoff** - Waits progressively longer between retry attempts to give temporary issues time to recover.
* **Daily API quota** - Detects when the Gemini API request quota has been reached and displays a clear message to the user.
* **Other API errors** - Displays a user-friendly error message instead of allowing the application to crash.
* **Incomplete responses** - Detects when a streaming interaction does not complete successfully.

## Example Interaction

```text
🧠 Welcome to your NLP Study Assistant!

Learn NLP concepts, practise your knowledge, and get feedback as you go!

You: What is tokenization?

Thinking....

Assistant: Tokenization is the process of breaking text into smaller units called tokens...
```

### Practice Mode

```text
You: /practice

Enter an NLP topic: RoBERTa

Assistant: [Practice question is generated]

Your answer: [Student's answer]

Assistant: [Constructive feedback and explanation]
```

## What I Learned

Building this project helped me gain hands-on experience with:

* Working with an AI API through the Google GenAI SDK
* Managing API keys securely using environment variables
* Writing system prompts and reusable prompt templates
* Maintaining conversation state and context
* Implementing streaming responses
* Structuring a Python application using separate modules
* Using classes to manage conversation history
* Validating user input
* Handling API errors and temporary failures
* Implementing retry logic with exponential backoff
* Testing and debugging an AI-powered application
* Documenting a project for future users and developers

## Reflection

### Prompt Design

Designing the system prompt taught me that an LLM's behavior depends heavily on how its instructions are written. I used a system prompt to define the assistant's role, target audience, tone, and learning approach. I also created reusable prompt templates for concept explanations, practice questions, and feedback so that different learning tasks could follow a consistent structure.

### Conversation State Management

I learned that conversation state involves more than simply storing previous messages. The application maintains local conversation history while Gemini uses an interaction ID to continue the conversation across API requests. This also made it important to reset both forms of state when the `/clear` command is used.

### API Cost Awareness

Working with the Gemini API showed me that API usage is subject to quotas and limits. During testing, I reached the available daily request limit, which helped me understand why unnecessary API calls should be avoided. I also learned to distinguish temporary API errors from quota exhaustion so that the application does not repeatedly retry a request when retrying will not help.

## Future Improvements

Potential improvements for future versions include:

* Add a graphical or web-based user interface
* Add more structured NLP learning modes and topics
* Improve conversation history management and persistence
* Add more advanced practice and assessment features
* Add automated tests for core application functions
* Improve prompt handling for different learner levels
* Add configurable model and response settings