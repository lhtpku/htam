from ..base.cnst import *
TimeTick = TimeNow()
NowTick = TimeTick.get_now()
###############
TodayStr     = '20180709'
YesterdayStr = all_jy_tradingday[all_jy_tradingday.index(TodayStr) - 1]
print(TodayStr)
#############################
DATA_ROOT      = 'C:/Users/liuhongtao/Desktop/DailyHolding'
DATA_ROOT_TODAY = os.path.join(DATA_ROOT, TodayStr)
DATA_ROOT_YESTERDAY = os.path.join(DATA_ROOT, YesterdayStr)
###################################
class BasicPara():
	def __init__(self):
		self.path_name = ['Holding%s.csv' %YesterdayStr,'Holding%s.csv' %TodayStr,'Trading%s.csv' %TodayStr]
		self.main_run()
		
	def main_run(self):
		self.get_net_value()
		self.all_col_by_order()
		self.alpha_para()
		self.get_stra_type()

	def df_standard(self,df):
		if 'TradingDay' not in df.columns:
			df.insert(0,'TradingDay',pd.to_datetime(TodayStr))
		df.insert(len(df.columns),'CreateDate',NowTick)
		return df.fillna(0)

	def get_net_value(self):
		self.ACCOUNT_PARA = {}
		net_value =  pd.read_excel('%s/%s.xlsx' %(DATA_ROOT_YESTERDAY, YesterdayStr))
		net_value.insert(0,'TradingDay',pd.to_datetime(YesterdayStr))
		connOF.delete_insert(self.df_standard(net_value),'net_value_real',['TradingDay'])
		############################
		self.ACCOUNT_PARA['net_value_0'] = dict(zip(net_value['PortfolioID'],net_value['NetValue']))
		self.ACCOUNT_PARA['net_value_1'] = self.ACCOUNT_PARA['net_value_0']
		self.ACCOUNT_PARA['net_asset_0'] = dict(zip(net_value['PortfolioID'],net_value['NetAsset']))
		self.ACCOUNT_PARA['net_asset_1'] = self.ACCOUNT_PARA['net_asset_0']
		self.ACCOUNT_PARA['share'] = dict(zip(net_value['PortfolioID'],net_value['Share']))

	def new_net_value_insert(self):
		tmp_max_day = connOF.read('max(TradingDay)','net_value_real','').iloc[0,0].strftime('%Y%m%d')
		#################################
		cols = ['PortfolioID','value','asset','share']
		dicts = [self.ACCOUNT_PARA['net_value_1'],self.ACCOUNT_PARA['net_asset_1'],self.ACCOUNT_PARA['share']]
		df = DataFrame(dict(zip(cols[1:],dicts))).reset_index().rename(columns={'index':cols[0]})[cols]
		df['value'] = df['value'].map(lambda k:round(k,4))
		connOF.delete_insert(self.df_standard(df),'net_value_real',['TradingDay'])
		return df

	def all_col_by_order(self):
		add_func = lambda a,b: a + b
		###############################
		self.other_stra_type = ['NewStock','Speculate','CvBond','CTA','Suspend']
		self.group_col = ['PortfolioID','Strategy']
		self.basic_col  = ['Weight','Position','pnl','holding_pnl','trading_pnl','other_pnl']
		self.alpha_col = ['alpha','exposure','basis']
		self.op_col = ['%s_pnl'%col for col in ['delta','gamma','vega','theta','epsilon']]
		self.bond_col = ['%s_pnl'%col for col in ['clean','interest']]
		self.performance_col = reduce(add_func,[self.group_col,self.basic_col,self.alpha_col,self.op_col,self.bond_col])
		self.attri_col = reduce(add_func,[['PortfolioID'],self.other_stra_type,self.alpha_col,self.op_col,self.bond_col,['trading_pnl','other_pnl']])
		###################
		tmp_col = ['PortfolioID','Strategy','Symbol','Type','Side','Quantity','multiplier']
		trading_col   = tmp_col + ['FilledPrice','close_1','revenue']
		holding_1_col = tmp_col + ['close_1','volume']
		holding_0_col = reduce(add_func,[tmp_col, ['close_0','close_1','volume','revenue'], self.bond_col, self.op_col])
		self.standard_col  = [holding_0_col, holding_1_col, trading_col]
		###################

	def columns_in_right_order(self,df,cols):
		for col in cols:
			if col not in df.columns:
				df[col] = 0
		return df[cols]

	def get_fut_code(self):
		fut_type  = ['IF','IH','IC']
		fut_month = [str(k).rjust(2,'0') for k in range(4)]
		fut_code  = ['%s%s.CFE'%(cat,month) for cat in fut_type for month in fut_month]
		return fut_code

	def alpha_para(self):
		data = w.wss(['000300.SH','000016.SH','000905.SH'], 'pct_chg', "tradeDate=%s"%TodayStr, "")
		tmp  = ['Alpha300','Alpha50','Alpha500']
		self.bench_pct = {bench:pct/100 for bench,pct in zip(tmp,data.Data[0])}

	def get_stra_type(self):
		self.strategy = pd.read_excel('%s/Strategy.xlsx'%DATA_ROOT)
		self.all_strategy = self.strategy['Name'].tolist()
		self.stra_map_type = dict(zip(self.strategy['Name'],self.strategy['StrategyType']))


class DataFromWind(BasicPara):
	def __init__(self):
		super().__init__()
		self.get_daily_path()
		self.data_in_json()

	def path_append(self,dir_path,file):
		dir_file_path = os.path.join(dir_path,file)
		#############################
		if file == self.path_name[0]:
			self.holding_0_path.append(dir_file_path)
		elif file == self.path_name[1]:
			self.holding_1_path.append(dir_file_path)
		elif file == self.path_name[2]:
			self.trading_path.append(dir_file_path)

	def get_daily_path(self):
		self.holding_0_path, self.holding_1_path, self.trading_path = [], [], []
		for root,dirs,files in os.walk(DATA_ROOT):
			for file in files:
				if 'stephen' in root:
					continue
				self.path_append(root,file)
		self.all_path = [self.holding_0_path, self.holding_1_path, self.trading_path]
		############################
		stephen_path = os.path.join(DATA_ROOT_TODAY, 'stephen')
		if os.path.exists(stephen_path):
			shutil.rmtree(stephen_path)
		# if not os.path.exists(stephen_path):
		os.mkdir(stephen_path)

	def path_df_concat(self,func,path_list):
		df_list = map(func,path_list)
		df = pd.concat(df_list, ignore_index=True)
		return df

	def stephen_data_concat(self):
		'''
		get holding & trading's symbol, which is used for data downloading.
		'''
		symbol_path = os.path.join(DATA_ROOT_TODAY,'stephen','stephen.xlsx')
		if os.path.exists(symbol_path):
			return pd.read_excel(symbol_path)
		################################
		tmp_all = []
		for i,path_list in enumerate(self.all_path):
			df = self.path_df_concat(lambda path:pd.read_csv(path),path_list)#[['Strategy','Type','Symbol']]
			df['Quantity'] = df['Quantity'].map(lambda num: eval(str(num).replace(',','')))
			df = df[df['Quantity'] > 0]
			df.to_csv(os.path.join(DATA_ROOT_TODAY,'stephen',self.path_name[i]), index=False)
			tmp_all.append(df)
		############################
		tmp_all = pd.concat(tmp_all, ignore_index=True).query("Strategy != 'S6001'")
		tmp_all['Symbol'] = tmp_all['Symbol'].map(str)
		tmp_all['Type']   = tmp_all['Type'].map(str.upper)
		tmp_all.to_excel(symbol_path, index=False)
		return tmp_all

	def get_symbol_by_cate(self):
		df = self.stephen_data_concat()
		self.all_symbol_cate = ['STOCK','BOND','CVBOND','FUT','OP']
		get_special_type_code = lambda category: df.query("Type == %r"%category)['Symbol'].unique().tolist()
		self.all_symbol = list(map(get_special_type_code,self.all_symbol_cate))
		self.all_symbol[3] = self.get_fut_code()
		##########################
		stk_index  = ["close"]
		bond_index = "dirtyprice,cleanprice,accruedinterest,accrueddays,durationifexercise".split(',')
		cb_index   = ["close"]
		fut_index  = ['trade_hiscode','settle']
		op_index   = "close,delta,gamma,vega,theta,rho,us_impliedvol,us_change".split(',')
		self.all_symbol_index = [[k.upper() for k in kk] for kk in [stk_index,bond_index,cb_index,fut_index,op_index]]
		###########################

	def data_in_json(self):
		self.get_symbol_by_cate()
		for datee in [YesterdayStr,TodayStr]:
			JSON = {}
			json_path = os.path.join(DATA_ROOT_TODAY,'stephen','wind_api_data_%s.json'%datee)
			if os.path.exists(json_path):
				continue
			date = 'tradeDate=%s'%datee
			##############################
			for i,cate in enumerate(self.all_symbol_cate):
				if cate == 'STOCK':
					wind_data = w.wss(self.all_symbol[i],self.all_symbol_index[i],date,'priceAdj=F')
				else:
					wind_data = w.wss(self.all_symbol[i],self.all_symbol_index[i],date)
				df = DataFrame(columns=wind_data.Codes,index=wind_data.Fields,data=wind_data.Data).T.reset_index()
				if cate == 'FUT':
					del df['index']
				df = df.rename(columns={'index':'CODE','TRADE_HISCODE':'CODE','SETTLE':'CLOSE'})
				if len(df) < len(self.all_symbol[i]):
					print(cate,len(self.all_symbol[i]),len(df),'somedata is missing with wind-api, please have a check.')
					break
				######################
				for col in df.columns:
					if col == 'CODE':
						continue
					tmp_dict = dict(zip(df['CODE'],df[col]))
					JSON.setdefault(col.lower(),{}).update(tmp_dict)
			with open(json_path,'w') as f:
				json.dump(JSON,f)
		return

		
class SymbolMapData(DataFromWind):
	def __init__(self):
		super().__init__()
		self.map_all_data()

	def map_all_data(self):
		self.holding_0,self.holding_1,self.trading = self.get_holding_trading_data()
		self.get_close_0(self.holding_0)
		self.get_other_para()

	def get_holding_trading_data(self):
		self.load_json_data()
		path_list = [os.path.join(DATA_ROOT_TODAY,'stephen',path) for path in self.path_name]
		df_list   = [pd.read_csv(path) for path in path_list]
		df_list   = [self.get_close_1(df) for df in df_list]
		return df_list

	def get_close_0(self,df):
		df['close_0'] = df['Symbol'].map(self.json_data_0['close'])
		### 
		df.loc[df['Type'].isin(['RREPO','MF']),'close_0'] = 100
		### 
		df.loc[df['Type']=='BOND','close_0'] = df['Symbol'].map(self.json_data_0['dirtyprice'])
		### 
		df.loc[np.isnan(df['close_0'])&(df['Type']=='STOCK'),'close_0'] = 0.694*df['close_1']
		###
		df['is_out'] = df['Type'].isin(['OP','FUT']) & np.isnan(df['close_1'])
		df = df.query("is_out == 0")
		del df['is_out']
		return df

	def get_other_para(self):
		for i,cate in enumerate(self.all_symbol_cate):
			if cate == 'BOND':
				for col in self.all_symbol_index[i][:-1]:
					col = col.lower()
					self.holding_0['%s_0'%col] = self.holding_0['Symbol'].map(self.json_data_0[col])
					self.holding_0['%s_1'%col] = self.holding_0['Symbol'].map(self.json_data_1[col])
				##############################
				tmp_condi = self.holding_0['accrueddays_0']>self.holding_0['accrueddays_1']
				self.holding_0.loc[tmp_condi,'accruedinterest_1'] += self.holding_0['accruedinterest_0']
				self.holding_0.loc[tmp_condi,'close_1'] += self.holding_0['accruedinterest_0'] 
			elif cate == 'OP':
				for col in self.all_symbol_index[i][1:]:
					col = col.lower()
					if col == 'us_change':
						self.holding_0[col] = self.holding_0['Symbol'].map(self.json_data_1[col])
					elif col == 'us_impliedvol':
						tmp1,tmp2 = self.holding_0['Symbol'].map(self.json_data_1[col]), self.holding_0['Symbol'].map(self.json_data_0[col])
						self.holding_0['iv'] = 100 * (tmp1 - tmp2)
					else:
						self.holding_0[col] = self.holding_0['Symbol'].map(self.json_data_0[col])
				####
				self.holding_0['op_t'] = w.tdayscount(YesterdayStr,TodayStr,"Days=Alldays").Data[0][0] / 365.0

	def load_json_data(self):
		json_path_0 = os.path.join(DATA_ROOT_TODAY,'stephen','wind_api_data_%s.json'%YesterdayStr)
		json_path_1 = os.path.join(DATA_ROOT_TODAY,'stephen','wind_api_data_%s.json'%TodayStr)
		with open(json_path_0, 'r') as f:
			self.json_data_0 = json.load(f)
		with open(json_path_1, 'r') as f:
			self.json_data_1 = json.load(f)

	def get_close_1(self,df):
		###
		df = self.add_multiplier(df)
		###
		df['Side'] = df['Side'].map({'LONG':1,'SHORT':-1,'BUY':1,'SELL':-1})
		###
		df['close_1'] = df['Symbol'].map(self.json_data_1['close'])
		###
		df.loc[df['Type'].isin(['RREPO','MF']),'close_1'] = 100
		###
		if 'FilledPrice' in df.columns:
			df.loc[df['Type'].isin(['RREPO','MF']),'FilledPrice'] = 100
			df.loc[df['Type']=='BOND','close_1'] = df['Symbol'].map(self.json_data_1['cleanprice'])
		else:
			df.loc[df['Type']=='BOND','close_1'] = df['Symbol'].map(self.json_data_1['dirtyprice'])
		return df

	def add_multiplier(self,df):
		df['multiplier'] = 0
		df.loc[df['Type']=='OP','multiplier'] = 10000
		df['multiplier'] += df['Symbol'].map(lambda k:k.startswith('IH')) * 300
		df['multiplier'] += df['Symbol'].map(lambda k:k.startswith('IF')) * 300
		df['multiplier'] += df['Symbol'].map(lambda k:k.startswith('IC')) * 200
		return df.replace({'multiplier':{0:1}})


class SymbolPerformance(SymbolMapData):
	def __init__(self):
		super().__init__()
		self.get_all_para()

	def get_all_para(self):
		self.common_para()
		self.holding_0 = self.bond_para(self.holding_0)
		self.holding_0 = self.option_para(self.holding_0)

	def common_para(self):
		self.holding_1['volume']  = self.holding_1['close_1'] * self.holding_1['Quantity'] * self.holding_1['multiplier']
		self.holding_0['volume']  = self.holding_0['close_0'] * self.holding_0['Quantity'] * self.holding_0['multiplier']
		self.holding_0['revenue'] = self.holding_0['Quantity'] * self.holding_0['multiplier'] * self.holding_0['Side']*\
									(self.holding_0['close_1'] - self.holding_0['close_0'])
		self.trading['revenue']   = self.trading['Quantity'] * self.trading['multiplier'] * self.trading['Side'] *\
									(self.trading['close_1'] - self.trading['FilledPrice'])

	def bond_para(self,df):
		df['clean_pnl']    = df['cleanprice_1'] - df['cleanprice_0']
		df['interest_pnl'] = df['accruedinterest_1'] - df['accruedinterest_0']
		for col in self.bond_col:
			df[col] = df['Side']*df['Quantity']*df[col]
		return df

	def option_para(self,df):
		df['delta_pnl'] = df['delta'] * df['us_change']
		df['gamma_pnl'] = 0.5 * df['gamma'] * df['us_change'] *  df['us_change']
		df['theta_pnl'] = df['theta'] * df['op_t']
		df['vega_pnl']  = df['vega'] * df['iv']
		for col in self.op_col[:-1]:
			df[col] = 10000 * df['Side'] * df['Quantity'] * df[col]
		df['epsilon_pnl'] = df['revenue']-df['delta_pnl']-df['gamma_pnl']-df['theta_pnl']-df['vega_pnl']
		return df

######################################
def insert_history_value():
	value_path = 'C:/Users/liuhongtao/Desktop/DailyHolding1/value'
	path_lists = MyDir(value_path).whole_file_path('.xlsx')[-1:]
	for path in path_lists:
		print(path)
		df = pd.read_excel(path).rename(columns={'TradeDate':'TradingDay'})
		df['TradingDay'] = df['TradingDay'].map(lambda k:pd.to_datetime(str(int(k))))
		df.insert(len(df.columns),'CreateDate',NowTick)
		connOF.delete_insert(df,'net_value_real',['TradingDay'])
	return