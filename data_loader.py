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

# dataset = load_dataset("wikipedia", "20220301.simple")
# dataset_fr = load_dataset("wikipedia", "20220301.fr")
# dataset_ar = load_dataset('SaiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101')
# dataset_lux = load_dataset("wikipedia", "20220301.frr")
# dataset_jp = load_dataset("AhmedSSabir/Japanese-wiki-dump-sentence-dataset")

# training_percent = 0.8
# validation_percent = 0.1
# testing_percent = 0.1
# training_percent = 0.8
# validation_percent = 0.1
# testing_percent = 0.1

# # english
# # ds_en_len = len(dataset)
# # test_index_en = ds_en_len * training_percent
# # valid_index_en = ds_en_len * (training_percent + validation_percent)

# # # start to test index
# # test_data_en = dataset['train'][: int(test_index_en)]
# # # test index to validation index
# # validation_data_en = dataset['train'][int(test_index_en):int(valid_index_en)]
# # # validation index to end
# # test_data_en = dataset['train'][int(valid_index_en):]

# # # french
# # ds_fr_len = len(dataset_fr)
# # test_index_fr = ds_fr_len * training_percent
# # valid_index_fr = ds_fr_len * (training_percent + validation_percent)

# # # start to test index
# # test_data_fr = dataset['train'][: int(test_index_fr)]
# # # test index to validation index
# # validation_data_fr = dataset['train'][int(test_index_fr):int(valid_index_fr)]
# # # validation index to end
# # test_data_fr = dataset['train'][int(valid_index_fr):]

# # # arabic
# # ds_ar_len = len(dataset['train'])
# # test_index_ar = ds_ar_len * training_percent
# # valid_index_ar = ds_ar_len * (training_percent + validation_percent)

# # # start to test index
# # test_data_ar = dataset['train'][: int(test_index_ar)]
# # # test index to validation index
# # validation_data_ar = dataset['train'][int(test_index_ar):int(valid_index_ar)]
# # # validation index to end
# # test_data_ar = dataset['train'][int(valid_index_ar):]

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

# text = map(lambda x: x['text'].replace("\n", ' ').split(". "), dataset['train'])
# text_long = []
# for t in text:
#   for s in t:
#     text_long.append(s) 

# text_fr = map(lambda x: x['text'].replace("\n", ' ').split(". "), dataset_fr['train'])
# for t in text_fr:
#   print(t)
#   break

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

# """Tokenize/Embbed English data"""

# train_data_en = []
# for (i, t) in enumerate(text_long):
#   if i > 5:
#     break
#   tokenized = tokenizer(t, padding='max_length', max_length=64, return_tensors='pt').input_ids[0] #took 18 mins to run
#   if len(tokenized) <= 64:
#     sentences = []
#     for s in range(len(tokenized)):
#       sentences.append(tokenizer.decode(tokenized[1:s], skip_special_tokens=True))
#     #[bs x 64 x 512]
#     clips = text_model.encode(sentences)
#     train_data_en.append((t,clips,tokenized))

# """Tokenize/Embbed French data"""

# train_data_fr = []

# for (i, t) in enumerate(text_fr):
#   if i > 5:
#     break
#   sentence = t[0]
#   if len(sentence.split(' ')) > 60:
#     continue
#   tokenized = tokenizer(sentence, padding='max_length', max_length=64, return_tensors='pt')['input_ids'][0]
#   # tokenized = tokenized.to(device)
#   train_data_fr.append((sentence, tokenized))

def dataset_splitter(dataset):
  training_percent = 0.8
  validation_percent = 0.1
  testing_percent = 0.1

  # creating index
  ds_len = len(dataset)
  test_index = ds_len * training_percent
  valid_index = ds_len * (training_percent + validation_percent)

  # start to test index
  test_data = dataset['train'][: int(test_index)]
  # test index to validation index
  validation_data = dataset['train'][int(test_index):int(valid_index)]
  # validation index to end
  test_data = dataset['train'][int(valid_index):]

  return [test_data, validation_data, test_data]
  
def dataset_splitter(dataset):
  training_percent = 0.24
  validation_percent = 0.03
  testing_percent = 0.03

  # creating index
  ds_len = len(dataset)
  test_index = ds_len * training_percent
  valid_index = ds_len * (training_percent + validation_percent)

  # start to test index
  train_data = dataset['train'][: int(test_index)]
  # test index to validation index
  validation_data = dataset['train'][int(test_index):int(valid_index)]
  # validation index to end
  test_data = dataset['train'][int(valid_index):]

  return [train_data, validation_data, test_data]
  
def data_loader(language):
  if language == 'en':
      dataset = load_dataset('wikipedia', '20220301.simple')
  elif language == 'fr':
      dataset = load_dataset('wikipedia', '20220301.fr')
  elif language == 'ar':
      dataset = load_dataset('SaiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101')
  elif language == 'frr':
      dataset = load_dataset('wikipedia', '20220301.frr')
  elif language == 'jp':
      dataset = load_dataset('AhmedSSabir/Japanese-wiki-dump-sentence-dataset')
  else:
    print("Error")

  # load clip model
  device = "cuda" if torch.cuda.is_available() else "cpu"
  text_model = SentenceTransformer('sentence-transformers/clip-ViT-B-32-multilingual-v1', device=device)

  tokenizer = BertTokenizer.from_pretrained('bert-base-multilingual-cased')

  # Split train dataset into train, validation, and test datasets
  split_datasets = dataset_splitter(dataset)

  train_data = {'sentences': [], 'clips': [], 'tokens': []}
  val_data = {'sentences': [], 'clips': [], 'tokens': []}
  test_data = {'sentences': [], 'clips': [], 'tokens': []}

  split_types = ["train", "validation", "test"]
  for split_type in enumerate(split_types):
    curr_split = split_datasets[split_type[0]]

    # print(curr_split)
    print(split_type[0])
    print(split_type[1])

    temp_data = []
    for sentence in curr_split["text"]:
      tokenized = tokenizer(sentence, padding='max_length', max_length=64, return_tensors='pt', truncation=True)['input_ids']

      if len(tokenized) <= 64:
        sentences = []
        for s in range(len(tokenized)):
          sentences.append(tokenizer.decode(tokenized[1:s], skip_special_tokens=True))
        #[bs x 64 x 512]
        clips = text_model.encode(sentences)
    
        if split_type[1] == "train":
            train_data['sentences'].append(sentences)
            train_data['clips'].append(clips)
            train_data['tokens'].append(tokenized)
        elif split_type[1] == "validation":
            val_data['sentences'].append(sentences)
            val_data['clips'].append(clips)
            val_data['tokens'].append(tokenized)
        elif split_type[1] == "test":
            test_data['sentences'].append(sentences)
            test_data['clips'].append(clips)
            test_data['tokens'].append(tokenized)

  return (train_data, val_data, test_data)

# en_data = data_loader("en")
# print(en_data)
# ds = load_dataset('wikipedia', '20220301.simple')
# print(ds)
# ds_ar = load_dataset('SaiedAlshahrani/Moroccan_Arabic_Wikipedia_20230101')
# print(ds_ar)
ar_data = data_loader("ar")
# print(ar_data)
print(ar_data[0])
print(ar_data[0]['sentences'])

# split_types = ["train", "validation", "test"]
# for split_type in enumerate(split_types):
#   print(split_type)
#   print(split_type[0])
#   print(split_type[1])
