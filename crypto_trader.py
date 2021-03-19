import requests 
from bs4 import BeautifulSoup

cryptos = []
url = 'https://finance.yahoo.com/cryptocurrencies?offset=0&count=100'
r = requests.get(url)
soup = BeautifulSoup(r.content, 'html.parser')
rows = soup.select('tbody tr')
for i in range(len(rows)):
    row = rows[i]
    name = row.select('a')[1]['data-symbol']
    crypto = name.replace('-USD', '')
    cryptos.append(crypto)

from psaw import PushshiftAPI
import datetime

api = PushshiftAPI()

start_time = int(datetime.datetime(2021, 1, 30).timestamp())

submissions = api.search_submissions(after = start_time,
                                     subreddit = 'CryptoCurrency',
                                     filter = ['url', 'author', 'title', 'subreddit'])

for submission in submissions:
    words = submission.title.split()
    cashtags = list(set(filter(lambda word: word.lower().startswith('$'), words)))
    
    if len(cashtags) > 0:
        print(cashtags)
        #print(submission.created_utc)
        #print(submission.title)
        #print(submission.url)