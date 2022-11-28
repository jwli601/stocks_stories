# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import akshare as ak # akshare 用来读取当日当时的数据，akshare如果用来读历史数据经常会出现数据丢失现象，不好用
import tushare as ts
import datetime
import cv_strategy


def sw_heatmap():
    date_today = str(datetime.date.today())

    sw_1st_info = ak.sw_index_first_info()
    sw_1st_list = [i[:6]for i in sw_1st_info['行业代码']]
    sw_data = pd.DataFrame(columns=sw_1st_list)
    for i in sw_1st_list:
        sw_data[i] = ak.index_hist_sw(i).set_index('日期')['收盘']

    sw_today = ak.index_realtime_sw('一级行业').set_index('指数代码')
    sw_data.loc[date_today,:] = sw_today['最新价']
    sw_data.columns = sw_1st_info['行业名称']
    sw_data.dropna(inplace=True)
    sw_data_v = ((sw_data-sw_data.rolling(50).mean())/(sw_data.rolling(50).std())).dropna()
    sw_data_v = sw_data_v.T
    sw_data_v.sort_values(date_today,inplace=True)

    fig = plt.figure(figsize=[15,3],dpi=150,facecolor='white')
    plt.style.use('bmh')
    ax = plt.subplot()
    ax.yaxis.set_ticks_position('right')

    ax.imshow(sw_data_v, cmap=plt.cm.PiYG_r, vmin = -3, vmax=3)
    ax.set_xticks(np.arange(len(sw_data_v.columns)))
    ax.set_xticklabels(sw_data_v.columns, rotation=90,fontsize=6)

    ax.set_yticks(np.arange(len(sw_data_v.index)))
    ax.set_yticklabels(sw_data_v.index, rotation=0,fontsize=6)
    # plt.yticks(sw_data_v.columns)
    plt.show()
    
def zh_us_interests_diff(start_date=''):

    hs300 = ts.get_k_data('hs300',start=start_date).set_index('date')
    sz50 = ts.get_k_data('sz50',start=start_date).set_index('date')
    zz500 = ts.get_k_data('399905',start=start_date).set_index('date')
    bond_table = ak.bond_zh_us_rate()
    bond_table.set_index('日期',inplace=True)
    bond_table.index = [str(i) for i in bond_table.index]
    bond_table['中美利差_10Y'] = bond_table['中国国债收益率10年']-bond_table['美国国债收益率10年']
    zmlc_10Y = bond_table['中美利差_10Y'].dropna()
    df1 = pd.DataFrame({'z':zmlc_10Y,'sz50':sz50.close,'hs300':hs300.close,'zz500':zz500.close})
    df1.dropna(inplace=True)
    df1['sz50_shift100'] = df1.sz50.shift(-100)

    corr = df1.corr().loc['z','sz50']
    corr2 = df1.corr().loc['z','sz50_shift100']

    df1_1 = (df1-df1.mean())/df1.std()
    plt.figure(figsize=[10,6],dpi=100)
    plt.style.use('ggplot')
    plt.title('中美利差与上证50指数走势 corr = {}'.format(round(corr,3)))


    plt.plot(df1_1.z,color='red',label='中美利差')
    plt.plot(df1_1.sz50,color='blue',alpha=0.2,label='上证50\n  corr={}'.format(round(corr,3)))
    plt.plot(df1_1.sz50.shift(-100),color='blue',label='sz50_shift_100\n  corr={}'.format(round(corr2,3)))

    plt.legend()
    plt.xticks(df1.index[::20],rotation=90,fontsize=8)
    plt.ylabel('纵轴经标准化',color='grey')
    plt.show()
    
    return df1
def stock_bond_rolling(start_date=''):
    bond_index = ak.stock_zh_index_daily(symbol = 'sh000012').set_index('date')
    bond_index.index = [str(i) for i in bond_index.index]
    df = pd.DataFrame(columns=['sz50','bond_index'])
    df.sz50 = ts.get_k_data('sz50',start=start_date).set_index('date')['close']
    df.bond_index = bond_index.close
    df_roc = (df/df.shift(240)).dropna()
    df_rocz = (df_roc-df_roc.mean())/(df_roc.std())
    fig=plt.figure(figsize=[10,5],dpi=80)
    plt.plot(df_rocz.bond_index,label='bond_index_return240',color='red')
    plt.plot(df_rocz.sz50,label='sz50_return240',color='blue')

    plt.xticks(df_rocz.index[::20],rotation=90)
    plt.legend()
    plt.title('股债轮动模型 corr = {}'.format(round(df_rocz.corr().loc['sz50','bond_index'],3)))
    plt.show()
    return df
def sz50_over_zz500(start_date = ''):
    sz50 = ts.get_k_data('sz50',start=start_date).set_index('date')
    zz500=ts.get_k_data('399905',start=start_date).set_index('date')
    df = pd.DataFrame({'sz50':sz50.close, 'zz500':zz500.close}).dropna()
    df['sz50/zz500'] = df.sz50/df.zz500
    df = df/df.iloc[0]

    plt.figure(figsize=[8,5],dpi=80)
    plt.plot(df.sz50,alpha=.4,label='上证50')
    plt.plot(df.zz500,alpha=.4,label='中证500')
    # plt.plot(df['sz50/zz500'],color='green',label='上证50/中证500')
    plt.xticks(df.index[::60],rotation=90)
    plt.title('规模效应：上证50/中证500')
    plt.legend()
    plt.show()

    plt.figure(figsize=[8,5],dpi=80)
    # plt.plot(df.sz50,alpha=.4,label='上证50')
    # plt.plot(df.zz500,alpha=.4,label='中证500')
    plt.plot(df['sz50/zz500'],color='green',label='上证50/中证500')
    plt.xticks(df.index[::60],rotation=90)
    plt.title('规模效应：上证50/中证500')
    plt.legend()
    plt.show()
    
def hs300_streamline():
    hs300_list = pd.read_excel(r'D:\jwli\stocks_stories\hs300.xlsx',sheet_name=1).dropna()
    hs300_list = [i[:6] for i in hs300_list['证券代码']]
    hs300_pool = cv_strategy.cv_strategy(hs300_list)
    hs300_pool.get_close()
    area = hs300_pool.close
    prd = 50
    cv = area.rolling(prd).std()/area.rolling(prd).mean()
    cv.dropna(inplace=True)
    cv = cv.iloc[1:]
    rtn = area/area.shift(prd)
    rtn.dropna(inplace=True)
    rtn = rtn.applymap(lambda x:np.log(x))
    # fig = plt.figure(figsize=[10,10],dpi=80)
    # ax1 = plt.subplot()
    # # ax1.scatter(x = cv.iloc[-1],y = rtn.iloc[-1],alpha=.6,marker='o')
    # # ax1.scatter(x = cv.iloc[-2],y = rtn.iloc[-2],alpha=.6,marker='o')
    # for i in range(len(cv.iloc[-1])):
    #     ax1.arrow(x=cv.iloc[-2,i], y=rtn.iloc[-2,i], dx = cv.iloc[-1,i]-cv.iloc[-2,i],dy = rtn.iloc[-1,i]-rtn.iloc[-2,i],
    #               length_includes_head=True,width=0.0005,head_width=0.003)
    # plt.scatter(x2,np.log(y2),alpha=0.2)
    dcv = cv-cv.shift(1)
    dcv.dropna(inplace=True)
    # dcv = dcv.iloc[1:]
    drtn=rtn-rtn.shift(1)
    drtn.dropna(inplace=True)
    vel = pd.DataFrame(columns=dcv.columns,index=dcv.index)
    for i in range(len(dcv.columns)):
        for j in range(len(dcv.index)):
            if dcv.iloc[j,i]>0 and drtn.iloc[j,i]>0:
                vel.iloc[j,i] = 1
            elif dcv.iloc[j,i]<0 and drtn.iloc[j,i]>0:
                vel.iloc[j,i] = 2
            elif dcv.iloc[j,i]<0 and drtn.iloc[j,i]<0:
                vel.iloc[j,i] = 3
            elif dcv.iloc[j,i]>0 and drtn.iloc[j,i]<0:
                vel.iloc[j,i] = 4


    # aset = cv.iloc[-1][cv.iloc[-1]>0].index.to_list()
    # bset = rtn.iloc[-1][rtn.iloc[-1]>0].index.to_list()
    # area_1 = [i for i in aset if i in bset]
    # x = cv.iloc[-1][area_1]
    # y = rtn.iloc[-1][area_1]
    # plt.scatter(x=x,y=y)
    fig=plt.figure(figsize=[10,10],dpi=100)
    fig.suptitle('沪深300成分股鱼群图')
    colors = ['red','orange','orange','green']
    for j in range(1,5):
        a1 = (vel.iloc[-1][vel.iloc[-1]==j]).index
        a1x=cv[a1].iloc[-2]
        a1y=rtn[a1].iloc[-2]
        a1dx=dcv[a1].iloc[-1]
        a1dy=drtn[a1].iloc[-1]
        for i in range(len(a1)):
            ax=plt.subplot(2,2,j)
            ax.set_xlim(0,.2)
            ax.set_ylim(-.5,.5)
            ax.arrow(x=a1x[i],y=a1y[i],dx=a1dx[i],dy=a1dy[i],width=0.0005,head_width=0.005,color=colors[j-1])
            ax.set_title('向第{}象限移动:{}只'.format(j,len(a1)))
def run_all():
    sw_heatmap()
    zh_us_interests_diff()
    stock_bond_rolling()
    hs300_streamline()