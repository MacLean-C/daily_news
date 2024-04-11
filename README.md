# Newsreader

This is a simple newsreader application built using Streamlit. It allows you to fetch and summarize articles from various RSS feeds. You can choose the language of the publication and enter a valid link to an RSS feed to get started.

## Setup

Make sure you have the following dependencies installed:

- Streamlit
- feedparser
- BeautifulSoup
- requests
- justext
- transformers
- torch

You can install them via pip:

```bash
pip install streamlit feedparser beautifulsoup4 requests justext transformers torch
```

## Usage

1. Run the application by executing the Python script.
2. Select the language of the publication from the dropdown menu.
3. Enter a valid link to an RSS feed in the provided text input field.
4. Once the feed is loaded, you will see the titles of the latest articles along with their summaries.
5. You can click on the checkbox to read the full article text.

## Features

- Summarization: The application uses T5 Transformer model to generate summaries of articles.
- Language Support: You can choose from English, French, German, and Spanish languages.
- Customizable: You can easily extend the list of RSS feeds by adding them to the `suggestion_dico` dictionary.

Feel free to explore different RSS feeds and stay updated with the latest news!
