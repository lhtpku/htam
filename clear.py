from .performance import *

class ValueClear():
	def __init__(self):
		super().__init__()
		self.display_netvalue()
		logging.warning('Clearing value in %s to db is ok.'%TodayStr)
		
	def get_daily_chg(self,df):
		df['Pct'] = df['NetValue'].pct_change()
		return df.fillna(0)

	def get_monthly_chg(self,df):
		df = df.set_index('TradingDay').resample('M').last()
		df['Pct'] = df['NetValue'].pct_change()
		df.ix[0,'Pct'] = df.ix[0,'NetValue'] - 1
		return df.reset_index()

	def get_latest_month_return(self,df):
		if len(df) == 1:
			return float(df['NetValue'] - 1)
		else:
			return float(df['NetValue'].pct_change().tolist()[-1])

	def get_account_performance(self,df):
		latest_value = df['NetValue'].tolist()[-1] - 1
		annual_return = latest_value*244/len(df)
		annual_std = df['Pct'].std() * np.sqrt(244)
		temp = df[['NetValue','TradingDay']].set_index('TradingDay')
		monthly_return = self.get_latest_month_return(temp.resample('M').last())
		yearly_return = self.get_latest_month_return(temp.resample('A').last()) 
		daily_return = self.get_latest_month_return(temp)
		return Series({'netvalue':latest_value + 1,
				'daily':daily_return,
				'monthly':monthly_return,
				'yearly':yearly_return,
				'newest':latest_value,
				'annual':annual_return,
				'std':annual_std,
				'sharp_ratio':annual_return / annual_std,
				'mdd':min(df['NetValue'] / df['NetValue'].cummax()) - 1})

	def display_netvalue(self):
		all_netvalue = connOF.read('TradingDay,PortfolioID,NetValue','net_value_real').sort_values(['PortfolioID','TradingDay'])

		daily_netvalue = all_netvalue.groupby('PortfolioID',as_index = False).apply(self.get_daily_chg)
		connOF.delete_insert(self.df_standard(daily_netvalue),'display_daily_netvalue',[])

		monthly_netvalue = all_netvalue.groupby('PortfolioID',as_index = False).apply(self.get_monthly_chg)
		connOF.delete_insert(self.df_standard(monthly_netvalue),'display_monthly_netvalue',[])

		account_general = daily_netvalue.groupby('PortfolioID').apply(self.get_account_performance)
		temp_col = ['netvalue','daily','monthly','yearly','newest','annual','std','sharp_ratio','mdd']
		account_general = account_general[temp_col].reset_index()
		connOF.delete_insert(self.df_standard(account_general),'account_general',[])


class AttributionClear():
	def __init__(self):
		super().__init__()
		self.all = connOF.read('*','daily_attribution').set_index('TradingDay')
		self.monthly_attribution()
		self.sum_attribution()

	def attri_standard(self,df):
		if 'PortfolioID' in df.columns:
			df = df.drop(['ID','PortfolioID'],axis = 1).reset_index()
			temp_col = ['TradingDay','PortfolioID'] + list(df.columns[2:])
			df = df[temp_col]
		else:
			df = df.drop(['ID'],axis = 1).reset_index()
		return self.df_standard(df)

	def monthly_attribution(self):
		month = self.all.groupby('PortfolioID').apply(lambda df:df.resample('M').sum())
		month = month.reset_index('TradingDay')
		#############
		from pandas.tseries.offsets import MonthEnd
		month_end =  MonthEnd().rollforward(TodayStr)
		month['TradingDay'] = month['TradingDay'].replace(month_end,pd.to_datetime(TodayStr))
		#########
		month = self.attri_standard(month)
		connOF.delete_insert(month,'monthly_attribution',[])

	def sum_attribution(self):
		all_ = self.all.groupby('PortfolioID').sum()
		all_ = self.attri_standard(all_)
		connOF.delete_insert(all_,'acc_attribution',['TradingDay'])


class StrategyClear():
	def __init__(self):
		self.main_run()

	def main_run(self):
		self.base_data()
		df = self.get_latest()
		df = pd.merge(self.today_performance,df,on=['PortfolioID','Strategy'],how='outer')
		# connOF.delete_insert(df,'daily_strategy_performance',['TradingDay'])
		return df

	def base_data(self):
		self.group_col = ['PortfolioID','Strategy']
		self.use_lag = [self.history_date(-4),self.history_date(-9),'20170101']
		use_col = 'TradingDay,PortfolioID,Strategy,Weight,pnl'
		self.history_performance = connOF.read(use_col,'strategy_performance','Weight > 0.0001')
		self.today_performance = connOF.read(use_col,'strategy_performance','TradingDay = %s and Weight > 0.02'%TodayStr)

	def get_latest(self):
		tt = list(map(self.latest_performance,[4,9,99]))
		tt1 = pd.merge(tt[1],tt[2],on = self.group_col,how = 'outer')
		tt2 = pd.merge(tt[0],tt1,on = self.group_col,how = 'outer').fillna(0)
		return tt2

	def latest_performance(self,lag_num):
		use_date = '20170101' if lag_num == 99 else w.tdaysoffset(-lag_num,TodayStr).Data[0][0].date().strftime('%Y%m%d')
		temp_df = self.history_performance[self.history_performance['TradingDay'] >= use_date]
		return temp_df.groupby(self.group_col)[['pnl']].sum().reset_index().rename({'pnl':'pnl%s'%(lag_num+1)})  
		