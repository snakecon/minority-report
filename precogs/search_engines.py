# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The search engine module, used for getting search items.

Authors: Snakecon (snakecon@gmail.com)
"""
import abc
import urllib

import requests
from bs4 import BeautifulSoup

from precogs import conf

__author__ = 'snakecon@gmail.com'


class SearchEngine(object):
    @abc.abstractmethod
    def search(self, q_list, num):
        pass


class Baidu(SearchEngine):
    def __init__(self, debug):
        self.debug = debug

    def search(self, q_list, num):
        pass


class Google(SearchEngine):
    def __init__(self, debug):
        self.debug = debug

    def search(self, q_list, num):
        params = {"q": " ".join(q_list), "num": num}
        url_params = urllib.urlencode(params)

        google_url = "https://www.google.com.hk/search?" + url_params

        r = requests.get(google_url, proxies=conf.PROXYS)
        if self.debug:
            print r.text

        soup = BeautifulSoup(r.text, "html.parser")
        spans = soup.find_all('span', {'class': 'st'})

        text = u" ".join([span.get_text() for span in spans]).lower().encode('utf-8').strip()

        return text


class Bing(SearchEngine):
    def __init__(self, debug):
        self.debug = debug

    def search(self, q_list, num):
        params = {"q": " ".join(q_list), "num": num}
        url_params = urllib.urlencode(params)

        bing_url = "https://cn.bing.com/search?q=" + url_params

        r = requests.get(bing_url)
        if self.debug:
            print r.text

        soup = BeautifulSoup(r.text, "html.parser")
        spans = soup.find_all('div', {'class': 'b_caption'})

        text = u" ".join([span.get_text() for span in spans]).lower().encode('utf-8').strip()

        return text

if __name__ == "__main__":
    bing = Bing(False)
    print bing.search(["华盛顿是哪一年去世的"], 10)
