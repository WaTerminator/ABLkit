import os

import torchvision
from torchvision.transforms import transforms

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_data(file, img_dataset, get_pseudo_label):
    X = []
    if get_pseudo_label:
        Z = []
    Y = []
    with open(file) as f:
        for line in f:
            line = line.strip().split(" ")
            X.append([img_dataset[int(line[0])][0], img_dataset[int(line[1])][0]])
            if get_pseudo_label:
                Z.append([img_dataset[int(line[0])][1], img_dataset[int(line[1])][1]])
            Y.append(int(line[2]))

    if get_pseudo_label:
        return X, Z, Y
    else:
        return X, None, Y

def get_mnist_add(train=True, get_pseudo_label=False):
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))]
    )
    img_dataset = torchvision.datasets.MNIST(
        root=CURRENT_DIR, train=train, download=True, transform=transform
    )
    if train:
        file = os.path.join(CURRENT_DIR, "train_data.txt")
    else:
        file = os.path.join(CURRENT_DIR, "test_data.txt")

    return get_data(file, img_dataset, get_pseudo_label)
