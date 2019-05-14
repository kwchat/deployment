import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import tensorflow as tf
import numpy as np
import math
import sys

from config import FLAGS
from model import Seq2Seq
from dialog import Dialog
from flask import Flask, request
import sys
from googletrans import Translator
from socket import *
from langdetect import detect
    

class ChatBot:

    def __init__(self, voc_path, train_dir):
        self.ciSock = socket(AF_INET, SOCK_STREAM)
        self.ciSock.connect(('127.0.0.1', 5001))
        self.drqaSock = socket(AF_INET, SOCK_STREAM)
        self.drqaSock.connect(('127.0.0.1', 5002))
        print('연결 수립')
        self.dialog = Dialog()
        self.dialog.load_vocab(voc_path)

        self.model = Seq2Seq(self.dialog.vocab_size)

        self.sess = tf.Session()
        ckpt = tf.train.get_checkpoint_state(train_dir)
        self.model.saver.restore(self.sess, ckpt.model_checkpoint_path)
    
    def predict_intent(self, msg):
        self.ciSock.send(msg.encode('utf-8'))
        res = self.ciSock.recv(1024)
        res = res.decode('utf-8')
        return res
    
    def predict_drqa(self, msg):
        self.drqaSock.send(msg.encode('utf-8'))
        res = self.drqaSock.recv(1024)
        res = res.decode('utf-8')
        return res

    def run(self):
        sys.stdout.write("> ")
        sys.stdout.flush()
        line = sys.stdin.readline()

        while line:
            print(self._get_replay(line.strip()))

            sys.stdout.write("\n> ")
            sys.stdout.flush()

            line = sys.stdin.readline()
    
    def run_server(self):
        app = Flask(__name__)

        @app.route('/')
        def home():
            message = request.args.get('message')
            res = self._get_replay(message)
            return res
            
        app.run()

    def _decode(self, enc_input, dec_input):
        if type(dec_input) is np.ndarray:
            dec_input = dec_input.tolist()

        # TODO: 구글처럼 시퀀스 사이즈에 따라 적당한 버킷을 사용하도록 만들어서 사용하도록
        input_len = int(math.ceil((len(enc_input) + 1) * 1.5))

        enc_input, dec_input, _ = self.dialog.transform(enc_input, dec_input,
                                                        input_len,
                                                        FLAGS.max_decode_len)

        return self.model.predict(self.sess, [enc_input], [dec_input])

    def _get_replay(self, msg):
        lang = detect(msg)
        translator = Translator()
        if lang != "ko":
            res = translator.translate(msg, dest='ko')
            msg = res.text
        chitclass = self.predict_intent(msg)
        if chitclass == 'what':
            res = translator.translate(msg, dest='en')
            msg = res.text
            reply = self.predict_drqa(msg)
            res = translator.translate(reply, dest=lang)
            reply = res.text
        else:
            enc_input = self.dialog.tokenizer(msg)
            enc_input = self.dialog.tokens_to_ids(enc_input)
            dec_input = []

            # TODO: 구글처럼 Seq2Seq2 모델 안의 RNN 셀을 생성하는 부분에 넣을것
            #       입력값에 따라 디코더셀의 상태를 순차적으로 구성하도록 함
            #       여기서는 최종 출력값을 사용하여 점진적으로 시퀀스를 만드는 방식을 사용
            #       다만 상황에 따라서는 이런 방식이 더 유연할 수도 있을 듯
            curr_seq = 0
            for i in range(FLAGS.max_decode_len):
                outputs = self._decode(enc_input, dec_input)
                if self.dialog.is_eos(outputs[0][curr_seq]):
                    break
                elif self.dialog.is_defined(outputs[0][curr_seq]) is not True:
                    dec_input.append(outputs[0][curr_seq])
                    curr_seq += 1

            reply = self.dialog.decode([dec_input], True)

        if lang != 'ko':
            res = translator.translate(reply, dest=lang)
            reply = res.text
        
        return reply


def main(_):
    print("깨어나는 중 입니다. 잠시만 기다려주세요...\n")
    chatbot = ChatBot(FLAGS.voc_path, FLAGS.train_dir)
    if len(sys.argv) == 1:
        chatbot.run()
    elif sys.argv[1] == 'server':
        chatbot.run_server()


if __name__ == "__main__":
    tf.app.run()
