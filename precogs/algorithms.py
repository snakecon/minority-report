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
from precogs.search_engines import Google

__author__ = 'snakecon@gmail.com'


class Colors:
    blue = '\033[94m'
    red = "\033[1;31m"
    green = '\033[0;32m'
    end = '\033[0m'
    bold = '\033[1m'


class BasicRanker(object):
    def __init__(self, debug):
        self.debug = debug
        self.google = Google(debug)

    def rank_answers(self, question_block):
        print "Rankings answers..."

        question = question_block["question"]
        ans_1 = question_block["ans_1"]
        ans_2 = question_block["ans_2"]
        ans_3 = question_block["ans_3"]

        reverse = True

        if "不是" in question.lower() or "不可能" in question.lower():
            print "Reversing results..."
            reverse = False

        text = self.google.search([question], 50)

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

            text = self.google.search([question, ans_1, ans_2, ans_3], 50)

            results = [
                {"ans": ans_1, "count": text.count(ans_1)},
                {"ans": ans_2, "count": text.count(ans_2)},
                {"ans": ans_3, "count": text.count(ans_3)}
            ]

        result_index = self.print_answers(results)
        return result_index

    def print_answers(self, results):
        print ''
        small = min(results, key=lambda x: x["count"])
        large = max(results, key=lambda x: x["count"])

        result_index = 0
        for (i, r) in enumerate(results):
            text = "%s. %s - %s" % (i, r["ans"], r["count"])

            if r["ans"] == large["ans"]:
                print Colors.green + text + Colors.end
                result_index = i
            elif r["ans"] == small["ans"]:
                print Colors.red + text + Colors.end
            else:
                print text
        print ''
        return result_index
