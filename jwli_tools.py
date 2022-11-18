import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def ols_v2(x,y,n=1):
    A=x**n
    for i in range(n-1,-1,-1):
        A_temp = x**i
        A=np.vstack((A,A_temp))
    A=A.T
    ATA=A.T.dot(A)
    abc=np.linalg.inv(ATA).dot(A.T).dot(y)#高次的系数在前，如ax**2 +bx**1+cx**0
    #画图
    x_p=np.linspace(min(x),max(x),100)
    y_p=np.zeros_like(x_p)
    for i in range(n+1):
        y_p+=abc[i]*(x_p**(n-i))
    
    plt.plot(x_p,y_p)
    plt.scatter(x,y,s=5)
    return abc

def zscore(x):
    return (x-x.mean())/x.std()

def Bll(df,ndays=64,N=1,plot_area=512,title=""):
    dft = df.copy()
    mean = dft.rolling(64).mean()
    std = dft.rolling(64).std()
    dft['mean'] = mean
    dft['std'] = std
    dft['upper'] = mean+N*std
    dft['lower'] = mean-N*std
    dft['upper_2times'] = mean+2*N*std
    dft['lower_2times'] = mean-2*N*std
    dft['d_upper'] = dft.upper_2times - dft.upper_2times.shift(1)
    dft['d_lower'] = dft.lower_2times-dft.lower_2times.shift(1)
    dft['byxs'] = std/mean
    dft['d_byxs'] = dft.byxs-dft.byxs.shift(1)
    dft['pos'] = (df-mean)/std
    
    fig = plt.figure(figsize=[10,10],dpi=150)
    ax1 = plt.subplot(411)
    ax1.plot(df)
    
    ax1.plot(dft['mean'])
    ax1.plot(dft.upper,lw=0.5,color='grey',)
    ax1.plot(dft.lower,lw=0.5,color='grey',)
    ax1.plot(dft.upper_2times,lw=0.5,color='lightgrey',ls='--')
    ax1.plot(dft.lower_2times,lw=0.5,color='lightgrey',ls='--')

    
    ax2 = plt.subplot(412,sharex=ax1)
    ax2_ = plt.twinx(ax2)
    ax2.set_ylabel('2times_upper')
    ax2_.set_ylabel('d_2times_upper(red)')

    
    ax2.plot(dft.upper)
    ax2_.plot(dft.d_upper,color='red',ls='--')
    ax2_.hlines(xmin=0,xmax=len(df),y=0,color='grey',alpha=0.4)
        
    ax3 = plt.subplot(413,sharex=ax1)
    ax3_ = plt.twinx(ax3)
    ax3.plot(dft.lower)
    ax3_.plot(dft.d_lower,color='red',ls='--')
    ax3_.hlines(xmin=0,xmax=len(df),y=0,color='grey',alpha=0.4)
    ax3.set_ylabel('2times_lower')
    ax3_.set_ylabel('d_2times_lower(red)')
    
    ax4 = plt.subplot(414,sharex=ax1)
    ax4.plot(dft.byxs)
    ax4_ = plt.twinx(ax4)
    ax4_.plot(dft.d_byxs,color='red',ls='--')
    ax4_.hlines(xmin=0,xmax=len(df),y=0,color='grey',alpha=0.4)

    
    start_date = len(df)-plot_area
    end_date = len(df)
    ax1.set_xlim(start_date,end_date)
    
    
    fig.subplots_adjust(hspace=0)
    fig.suptitle(title)

    return dft


