"""Tool definition and implementation for evaluating arithmetic expressions."""


def calculate(expression):
    """
    Evaluate a mathematical expression and return the result as a string.

    >>> calculate('2 + 2')
    '4'
    >>> calculate('10 * 3')
    '30'
    >>> calculate('not valid')
    'Error: invalid expression'
    >>> calculate('2 ** 8')
    '256'
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception:
        return 'Error: invalid expression'


tool_definition = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The arithmetic expression to evaluate.",
                }
            },
            "required": ["expression"],
        },
    },
}
