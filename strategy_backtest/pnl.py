from .h5 import *

class DailyPosition():
	def __init__(self,strategy):
		self.stra = strategy
		self.strategy_basic_attri()
		self.get_position()

	def get_position(self):
		if self.isOnlyReturn == 1:
			return
		################################
		self.total_pct = total_pct
		sql_table = 'alpha_strategy_daily_position' 
		self.all_position = connBackTest.read('TradingDay,InnerCode,Weight', sql_table, "Strategy = %r" %self.stra)
		self.get_position_special()

	def get_position_special(self):
		self.all_position = self.all_position.drop_duplicates(['TradingDay','InnerCode'])
		if self.stra == 'S3102B':
			self.all_position['Weight'] *= 0.5
		###################################
		if self.isLongShort == 1:
			self.position_short_raw = self.all_position.query("Weight < 0").pivot('TradingDay','InnerCode','Weight')
			self.position_short = self.position_reindex(self.position_short_raw)
		###################################
		self.position_long_raw = self.all_position.query("Weight > 0").pivot('TradingDay','InnerCode','Weight')
		self.position_long = self.position_reindex(self.position_long_raw)

	def strategy_basic_attri(self):
		self.isLongShort = strategy_longshort_dict[self.stra]
		self.isTiming = strategy_timing_dict[self.stra]
		self.isIndex = strategy_index_dict[self.stra]
		self.isBeta = strategy_beta_dict[self.stra]
		self.BenchMark = strategy_bench_dict[self.stra]
		self.isMixHedge = strategy_mixhedge_dict[self.stra]
		self.isOnlyReturn = strategy_onlyreturn_dict[self.stra]
		self.sellingTime = strategy_sellingtime_dict[self.stra]
		#############################
		if self.BenchMark in [50,300,500]:
			self.BenchMarkJY = {300:3145,500:4978,50:46}[self.BenchMark]
		if self.stra in ['S3102B','S3103B']:
			self.change_cost = 0
		else:
			self.change_cost = get_config_para('BasicPara','change_cost')

	def df_standard(self,df):
		df.insert(0,'Strategy',self.stra)
		df.insert(len(df.columns),'CreateDate',NowTick)
		return df

	def position_reindex(self,dff):
		if self.isTiming == 1:
			return dff.reindex(all_trading_day).shift(1).dropna(how='all')
		############################
		if self.sellingTime == 'PreClose':
			df = dff.reindex(all_trading_day).shift(1)
		else:
			df = dff.reindex(all_trading_day).shift(2)
		##################################
		dfNull = list(map(all,pd.isnull(df.values)))
		for i in range(1,len(df)):
			if dfNull[i]:
				df.iloc[i,:] = df.iloc[i-1,:]
		return df.dropna(how='all')

	def all_position(self):
		if self.isLongShort == 1:
			return self.position_reindex(self.position),self.position_reindex(self.position_short)
		return self.position_reindex(self.position)

	def vwap_position(self,df_vwap):
		df = df_vwap.add((-1)*df_vwap.shift(), fill_value=0)
		df = df.reindex(all_trading_day).shift().dropna(how='all')
		return df

		
class DailyReturn(DailyPosition):
	def __init__(self,strategy):
		DailyPosition.__init__(self,strategy)
		self.change_rate_insert()

	def change_rate_without_fund(self,df):
		if self.isIndex == 0:
			return df
		return df[[k for k in df.columns if k not in SecuFund]]
		
	def change_rate_insert(self):
		if self.isOnlyReturn == 1:
			return
		dff = self.all_position.pivot('TradingDay','InnerCode','Weight')
		dff = self.change_rate_without_fund(dff)
		##########################################
		change_rate_num = dff.fillna(0).diff().apply(abs).sum(axis=1).dropna() / 2
		change_rate_num = DataFrame(change_rate_num).reset_index().rename(columns={0:'change_rate'})
		change_rate_num = change_rate_num[change_rate_num['change_rate'] > 0]
		if len(change_rate_num) == 0:
			return
		change_rate_num.insert(1,'Market','ChangeRate')
		connBackTest.delete_insert(self.df_standard(change_rate_num),'alpha_strategy_sh_sz',['Strategy','Market'])
		
	def change_rate(self,dff):
		dff = self.change_rate_without_fund(dff)
		dff = dff.reindex(all_trading_day)
		return dict(dff.fillna(0).diff().apply(abs).sum(axis=1).shift(-1).dropna() / 2)

	def position_multi_pct(self,df,use_pct,col):
		use_pct = use_pct.reindex(df.index).fillna(0)
		daily_return = (df.fillna(0) * use_pct).sum(axis=1).dropna().reset_index()
		daily_return = DataFrame(daily_return).rename(columns={0:col,'index':'TradingDay'})
		daily_return = daily_return[daily_return['TradingDay'] >= max(start_date,'20070101')]
		return daily_return

	def get_return(self,df,df_vwap):
		normal_return = self.position_multi_pct(df,self.total_pct,'DailyReturn')
		if self.sellingTime != 'VWAP':
			return normal_return
		#####################################
		daily_pnl = self.position_multi_pct(self.vwap_position(df_vwap),total_pct_h5['VwapPct'],'pnl')
		daily_return = pd.merge(normal_return,daily_pnl,on = 'TradingDay',how = 'left').fillna(0)
		daily_return['DailyReturn'] = daily_return['DailyReturn'] + daily_return['pnl']
		return daily_return[['TradingDay','DailyReturn']]

	def net_long_position_out(self,df):
		connBackTest.delete_insert(self.df_standard(df),'long_position_daily_return',['Strategy'])
		df = df.set_index('TradingDay')[['DailyReturn']]
		year_stat = ReturnSeries(df).year_statistic()
		connBackTest.delete_insert(self.df_standard(year_stat),'long_position_yearly_return',['Strategy'])

	def no_cost_return(self,df,df_vwap):
		daily_return = self.get_return(df,df_vwap)
		cost = self.change_rate(df)
		#########################
		daily_return['Cost'] = daily_return['TradingDay'].map(lambda k:cost.get(k,0))
		daily_return['DailyReturn'] = daily_return['DailyReturn'] - self.change_cost*daily_return['Cost']
		daily_return = daily_return[['TradingDay','DailyReturn']]
		if self.isLongShort == 0:
			self.net_long_position_out(daily_return)
		return daily_return

	def beta(self):
		if self.isBeta == 1:
			daily_beta = connBackTest.read('TradingDay,Beta','alpha_strategy_daily_beta',"Strategy = %r" %self.stra)
			daily_beta = daily_beta.set_index('TradingDay').reindex(all_trading_day).fillna(method='ffill').shift(1).dropna()
			return dict(daily_beta['Beta'])
		if self.isTiming == 1:
			condi = "Strategy = %r and Market in ('SH','SZ')" %self.stra
			daily_beta = connBackTest.read('TradingDay,Market,Weight','alpha_strategy_sh_sz',condi)
			daily_beta = daily_beta['Weight'].groupby(daily_beta['TradingDay']).sum()
			return dict(daily_beta)
		return dict()

	def bench(self):
		if self.isLongShort == 1:
			bench = self.no_cost_return(self.position_short,self.position_short_raw).set_index('TradingDay')
			return dict(bench['DailyReturn'])
		if self.BenchMark != 0:
			condi = "Bench = %r" %BenchmarkDict[self.BenchMark]
			bench = connBackTest.read('TradingDay,PctChg','benchmark_daily_pct',condi).set_index('TradingDay')
			return dict(bench['PctChg'])
		else:
			return dict()

	def alpha(self):
		df = self.no_cost_return(self.position_long,self.position_long_raw)
		use_bench = self.bench()
		use_beta = self.beta()
		df['bench'] = df['TradingDay'].map(lambda k:use_bench.get(k,0))
		df['beta'] = df['TradingDay'].map(lambda k:use_beta.get(k,1))
		para = 2 * self.isLongShort - 1
		df['Alpha'] = df['DailyReturn'] + para * df['beta'] * df['bench']
		return df[['TradingDay','Alpha']].set_index('TradingDay')

	def strategy_summary(self,daily_return):
		tmp_summary = [self.stra,
						daily_return.annual_yield(),
						daily_return.annual_std(),
						daily_return.information_ratio(),
						daily_return.mdd(),
						daily_return.acc_yield(),
						daily_return.daily_victory_rate(),
						daily_return.monthly_victory_rate(),
						244*sum(self.change_rate(self.position_long).values()) / daily_return.tradingday_len()]
		tmp_summary.extend(daily_return.rolling())
		tmp_summary.extend(daily_return.win_loss_statistic())
		tmp_summary.extend(daily_return.total_longest_dd())
		tmp_summary.append(NowTick)
		connBackTest.delete_insert(tmp_summary,'alpha_strategy_summary',['Strategy'])

	def index_return(self,Index):
		condi = "Bench in ('%s')" %Index
		df = connBackTest.read("TradingDay,Bench,PctChg","benchmark_daily_pct", condi)
		df = df.pivot('TradingDay','Bench','PctChg')
		####################################
		if self.stra == 'S0012':
			df['DailyReturn'] = df['000852.SH'] - df['H00016.SH']
		else:
			df['DailyReturn'] = df[Index]
		df.columns.name = ''
		return ReturnSeries(df[['DailyReturn']])

	def only_daily_return(self):
		df = connBackTest.read('TradingDay,DailyReturn','strategy_daily_return','Strategy=%r'%self.stra)
		return ReturnSeries(df.set_index('TradingDay')[['DailyReturn']])

	def return_insert(self):
		if self.isOnlyReturn == 0:
			alpha_return = ReturnSeries(self.alpha())
			self.strategy_summary(alpha_return)
		elif self.stra == 'S0012':
			alpha_return = self.index_return("','".join(['000852.SH','H00016.SH']))
		elif self.stra == 'S0300':
			alpha_return = self.index_return('000300.SH')
		elif self.stra == 'S0016':
			alpha_return = self.index_return('000016.SH')
		elif self.stra == 'S0905':
			alpha_return = self.index_return('000905.SH')
		elif self.stra == 'S0852':
			alpha_return = self.index_return('000852.SH')
		elif self.stra == 'S0120':
			alpha_return = self.index_return('CES120.CSI')
		else:
			alpha_return = self.only_daily_return()
		##################################
		day_return = alpha_return.get_daily_return()
		month_return = alpha_return.get_month_return()
		quarter_return = alpha_return.get_quarter_return()
		year_return = alpha_return.year_statistic()
		####################################
		connBackTest.delete_insert(self.df_standard(day_return),'strategy_daily_return',['Strategy'])
		connBackTest.delete_insert(self.df_standard(month_return),'alpha_strategy_monthly_return',['Strategy'])
		connBackTest.delete_insert(self.df_standard(quarter_return),'alpha_strategy_quarterly_return',['Strategy'])
		connBackTest.delete_insert(self.df_standard(year_return),'alpha_strategy_annulized_return',['Strategy'])
		if self.isOnlyReturn == 1:
			connBackTest.delete_insert(year_return,'long_position_yearly_return',['Strategy'])
		logging.info('Updating %s return data is ok.'%self.stra)

	def merge_position_industry_grade(self):
		df_grade = get_factor_data_from_h5('Grade',self.BenchMarkJY)
		df_weight = DataFrame(self.position_long.stack()).reset_index().rename(columns={0:'Weight'})
		df_pct = DataFrame(self.total_pct.stack()).reset_index().rename(columns={0:'Pct','level_0':'TradingDay'})
		###################################
		df = pd.merge(df_weight, df_pct, on=['TradingDay','InnerCode'], how='left').fillna(0)
		df = pd.merge(df, df_grade, on=['TradingDay','InnerCode'], how='left').fillna('Grade05')
		df['Industry'] = df['InnerCode'].map(IndustryDict)
		change_rate_industry = self.change_rate(self.position_long)
		df['TradeCost'] = self.change_cost*df['TradingDay'].map(lambda k:change_rate_industry.get(k,0))
		df['Pct'] = df['Pct'] - df['Weight']*df['TradeCost']
		df['Weight*Pct'] = df['Weight']*df['Pct']
		del df['TradeCost']
		return df.dropna()

	def split_factor_industry_grade(self,df,factor):
		use_col = factor if factor == 'Industry' else 'Grade_%s' %factor
		df = df.groupby(['TradingDay',use_col]).sum()
		#######################
		df['WeightedPct'] = df['Weight*Pct'] / df['Weight']
		df = df[['Weight','WeightedPct']].reset_index()
		df_Bench = get_factor_data_from_h5(factor,self.BenchMarkJY)
		_ = df_Bench.drop(['Pct'], axis=1, inplace=True)
		########################
		df = pd.merge(df,df_Bench, on=['TradingDay',use_col], suffixes=('_Real','_Bench'), how='outer')
		if self.BenchMarkJY == 46:
			df = df[df['TradingDay'] >= '20120101']
		else:
			min_date = min(df['TradingDay']).strftime('%Y%m%d')
			df = df[df['TradingDay'] >= max('20070104',min_date)]
			df = df[df['TradingDay'] < end_date]
		df = df.sort_values(['TradingDay',use_col]).fillna(0)
		###################################
		df['Real'] = df['Weight_Real'] * df['WeightedPct_Real']
		df['Bench'] = df['Weight_Bench'] * df['WeightedPct_Bench']
		#df['Neutral'] = df['WeightedPct_Bench'] * (df['Weight_Real'] - df['Weight_Bench'])
		df['Alpha'] = df['Real'] - df['Bench']
		df['Choice'] = df['Weight_Bench'] * (df['WeightedPct_Real'] - df['WeightedPct_Bench']) * (df['Weight_Real'] != 0)
		df['Neutral'] = df['WeightedPct_Bench'] * (df['Weight_Real'] - df['Weight_Bench'])
		######################################
		df = df.reset_index()[['TradingDay',use_col,'Real','Bench','Alpha','Neutral','Choice']]
		df['Year'] = df['TradingDay'].map(lambda k:k.year)
		df1 = df.groupby(['Year',use_col]).sum().reset_index()
		df2 = df.groupby(['Year']).sum().reset_index()
		df2[use_col] = 'Total'
		#####################################
		df = pd.concat([df1,df2], ignore_index=True)
		df = df[['Year',use_col,'Real','Bench','Alpha','Choice','Neutral']]
		if factor == 'Industry':
			df['IndustryChi'] = df[use_col].map(lambda k:IndustryChinese.get(k,'未知'))
		return self.df_standard(df)

	def insert_factor(self,df,factor,table):
		dfc = self.split_factor_industry_grade(df,factor)
		connBackTest.delete_insert(dfc,table,['Strategy'])

	def insert_industry_grade(self):
		if self.BenchMark == 0 or self.isTiming == 1 or self.isBeta == 1 or self.isLongShort == 1 or (self.BenchMark not in [50,300,500]):
			return
		df = self.merge_position_industry_grade()
		self.insert_factor(df,'Industry','alpha_strategy_annulized_industry_detail')
		self.insert_factor(df,'mv','alpha_strategy_annulized_grade_detail')
		self.insert_factor(df,'pe','alpha_strategy_annulized_pe_detail')
		self.insert_factor(df,'pb','alpha_strategy_annulized_pb_detail')
		self.insert_factor(df,'turn_rate','alpha_strategy_annulized_turnrate_detail')
		logging.info('Updating %s industry & Grade is ok.' %self.stra)

if __name__ == '__main__':
	pass