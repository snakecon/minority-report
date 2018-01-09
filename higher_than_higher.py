#!/bin/env python
# -*- coding:utf-8 -*-

"""
The WeChat Server.

Authors: Alex Lu (flyland_lf@hotmail.com)
"""

from flask import Flask, request, abort, render_template
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)
from wechatpy.crypto import WeChatCrypto

import sys
import os
import logging
import urllib
import tempfile
import json
import argparse
import re

import cv2
import numpy as np
from aip import AipOcr
from zhon import hanzi

from precogs import algorithms
            
__author__ = u'lufei@baidu.com'

WECHAT_TOKEN = os.getenv('WECHAT_TOKEN', 'wechat_token')
WECHAT_AES_KEY = os.getenv('WECHAT_AES_KEY', '')
WECHAT_APPID = os.getenv('WECHAT_APPID', '')

OCR_APPID = os.getenv('OCR_APPID', '10637074')
OCR_API_KEY = os.getenv('OCR_API_KEY', '6sTsfi71CdGQG5l82cYREQyF')
OCR_SECRET_KEY = os.getenv('OCR_SECRET_KEY', '4kTQR54X1FtwcwNd7s1eHHTBhyZ5hyML')

app = Flask(__name__)

FLAGS = None
RANKER = None

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    try:
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        encrypt_type = request.args.get('encrypt_type', 'raw')
        msg_signature = request.args.get('msg_signature', '')
        try:
            check_signature(WECHAT_TOKEN, signature, timestamp, nonce)
        except InvalidSignatureException:
            abort(403)
        if request.method == 'GET':
            echo_str = request.args.get('echostr', '')
            return echo_str
        
        # POST
        if encrypt_type != 'raw':
            crypto = WeChatCrypto(WECHAT_TOKEN, WECHAT_AES_KEY, WECHAT_APPID)
            try:
                msg = crypto.decrypt_message(
                    request.data,
                    msg_signature,
                    timestamp,
                    nonce
                )
            except (InvalidSignatureException, InvalidAppIdException):
                abort(403)
        else:
            msg = request.data
            
        # BIZ
        msg = parse_message(msg)
        if msg.type == 'image':
            problem = process_image(msg.image)
            
            result_arthur, reverse = RANKER.do_rank_answers(problem)
            
            message = ' | '.join(['%d-%s' % (r['count'], r['ans']) for r in result_arthur])
            logging.info(message)
            reply = create_reply(message, msg)
        else:
            reply = create_reply('Sorry, can not handle this for now', msg)
        

        # Render
        if encrypt_type != 'raw':
            return crypto.encrypt_message(reply.render(), nonce, timestamp)
        else:
            return reply.render()
    
    except Exception as e:
        import traceback
        traceback.print_exc()

    
def process_image(image_url):
    logging.info("image_url:%s" % (image_url))
    
    img = cv2.imdecode(np.asarray(bytearray(urllib.urlopen(image_url).read()), dtype='uint8'), cv2.IMREAD_GRAYSCALE)
    ret, img =cv2.threshold(img, 215, 255, cv2.THRESH_BINARY)
    
#    with open('temp.jpg', 'w') as t:
#        t.write(cv2.imencode('.jpg', img)[1].tostring())
    
    ocr_client = AipOcr(OCR_APPID, OCR_API_KEY, OCR_SECRET_KEY)
    result = ocr_client.general(cv2.imencode('.jpg', img)[1].tostring(), { 'probability': 'true' })
    
#    print >> sys.stderr, json.dumps(result, encoding='utf-8', ensure_ascii=False)
    
    words_result = filter(lambda x: x['location']['top'] > 300 and x['location']['top'] < 1400, result['words_result'])
#    print >> sys.stderr, json.dumps(words_result, encoding='utf-8', ensure_ascii=False)

    question = ''.join([word['words'] for word in words_result[:-3]]).split('.')[-1]
    answers = [word['words'].split('.')[-1] for word in words_result[-3:]]
    
    problem = {
        'question': question.encode('utf-8'),
        'ans_1': re.sub(ur"[%s]" % hanzi.punctuation, "", answers[0]).encode('utf-8'),
        'ans_2': re.sub(ur"[%s]" % hanzi.punctuation, "", answers[1]).encode('utf-8'),
        'ans_3': re.sub(ur"[%s]" % hanzi.punctuation, "", answers[2]).encode('utf-8')
    }
    
#    print >> sys.stderr, json.dumps(problem, encoding='utf-8', ensure_ascii=False)
    
    return problem    
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,  
                        format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                        datefmt='%a, %d %b %Y %H:%M:%S')
    parser = argparse.ArgumentParser()
    parser.register("type", "bool", lambda v: v.lower() == "true")
    parser.add_argument("--precog", type=str, default="Baidu",
                        help="Agatha | Arthur | Dash for different precogs(SearchEngine for now.).")
    parser.add_argument("--debug", type="bool", default=False,
                        help="Whether to enable debug mode.")
    FLAGS, unparsed = parser.parse_known_args()

    RANKER = algorithms.BasicRanker(FLAGS)
    app.run(host="0.0.0.0", port=80, debug=True)


