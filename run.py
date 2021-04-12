import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image
import torch.nn as nn
import torch.nn.functional as F
import torch.nn.init as init

import argparse
parser = argparse.ArgumentParser(description='SRCNN run parameters')
parser.add_argument('--image', type=str, required=True)
args = parser.parse_args()

class SRCNN(nn.Module):
    def __init__(self):
        super(SRCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 64, kernel_size=9, padding=4)
        self.conv2 = nn.Conv2d(64, 32, kernel_size=1, padding=0)
        self.conv3 = nn.Conv2d(32, 1, kernel_size=5, padding=2)
        
    def forward(self, x):
        out = F.relu(self.conv1(x))
        out = F.relu(self.conv2(out))
        out = self.conv3(out)

        return out

image = args.image
img_in = Image.open(args.image)
img_in.show()
img = Image.open(args.image).convert('YCbCr')
img = img.resize((int(img.size[0]*2), int(img.size[1]*2)), Image.BICUBIC)  # first, we upscale the image via bicubic interpolation
y, cb, cr = img.split()

img_to_tensor = transforms.ToTensor()
input = img_to_tensor(y).view(1, -1, y.size[1], y.size[0])  # we only work with the "Y" channel

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
# device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)
model = torch.load("models/epoch-199.pth").to(device)
input = input.to(device)

out = model(input)
out = out.cpu()
out_img_y = out[0].detach().numpy()
out_img_y *= 255.0
out_img_y = out_img_y.clip(0, 255)
out_img_y = Image.fromarray(np.uint8(out_img_y[0]), mode='L')

out_img = Image.merge('YCbCr', [out_img_y, cb, cr]).convert('RGB')  # we merge the output of our network with the upscaled Cb and Cr from before
                                                                    # before converting the result in RGB
out_img.save(f"zoomed_{image}")
out_img.show()