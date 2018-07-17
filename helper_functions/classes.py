from .module import *
import time

class JsonIO():
	def __init__(self,path):
		self.path = path

	def write(self,data):
		with open(self.path, 'w') as f:
			json.dump(data, f)

	def read(self):
		with open(self.path, 'r') as f:
			data = json.load(f)
		return data


class FtpSendRecieve():
	def __init__(self,ip,user,psw,transport_path=''):
		self.ftp = FTP(ip)
		self.ftp.login(user=user, passwd=psw)
		self.ftp.cwd(transport_path)

	def get_file(self, cate=''):
		all_file = self.ftp.nlst()
		if cate == '':
			return all_file
		return [file for file in all_file if file.endswith(cate)]

	def mget(self,new_path_dir,path):
		new_path = os.path.join(new_path_dir,path)
		with open(new_path, 'wb') as get_new_file:
			try:
				self.ftp.retrbinary('RETR %s'%path, get_new_file.write, 1024)
			except:
				pass
		return

	def mput(self,old_path_dir,new_path_dir,path):
		old_path = os.path.join(old_path_dir,path)
		new_path = os.path.join(new_path_dir,path)
		with open(new_path, 'rb') as put_new_file:
			try:
				self.ftp.storbinary('STOR %s'%old_path,put_new_file,1024)
			except:
				pass
		return


class Timer:
	def __init__(self,func=time.clock):
		self.elapsed = 0.0
		self._func = func
		self._start = None

	def start(self):
		if self._start is not None:
			raise RuntimeError('Already started')
		self._start = self._func()

	def stop(self):
		if self._start is None:
			raise RuntimeError('Not Started')
		end = self._func()
		self.elapsed += end - self._start
		self._start = None

	def reset(self):
		self.elapsed = 0.0

	@property
	def running(self):
		return self._start is not None

	def __enter__(self):
		self.start()
		return self

	def __exit__(self,*args):
		self.stop()

	def trade_time_run(self,outside_func,*args):
		tick_time = datetime.now().strftime('%H%M%S')
		morning = (tick_time > '0913') & (tick_time < '1131')
		noon = (tick_time > '1129') & (tick_time < '1258')
		after = (tick_time > '1257') & (tick_time < '1502')
		#############################################
		outside_func(*args)
		logging.info('--%s--'%tick_time)
		sleep_time = 900 if noon else 120
		time.sleep(sleep_time)
		if not (morning or after or noon):
			raise SystemExit('---Close Trading---')
		return

	def try_except_sleep(self,func,*args):
		try:
			return func(*args)
		except:
			time.sleep(10)
			return self.try_except_sleep(self,func,*args)


class MyCode():
	__slots__ = ['code']

	def __init__(self,code):
		self.code = self.normal_code(code)
		
	def normal_code(self,code):
		code = str(code)
		return code if len(code) > 6 else code.rjust(6,'0')

	def secu_code(self):
		return self.code

	def wind_code(self):
		self.code = self.code[:6]
		if self.code[0] == '6':
			tmp = self.code + '.SH'
		elif self.code[:2] == '80':
			tmp = self.code + '.SI'
		else:
			tmp = self.code + '.SZ'
		return tmp

	def map_other_code(self,diction):
		return diction[self.code]


class TwoList(list):
	def __init__(self,list1,list2):
		self.list1 = list1
		self.list2 = list2

	def to_dict(self):
		assert len(self.list1) == len(self.list2), 'Two list should be some length.'
		return dict(list(zip(self.list1, self.list2)))

	def not_in_list2(self):
		return [k for k in self.list1 if k not in self.list2]

	def in_list2(self):
		return [k for k in self.list1 if k in self.list2]

	def list2_before_list1(self):
		tmp = [k for k in self.list2 if k in self.list1]
		return tmp + self.not_in_list2()

	def union(self):
		return list(set(self.list1) | set(self.list2))

	def intersection(self):
		return list(set(self.list1) & set(self.list2))


class TwoDataFrame():
	def __init__(self,df1,df2):
		self.df1 = df1
		self.df2 = df2

	def concat_by_index(self,idx):
		assert isinstance(idx,list), 'idx should be list, get %s.'%idx
		xx1 = self.df1.loc[~(self.df1.index.isin(idx))]
		xx2 = self.df2.loc[self.df2.index.isin(idx)]
		return pd.concat([xx1,xx2]).sort_index()

	def updata_df1(self):
		tmpdf = self.df1.copy()
		tmpdf.update(self.df2, overwrite=False)


class MyList(list):
	def __init__(self,list1):
		assert isinstance(list1,list),'Input should be list, get %s'%str(list1)
		self.list = list1

	def sort_list(self):
		self.list.sort()
		return self.list

	def to_str(self):
		return list(map(str, self.list))

	def try_remove(self,for_remove):
		if for_remove in self.list:
			self.list.remove(for_remove)
		return self.list

	def try_add(self,for_add):
		if for_add not in self.list:
			self.list.append(for_add)
		return self.list

	def get_comma(self):
		return ','.join(['%s']*len(self.list))

	def get_latest_index(self, element, cate='no_repeat_lag'):
		self.list = self.sort_list()
		tmp = bisect.bisect(self.list, element)
		if element in self.list and cate != 'no_repeat_lag':
			tmp -= 1
		return max(tmp-1, 0)
		
	def get_latest_element(self, element, cate='no_repeat_lag'):
		self.list = self.sort_list()
		idx = self.get_latest_index(element,cate)
		return self.list[idx]

	def shift(self, element, lag):
		idx = self.get_latest_index(element)
		return self.list[idx+lag]


class MyDir():
	def __init__(self,direc):
		assert isinstance(direc,str), 'direc should be string or unicode.'
		self.dir = direc
		self.is_file_exists = os.path.exists(self.dir)

	def mkdir(self):
		if not self.is_file_exists:
			os.mkdir(self.dir)

	def get_file(self,file_type):
		assert self.is_file_exists, 'dir %s does not exists.'% self.dir
		all_file_path = [file for file in os.listdir(self.dir) if file.endswith(file_type)]
		return MyList(all_file_path).sort_list()

	def whole_file_path(self,file_type):
		return [os.path.join(self.dir, file) for file in self.get_file(file_type)]

	def change_date(self,file_type):
		return [file.split('_')[2][:8] for file in self.get_file(file_type)]


class PathIO():
	def __init__(self,path):
		assert isinstance(path,str), 'filePath should be string,but get %s.'%path
		self.path = path
		self.file_type = os.path.splitext(path)[1]
		self.is_file_exists = os.path.exists(self.path)
		
	def get_path(self):
		return self.path

	def read_df(self):
		assert self.is_file_exists, '%s does not exits.'%self.path
		if self.file_type == '.pkl':
			return pd.read_pickle(self.path)
		elif self.file_type == '.csv':
			return pd.read_csv(self.path)
		elif self.file_type in ('.xlsx','.xls'):
			return pd.read_excel(self.path)
		elif self.file_type == '.h5':
			return pd.HDFStore(self.path)
		else:
			logging.error('cate of %s should have been added to Class pathIO' %self.file_type)

	def write_df(self,df):
		if self.file_type == '.pkl':
			df.to_pickle(self.path)
		elif self.file_type == '.csv':
			df.to_csv(self.path,index = None)
		elif self.file_type == '.xlsx':
			df.to_excel(self.path,index = None)
		else:
			logging.error('type of %s should have been added to Class pathIO' %self.file_type)


class MyDate():
	__slots__ = ['date']

	def __init__(self,date):
		self.date = pd.to_datetime(date)

	def get_time_stamp(self):
		return self.date

	def get_date(self):
		return self.date.date()

	def get_str_date(self):
		return self.date.strftime('%Y%m%d')

	def normalize_time(self):
		return pd.to_datetime(self.date.date())


class TimeNow():
	def __init__(self):
		self.date = datetime.today()

	def get_now(self):
		return self.date

	def get_str(self):
		return self.date.strftime('%Y%m%d')

	def get_str_time(self):
		return self.date.strftime('%Y%m%d-%H:%M')

	def get_tradingday_delta(self,lag):
		return w.tdaysoffset(lag,self.date).Data[0][0].date().strftime('%Y%m%d')


class MyWind():
	def __init__(self):
		pass

	def get_tradingday_str(self,start,end,cycle='D'):
		tmp = [k.date().strftime('%Y%m%d') for k in w.tdays(start, end, "Period=%s"%cycle).Data[0]]
		return tmp

	def get_tradingday_stamp(self,start,end,cycle='D'):
		tmp = [pd.to_datetime(k.date()) for k in w.tdays(start, end, "Period=%s" %cycle).Data[0]]
		return tmp

	def get_pct_change(self,start,end,idx):
		wind_data = w.wsd(idx, "pct_chg", start, end, "")
		dates = [pd.to_datetime(k.date()) for k in wind_data.Times]
		pcts = [k / 100 for k in wind_data.Data[0]]
		return dict(zip(dates, pcts))


class LazyProperty:
	def __init__(self,func):
		self.func = func

	def __get__(self,instance,cls):
		if instance is None:
			return self
		else:
			value = self.func(instance)
			setattr(instance, self.func.__name__, value)
			return value


class ReturnSeries():
	def __init__(self,df):
		assert isinstance(df,pd.core.frame.DataFrame), 'Input should be DataFrame'
		self.df = df.sort_index().dropna()
		self.column = self.df.columns[0]
		self.pct = self.df[self.column].values

	def get_daily_return(self):
		return self.df.reset_index().fillna(0)

	def get_month_return(self):
		df = self.df.resample('M', kind='period').sum().fillna(0)
		df.insert(0,'Month',['M'+str(k).rjust(2,'0') for k in df.index.month])
		df.insert(0,'Year',df.index.year)
		return self.merge_year_return(df,'Month')

	def get_quarter_return(self):
		df = self.df.resample('Q',kind='period').sum().fillna(0)
		df.insert(0,'Quarter',['Q'+str(k).rjust(2,'0') for k in df.index.quarter])
		df.insert(0,'Year',df.index.year)
		return self.merge_year_return(df,'Quarter')

	def merge_year_return(self,df,cate):
		xx = df.groupby('Year')[[self.column]].sum().reset_index()
		xx.insert(1,cate,'Sum')
		return pd.concat([df,xx],ignore_index=True)

	def tradingday_len(self):
		return len(self.df)

	def daily_victory_rate(self,rets=None):
		if rets is None:
			rets = self.pct
		tmp = rets[np.abs(rets) > 0.00002]
		return np.mean(np.where(tmp>0, 1, 0))

	def monthly_victory_rate(self):
		dff = self.df.resample('M',kind='period').sum().dropna()
		return self.daily_victory_rate(dff[self.column].values)

	def acc_yield(self):
		return self.pct.sum()

	def annual_yield(self):
		return 244*self.acc_yield()/self.tradingday_len()

	def annual_std(self):
		return np.sqrt(244)*self.pct.std()

	def information_ratio(self):
	    return self.annual_yield()/self.annual_std()

	def mdd(self):
		tmp = self.df.copy()
		tmp['cumsum'] = tmp[self.column].cumsum()
		tmp['cummax'] = np.maximum(0,tmp['cumsum'].cummax())
		return (tmp['cumsum'] - tmp['cummax']).min()

	def win_loss_statistic(self):
		tmp = self.pct[np.abs(self.pct) > 0.00002]
		positive_rets = tmp[tmp > 0]
		negative_rets = tmp[tmp < 0]
		############################
		tmp.sort()
		positive_rets.sort()
		negative_rets.sort()
		##############################
		return [tmp.max(), tmp.min(), positive_rets.mean(), negative_rets.mean(),
				tmp[int(len(tmp)*0.9):].mean(),
				tmp[: int(len(tmp)*0.1)].mean(),
				tmp[int(len(tmp)*0.1) : int(len(tmp)*0.9)].mean()]

	def rolling(self):
		rolling_func = lambda df: 244*df.sum() / len(df)
		rolling_annual = self.df.rolling(window=244, min_periods=244).apply(func=rolling_func).dropna().values
		if len(rolling_annual) <= 2:
			return [0,0]
		return [rolling_annual.mean(), rolling_annual.min()]

	def longest_dd(self, dfc, col):
		df = dfc.copy()
		map_index_int = {value:key for key,value in enumerate(df.index)}
		df.loc[df.query("cumsum == cummax").index, 'nearest_high'] = df.query("cumsum == cummax").index
		df.loc[df.index[0], 'nearest_high'] = df.index[0]
		df['nearest_high'] = df['nearest_high'].fillna(method='ffill')#.fillna(method='bfill')
		df['start_dd'] = df['nearest_high'].map(map_index_int)
		df['end_dd'] = df.index.map(lambda k:map_index_int[k])
		df['count_dd'] = df['end_dd'] - df['start_dd']
		tmp = df['count_dd'].idxmax()
		#############################################
		df['posi_or_neg'] = np.where((np.abs(df[col])>0.00002) & (df[col]<0), 1, 0)
		df['sig'] = df['posi_or_neg'].groupby((df['posi_or_neg'] != df['posi_or_neg'].shift()).cumsum()).transform(sum)
		out_1 = [df['sig'].max(), df['count_dd'].max()]
		out_2 = [df.loc[tmp,'nearest_high'].strftime('%Y-%m-%d'), tmp.strftime('%Y-%m-%d')]
		return out_1 + out_2

	def total_longest_dd(self):
		tmp = self.df.copy()
		tmp['cumsum'] = tmp[self.column].cumsum()
		tmp['cummax'] = np.maximum(0, tmp['cumsum'].cummax())
		return self.longest_dd(tmp,self.column)

	def year_statistic_detail(self,dfc):
		df = dfc.copy()
		df['cumsum'] = df[self.column].cumsum()
		df['cummax'] = np.maximum(0,df['cumsum'].cummax())
		df['dd'] = df['cumsum'] - df['cummax']
		#########################################
		result = dict()
		result['ret'] = df[self.column].sum()
		result['std'] = df[self.column].std() * np.sqrt(len(df))
		result['mdd'] = min(0,df['dd'].min())
		result['IR'] = result['ret'] / result['std']
		result['ret2mdd'] = 0 if result['mdd'] == 0 else -1*result['ret'] / result['mdd']
		#########################################
		date_str_type = '%Y-%m-%d'
		if result['mdd'] == 0:
			result['mdd_end'] = df.index[0].strftime(date_str_type)
			result['mdd_start'] = df.index[0].strftime(date_str_type)
		else:
			result['mdd_end'] = df['dd'].idxmin().strftime(date_str_type)
			result['mdd_start'] = df[:df['dd'].idxmin()]['cummax'].idxmax().strftime(date_str_type)
		#########################################
		[result['longest_neg_day_count'],
		result['longest_dd_day_count'],
		result['longest_dd_start'],
		result['longest_dd_end']] = self.longest_dd(df,self.column)
		return Series(result)

	def year_statistic(self):
		year_split = self.df.groupby(self.df.index.year).apply(self.year_statistic_detail)
		out_col = ['ret','std','mdd','IR','ret2mdd','mdd_start','mdd_end']
		out_col += ['longest_neg_day_count','longest_dd_day_count','longest_dd_start','longest_dd_end']
		year_split = year_split[out_col]
		return year_split.reset_index().dropna()

	def year_statistic_out(self):
		df = self.year_statistic()
		for col in ['ret','std','mdd']:
			df[col] = df[col].map(lambda k:format(k,'.2%'))
		for col in ['IR','ret2mdd']:
			df[col] = df[col].map(lambda k:round(k,2))
		return df

