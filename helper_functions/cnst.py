from .dbclass import *
#######################################
conn_ams = DBConnect(get_config_para('DataBasePara','ams_ip'),'root','root',3306,'amsdb')
conn_of  = DBConnect(get_config_para('DataBasePara','ams_ip'),'root','root',3306,'ofdb')
conn_jy  = DBConnect(get_config_para('DataBasePara','jy_ip'),'JYDB_USER','abcd@1234',1433,'JYDB')
conn_jy_cloud = DBConnect(get_config_para('DataBasePara','jy_cloud'),'JYDB_USER','abcd@1234',1433,'JYDB')
conn_bt = DBConnect(get_config_para('DataBasePara','bt_ip'),'root','root',3306,'performancedb')
conn_wind = DBConnect(get_config_para('DataBasePara','wind_ip'),'WindDB_ADMIN','abcd@1234',1433,'WindDB')
########################################
connAMS = conn_ams.connectMySQL()
connOF  = conn_of.connectMySQL()
connJY = conn_jy.connectJY()
connCloud = conn_jy_cloud.connectJY()
connBackTest = conn_bt.connectMySQL()
connWind = conn_wind.connectJY()
#########################################
ALL_INDEX = get_config_para('BasicPara','all_index')
####################################
TimeTick = TimeNow()
NowTick = TimeTick.get_now()
tmp_date = ''
TodayStr = TimeTick.get_str() if tmp_date == '' else tmp_date
start_date = '20061220'
def all_jy_tradingday_f(start_date=start_date):
	temp_condi = "SecuMarket = 83 and IfTradingDay=1 and TradingDate >= %r and TradingDate <= %r" %(start_date,'20200101')
	temp_tradingday = connJY.read("TradingDate",'QT_TradingDayNew',temp_condi).sort_values('TradingDate')
	all_tradingday = [k.strftime('%Y%m%d') for k in temp_tradingday['TradingDate'].tolist()]
	if TodayStr not in all_tradingday:
		logging.critical('%s is not a tradingday.'%today_str)
		raise SystemExit('%s is not a tradingday.'%today_str)
	yesterday_str = all_tradingday[all_tradingday.index(TodayStr)-1]
	end_date = yesterday_str
	all_use_tradingday = [day for day in all_tradingday if day <= end_date]
	all_use_tradingday = list(map(pd.to_datetime,all_use_tradingday))
	return all_tradingday,yesterday_str,end_date,all_use_tradingday
all_jy_tradingday,YesterdayStr,end_date,all_trading_day = all_jy_tradingday_f()
############################################################
def df_fillna_index(df,new_index):
	if isinstance(new_index,DataFrame):
		new_index = new_index.index
	df = df.reindex(new_index)
	df_is_null = list(map(all,pd.isnull(df.values)))
	for i in range(1,len(df)):
		if df_is_null[i]:
			df.iloc[i,:] = df.iloc[i-1,:]
	return df.dropna(how='all')
