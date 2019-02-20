import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import time
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Load the data
def loadData():
    with np.load("notMNIST.npz") as data:
        Data, Target = data["images"], data["labels"]
        np.random.seed(521)
        randIndx = np.arange(len(Data))
        np.random.shuffle(randIndx)
        Data = Data[randIndx] / 255.0
        Target = Target[randIndx]
        trainData, trainTarget = Data[:10000], Target[:10000]
        validData, validTarget = Data[10000:16000], Target[10000:16000]
        testData, testTarget = Data[16000:], Target[16000:]
    return trainData, validData, testData, trainTarget, validTarget, testTarget

# Implementation of a neural network using only Numpy - trained using gradient descent with momentum
def convertOneHot(trainTarget, validTarget, testTarget):
    newtrain = np.zeros((trainTarget.shape[0], 10))
    newvalid = np.zeros((validTarget.shape[0], 10))
    newtest = np.zeros((testTarget.shape[0], 10))

    for item in range(0, trainTarget.shape[0]):
        newtrain[item][trainTarget[item]] = 1
    for item in range(0, validTarget.shape[0]):
        newvalid[item][validTarget[item]] = 1
    for item in range(0, testTarget.shape[0]):
        newtest[item][testTarget[item]] = 1
    return newtrain, newvalid, newtest


def shuffle(trainData, trainTarget):
    np.random.seed(421)
    randIndx = np.arange(len(trainData))
    target = trainTarget
    np.random.shuffle(randIndx)
    data, target = trainData[randIndx], target[randIndx]
    return data, target


def relu(x):
    relu_x = np.maximum(x, 0)
    return relu_x

def softmax(x):
    softmax_x = np.exp(x)/sum(np.exp(x))
    return softmax_x

def computeLayer(X, W, b):
    compute_layer = np.matmul(X_trans, W) + b
    return compute_layer

def CE(target, prediction):
    ce = -np.mean(np.matmul(target, np.log(prediction)))
    return ce 

def gradCE(target, prediction):
    softmax_ce = prediction - target
    return softmax_ce

def back_out_weight(target, prediction, hidden_out):
    softmax_ce = gradCE(target, prediction)
    hidden_out_transpose = np.transpose(hidden_out)
    grad_out_weight = np.matmul(hidden_out_transpose, softmax_ce)
    return grad_out_weight

def back_out_bias(target, prediction):
    softmax_ce = gradCE(target, prediction)
    ones = np.ones(1, shape(target)[0])
    grad_out_bias = np.matmul(ones, softmax_ce)
    return grad_out_bias

def back_hidden_weight(target, prediction, input, input_out, out_weight):
    input_out[input_out > 0] = 1
    input_out[input_out < 0] = 0
    softmax_ce = gradCE(target, prediction)
    print(np.shape(out_weight))
    grad_hidden_weight = np.matmul(np.transpose(input), \
     (input_out * np.matmul(softmax_ce, np.transpose(out_weight))))
    return grad_hidden_weight

def back_hidden_bias(target, prediction, input_out, out_weight):
    input_out[input_out > 0] = 1
    input_out[input_out < 0] = 0
    ones = np.ones(1, shape(input_out)[0])
    softmax_ce = gradCE(target, prediction)
    grad_hidden_bias = np.matmul(np.transpose(ones), \
     (input_out * np.matmul(softmax_ce, np.transpose(out_weight))))
    return grad_hidden_bias


def learning(trainData, target, W_o, v_o, W_h, v_h, epochs, \
        gamma, learning_rate, bias_o, bias_h):

    for i in range(epochs):
        hidden_out = relu(np.matmul(trainData, W_h))
        print(np.shape(hidden_out))
        prediction = softmax(np.matmul(hidden_out, W_o))
        v_o = gamma*v_o + learning_rate*back_out_weight(target, prediction, hidden_out)
        W_o = W_o - v_o

        v_h = gamma*v_h + learning_rate*back_hidden_weight(target, \
            prediction, trainData, hidden_out, W_o)
        W_h = W_h - v_h


if __name__ == '__main__':
    trainData, validData, testData, trainTarget, validTarget, testTarget = loadData()
    trainData = trainData.reshape((trainData.shape[0], trainData.shape[1]*trainData.shape[2]))
    validData = validData.reshape((-1,validData.shape[1]*validData.shape[2])) 
    testData = testData.reshape((-1,testData.shape[1]*testData.shape[2]))

    hidden_units = 1000
    epochs = 200
    gamma = 0.99
    learning_rate = 0.01


    newtrain, newvalid, newtest = convertOneHot(trainTarget, validTarget, testTarget)
    mu = 0 # mean and standard deviation
    stddev_o = 1.0/(hidden_units+10)
    W_o = np.random.normal(mu, stddev_o, (hidden_units,10))
    v_o = np.full((hidden_units,10), 1e-5)

    stddev_h = 1.0/(trainData.shape[1]+hidden_units)
    W_h = np.random.normal(mu, stddev_h, (trainData.shape[1],hidden_units))
    v_h = np.full((trainData.shape[1],hidden_units), 1e-5)

    bias_o = np.zeros((1, 10))
    bias_h = np.zeros((1, hidden_units))

    weight_o, bias_o, weight_h, bias_h = learning(trainData, newtrain, W_o, v_o, W_h, v_h, epochs, \
        gamma, learning_rate, bias_o, bias_h)