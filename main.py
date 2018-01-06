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
from precogs import pipelines

__author__ = 'snakecon@gmail.com'


if __name__ == '__main__':
    pipeline = pipelines.Pipeline(False)
    pipeline.run()
