import time
from tempfile import TemporaryDirectory

import numpy as np
import os
from PIL import Image

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

import torchvision
import torchvision.transforms as transforms
from torch.backends import cudnn
from torch.utils.data import Subset, DataLoader
from torchvision import datasets, models
import matplotlib.pyplot as plt

cudnn.benchmark = True
dev = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
plt.ion()   # interactive mode

mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])

#Transformation of data method
tf = {
    'train': transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(.6, 1.0)),
    transforms.ToTensor(), #0, 1 range
    transforms.Normalize(mean, std)#imagenet data normalization
    ]),
    'val' : transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean, std)
    ])
}


def get_val_train_chunks(data_dir = 'mag7'):
    """
    :param data_dir: Directory where all the images are located
    :return: training dataset, validation dataset, class list of the entire full dataset
    """
    # All data in mag7 (7 sub folders)
    train_full = datasets.ImageFolder(data_dir, transform=tf['train'])
    val_full = datasets.ImageFolder(data_dir, transform=tf['val'])

    # splitting into val and training
    n = len(train_full)  # size of entire dataset
    n_val = int(.2 * n)  # size of validation set

    # shuffling the data so that everything is trained and everything is validated
    idx = torch.randperm(n)

    val_idx = idx[:n_val]  # validation chunk
    train_idx = idx[n_val:]  # training chunk

    train_ds = Subset(train_full, train_idx)
    val_ds   = Subset(val_full, val_idx)

    return train_ds, val_ds, train_full.classes

def build_model():
    """
    Builds the Transfer Training Model before training
    :return:
        model - resnet18 with last layer swapped to len(x) classes on GPU or CPU
        train_data - training Dataloader Subset (augmented transform)
        val_data - validation Dataloader Subset (clean transform)
        x - list of class names
    """
    train_data, val_data, x = get_val_train_chunks()

    model = models.resnet18(weights='DEFAULT')
    model.fc = nn.Linear(model.fc.in_features, len(x)) #creates final layer with 512 inputs that give 7 class scores
    model.to(dev) #sends model to GPU or CPU

    dataloaders = {
        'train': DataLoader(train_data, batch_size=32, shuffle=True),
        'val':   DataLoader(val_data,   batch_size=32),
    }

    return model, dataloaders, x

def train_model(model, dataloaders, optimizer, scheduler, num_epochs=25, criterion=nn.CrossEntropyLoss()):
    """
    :param model: Modified ResNet18 model
    :param dataloaders: dict with 'train' and 'val' DataLoaders
    :param criterion: loss function - Cross Entropy Loss for classification. (more loss = worse)
    :param optimizer: Adjusts weights to reduce loss (The learning)
    :param scheduler: Lowers learning rate over time
    :param num_epochs: Iterations
    :return: trained model
    """
    since = time.time() #tracks time of training

    #Temp folder to save checkpoints and save initial weights, if val_accuracy does not improve somethiing needs to load back
    with TemporaryDirectory() as tmpdir:
        best_model_params_path = os.path.join(tmpdir, 'best_model.pth')
        torch.save(model.state_dict(), best_model_params_path)
        best_acc = 0.0


        for epoch in range(num_epochs):
            print(f'Epoch {epoch}/{num_epochs - 1}')
            print('-' * 10)
            #runs train then val in each epoch
            for phase in ['train', 'val']:
                if phase == 'train':
                    model.train() #enapbles ddropout/bathnorm updates
                else:
                    model.eval() #freezes them for consistent results

                running_loss = 0.0
                running_corrects = 0.0

                #pulls batches to gpu/cpu
                for inputs, labels in dataloaders[phase]:
                    inputs = inputs.to(dev)
                    labels = labels.to(dev)

                    optimizer.zero_grad()  # clears gradients from previous batch

                    with torch.set_grad_enabled(phase == 'train'): #turns gradient tracking off during val for memory saving
                        outputs = model(inputs)
                        _, preds = torch.max(outputs, 1) #index of highest score
                        loss = criterion(outputs, labels) #how wrong was the prediction

                        if phase == 'train':
                            loss.backward() #computes gradients through network during training
                            optimizer.step() #updates weights using the gradients (learning)

                    #total loss and correct predictions across current epoch
                    running_loss += loss.item() * inputs.size(0)
                    running_corrects += torch.sum(preds == labels.data).item()

                if phase == 'train': #after a train phase lower the learning rate
                    scheduler.step()

                n = len(dataloaders[phase].dataset)
                # avg loss and accuracy over all the images in the current phase
                epoch_loss = running_loss / n
                epoch_acc = running_corrects / n
                print(f'{phase} Loss: {epoch_loss:.4f}  Acc: {epoch_acc:.4f}')

                if phase == 'val' and epoch_acc > best_acc: #save checkpoint if best accuracy
                    best_acc = epoch_acc
                    torch.save(model.state_dict(), best_model_params_path)

        time_elapsed = time.time() - since
        print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
        print(f'Best val Acc: {best_acc:.4f}')


        model.load_state_dict(torch.load(best_model_params_path))
        # after all epochs load the best checkpoint back and return it
    return model


if __name__ == '__main__':
    m, dataloaders, classes = build_model()

    print("classes:", classes)
    print("train batches:", len(dataloaders['train']), "| images:", len(dataloaders['train'].dataset))  # type: ignore[arg-type]
    print("val batches:",   len(dataloaders['val']),   "| images:", len(dataloaders['val'].dataset))    # type: ignore[arg-type]

    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(m.parameters(), lr=0.001, momentum=0.9)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    m = train_model(m, dataloaders, optimizer, scheduler, num_epochs=25, criterion=criterion)
    torch.save(m.state_dict(), 'mag7_resnet18.pth')
    print('Model saved to mag7_resnet18.pth')