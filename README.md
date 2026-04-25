# docsum AI chat tool

![Doctests](https://github.com/avankomen25/LLM-Project/actions/workflows/tests.yaml/badge.svg)
![Integration Tests](https://github.com/avankomen25/LLM-Project/actions/workflows/integration-tests.yaml/badge.svg)
![Flake8](https://github.com/avankomen25/LLM-Project/actions/workflows/flake8.yaml/badge.svg)
[![codecov](https://codecov.io/github/avankomen25/LLM-Project/graph/badge.svg?token=K97YWXIYUX)](https://codecov.io/github/avankomen25/LLM-Project)
[![PyPI](https://img.shields.io/pypi/v/cmc-csci040-andrewvankomen)](https://pypi.org/project/cmc-csci040-andrewvankomen/)

A command-line AI chat tool that lets you have conversations with your codebase. Point it at any project and ask questions. It can read files, search for patterns, list directories, and write files automatically.

![Demo](https://raw.githubusercontent.com/avankomen25/LLM-Project/master/llmdemo.gif)

## Examples

The examples below show how to use `chat` with real projects. Run `chat --help` for a full list of options.

### eBay Scraper

This example shows how `/ls` loads the file list into context so the LLM can answer questions without making an extra tool call.

```bash
$ cd test_projects/ebay_scraper
$ chat
chat> /ls .
__pycache__
ebay-dl.py
hammer.csv
hammer.json
laptop.csv
laptop.json
stuffed_animal.csv
stuffed_animal.json
chat> what does this project scrape?
The script scrapes eBay search result pages, extracting each listing's name, price, status, shipping cost, free-returns flag, and number of items sold. It outputs the collected data to JSON (or CSV).
```

### Markdown Compiler

This example shows automatic tool use where the LLM reads the README on its own to answer the question.

```bash
$ cd test_projects/markdown_compiler
$ chat
chat> what does this project do?
It's a simple command-line tool that reads a Markdown file and compiles it into an HTML document, optionally adding a CSS stylesheet for nicer formatting.
```

### Webpage

This example shows automatic tool use where the LLM calls `grep` on its own to answer the question.

```bash
$ cd test_projects/webpage
$ chat
chat> what pages does this website link to?
- **style.css** (stylesheet)
- **index.html** (the fanpage itself)
- **nfcwest.html** (NFC West Guide)
- **2021superbowl.html** (2021 Superbowl)
- **https://github.com/mikeizbicki/cmc-csci040** (CSCI040 course webpage)
- **https://izbicki.me/** (Mike Izbicki's personal webpage)
- **https://sophia09zheng13.github.io/** (Sophia's webpage)
```

## Agent Examples

The examples below demonstrate the agent's ability to create, modify, and delete files, with all changes automatically committed to git.

### Creating a file

The session below shows the agent creating a new Python file and automatically committing it to git.

```bash
$ chat
chat> create a python file called hello.py that prints "hello world"
File `hello.py` has been created and prints "hello world".
$ ls
chat.py  hello.py  README.md  tools/  test_files/  ...
$ git log --oneline -3
2ca9828 (HEAD -> project4) [docchat] Add hello.py that prints hello world
77aba2f finalize project4
d440d0c [docchat] test
```

### Modifying a file

The session below shows the agent modifying an existing file and committing the change.

```bash
$ chat
chat> update hello.py to also print "goodbye world"
hello.py now prints both "hello world" and "goodbye world".
$ cat hello.py
print("hello world")
print("goodbye world")
$ git log --oneline -3
1300693 (HEAD -> project4) [docchat] Add goodbye world print
2ca9828 [docchat] Add hello.py that prints hello world
77aba2f finalize project4
```

### Deleting a file

The session below shows the agent deleting a file and committing the deletion.

```bash
$ chat
chat> delete hello.py
File `hello.py` has been deleted.
$ ls
chat.py  README.md  tools/  test_files/  ...
$ git log --oneline -3
fbb4b27 (HEAD -> project4) [docchat] rm hello.py
1300693 [docchat] Add goodbye world print
2ca9828 [docchat] Add hello.py that prints hello world
```

### Running doctests with the agent

The session below shows the agent running doctests on a file and reporting the results.

```bash
$ chat
chat> run the doctests on tools/utils.py
All doctests in `tools/utils.py` passed successfully.
```
