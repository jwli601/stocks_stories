# -*- coding: gbk -*-

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.animation as animation

import tushare as ts
import time
import datetime
import akshare
plt.rcParams['font.sans-serif']=['SimHei'] 
plt.rcParams['axes.unicode_minus']=False 
import os
import akshare as ak
from jwli_tools import ols_v2

class cv_strategy:

    def __init__(self, stock_pool,):
        """
        stock_pool: 股票池，list，后续可用 xxx.stock_pool 来查看

        """
        
        self.stock_pool = stock_pool
        


    def get_close(self,date_start='',date_end='',autype_='qfq',ktype_='D'):
        """
        读取数据开始回测，可以选择输入回测的起止时间：
        date_start: 回测开始时间，string，如'2015-01-01'，默认为''
        date_end: 回测结束时间，string，如'2015-01-01'，默认为''
        注意date_start与，date_end 一旦填写则不能获取当天实时数据。
        
        返回值：
        close: 回测期间各标的收盘价
        returns：回测期间各标的的涨跌幅
        ma：回测期间各标的的64日移动平均值
        cv：回测期间各标的的64日移动变异系数
        cv_previous_date：上一个交易日的移动变异系数
        status：各标的所处的状态
        status_p：上一交易日各标的的状态
        """
        self.date_end = date_end
        self.date_start = date_start
        self.ktype=ktype_
        
        print(time.strftime('%Y-%m-%d-%H:%M:%S',time.localtime(time.time()-0*(24*60*60))))

        sh = ts.get_k_data('sh',start=self.date_start, end=self.date_end,ktype=self.ktype)
        self.close = pd.DataFrame(index=sh.date)
        for i in self.stock_pool:
            self.close[i] = ts.get_k_data(i,start=self.date_start, end=self.date_end,autype=autype_ ,ktype=self.ktype).set_index('date')['close']

        self.close=self.close.fillna(method='ffill')
        self.close = self.close#.dropna()
        
        

#         self.close.to_csv(r'./pool_1/close/close.csv')
    
    
    def run(self,operation_pct_in=0.5,operation_pct_out = 0.5,operation_pct_clr=1,period=64):
        """
        开始回测！可选择操作比例：
        operation_pct_in与operation_pct_out, 买卖的操作比例，默认为0.5，即买卖比例为“半仓”
        
        返回值：
        weight：回测期间各标的占净值的部分，注意不是百分比，而是所有weight求和等于净值。
        net_value: 回测期间基金净值
        var：回测期间每日涨跌幅度
        max_drawdown: 最大回撤
        """
#         self.close = pd.read_csv(r'./pool_1/close/close.csv',index_col='date')
        self.operation_pct_in = operation_pct_in
        self.operation_pct_out = operation_pct_out
        self.operation_pct_clr = operation_pct_clr
        self.period=period
        
        self.returns = self.close.pct_change()
        self.returns["cash"] = np.zeros(len(self.returns)) # 现金的收益率是0

        # stock_ma用来存股票池中相关股票的均值
        self.ma = self.close.rolling(self.period).mean().dropna()

        # stock_cv用来存变异系数，stock_cv_previous_date用来放前一天的cv，用来判断cv是在上升还是下降
        # cv: 变异系数 = 标准差/均值
        self.cv = (self.close.rolling(self.period).std()/self.close.rolling(self.period).mean()).dropna()
        self.stock_pool = self.cv.median().sort_values(ascending=False).index.to_list()
        
        self.cv_previous_date = self.cv.shift(1) #因为要比对昨天和今天的变异系数，所以把昨天的存在这里
        self.weight = pd.DataFrame(columns=self.stock_pool+['cash'],index = self.cv.index)
        self.trade_amount = pd.DataFrame(columns=['buy','sell'],index = self.cv.index)
        self.trade_record = pd.DataFrame(columns=self.stock_pool,index = self.cv.index)

        # 初始状态设置：10%的现金，其他的等比例分配
        self.weight.iloc[0] = [0.9/len(self.stock_pool)]*len(self.stock_pool)+[0.1]
        
        # stock_status用于判断该票目前处于什么状态，共分为上涨、下跌、反弹，回调四种
        self.status = pd.DataFrame(columns=self.stock_pool,index=self.close.index)
        for i in self.stock_pool:
            for j in self.ma.index:
                if self.close.loc[j,i]>self.ma.loc[j,i] and self.cv.loc[j,i]>self.cv_previous_date.loc[j,i]:
                    self.status.loc[j,i] = '上涨'
                elif self.close.loc[j,i]<self.ma.loc[j,i] and self.cv.loc[j,i]>self.cv_previous_date.loc[j,i]:
                    self.status.loc[j,i] = '下跌'
                elif self.close.loc[j,i]<self.ma.loc[j,i] and self.cv.loc[j,i]<self.cv_previous_date.loc[j,i]:
                    self.status.loc[j,i] = '反弹'
                elif self.close.loc[j,i]>self.ma.loc[j,i] and self.cv.loc[j,i]<self.cv_previous_date.loc[j,i]:
                    self.status.loc[j,i] = '回调'
        
        
        
        self.status_p = self.status.shift(1) # 因为要比对“状态的变化”，例如昨天是“反弹”，今天是“上涨”。所以要把昨天的状态记下来
    
        
        
        for i in self.weight.index[1:]:
            print(i) # i是日期

            self.weight.loc[i,:] = self.weight.shift(1).loc[i,:]*(1+self.returns.loc[i,:])

            #调仓部分

            d_cash_buy = 0
            d_cash_sell = 0
            for j in self.stock_pool:  
                #追涨部分
                if self.status.loc[i,j] =='上涨' and self.status_p.loc[i,j] != '上涨' and self.weight.shift(1).loc[i,"cash"]> -d_cash_buy:
                    
                    buy_amount = self.weight.shift(0).loc[i,"cash"]*self.operation_pct_in
                    self.weight.loc[i,j] = self.weight.loc[i,j] + buy_amount
                    d_cash_buy -= buy_amount
                    self.trade_record.loc[i,j] = 1
                    print("买——追涨：",j)

#                 # 逃顶部分    
                elif self.status.loc[i,j] != '上涨' and self.status_p.loc[i,j] == '上涨':
                    sell_amount = self.weight.shift(0).loc[i,j]*self.operation_pct_out
                    self.weight.loc[i,j] = self.weight.loc[i,j] - sell_amount
                    d_cash_sell += sell_amount
                    self.trade_record.loc[i,j] = -1

                    print("卖——逃顶：",j)

                #割肉部分    
                elif self.status.loc[i,j] =='下跌' and self.status_p.loc[i,j] != '下跌' and self.weight.loc[i,j]>0:
                    sell_amount = self.weight.shift(0).loc[i,j]*self.operation_pct_clr
                    self.weight.loc[i,j] = self.weight.loc[i,j] - sell_amount
                    self.trade_record.loc[i,j] = -1

                    d_cash_sell += sell_amount
                    print("卖——割肉：",j)

                else:
                    print("无操作:",j)
                    continue
            self.weight.loc[i,"cash"] = self.weight.shift(1).loc[i,"cash"] + d_cash_buy*1.0003 + d_cash_sell*0.9997
            self.trade_amount.loc[i,"buy"] = d_cash_buy
            self.trade_amount.loc[i,"sell"] = d_cash_sell

        self.net_value = self.weight.T.sum()
        self.var = self.net_value.pct_change().dropna()
        self.position = (self.weight.iloc[-1]/self.weight.iloc[-1].sum()).sort_values(ascending=False)
        self.result_today = pd.DataFrame({"仓位":(self.weight.iloc[-1]/self.weight.iloc[-1].sum()).sort_values(ascending=False),
                                          "今日涨幅":self.returns.iloc[-1]})


        # 计算最大回撤，偷懒抄的网上的代码
        def max_drawdown(x):
            i=np.argmax((np.maximum.accumulate(x)-x) / np.maximum.accumulate(x))
            if i == 0:
                return i
            j=np.argmax(x[:i])
            return (x[j]-x[i])/x[j],i,j
        self.max_drawdown = max_drawdown(self.net_value)
    def visualization(self,control_group='hs300',):
        self.control_group=control_group
        
        """
        该部分主要是可视化结果，会计算如下内容
        control_group: 选择对照组，默认为沪深300
        
        compare：回测结果与对照组的比较的结果，默认为沪深300
        
        """
        
        
        
        ###图1：各成分标的净值图
        l = len(self.stock_pool)
        fig = plt.figure(figsize=[20,12])
        plt.style.use('ggplot')
        plot_edge = round(len(self.stock_pool)**0.5)+1
        for i,j in enumerate(self.weight.columns):
            ax = plt.subplot(plot_edge,plot_edge,1+i)
            ax.plot(self.weight[j],lw=0.6)
            ax.set_xticks([])
            ax.set_title(j)
        fig.suptitle('各成分标的净值图')

        ###图2：相对沪深300走势图    
        
        plt.figure(figsize=[20,6],)

        hs300 = ts.get_k_data(self.control_group,start=self.date_start, end=self.date_end,ktype=self.ktype).set_index('date')
        hs300_ret = pd.DataFrame(hs300.close/hs300.close[0])
        hs300_ret.columns=[self.control_group]
        
        self.compare = pd.DataFrame(self.weight.T.sum(),columns=['strategy'])
        self.compare = self.compare.join(hs300_ret)
        
        self.compare = self.compare/self.compare.iloc[0]
        self.compare['hedge_with_{}'.format(self.control_group)] = self.compare.iloc[:,0]/self.compare[self.control_group]
        
        
        ax1=plt.subplot(121)
        
        for i in self.compare.columns:
#             self.compare[i].plot()
            ax1.plot(self.compare[i],label=i)
#         ax1.plot(self.weight['cash'],label='cash',color='gold')
        ax1.set_xticks(self.compare.index[::64])
        
        plt.hlines(y=[i for i in self.compare.iloc[-1]],xmin=self.compare.index[0],xmax=self.compare.index[-1],alpha=0.2)
        ax1.set_title(('策略收益与{}：绝对收益对比'.format(self.control_group)))
        ax1.legend()
        # ax1.set_xlim(stock_weight.index[-128],stock_weight.index[-1])


        ax2=plt.subplot(122)
        (self.compare['hedge_with_{}'.format(self.control_group)]).plot()
        ax2.set_title('策略收益/{}：相对收益走势'.format(self.control_group))
        plt.show()
        
        
        ###图3：策略涨跌分布图

        plt.figure(figsize=[10,6])
        plt.title('回测期间涨跌分布与分位数')
        a = plt.hist(self.var,40)
        h = a[0].max()
        hs = [h/8,h/4,h/2,h]
        p = np.percentile(self.var,[1,5,10,50])
        p_=['1%','5%','10%','50%']
        plt.vlines(x=p,ymin=0,ymax=hs,color='blue',lw=5)
        for i in range(4):
            plt.text(x=p[i],y=hs[i],s="{}:\n{}%".format(p_[i],round(100*p[i],2)),ha='center',va='center',fontsize=15)
        plt.show()
        print('近5日组合净值：\n{}'.format(self.net_value.tail()))
        print('近5日组合涨跌：\n{}'.format(self.var.tail()))
        print('今日持仓比例与涨跌幅：\n{}'.format(self.result_today.sort_values('仓位',ascending=False)))