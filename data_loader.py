# -*- coding: utf-8 -*-
"""CSC413_FP_Data_Processing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/github/pinnouse/zeroshot-unsurpervised-mt/blob/main/CSC413_FP_Data_Processing.ipynb

Packages
"""

#!pip install apache_beam mwparserfromhell
#!pip install transformers
#!pip install datasets
#!pip install ftfy regex tqdm
#!pip install git+https://github.com/openai/CLIP.git

# multilingual CLIP pretrained
# https://github.com/FreddeFrallan/Multilingual-CLIP
#!pip install multilingual-clip
#!pip install -U sentence-transformers

"""Data Batching"""

from datasets import load_dataset
import random
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')

dataset = load_dataset("wikipedia", "20220301.simple")
dataset_fr = load_dataset("wikipedia", "20220301.fr")
dataset_ar = load_dataset('SaiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101')
dataset_lux = load_dataset("wikipedia", "20220301.frr")
dataset_jp = load_dataset("AhmedSSabir/Japanese-wiki-dump-sentence-dataset")

training_percent = 0.8
validation_percent = 0.1
testing_percent = 0.1

# english
ds_en_len = len(dataset)
test_index_en = ds_en_len * training_percent
valid_index_en = ds_en_len * (training_percent + validation_percent)

# start to test index
test_data_en = dataset['train'][: int(test_index_en)]
# test index to validation index
validation_data_en = dataset['train'][int(test_index_en):int(valid_index_en)]
# validation index to end
test_data_en = dataset['train'][int(valid_index_en):]

# french
ds_fr_len = len(dataset_fr)
test_index_fr = ds_fr_len * training_percent
valid_index_fr = ds_fr_len * (training_percent + validation_percent)

# start to test index
test_data_fr = dataset['train'][: int(test_index_fr)]
# test index to validation index
validation_data_fr = dataset['train'][int(test_index_fr):int(valid_index_fr)]
# validation index to end
test_data_fr = dataset['train'][int(valid_index_fr):]

# arabic
ds_ar_len = len(dataset['train'])
test_index_ar = ds_ar_len * training_percent
valid_index_ar = ds_ar_len * (training_percent + validation_percent)

# start to test index
test_data_ar = dataset['train'][: int(test_index_ar)]
# test index to validation index
validation_data_ar = dataset['train'][int(test_index_ar):int(valid_index_ar)]
# validation index to end
test_data_ar = dataset['train'][int(valid_index_ar):]

def batch_loader(dataset, batch_size, shuffle=True):
  text = dataset['train']['text']

  if shuffle:
    random.shuffle(text)

  data_batch = []

  for i in range((len(text) // batch_size)):
    data_batch.append(text[i * batch_size:(i + 1) * batch_size])

  if len(text) % batch_size != 0:
    data_batch.append(text[(len(text) // batch_size) * batch_size:])
  
  return data_batch

text = map(lambda x: x['text'].replace("\n", ' ').split(". "), dataset['train'])
text_long = []
for t in text:
  for s in t:
    text_long.append(s) 

text_fr = map(lambda x: x['text'].replace("\n", ' ').split(". "), dataset_fr['train'])
for t in text_fr:
  print(t)
  break

import torch
import torchtext
import clip
import numpy as np
from sentence_transformers import SentenceTransformer, util

device = "cuda" if torch.cuda.is_available() else "cpu"
# model, preprocess = clip.load("ViT-B/32", device=device)

text_model = SentenceTransformer('sentence-transformers/clip-ViT-B-32-multilingual-v1',
                                 device=device)

context_length = 64
#glove = torchtext.vocab.GloVe(name="6B", dim=50)
#ft = torchtext.vocab.FastText(language="simple")

"""Tokenize/Embbed English data"""

train_data_en = []
for (i, t) in enumerate(text_long):
  if i > 5:
    break
  tokenized = tokenizer(t, padding='max_length', max_length=64, return_tensors='pt').input_ids[0] #took 18 mins to run
  if len(tokenized) <= 64:
    sentences = []
    for s in range(len(tokenized)):
      sentences.append(tokenizer.decode(tokenized[1:s], skip_special_tokens=True))
    #[bs x 64 x 512]
    clips = text_model.encode(sentences)
    train_data_en.append((t,clips,tokenized))

"""Tokenize/Embbed French data"""

train_data_fr = []

for (i, t) in enumerate(text_fr):
  if i > 5:
    break
  sentence = t[0]
  if len(sentence.split(' ')) > 60:
    continue
  tokenized = tokenizer(sentence, padding='max_length', max_length=64, return_tensors='pt')['input_ids'][0]
  # tokenized = tokenized.to(device)
  train_data_fr.append((sentence, tokenized))

def data_loader(language):
  if language == 'en':
      dataset = load_dataset('wikipedia', '20220301.simple')
  elif language == 'fr':
      dataset = load_dataset('wikipedia', '20220301.fr')
  elif language == 'frr':
      dataset = load_dataset('wikipedia', '20220301.frr')
  elif language == 'jp':
      dataset = load_dataset('AhmedSSabir/Japanese-wiki-dump-sentence-dataset')

  # load clip model
  device = "cuda" if torch.cuda.is_available() else "cpu"
  text_model = SentenceTransformer('sentence-transformers/clip-ViT-B-32-multilingual-v1', device=device)

  tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')

  train_data, val_data, test_data = [], [], []

  for split_type in ["train", "validation", "test"]:
    curr_split = dataset[split_type]

    temp_data = []
    for sentence in curr_split["text"]:
      tokenized = tokenizer(sentence, padding='max_length', max_length=64, return_tensors='pt', truncation=True)

      if len(tokenized) <= 64:
        sentences = []
        for i in range(len(tokenized)):
            sentence = tokenizer.decode(tokenized[:i+1], skip_special_tokens=True)
            sentences.append(sentence)
        clips = text_model.encode(sentences)

        temp_data.append((sentence, clips, tokenized))
    
      if curr_split == "train":
          train_data = curr_split
      elif curr_split == "validation":
          val_data = curr_split
      else:
          test_data = curr_split

  return (train_data, val_data, test_data)

en_data = data_loader("en")
print(en_data)