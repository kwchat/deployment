import tensorflow as tf

tf.app.flags.DEFINE_string("train_dir", "./", "학습한 신경망을 저장할 폴더")
tf.app.flags.DEFINE_string("log_dir", "./log", "로그를 저장할 폴더")

tf.app.flags.DEFINE_integer("epoch", 20000, "총 학습 반복 횟수")
tf.app.flags.DEFINE_integer("max_length", 100, "최대 입력 문장 길이")
tf.app.flags.DEFINE_integer("num_classes", 2, "class depth")
tf.app.flags.DEFINE_integer("hidden_size", 100, "히든 사이즈")
tf.app.flags.DEFINE_float("learning_rate", 0.01, "learning rate")

FLAGS = tf.app.flags.FLAGS