# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The exceptions.

Authors: Snakecon (snakecon@gmail.com)
"""

__author__ = 'snakecon@gmail.com'


class PipelineException(BaseException):
    def __init__(self, message="Unknown message", payload=None):
        self.message = message
        self.payload = payload
