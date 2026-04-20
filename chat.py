"""A REPL-based chat interface that supports tool use for file system operations."""

import os   # noqa: F401
import json
import argparse

from groq import Groq
from dotenv import load_dotenv
# there's no need for both the openai and groq import;
# they both have the same code inside, and so you should only need one

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

    # the repl tests should be in the repl function

    # this isn't a super exciting test
    >>> chat_openai = Chat(provider='openai')
    >>> chat_openai.model
    'openai/gpt-4o'
    '''

    def __init__(self, provider='groq'):
        """Initialize the chat client with the specified provider."""
        if provider == 'groq':
            self.client = Groq()
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
        # this is dangerous, especially since you are using the openrouter;
        # if one of the AIs gets into a buggy loop where it always wants to use
        # a tool call no matter what, it will instantly deplete all your tokens
        # (you probably only have like $10 or some small amount,
        # but you could imagine a real company would need to have 10s of thousands in their account,
        # and all that would be gone instantly)
        # it is customary to make this a for loop so that termination is guaranteed
        # (I won't give you the provider ec this time due to this bug,
        # but if you fix the problem I'll give it to you on the next submission)
        while True:
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


def run_slash_command(chat, user_input):
    """
    Run a slash command manually and add the output to the chat context.

    >>> chat = Chat()
    >>> run_slash_command(chat, '/ls .')
    you should actually list the files here;
    there are no problems with determinism,
    and the purpose of a doctest is to actually show the output
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

    The repl tests should be here.
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
