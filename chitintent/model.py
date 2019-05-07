from konlpy.tag import Mecab
import tensorflow as tf
import os

f1 = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'voc.text'), 'r')

vocs = f1.readlines()
vocs = [voc.strip('\n') for voc in vocs]
word_dict = {k:v for v,k in enumerate(vocs)}

def word2vec(sentence, max_length):
    mecab = Mecab()
    josas = ['JKS', 'JKC', 'JKG', 'JKO', 'JKB', 'JKV', 'JKQ', 'JX', 'JC']
    sentence = sentence.strip('.,?!')
    pos = mecab.pos(sentence)
    token = []
    vec = []
    for i in range(max_length):
        if i < len(pos):
            tk, tag = pos[i]
            
            if tag in josas:
                token.append('<J>')
            elif tk in vocs:
                token.append(tk)
            else:
                token.append('<UNK>')
        else:
            token.append('<P>')

    for tk in token:
        vec.append(word_dict[tk])

    return vec

def one_hot(num, depth):
    res = []
    for i in range(depth):
        if(num == i):
            res.append(1)
        else:
            res.append(0)
    return res


class Model():
    hypothesis = None
    cost = None
    optimizer = None

    def __init__(self, epoch, max_length, num_classes, hidden_size, learning_rate):
        self.model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'conversation')
        self.epoch = epoch
        self.max_length = max_length
        self.num_classes = num_classes
        #build model
        self.X = tf.placeholder(tf.float32, [None, max_length])
        self.Y = tf.placeholder(tf.float32, [None, num_classes])

        W1 = tf.Variable(tf.random_normal([max_length, hidden_size]), name='weight1')
        b1 = tf.Variable(tf.random_normal([hidden_size]), name='bias1')
        L1 = tf.sigmoid(tf.matmul(self.X, W1) + b1)

        W2 = tf.Variable(tf.random_normal([hidden_size, hidden_size]), name='weight2')
        b2 = tf.Variable(tf.random_normal([hidden_size]), name='bias2')
        L2 = tf.sigmoid(tf.matmul(L1, W1) + b1)

        W3 = tf.Variable(tf.random_normal([hidden_size, num_classes]), name='weight3')
        b3 = tf.Variable(tf.random_normal([num_classes]), name='bias3')
        self.hypothesis = tf.nn.softmax(tf.matmul(L2, W3) + b3)

        self.cost = tf.reduce_mean(-tf.reduce_sum(self.Y * tf.log(self.hypothesis), axis=1))
        self.optimizer = tf.train.GradientDescentOptimizer(learning_rate).minimize(self.cost)
        self.saver = tf.train.Saver()

    def train(self):
        f2 = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'train.text'), 'r')
        lines = f2.readlines()
        lines = [line.strip('\n') for line in lines]
        lines = [line.split('++$++') for line in lines]
        x_data = [line[0] for line in lines]
        x_data = [word2vec(sentence, self.max_length) for sentence in x_data]
        y_data = [int(line[1]) for line in lines]
        y_data = [one_hot(num, self.num_classes) for num in y_data]

        with tf.Session() as sess:
            sess.run(tf.global_variables_initializer())

            for step in range(self.epoch):
                _, cost_val = sess.run([self.optimizer, self.cost], feed_dict={self.X: x_data, self.Y: y_data})

                if step % 200 == 0:
                    print(step, cost_val)
            self.saver.save(sess, self.model_path)
    
    def predict(self, sentence):
        intent_class = ['others', 'what', 'realtime']
        with tf.Session() as sess:
            self.saver.restore(sess, self.model_path)
            a = sess.run(self.hypothesis, feed_dict={self.X: [word2vec(sentence, self.max_length)]})
            pred = sess.run(tf.argmax(a, 1)).tolist()
            return intent_class[pred[0]]