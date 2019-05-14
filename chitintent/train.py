from config import FLAGS
from model import Model

model = Model(FLAGS.epoch, FLAGS.max_length, FLAGS.num_classes, FLAGS.hidden_size, FLAGS.learning_rate)

def main():
    model.train()


if __name__ == "__main__":
    main()