from ..base.cnst import *
all_sz_code = list(map(str,w.wset("sectorconstituent","date=%s;sectorid=a001010100000000"%TodayStr).Data[1]))
all_index = get_config_para('BasicPara','all_wind_index')
all_sz_code.extend(all_index)
###########################
class StrategyTickReturn():
	def __init__(self):
		self.all = connBackTest.read('*','strategy',"Deleted = 0").sort_values('Strategy')
		self.all = self.all.query("IsTiming == 0 & IsIndex == 0 & IsLongShort == 0 & IsOnlyReturn == 0 & StraStatus in ('In','Pre')")
		self.all['bench'] = self.all['BenchMark'].map(lambda k:dict(list(zip([50,300,500],all_index))).get(k,'0'))
		self.all_strategy = list(map(str,self.all['Strategy'].tolist()))
		self.position = self.get_position()
		self.beta_hedge = self.beta_hedge_strategy()
		
	def beta_hedge_strategy(self):
		beta_hedge_stra = self.all.query("IsBeta == 1")['Strategy'].tolist()
		sql_condi = "Strategy in ('%s')" %"','".join(beta_hedge_stra)
		df = connBackTest.read('*','alpha_strategy_daily_beta',sql_condi).sort_values(['Strategy','TradingDay'])
		return dict(df.groupby('Strategy')['Beta'].last())
		
	def get_position(self):
		table = "select Strategy,max(TradingDay) TradingDay from alpha_strategy_daily_position group by Strategy"
		condi = "a.Strategy = b.Strategy and a.TradingDay = b.TradingDay and b.Strategy in ('%s')" %"','".join(self.all_strategy)
		sql = "select a.Strategy,a.Symbol,a.ChiName,a.Weight from alpha_strategy_daily_position a INNER JOIN (%s)b on %s" %(table,condi)
		df = connBackTest.read_by_sql(sql)
		df['Symbol'] = df['Symbol'].map(lambda k:MyCode(k).wind_code())
		return df

	def get_wind_tick_pct(self):
		try:
			data = w.wsq(all_sz_code,['rt_pct_chg'])
			df = DataFrame(data.Data).T
			df.columns = ['Pct']
			df.insert(0,'Symbol',[str(k) for k in data.Codes])
			df = df.sort_values('Symbol')[['Symbol','Pct']]
			return df
		except:
			logging.warning('------obtaining tick pct is wrong------')
			time.sleep(15)
			return self.get_wind_tick_pct()

	def get_latest_pct(self):
		df = self.get_wind_tick_pct()
		bench_pct = df[df['Symbol'].isin(all_index)]
		bench_pct = dict(list(zip(bench_pct['Symbol'], bench_pct['Pct'])))
		return df,bench_pct

	def calculate_single_return(self,df):
		df.insert(len(df.columns),'CreateDate',datetime.today().strftime('%Y%m%d-%H:%M:%S'))
		connBackTest.delete_insert(df,'single_strategy_tick_pct',[])
		return 

	def calculate_return(self):
		tick_pct,bench_pct = self.get_latest_pct()
		self.all['bench_pct'] = self.all['bench'].map(lambda k:bench_pct.get(k,0))
		strategy_bench = dict(list(zip(self.all['Strategy'],self.all['bench_pct'])))
		df = pd.merge(self.position, tick_pct, on='Symbol', how='left').dropna()
		self.calculate_single_return(df)
		##############################
		df['long'] = df['Weight']*df['Pct']
		df = df.groupby('Strategy')[['long']].sum().reset_index()
		df['beta'] = df['Strategy'].map(lambda k:self.beta_hedge.get(k,1.0))
		df['bench'] = df['Strategy'].map(strategy_bench)
		df['alpha'] = df['long'] - df['beta']*df['bench']
		df = df[['Strategy','alpha','long','bench']]
		df.insert(len(df.columns),'CreateDate',datetime.today().strftime('%Y%m%d-%H:%M:%S'))
		connBackTest.delete_insert(df,'strategy_tick_pct',[])
		return 
