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
        stock_pool: ��Ʊ�أ�list���������� xxx.stock_pool ���鿴

        """
        
        self.stock_pool = stock_pool
        


    def get_close(self,date_start='',date_end='',autype_='qfq',ktype_='D'):
        """
        ��ȡ���ݿ�ʼ�ز⣬����ѡ������ز����ֹʱ�䣺
        date_start: �ز⿪ʼʱ�䣬string����'2015-01-01'��Ĭ��Ϊ''
        date_end: �ز����ʱ�䣬string����'2015-01-01'��Ĭ��Ϊ''
        ע��date_start�룬date_end һ����д���ܻ�ȡ����ʵʱ���ݡ�
        
        ����ֵ��
        close: �ز��ڼ��������̼�
        returns���ز��ڼ����ĵ��ǵ���
        ma���ز��ڼ����ĵ�64���ƶ�ƽ��ֵ
        cv���ز��ڼ����ĵ�64���ƶ�����ϵ��
        cv_previous_date����һ�������յ��ƶ�����ϵ��
        status�������������״̬
        status_p����һ�����ո���ĵ�״̬
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
        ��ʼ�ز⣡��ѡ�����������
        operation_pct_in��operation_pct_out, �����Ĳ���������Ĭ��Ϊ0.5������������Ϊ����֡�
        
        ����ֵ��
        weight���ز��ڼ�����ռ��ֵ�Ĳ��֣�ע�ⲻ�ǰٷֱȣ���������weight��͵��ھ�ֵ��
        net_value: �ز��ڼ����ֵ
        var���ز��ڼ�ÿ���ǵ�����
        max_drawdown: ���س�
        """
#         self.close = pd.read_csv(r'./pool_1/close/close.csv',index_col='date')
        self.operation_pct_in = operation_pct_in
        self.operation_pct_out = operation_pct_out
        self.operation_pct_clr = operation_pct_clr
        self.period=period
        
        self.returns = self.close.pct_change()
        self.returns["cash"] = np.zeros(len(self.returns)) # �ֽ����������0

        # stock_ma�������Ʊ������ع�Ʊ�ľ�ֵ
        self.ma = self.close.rolling(self.period).mean().dropna()

        # stock_cv���������ϵ����stock_cv_previous_date������ǰһ���cv�������ж�cv�������������½�
        # cv: ����ϵ�� = ��׼��/��ֵ
        self.cv = (self.close.rolling(self.period).std()/self.close.rolling(self.period).mean()).dropna()
        self.stock_pool = self.cv.median().sort_values(ascending=False).index.to_list()
        
        self.cv_previous_date = self.cv.shift(1) #��ΪҪ�ȶ�����ͽ���ı���ϵ�������԰�����Ĵ�������
        self.weight = pd.DataFrame(columns=self.stock_pool+['cash'],index = self.cv.index)
        self.trade_amount = pd.DataFrame(columns=['buy','sell'],index = self.cv.index)
        self.trade_record = pd.DataFrame(columns=self.stock_pool,index = self.cv.index)

        # ��ʼ״̬���ã�10%���ֽ������ĵȱ�������
        self.weight.iloc[0] = [0.9/len(self.stock_pool)]*len(self.stock_pool)+[0.1]
        
        # stock_status�����жϸ�ƱĿǰ����ʲô״̬������Ϊ���ǡ��µ����������ص�����
        self.status = pd.DataFrame(columns=self.stock_pool,index=self.close.index)
        for i in self.stock_pool:
            for j in self.ma.index:
                if self.close.loc[j,i]>self.ma.loc[j,i] and self.cv.loc[j,i]>self.cv_previous_date.loc[j,i]:
                    self.status.loc[j,i] = '����'
                elif self.close.loc[j,i]<self.ma.loc[j,i] and self.cv.loc[j,i]>self.cv_previous_date.loc[j,i]:
                    self.status.loc[j,i] = '�µ�'
                elif self.close.loc[j,i]<self.ma.loc[j,i] and self.cv.loc[j,i]<self.cv_previous_date.loc[j,i]:
                    self.status.loc[j,i] = '����'
                elif self.close.loc[j,i]>self.ma.loc[j,i] and self.cv.loc[j,i]<self.cv_previous_date.loc[j,i]:
                    self.status.loc[j,i] = '�ص�'
        
        
        
        self.status_p = self.status.shift(1) # ��ΪҪ�ȶԡ�״̬�ı仯�������������ǡ��������������ǡ����ǡ�������Ҫ�������״̬������
    
        
        
        for i in self.weight.index[1:]:
            print(i) # i������

            self.weight.loc[i,:] = self.weight.shift(1).loc[i,:]*(1+self.returns.loc[i,:])

            #���ֲ���

            d_cash_buy = 0
            d_cash_sell = 0
            for j in self.stock_pool:  
                #׷�ǲ���
                if self.status.loc[i,j] =='����' and self.status_p.loc[i,j] != '����' and self.weight.shift(1).loc[i,"cash"]> -d_cash_buy:
                    
                    buy_amount = self.weight.shift(0).loc[i,"cash"]*self.operation_pct_in
                    self.weight.loc[i,j] = self.weight.loc[i,j] + buy_amount
                    d_cash_buy -= buy_amount
                    self.trade_record.loc[i,j] = 1
                    print("�򡪡�׷�ǣ�",j)

#                 # �Ӷ�����    
                elif self.status.loc[i,j] != '����' and self.status_p.loc[i,j] == '����':
                    sell_amount = self.weight.shift(0).loc[i,j]*self.operation_pct_out
                    self.weight.loc[i,j] = self.weight.loc[i,j] - sell_amount
                    d_cash_sell += sell_amount
                    self.trade_record.loc[i,j] = -1

                    print("�������Ӷ���",j)

                #���ⲿ��    
                elif self.status.loc[i,j] =='�µ�' and self.status_p.loc[i,j] != '�µ�' and self.weight.loc[i,j]>0:
                    sell_amount = self.weight.shift(0).loc[i,j]*self.operation_pct_clr
                    self.weight.loc[i,j] = self.weight.loc[i,j] - sell_amount
                    self.trade_record.loc[i,j] = -1

                    d_cash_sell += sell_amount
                    print("���������⣺",j)

                else:
                    print("�޲���:",j)
                    continue
            self.weight.loc[i,"cash"] = self.weight.shift(1).loc[i,"cash"] + d_cash_buy*1.0003 + d_cash_sell*0.9997
            self.trade_amount.loc[i,"buy"] = d_cash_buy
            self.trade_amount.loc[i,"sell"] = d_cash_sell

        self.net_value = self.weight.T.sum()
        self.var = self.net_value.pct_change().dropna()
        self.position = (self.weight.iloc[-1]/self.weight.iloc[-1].sum()).sort_values(ascending=False)
        self.result_today = pd.DataFrame({"��λ":(self.weight.iloc[-1]/self.weight.iloc[-1].sum()).sort_values(ascending=False),
                                          "�����Ƿ�":self.returns.iloc[-1]})


        # �������س���͵���������ϵĴ���
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
        �ò�����Ҫ�ǿ��ӻ�������������������
        control_group: ѡ������飬Ĭ��Ϊ����300
        
        compare���ز����������ıȽϵĽ����Ĭ��Ϊ����300
        
        """
        
        
        
        ###ͼ1�����ɷֱ�ľ�ֵͼ
        l = len(self.stock_pool)
        fig = plt.figure(figsize=[20,12])
        plt.style.use('ggplot')
        plot_edge = round(len(self.stock_pool)**0.5)+1
        for i,j in enumerate(self.weight.columns):
            ax = plt.subplot(plot_edge,plot_edge,1+i)
            ax.plot(self.weight[j],lw=0.6)
            ax.set_xticks([])
            ax.set_title(j)
        fig.suptitle('���ɷֱ�ľ�ֵͼ')

        ###ͼ2����Ի���300����ͼ    
        
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
        ax1.set_title(('����������{}����������Ա�'.format(self.control_group)))
        ax1.legend()
        # ax1.set_xlim(stock_weight.index[-128],stock_weight.index[-1])


        ax2=plt.subplot(122)
        (self.compare['hedge_with_{}'.format(self.control_group)]).plot()
        ax2.set_title('��������/{}�������������'.format(self.control_group))
        plt.show()
        
        
        ###ͼ3�������ǵ��ֲ�ͼ

        plt.figure(figsize=[10,6])
        plt.title('�ز��ڼ��ǵ��ֲ����λ��')
        a = plt.hist(self.var,40)
        h = a[0].max()
        hs = [h/8,h/4,h/2,h]
        p = np.percentile(self.var,[1,5,10,50])
        p_=['1%','5%','10%','50%']
        plt.vlines(x=p,ymin=0,ymax=hs,color='blue',lw=5)
        for i in range(4):
            plt.text(x=p[i],y=hs[i],s="{}:\n{}%".format(p_[i],round(100*p[i],2)),ha='center',va='center',fontsize=15)
        plt.show()
        print('��5����Ͼ�ֵ��\n{}'.format(self.net_value.tail()))
        print('��5������ǵ���\n{}'.format(self.var.tail()))
        print('���ճֱֲ������ǵ�����\n{}'.format(self.result_today.sort_values('��λ',ascending=False)))