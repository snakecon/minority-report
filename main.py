# coding=utf-8
import os
import urllib
from subprocess import call

import requests
from aip import AipOcr
from bs4 import BeautifulSoup

# Config.
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
PROXYS = {}
SCREEN_BBOX = ""


def main():
    filename = "q.png"

    screenshot(filename)
    question_block = ocr(filename)
    print_questions(question_block)
    results = rank_answers(question_block)
    print_answers(results)


def screenshot(img_name):
    print "grabbing screenshot..."
    call(["screencapture", "-R", SCREEN_BBOX, img_name])
    call(["sips", "-Z", "350", img_name])


def ocr(img_name):
    print "running OCR..."
    file_name = os.path.join(os.path.dirname(__file__), img_name)

    image = _get_file_content(file_name)

    options = {"probability": "true"}

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    result = client.basicGeneral(image, options)

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
    print "rankings answers..."

    question = question_block["question"]
    ans_1 = question_block["ans_1"]
    ans_2 = question_block["ans_2"]
    ans_3 = question_block["ans_3"]

    reverse = True

    if "不是" in question.lower():
        print "reversing results..."
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
        print "running tiebreaker..."

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

    for (i, r) in enumerate(results):
        text = "%s. %s - %s" % (i, r["ans"], r["count"])

        if r["ans"] == large["ans"]:
            print Colors.green + text + Colors.end
        elif r["ans"] == small["ans"]:
            print Colors.red + text + Colors.end
        else:
            print text
    print ''


class Colors:
    blue = '\033[94m'
    red = "\033[1;31m"
    green = '\033[0;32m'
    end = '\033[0m'
    bold = '\033[1m'


def _get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


def _google(q_list, num):
    params = {"q": " ".join(q_list), "num": num}
    url_params = urllib.urlencode(params)

    google_url = "https://www.google.com.hk/search?" + url_params

    r = requests.get(google_url, proxies=PROXYS)

    soup = BeautifulSoup(r.text, "html.parser")
    spans = soup.find_all('span', {'class': 'st'})

    text = u" ".join([span.get_text() for span in spans]).lower().encode('utf-8').strip()

    return text


if __name__ == "__main__":
    main()
