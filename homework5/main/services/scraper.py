from itertools import count

from bs4 import BeautifulSoup

from .request_handler import ProxyRequest


def medusweet_scraper():

    request_handler = ProxyRequest()
    super_request = request_handler.get

    link = 'https://medusweet.com.ua/category/%d0%b1%d0%bb%d0%be%d0%b3/page/'
    article_links = []

    for page in count(start=1):
        request = super_request(link + str(page) + '/')

        if request_handler.status_code == 404:
            print('status_code 404')
            break

        soup = BeautifulSoup(request.content, 'html.parser')

        anchors = soup.select('h3 a', attrs={'class': 'post_title'})
        for anchor in anchors:
            article_links.append(anchor['href'])

    result = {
        'titles': [],
        'contents': [],
    }

    for article in article_links:
        request = super_request(article)
        if request_handler.status_code == 404:
            print('status_code 404')
            continue

        soup = BeautifulSoup(request.content, 'html.parser')

        title = soup.find('h1', attrs={'class': 'page_title'}).text.strip()
        content = soup.find('section', attrs={'class': 'post_content'})
        content_stripped = ' '.join([p.text.strip() for p in content])

        result['titles'].append(title)
        result['contents'].append(content_stripped)

    return result
