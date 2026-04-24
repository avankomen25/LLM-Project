"""A REPL-based chat interface that supports tool use for file system operations."""

import os   # noqa: F401
import json
import argparse

from groq import Groq
from dotenv import load_dotenv

from tools.calculate import calculate, tool_definition as calculate_def
from tools.ls import ls, tool_definition as ls_def
from tools.cat import cat, tool_definition as cat_def
from tools.grep import grep, tool_definition as grep_def

load_dotenv()

TOOLS = [calculate_def, ls_def, cat_def, grep_def]
TOOL_MAP = {
    'calculate': calculate,
    'ls': ls,
    'cat': cat,
    'grep': grep,
}

PROVIDER_MODELS = {
    'groq': 'openai/gpt-oss-120b',
    'openai': 'openai/gpt-4o',
    'anthropic': 'anthropic/claude-opus-4-6',
    'google': 'google/gemini-2.0-flash',
}


class Chat:
    '''
    A chat interface that uses the Groq API with support for tool use.

    Supports automatic tool calling via the LLM and manual slash commands.

    >>> chat = Chat()
    >>> chat.send_message('Hello!', temperature=0.0)
    'Hello! How can I help you with your code today?'
    '''
    MODEL=PROVIDER_MODELS['groq']

    def __init__(self, provider='groq'):
        """Initialize the chat client with the specified provider."""
        if provider == 'groq':
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        else:
            self.client = Groq(
                base_url='https://openrouter.ai/api/v1',
                api_key=os.environ.get('OPENROUTER_API_KEY'),
            )
        self.model = PROVIDER_MODELS[provider]
        self.messages = [
            {
                'role': 'system',
                'content': (
                    'You are a helpful assistant that answers questions about code. '
                    'You MUST use the provided tools to answer questions, never say you cannot access files. '
                    'When asked about files or directories, immediately call ls, cat, or grep. '
                    'Do not describe what you will do, just do it. '
                    'Keep responses to 1-2 sentences.'
                )
            },
        ]

    def send_message(self, message, temperature=0.8):
        """Send a message and return the assistant response, handling tool calls if needed."""
        self.messages = self.messages[:1] + self.messages[-10:]
        self.messages.append({'role': 'user', 'content': message})
        for i in range(10):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=self.messages,
                    model=self.model,
                    temperature=temperature,
                    tools=TOOLS,
                    tool_choice='auto',
                )
            except Exception as e:
                return f'Error: {e}'
            choice = chat_completion.choices[0]
            if choice.finish_reason == 'tool_calls':
                self.messages.append(choice.message)
                for tool_call in choice.message.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments or '{}') or {}
                    result = TOOL_MAP[name](**args)
                    self.messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.id,
                        'name': name,
                        'content': result,
                    })
            else:
                result = choice.message.content
                self.messages.append({'role': 'assistant', 'content': result})
                return result
        return 'Max tool call iteration reached'


def run_slash_command(chat, user_input):
    """
    Run a slash command manually and add the output to the chat context.

    >>> chat = Chat()
    >>> files = run_slash_command(chat, '/ls tools')
    >>> print(files)
    __init__.py
    __pycache__
    calculate.py
    cat.py
    grep.py
    ls.py
    utils.py
    >>> run_slash_command(chat, '/cat /etc/passwd')
    'Error: unsafe path'
    >>> run_slash_command(chat, '/unknowncmd')
    'Error: unknown command'
    """
    parts = user_input[1:].split()
    command = parts[0]
    args = parts[1:]
    if command not in TOOL_MAP:
        return 'Error: unknown command'
    result = TOOL_MAP[command](*args)
    chat.messages.append({'role': 'user', 'content': f'/{command} {" ".join(args)}'})
    chat.messages.append({'role': 'assistant', 'content': result})
    return result


def repl(temperature=0.8, provider='groq'):
    """Run the interactive chat REPL, supporting both messages and slash commands.

    >>> def monkey_input(prompt, user_inputs=['Hello, I am monkey.', 'Goodbye.']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> Hello, I am monkey.
    Hello, monkey! How can I help you today?
    chat> Goodbye.
    Goodbye! Feel free to return if you have any more questions.
    <BLANKLINE>
    >>> chat_openai = Chat(provider='openai')
    >>> chat_openai.model
    'openai/gpt-4o'
    >>> def monkey_input(prompt, user_inputs=['/ls .', 'Goodbye.']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /ls .
    ...
    chat> Goodbye.
    ...
    <BLANKLINE>
    """
    import readline  # noqa: F401
    chat = Chat(provider=provider)
    try:
        while True:
            user_input = input('chat> ')
            if user_input.startswith('/'):
                print(run_slash_command(chat, user_input))
            else:
                response = chat.send_message(user_input, temperature=temperature)
                print(response)
    except (KeyboardInterrupt, EOFError):
        print()


def main():
    """Entry point for the chat CLI."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--provider', default='groq', choices=PROVIDER_MODELS.keys())
    args = parser.parse_args()
    repl(provider=args.provider)


if __name__ == '__main__':
    main()
