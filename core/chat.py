import tensorflow as tf
import argparse
import numpy as np
import math
import sys
import re
from flask import Flask, request
from papago import Translator
from socket import *
from langdetect import detect
import hgtk

# other module


from . import nmt
from . import attention_model
from . import gnmt_model
from . import model as nmt_model
from . import model_helper

from . import constants
from konlpy.tag import Mecab

from .utils import vocab_utils

from .utils import misc_utils as utils
from .utils import nmt_utils


FLAGS = constants

mecab = Mecab()

def remove_special_char(s_input):
    return re.sub("([.,!?\"':;)(])", "", s_input)


def apply_nlpy(s_input):
    """
    형태소 분석을 통해서 교육 효율을 높인다.
    """
    result = mecab.morphs(s_input)
    return ' '.join(result)
    

class ChatBot:
    ckpt = None
    hparams = None
    infer_model = None
    sess = None
    loaded_infer_model = None
    
    def __init__(self):
        self.connect_sock()
    
    def connect_sock(self):
        self.ciSock = socket(AF_INET, SOCK_STREAM)
        self.ciSock.connect(('127.0.0.1', 5001))
        self.drqaSock = socket(AF_INET, SOCK_STREAM)
        self.drqaSock.connect(('127.0.0.1', 5002))
        print('연결 수립')

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

    def _do_reply(self, input):
        lang = detect(input)
        translator = Translator(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'])
        
        if len(input) == 0:
            return ''

        if lang != "ko":
            res = translator.translate(input, source=lang, target='ko')
            input = res.text
        chitclass = self.predict_intent(input)
        if chitclass == 'what':
            res = translator.translate(input, source='ko', target='en')
            input = res.text
            reply = self.predict_drqa(input)
            res = translator.translate(reply, source='en', target='ko')
            reply = res.text
            if hgtk.checker.is_hangul(reply[-1]):
                if hgtk.checker.has_batchim(reply[-1]):
                    reply = reply + '이에요'
                else:
                    reply = reply + '에요'
        else:
            infer_data = [apply_nlpy(remove_special_char(input))]

            self.sess.run(
                self.infer_model.iterator.initializer,
                feed_dict={
                    self.infer_model.src_placeholder: infer_data,
                    self.infer_model.batch_size_placeholder: self.hparams.infer_batch_size})

            # variable check
                
            beam_width = self.hparams.beam_width
            num_translations_per_input = max(
                min(1, beam_width), 1)
                
            nmt_outputs, _ = self.loaded_infer_model.decode(self.sess)
            if beam_width == 0:
                nmt_outputs = np.expand_dims(nmt_outputs, 0)

            batch_size = nmt_outputs.shape[1]

            for sent_id in range(batch_size):
                for beam_id in range(num_translations_per_input):
                    translation = nmt_utils.get_translation(
                        nmt_outputs[beam_id],
                        sent_id,
                        tgt_eos=self.hparams.eos,
                        subword_option=self.hparams.subword_option)
            reply = translation.decode('utf-8')

        if lang != "ko":
            res = translator.translate(reply, source='ko', target=lang)
            reply = res.text
        return reply

    def nmt_main(self, flags, default_hparams, scope=None):
        ## Train / Decode
        out_dir = flags.out_dir

        if not tf.gfile.Exists(out_dir): tf.gfile.MakeDirs(out_dir)

        # Load hparams.
        self.hparams = nmt.create_or_load_hparams(
            out_dir, default_hparams, flags.hparams_path, save_hparams=False)

        self.ckpt = flags.ckpt
        if not self.ckpt:
            self.ckpt = tf.train.latest_checkpoint(out_dir)

        if not self.ckpt:
            print('Train is needed')
            sys.exit()

        hparams = self.hparams
        
        if not hparams.attention:
            model_creator = nmt_model.Model
        elif hparams.attention_architecture == "standard":
            model_creator = attention_model.AttentionModel
        elif hparams.attention_architecture in ["gnmt", "gnmt_v2"]:
            model_creator = gnmt_model.GNMTModel
        else:
            raise ValueError("Unknown model architecture")
        self.infer_model = model_helper.create_infer_model(model_creator, hparams, scope)

        # get tensorflow session

        self.sess = tf.Session(graph=self.infer_model.graph, config=utils.get_config_proto())

        with self.infer_model.graph.as_default():
            self.loaded_infer_model = model_helper.load_model(
                self.infer_model.model, self.ckpt, self.sess, 'infer')

    
    def run(self,flags, default_hparams):
        # load all parameters
        self.nmt_main(flags, default_hparams)
        try:
            sys.stdout.write("> ")
            sys.stdout.flush()
            line = sys.stdin.readline()

            while line:
                print(self._do_reply(line.strip()))

                sys.stdout.write("\n> ")
                sys.stdout.flush()

                line = sys.stdin.readline()

        except KeyboardInterrupt:
            self.sess.close()
            sys.exit()

    def run_server(self, flags, default_hparams):
        app = Flask(__name__)

        @app.route('/')
        def home():
            message = request.args.get('message')
            res = self._do_reply(message)
            return res

        self.nmt_main(flags, default_hparams)
        try:
            app.run()
        except KeyboardInterrupt:
            self.sess.close()
            sys.exit()

def create_hparams(flags):
    """Create training hparams."""


    return tf.contrib.training.HParams(
        out_dir=flags.out_dir,
        override_loaded_hparams=flags.override_loaded_hparams,
    )

def main(unused_argv):
    default_hparams = create_hparams(FLAGS)
    print('starting... \n')
    chatbot = ChatBot()
    if len(sys.argv) == 1:
        chatbot.run(FLAGS, default_hparams)
    elif sys.argv[1] == 'server':
        chatbot.run_server(FLAGS, default_hparams)

if __name__ == "__main__":
    tf.app.run(main=main, argv=[sys.argv[0]])
