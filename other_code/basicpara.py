import os
import shutil
import sys
import time
import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import MySQLdb
import pymssql
from datetime import datetime
import functools
Today = datetime.today().strftime('%Y%m%d')
orderCol = ['日期','账户','资金账号','策略名称','证券代码','证券类型','交易方向','开平仓','交易数量']

def ConnectDB(IP,User,PW,Port,DB):
	conn = MySQLdb.connect(host = IP,user = User,passwd = PW,port = Port,db = DB,charset = 'utf8')
	return conn

def ConnectJY(DB):
	ii = '10.248.25.10'
	conn = pymssql.connect(host =ii,user ='JYDB_USER',password ='abcd@1234',port =1433,database =DB,charset = 'GBK')
	return conn

def ReturnDF(DB,COL,TABLE,Condition = ''):
	if Condition == '':
		sql = "select %s from %s" %(COL,TABLE)
	else:
		sql = "select %s from %s where %s" %(COL,TABLE,Condition)
	df = pd.read_sql(sql,con = DB)
	return df


connTick = ConnectDB('xxxx','read_only','read_only',8908,'referencedb')
connHolding = ConnectDB('xxxx','read_only','read_only',8908,'omsdb')
connAlgo = ConnectDB('xxxx','root','root',8908,'algodb')
connJY = ConnectJY('JYDB')

TotalPortfolio = ReturnDF(connAlgo,'ID,Name','portfolio','Deleted = 0')
PortfolioMap = dict(list(zip(TotalPortfolio['ID'],TotalPortfolio['Name'])))

AccountNo = ReturnDF(connAlgo,'PortfolioID,AccountNo','account',"AccountType = 'China_Stock_Cash'")
AccountNoMap = dict(list(zip(AccountNo['PortfolioID'],AccountNo['AccountNo'])))

Holdingcol = 'PortfolioID,Strategy,Type,Symbol SecuCode,Quantity,AvailableQuantity'
TotalHolding = ReturnDF(connHolding,Holdingcol,'strategy_position')

def get_tick_price(tick_path=''):
	if tick_path == '':
		tick_path = 'tick_data/tick_price_%s.xlsx' %Today
	TickPCT = pd.read_excel(tick_path)
	if len(TickPCT) > 1000:
		TickPCT['code'] = TickPCT['code'].map(lambda k:str(k)[:6])
		return TickPCT
	else:
		time.sleep(10)
		return get_tick_price()

print('-------basic para is ok.----------')

