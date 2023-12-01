# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 09:20:23 2022

@author: GMJJB
"""

import cv_strategy
import dingpan_plots
import pandas as pd
import tushare as ts
import numpy as np
import matplotlib.pyplot as plt

# ETF持仓
pool_1=['512660','512800',# 军工、银行
        '513180','515220',# 恒生科技、煤炭
        '159996','512010',# 家电、医药
        '159825','159865',# 农业、养殖
        '159732','159995',# 消费电子、芯片
        '518880','501018',# 黄金、原油
        '159766','512690',# 旅游，酒
        '515700','515790',# 新能车、光伏
        '159985',#'511260',# 豆粕期货，十年国债ETF
        '159941', '513030',#'513080',#'513880',#,         # nasdaq,德国，法国cac40，日本225 
        '512980','512720',         # 传媒, 计算机
        '513360','159611',                  # 教育,电力
#        '515880',          # 通讯  
#       '563000','510300','510500',# 中国A50，hs300, zz500
       ]


#%%
s = a.close.corr()

for i in s.columns:
    print(i)
    print(np.percentile(s[i],[10,90]))
#%%
am = cv_strategy.cv_strategy(pool_1)
am.get_close(ktype_='M')
# 价格修正
am = cv_strategy.cv_strategy(pool_1)
am.get_close(ktype_='M',)
# 价格修正：由于tushare读取的ETF数据未进行复权，因此需要手动对数据进行复权。

# 纳指etf复权
am.close.loc[:'2022-07-29','159941'][:-1] = am.close.loc[:'2022-07-29','159941'][:-1]/4
# 酒etf复权
am.close.loc[:'2021-05-31','512690'][:-1] = am.close.loc[:'2021-05-31','512690'][:-1]/2
am.close.loc[:'2021-12-31','512690'][:-1] = am.close.loc[:'2021-12-31','512690'][:-1]-0.35
# 医药etf复权
am.close.loc[:'2021-06-30','512010'][:-1] = am.close.loc[:'2021-06-30','512010'][:-1]/4
# 煤炭etf复权
am.close.loc[:'2021-12-31','515220'][:-1] = am.close.loc[:'2021-12-31','515220'][:-1]-0.8
am.close.loc[:'2022-12-30','515220'][:-1] = am.close.loc[:'2022-12-30','515220'][:-1]-0.4
# 计算机etf分红
am.close.loc[:'2023-09-28','512720'][:-1] = am.close.loc[:'2023-09-28','512720'][:-1]-0.048

am.close.loc['2023-03-31','513030'] = 1.157
#___________________________________________
a = cv_strategy.cv_strategy(pool_1)
a.get_close(ktype_='D',)
# 纳指etf复权
a.close.loc[:'2022-07-05','159941'][:-1] = a.close.loc[:'2022-07-05','159941'][:-1]/4
# 酒etf复权
a.close.loc[:'2021-05-17','512690'][:-1] = a.close.loc[:'2021-05-17','512690'][:-1]/2
a.close.loc[:'2021-12-31','512690'][:-1] = a.close.loc[:'2021-12-31','512690'][:-1]-0.35
# 医药etf复权
a.close.loc[:'2021-06-28','512010'][:-1] = a.close.loc[:'2021-06-28','512010'][:-1]/4
# 煤炭etf复权
a.close.loc[:'2021-12-27','515220'][:-1] = a.close.loc[:'2021-12-27','515220'][:-1]-0.8
a.close.loc[:'2022-12-27','515220'][:-1] = a.close.loc[:'2022-12-27','515220'][:-1]-0.4
# 计算机etf分红
a.close.loc[:'2023-09-25','512720'][:-1] = a.close.loc[:'2023-09-25','512720'][:-1]-0.48
a.close.loc['2023-03-31','513030'] = 1.157
#%%
a.run()
am.run(operation_pct_in=4/len(am.stock_pool),
      operation_pct_out=0.5,
      operation_pct_clr=1,
      period=2)
#%%
startdate='2023-11-30'
dec_dailyreturn = a.returns.dropna().loc[startdate:]
df_model = a.weight.loc[am.weight.iloc[-2].name:]
df = pd.DataFrame(index = df_model.index,columns=df_model.columns)
df.iloc[0,:] = am.weight.iloc[-2][df.columns]

for i in range(1,len(df)):
    df.iloc[i,:] = df.iloc[i-1,:]*(1+dec_dailyreturn.iloc[i,:])[df.columns]

dfsum = pd.DataFrame(df.T.sum(),columns=['cv_m'])
hs300 = ts.get_k_data('hs300').set_index('date')
hs300 = hs300.loc[startdate:,'close']
dfs = pd.concat([df.T.sum(),hs300],axis=1)
dfs.columns=['cv_m','hs300']
dfs['ex'] = dfs.cv_m/dfs.hs300
dfs=dfs/dfs.iloc[0]
#%%
am.visualization(control_group='hs300')

plt.style.use('ggplot')
plt.figure(figsize=[10,6],dpi=80)
plt.title('cv_m 策略与沪深300指数的走势')
plt.plot(dfs.cv_m,label='cv_m 策略走势')
plt.plot(dfs.hs300,label='沪深300指数走势')
plt.plot(dfs.ex,lw=5,alpha=0.6,color='red',label='cv_m策略相对指数走势')
plt.xticks(dfs.index,rotation=90)
plt.legend()
plt.show()
#——————
pt = df.T.sort_values(startdate,ascending=False).iloc[:14].T
aa = pt.columns.to_list()
aa.remove('cash')
pt=pt[aa]
fig = plt.figure(figsize=[20,6],dpi=80)
ax1 = plt.subplot(121)
ax1.set_ylabel('成分ETF的单位净值（元）：求和即为当日基金单位净值')
for i in pt.columns:
    if i != 'cash':
        ax1.plot(pt[i],label=i)
    
ax1.legend()
ax2=plt.subplot(122)
ax2.plot((pt/pt.iloc[0])-1)
ax2.set_ylabel('成分ETF回报率')

fig.suptitle('成分ETF表现',fontsize=20)
plt.show()
#----
qq = ((am.compare/(am.compare.loc['2022-12-30'])).iloc[-13:])
plt.plot(qq.strategy,label='cv_m',lw=5)
plt.plot(qq.hs300,label='hs300')
plt.title('cv_m策略表现')
plt.xticks(rotation=45)
plt.legend()


#%%
c = am.close.corr()
#%%
dingpan_plots.run_all()
zmlc = dingpan_plots.zh_us_interests_diff(start_date='2020-01-01')
zmlc_z = (zmlc-zmlc.mean())/zmlc.std()
sz50_predict = (zmlc_z.z[-1]*zmlc.std().sz50)+zmlc.mean().sz50
print(sz50_predict)
dingpan_plots.sz50_over_zz500(start_date='2003-01-01')
dingpan_plots.stock_bond_rolling(start_date='2006-01-01')

print(dingpan_plots.zh_us_interests_diff())
#%%
import pandas as pd
hs300_list = pd.read_excel(r'D:\jwli\stocks_stories\hs300.xlsx',sheet_name=1).dropna()
hs300_list = [i[:6] for i in hs300_list['证券代码']]
hs = cv_strategy.cv_strategy(hs300_list)
hs.get_close(ktype_='W',date_start='2012-10-01',autype_='hfq')
hs.close = hs.close.T.dropna().T
hs.run(operation_pct_in=4/len(hs.stock_pool),period=9)
hs.visualization()
#%%
aa  =dingpan_plots.stock_bond_rolling()
aa.std()/aa.mean()
#%%
swdata = dingpan_plots.sw_heatmap()
swdatacc = swdata.corr()