from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
import re
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup


class LinkChecker:
    
    def __init__(self, link):
        self.link = link
        self.internal_links = dict()
        self.external_links = dict()
        self.empty_links = dict()
        self.bad_links = dict()
        self.visited_links = list()
        self.working_internal_links = dict()
        self.working_external_links = dict()
        self.broken_internal_links = dict()
        self.broken_external_links = dict()
        self.edu_with_nofollow = dict()
        self.edu_missing_nofollow = dict()
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        print('Sorting links')
        self.sortLinks(self.link)
        print('\nLinks sorted')
        self.testLinks()
        
    
    def sortLinks(self,link):
        link_text_dict = dict()
        local_internal_links = dict()
        response = requests.get(link, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup.find_all("a"):
            href = tag.get('href')
            text = tag.text
            if href != None and '.edu' in href:
                if 'rel' in tag.attrs and "nofollow" in tag['rel']:
                    if href not in self.edu_with_nofollow.values():
                        self.edu_with_nofollow[text]=href
                else:
                    if href not in self.edu_missing_nofollow.values():
                        self.edu_missing_nofollow[text]=href
            link_text_dict[text] = href
        
        for text,href in link_text_dict.items():
            if href == None:
                continue
            if href.startswith('https://findbestdev'):
                if href not in self.internal_links.values():
                    self.internal_links[text] = href
                    local_internal_links[text] = href
            elif href.startswith('#'):
                if text not in self.empty_links:
                    self.empty_links[text] = href
            else:
                if href not in self.external_links.values() and href.startswith('https://'):
                    self.external_links[text] = href
                else:
                    self.bad_links[text] = href

        self.visited_links.append(link)
        for href in local_internal_links.values():
            if href not in self.visited_links:
                self.sortLinks(href)


    def testLinks(self):
        print("\nTesting internal links...")
        for text, href in self.internal_links.items():
            if href.startswith('https://'):

                request = requests.get(href, headers=self.headers)
                if request.ok:
                    self.working_internal_links[text] = href
                else:
                    self.broken_internal_links[text] = href
            else:
                self.broken_internal_links[text] = href
        print("\nFinished testing internal links\nTesting external links...")
        for text, href in self.external_links.items():
            if href.startswith('https://'):
                try:
                    request = requests.get(href, headers = self.headers, timeout=10)
            
                    if request.ok:
                        self.working_external_links[text] = href
                    else:
                        self.broken_external_links[text] = href
                except:
                    self.broken_external_links[text] = href
            else:
                self.broken_external_links[text] = href




if __name__ == "__main__":
    linkCheckerObj = LinkChecker("https://findbestdev.wpengine.com/")