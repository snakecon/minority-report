# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The driver module, used for get phone image and send command.

Authors: Snakecon (snakecon@gmail.com)
"""
from subprocess import call

from precogs import conf

__author__ = 'snakecon@gmail.com'


class AndroidDriver(object):
    def __init__(self, debug):
        self.debug = debug

    def screenshot(self, file_name):
        print "Grabbing screenshot..."
        if self.debug:
            print(' '.join(["screencapture", "-l", str(conf.WINDOW_ID), "-o", file_name]))
        call(["screencapture", "-l", str(conf.WINDOW_ID), "-o", file_name])

    def touch_button(self, result_index):
        print ''
        ans_position = conf.ANS_POSITION[result_index]
        print "Touch button index:%s, position: %s " % (result_index, str(ans_position))
        call(["adb", "shell", "input", "tap", str(ans_position[0]), str(ans_position[1])])
        print ''
