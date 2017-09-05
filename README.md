# Weibull-Reliability
Software used for quick reliability calculations and analysis

Two python tools I made to help with testing needs.

*WeibullCalc.pyw:*
  
  UI below:
  
  ![Image of UI](Weibull-Reliability/Images/WeibullCalcPlot.png)
  
  Make sweet plots like this one:
  
  
  
  Inputs: 
  
    Number of samples, failure/suspension cycle counts
  
  Outputs: 
  
    estimated eta and beta for weibull fit, Bxx life, RxxCxx life, and a neat plot
  
  Uses MLE or Regression method.

*Reliability Test Planning Binomial Method.py:*
  
  Input: 
  
    reliability and confidence levels you would like to demonstrate.
  
  Output: 
  
    Number of samples required for testing.
  
  Optional Inputs include:
  
    lifetime test ratio for accelerated testing
    Expected Beta
    Expected number of failures
