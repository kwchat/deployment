import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
from config import FLAGS
from model import Model
from socket import *

model = Model(FLAGS.epoch, FLAGS.max_length, FLAGS.num_classes, FLAGS.hidden_size, FLAGS.learning_rate)

def main():
        serverSock = socket(AF_INET, SOCK_STREAM)
        serverSock.bind(('', 5001))
        serverSock.listen(1)
        print('Listening')

        connectionSock, addr = serverSock.accept()
        print('연결 수립')

        while True:
                msg = connectionSock.recv(1024)
                msg = msg.decode('utf-8')
                print('받은 데이터 :', msg)
                res = model.predict(msg)
                connectionSock.send(res.encode('utf-8'))
                print('메시지를 보냈습니다.')


if __name__ == "__main__":
    main()