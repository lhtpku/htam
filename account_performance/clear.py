from .performance import *

class ValueClear(BasicPara):
	def __init__(self):
		super().__init__()
		self.display_netvalue()
		
	def get_daily_chg(self,df):
		df['Pct'] = df['NetValue'].pct_change()
		return df.fillna(0)

	def get_monthly_chg(self,df):
		df = df.set_index('TradingDay').resample('M').last()
		df['Pct'] = df['NetValue'].pct_change()
		df.ix[0,'Pct'] = df.ix[0,'NetValue'] - 1
		return df.reset_index()

	def get_latest_freq_return(self,df):
		if len(df) == 1:
			return float(df['NetValue'] - 1)
		else:
			return float(df['NetValue'].pct_change().tolist()[-1])

	def get_account_performance(self,df):
		latest_value = df['NetValue'].tolist()[-1] - 1
		annual_return = latest_value*244/len(df)
		annual_std = df['Pct'].std() * np.sqrt(244)
		tmp = df[['NetValue','TradingDay']].set_index('TradingDay')
		monthly_return = self.get_latest_freq_return(tmp.resample('M').last())
		yearly_return = self.get_latest_freq_return(tmp.resample('A').last()) 
		daily_return = self.get_latest_freq_return(tmp)
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
		whole_netvalue = connOF.read('TradingDay,PortfolioID,NetValue','net_value_real').sort_values(['PortfolioID','TradingDay'])
		####################
		daily_netvalue = whole_netvalue.groupby('PortfolioID', as_index=False).apply(self.get_daily_chg)
		connOF.delete_insert(self.df_standard(daily_netvalue),'display_daily_netvalue',[])
		######################
		monthly_netvalue = whole_netvalue.groupby('PortfolioID', as_index=False).apply(self.get_monthly_chg)
		connOF.delete_insert(self.df_standard(monthly_netvalue),'display_monthly_netvalue',[])
		######################
		account_general = daily_netvalue.groupby('PortfolioID').apply(self.get_account_performance)
		tmp_col = ['netvalue','daily','monthly','yearly','newest','annual','std','sharp_ratio','mdd']
		account_general = account_general[tmp_col].reset_index()
		connOF.delete_insert(self.df_standard(account_general),'account_general',[])


class AttributionClear(BasicPara):
	def __init__(self):
		super().__init__()
		self.whole = connOF.read('*','daily_attribution').set_index('TradingDay')
		self.monthly_attribution()
		self.sum_attribution()

	def attri_standard(self,df):
		if 'PortfolioID' in df.columns:
			df = df.drop(['ID','PortfolioID'], axis=1).reset_index()
			tmp_col = ['TradingDay','PortfolioID'] + list(df.columns[2:])
			df = df[tmp_col]
		else:
			df = df.drop(['ID'],axis = 1).reset_index()
		return self.df_standard(df)

	def monthly_attribution(self):
		month = self.whole.groupby('PortfolioID').apply(lambda df:df.resample('M').sum())
		month = month.reset_index('TradingDay')
		#############
		from pandas.tseries.offsets import MonthEnd
		month_end =  MonthEnd().rollforward(TodayStr)
		month['TradingDay'] = month['TradingDay'].replace(month_end,pd.to_datetime(TodayStr))
		#########
		month = self.attri_standard(month)
		connOF.delete_insert(month,'monthly_attribution',[])

	def sum_attribution(self):
		whole_ = self.whole.groupby('PortfolioID').sum()
		whole_ = self.attri_standard(whole_)
		connOF.delete_insert(whole_,'acc_attribution',['TradingDay'])


class StrategyClear(BasicPara):
	def __init__(self):
		self.main_run()

	def main_run(self):
		self.base_data()
		df = self.get_latest()
		df = pd.merge(self.today_performance,df,on=['PortfolioID','Strategy'],how='left')
		df = df[self.group_col+['Weight','Bias','pnl','pnl_5','pnl_10','pnl_99']]
		connOF.delete_insert(self.df_standard(df),'daily_strategy_performance',['TradingDay'])
		return

	def base_data(self):
		self.group_col = ['PortfolioID','Strategy']
		self.use_lag = [self.history_date(-4),self.history_date(-9),'20170101']
		use_col = 'PortfolioID,Strategy,Weight,pnl'
		self.history_performance = connOF.read('%s,TradingDay'%use_col,'strategy_performance','Weight > 0.0001')
		###############
		today_performance = connOF.read(use_col,'strategy_performance','TradingDay=%s and Weight > 0.02' %TodayStr)
		strategy_bias = StrategyBias().total_bias()
		self.today_performance = pd.merge(today_performance, strategy_bias, on=self.group_col, how='left').fillna('..')

	def get_latest(self):
		tt = list(map(self.latest_performance,[4,9,99]))
		tt1 = pd.merge(tt[1],tt[2], on=self.group_col, how='outer', suffixes=('_10', '_99'))
		tt2 = pd.merge(tt[0],tt1, on=self.group_col, how='outer').fillna(0)
		return tt2.rename(columns={'pnl':'pnl_5'})

	def history_date(self,lag_num):
		return w.tdaysoffset(-lag_num,TodayStr).Data[0][0].date().strftime('%Y%m%d')

	def latest_performance(self,lag_num):
		use_date = '20170101' if lag_num == 99 else self.history_date(lag_num)
		tmp_df = self.history_performance[self.history_performance['TradingDay'] >= use_date]
		return tmp_df.groupby(self.group_col)[['pnl']].sum().reset_index().rename({'pnl':'pnl%s'%(lag_num+1)})  


class StrategyBias(BasicPara):
	def __init__(self):
		super().__init__()
		self.theory_dir = os.path.join(DATA_ROOT,'DailyWeight')
		self.position = connOF.read('PortfolioID,Strategy,Code,Volume','daily_holding',"TradingDay = %r" %TodayStr)
		self.bias_strategy = self.theory_strategy()

	def theory_strategy(self):
		strategy = MyDir(self.theory_dir).whole_file_path('.csv')
		strategy = [k for k in strategy if 'S' in k or 'N' in k]
		strategy = [str(k).split('_')[1].strip('.csv') for k in strategy]
		return strategy

	def theory_weight(self,Stra):
		df = pd.read_csv("%s/W_%s.csv"%(self.theory_dir,Stra)).iloc[:,:2]
		df.columns = ['Code','Weight']
		weight_sum = df['Weight'].sum()
		if weight_sum <= 1:
			return DataFrame(columns=['Code','Weight'])
		df['Weight'] = df['Weight'] / weight_sum
		return df

	def strategy_bias(self,df):
		stra = df['Strategy'].unique()[0]
		df['Weight'] = df['Volume'] / df['Volume'].sum()
		df = pd.merge(df,self.theory_weight(stra), on='Code', how='outer').fillna(0)
		return abs(df['Weight_x'] - df['Weight_y']).sum() / 2
		
	def total_bias(self):
		tmp_df = self.position.query("Strategy in ('%s')" %"','".join(self.bias_strategy))
		if len(tmp_df) == 0:
			return
		######################
		bias = tmp_df.groupby(['PortfolioID','Strategy']).apply(lambda dfk: self.strategy_bias(dfk)).reset_index()
		_ = bias.rename(columns={0:'Bias'}, inplace=True)
		bias['Bias'] = bias['Bias'].map(lambda k:format(k,'.2%'))
		return bias

