# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The pipelines.

Authors: Snakecon (snakecon@gmail.com)
"""

from precogs.algorithms import BasicRanker
from precogs.drivers import AndroidDriver
from precogs.ocrs import BaiduClondOcr
from precogs.scenes import Scene
from precogs.scenes import SceneRecognizer

__author__ = 'snakecon@gmail.com'


class Pipeline(object):

    def __init__(self, debug=False):
        self.debug = debug
        self.ranker = BasicRanker(debug)
        self.driver = AndroidDriver(debug)
        self.ocr = BaiduClondOcr(debug)
        self.recognizer = SceneRecognizer(debug)

    def run(self):
        filename = 'q.png'
        self.driver.screenshot(filename)

        scene = self.recognizer.recogize(filename)
        if scene == Scene.OTHER:
            return

        questions = self.ocr.ocr(filename)

        result_index = self.ranker.rank_answers(questions)

        self.driver.touch_button(result_index)
