# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 19:00:57 2018

@author: HP
"""
from numpy import asarray
from numpy import zeros
import numpy as np
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential, Model
from keras.layers import Dense
from keras.layers import Flatten, LSTM ,Dropout,GRU, Bidirectional
from keras.layers import Embedding, Maximum, Merge, Input, concatenate
from collections import defaultdict
from nltk.corpus import brown,stopwords
from keras.layers import Conv1D, MaxPooling1D, Conv2D, MaxPooling2D
import random
import nltk
#brown.categories()
#brown.words(categories='news')
#brown.words(fileids=['cg22'])
#brown.sents(categories=['news', 'editorial', 'reviews'])

batch_size=30
embedding_size=128

# Convolution
kernel_size = 5
filters1 = 64
filters2 =128
filters3=256
filters4=512
filters5=1024
pool_size = 4

# GRU
gru_output_size = 70
#LSTM
lstm_output_size = 70

dataset = [] # 500 samples

for category in brown.categories():
 for fileid in brown.fileids(category):
  dataset.append((brown.words(fileids = fileid),category))

dataset = [([w.lower() for w in text],category) for text,category in dataset]

labels=[]
for sample in dataset:
 labels.append(sample[1])

inputset=[]
for sample in dataset:
 inputset.append(' '.join(sample[0]))

categ=brown.categories()

label_class=[]
for x in labels:
 label_class.append(categ.index(x))

len_finder=[]
for dat in inputset:
 len_finder.append(len(dat))

input_train=[]
j=0;
for zz in inputset:
    j=j+1
    if (j%4 is not 0):
        input_train.append(zz)


input_test=[]
j=0;
for zz in inputset:
    j=j+1
    if (j%4 is 0):
        input_test.append(zz)

label_train=[]
j=0;
for zz in label_class:
    j=j+1
    if (j%4 is not 0):
        label_train.append(zz)

label_test=[]
j=0;
for zz in label_class:
    j=j+1
    if (j%4 is 0):
        label_test.append(zz)


#one hot encoding
i=0
y=np.zeros((len(label_class),max(label_class)+1))
for x in label_class:
 y[i][x]=1
 i=i+1


i=0
y_train=np.zeros((len(label_train),max(label_train)+1))
for x in label_train:
    y_train[i][x]=1
    i=i+1

i=0
y_test=np.zeros((len(label_test),max(label_test)+1))
for x in label_test:
    y_test[i][x]=1
    i=i+1


t = Tokenizer()
t.fit_on_texts(input_train)
vocab_size = len(t.word_index) + 1
# integer encode the documents
encoded_docs = t.texts_to_sequences(input_train)
#print(encoded_docs)
# pad documents to a max length of 4 words
max_length = max(len_finder)
padded_docs = pad_sequences(encoded_docs, maxlen=max_length, padding='post')
#print(padded_docs)
# load the whole embedding into memory
embeddings_index = dict()
f = open("G:\\NLP\\Dataset\\GloVe\\glove.6B.100d.txt", encoding="utf8")
for line in f:
 values = line.split()
 word = values[0]
 coefs = asarray(values[1:], dtype='float32')
 embeddings_index[word] = coefs
f.close()
#print('Loaded %s word vectors.' % len(embeddings_index))
# create a weight matrix for words in training docs
embedding_matrix = zeros((vocab_size, 100))
for word, i in t.word_index.items():
 embedding_vector = embeddings_index.get(word)
 if embedding_vector is not None:
  embedding_matrix[i] = embedding_vector

rows,cols = padded_docs.shape
input_shape = Input(shape=(rows,cols))

e = Embedding(vocab_size, 100, weights=[embedding_matrix], input_length=max_length, trainable=False)(input_shape)
tower_1 = Conv1D(64,kernel_size,padding='valid',activation='relu',strides=1)(e)
tower_1 = MaxPooling1D(pool_size=pool_size)(tower_1)

tower_2 = Conv1D(64,kernel_size,padding='valid',activation='relu',strides=1)(e)
tower_2 = MaxPooling1D(pool_size=pool_size)(tower_2)

merged = concatenate([tower_1, tower_2])

out = Dense(200, activation='relu')(merged)
out = Dense(15, activation='softmax')(out)

model = Model(input_shape, out)

# compile the model
model.compile(optimizer='rmsprop', loss='binary_crossentropy', metrics=['accuracy'])
# summarize the model
print(model.summary())
# fit the model
model.fit(padded_docs,y_train, epochs=3, verbose=0)


#Testing the model
tt = Tokenizer()
tt.fit_on_texts(input_test)
tvocab_size = len(tt.word_index) + 1
# integer encode the documents
tencoded_docs = tt.texts_to_sequences(input_test)
#print(encoded_docs)
# pad documents to a max length of 4 words
tpadded_docs = pad_sequences(tencoded_docs, maxlen=max_length, padding='post')
#print(padded_docs)


# evaluate the model
loss, accuracy = model.evaluate(tpadded_docs, y_test, verbose=0)
print('Accuracy: %f' % (accuracy*100))