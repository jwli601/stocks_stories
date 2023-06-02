# -*- coding: utf-8 -*-
"""
Created on Thu Nov 10 09:20:23 2022

@author: GMJJB
"""

import cv_strategy
import dingpan_plots
# ETF持仓
pool_1=['512660','512800',# 军工、银行
        '513330','515220',# 恒生科技、煤炭
        '159996','512010',# 家电、医药
        '159825','159865',# 农业、养殖
        '159995','159732',# 消费电子、芯片
        '518880','501018',# 黄金、原油
        '159766','512690',# 旅游，酒
        '515700','515790',# 新能车、光伏
        '159985',#'511260',# 豆粕期货，十年国债ETF
        '159941', '513030',#'513080',#'513880',#,         # nasdaq,德国，法国cac40，日本225 
        '512980','512720',         # 传媒, 计算机
        '513360',#'159611'                  # 教育

#       '563000','510300','510500',# 中国A50，hs300, zz500
       ]
#%%

pool_2 = ['159865','159870','502023','512400','159997','159996','159928','159936','161726',
          '159611','516530','512200','159766','159745','165525','512580','512660','159998',
          '512980','515880','512800','512070','516110','161032','159930','512580']
am2 = cv_strategy.cv_strategy(pool_2)
am2.get_close(ktype_='D')
am2.close.loc[:'2021-06-24','159928'] = am2.close.loc[:'2021-06-24','159928']/4.94*1.235
am2.close.loc[:'2021-09-10','512070'] = am2.close.loc[:'2021-09-10','512070']/2.318*0.773

am2.run(operation_pct_in=4/len(am2.stock_pool),
      operation_pct_out=0.5,
      operation_pct_clr=1,
      period=42)
am2.visualization(control_group='hs300')
print(am2.compare.pct_change().tail(5))
#%%

a = cv_strategy.cv_strategy(pool_1)
a.get_close(ktype_='D')
# 价格修正
a.close.loc['2022-07-05':,'159941']=a.close.loc['2022-07-05':,'159941']/0.604*2.416
a.close.loc[:'2021-05-14','512690'] = a.close.loc[:'2021-05-14','512690']/2.644*0.972
a.close.loc['2021-05-15':'2021-12-30','512690'] = a.close.loc['2021-05-15':'2021-12-30','512690']/1.323*0.973
a.close.loc[:'2021-06-25','512010'] = a.close.loc[:'2021-06-25','512010']/3.206*0.836
a.close.loc[:'2022-12-26','515220'] = a.close.loc[:'2022-12-26','515220']/2.187*2.147

a.run(operation_pct_in=4/len(a.stock_pool),
      operation_pct_out=0.5,
      operation_pct_clr=1,
      period=50)
a.visualization(control_group='hs300')
print(a.compare.pct_change().tail(5))
#%%
import numpy as np
s = a.close.corr()
for i in s.columns:
    print(i)
    print(np.percentile(s[i],[10,90]))
#%%
am = cv_strategy.cv_strategy(pool_1)
am.get_close(ktype_='M')
# 价格修正
am.close.loc['2022-07-05':,'159941']=am.close.loc['2022-07-05':,'159941']/0.604*2.416
am.close.loc[:'2021-05-14','512690'] = am.close.loc[:'2021-05-14','512690']/2.644*0.972
am.close.loc['2021-05-15':'2021-12-30','512690'] = am.close.loc['2021-05-15':'2021-12-30','512690']/1.323*0.973
am.close.loc[:'2021-06-25','512010'] = am.close.loc[:'2021-06-25','512010']/3.206*0.836
am.close.loc[:'2022-12-26','515220'] = am.close.loc[:'2022-12-26','515220']/2.187*2.147
am.close.loc['2023-03-31','513030'] = 1.157

#%%


am.run(operation_pct_in=4/len(am.stock_pool),
      operation_pct_out=0.5,
      operation_pct_clr=1,
      period=2)
am.visualization(control_group='hs300')
print(am.compare.pct_change().tail(5))
#%%
c = am.close.corr()
#%%
dingpan_plots.run_all()
zmlc = dingpan_plots.zh_us_interests_diff(start_date='2016-01-01')
zmlc_z = (zmlc-zmlc.mean())/zmlc.std()
sz50_predict = (zmlc_z.z[-1]*zmlc.std().sz50)+zmlc.mean().sz50
print(sz50_predict)
dingpan_plots.sz50_over_zz500(start_date='2013-01-01',end_date='2023-05-01')

print(dingpan_plots.zh_us_interests_diff())
#%%
import pandas as pd
hs300_list = pd.read_excel(r'D:\jwli\stocks_stories\hs300.xlsx',sheet_name=1).dropna()
hs300_list = [i[:6] for i in hs300_list['证券代码']]
hs = cv_strategy.cv_strategy(hs300_list)
hs.get_close(ktype_='D',date_start='2015-10-01')
hs.close = hs.close.T.dropna().T
hs.run(operation_pct_in=4/len(hs.stock_pool),period=50)
hs.visualization()
#%%
aa  =dingpan_plots.stock_bond_rolling()
aa.std()/aa.mean()
#%%
dingpan_plots.stock_bond_rolling(start_date='1996-01-01')
