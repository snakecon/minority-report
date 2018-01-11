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
import pickle
import random
import re
import uniout
import jieba
import jieba.analyse
from collections import Counter
from time import sleep

from precogs.exceptions import PipelineException
from precogs.puzzles import Puzzle
from precogs.search_engines import Baidu
from precogs.search_engines import BaiduWireless
from precogs.search_engines import Bing
from precogs.search_engines import Google

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

        jieba.initialize()

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
            {"ans": ans_1, "count": self._count(text, ans_1)},
            {"ans": ans_2, "count": self._count(text, ans_2)},
            {"ans": ans_3, "count": self._count(text, ans_3)}
        ]

        sorted_results = [
            {"ans": ans_1, "count": self._count(text, ans_1)},
            {"ans": ans_2, "count": self._count(text, ans_2)},
            {"ans": ans_3, "count": self._count(text, ans_3)}
        ]

        sorted_results.sort(key=lambda x: x["count"], reverse=reverse)

        # If there's a tie redo with answers in q
        if sorted_results[0]["count"] == sorted_results[1]["count"]:
            print "Running tiebreaker..."

            text = self._serach_with_cache([question, ans_1, ans_2, ans_3], 50)

            results = [
                {"ans": ans_1, "count": self._count(text, ans_1)},
                {"ans": ans_2, "count": self._count(text, ans_2)},
                {"ans": ans_3, "count": self._count(text, ans_3)}
            ]

        return results, reverse

    def _count(self, text, ans):
        total_score = 0
        total_len = 0

        # Rule score.
        # match_count = 0
        # re_result = re.search(r"是.{0,2}(" + ans + ')', text)
        # if re_result is not None:
        #     match_count = len(re_result.groups())
        #
        # neg_match = 0
        # re_result = re.search(r"不是.{0,2}(" + ans + ')', text)
        # if re_result is not None:
        #     neg_match = len(re_result.groups())
        # total_score += 10 * match_count
        # total_score -= 10 * neg_match

        # Whole ans score.
        # total_score += len(ans) * text.count(ans)
        # total_len += len(ans)
        h_param = 3.5

        whole_score = text.count(ans)
        # Tags score.
        terms = jieba.analyse.extract_tags(ans, topK=3)
        for term in terms:
            total_score += text.count(term.encode('utf-8'))

        # Calculate average score.
        if len(terms) == 0:
            return h_param * whole_score
        return h_param * whole_score + float(total_score) / float(len(terms))

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
            print "Hit cache"
            return self.cache[cache_key]

        result = self.search_engine.search(q_list, num)
        self.cache[cache_key] = result

        return result

    def benchmark(self):
        puzzle_set = Puzzle(self.flags)

        total = 0
        corrent = 0

        wrong_questions = []

        for puzzle in puzzle_set.puzzles:
            try:
                if u'index' in puzzle and u'ans_1' in puzzle and u'ans_2' in puzzle\
                        and u'ans_3' in puzzle and u'question' in puzzle:

                    serial_puzzle = {}
                    for item in [u'question', u'ans_1', u'ans_2', u'ans_3']:
                        serial_puzzle[item.encode('utf-8')] = puzzle[item].encode('utf-8')

                    result_index = self.rank_answers(serial_puzzle)
                    label_index = puzzle[u'index']

                    total += 1
                    if result_index == label_index:
                        corrent += 1

                    print "Question: %s, Correct: %s" % (puzzle[u'question'].encode('utf-8'), result_index == label_index)
                    print "Precog: %s, Total: %d, Correct: %d, Acc: %f" % (self.flags.precog, total, corrent, float(corrent)/ float(total))

                    if result_index != label_index:
                        wrong_questions.append(puzzle[u'question'].encode('utf-8'))

                    if self.flags.sleep:
                        sleep(9 * random.random())

                    if self.flags.dump_cache:
                        self._dump_cache()
            except PipelineException as e:
                print e.message

        for wrong_question in wrong_questions:
            print wrong_question

    def benchmark_vote(self):
        puzzle_set = Puzzle(self.flags)

        flag1 = Flag()
        flag1.precog = 'arthur'
        v1 = BasicRanker(flag1)
        flag2 = Flag()
        flag2.precog = 'Dash'
        v2 = BasicRanker(flag2)
        flag3 = Flag()
        flag3.precog = 'dash2'
        v3 = BasicRanker(flag3)

        total = 0
        corrent = 0
        for puzzle in puzzle_set.puzzles[:517]:
            try:
                if u'index' in puzzle and u'ans_1' in puzzle and u'ans_2' in puzzle\
                        and u'ans_3' in puzzle and u'question' in puzzle:
                    serial_puzzle = {}
                    for item in [u'question', u'ans_1', u'ans_2', u'ans_3']:
                        serial_puzzle[item.encode('utf-8')] = puzzle[item].encode('utf-8')

                    result_index1 = v1.rank_answers(serial_puzzle)
                    result_index2 = v2.rank_answers(serial_puzzle)
                    result_index3 = v3.rank_answers(serial_puzzle)

                    result_index = Counter([result_index1, result_index2, result_index3]).most_common(1)[0][0]

                    if result_index != result_index3:
                        print "Not baiduwireless"

                    label_index = puzzle[u'index']

                    total += 1
                    if result_index == label_index:
                        corrent += 1

                    print "Question: %s, Correct: %s" % (puzzle[u'question'].encode('utf-8'), result_index == label_index)
                    print "Precog: %s, Total: %d, Correct: %d, Acc: %f" % ('dash2 + Dash + arthur', total, corrent, float(corrent)/ float(total))

                    if self.flags.sleep:
                        sleep(2 * random.random())

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
            self.precog = 'dash2'
            self.debug = False
            self.dump_cache = False
            self.sleep = False
    ranker = BasicRanker(Flag())
    if False:
        ranker.benchmark_vote()
    else:
        ranker.benchmark()

    # Benchmark:
    # Precog: Agatha, Total: 55, Correct: 43, Acc: 0.781818
    # Precog: arthur, Total: 55, Correct: 35, Acc: 0.636364
    # Precog: Dash, Total: 55, Correct: 43, Acc: 0.781818
    # Precog: dash2, Total: 55, Correct: 42, Acc: 0.763636
    # Precog: dash2 + Dash + arthur, Total: 55, Correct: 43, Acc: 0.781818

    # Benchmark II:
    # Original -- Precog: dash2, Total: 300, Correct: 230, Acc: 0.766667
    # The tags -- Precog: dash2, Total: 300, Correct: 236, Acc: 0.786667
    # The tags2 -- Precog: dash2, Total: 300, Correct: 238, Acc: 0.793333
    # The tags3 -- Precog: dash2, Total: 300, Correct: 243, Acc: 0.810000
    # The tags4 -- Precog: dash2, Total: 300, Correct: 248, Acc: 0.826667

