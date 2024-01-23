import os
import openai
from datetime import date
import feedparser as fp
from dateutil import parser
import ssl
import pickle


ssl._create_default_https_context = ssl._create_unverified_context

from app import app, db, Article

app.app_context().push()
# db.drop_all()
# db.create_all()

relevant = pickle.load(open('relevancy.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))


def relevancy(text):
    text = str(text)
    tfidf_text = vectorizer.transform([text])
    pred = relevant.predict(tfidf_text)
    return pred.item()

# Set your OpenAI API key
api_key = ''
openai.api_key = api_key

keywords = ['5G', 'AI', 'Award', 'Banking as a Service', 'Biometrics',
           'Blockchain', 'Central Bank Digital Currency', 'Cloud', 'Crypto', 'Cybersecurity',
           'Decentralized ID', 'DeFi', 'Digital', 'Digital ID',
           'Digital Lending', 'Embedded Banking', 'Fines', 'FinTech',
           'Tech Innovation', 'Metaverse', 'NFTs', 'Open Banking',
           'Passwordless authentication', 'Payments', 'Quantum',
           'Real-Time Payments', 'Sustainability', 'Sustainable Finance',
           'Tech Talent', 'Tech Spend', "Other"]

def pred_tags(text):
    prompt = f"Given the description: '{text}', tag one relevant keywords from this list: '{keywords}'. If it's not related to any of the keywords, tag 'Other'"

    response = openai.Completion.create(
        engine="text-davinci-003",  
        prompt=prompt,
        max_tokens=20,  # Limit the number of tokens in the response
        stop=None  # Let the model generate keywords
    )

    generated_keywords = response.choices[0].text.strip()
    return generated_keywords

sites = ["https://www.finextra.com/rss/headlines.aspx", 
         "https://www.coindesk.com/arc/outboundfeeds/rss/"]


for i in sites:
    feed = fp.parse(i)

    article_title = feed.channel.title

    for item in feed.entries:

        result = relevancy(item.title) #check if development is relevant to us and fits criteria

        exists = db.session.query(db.session.query(Article).filter_by(title=item.title).exists()).scalar() #check if development is in database already

        if (result == 'relevant') and (not exists):
            # print(item.title)

            labels = pred_tags(item.title)
            # print(labels)
            
            pub = parser.parse(item.published)
            pub = pub.date()

            article = Article(
                title=item.title,
                description=item.description,
                pub_date=pub,
                link=item.link,
                source=article_title,
                # tag = ', '.join(labels)
                tag = pred_tags(item.title)
            )

            db.session.add(article)
            db.session.commit()



