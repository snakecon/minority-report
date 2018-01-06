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
import argparse
from time import sleep

from precogs import pipelines
import uniout

__author__ = 'snakecon@gmail.com'


def main():
    parser = argparse.ArgumentParser()
    parser.register("type", "bool", lambda v: v.lower() == "true")

    parser.add_argument("--debug", type="bool", default=False,
                        help="Whether to enable debug mode.")
    parser.add_argument("--touch", type="bool", default=True,
                        help="Whether to touch screen.")
    parser.add_argument("--once", type="bool", default=False,
                        help="Whether to touch screen.")
    parser.add_argument("--precog", type=str, default="Dash",
                        help="Agatha | Arthur | Dash for different precogs(SearchEngine for now.).")

    flags, unparsed = parser.parse_known_args()

    print flags

    pipeline = pipelines.Pipeline(flags)
    while True:
        pipeline.run()
        if flags.once:
            break
        sleep(0.2)


if __name__ == '__main__':
    main()
    print uniout.__version__
