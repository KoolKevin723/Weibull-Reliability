# -*- coding: utf-8 -*-
"""
Created on Fri Sep 05 11:10:32 2014
Calculates number of samples needed for testing given a target 
reliability and confidence

@author: z306905 (aka Kevin Nagle)

R = Reliability (target, ex. 90)
C = Confidence (target, ex. 50 or 90)
f = Number of failures allowed
        usually this is zero. It's useful to know how many samples
        you will have to run if you have an unexpected failure
r = test to lifetime ratio (1.5 means "we'll test each sample to 1.5 lives")
B = Weibull Beta value (assume one of these for accelerated life tests)
        
Based on this website (and every other reliability site/book ever written):
    http://reliabilityanalyticstoolkit.appspot.com/sample_size
"""
def F(R, C, f=0, r = 1.0, B = 2.5):
    from scipy import log
    from scipy.stats import chi2
    #this makes it work with RC#s of 90 or 0.90  
    if R > 1.0:
        R = R/100.0
    if C > 1.0:
        C = C/100.0
    #Handy lambda to round up number of samples
    round_up = lambda num: int(num + 1) if int(num) != num else int(num)
    #three different ways to calculate, depending on inputs
    if f == 0:
        if r != 1.0:
            numsamp = round_up(log(1-C)/(r**B*log(R))) #No failures and r!=1
        else:
            numsamp = log(1-C)/log(R) #No failures and r=1
        return round_up(numsamp)
    else:
        for i in range(int(f)):
            chi = chi2.isf(1-C, 2*f+2)
            return round_up((r * -chi) / (2 * log(R))) #Failures allowed