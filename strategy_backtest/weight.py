from .h5 import *

class StrategyWeight():
	def __init__(self, strategy, file_type='.xlsx'):
		self.stra = strategy
		self.file_type = file_type
		self.dir = MyDir(StrategyWeightRootPath + self.stra)
		self.file_path = self.dir.whole_file_path(self.file_type)
		self.change_date = self.dir.change_date(self.file_type)
		self.is_idx_stra = strategy_index_dict[self.stra]

	def df_standard(self,df):
		df.insert(0,'Strategy',self.stra)
		df.insert(len(df.columns),'CreateDate',NowTick)
		return df

	def single_position_process(self,df):
		if len(df.columns) == 2:
			df.columns = ['Code','Weight']
			beta = 1
		elif len(df.columns) == 3:
			df.columns = ['Code','Weight','Beta']
			df = df.fillna({'Beta':1})
			beta = df.iloc[0,2]
		df = df.iloc[:,:2]
		mm = df['Code'].tolist()
		df['Code'] = df['Code'].replace({601313:601360}) ###江南嘉捷改360,代码变动。
		df['Weight'] /= 100
		return df,beta

	def single_position(self,path):
		df = PathIO(path).read_df()
		df,beta = self.single_position_process(df)
		use_date = os.path.basename(path).split('_')[2][:8]
		df['TradingDay'] = use_date
		return df, {use_date:beta}

	def all_position(self,path_list):
		assert isinstance(path_list,list),'multiple paths should be list.'
		tmp = [self.single_position(path) for path in path_list]
		TotalHolding,TotalBeta = map(list,zip(*tmp))
		TotalBeta = self.beta_standard(TotalBeta)
		TotalHolding = self.holding_standard(TotalHolding)
		sh_sz_weight = self.sh_sz_standard(TotalHolding[['TradingDay','Code','InnerCode','Weight','Type']])#.query("Type == 1"))
		return TotalHolding,TotalBeta,sh_sz_weight

	def beta_standard(self,total_beta):
		df = dict(reduce(lambda x,y:x + y,[list(k.items()) for k in total_beta]))
		df = DataFrame(df,index = ['Beta']).T.reset_index().rename(columns={'index':'TradingDay'})
		df['TradingDay'] = df['TradingDay'].map(pd.to_datetime)
		return self.df_standard(df)

	def holding_standard(self,df):
		df = pd.concat(df, ignore_index=True)
		df['Code'] = df['Code'].map(lambda k:MyCode(k).secu_code())
		#############################
		df = self.get_innerCode(df)
		df['TradingDay'] = df['TradingDay'].map(pd.to_datetime)
		df['ChiName'] = df['InnerCode'].map(lambda k:mapChiName.get(k,'Unkown'))
		df['Type'] = df['InnerCode'].map(lambda k:mapSecuType.get(k,1))
		df = self.df_standard(df).fillna(method='ffill')
		_ = df.sort_values(by='TradingDay', inplace=True)
		return df[['Strategy','TradingDay','InnerCode','Weight','Code','Type','ChiName','CreateDate']]

	def get_innerCode(self,df):
		if self.is_idx_stra == 0:
			df['InnerCode'] = df['Code'].map(lambda k:k[:6]).map(mapInnerCode)
			return df
		######################
		df['code_len'] = df['Code'].map(len)
		df1 = df[df['code_len'] == 6]
		df1['InnerCode'] = df1['Code'].map(mapInnerCode)
		df2 = df[df['code_len'] > 6]
		if len(df2) == 0:
			return df1
		#################################
		df2['InnerCode'] = df2['Code'].map(lambda k:k[:6]).map(mapIndexInnerCode)
		return pd.concat([df1,df2], ignore_index=True)

	def sh_sz_standard(self,df):
		df['Weight'] = df['Weight'] * (df['Type'] == 1)
		df['Market'] = df['Code'].map(lambda k:'SH' if k[0] == '6' else 'SZ')
		total_weight = df.groupby(['TradingDay'])[['Weight']].sum().reset_index()
		total_weight.insert(1,'Market','TotalWeight')
		#################################
		sh_sz_weight = df.groupby(['TradingDay','Market']).sum()[['Weight']].reset_index()
		index_weight = df.groupby(['TradingDay']).apply(self.get_weight).reset_index().set_index('TradingDay')
		for i,j in enumerate(['Weight50','Weight300','Weight500']):
			index_weight[j] = index_weight[0].map(lambda k:k[i])
		del index_weight[0]
		#####################
		index_weight = index_weight.stack().reset_index()
		index_weight.columns = ['TradingDay','Market','Weight']
		return self.df_standard(pd.concat([total_weight,sh_sz_weight,index_weight],ignore_index = True))

	def get_weight(self,df):
		use_date = list(df['TradingDay'])[0]
		tmp_dict = get_index_constitution(use_date)
		return [df[df['InnerCode'].isin(tmp_dict[idx])]['Weight'].sum() for idx in ALL_INDEX]

	def insert_to_db(self,path_list,del_col):
		TotalHolding,TotalBeta,sh_sz_weight = self.all_position(path_list)
		connBackTest.delete_insert(TotalHolding,'alpha_strategy_daily_position',del_col)
		connBackTest.delete_insert(TotalBeta,'alpha_strategy_daily_beta',del_col)
		connBackTest.delete_insert(sh_sz_weight,'alpha_strategy_sh_sz',del_col)
		logging.info('Inserting %s Holding & Beta & sh_sz ratio into DataBase is ok.' %self.stra)
		