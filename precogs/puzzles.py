# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The puzzles script, fetch/load/save history puzzle.

Authors: Snakecon (snakecon@gmail.com)
"""
import json
import re
from time import sleep

import requests
from bs4 import BeautifulSoup

__author__ = 'snakecon@gmail.com'


class Puzzle(object):

    def __init__(self, flags):
        self.flags = flags
        self.filename = "data/puzzles.json"
        self.puzzles = []
        self.questions = set()
        self.loads()

    def loads(self):
        with open(self.filename, 'r') as puzzle_file:
            self.puzzles = json.loads(puzzle_file.read())
            for puzzle in self.puzzles:
                self.questions.add(puzzle[u'question'])

    def save(self, puzzle):
        serial_puzzle = {}
        for item in ['question', 'ans_1', 'ans_2', 'ans_3']:
            serial_puzzle[item.decode('utf-8')] = puzzle[item].decode('utf-8')

        if serial_puzzle[u'question'] in self.questions:
            return

        self.puzzles.append(serial_puzzle)
        self._save()

    def crawl(self):
        index_urls = [
            "https://zhidao.baidu.com/culture/topic?name=yingke",
            "https://zhidao.baidu.com/culture/topic?name=baiwanyingxiong",
            "https://zhidao.baidu.com/culture/topic?name=huajiao",
            "https://zhidao.baidu.com/culture/topic?name=chongding1",
        ]

        for url in index_urls:
            for puzzle_url in self._crawl_index(url):
                for puzzle in self._crawl_puzzle(puzzle_url):
                    sleep(2)
                    if puzzle[u'question'] in self.questions or u'index' not in puzzle:
                        continue
                    self.puzzles.append(puzzle)
                self._save()

    def _crawl_index(self, url):
        print "Crawl index url: %s" % url
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        divs = soup.find_all('div', {'class': 'item-outer'})

        for div in divs:
            yield div.find("a")['href']

    def _crawl_puzzle(self, url):
        print "Crawl puzzle url: %s" % url
        r = requests.get(url)
        r.encoding = 'gb2312'
        soup = BeautifulSoup(r.text, "lxml")
        div = soup.find('div', {'class': 'text-content'})

        if div is None or div.find_all('p') is None:
            return

        blocks = []
        sep = False
        for p in div.find_all('p'):
            p_text = p.text
            if re.match(r'^\d', p_text):
                sep = True
            if not sep:
                blocks.append(p_text)
            else:
                if len(blocks) != 0:
                    yield self._block_to_puzzle(blocks)
                sep = False
                blocks = [p_text]

    def _block_to_puzzle(self, blocks):
        serial_puzzle = {}

        index_dict = {
            "a": 0,
            "b": 1,
            "c": 2
        }

        for block in blocks:
            if re.match(ur'^\d', block):
                serial_puzzle[u'question'] = re.sub(r'^\d+', "", block).strip()
            if re.match(ur'^A', block):
                groups = re.match(r'A(.*)B(.*)C(.*)', block)
                if groups is None:
                    print "Can't find answer: %s" % json.dumps(blocks, ensure_ascii=False).encode('utf-8')
                    continue
                serial_puzzle[u'ans_1'] = groups.group(1).strip()
                serial_puzzle[u'ans_2'] = groups.group(2).strip()
                serial_puzzle[u'ans_3'] = groups.group(3).strip()
            if re.match(ur'^[正确,答案]', block):
                groups = re.match(ur'[正确,答案].*([ABCabc])', block)
                if groups is None:
                    print "Can't find index: %s" % json.dumps(blocks, ensure_ascii=False).encode('utf-8')
                    continue
                serial_puzzle[u'index'] = groups.group(1).strip().lower()

        for k, v in serial_puzzle.items():
            v = re.sub(ur'^,', u'', v)
            v = re.sub(ur'^\s', u'', v)
            v = re.sub(ur'^、', u'', v)
            v = re.sub(ur'^\.', u'', v)

            serial_puzzle[k] = v.strip()

        if u'index' in serial_puzzle:
            serial_puzzle[u'index'] = index_dict[serial_puzzle[u'index']]

        return serial_puzzle

    def _save(self):
        with open(self.filename, 'w') as puzzle_file:
            puzzle_file.write(json.dumps(self.puzzles, indent=4, sort_keys=True,
                                         ensure_ascii=False).encode('utf-8'))


if __name__ == "__main__":
    puzzle = Puzzle(None)
    puzzle.crawl()
