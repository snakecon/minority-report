# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The algorithm module, used for preprocess text and ranking answers.

Authors: Snakecon (snakecon@gmail.com)
"""
import os
import random
import pickle
from time import sleep

from precogs.exceptions import PipelineException
from precogs.puzzles import Puzzle
from precogs.search_engines import BaiduWireless
from precogs.search_engines import Bing
from precogs.search_engines import Google
from precogs.search_engines import Baidu

__author__ = 'snakecon@gmail.com'


class Colors:
    blue = '\033[94m'
    red = "\033[1;31m"
    green = '\033[0;32m'
    end = '\033[0m'
    bold = '\033[1m'


class BasicRanker(object):
    def __init__(self, flags):
        self.flags = flags
        precog = self.flags.precog.lower()
        if precog == "agatha":
            self.search_engine = Google(flags)
        elif precog == "arthur":
            self.search_engine = Bing(flags)
        elif precog == "dash":
            self.search_engine = BaiduWireless(flags)
        elif precog == "dash2":
            self.search_engine = Baidu(flags)
        else:
            raise PipelineException("Invalid precog", precog)

        self.cache = {}
        self.cache_data_path = 'data/cache.pickle'
        if os.path.exists(self.cache_data_path):
            print "Load cache..."
            with open(self.cache_data_path, 'r') as cache_file:
                self.cache = pickle.load(cache_file)

    def rank_answers(self, question_block):
        results, reverse = self.do_rank_answers(question_block)
        result_index = self.print_answers(results, reverse)
        return result_index

    def do_rank_answers(self, question_block):
        print "Rankings answers..."

        question = question_block["question"]
        ans_1 = question_block["ans_1"]
        ans_2 = question_block["ans_2"]
        ans_3 = question_block["ans_3"]

        reverse = True

        if "不是" in question.lower()\
                or "不可能" in question.lower()\
                or "不包含" in question.lower()\
                or "不属于" in question.lower():
            print "Reversing results..."
            reverse = False

        text = self._serach_with_cache([question], 50)

        results = [
            {"ans": ans_1, "count": text.count(ans_1)},
            {"ans": ans_2, "count": text.count(ans_2)},
            {"ans": ans_3, "count": text.count(ans_3)}
        ]

        sorted_results = [
            {"ans": ans_1, "count": text.count(ans_1)},
            {"ans": ans_2, "count": text.count(ans_2)},
            {"ans": ans_3, "count": text.count(ans_3)}
        ]

        sorted_results.sort(key=lambda x: x["count"], reverse=reverse)

        # If there's a tie redo with answers in q
        if sorted_results[0]["count"] == sorted_results[1]["count"]:
            print "Running tiebreaker..."

            text = self._serach_with_cache([question, ans_1, ans_2, ans_3], 50)

            results = [
                {"ans": ans_1, "count": text.count(ans_1)},
                {"ans": ans_2, "count": text.count(ans_2)},
                {"ans": ans_3, "count": text.count(ans_3)}
            ]

        return results, reverse

    def print_answers(self, results, reverse):
        print ''
        small = min(results, key=lambda x: x["count"])
        large = max(results, key=lambda x: x["count"])

        result_index = 0
        for (i, r) in enumerate(results):
            text = "%s. %s - %s" % (i, r["ans"], r["count"])

            if r["ans"] == large["ans"]:
                if reverse:
                    result_index = i
                print Colors.green + text + Colors.end
            elif r["ans"] == small["ans"]:
                if not reverse:
                    result_index = i
                print Colors.red + text + Colors.end
            else:
                print text
        print ''
        return result_index

    def _serach_with_cache(self, q_list, num):
        cache_key = " ".join([self.flags.precog] + q_list)
        if cache_key in self.cache:
            return self.cache[cache_key]

        result = self.search_engine.search(q_list, num)
        self.cache[cache_key] = result

        return result

    def benchmark(self):
        puzzle_set = Puzzle(self.flags)

        total = 0
        corrent = 0
        for puzzle in puzzle_set.puzzles:
            try:
                if u'index' in puzzle and u'ans_1' in puzzle and u'ans_2' in puzzle\
                        and u'ans_3' in puzzle and u'question' in puzzle:
                    sleep(2 * random.random())

                    serial_puzzle = {}
                    for item in [u'question', u'ans_1', u'ans_2', u'ans_3']:
                        serial_puzzle[item.encode('utf-8')] = puzzle[item].encode('utf-8')

                    result_index = self.rank_answers(serial_puzzle)
                    label_index = puzzle[u'index']

                    total += 1
                    if result_index == label_index:
                        corrent += 1

                    print "Question: %s" % puzzle[u'question'].encode('utf-8')
                    print "Precog: %s, Total: %d, Correct: %d, Acc: %f" % (self.flags.precog, total, corrent, float(corrent)/ float(total))
                    if self.flags.dump_cache:
                        self._dump_cache()
            except PipelineException as e:
                print e.message

    def _dump_cache(self):
        with open(self.cache_data_path, 'w') as cache_file:
            pickle.dump(self.cache, cache_file)


if __name__ == "__main__":
    class Flag(object):
        def __init__(self):
            self.precog = 'arthur'
            self.debug = False
            self.dump_cache = False
    ranker = BasicRanker(Flag())
    ranker.benchmark()

    # Benchmark:
    # Precog: Arthur, Total: 290, Correct: 212, Acc: 0.731034
    # Precog: Dash, Total: 290, Correct: 218, Acc: 0.751724
    # Precog: Dash2, Total: 290, Correct: 219, Acc: 0.755172
    # Precog: Agatha, Total: 55, Correct: 43, Acc: 0.781818
