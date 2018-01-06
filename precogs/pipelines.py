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
from precogs.exceptions import PipelineException
from precogs.ocrs import BaiduClondOcr
from precogs.scenes import HistSceneRecognizer

__author__ = 'snakecon@gmail.com'


class Pipeline(object):

    def __init__(self, flags):
        self.flags = flags
        self.ranker = BasicRanker(flags)
        self.driver = AndroidDriver(flags)
        self.ocr = BaiduClondOcr(flags)
        self.recognizer = HistSceneRecognizer(flags)

    def run(self):
        try:
            filename = self.flags.precog + '.png'
            self.driver.screenshot(filename)

            questions = self.ocr.ocr(filename)

            result_index = self.ranker.rank_answers(questions)

            if self.flags.touch:
                self.driver.touch_button(result_index)
        except PipelineException as e:
            print e.message
            if e.payload is not None:
                print e.payload
