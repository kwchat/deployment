from config import FLAGS
from model import Model
from flask import Flask, request

def main():
        model = Model(FLAGS.epoch, FLAGS.max_length, FLAGS.num_classes, FLAGS.hidden_size, FLAGS.learning_rate)
        app = Flask(__name__)

        @app.route('/')
        def home():
                msg = request.args.get('msg')
                res = model.predict(msg)
                return res
        @app.route('/train')
        def train():
                model.train()
                return ''
        app.run(port=5001)



if __name__ == "__main__":
    main()