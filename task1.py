# -*- coding: utf-8 -*-
"""ML_Tutorial_01.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KtvK2LQpWbhQOYdQNsA55WFBqMeuwiCL

**Sequence of tutorial**
1. Getting started with Google Colab
2. Loading and normalizing data
3. Intializing Neural Network Class
4. Initializing loss and optimizer Class
5. Training the Model
6. Saving and Loading the Model
7. Testing the model
8. Custom dataset class and dataloaders
"""

from google.colab import drive
drive.mount('/content/drive')

import zipfile
with zipfile.ZipFile('/content/drive/MyDrive/MNIST_Data.zip', 'r') as zip_ref:
    zip_ref.extractall('/content/MNIST_Data')

import torch
import torchvision
from torchvision import transforms, datasets

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

"""**Load and Normalize MNIST data**"""

transform = transforms.Compose([transforms.Grayscale(), 
                                         transforms.ToTensor(),
                                         #transforms.Resize((28,28)), 
                                         transforms.Normalize(0,0.5)])

batch_size = 4
train_set = datasets.ImageFolder('/content/MNIST_Data/train', 
                                 transform=transform)
train_loader = torch.utils.data.DataLoader(train_set, batch_size=batch_size, shuffle=True)


test_set = datasets.ImageFolder('/content/MNIST_Data/test', 
                                transform=transform)
test_loader = torch.utils.data.DataLoader(test_set, batch_size=batch_size, shuffle=True)

len(train_set) , len(test_set)

import matplotlib.pyplot as plt
import numpy as np

# function to show images
def imshow(img):
  img = img * 0.5
  np_img = img.numpy() 
  plt.imshow(np.transpose(np_img*255, (1,2,0)).astype(np.uint8))
  plt.show()

# get some random images
dataiter = iter(train_loader)
images, labels = dataiter.next()

# show images
imshow(torchvision.utils.make_grid(images))

# show labels
print('Labels: ', labels)

"""**Initialize Neural Network**"""

from torch import nn
import torch.nn.functional as F


class Net(nn.Module):
  def __init__(self):
    super().__init__()
    self.fc1 = nn.Linear(28*28, 400)
    self.fc2 = nn.Linear(400, 120)
    self.fc3 = nn.Linear(120, 84)
    self.fc4 = nn.Linear(84, 10)


  def forward(self, x):
    x = torch.flatten(x, 1) # flatten all dimension except batch
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc2(x))
    x = F.relu(self.fc3(x))
    x = self.fc4(x)
    return x

net = Net().to(device)

print(net)

"""**Training the Model**"""

from torch import optim

# loss
criterion = nn.CrossEntropyLoss()

#optimizer
optimizer = optim.Adam(net.parameters(), lr=0.001)

total_epochs = 4
total_step = len(train_loader)
train_loss = []

for epoch in range(total_epochs): # iterate over epochs
  epoch_loss = 0
  for i, data in enumerate(train_loader): # iterate over batches
    # get image and labels data is in tuple form (inputs, label)
    inputs, labels = data
    inputs = inputs.to(device)
    labels = labels.to(device)

    # Zero-out gradients
    optimizer.zero_grad()
    # print(inputs.get_device())
    # print(labels.get_device())

    # # forward + backward + optimize
    outputs = net(inputs)
    loss = criterion(outputs, labels)
    loss.backward()
    optimizer.step()
    epoch_loss += loss.item()
    
    if (i+1) % 500 == 0:
      print ('Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}' .format(epoch+1, total_epochs, i+1, total_step, loss.item()))
  train_loss.append(epoch_loss)

# epoch vs loss graph

plt.plot([1,2,3,4], train_loss)
plt.title('Epochs vs Loss')
plt.show()

# save model
path = '/content/mnist.pt'
torch.save(net.state_dict(), path)

# load model
net.load_state_dict(torch.load(path))

"""**Testing Model**"""

# get some random images
dataiter = iter(test_loader)
images, test_labels = dataiter.next()

# show images
imshow(torchvision.utils.make_grid(images))

# show labels
print(test_labels)

# test trained model
test_out = net(images.to(device))
test_out.shape

# Finding predicted class
_, pred = torch.max(test_out, 1) 
pred

"""## Custom Dataset and DataLoader"""

img_dir = '/content/drive/MyDrive/Mnist_subset/imgs'
label_file = '/content/drive/MyDrive/Mnist_subset/labels.csv'

import pandas as pd

# reading label file
df = pd.read_csv(label_file)
df.head()

import os

# create directories
os.makedirs('data', exist_ok=True)
for i in range(10):
  
  os.makedirs(os.path.join('data', str(i)), exist_ok=True)

import cv2

for i in range(10):
  # find imgs belonging to class i
  id_df = df.loc[df.labels == i]

  # create image list
  img_list = id_df.img.to_list()
  
  for img in img_list:
    # reading img
    image = cv2.imread(os.path.join(img_dir,img))

    # saving image in the relevant directory
    cv2.imwrite(os.path.join('data',str(i),img), image)

from torch.utils.data import Dataset
import PIL

class Custom_Dataset(Dataset):
  def __init__(self, csv_file, img_dir, transform=None): 
    # Run once
    self.img_labels = pd.read_csv(csv_file)
    self.transform = transform
    self.img_dir = img_dir
    

  def __len__(self):
    # return the number of samples in dataset
    return len(self.img_labels)

  def __getitem__(self, idx):
    # loads and returns a sample from the dataset at the given index
    img_path = os.path.join(self.img_dir ,self.img_labels.iloc[idx, 0])
    image = PIL.Image.open(img_path)
    label = torch.tensor(self.img_labels.iloc[idx, 1])
    
    if self.transform:
      image = self.transform(image)
        
    return image, label

# creating dataset object
dataset = Custom_Dataset(csv_file=label_file, img_dir=img_dir, transform=transform)

# creating dataset iterator
data_loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)

# get some random images
dataiter = iter(data_loader)
images, labels = dataiter.next()

# show images
imshow(torchvision.utils.make_grid(images))

# show labels
print('Labels:', labels)

