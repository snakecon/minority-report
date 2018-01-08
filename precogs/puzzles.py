# coding=utf-8
#########################################################
#
# Copyright 2018 The minority-report Authors. All Rights Reserved
#
#########################################################
"""
The puzzles script, fetch/load/save history puzzle.

Authors: Snakecon (snakecon@gmail.com)
"""
import json

__author__ = 'snakecon@gmail.com'


class Puzzle(object):

    def __init__(self, flags):
        self.flags = flags
        self.filename = "data/puzzles.json"
        self.puzzles = []
        self.questions = set()
        self.loads()

    def loads(self):
        with open(self.filename, 'r') as puzzle_file:
            self.puzzles = json.loads(puzzle_file.read())
            for puzzle in self.puzzles:
                self.questions.add(puzzle[u'question'])

    def save(self, puzzle):
        serial_puzzle = {}
        for item in ['question', 'ans_1', 'ans_2', 'ans_3']:
            serial_puzzle[item.decode('utf-8')] = puzzle[item].decode('utf-8')

        if serial_puzzle[u'question'] in self.questions:
            return

        self.puzzles.append(serial_puzzle)
        with open(self.filename, 'w') as puzzle_file:
            puzzle_file.write(json.dumps(self.puzzles, indent=4, sort_keys=True, ensure_ascii=False).encode('utf-8'))
