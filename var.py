from ..base.dbclass import *

TodayStr     = '20180619'
YesterdayStr = '20180615'

DATA_TOOT_PATH = 'C:/Users/liuhongtao/Desktop/dz'

'''
整合持仓
下载数据：股票，债券，期权，股指期货，存np？



map所有的数据

按照策略划分，进行策略层面上的归因，比如alpha归为哪几类 op归为哪几类
在账户层面上，将策略归因进行叠加。
分别按照 normal op bnd 三类进行叠加，将数据存储于三个表格中？
or 直接在js中处理。

'''
class DailyData(object):
	"""give data a uniform format"""
	def __init__(self):
		self.root_path = DATA_TOOT_PATH
		self.path_name = ['Holding%s.csv' %YesterdayStr,'Holding%s.csv' %TodayStr,'Trading%s.csv' %TodayStr]
		self.daily_path()
		self.all_path = [self.holding_0_path, self.holding_1_path, self.trading_path]

	def path_append(self,dir_path,file):
		dir_file_path = os.path.join(dir_path,file)
		if file == self.path_name[0]:
			self.holding_0_path.append(dir_file_path)
		elif file == self.path_name[1]:
			self.holding_1_path.append(dir_file_path)
		elif file == self.path_name[2]:
			self.trading_path.append(dir_file_path)

	def daily_path(self):
		self.holding_0_path, self.holding_1_path, self.trading_path = [], [], []
		for root,dirs,files in os.walk(self.root_path):
			for file in files:
				if 'all' in root:
					continue
				self.path_append(root,file)

	def data_concat(self):
		for i,path_list in enumerate(self.all_path):
			df_list = map(lambda path:pd.read_csv(path),path_list)
			df = pd.concat(df_list,ignore_index=True)
			if 'AvailableQuantity' in df.columns:
				del df['AvailableQuantity']
			df.to_csv(os.path.join(DATA_TOOT_PATH,'all',self.path_name[i]), index=False)

	def get_symbol(self):
		path = os.path.join(DATA_TOOT_PATH,'all','all.xlsx')
		if os.path.exists(path):
			df = pd.read_excel(path)
		else:
			self.data_concat()
			get_type_symbol = lambda path:pd.read_csv(os.path.join(DATA_TOOT_PATH,'all',path))[['Strategy','Type','Symbol']]
			df = map(get_type_symbol, self.path_name)
			df = pd.concat(df,ignore_index=True)
			df.to_excel(os.path.join(DATA_TOOT_PATH,'all','all.xlsx'),index=False)
			df = df.query("Strategy != 'S6001'")
		df['Symbol'] = df['Symbol'].map(str)
		df['Type']   = df['Type'].map(str.upper)
		return df

	def get_fut_code(self):
		fut_type  = ['IF','IH','IC']
		fut_month = [str(k).rjust(2,'0') for k in range(4)]
		fut_code  = ['%s%s.CFE'%(cat,month) for cat in fut_type for month in fut_month]
		return fut_code

	def get_symbol_by_cate(self):
		df = self.get_symbol()
		self.all_symbol_cate = ['STOCK','BOND','CVBOND','FUT','OP']
		get_code = lambda df1: df1['Symbol'].unique().tolist()
		get_special_type_code = lambda category: get_code(df.query("Type == %r"%category))
		self.all_symbol = list(map(get_special_type_code,self.all_symbol_cate))
		self.all_symbol[3] = self.get_fut_code()
		# print([len(code) for code in self.all_symbol])
		##########################
		stk_index  = ["close"]
		bond_index = "dirtyprice,cleanprice,accruedinterest,durationifexercise".split(',')
		cb_index   = ["close"]
		fut_index  = ['trade_hiscode','settle']
		op_index   = "close,delta,gamma,vega,theta,rho,us_impliedvol,us_change".split(',')
		self.all_symbol_index = [stk_index,bond_index,cb_index,fut_index,op_index]
		self.all_symbol_index = [[k.upper() for k in kk] for kk in self.all_symbol_index]
		###########################

	def wind_api_func(self):
		self.get_symbol_by_cate()
		for datee in [YesterdayStr,TodayStr]:
			DATA_JSON = {}
			json_path = os.path.join(DATA_TOOT_PATH,'all','data%s.json'%datee)
			if os.path.exists(json_path):
				# print('%s has already existed.'%json_path)
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
				if len(df) < self.all_symbol[i]:
					print(cate,len(self.all_symbol[i]),len(df),'something is wrong with wind-api, be careful')
					break
				######################
				for col in df.columns:
					if col == 'CODE':
						continue
					tmp_dict = dict(zip(df['CODE'],df[col]))
					DATA_JSON.setdefault(col.lower(),{}).update(tmp_dict)
			with open(json_path,'w') as f:
				json.dump(DATA_JSON,f)
		return

		
class SecurityParameter(DailyData):
	def __init__(self):
		super().__init__()
		self.wind_api_func()

	#### 导入持仓与交易数据
	def process_data(self):
		holding_trading_data = self.load_json_data()
		self.holding_0,self.holding_1,self.trading = holding_trading_data
		### 考虑收盘价
		self.get_close_0()
		### 将BOND & OP 的指标加入0日持仓。
		self.get_other_para()
		return 

	def get_other_para(self):
		for i,cate in enumerate(self.all_symbol_cate):
			if cate == 'BOND':
				for col in self.all_symbol_index[i][:-1]:
					col = col.lower()
					self.holding_0['%s_0'%col] = self.holding_0['Symbol'].map(self.json_data_0[col])
					self.holding_0['%s_1'%col] = self.holding_0['Symbol'].map(self.json_data_1[col])

			elif cate == 'OP':
				for col in self.all_symbol_index[i][1:]:
					col = col.lower()
					if col == 'us_change':
						self.holding_0[col] = self.holding_0['Symbol'].map(self.json_data_1[col])
					elif col == 'us_impliedvol':
						self.holding_0['iv'] = self.holding_0['Symbol'].map(self.json_data_1[col])-self.holding_0['Symbol'].map(self.json_data_0[col])
					else:
						self.holding_0[col] = self.holding_0['Symbol'].map(self.json_data_0[col])
				#### 加入iv&t
				self.holding_0['op_t'] = w.tdayscount(YesterdayStr,TodayStr,"Days=Alldays").Data[0][0] / 365.0
				# self.holding_0['iv'] = self.holding_0['us_impliedvol_1'] - self.holding_0['us_impliedvol_0']
					
	def get_close_0(self):
		self.holding_0['close_0'] = self.holding_0['Symbol'].map(self.json_data_0['close'])
		### 现金 close_0
		self.holding_0.loc[self.holding_0['Type'].isin(['RREPO','MF']),'close_0'] = 100
		### 债券 close_0
		self.holding_0.loc[self.holding_0['Type']=='BOND','close_0'] = self.holding_0['Symbol'].map(self.json_data_0['dirtyprice'])
		### 新股 close_0
		self.holding_0.loc[np.isnan(self.holding_0['close_0'])&(self.holding_0['Type']=='STOCK'),'close_0'] = 0.694*self.holding_0['close_1']
		### 去掉可能的过期合约
		self.holding_0['is_out'] = self.holding_0['Type'].isin(['OP','FUT']) & np.isnan(self.holding_0['close_1'])
		self.holding_0 = self.holding_0.query("is_out == 0")
		del self.holding_0['is_out']

	def get_close_1(self,df):
		### 统一单位or点数
		df = self.add_multiplier(df)
		### 收盘价
		df['close_1'] = df['Symbol'].map(self.json_data_1['close'])
		### 现金 close_1
		df.loc[df['Type'].isin(['RREPO','MF']),'close_1'] = 100
		### 债券 close_1
		df.loc[df['Type'] == 'BOND','close_1'] = df['Symbol'].map(self.json_data_1['dirtyprice'])
		return df

	#### 导入json数据 & 持仓与交易数据
	def load_json_data(self):
		json_path_0 = os.path.join(DATA_TOOT_PATH,'all','data%s.json'%YesterdayStr)
		json_path_1 = os.path.join(DATA_TOOT_PATH,'all','data%s.json'%TodayStr)
		with open(json_path_0, 'r') as f:
			self.json_data_0 = json.load(f)
		with open(json_path_1, 'r') as f:
			self.json_data_1 = json.load(f)
		holding_trading_path = [os.path.join(DATA_TOOT_PATH,'all',path) for path in self.path_name]
		holding_trading_data = [pd.read_csv(path) for path in holding_trading_path]
		holding_trading_data = [self.get_close_1(df) for df in holding_trading_data]
		return holding_trading_data

	def add_multiplier(self,df):
		df['multiplier'] = 0
		df.loc[df['Type'] == 'OP','multiplier'] = 10000
		df['multiplier'] += df['Symbol'].map(lambda k:k.startswith('IH')) * 300
		df['multiplier'] += df['Symbol'].map(lambda k:k.startswith('IF')) * 300
		df['multiplier'] += df['Symbol'].map(lambda k:k.startswith('IC')) * 200
		return df.replace({'multiplier':{0:1}})











						












class BasicParameter():
	def __init__(self):
		self.time_tick = timeNow()
		self.now = self.time_tick.getThisTick()
		self.connAMS = connAMS
		self.fut_code_()
		self.basic_dict()
		self.date_process()
		self.asset_to_db()
		self.account = self.account_attri()
		logging.debug(self.account)
		self.account_attri_dict()
		logging.debug(self.account_share_dict)
		self.strategy()
		self.old_sh,self.old_sz = self.old_stock()
		logging.warning("Basic para set in class Parameter is ok.")

	def date_process(self):
		self.today_str = TodayStr
		self.yesterday_str = YesterdayStr

	def fut_code_(self):
		self.fut_code_type = ['IF','IH','IC']
		fut_code_month = [str(k).rjust(2,'0') for k in range(4)]
		self.fut_code = [type_ +month +'.CFE' for type_ in self.fut_code_type for month in fut_code_month]

	def basic_dict(self):
		self.fut_multiplier = twoList(self.fut_code_type,[300,300,200]).to_dict()
		self.direction_dict = {'LONG': 1, 'SHORT': -1, 'BUY': 1, 'SELL': -1}
		self.index_code = twoList(self.fut_code_type,['000300.SH','000016.SH','000905.SH']).to_dict()

	def asset_to_db(self):
		daily_value_path = 'D:/DailyReport/DailyValuation/%s/' % self.yesterday_str
		ReName1 = {0:'PortfolioID',1:'Share'}
		ReName2 = {0:'PortfolioID',1:'Asset',2:'value'}
		share = pd.read_csv('%sShareTable.csv' %daily_value_path,header=None)
		share = share.rename(columns = ReName1).applymap(float)
		value = pd.read_csv('%s%s.csv'%(daily_value_path,self.yesterday_str), header=None)
		value = value.rename(columns = ReName2).applymap(float)
		df = pd.merge(value,share,on = 'PortfolioID')
		df.insert(0,'TradingDay',pd.to_datetime(self.yesterday_str))
		df.insert(len(df.columns),'CreateDate',self.now)
		self.connAMS.delete_insert(df,'account_daily_asset',['TradingDay'])
		logging.debug("insert share & asset to db is ok.")

	def account_attri(self):
		portfolio = self.connAMS.read('*','portfolio','Deleted = 0')
		portfolio['Account'] = portfolio['Account'].map(str)
		asset = self.connAMS.read('*','account_daily_asset','TradingDay = %s'%self.yesterday_str)
		return pd.merge(portfolio,asset,on = 'PortfolioID')

	def account_dict(self,Col):
		return twoList(self.account['PortfolioID'],self.account[Col]).to_dict()

	def account_attri_dict(self):
		[self.account_account_dict,
		self.account_netvalue_dict,
		self.account_share_dict,
		self.account_asset_dict,
		self.account_chiname_dict] = \
		list(map(self.account_dict,['Account','NetValue','Share','TotalAsset','ChiName']))
		self.account_portfolioID_dict = {value:key for key,value in list(self.account_account_dict.items())}

		self.account_today_asset_dict = {}
		self.account_today_value_dict = {}

		self.all_account = myList(list(self.account_account_dict.values())).sort_list()
		self.all_account_virtual = ['RuiTai']
		self.all_account_real = [acc for acc in self.all_account if acc not in self.all_account_virtual]

	def old_stock(self):
		old_fixed = pd.read_excel('lht/ams/IndexCompose/OldFixed.xlsx')
		old_fixed['PortfolioID'] = old_fixed['Account'].map(self.account_portfolioID_dict)
		old_sh = twoList(old_fixed['PortfolioID'],old_fixed['SH']).to_dict()
		old_sz = twoList(old_fixed['PortfolioID'],old_fixed['SZ']).to_dict()
		return old_sh,old_sz

	def get_set(self,LL):
		return set(LL.unique())

	def strategy(self):
		table = pd.read_csv(open('D:/DailyReport/Strategy.csv'))
		table['Name'] = table['Name'].map(str)

		self.alpha_strategy = self.get_set(table.query("StrategyType == 'ALPHA'")['Name'])
		self.alpha_300 = self.get_set(table.query("StrategyType == 'ALPHA' and BenchmarkISIN == 4003145")['Name'])
		self.alpha_500 = self.get_set(table.query("StrategyType == 'ALPHA' and BenchmarkISIN == 4004978")['Name'])
		self.alpha_50 = self.get_set(table.query("StrategyType == 'ALPHA' and BenchmarkISIN == 4000046")['Name'])

		self.long_strategy = self.get_set(table.query("StrategyType != 'ALPHA'")['Name'])
		self.speculate_strategy = self.get_set(table.query("StrategyType == 'SPECULATE'")['Name'])

		self.ticket = ['S0050', 'S0052', 'S0051','S0053','S0054','S0050A']
		self.fenji = ['S0000']
		self.new = ['S0001']
		self.bond = ['S0002']
		self.mini = ['S9999']
		self.timing = ['S2121', 'S2122']

		temp = self.ticket + self.fenji + self.new + self.bond + self.mini + self.timing

		self.netlong = self.long_strategy - set(temp)
		# self.allocate500 = ['S2124','S2128']
		# self.trade500 = ['S2121','S2122']
		# self.alpha500 = ['S1601A','S1202A','S1202C']
		logging.debug("get strategy in.")


class FormatStandard():
	def code(self,Type,Code):
		Code = str(Code).rjust(6,'0')
		if Type == 'CS':
			return Code + '.SH' if Code[0] == '6' else Code + '.SZ'
		elif Type == 'FUT':
			return Code + '.CFE'
		elif Type == 'FUD':
			if Code[:2] == '16':
				return Code + '.OF'
			elif Code[0] == '5':
				return Code + '.SH'
			else:
				return Code + '.SZ'
		elif Type == 'BND':
			if Code[:2] == '12':
				return Code + '.SZ'
			return Code + '.SH'
		else:
			logging.warning('type %s has not been included before.'% Type)
			return Code + '.SH'

	def percent(self,Num):
		return format(Num,'.2%')

	def division(self,numerator,denominator):
		if denominator != 0:
			return numerator / denominator
		else:
			return 0

	def df_standard(self,df):
		if 'TradingDay' not in df.columns:
			df.insert(0,'TradingDay',pd.to_datetime(root_para.today_str))
		df.insert(len(df.columns),'CreateDate',root_para.now)
		return df

	def last_month_end(self):
		month_end_date = MonthEnd().rollback(root_para.today_str).strftime('%Y%m%d')
		return w.tdays('20170101',self.today_str,"Period=M").Data[0][-2].strftime('%Y%m%d')

	def dict_to_df(self,Dict,RenameCol):
		Rename = dict(list(zip(['index',0],RenameCol)))
		return DataFrame(Series(Dict)).reset_index().rename(columns = Rename)

	def value_dict_to_df(self,Dict,RenameCol = ['PortfolioID','NetValue']):
		df = self.dict_to_df(Dict,RenameCol)
		return self.df_standard(df)


# root_para = BasicParameter()	


class SecurityPrice():
	def __init__(self):
		self.yesterday_str,self.today_str = root_para.yesterday_str,root_para.today_str
		self.fut_code_type = root_para.fut_code_type
		self.str_date_H = 'tradeDate=%s' % self.yesterday_str
		self.str_date_T = 'tradeDate=%s' % self.today_str
		self.security_code()
		self.chiname()
		self.index_price()
		self.stock_fut_price()
		logging.warning("Necessary price have been prepared.")

	def security_code(self):
		stock_code = w.wset("sectorconstituent",self.str_date_T, "sectorid=a001010100000000;field=wind_code").Data[0]
		stock_code = list(map(str,stock_code))
		struct_code = w.wset("leveragedfundinfo",self.str_date_T, "field=wind_code,class_a_code,class_b_code").Data
		struct_code = [list(map(str,k)) for k in struct_code]
		self.struct_mum = struct_code[0]
		self.extra_code = ['511990.SH','113011.SH','150022.SZ','510050.SH','510300.SH','510900.SH','128032.SZ']
		self.total_code = list(set(stock_code) | set(self.extra_code) |set(struct_code[1]) | set(struct_code[2]))

	def chiname(self):
		temp = w.wss(root_para.fut_code, "trade_hiscode",self.str_date_T, 'priceAdj=F').Data[0]
		logging.debug(temp)
		all_code = list(set(self.struct_mum) | set(self.total_code) | set(map(str,temp)) | set(self.extra_code))
		m = w.wss(all_code,'sec_name')
		self.chi_name = twoList(list(map(str,m.Codes)),m.Data[0]).to_dict()
		logging.debug(self.chi_name[temp[0]])


	def index_price(self):
		index_price = list(zip(*[self.index(k) for k in self.fut_code_type]))
		self.index_price_0 = twoList(self.fut_code_type,index_price[0]).to_dict()
		self.index_price_1 = twoList(self.fut_code_type,index_price[1]).to_dict()
		self.index_pct = twoList(self.fut_code_type,np.array(index_price[1]) / np.array(index_price[0]) - 1).to_dict()
		logging.debug(self.index_price_1)
		logging.debug(self.index_pct)


	def stock_fut_price(self):
		self.close_price_0,self.close_price_1 = list(map(self.close,[self.str_date_H,self.str_date_T]))
		# logging.debug(self.close_price_0)
		# logging.debug('113011.SH' in list(self.close_price_0.keys()))
		# logging.debug(self.close_price_0['113011.SH'])
		self.settle_price_0 = self.fut_settle(self.str_date_H)
		self.settle_price_1 = self.fut_settle(self.str_date_T)
		print('----------------------')
		print(self.settle_price_0)
		print(self.settle_price_1)
		print('----------------------')
		self.nav_0,self.nav_1 = list(map(self.nav,[self.str_date_H,self.str_date_T]))
		
	def close(self,Date):
		m = w.wss(self.total_code,'close',Date,'priceAdj=F')
		temp_dict = twoList(list(map(str,m.Codes)),m.Data[0]).to_dict()
		temp_dict.update(self.close_other(Date))
		return temp_dict

	def close_other(self,Date):
		m = w.wss(self.extra_code,'close',Date)
		logging.debug(m)
		return twoList(list(map(str,m.Codes)),m.Data[0]).to_dict()

	def fut_settle(self,Date):
		m = w.wss(root_para.fut_code, "trade_hiscode,settle",Date, 'priceAdj=F').Data
		temp = twoList(list(map(str,m[0])),m[1]).to_dict()
		return temp

	def fut_close(self,Date):
		m = w.wss(root_para.fut_code, "trade_hiscode,close",self.str_date_T, 'priceAdj=F').Data
		temp = twoList(list(map(str,m[0])),m[1]).to_dict()
		return temp

	def nav(self,Date):
		m = w.wss(self.struct_mum, "nav", Date, 'priceAdj=F')
		temp = twoList(list(map(str,m.Codes)),m.Data[0]).to_dict()
		return temp

	def normal(self,Code,Date,Type='close'):
		logging.debug('code %s has not been taken into account.' %Code)
		return w.wsd(Code,Type,Date,Date).Data[0][0]

	def index(self,Index):
		return w.wsd(root_para.index_code[Index],'close',self.yesterday_str,self.today_str, '').Data[0]

	def get_price_0(self,Type,Code):
		if Type == 'CS':
			return self.close_price_0.get(Code,0)
		elif Type == 'FUT':
			return self.settle_price_0[Code]
		elif Type == 'FUD' and Code[-2:] == 'OF':
			return self.nav_0.get(Code,0)
		elif Type == 'FUD' and Code[-2:] != 'OF':
			return self.close_price_0.get(Code,self.normal(Code,self.yesterday_str))
		elif Type == 'BND':
			try:
				return self.close_price_0.get(Code,self.normal(Code,self.yesterday_str))
			except:
				return 100
		else:
			logging.info("code %s have not been included." %Code)
			return float(self.normal(Code,self.yesterday_str))

	def get_price_1(self,Type,Code):
		if Type == 'CS':
			return self.close_price_1.get(Code,0)
		elif Type == 'FUT':
			return self.settle_price_1[Code]
		elif Type == 'FUD' and Code[-2:] == 'OF':
			return self.nav_1.get(Code,0)
		elif Type == 'FUD' and Code[-2:] != 'OF':
			return self.close_price_1.get(Code,self.normal(Code,self.today_str))
		elif Type == 'BND':
			try:
				return self.close_price_1.get(Code,self.normal(Code,self.today_str))
			except:
				return 100
		else:
			logging.info("code %s have not been included." %Code)
			return float(self.normal(Code,self.today_str))


class DailyPositionTrading():
	def __init__(self,today_price):
		self.today_price = today_price
		self.root_path = 'D:/DailyReport/'
		self.yesterday_str,self.today_str = root_para.yesterday_str,root_para.today_str
		self.base_col = ['TradingDay','PortfolioID','Strategy','Code','Quantity','Type','Direction','ChiName']
		
		self.position_0 = self.get_position_0()

		self.position_1 = self.get_position_1()

		self.trading = self.get_trading()

		self.insert_holding_trading()

	def is_df_null(self,df,col=[]):
		if len(df) >= 1:
			return df
		return DataFrame(columns = col)

	def position_basic(self,path):
		df = pd.read_csv(path)
		if len(df) == 0:
			return DataFrame(columns = self.base_col)
		# df = self.is_df_null(df,self.base_col)
		df['Code'] = df.apply(lambda k:FormatStandard().code(k['Type'],k['Symbol']),axis = 1)
		df['DianShu'] = df['Code'].map(lambda k:root_para.fut_multiplier.get(k[:2],1))
		df['ChiName'] = df['Code'].map(lambda k:self.today_price.chi_name.get(k,'Unkown'))
		df['Direction'] = df['Side'].map(root_para.direction_dict)
		df['Price1'] = df.apply(lambda k:self.today_price.get_price_1(k['Type'],k['Code']),axis = 1)
		return df

	def insert_holding_trading(self):
		root_para.connAMS.delete_insert(self.position_0,'daily_holding_cross',['TradingDay'])
		root_para.connAMS.delete_insert(self.position_1,'daily_holding',['TradingDay'])
		# print(self.trading,len(self.trading))
		# print('------------------')
		root_para.connAMS.delete_insert(self.trading,'daily_trading',['TradingDay'])
		logging.warning("insertint daily trading & position in %s into db is ok." %self.today_str)


	def get_position_0(self):
		path = '%sHolding%s.csv' %(self.root_path,self.yesterday_str)
		df = self.position_basic(path)
		if len(df) == 0:
			return DataFrame(columns = self.base_col + ['Price0','Price1','Volume','Revenue','CreateDate'])
		df['TradingDay'] = pd.to_datetime(self.yesterday_str)
		df['Price0'] = df.apply(lambda k: self.today_price.get_price_0(k['Type'], k['Code']), axis=1).fillna(0.694 * df['Price1'])
		df['Revenue'] = (df['Price1'] - df['Price0']) * df['Quantity'] * df['Direction'] * df['DianShu']*(df['Price0'] != 0)
		df['Volume'] = df['Price0'] * df['Quantity'] * df['DianShu']
		df['CreateDate'] = root_para.now
		use_col = self.base_col + ['Price0','Price1','Volume','Revenue','CreateDate']
		return df[use_col].dropna()

	def get_position_1(self):
		path = '%sHolding%s.csv' %(self.root_path,self.today_str)
		df = self.position_basic(path)
		if len(df) == 0:
			return DataFrame(columns = self.base_col + ['Price1','Volume','CreateDate'])
		df['TradingDay'] = pd.to_datetime(self.today_str)
		df['Volume'] = df['Price1'] * df['Quantity'] * df['DianShu']
		df['CreateDate'] = root_para.now
		use_col = self.base_col + ['Price1','Volume','CreateDate']
		return df[use_col].dropna()

	def get_trading(self):
		path = '%sTrading%s.csv' %(self.root_path,self.today_str)
		df = self.position_basic(path)
		if len(df) == 0:
			return DataFrame(columns = self.base_col + ['FilledPrice','Price1','Revenue','CreateDate'])
		df['TradingDay'] = pd.to_datetime(self.today_str)
		df['Revenue'] = (df['Price1'] - df['FilledPrice']) * df['Quantity'] * df['Direction'] * df['DianShu']
		df['CreateDate'] = root_para.now
		use_col = self.base_col + ['FilledPrice','Price1','Revenue','CreateDate']
		return df[use_col].dropna()

# root_price = SecurityPrice()
# if __name__ == '__main__':
# 	DailyPositionTrading(root_price)
