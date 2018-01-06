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

__author__ = 'snakecon@gmail.com'


class Scene(object):
    PUZZLE = 0
    OTHER = 1


class SceneRecognizer(object):
    def __init__(self, debug):
        self.debug = debug

    def recogize(self, filname):
        return Scene.PUZZLE
