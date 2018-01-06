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
from time import sleep

from precogs import pipelines
import uniout

__author__ = 'snakecon@gmail.com'


if __name__ == '__main__':
    pipeline = pipelines.Pipeline(False)
    while True:
        pipeline.run()
        sleep(0.2)
