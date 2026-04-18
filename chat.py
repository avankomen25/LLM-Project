"""A REPL-based chat interface that supports tool use for file system operations."""

import os   # noqa: F401
import json
import argparse

from groq import Groq
from dotenv import load_dotenv
from openai import OpenAI

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
    'groq': 'llama-3.1-8b-instant',
    'openai': 'openai/gpt-4o',
    'anthropic': 'anthropic/claude-opus-4-6',
    'google': 'google/gemini-2.0-flash',
}


class Chat:
    '''
    A chat interface that uses the Groq API with support for tool use.

    Supports automatic tool calling via the LLM and manual slash commands.

    >>> chat = Chat()
    >>> chat.send_message('Hi, my name is Bob', temperature=0.0)
    "Hello Bob, it's nice to meet you."
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
    Hello monkey, I'm here to help you with any questions you have about code. What would you like to know?
    chat> Goodbye.
    See you later monkey.
    <BLANKLINE>
    '''

    def __init__(self, provider='groq'):
        """Initialize the chat client with the specified provider."""
        if provider == 'groq':
            self.client = Groq()
        else:
            self.client = OpenAI(
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
        self.messages = self.messages[:1] + self.messages[-10:]  # I want to trim history to avoid hitting token limits
        self.messages.append({'role': 'user', 'content': message})
        while True:
            chat_completion = self.client.chat.completions.create(
                messages=self.messages,
                model=self.model,
                temperature=temperature,
                tools=TOOLS,
                tool_choice='auto',
            )
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


def run_slash_command(chat, user_input):
    """
    Run a slash command manually and add the output to the chat context.

    >>> chat = Chat()
    >>> output = run_slash_command(chat, '/ls .')
    >>> 'chat.py' in output
    True
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
    """Run the interactive chat REPL, supporting both messages and slash commands."""
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
