import re
from os import environ
import requests
from bs4 import BeautifulSoup
import openai
from flask import Flask, redirect, render_template, request, url_for


app = Flask(__name__)
openai.api_key=environ.get("OPENAI_API_KEY")
openai.api_base=environ.get("OPENAI_API_BASE")
openai.api_type=environ.get("OPENAI_API_TYPE")
openai.api_version=environ.get("OPENAI_API_VERSION") # this may change in the future


def getArticle(url):
    text = ""
    try:
        r = requests.get(url)
        if r.status_code == 200:
            soup = BeautifulSoup(r.content, 'lxml')
            # title = soup.select_one("h1.title.title-large.article-title")
            # if (title != None):
            #     text += title.text.strip() + " "
            bul_title = soup.select_one("h2.bulletin-title")
            if (bul_title != None):
                text += bul_title.text.strip() + " "
            ingress = soup.select_one("div.text-body.text-body-sans-serif.article-lead")
            if (ingress != None):
                text += ingress.text.strip() + " "
            article_body = soup.find('div', {'class': 'article-body'})
            if (article_body == None):
                article_body = soup.find('div', {'class': 'bulletin-text'})
            if (article_body != None):
                paragraphs = article_body.find_all('p')
                for p in paragraphs:
                    if "Du trenger javascript for å" not in p.get_text() and not p.find_parent('figcaption'):
                        paragraph_text = p.get_text().strip()
                        text += paragraph_text + " "
    except Exception as e:
        app.logger.error(f"Error in getArticle: {e}")
    return text

def getUrl(url):
    pattern = r"(\d+\.\d{8})"
    match = re.search(pattern, url)
    if match:
        result = match.group(1)
        url = "https://www.nrk.no/" + result
        return url
    else:
        return None

@app.route("/", methods=("GET", "POST"))
def index():
    if request.method == "POST":
        requestText = request.form["tekst"]
        url = getUrl(requestText)
        if not (url == None): 
            textToAnalyze = generate_prompt(url)
        else:
            textToAnalyze = get_prompt() + requestText
        if (len(textToAnalyze) > 8000):
            textToAnalyze = textToAnalyze[:8000]
        if (len(textToAnalyze) > 100):
            res = ""
            try:
                response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=textToAnalyze,
                temperature=0.3,
                max_tokens=800,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                best_of=1,
                stop=None)
                #res=response.choices[0].message["content"]
                res = response['choices'][0]['text']
            except openai.error.InvalidRequestError as e:
                res =  f"En feil hos OpenAi har oppstått: {e}"
                app.logger.warning(f"Error in response from Azur/OpenAi: {e}")
            return redirect(url_for("index", result=res, requestText=requestText))

    result = request.args.get("result")
    return render_template("index.html", result=result)


def get_prompt():
    prompt = "Skriv tre vanlige, tre søkemotoroptimaliserte og tre korte tittelforslag samt en oppsummering av det viktigste i denne teksten med seks til åtte kulepunkter: "
    return prompt

def generate_prompt(url):
    text = getArticle(url)
    prompt = get_prompt() + "'" + text + "'"
    #prompt = f"Skriv tre vanlige, tre søkemotoroptimaliserte og tre korte tittelforslag samt en oppsummering av det viktigste i denne teksten med seks til åtte kulepunkter: '{text}'"
    return prompt

if __name__ == "__main__":
    port = int(environ.get('PORT', 80))
    app.run(debug=True, host='0.0.0.0', port=port)

