from ..base.cnst import *

class WindData():
	def __init__(self):
		self.db = connWind
		self.stock_list_day = self.stock_list_day()

	def get_tradingday(self,start_date = '20051001'):
		table,typee = 'AShareCalendar','SSE'
		df = self.db.read("trade_days", table, "S_INFO_EXCHMARKET=%r" %typee).sort_values('trade_days')
		df = df.query("%r < trade_days <= %r" %(start_date,YesterdayStr))
		return df

	def index_component(self,index_code,day):
		condi = "S_INFO_WINDCODE = %r and S_CON_INDATE <= %r and S_CON_OUTDATE > %r order by S_CON_INDATE" %(index_code,day,day)
		df = self.db.read("S_CON_WINDCODE","AIndexMembers",condi)
		return df.drop_duplicates('S_CON_WINDCODE')['S_CON_WINDCODE'].tolist()

	def yearly_start_end(self, exchge_market='A'):
		trade_dates = self.get_tradingday()['trade_days'].tolist()
		self.all_year = sorted(list(set([date[:4] for date in trade_dates])))
		self.year_start_end = defaultdict(list)
		for date in trade_dates:
			self.year_start_end[date[:4]].append(date)
		for year in self.all_year:
			self.year_start_end[year] = (self.year_start_end[year][0],self.year_start_end[year][-1])
		self.year_start_end = dict(self.year_start_end)

	def next_n_days(self,day):
		xx = all_jy_tradingday[:]
		bisect.insort(xx,day)
		return xx[xx.index(day)+120]
		
	def del_no_list_stock(self,df):
		out = DataFrame(np.nan,index = df.index,columns = self.stock_list_day['S_INFO_WINDCODE'].tolist())
		for day in out.index[:]:
			day_str = day.strftime('%Y%m%d')
			stock = self.list_stock(day_str)
			out.loc[day,stock] = df.loc[day,stock]
		return out

	def stock_list_day(self):
		df = self.db.read('S_INFO_WINDCODE,S_INFO_LISTDATE,S_INFO_DELISTDATE','AShareDescription')
		df = df.fillna({'S_INFO_DELISTDATE':'20301111'}).dropna()
		df['S_INFO_LISTDATE_120'] = df['S_INFO_LISTDATE'].map(lambda day:self.next_n_days(day))
		return df

	def list_stock(self,day):
		df = self.stock_list_day.query("(S_INFO_LISTDATE_120 < %r) & (S_INFO_DELISTDATE >%r)" %(day,day))
		return df['S_INFO_WINDCODE'].tolist()

	def trade_date_func(self,trade_date):
		if len(trade_date) == 1:
			condi = "TRADE_DT = %r" %trade_date[0]
		elif len(trade_date) == 2:
			condi = "TRADE_DT >= %r and TRADE_DT <= %r" %(trade_date[0],trade_date[1])
		return condi

	def get_dailyquote(self,trade_date):
		col = "TRADE_DT,S_INFO_WINDCODE,S_DQ_ADJCLOSE,S_DQ_ADJFACTOR,S_DQ_AVGPRICE"
		table = 'AShareEODPrices'
		condi = self.trade_date_func(trade_date)
		condi += " and S_DQ_AMOUNT > 0"
		df = self.db.read(col,table,condi)
		return df

	def get_change_rate(self,trade_date):
		col = "TRADE_DT,S_INFO_WINDCODE,S_DQ_FREETURNOVER"
		table = "AShareEODDerivativeIndicator"
		condi = self.trade_date_func(trade_date)
		df = self.db.read(col,table,condi)
		return df

	def pct_data_save(self):
		self.yearly_start_end()
		for year in self.all_year[-1:]:
			trade_date = self.year_start_end[year]
			pct_data =  self.get_dailyquote(trade_date)
			change_rate_data = self.get_change_rate(trade_date)
			cgo_data = pd.merge(pct_data,change_rate_data,on=['TRADE_DT','S_INFO_WINDCODE'],how='left')
			cgo_data.to_pickle('lht/cgo/data/cgo_%s.pkl' %year)
			print(year)

	def pct_concat(self):
		self.yearly_start_end()
		a_pct = []
		for year in self.all_year[:-1]:
			a_pct_year = pd.read_pickle('lht/cgo/data/cgo_%s.pkl' %year)
			a_pct.append(a_pct_year)
		a_pct = pd.concat(a_pct,ignore_index=True)
		a_pct['VWAP'] = a_pct['S_DQ_ADJFACTOR'] * a_pct['S_DQ_AVGPRICE']
		a_pct['S_DQ_FREETURNOVER'] /= 100
		a_pct = a_pct.pivot('TRADE_DT','S_INFO_WINDCODE')
		a_pct.index = a_pct.index.map(lambda k:pd.to_datetime(k))
		###########################
		a_pct['S_DQ_ADJCLOSE'].fillna(method='ffill').fillna(method='bfill').to_pickle('lht/cgo/data/cgo_close.pkl')
		a_pct['VWAP'].fillna(method='ffill').fillna(method='bfill').to_pickle('lht/cgo/data/cgo_vwap.pkl')
		a_pct['S_DQ_FREETURNOVER'].fillna(0.00001).to_pickle('lht/cgo/data/cgo_turn_rate.pkl')
		

class CGO(WindData):
	def __init__(self):
		super().__init__()

	def cal_cgo(self,window = 100):
		close = pd.read_pickle('lht/cgo/data/cgo_close.pkl')
		vwap  = pd.read_pickle('lht/cgo/data/cgo_vwap.pkl')
		cr    = pd.read_pickle('lht/cgo/data/cgo_turn_rate.pkl')
		reference_price = DataFrame(0,columns=vwap.columns,index=vwap.index)
		cr_minus = 1 - cr
		for index in vwap.index[window-1:]:
			r_p = cr_minus[:index][-window:][::-1].shift(1).fillna(1).cumprod() * cr[:index][-window:]
			reference_price.loc[index,:] = np.average(vwap[:index][-window:],axis=0,weights=r_p)
		##################
		reference_price.to_pickle('lht/cgo/data/cgo_rp.pkl')
		cgo = (close / reference_price) - 1
		cgo.to_pickle('lht/cgo/data/cgo.pkl')
		
	def df_check(self,path):
		df = pd.read_pickle(path)
		return df

	def rank_ic_describe(self,data):
		xx = data.values
		xx = np.where(xx>0,0,1)
		return

	def only_get_tradingday(self,df):
		xx = DataFrame(df.index)
		xx['week'] = xx['TRADE_DT'].map(lambda k:k.week)
		xx['is_last'] = xx['week'] < xx['week'].shift(-1)
		xx = xx[xx['is_last'] == True]['TRADE_DT'].tolist()
		return df.loc[xx,:]

	def choice_300_by_cgo(self):
		cgo = self.df_check('lht/cgo/data/cgo.pkl')#.resample('W').last().fillna(method='ffill')
		cgo = self.only_get_tradingday(cgo)
		cgo = self.del_no_list_stock(cgo)['20061231':]
		################
		is_up_240_mean = self.up_240_mean()
		cgo,is_up_240_mean = cgo.align(is_up_240_mean,join='inner')
		cgo[is_up_240_mean == False] = 1
		###################
		for day in cgo.index[:]:
			day_str = day.strftime('%Y%m%d')
			stock = self.index_component('000300.SH',day_str)
			NN = 50
			xx = cgo.loc[day,stock].dropna().sort_values()
			######################
			xx = DataFrame(xx).reset_index()[:].rename(columns={'index':'Code',day:'Weight'})[:NN]
			xx['Code'] = xx['Code'].map(lambda k:k[:6])
			xx['Weight'] = 100.0 / NN
			xx.to_excel("lht/cgo/S5003L/W_S5003L_%s.xlsx"%day_str,index=None)
		return

	def up_240_mean(self):
		close = self.df_check('lht/cgo/data/cgo_close.pkl')
		close_mean = close.rolling(window=240, min_periods=40).mean()
		is_up_240_mean = (close > close_mean).dropna(how='all')
		return is_up_240_mean

	def corr_cal(self,i = 5):
		df1 = self.df_check('lht/cgo/data/cgo_close.pkl').pct_change(i).shift(-i)
		df1 = df1.resample('M').last().fillna(method='ffill')
		df2 = self.df_check('lht/cgo/data/cgo.pkl')
		df2 = df2.resample('M').last().fillna(method='ffill')
		df1 = self.del_no_list_stock(df1).rank(axis=1)
		df2 = self.del_no_list_stock(df2).rank(axis=1)
		rank_corr = df1.corrwith(df2,axis=1).dropna()['2007':]
		return rank_corr

