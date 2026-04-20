# docsum AI chat tool

![Doctests](https://github.com/avankomen25/LLM-Project/actions/workflows/tests.yaml/badge.svg)
![Integration Tests](https://github.com/avankomen25/LLM-Project/actions/workflows/integration-tests.yaml/badge.svg)
![Flake8](https://github.com/avankomen25/LLM-Project/actions/workflows/flake8.yaml/badge.svg)
[![codecov](https://codecov.io/github/avankomen25/LLM-Project/graph/badge.svg?token=K97YWXIYUX)](https://codecov.io/github/avankomen25/LLM-Project)
[![PyPI](https://img.shields.io/pypi/v/cmc-csci040-andrewvankomen)](https://pypi.org/project/cmc-csci040-andrewvankomen/)

<!-- the PyPI button should be the link to your pypi page (that's the whole point!) -->

A command-line AI chat tool that lets you have conversations with your codebase. Point it at any project and ask questions. It can read files, search for patterns, and list directories automatically.

![Demo](https://raw.githubusercontent.com/avankomen25/LLM-Project/master/llmdemo.gif)

## Examples

"Usage" implies a reference explaining what something does without examples.
(Run `chat --help` for an example.)

Also, you need to have a sentence explaining something right here... never have a header without something after it.

### eBay Scraper

You should put the explanations of codeblocks/images before the codeblock image.

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
The script scrapes eBay search result pages, extracting each listing’s name, price, status, shipping cost, free‑returns flag, and number of items sold. It outputs the collected data to JSON (or CSV).
```

### Markdown Compiler

This example shows automatic tool use where the LLM reads the README on its own to answer the question.

```bash
$ cd test_projects/markdown_compiler
$ chat
chat> what does this project do?
It’s a simple command‑line tool that reads a Markdown file and compiles it into an HTML document, optionally adding a CSS stylesheet for nicer formatting.
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
- **https://izbicki.me/** (Mike Izbicki’s personal webpage)
- **https://sophia09zheng13.github.io/** (Sophia’s webpage)
```
