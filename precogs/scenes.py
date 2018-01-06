# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The scenes module, used for answer questions. Precogs named by the three psychics.

Authors: Snakecon (snakecon@gmail.com)
"""
from PIL import Image

__author__ = 'snakecon@gmail.com'


class Scene(object):
    PUZZLE = 0
    OTHER = 1


class HistSceneRecognizer(object):
    def __init__(self, debug):
        self.debug = debug
        self.target_img = Image.open('data/target.png')
        self.target_hist = self.target_img.histogram()
        self.threshold = 0.6

    def recogize(self, dst_img):
        if self.debug:
            print dst_img.histogram()
            print self.target_hist

        similar = self._hist_similar(dst_img.histogram(), self.target_hist)
        print "Scene similar: %f" % similar

        if similar > self.threshold:
            return Scene.PUZZLE
        else:
            return Scene.OTHER

    def _hist_similar(self, lh, rh):
        assert len(lh) == len(rh)
        sum_value = sum(1 - (0 if l == r else float(abs(l - r))/max(l, r)) for l, r in zip(lh, rh))
        return sum_value/len(lh)
