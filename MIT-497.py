Python 3.12.5 (tags/v3.12.5:ff3bc82, Aug  6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license()" for more information.
>>> class SitemapParser:
...     def init(self, sitemap_url):
...         self.sitemap_url = sitemap_url
... 
...     def get_monthly_sitemap(self):
... 
...         class SitemapFetcher:
...             def _init_(self, sitemap_url):
...                 self.sitemap_url = sitemap_url
... 
... import os
... import json
... import requests
... from dataclasses import dataclass
... from datetime import datetime
... from bs4 import BeautifulSoup
... from langdetect import detect, DetectorFactory, LangDetectException
... from typing import Optional, List
... @dataclass
... class Article:
...     url: str
...     postid: str
...     title: str
...     keywords: list[str]
...     thumbnail: str
...     word_count: int
...     publication_date: str
...     last_updated: str
...     author: str
...     content: str
...     video_duration:str
...     lang: str
...     description: str
...     classes: List[dict]
... 
... 
... 
... class SitemapParser:
...     def init(self, sitemap_index_url):
...         self.sitemap_index_url = sitemap_index_url

    def get_monthly_sitemap_urls(self):
        response = requests.get(self.sitemap_index_url)
        soup = BeautifulSoup(response.text, 'xml')
        return [loc.text for loc in soup.find_all('loc')]

    def extract_article_urls(self, monthly_sitemap_url):
        response = requests.get(monthly_sitemap_url)
        soup = BeautifulSoup(response.text, 'xml')
        return [loc.text for loc in soup.find_all('loc')]

    def post_init(self):
        if self.word_count is None:
            self.word_count = len(self.content.split())


class ArticleScraper:
    def init(self):
        # Disable language detection model caching to avoid thread safety issues
        DetectorFactory.seed = 0
    def detect_language_with_langdetect(self, text: str):
        try:
            detected_lang = detect(text)
            return detected_lang, 1.0
        except LangDetectException:
            return "unknown", 0.0

    def generate_description(self, content: str):
        # Implement logic to generate a description from the article content
        if len(content) > 800:
            return content[:800] + "..."
        else:
            return content

    def extract_author(self, soup: BeautifulSoup):
        # Implement logic to extract the author from the webpage
        author_tag = soup.find('a', {'class': 'author-link'})
        if author_tag:
            return author_tag.text.strip()
        else:
            return 'unknown'



    def extract_classes(self, soup: BeautifulSoup):
        # Implement logic to extract the classes (or categories) from the webpage
        class_tags = soup.find_all('a', {'class': 'article-class'})
        classes = [tag.text.strip() for tag in class_tags]
        return classes

    def scrape_article(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        script_tag = soup.find('script', {'type': 'text/tawsiyat'})
        if script_tag:

                script_data = json.loads(script_tag.string)
                postid =  script_data['postid']
                title = script_data['title']
                keywords = ''.join(script_data['keywords'])
                thumbnail = script_data['thumbnail']
               # "published_time": "2024-07-10T19:10:05+03:00",
               # "last_updated": "2024-07-10T19:12:36+03:00",
                publication_date = script_data['published_time']
                last_updated = script_data['last_updated']
                content = '\n'.join([p.get_text() for p in soup.find_all('p')])
                word_count = len(content.split())
                video_duration = self.extract_video_duration(soup)
                author = script_data['author']
                lang = self.detect_language_with_langdetect(content)
                description = self.generate_description(content)
                classes = script_data['classes']#self.extract_classes(soup)


                return Article(
                    url=url,
                    postid=postid,
                    title=title,
                    keywords=keywords,
                    thumbnail=thumbnail,
                    publication_date=publication_date,
                    last_updated=last_updated,
                    video_duration=video_duration,
                    author=author,
                    word_count=word_count,
                    content=content,
                    lang=lang,
                    description = description,
                    classes=classes

                )


        return None

    def extract_video_duration(self, soup: BeautifulSoup):
        video_tag = soup.find('video')
        if video_tag and 'duration' in video_tag.attrs:
            return int(video_tag['duration'])
        return None

class FileUtility:
    def save_articles_to_json(self, articles, year, month):
        filename =  f"articles\\articles_{year}_{month:02}.json"
        with open( filename, 'w', encoding='utf-8') as file:
            json.dump([article.dict for article in articles], file, ensure_ascii=False, indent=4)

def main():
    sitemap_index_url = "https://www.almayadeen.net/sitemaps/all.xml"
    parser = SitemapParser(sitemap_index_url)

    monthly_sitemap_urls = parser.get_monthly_sitemap_urls()
    scraper = ArticleScraper()
    file_util = FileUtility()

    monthly_articles_count=0
    for monthly_sitemap_url in monthly_sitemap_urls:
        article_urls = parser.extract_article_urls(monthly_sitemap_url)
        articles = []
        articles_count = 0
        for article_url in article_urls:
            try:
                article = scraper.scrape_article(article_url)
            except Exception as e:
                print(f"Error scraping article from {article_url}: {e}")
                continue

            if article:
                articles.append(article)
                articles_count += 1
                if articles_count >= 5:
                    break

        year_month = monthly_sitemap_url.split('/')[-1].split('-')
        year = int(year_month[1])
        month = int(year_month[2].replace('.xml', ''))
        filename = f"output\\articles_{year}_{month:02}.json"
        file_util.save_articles_to_json(articles, year, month)
        print(f"Saved articles for {year}-{month:02}")
        monthly_articles_count += 1
        if monthly_articles_count >= 5:
