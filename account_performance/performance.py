from .var import *

class Performance(SymbolPerformance):
	def __init__(self):
		super().__init__()
		self.net_asset_update()
		self.position_ratio()
		self.stra_account_performance()
		self.stock_exposure()
		self.fut_position()
		
	def net_asset_update(self):
		holding_pnl = dict(self.holding_0.groupby('PortfolioID')['revenue'].sum())
		trading_pnl = dict(self.trading.groupby('PortfolioID')['revenue'].sum())
		self.ACCOUNT_PARA['net_asset_1'] = {key:value + holding_pnl.get(key,0) + trading_pnl.get(key,0) for key,value in 
											self.ACCOUNT_PARA['net_asset_0'].items()}
		self.ACCOUNT_PARA['net_value_1'] = {key:(self.ACCOUNT_PARA['net_asset_1'][key]/value) for key,value in
											self.ACCOUNT_PARA['share'].items()}
		self.new_net_value_insert()
		################################
		for i,df in enumerate([self.holding_0,self.holding_1,self.trading]):
			tmp_df = df[self.standard_col[i]]
			table = 'daily_'+ 'holding_cross'*(i==0) + 'holding'*(i==1) + 'trading'*(i==2)
			connOF.delete_insert(self.df_standard(tmp_df),table,['TradingDay'])
			######################################
			df['stra_type'] = df['Strategy'].map(self.stra_map_type)
			asset_dict_key = 'net_asset_0' if i==1 else 'net_asset_1'
			df['asset'] = df['PortfolioID'].map(self.ACCOUNT_PARA[asset_dict_key])
			
	def position_ratio(self):
		for ratio_type in ['Type','stra_type']:
			ratio = self.holding_1.groupby(['PortfolioID',ratio_type])[['volume']].sum().reset_index()
			ratio = self.common_ratio_process(ratio)
			table = 'secu_ratio' if ratio_type == 'Type' else 'strategy_ratio'
			connOF.delete_insert(self.df_standard(ratio),table,['TradingDay'])

	def common_ratio_process(self,df):
		df['ratio'] = df['volume'] / df['PortfolioID'].map(self.ACCOUNT_PARA['net_asset_1'])
		del df['volume']
		other = (1 - df.groupby('PortfolioID')[['ratio']].sum()).reset_index()
		other.insert(1,df.columns[1],'OTHER')
		df = pd.concat([df,other],ignore_index=True)
		return df

	def stra_account_performance(self):
		option = self.option_performance()
		bond   = self.bond_performance()
		specu  = self.specu_performance()
		alpha  = self.alpha_performance()
		df     = pd.concat([option,bond,specu,alpha],ignore_index=True).fillna(0)
		df['pnl'] = df['holding_pnl'] + df['trading_pnl']
		df['stra_type'] = df['Strategy'].map(self.stra_map_type)
		######################
		account_attribution = df.groupby('PortfolioID').apply(lambda k:AccountAttribution(k).attri()).reset_index()
		######################
		df = self.columns_in_right_order(df,self.performance_col)
		connOF.delete_insert(self.df_standard(df),'strategy_performance',['TradingDay'])
		#####################
		account_attribution = self.columns_in_right_order(account_attribution, self.attri_col)
		connOF.delete_insert(self.df_standard(account_attribution),'daily_attribution',['TradingDay'])

	def stock_exposure(self):
		df = StockExposure(self.holding_1).exposure_df
		df['asset'] = df['PortfolioID'].map(self.ACCOUNT_PARA['net_asset_1'])
		use_col = ['PortfolioID','exposure','exposure50','exposure300','exposure500','exposure1000','exposure9999']
		df['exposure'] = 0
		for col in use_col[2:]:
			df[col] = df[col] / df['asset']
			df['exposure'] += df[col]
		connOF.delete_insert(self.df_standard(df[use_col]),'stock_exposure',['TradingDay'])
	
	def fut_position(self):
		fut_holding = self.holding_1.query("Type == 'FUT'")[['PortfolioID','Symbol','Side','Quantity']]
		fut_holding['Symbol'] = fut_holding['Symbol'].map(lambda k:k[:6])
		#####
		fut_total = fut_holding.groupby('Symbol')[['Quantity']].sum().reset_index()
		fut_total.insert(0,'PortfolioID',998)
		_ = fut_total.rename(columns = {'Quantity':'Position'},inplace = True)
		fut_total['Position'] = fut_total['Position'].map(str)
		#####
		fut_detial = fut_holding.groupby(['PortfolioID','Symbol','Side'])[['Quantity']].sum().reset_index()
		fut_detial['Position'] = fut_detial['Side'].map({1:'+',-1:'-'}) + fut_detial['Quantity'].map(str)
		fut_detial = fut_detial.groupby(['PortfolioID','Symbol'])[['Position']].sum().reset_index()
		fut_detial = pd.concat([fut_detial,fut_total],ignore_index = True)
		connOF.delete_insert(self.df_standard(fut_detial),'daily_futures_position',['TradingDay'])
		return
		
	def option_performance(self):
		holding_df,trading_df = self.stra_type_filter('OP')
		holding_pnl = holding_df.groupby(self.group_col).apply(lambda k:StrategyAttribution(k).option_detail())
		return self.common_performance(holding_df,trading_df,holding_pnl)

	def bond_performance(self):
		holding_df,trading_df = self.stra_type_filter('Bond')
		holding_pnl = holding_df.groupby(self.group_col).apply(lambda k:StrategyAttribution(k).bond_detail())
		return self.common_performance(holding_df,trading_df,holding_pnl)

	def specu_performance(self):
		holding_df,trading_df = self.stra_type_filter(self.other_stra_type)
		holding_pnl = holding_df.groupby(self.group_col).apply(lambda k:StrategyAttribution(k).specu_detail())
		return self.common_performance(holding_df,trading_df,holding_pnl)

	def alpha_performance(self):
		holding_df,trading_df = self.stra_type_filter(['Alpha50','Alpha300','Alpha500'])
		holding_pnl = holding_df.groupby(self.group_col).apply(lambda k:StrategyAttribution(k).alpha_detail())
		return self.common_performance(holding_df,trading_df,holding_pnl)

	def stra_type_filter(self,stra_type):
		if isinstance(stra_type,str):
			sql = "stra_type == %r" %stra_type
		elif isinstance(stra_type,list):
			sql = "stra_type in ('%s')" %"','".join(stra_type)
		holding_0 = self.holding_0.query(sql)
		trading   = self.trading.query(sql)
		return holding_0,trading

	def common_performance(self,holding_df,trading_df,holding_pnl):
		len_1 = len(holding_df); len_2 = len(trading_df)
		trading_pnl = trading_df.groupby(self.group_col).apply(lambda k:StrategyAttribution(k).pnl())
		trading_pnl = trading_pnl.reset_index().rename(columns={0:'trading_pnl'})
		###############################
		if len_1 == len_2 == 0:
			return DataFrame()
		elif len_2 == 0:
			return holding_pnl.reset_index()
		elif len_1 == 0:
			return trading_pnl
		else:
			df = pd.merge(holding_pnl.reset_index(),trading_pnl,on=self.group_col,how='outer').fillna(0)
			return df


class StrategyAttribution(BasicPara):
	def __init__(self,df):
		super().__init__()
		self.df = df
		self.asset = self.df['asset'].tolist()[0]
		if 'volume' in self.df.columns:
			self.position = self.position_func()

	def sum(self,df,col='volume'):
		return 0.0 if len(df) == 0 else df[col].sum()

	def long_position(self):
		df = self.df.query("Side == 1")
		return self.sum(df)

	def stock_long_position(self):
		df = self.df.query("Type == 'STOCK'")
		return self.sum(df)

	def short_position(self):
		df = self.df.query("Side == -1")
		return self.sum(df)

	def fut_short_position(self):
		df = self.df.query("(Side == -1)&(Type == 'FUT')")
		return self.sum(df)

	def fut_long_position(self):
		df = self.df.query("(Side == 1)&(Type == 'FUT')")
		return self.sum(df)

	def position_func(self):
		return max(self.long_position(),self.short_position())

	def weight(self):
		return self.position / self.asset

	def exposure(self):
		up = self.long_position() - self.short_position()
		return up / self.position

	def pnl(self):
		return self.df['revenue'].sum() / self.asset

	def specific_pnl(self,Type):
		df = self.df.query("Type == %r"%Type)
		return self.sum(df,'revenue') / self.asset

	def long_pnl(self):
		df = self.df.query("Side == 1")
		return self.sum(df,'revenue')

	def short_pnl(self):
		df = self.df.query("Side == -1")
		return self.sum(df,'revenue')

	def common_detail(self):
		result = dict()
		result['Position'] = self.position
		result['Weight']   = self.weight()
		result['holding_pnl'] = self.pnl()
		result['asset'] = self.asset
		return result

	def specu_detail(self):
		result = self.common_detail()
		return Series(result)

	def option_detail(self):
		result = self.common_detail()
		result['other_pnl'] = result['holding_pnl'] - self.specific_pnl('OP')
		for col in self.op_col:
			result[col] = self.df[col].sum() / self.asset
		return Series(result)

	def bond_detail(self):
		result = self.common_detail()
		result['other_pnl'] = result['holding_pnl'] - self.specific_pnl('BOND')
		for col in self.bond_col:
			result[col] = self.df[col].sum() / self.asset
		return Series(result)

	def alpha_detail(self):
		result = self.common_detail()
		result['exposure'] = self.exposure()
		result['alpha'],result['exposure'],result['basis'] = self.alpha_expusore_basis()
		return Series(result)

	def alpha_expusore_basis(self):
		tmp_1,tmp_2 = self.index_tmp_pnl()
		alpha       = self.long_pnl() - tmp_1
		exposuree   = tmp_1 - tmp_2
		basis       = tmp_2 + self.short_pnl()
		return [k/self.position for k in [alpha,exposuree,basis]]

	def index_tmp_pnl(self):
		index_pct = self.bench_pct[self.df['stra_type'].tolist()[0]]
		tmp_1     = self.long_position() * index_pct
		tmp_2     = self.short_position() * index_pct
		return tmp_1,tmp_2


class AccountAttribution(BasicPara):
	def __init__(self,df):
		super().__init__()
		self.df = df

	def sum(self,df,col):
		return 0.0 if len(df) == 0 else df[col].sum()

	def attri(self):
		result = {}
		for col in self.alpha_col+self.op_col+self.bond_col:
			if col in self.df.columns:
				result[col] = self.df[col].sum()
		for col in self.other_stra_type:
			result[col] = self.specific_pnl(col)
		result['other_pnl'] = self.df['other_pnl'].sum()
		result['trading_pnl'] = self.trading_pnl()
		return Series(result)

	def specific_pnl(self,Type):
		df = self.df.query("stra_type == %r" %Type)
		return self.sum(df,'pnl')

	def trading_pnl(self):
		sql = "stra_type not in ('%s')" %"','".join(self.other_stra_type)
		df = self.df.query(sql)
		return self.sum(df,'trading_pnl')


class StockExposure():
	def __init__(self,df):
		self.df = df.query("Type in ('STOCK','FUT')").copy() 
		self.df['fut_type'] = self.df['Symbol'].map(lambda k:k[:2])
		
		self.index_component = list(map(self.index_code,['50','300','500','1000']))
		self.stock9999 = list(set.union(*list(map(set,self.index_component))))
		self.exposure_df = self.df.groupby('PortfolioID').apply(self.exposure).reset_index()

	def sum(self,df,col='volume'):
		return 0.0 if len(df) == 0 else df[col].sum()

	def exposure(self,df):
		result = dict()
		stock50,stock300,stock500,stock1000 = map(lambda code:self.sum(df[df['Symbol'].isin(code)]),self.index_component)
		stock9999 = self.sum(df[~df['Symbol'].isin(self.stock9999)])

		short50,short300,short500 = map(lambda fut:self.sum(df[(df['fut_type']==fut)&(df['Side']==-1)]), ['IH','IF','IC'])
		long50, long300,  long500 = map(lambda fut:self.sum(df[(df['fut_type']==fut)&(df['Side']== 1)]), ['IH','IF','IC'])

		result['exposure50']   = stock50  - short50  + long50
		result['exposure300']  = stock300 - short300 + long300 - stock50
		result['exposure500']  = stock500 - short500 + long500
		result['exposure1000'] = stock1000
		result['exposure9999'] = stock9999
		return Series(result)

	def index_code(self,index_type):
		add_code = {'50':['510050.SH'],'300':['510300.SH'],'500':['510500.SH']}
		all_code = [k.strip('\n') for k in open('lht/dz/IndexCompose/%s.txt'%index_type).readlines()]	
		all_code.extend(add_code.get(index_type,[]))
		if index_type != '1000':
			return all_code
		temp1 = set(all_code + self.index_code('1800'))
		temp2 = set(self.index_code('300') + self.index_code('500'))
		return list(temp1 - temp2)
