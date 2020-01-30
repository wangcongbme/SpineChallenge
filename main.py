import numpy as np
import os
import torch
import torch.nn as nn


from label_io import read_data_names, read_labels, plot_image, chw, hwc
from dataset import CoordDataset, get_loader_train, get_loader_test, get_loader_train_val
from model import SegmentNet, LandmarkNet, get_classifier_deep, SpinalStructured, get_classifier_conv
from train import Trainer

'''
git : revert to last commit 한다음 pull해주면 되겠다!

Labtop : 34 nopad
desktop : 101 nopad

cloud : 101 pad
34 nopad
101 nopad plus grad
each 2000

'''
device = torch.device("cuda:0" if torch.cuda.is_available()  else "cpu")

###################################
# TRAINING           ##############
###################################

config = dict(num_epochs=2000, learning_rates=1e-5, save_every=25,
              all_model_save=0.99,
              is_lr_decay=True, lrdecay_thres=0.1, lrdecay_every=200, lrdecay_window = 50,
              model_save_dest="./model", dropout_prob=0.5
              )
batch_size = 24
pad_mode = 'nopad' # pad or nopad
config['model_name'] = 'renew_34'
config['model_name'] += '_' + pad_mode

####    DataLoader
loader_train = get_loader_train(tfm = pad_mode, batch_size=batch_size, shuffle=True)
loader_val = get_loader_test(tfm = pad_mode, batch_size = 1, shuffle = False )
####    MODEL 101_deep
#model = LandmarkNet(resnet_dim=101, classifier = get_classifier_deep(config['dropout_prob'])).to(device)

####    MODEL 34_swallow
cl34 = nn.Sequential(*[#512 16 8 for 34
    nn.Conv2d(512,128,1),
    nn.BatchNorm2d(128),
    nn.ReLU(),

    nn.Conv2d(128,128,3,padding = 1),
    nn.BatchNorm2d(128),
    nn.ReLU(),

    nn.Conv2d(128,128,kernel_size=4, stride=2, padding =1),
    nn.BatchNorm2d(128),
    nn.ReLU(),

    nn.Flatten(),
    nn.Linear(128*8*4,4096),
    nn.ReLU(),
    nn.Dropout(config['dropout_prob']),

    nn.Linear(4096,136)

])
model = LandmarkNet(resnet_dim=34, classifier = cl34, requires_grad=True).to(device)

trainer = Trainer(model=model,
                  optimizer=torch.optim.Adam(model.parameters(), lr=config['learning_rates']),
                  loader_train = loader_train, loader_val = loader_val, criterion = nn.SmoothL1Loss(), **config)

#trainer.test(test_loader=loader_val, load_model_name='NEW_TEST_ep4_tL1.65e+16_vL1.55e+00.tar')
trainer.load_model('renew_34_nopad_ep350_tL4.32e-04_vL5.09e-04.tar', model_only = False)
#trainer.load_model()
trainer.train()



