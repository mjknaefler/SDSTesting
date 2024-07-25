from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import requests
from webdriver_manager.chrome import ChromeDriverManager
import threading as thr
from queue import Queue
import time
import csv

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
        self.testInternalLinks()
        self.testExternalLinks()
        
        
    
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

    def requestInternalLink(self,key):

        if self.internal_links[key].startswith('https://'):
            try:
                request = requests.head(self.internal_links[key], headers=self.headers, timeout=5)
                if request.ok:
                    self.working_internal_links[key] = self.internal_links[key]
                else:
                    self.broken_internal_links[key] = self.internal_links[key]
            except:
                self.broken_internal_links[key] = self.internal_links[key]
        else:
            self.broken_internal_links[key] = self.internal_links[key]

    def workInternal(self,input_q):
        while True:
            item = input_q.get()
            if item == "STOP":
                break
            self.requestInternalLink(item)



    def testInternalLinks(self):
        print("\nTesting internal links...")
        input_q = Queue()
        threads_number = 8
        workers = [thr.Thread(target=self.workInternal, args=(input_q,),) for i in range(threads_number)]
        for w in workers:
            w.start()
        for task in self.internal_links:
            input_q.put(task)
        for i in range(threads_number):
            input_q.put("STOP")
        for w in workers:
            w.join()
            
        print("\nFinished testing internal links")
    
    def requestExternalLink(self,key):

        if self.external_links[key].startswith('https://'):
            try:
                request = requests.head(self.external_links[key], headers=self.headers, timeout=5)
                if request.ok:
                    self.working_external_links[key] = self.external_links[key]
                else:
                    self.broken_external_links[key] = self.external_links[key]
            except:
                self.broken_external_links[key] = self.external_links[key]
        else:
            self.broken_external_links[key] = self.external_links[key]

    def workExternal(self,input_q):
        while True:
            item = input_q.get()
            if item == "STOP":
                break
            self.requestExternalLink(item)



    def testExternalLinks(self):
        print("\nTesting external links...")
        input_q = Queue()
        threads_number = 8
        workers = [thr.Thread(target=self.workExternal, args=(input_q,),) for i in range(threads_number)]
        for w in workers:
            w.start()
        for task in self.external_links:
            input_q.put(task)
        for i in range(threads_number):
            input_q.put("STOP")
        for w in workers:
            w.join()
        print(f"{self.working_external_links}\n\n\n\n\n\n\n\n{self.broken_external_links}")


if __name__ == "__main__":
    start_time = time.time()
    linkCheckerObj = LinkChecker("https://findbestdev.wpengine.com/")
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")