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
from precogs.exceptions import PipelineException
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
        else:
            raise PipelineException("Invalid precog", precog)

        self.cache = {}

    def rank_answers(self, question_block):
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

        result_index = self.print_answers(results, reverse)
        return result_index

    def print_answers(self, results, reverse):
        print ''
        small = min(results, key=lambda x: x["count"])
        large = max(results, key=lambda x: x["count"])

        result_index = 0
        for (i, r) in enumerate(results):
            text = "%s. %s - %s" % (i, r["ans"], r["count"])

            if r["ans"] == large["ans"]:
                color = Colors.green
                if reverse:
                    result_index = i
                    color = Colors.red
                print color + text + Colors.end
            elif r["ans"] == small["ans"]:
                color = Colors.red
                if not reverse:
                    color = Colors.green
                    result_index = i
                print color + text + Colors.end
            else:
                print text
        print ''
        return result_index

    def _serach_with_cache(self, q_list, num):
        cache_key = " ".join(q_list)
        if cache_key in self.cache:
            raise PipelineException("Cache hit, key: %s" % cache_key)

        result = self.search_engine.search(q_list, num)
        self.cache[cache_key] = result

        return result
