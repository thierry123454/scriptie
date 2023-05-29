import numpy as np
import matplotlib.pyplot as plt
import os
import wave
import pylab
from pathlib import Path
from scipy import signal
from scipy.io import wavfile
from sklearn.metrics import confusion_matrix
import itertools
import torch
import torchaudio
from torchaudio.datasets import SPEECHCOMMANDS
from torchvision.transforms import ToTensor

from sklearn.metrics import classification_report
from torch.utils.data import random_split
from torch.utils.data import DataLoader
from torchvision.transforms import ToTensor
from torch.optim import Adam
from torch import nn
from torch.nn import functional as F

import time

from models.morph_audio_model import MorphAudioModel

torch.manual_seed(0)

# define training hyperparameters
INIT_LR = 1e-3
BATCH_SIZE = 32
EPOCHS = 10

# set the device we will be using to train the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Specify the root directory where you want to store the dataset
root_dir = "data/speech_commands"

# Create the root directory if it does not exist
os.makedirs(root_dir, exist_ok=True)

# load the dataset
trainData = SPEECHCOMMANDS(root="data/speech_commands", subset="training", download=True)
valData = SPEECHCOMMANDS(root="data/speech_commands", subset="validation", download=True)
testData = SPEECHCOMMANDS(root="data/speech_commands", subset="testing", download=True)

word_list = ['marvin', 'four', 'follow', 'stop', 'backward', 
	         'left', 'off', 'two', 'sheila', 'five', 'one', 
			 'eight', 'house', 'tree', 'forward', 'on', 'three', 
			 'dog', 'go', 'visual', 'happy', 'wow', 'cat', 'no', 
			 'bird', 'learn', 'right', 'up', 'zero', 'six', 'yes', 
			 'nine', 'down', 'seven', 'bed']

word_dict = {word: i for i, word in enumerate(word_list, start=1)}

def collate_fn(batch):
	# ADD PADDING!!!
	audio = [item[0].tolist() for item in batch]
	labels = [item[2] for item in batch]
	labels_numeric = [word_dict[label] for label in labels]
	print(torch.tensor(audio).shape)
	return torch.tensor(audio), torch.tensor(labels_numeric)

# initialize the train, validation, and test data loaders
trainDataLoader = DataLoader(trainData, shuffle=True, batch_size=BATCH_SIZE, collate_fn=collate_fn)
valDataLoader = DataLoader(valData, shuffle=True, batch_size=BATCH_SIZE, collate_fn=collate_fn)
testDataLoader = DataLoader(testData, batch_size=BATCH_SIZE, collate_fn=collate_fn)

# calculate steps per epoch for training and validation set
trainSteps = len(trainDataLoader.dataset) // BATCH_SIZE

model = MorphAudioModel(1, len(word_list)).to(device)

# initialize our optimizer and loss function
opt = Adam(model.parameters(), lr=INIT_LR)
lossFn = nn.NLLLoss()

startTime = time.time()
for _ in range(EPOCHS):
	model.train()

	for (x, y) in trainDataLoader:
		break
		(x, y) = (x.to(device), y.to(device))
		pred = model(x)
		loss = lossFn(pred, y)
		opt.zero_grad()
		loss.backward()
		opt.step()
totalTime = time.time() - startTime

with torch.no_grad():
	model.eval()

	preds = []

	for (x, y) in testDataLoader:
		x = x.to(device)
		pred = model(x)
		preds.extend(pred.argmax(axis=1).cpu().numpy())

class_report = classification_report(testData.targets.cpu().numpy(),
										np.array(preds),
										target_names=testData.classes,
										output_dict=True)

print(class_report["accuracy"])
print(class_report["macro avg"]["f1-score"])
print(class_report["macro avg"]["precision"])
print(class_report["macro avg"]["recall"])
print(totalTime)