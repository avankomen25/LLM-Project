"""A REPL-based chat interface that supports tool use for file system operations."""

import os   # noqa: F401
import json
import argparse

from groq import Groq
from openai import OpenAI  # I couldn't get the provder tag to work through Groq
from dotenv import load_dotenv

from tools.calculate import calculate, tool_definition as calculate_def
from tools.ls import ls, tool_definition as ls_def
from tools.cat import cat, tool_definition as cat_def
from tools.grep import grep, tool_definition as grep_def
from tools.write_file import write_file, tool_definition as write_file_def
from tools.write_files import write_files, tool_definition as write_files_def
from tools.rm import rm, tool_definition as rm_def
from tools.doctests import doctests, tool_definition as doctests_def

load_dotenv()

TOOLS = [calculate_def, ls_def, cat_def, grep_def, write_file_def, write_files_def, rm_def, doctests_def]
TOOL_MAP = {
    'calculate': calculate,
    'ls': ls,
    'cat': cat,
    'grep': grep,
    'write_file': write_file,
    'write_files': write_files,
    'rm': rm,
    'doctests': doctests,
}

PROVIDER_MODELS = {
    'groq': 'openai/gpt-oss-120b',
    'openai': 'openai/gpt-4o',
    'anthropic': 'anthropic/claude-opus-4',
    'google': 'google/gemini-2.0-flash',
}


class Chat:
    '''
    A chat interface that uses the Groq API with support for tool use.

    Supports automatic tool calling via the LLM and manual slash commands.
    I have to check for just the name in the response because the output is non-deterministic

    >>> chat = Chat()
    >>> response = chat.send_message('my name is Bob. Please remember this.', temperature=0.0)
    >>> response = chat.send_message('what is my name? Answer with just the name.', temperature=0.0)
    >>> 'Bob' in response
    True

    The response should not include the name 'Bob' if the conversation has not mentioned the name.

    >>> chat2 = Chat()
    >>> response = chat2.send_message('what is my name?', temperature=0.0)
    >>> 'bob' in response.lower()
    False
    '''

    def __init__(self, provider='groq'):
        """
        Initialize the chat client with the specified provider.

        Checking if provider is working
        >>> chat_openai = Chat(provider='openai')
        >>> print(chat_openai.model)
        openai/gpt-4o
        """
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
    doctests.py
    grep.py
    ls.py
    rm.py
    utils.py
    write_file.py
    write_files.py
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

    The repl accepts user input, handles slash commands directly, and prints the model's response.

    >>> def monkey_input(prompt, user_inputs=['/ls .github', 'Goodbye.']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)  # doctest: +ELLIPSIS
    chat> /ls .github
    workflows
    chat> Goodbye.
    ...
    <BLANKLINE>
    """
    import readline  # noqa: F401

    if not os.path.exists('.git'):
        print('Error: no .git folder found. Please run chat from a git repository.')
        return

    chat = Chat(provider=provider)

    if os.path.exists('AGENTS.md'):
        agents_content = cat('AGENTS.md')
        chat.messages.append({'role': 'user', 'content': f'AGENTS.md:\n{agents_content}'})
        chat.messages.append({'role': 'assistant', 'content': 'Loaded AGENTS.md instructions.'})

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
    parser.add_argument('message', nargs='?', default=None)
    args = parser.parse_args()
    if args.message:
        chat = Chat(provider=args.provider)
        print(chat.send_message(args.message))
    else:
        repl(provider=args.provider)


if __name__ == '__main__':
    main()
