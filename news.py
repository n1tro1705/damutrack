from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup, Tag

@dataclass
class Article:
    author_name: Tag
    topic: Tag
    time: Tag
    title: Tag
    subtitle: Tag

def parse_news():
    url = 'https://vc.ru/popular'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='html.parser')
    result = []
    for block in soup.select('div.content.content--short'):
        author_name = block.select_one('a.author__name')
        topic = block.select_one('a.content-header__topic')
        time = block.select_one('time')
        title = block.select_one('div.content-title')
        subtitle = block.select_one('div.block-text>p')
        result.append(Article(author_name, topic, time, title, subtitle))
    return result