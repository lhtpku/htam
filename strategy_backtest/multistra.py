from .weight import *
from .pnl import *

class class_full_strategy():
	def __init__(self):
		self.full_Strategy = full_strategy[:]
		self.all_return_cal()
		self.col = ['week','month','year']+['re_05','re_10','re_20','re_60','re_half','re_year']

	def all_return_cal(self):
		self.tmp_condi = "Strategy in ('%s') and TradingDay <= %r" %("','".join(self.full_Strategy),YesterdayStr)
		self.tmp_col = "Strategy,TradingDay,DailyReturn"
		self.all_return = self.get_dailyupdate_return('strategy_daily_return').set_index('Strategy')

	def get_dailyupdate_return(self,table):
		df = connBackTest.read(self.tmp_col,table,self.tmp_condi)
		if table == 'strategy_daily_return':
			self.all_return_raw = df.set_index('Strategy')
		df = df.pivot('TradingDay','Strategy','DailyReturn')
		df = df.loc[:,pd.notnull(df.iloc[-1,:])].stack().reset_index()
		return df.rename(columns={0:'DailyReturn'})

	def main_run(self):
		self.dd()
		self.corr()
		self.history_weight()
		self.weekly_return()
		self.total_latest_performance()
		logging.info('updating multi-stra.')

	def mdd_process(self,use_df,process_type):
		if process_type != 'all_year_mdd':
			use_df = use_df[YesterdayStr[:4]]
		use_df['cumsum'] = use_df['DailyReturn'].cumsum()
		use_df['cummax'] = np.maximum(0,use_df['cumsum'].cummax())
		use_df['dd'] = use_df['cumsum']-use_df['cummax']
		mdd = min(0,use_df['dd'].min())
		###################################
		if process_type.endswith('_year_mdd'):
			return mdd
		######
		if process_type == 'ir':
			return use_df['DailyReturn'].sum() / (np.sqrt(len(use_df))*use_df['DailyReturn'].std())
		######
		if process_type == 'is_in_mdd':
			if (mdd == 0) or (mdd >= -0.0002):
				return 'No'
			if np.allclose(mdd,use_df['dd'].tolist()[-1]):
				return 'Yes'
			else:
				return 'No'
		#####
		if process_type == 'start_mdd':
			if mdd == 0:
				return use_df.index[0].strftime('%Y-%m-%d')
			return use_df[:use_df['dd'].idxmin()]['cummax'].idxmax().strftime('%Y-%m-%d')
		#####
		if process_type == 'end_mdd':
			if mdd == 0:
				return use_df.index[0].strftime('%Y-%m-%d')
			return use_df['dd'].idxmin().strftime('%Y-%m-%d')

	def latest_frequency_performance(self,df,frequ):
		return float(df.resample(frequ).sum()['DailyReturn'][-1])


	def strategy_weekly_report(self,df):
		df = df.sort_index()[['DailyReturn']]
		#############
		self.week_col = ['week','month','year','month_3','this_year_mdd','is_in_mdd','ir','all_year_mdd','start_mdd','end_mdd']
		self.week_col.extend(['week_min','month_min','victory_rate_latest_12','victory_rate_all'])
		week_month_year = list(map(functools.partial(self.latest_frequency_performance,df),['W','M','A']))
		################
		xx = functools.partial(self.mdd_process,df)
		about_mdd = list(map(xx,['this_year_mdd','is_in_mdd','ir','all_year_mdd','start_mdd','end_mdd']))
		######################
		f2 = lambda frequ:float(df.resample(frequ).sum()['DailyReturn'].min())
		week_month_min = list(map(f2,['W','M']))
		######################
		month_return = np.array(df.resample('M').sum()['DailyReturn'].tolist())
		latest_3_month = month_return[-3:].sum()
		victory_rate_latest_12 = len([mr for mr in month_return[-12:] if mr > 0]) / len(month_return[-12:])
		victory_rate_all       = len([mr for mr in month_return if mr > 0]) / len(month_return)
		########################
		all_data = week_month_year + [latest_3_month] + about_mdd + week_month_min + [victory_rate_latest_12,victory_rate_all]
		return Series(dict(list(zip(self.week_col,all_data))))

	def weekly_return(self):
		alpha_return = self.all_return.reset_index('Strategy').set_index('TradingDay').groupby('Strategy')
		alpha_return = alpha_return.apply(self.strategy_weekly_report)
		alpha_return = alpha_return[self.week_col].reset_index()
		alpha_return['Type'] = alpha_return['Strategy'].map(strategy_status)
		connBackTest.delete_insert(alpha_return,'week_report',[])
		return alpha_return

	def latest_performance(self,df):
		df = df.sort_index()[['DailyReturn']]	
		value_1 = list(map(functools.partial(self.latest_frequency_performance,df),['W','M','A']))
		value_2 = [df[-n:]['DailyReturn'].sum() for n in [5,10,20,60,120,240]]
		return Series(dict(list(zip(self.col,value_1 + value_2))))

	def total_latest_performance(self):
		long_return = self.get_dailyupdate_return('long_position_daily_return').set_index('TradingDay')
		long_return = long_return.groupby('Strategy').apply(self.latest_performance)
		alpha_return = self.all_return.reset_index('Strategy').set_index('TradingDay').groupby('Strategy').apply(self.latest_performance)
		long_return['Type'] = 'Long'
		alpha_return['Type'] = 'Alpha'
		total_return = pd.concat([alpha_return,long_return]).reset_index().fillna(0)
		total_return = total_return[['Strategy'] + self.col + ['Type']]
		connBackTest.delete_insert(total_return,'latest_performance',[])
		return 

	def sub_corr(self):
		my_corr = [stra for stra in self.full_Strategy if stra.startswith('S15')]
		stra_corr = self.all_return.reset_index().pivot('TradingDay','Strategy','DailyReturn')
		stra_corr = stra_corr[my_corr]
		# stra_corr[stra_corr.applymap(abs) < 0.00002] = np.nan
		stra_corr = stra_corr.corr()
		stra_corr = stra_corr.applymap(lambda k:round(k,2))
		print(stra_corr)
		return stra_corr

	def corr_pre(self,col):
		df = self.all_return_raw.reset_index().pivot('TradingDay','Strategy',col)
		df[df.applymap(abs) < 0.00002] = np.nan
		df_corr = df.corr()
		#########################
		for stra1 in self.full_Strategy:
			for stra2 in self.full_Strategy:
				df_corr.loc[stra1,stra2] = df[[stra1,stra2]].dropna(how='all').fillna(0).corr().iloc[1,0]
		df = DataFrame(df_corr.stack())
		df = df.reset_index(level = 1).rename(columns = {'Strategy':'sub_Strategy'}).reset_index()
		return df

	def corr(self):
		self.all_return_raw['DailyReturn2'] = np.where(self.all_return_raw['DailyReturn'] > 0,1,-1)
		StrategyCorr1 = self.corr_pre('DailyReturn')
		StrategyCorr2 = self.corr_pre('DailyReturn2')
		StrategyCorr = pd.merge(StrategyCorr1,StrategyCorr2,on = ['Strategy','sub_Strategy'],how = 'inner')
		StrategyCorr['CreateDate'] = NowTick
		connBackTest.delete_insert(StrategyCorr,'alpha_strategy_corr',[])
		logging.debug('Updating Corr is ok.')

	def dd(self):
		NN = 30
		def getSignal(df):
			colAttri = ['Seri' + str(k).rjust(2,'0') for k in range(1,NN + 1)] + ['Sample','DD']
			df = df.set_index('TradingDay').sort_index()
			df['CumRet'] = df['DailyReturn'].cumsum()
			df['CumMax'] = df['CumRet'].rolling(window = 60,min_periods = 30).max()
			df['DrawDown'] = df['CumRet'] - df['CumMax']
			newestDD = df.ix[-1,'DrawDown']
			df['Sig'] = np.where(df['DrawDown'] < newestDD,1,0)
			#### signal
			AllIndex = dict((value,key) for key,value in enumerate(list(df.index)))
			df['Signal'] = df['Sig'].groupby((df['Sig'] != df['Sig'].shift()).cumsum()).cumsum()
			#### signal for 3
			useIndex = list(df[:-NN].query('Signal == 3').index)
			afterPerformance = []
			if len(useIndex) > 1:
				useIndex = [AllIndex[k] + 1 for k in useIndex]
				useIndex2 = [k + NN for k in useIndex]
				cpIndex = list(zip(useIndex,useIndex2))
				result = [np.array(df[k[0]:k[1]]['DailyReturn']) for k in cpIndex[:]]
				afterPerformance = list(np.array(result).mean(axis = 0))
				colAttri2 = colAttri
			else:
				colAttri2 = ['Sample','DD']
			afterPerformance.extend([len(useIndex),newestDD])
			df = DataFrame({'Attri':colAttri2,'Value':afterPerformance})
			return df
		StrategyDD = self.all_return.groupby(level = 0).apply(getSignal).reset_index()
		del StrategyDD['level_1']
		StrategyDD['CreateDate'] = NowTick
		connBackTest.delete_insert(StrategyDD,'strategy_return_dd',[])
		logging.debug('Updating DrawDown Performance is ok.')

	def history_weight(self):
		Col = "Strategy,TradingDay,Market,Weight"
		weightt = connBackTest.read(Col,"alpha_strategy_sh_sz",self.tmp_condi).set_index('Strategy')
		##############
		def weightAnalysis(df):
			df = df.pivot('TradingDay','Market','Weight').fillna(0)
			df = DataFrame(df.describe().rename(index = {'25%':'Q01','50%':'median','75%':'Q03'}).unstack()).reset_index()
			return df
		#############
		weightt = weightt.groupby(level = 0).apply(weightAnalysis)
		weightt = weightt.rename(columns = {'level_1':'Attri',0:'Value'}).reset_index().fillna(0)
		del weightt['level_1']
		weightt['CreateDate'] = NowTick
		connBackTest.delete_insert(weightt,'strategy_weight_stat',[])
		logging.debug('Updating Histoty Weight Stat is ok.')


