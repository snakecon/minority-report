# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The ocr module, used for convert image into text.

Authors: Snakecon (snakecon@gmail.com)
"""
import io

import re
from PIL import Image
from aip import AipOcr

from precogs import conf
from precogs.exceptions import PipelineException
from precogs.scenes import Scene
from precogs.scenes import HistSceneRecognizer


__author__ = 'snakecon@gmail.com'


class BaiduClondOcr(object):

    def __init__(self, flags):
        self.flags = flags
        self.recognizer = HistSceneRecognizer(flags)

    def ocr(self, file_name):
        print "Running OCR..."
        im = Image.open(file_name)
        img_bytes = io.BytesIO()

        corp_img = im.crop(conf.BBOX)

        corp_img.save(self.flags.precog + '_corp.png')
        corp_img.save(img_bytes, format='PNG')

        scene = self.recognizer.recogize(corp_img)
        if scene == Scene.OTHER:
            raise PipelineException('Other scene')

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

        question = re.sub(r'^\d\.', "", question)

        question_block = {
            "question": question,
            "ans_1": ans_1.replace('a.', ''),
            "ans_2": ans_2.replace('b.', ''),
            "ans_3": ans_3.replace('c.', ''),
        }

        if len(lines) > 3:
            raise PipelineException('Invalid ocr', question_block)

        self.print_questions(question_block)
        return question_block

    def print_questions(self, question_block):
        print ''
        print "Q: ", question_block["question"]
        print "1: ", question_block["ans_1"]
        print "2: ", question_block["ans_2"]
        print "3: ", question_block["ans_3"]
        print ''
