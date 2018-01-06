# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The entry point.

Authors: Snakecon (snakecon@gmail.com)
"""
import io
import urllib
from subprocess import call

import requests
from PIL import Image
from aip import AipOcr
from bs4 import BeautifulSoup

import conf_air as conf

__author__ = 'snakecon@gmail.com'


def main():
    filename = "q.png"

    screenshot(filename)
    question_block = ocr(filename)
    print_questions(question_block)
    results = rank_answers(question_block)
    index = print_answers(results)
    touch_button(index)


def screenshot(file_name):
    print "Grabbing screenshot..."
    call(["screencapture", "-l", str(conf.WINDOW_ID), "-o", file_name])


def ocr(file_name):
    print "Running OCR..."
    im = Image.open(file_name)
    img_bytes = io.BytesIO()

    corp_img = im.crop(conf.BBOX)

    corp_img.save('debug.png')
    corp_img.save(img_bytes, format='PNG')

    client = AipOcr(conf.APP_ID, conf.API_KEY, conf.SECRET_KEY)
    result = client.basicGeneral(img_bytes.getvalue(), {"probability": "true"})

    lines = result['words_result']

    ans_1 = lines[-3]['words'].lower().encode('utf-8')
    ans_2 = lines[-2]['words'].lower().encode('utf-8')
    ans_3 = lines[-1]['words'].lower().encode('utf-8')

    del lines[-1]
    del lines[-1]
    del lines[-1]

    question = u" ".join([line['words'].strip() for line in lines]).encode('utf-8')
    return {
        "question": question,
        "ans_1": ans_1.replace('a.', ''),
        "ans_2": ans_2.replace('b.', ''),
        "ans_3": ans_3.replace('c.', ''),
    }


def print_questions(question_block):
    print ''
    print "Q: ", question_block["question"]
    print "1: ", question_block["ans_1"]
    print "2: ", question_block["ans_2"]
    print "3: ", question_block["ans_3"]
    print ''


def rank_answers(question_block):
    print "Rankings answers..."

    question = question_block["question"]
    ans_1 = question_block["ans_1"]
    ans_2 = question_block["ans_2"]
    ans_3 = question_block["ans_3"]

    reverse = True

    if "不是" in question.lower() or "不可能" in question.lower():
        print "Reversing results..."
        reverse = False

    text = _google([question], 50)

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

        text = _google([question, ans_1, ans_2, ans_3], 50)

        results = [
            {"ans": ans_1, "count": text.count(ans_1)},
            {"ans": ans_2, "count": text.count(ans_2)},
            {"ans": ans_3, "count": text.count(ans_3)}
        ]

    return results


def print_answers(results):
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


def touch_button(result_index):
    print ''
    ans_position = conf.ANS_POSITION[result_index]
    print "Touch button index:%s, position: %s " % (result_index, str(ans_position))
    call(["adb", "shell", "input", "tap", str(ans_position[0]), str(ans_position[1])])
    print ''


class Colors:
    blue = '\033[94m'
    red = "\033[1;31m"
    green = '\033[0;32m'
    end = '\033[0m'
    bold = '\033[1m'


def _google(q_list, num):
    params = {"q": " ".join(q_list), "num": num}
    url_params = urllib.urlencode(params)

    google_url = "https://www.google.com.hk/search?" + url_params

    r = requests.get(google_url, proxies=conf.PROXYS)

    soup = BeautifulSoup(r.text, "html.parser")
    spans = soup.find_all('span', {'class': 'st'})

    text = u" ".join([span.get_text() for span in spans]).lower().encode('utf-8').strip()

    return text


if __name__ == "__main__":
    main()
