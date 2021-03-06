import tensorflow as tf
import numpy as np
import time
import datetime
import os
import network
import json
from sklearn.metrics import average_precision_score
import sys
from framework import Framework

FLAGS = tf.app.flags.FLAGS
tf.app.flags.DEFINE_string('export_path','./data','path to data')

# config file
config_file = open(os.path.join(FLAGS.export_path, "config"), 'r')
config = json.loads(config_file.read())
config_file.close()

tf.app.flags.DEFINE_integer('max_length', config['fixlen'], 'maximum of number of words in one sentence')
tf.app.flags.DEFINE_integer('pos_num', config['maxlen'] * 2 + 1, 'number of position embedding vectors')
tf.app.flags.DEFINE_integer('num_classes', len(config['relation2id']),'maximum of relations')

tf.app.flags.DEFINE_integer('hidden_size',230,'hidden feature size')
tf.app.flags.DEFINE_integer('pos_size',5,'position embedding size')
tf.app.flags.DEFINE_integer('word_size', 50, 'word embedding size')

tf.app.flags.DEFINE_integer('max_epoch',60,'maximum of training epochs')
tf.app.flags.DEFINE_integer('batch_size',160,'entity numbers used each training time')
tf.app.flags.DEFINE_integer('test_batch_size', 160, 'batch size during testing')

tf.app.flags.DEFINE_float('learning_rate',0.5,'entity numbers used each training time')
tf.app.flags.DEFINE_float('weight_decay',0.00001,'weight_decay')
tf.app.flags.DEFINE_float('keep_prob',0.7,'dropout rate')

tf.app.flags.DEFINE_string('checkpoint_dir','./checkpoint/','path to store model')
tf.app.flags.DEFINE_string('summary_dir','./summary','path to store summary_dir')
tf.app.flags.DEFINE_string('test_result_dir', './test_result', 'path to store the test results')
tf.app.flags.DEFINE_boolean('use_adv', False, 'use adversarial training or not')
tf.app.flags.DEFINE_integer('save_epoch', 2, 'save the checkpoint after how many epoches')
tf.app.flags.DEFINE_integer('test_epoch', 9, 'epoch to be tested')

tf.app.flags.DEFINE_boolean('is_train', True, 'training or testing')

def main(_):
    framework = Framework(is_training=FLAGS.is_train)

    word_embedding = framework.embedding.word_embedding()
    pos_embedding = framework.embedding.pos_embedding()
    embedding = framework.embedding.concat_embedding(word_embedding, pos_embedding)
    x = framework.encoder.pcnn(embedding, activation=tf.nn.relu)
    x = framework.selector.attention(x)
    output = framework.classifier.output(x)
    
    if FLAGS.is_train:
        loss = framework.classifier.softmax_cross_entropy(x)
        framework.init_train_model(loss, output, optimizer=tf.train.GradientDescentOptimizer)
        framework.load_train_data()
        framework.train()
        
    else:
        framework.init_test_model(x, output)
        framework.load_test_data()
        framework.test([FLAGS.test_epoch])


if __name__ == "__main__":
    tf.app.run() 
