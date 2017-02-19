import torch
from torch import nn
from chainer import functions as F


def replace_weight(t, c):
    t.data.copy_(torch.from_numpy(c.data))


class LSTM(nn.LSTM):

    @classmethod
    def from_chainer(cls, c):
        cweights = c._children[0]
        d_hid, d_in = cweights.w0.shape
        t = cls(d_in, d_hid)
        c_ih_w = F.concat([getattr(cweights, 'w{}'.format(i)) for i in range(4)], 0)
        c_ih_b = F.concat([getattr(cweights, 'b{}'.format(i)) for i in range(4)], 0)
        replace_weight(t.weight_ih_l0, c_ih_w)
        replace_weight(t.bias_ih_l0, c_ih_b)

        c_hh_w = F.concat([getattr(cweights, 'w{}'.format(i)) for i in range(4, 8)], 0)
        c_hh_b = F.concat([getattr(cweights, 'b{}'.format(i)) for i in range(4, 8)], 0)
        replace_weight(t.weight_hh_l0, c_hh_w)
        replace_weight(t.bias_hh_l0, c_hh_b)
        return t


class Linear(nn.Linear):

    @classmethod
    def from_chainer(cls, c):
        d_hid, d_in = c.W.shape
        t = cls(d_in, d_hid)
        replace_weight(t.weight, c.W)
        replace_weight(t.bias, c.b)
        return t

    def forward(self, input):
        shape = list(input.size())
        d_hid, d_in = self.weight.size()
        shape[-1] = d_hid
        return super().forward(input.view(-1, d_in)).view(*shape)


class Embedding(nn.Embedding):

    @classmethod
    def from_chainer(cls, c):
        vocab_size, d_emb = c.W.shape
        t = cls(vocab_size, d_emb)
        replace_weight(t.weight, c.W)
        return t
