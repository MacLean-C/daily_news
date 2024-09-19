import streamlit as st
import feedparser
from bs4 import BeautifulSoup
import requests
import justext
import textwrap
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch


def wrap_text(text, width=70):
    wrapped_text = textwrap.fill(text, width)
    return wrapped_text

@st.cache_resource  
def load_model():
    return T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

@st.cache_resource
def load_device():
    return "cuda:0" if torch.cuda.is_available() else "cpu"

@st.cache_resource  
def load_tokenizer():
    return T5Tokenizer.from_pretrained("google/flan-t5-base")

def clean_text(text, language):
    """justext is the best solution I have found to remove boilerplate text.
    Without this function, boilerplate HTML can be summarized instead of
    article content.

    Args:
        text (str): text from webpage/article

    Returns:
        str: cleaned text from webpage/article
    """
    if not text:
        return ""
    texts = []
    paragraphs = justext.justext(text, justext.get_stoplist(language))
    for paragraph in paragraphs:
        if not paragraph.is_boilerplate:
            texts.append(paragraph.text)
    return " ".join(texts)


def get_and_print_page(url, language):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            
            text = response.content

            return wrap_text(clean_text(text, language))    
        
        else:
            st.error(
                f"Error: Unable to fetch the page. Status code: {response.status_code}"
            )
    except requests.RequestException as e:
        st.error(f"Error: {e}")


def extraction(i, feed, model, tokenizer, device, language):
    # change number for number of entries to show
    for i, entry in enumerate(feed.entries[i:i+10]):
        st.subheader(f"Entry {i + 1}:")

        st.write(f"**Title:** {entry.title}")

        if "published" in entry:
            st.write(f"**Published:** {entry.published}")
        elif "updated" in entry:
            st.write(f"**Updated:** {entry.updated}")
        summary_text1 = get_and_print_page(entry.link, language)
        summary_text = tokenize_cat_summaries(summary_text1, language, model, tokenizer, device)
        st.write(f"**Summary:** {summary_text}")

        link = entry.link
        st.write(f"Link: {link}")
        #st.write("**Page Content:** ?")
        
        #show_text = st.checkbox("**Read Full Article?**", key=link)
        #if show_text:
         #   st.code(summary_text1)
        

def tokenize_cat_summaries(text, language, model, tokenizer, device, chunk_size=512):
    # Download the punkt tokenizer if not already installed
    #nltk.download('punkt', quiet=True)
        
    words = text.split(' ')
    chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

    summaries = []
    for chunk in chunks:
        torch.cuda.empty_cache()
        chunk = ' '.join(chunk)
        input_ids = tokenizer.encode(
                            f"Summarize in {language}: "
                            + chunk,
                            return_tensors="pt",
                        ).to(device)
                       
        summary = model.generate(
                            input_ids, max_length=300, num_beams=2, early_stopping=True
                        )
        summary = tokenizer.decode(summary[0], skip_special_tokens=True)
        summaries.append(summary)
      
    final_summary = ' '.join(summaries) 
    return final_summary
    
if __name__ == "__main__":
    st.title("Newsreader")
    
    tokenizer = load_tokenizer()
    device = load_device()
    model = load_model().to(device)
    
    #snltk.download('stopwords')
    language = st.selectbox("Please select the language of the publication: ",["English", "French", "German", "Spanish"])
    
    i = 0
    def plus_ten(i):
        return i+10
    #next_10_stories = st.button(label="Next 10 Stories", on_click=plus_ten(i))

    if language:
        
        suggestion_dico = {
    
        'BBC': 'http://feeds.bbci.co.uk/news/rss.xml',
        'The New York Times': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',
        'Reuters': 'https://www.reutersagency.com/feed/?taxonomy=best-sectors&post_type=best',
        'Steam': 'http://www.steampowered.com/rss.xml',
        'France Inter':'https://www.radiofrance.fr/franceinter/rss', 
        'Le Monde': 'https://www.lemonde.fr/rss/une.xml',
        'Franceinfo': 'https://www.francetvinfo.fr/titres.rss',
        '20 Minutes': 'https://www.20minutes.fr/rss/une.xml',
        'BFMTV': 'https://www.bfmtv.com/rss/',
        'Slate': 'https://www.slate.fr/rss.xml',
        'Der Spiegel': 'https://www.spiegel.de/schlagzeilen/index.rss'
    
}
        
        rss_url2 = st.text_input("Enter a URL")
        existing_site = st.checkbox("Choose a site?")
        
        if existing_site:
            rss_url2 = st.selectbox("Choose a website", suggestion_dico)
            url = suggestion_dico[rss_url2]
            
        go = st.checkbox("Load news summaries")
        if go:
            url = str(rss_url2)
            feed = feedparser.parse(url)
            extraction(i, feed, model, tokenizer, device, language)
        
        
        
## relire checkbox, il parait que tout se reexecute pour afficher le texte d'un seul article