import torch
import numpy as np
from utils.utils import AverageMeter
from utils.eval import Accuracy, getPreds, MPJPE
from utils.debugger import Debugger
#from models.layers.FusionCriterion import FusionCriterion
import cv2
import ref
from progress.bar import Bar
from mse import mean_squared_error
import os

def _checkpoint( model, optimizer ):
  filename = os.path.join( 'save' )
 # torch.save({'epoch': epoch + 1, 'logger': logger.state_dict()}, filename + '.iter')
  torch.save(model.state_dict(), filename + '.model')
  torch.save(optimizer.state_dict(), filename + '.state')


def step(split, epoch, opt, dataLoader, model, criterion, optimizer = None):

  if True:
    model.load_state_dict(torch.load("save.model"))
    optimizer.load_state_dict(torch.load("save.state"))

  if split == 'train':
    model.train()
  else:
    model.eval()

  Loss, Acc, Mpjpe, Loss3D = AverageMeter(), AverageMeter(), AverageMeter(), AverageMeter()

  nIters = len(dataLoader)
  bar = Bar('==>', max=nIters)


  #print("aaaaaaaaaaaaaaaaa")

  for i, (input, target3D, meta) in enumerate(dataLoader):
    #print(input.size())
    input_var = torch.autograd.Variable(input).float().cuda()
#    target3D_var = torch.autograd.Variable(target3D).float().cuda()
    target3D_var = torch.autograd.Variable(meta).float().cuda()


 #   print(target3D_var)

    output = model(input_var)
#    reg = output[opt.nStack]

    optimizer.zero_grad()
    loss = mean_squared_error(output, target3D_var)
    loss.backward()
    optimizer.step()

    #print(i)



    Loss.update(loss, input.size(0))
    #Acc.update(Accuracy((output.data).cpu().numpy(), (target3D_var.data).cpu().numpy()))

    #Bar.suffix = '{split} Epoch: [{0}][{1}/{2}]| Total: {total:} | ETA: {eta:} | Loss {loss.avg:.6f} | Loss3D {loss3d.avg:.6f} | Acc {Acc.avg:.6f} | Mpjpe {Mpjpe.avg:.6f} ({Mpjpe.val:.6f})'.format(epoch, i, nIters, total=bar.elapsed_td, eta=bar.eta_td, loss=Loss, Acc=Acc, split = split, Mpjpe=Mpjpe, loss3d = Loss3D)
    Bar.suffix = '{split} Epoch: [{0}][{1}/{2}]| Total: {total:} | ETA: {eta:} | Loss {lossa:} '.format(epoch, i, nIters, total=bar.elapsed_td, eta=bar.eta_td, lossa = Loss.avg, split=split)
    #print(Loss.avg)
    bar.next()
    bar.finish()

    if i%500 == 0:
        _checkpoint( model, optimizer)

  return Loss.avg #, Acc.avg, Mpjpe.avg, Loss3D.avg


def train(epoch, opt, train_loader, model, criterion, optimizer):
  return step('train', epoch, opt, train_loader, model, criterion, optimizer)

def val(epoch, opt, val_loader, model, criterion):
  return step('val', epoch, opt, val_loader, model, criterion)



