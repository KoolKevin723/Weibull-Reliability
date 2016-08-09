# -*- coding: utf-8 -*-
"""
Created on Thu Oct 03 10:27:29 2013
Super Fun Weibull Calculator
@author: Kevin Nagle
"""

from sys import argv, exit
from PyQt4 import QtGui
from numpy import linspace
from scipy import log, exp
from scipy.stats import linregress
#from scipy.stats import weibull_min
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt

class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):        
        #Building the layout        
        self.NS = QtGui.QSpinBox(self)
        self.NS.setValue(16)
        self.NS.setMaximum(16)
        self.NumberofSamples = self.NS.value()
        self.NS.setFixedWidth(50)
        self.NS.move(0, 20)
        self.NS.valueChanged.connect(self.Change)
        
        Nums = QtGui.QLabel('Number of Samples',self)
        Nums.move(0, 0)
        
        Suspended = QtGui.QLabel('Suspended?',self)
        Suspended.move(80, 50)
        
        Cycles = QtGui.QLabel("Cycles", self)
        Cycles.move(0, 50)  
        
        self.ParamsButton = QtGui.QPushButton("Calculate Weibull Parameters",self)
        self.ParamsButton.move(175, 50)
        self.ParamsButton.setFixedWidth(170)
        self.ParamsButton.clicked.connect(self.Calc)
        
        self.MLEbutton = QtGui.QRadioButton(self)
        self.MLEbutton.move(190, 25)
        self.MLElabel = QtGui.QLabel("MLE Method", self)
        self.MLElabel.setToolTip("Maximum Likelihood Estimation: Use this one if you have few samples and/or many suspensions")
        self.MLElabel.move(175,0)
        
        self.LSQbutton = QtGui.QRadioButton(self)
        self.LSQbutton.move(290, 25)
        self.LSQlabel = QtGui.QLabel("LSQ Method (Standard)", self)
        self.LSQlabel.setToolTip("Least Square Estimation (Regression on X): The Standard; Use this one with decent samples sizes and no suspensions")
        self.LSQlabel.move(275,0)
        
        self.BetaLabel = QtGui.QLabel("Beta = ",self)
        self.BetaLabel.setFixedWidth(100)
        self.BetaLabel.move(175, 75)
        
        self.etaLabel = QtGui.QLabel("eta = ",self)
        self.etaLabel.setFixedWidth(100)
        self.etaLabel.move(275, 75)
        
        self.RLabel = QtGui.QLabel("This box returns Bx life. \nFor B10 life enter 10.  \nAlso note B10 == Reliability of 90", self)
        self.RLabel.move(175,100)
        self.RLabel.hide()
        
        self.Rbox = QtGui.QSpinBox(self)
        self.Rbox.move(175, 140)
        self.Rbox.setMaximum(99)
        self.Rbox.setFixedWidth(50)
        self.Rbox.hide()
        self.Rbox.valueChanged.connect(self.Blife)
        
        self.rlabel = QtGui.QLabel(" -- ", self)
        self.rlabel.setFixedWidth(100)
        self.rlabel.move(175, 160 )
        self.rlabel.hide() 
        
        self.bplot = QtGui.QCheckBox(self)
        self.bplot.move(260, 147)
        self.bplot.hide()
        self.bplotlabel = QtGui.QLabel("Check to plot B-Life",self)
        self.bplotlabel.move(275, 147)
        self.bplotlabel.hide()
        
        #Confidence Limits
        self.CLabel = QtGui.QLabel("This box applies confidence intervals. \nEnter two-sided value (between 65 and 99).  \nEntering 90 will return the 5% lower bound", self)
        self.CLabel.move(175,180)
        self.CLabel.hide()
        
        self.Cbox = QtGui.QSpinBox(self)
        self.Cbox.move(175, 220)
        self.Cbox.setMaximum(99)
        self.Cbox.setMinimum(65)
        self.Cbox.setValue(90)
        self.Cbox.setFixedWidth(50)
        self.Cbox.hide()
        self.Cbox.valueChanged.connect(self.Confidence)
        
        self.clabel = QtGui.QLabel(" -- ", self)
        self.clabel.setFixedWidth(100)
        self.clabel.move(175, 240 )
        self.clabel.hide()
        
        #Plot Stuff
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.PlotButton = QtGui.QPushButton("Plot",self)
        self.PlotButton.move(175, 280)
        self.PlotButton.hide()
        self.toolbar = NavigationToolbar(self.canvas, self.canvas)
        self.toolbar.show()
        
        self.PlotButton.clicked.connect(self.Plot)
        
        #This is to build all the cycle boxes and suspension checks
        self.S = []
        self.C = []
        for i in range(16):
            self.C.append(QtGui.QDoubleSpinBox(self))
            self.C[i].setMaximum(100000000)
            self.C[i].move(0, (i+3.5)*20)
            self.S.append(QtGui.QCheckBox(self))
            self.S[i].move(100, (i+3.5)*20)       
        
        #some bullshit
        self.setWindowTitle('Weibull Calc')
        icon = QtGui.QIcon('ZF RGB_1.jpg')
        self.setWindowIcon(icon)
        self.show()
                
    def Change(self,value):
        #show or hide samples based on number of samples spinbox
        if value < self.NumberofSamples:
            for i in range(self.NumberofSamples - value):
                self.C[self.NumberofSamples - i - 1].hide()
                self.S[self.NumberofSamples - i - 1].hide()
            self.NumberofSamples = value
        if value > self.NumberofSamples:
            for i in range(value - self.NumberofSamples):
                self.C[i + self.NumberofSamples].show()
                self.S[i + self.NumberofSamples].show()
            self.NumberofSamples = value
        
    def Calc(self):
        #Calculates the Weibull parameters
        c = [] #cycles and suspended or not
        for i in range(self.NumberofSamples):
            c.append((self.C[i].value(), self.S[i].isChecked()))
        c.sort()
        self.cycles = [x[0] for x in c]
        self.fail = [x[1] for x in c]
        n = self.NumberofSamples
        rank = linspace(1, len(c),len(c))
        self.pp = [] #Unreliability plotting position
        self.y = [] #used for regression
        self.x = [] #used for regression
        self.cx = [] #cycle counts of failed samples only
        #Median Rank Stuff
        self.nf = 0.0
        im = 0.0
        nfs = -1
        for i in range(n):
            if not self.fail[i]:
                nfs += 1
                N = ((n+1.0) - im)/(1.0+(n-(rank[i]-1.0)))
                im = im + N
                r = (im - 0.3)/(n + 0.4)
                self.nf += 1
                self.pp.append(r)
                self.y.append(log(-log(1-self.pp[nfs])))
                self.x.append(log(self.cycles[i]))
                self.cx.append(self.cycles[i])
        self.reg = linregress(self.y, self.x)

        #Find b and eta
        #LSQ Method (Assuming scatter in the x direction because Waloddi said to)
        if self.LSQbutton.isChecked():
            self.b = 1.0/self.reg[0]            
            self.eta = exp(self.reg[1]/(self.reg[0]*self.b))            
            self.r = self.reg[2]
        
        #Find b and eta 
        #MLE Method, using method from Abernethy Appendix C  
        if self.MLEbutton.isChecked():
            from scipy.optimize import fsolve           
            def eq(Bhat):
                num, denom, mult, eta = 0.0, 0.0, 0.0, 0.0
                for i in range(self.NumberofSamples):
                    num = num + self.cycles[i]**Bhat * log(self.cycles[i])
                    denom = denom + self.cycles[i]**Bhat
                    if not self.fail[i]:
                        mult = mult + log(self.cycles[i]) 
                return num / denom - (1.0/self.nf) * mult - 1.0/Bhat
            x = float(fsolve(eq, 0.5))
            self.b = x
            eta = 0.0
            for i in range(self.NumberofSamples):
                eta = eta + self.cycles[i]**self.b
            self.eta = (eta / self.nf) ** (1.0 / self.b)
        
        #Show Beta and eta values, also show the plot button
        shortb = "%.2f" % self.b
        shorteta = "%.2f" % self.eta
        self.BetaLabel.setText("Beta = "+ str(shortb))
        self.etaLabel.setText("eta = "+ str(shorteta))
        self.rlabel.show()
        self.Rbox.show()
        self.RLabel.show()
        self.Rbox.setValue(10)
        self.clabel.show()
        self.Cbox.show()
        self.CLabel.show()
        self.PlotButton.show()
        self.bplot.show()
        self.bplotlabel.show()
        
    def Blife(self,R):
        #B Lives!!!
        from scipy import log
        self.blife = self.eta * (-log((100-R)/100.0))**(1/self.b)
        shortr = "%.2f" % self.blife
        self.rlabel.setText(str(shortr) + " Cycles")
        
    def Confidence(self,C):
        #Confidence Interval!!!
        #Calculate Bxx life (if confidence input is 90%, just report 5% value, the lower bound)
        #for now do Monte Carlo bounds, later do pivotal bounds
        from scipy import log
        from scipy.stats import weibull_min
        from scipy.stats import scoreatpercentile
        rv = weibull_min.rvs
        CL = ((100 - C) / 2.0) / 100.0
        #Get a bunch of sets of weibull data using calculated beta and eta 
        x = []
        y = []
        blives = [] #blives from Bxx spinbox value (default B10)
        tempbxxlives = []
        self.bxxlives = []
        self.sortedblives = []
        self.clvalues = []
        self.percentiles = range(1, 100, 1)
        self.percentiles = [0.01* i for i in self.percentiles]
        d = range(1, self.NumberofSamples + 1)
        r = [(i - 0.3) / (self.NumberofSamples + 0.4) for i in d]
        y = [log(-log(1-i)) for i in r]
        for i in range(2500):
            x.append(rv(self.b, scale=self.eta, size = self.NumberofSamples))
            x[i].sort()
        #Calculate beta and eta for each simulated data set
        for i in range(len(x)):
            be = linregress(y, log(x[i]))
            tempbeta = 1.0 / be[0]
            tempeta = exp(be[1] / (be[0] * tempbeta))
            #also calculate Bxx life
            tempblife = tempeta * (-log((100-self.Rbox.value())/100.0))**(1/tempbeta)
            blives.append(tempblife)
            #Get Bxx life for every percentile (B10 - B99)
            tempbxxlives = []
            for j in range(len(self.percentiles)):
                tempbxxlives.append(tempeta * (-log((100-self.percentiles[j]*100.0)/100.0))**(1/tempbeta))
            self.bxxlives.append(tempbxxlives)
        #Get blife at desired confidence level (lower bound)
        LBt = scoreatpercentile(blives, CL*100) #add the 100 - before CL for upper bound, then do B99
        #All levels of blives for plot
        for i in range(len(self.percentiles)):
            self.sortedblives.append([row[i] for row in self.bxxlives])            
            self.clvalues.append(scoreatpercentile(self.sortedblives[i], CL*100))
        #Write to label
        self.shortLBt = "%.2f" % LBt
        self.clabel.setText(str(self.shortLBt) + " Cycles")
            
        #some pivotal code (better method, but more confusing)
        '''wp = log(log(1.0 / (1.0 - C / 100.0)))
        bhat = [1.0 / i[:][0] for i in pbe]
        uhat = [log(i[:][1]) for i in pbe]
        Z = (uhat - wp) / bhat
        LBy = log(self.eta) - scoreatpercentile(Z, CL*100) / self.b
        LBt = exp(LBy)'''

    def Plot(self):
        #Let's make a plot!
        from matplotlib.ticker import FuncFormatter
        from scipy.stats import weibull_min
        rv = weibull_min.rvs
        ax = self.figure.add_subplot(111)
        self.canvas.showNormal()        
        self.canvas.activateWindow()
        ax.cla()
        #First plot failed samples
        ax.semilogx(self.cx, self.y, 'o', color = "orange") 
        #Labels
        ax.set_title("Occurrence Cumulative Density Function")
        ax.set_xlabel("Cycles")
        ax.set_ylabel("Unreliability")
        ax.set_xscale('log')
        ax.set_ylim(-4.60015,1.5271796)
        #Grab some x values that should fall in our distribution
        x = rv(self.b, scale = self.eta, size=100)
        x.sort()   
        #Get y values using all created x values
        F = 1.0 - exp(-(x/self.eta)**self.b)
        y = log(-log(1 - F))
        #Plot and Legend
        ax.plot(x,y, label="beta= %.2f\neta = %.0f" % (self.b, self.eta) )
        
         #Confidence Plot
        cy = [log(-log(1- i)) for i in self.percentiles]
        ax.plot(self.clvalues, cy)
        
        #Add B-Life to plot
        if self.bplot.isChecked():
            ax.plot(self.shortLBt,log(-log(1-(self.Rbox.value()/100.0))), '+', ms=20, mew=2.5,color = "#98FB98", label = "B%.0f-Life = %.0f" % (self.Rbox.value(), float(self.shortLBt )))
            plt.legend(loc='lower right', numpoints = 1)

       
        #Formatting function for the y-axis
        def weibull_CDF(ys, pos):
            return "%.2f"  % (1-exp(-exp(ys)))
        formatter = FuncFormatter(weibull_CDF)
        ax.yaxis.set_major_formatter(formatter)
        yt_F = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5,
           0.6, 0.7, 0.8, 0.9, 0.95, 0.99]
        yt_lnF = [log( -log(1-i)) for i in yt_F]
        ax.set_yticks(yt_lnF)
        ax.yaxis.grid()
        ax.xaxis.grid(which='both')
        
        self.canvas.draw()
        
def main():
    
    app = QtGui.QApplication(argv)
    ex = Example()
    exit(app.exec_())

if __name__ == '__main__':
    main()