from __future__ import division
import numpy as np
import wx
import math
import time


class DisplayPanel(wx.Frame):

    ENV = None
    def __init__(self, title):
        super(DisplayPanel,self).__init__(None, title=title, size = (800,550))
        h = 450
        w = 500

        self.panel = wx.Panel(self, -1, size = (500,500) )
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        neuron_group, self.network = self.display_group(["I1", "H1","O1", "I2", "H2", "O2"], (2,6), (0,30))
        hbox1.Add(neuron_group)

        error_group, self.error = self.display_group(["EO1", "EO2"], (2,2 ))
        vbox2.Add(error_group, flag=wx.LEFT, border = 75)
        hbox1. Add(vbox2)

        W_group, self.W = self.display_group(["W1", "W5", "W2", "W6", "W3", "W7", "W4", "W8"], (4,4))
        dW_group, self.dW = self.display_group(["dW1", "dW5", "dW2", "dW6", "dW3", "dW7", "dW4", "dW8"], (4,4))

        train_btn = wx.Button(self.panel, label='>>', size=(-1,30))
        train_btn.Bind(wx.EVT_BUTTON,self.run)
        step_btn = wx.Button(self.panel, label='>', size=(-1,30))
        step_btn.Bind(wx.EVT_BUTTON,self.step)
        vbox1.Add(train_btn)
        vbox1.Add(step_btn)
        vbox1.Add(hbox1)
        vbox1.AddSpacer((0,50))
        vbox1.Add(W_group)

        vbox1.AddSpacer((0,50))
        vbox1.Add(dW_group)

        self.brain = self.init_ANN()
        self.panel.SetSizer(vbox1)

    def display_group(self, lbl, size, border=(0,0)):
        labels = lbl
        gs = wx.GridSizer(rows=size[0],cols=size[1])
        text_group = dict()
        for label in labels:
            txt = wx.StaticText(self.panel,label=label)
            gs.Add(txt, flag=wx.ALIGN_RIGHT|wx.TOP ,border=border[1])
            txt_ctrl = wx.TextCtrl(self.panel,size=(90,-1))
            text_group.update({label: txt_ctrl})
            gs.Add(txt_ctrl, flag=wx.TOP|wx.ALIGN_RIGHT, border=border[1])

        return gs, text_group

    def init_ANN(self):
        W1 = np.matrix([[.15, .20, 1], [.25, .30, 1]])
        W2 = np.matrix([[.4, .45, 1], [.5, .55, 1]])
        target = np.matrix([[.01], [.99]])
        brain = ANN(W1, W2, 4, .5)
        brain.setTarget(target)
        self.input = np.matrix([[.05], [.10], [.35]])
        self.network['I1'].Clear()
        self.network['I1'].AppendText(str(self.input[0,0]))
        self.network['I2'].Clear()
        self.network['I2'].AppendText(str(self.input[1,0]))
        return brain

    def run(self, e):
        nTrain = 2
        self.brain.run(self.input, (self.network, self.error, self.dW, self.W), nTrain)


    def step(self, e):
        self.brain.paused = False


class ANN:
    def __init__(self, W1, W2, nWeights, LearningConstant):
        self.W1         = W1
        self.W2         = W2
        self.LC         = LearningConstant
        self.nWeights   = nWeights
        self.jacobian   = np.empty([nWeights/2,2])
        self.nNeurons   = W1.shape[0]      ##num Neurons per layer

    def setTarget(self, target):
        self.target = target

    def dE_dout(self, output, target):
        self.dEdOut = np.empty([self.nNeurons,1])
        for i in range(0, self.nNeurons):
            self.dEdOut[i]    = -(target[i,0] - output[i])
        return self.dEdOut

    def dE_dnet(self, output):
        self.dEdnet = np.empty([self.nNeurons,1])
        for i in range(0, self.nNeurons):
            self.dEdnet[i] = output[i]*(1-output[i])
        return self.dEdnet

    def feedForwardNet1(self, input):
        net01 = np.dot(self.W1,input)
        return net01

    def activate(self, input):
        activated = np.empty([self.nNeurons,1])
        for i in range(0,self.nNeurons):
            activated[i,0] = 1/(1+math.exp(-input[i]))
        return activated

    def feedForwardNet2(self, input):
        net02 = np.dot(self.W2,input)
        return net02

    def error(self, input):
        error = 0
        error_total = 0
        error_list = []
        for i in range(0,self.nNeurons):
            error = .5*(self.target[i,0] - input[i,0])**2
            error_list.append(error)
            error_total += error
        return error_total, error_list

    def dnet_dwm(self, x,y,z):
        return x*y*z

    def update_Weights(self, dw1, dw2, dw3, dw4, dw5, dw6, dw7, dw8 ):
         updateL1 = np.matrix([[dw1, dw2, 0],[dw3, dw4, 0]])
         updateL2 = np.matrix([[dw5, dw6, 0],[dw7, dw8, 0]])
         self.W1 = self.W1 - self.LC*updateL1
         self.W2 = self.W2 - self.LC*updateL2



    def display_Weights(self, group, weight_list):
            precision = 11

            group['W1'].Clear()
            group['W1'].AppendText(str(self.W1[0,0])[2:precision + 2])
            group['W2'].Clear()
            group['W2'].AppendText(str(self.W1[0,1])[2:precision + 2])
            group['W3'].Clear()
            group['W3'].AppendText(str(self.W1[1,0])[2:precision + 2])
            group['W4'].Clear()
            group['W4'].AppendText(str(self.W1[1,1])[2:precision + 2])
            group['W5'].Clear()
            group['W5'].AppendText(str(self.W2[0,0])[1:precision])
            group['W6'].Clear()
            group['W6'].AppendText(str(self.W2[0,1])[1:precision])
            group['W7'].Clear()
            group['W7'].AppendText(str(self.W2[1,0])[1:precision])
            group['W8'].Clear()
            group['W8'].AppendText(str(self.W2[1,1])[1:precision])



    def calc_dWL2(self,out_h,dEdOut,dOdnet ):
        self.dW_L2 = np.empty([self.nNeurons,2])
        for b in range(0,self.nNeurons):
            for a in range(0,2):
                self.dW_L2[b,a] = out_h[a] * dEdOut[b] *dOdnet[b]
        return self.dW_L2

    def run(self, input ,display_groups, nTrain = 10000):

        display = display_groups[0]
        error_txt = display_groups[1]
        dw_weights = display_groups[2]
        weights = display_groups[3]

        W1 = self.W1
        W2 = self.W2

        for generation in range(1, nTrain):
            net_h = self.feedForwardNet1(input)
            out_h = self.activate(net_h)  ## net_h[0] is neth1
            netO1 = np.matrix([out_h[0], out_h[1], [.60]])
            netO2 = self.feedForwardNet2(netO1)
            out_O = self.activate(netO2)  # out2_1 -> out_O[0]
            error, error_list = self.error(out_O)
            dEdOut = self.dE_dout(out_O, self.target)
            dOdnet = self.dE_dnet(out_O)
            dWL2 = self.calc_dWL2(out_h, dEdOut, dOdnet)

            ##print('---------------Variablw to update w1------------------')

            D = out_h[0] * (1 - out_h[0])
            E = input[0, 0]
            I = out_h[0] * (1 - out_h[0])
            J = input[0, 0]
            #    for i in range(0, self.brain.nNeurons):
            A = dEdOut[0]
            B = dOdnet[0]
            C = W2[0, 0]
            F = dEdOut[1]
            G = dOdnet[1]
            H = W2[1, 0]

            dW1 = (A * B * C * D * E + F * G * H * I * J)
            new_W1 = W1[0, 0] - dW1
            I = D = out_h[0] * (1 - out_h[0])
            J = E = input[1, 0]

            A = dEdOut[0]
            B = dOdnet[0]
            C = W2[0, 0]
            F = dEdOut[1]
            G = dOdnet[1]
            H = W2[1, 0]

            dW2 = (A * B * C * D * E + F * G * H * I * J)
            new_W2 = W1[0, 1] - dW2
            I = D = out_h[1] * (1 - out_h[1])
            J = E = input[0, 0]  ## Input 1

            A = dEdOut[0]
            B = dOdnet[0]
            C = W2[0, 1]  ## W6
            F = dEdOut[1]
            G = dOdnet[1]
            H = W2[1, 1]  ## W8

            dW3 = (A * B * C * D * E + F * G * H * I * J)
            new_W3 = W1[1, 0] - dW3

            I = D = out_h[1] * (1 - out_h[1])
            J = E = input[1, 0]  ## Input 2

            A = dEdOut[0]
            B = dOdnet[0]
            C = W2[0, 1]  ## W6
            F = dEdOut[1]
            G = dOdnet[1]
            H = W2[1, 1]  ## W8

            dW4 = (A * B * C * D * E + F * G * H * I * J)
            new_W4 = W1[1, 1] - dW4

            ##print('---------------Variablw to update w4------------------')

            i = 0
            for key in display.iterkeys():
                display[key].Clear()
                display[key].AppendText(str(out_h[i])[1:9])
                i %= 2

            for key in dw_weights.iterkeys():
                dw_weights[key].Clear()
                dw_weights[key].AppendText(str(dW1[0])[1:9])

            weight_list = self.update_Weights(dW1, dW2, dW3, dW4, dWL2[0, 0], dWL2[0, 1], dWL2[1, 0], dWL2[1, 1])
            self.display_Weights(weights, weight_list)



            if (generation % 100 == 0):
                print(error)

    def pause(self):
        self.paused = True
        while self.paused:
            pass

app = wx.App()
controll = DisplayPanel('BackPropogator')
controll.Show()
app.MainLoop()












