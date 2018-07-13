from .classes import *
fillnaConstant = get_config_para('BasicPara','fill_cnst')
#####################################
class SqlSelect():
	def __init__(self,table):
		self.table = table

	def entire_select(self,col):
		return "select %s from %s" %(col,self.table)

	def condition_select(self,col,condition):
		assert isinstance(condition,list), 'condition should be list, not %s'%condition
		select_all = self.entire_select(col)
		if condition == []:
			return select_all
		return  "%s where %s" %(select_all, " and ".join(condition))


class SqlCreate():
	def __init__(self):
		pass

	def pk_sentence(self,pk):
		if isinstance(pk,str):
			return "PRIMARY KEY (%s)" %pk
		elif isinstance(pk,list):
			return "PRIMARY KEY (%s)" %','.join(pk)

	def simple_index(self,idx):
		if idx == '':
			return ''
		elif isinstance(idx,str):
			return "INDEX %s (%s ASC)" %('idx_%s'%idx,idx)
		elif isinstance(idx,list):
			index_name = 'idx_%s' %idx[0]
			all_index = ",".join(["%s ASC" % k for k in idx])
			return "INDEX %s (%s)" %(index_name, all_index)

	def index_sentence(self,idx,cate='Single'):
		if isinstance(idx,str):
			return self.idx(idx)
		elif isinstance(idx,list) and cate == 'Single':
			return ",".join([self.simple_index(k) for k in idx])
		elif isinstance(idx,list) and cate == 'Multiple':
			return self.simple_index(idx)

	def col_describe(self,zipcol):
		if zipcol[1][:7] == 'varchar':
			default_value = " DEFAULT 'unknown'"
		elif zipcol[1] == 'double':
			default_value = 'DEFAULT %s' %str(fillnaConstant)
		return "%s %s NOT NULL %s" %(zipcol[0],zipcol[1],default_value)

	def col_sentence(self,table_col,pk):
		write_col = ','.join([self.col_describe(k) for k in table_col])
		write_col += ",UpdateTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP"
		write_col += ",CreateTime datetime NOT NULL DEFAULT CURRENT_TIMESTAMP"
		if 'ID' in pk:
			write_col = "ID INT NOT NULL AUTO_INCREMENT," + write_col
		return write_col


class  SqlDelete():
	def by_condition(self,**kw):
		if kw == {}:
			return ''
		else:
			condition = ["%s = %r" %(k[0],k[1]) for k in list(kw.items())]
			return " and ".join(condition)


class DBConnect():
	def __init__(self,IP,user,pwd,Port,DB):
		self.IP = IP
		self.user = user
		self.pw = pwd
		self.Port = Port
		self.db = DB

	def connect_mysql(self):
		conn = MySQLdb.connect(host=self.IP,user=self.user,passwd=self.pw,port=self.Port,db=self.db,charset='utf8')
		return conn

	def connect_jy(self):
		conn = pymssql.connect(host=self.IP,user=self.user,password=self.pw,port=self.Port,database=self.db,charset='GBK')
		return conn

	def connectMySQL(self):
		return DataBaseOperate(self.connect_mysql())

	def connectJY(self):
		return DataBaseOperate(self.connect_jy())
	

class DataBaseOperate():
	def __init__(self,data_base):
		self.db = data_base
		self.cur = self.db.cursor()

	def read_by_sql(self,sql,chunk=20000):
		try:
			dfs = pd.read_sql(sql,con=self.db,chunksize=chunk)
			chunks = []
			for df in dfs:
				chunks.append(df)
			return pd.concat(chunks,ignore_index=True)
		except ValueError:
			return pd.read_sql(sql,con=self.db)

	def read(self,columns,table,condition='',chunk=20000):
		condition = '' if condition == '' else ' where ' + condition
		sql = "select %s from %s%s" %(columns,table,condition)
		return self.read_by_sql(sql,chunk=chunk)

	def get_db_cols_struct(self,table):
		sql = "show columns from %s" %table
		df = pd.read_sql(sql,con=self.db)
		return df

	def get_db_cols(self,table,cate='All'):
		df = self.get_db_cols_struct(table)
		if cate == 'Raw':
			return df
		if cate == 'PK':
			return df.query("Key == 'PRI'")['Field'].tolist()
		elif cate == 'notPK':
			return df.query("Key != 'PRI'")['Field'].tolist()
		else:
			col = MyList(df['Field'].tolist()).try_remove('ID')
			return col

	def delete_table(self,table):
		try:
			self.cur.execute("drop table %s" %table)
			self.db.commit()
		except:
			logging.info('table %s has not been created or has been deleted before' %table)

	def create_table(self,table,col,PK,idx,is_delete_old=0):
		if is_delete_old == 1:
			self.delete_table(table)
		#############################################
		pk_sentence = SqlCreate().pk_sentence(PK)
		idx_sentence = SqlCreate().index_sentence(idx)
		Sql = "create table if not exists %s(%s,%s,%s) ENGINE = InnoDB DEFAULT CHARSET = utf8" %(table,col,pk_sentence,idx_sentence)
		self.cur.execute(Sql)
		self.db.commit()
		
	def columns_sqlServer(self,table):
		sql = "sp_columns %s" %table
		return pd.read_sql(sql,con=self.db)

	def db_cols(self,table):
		sql = "show columns from %s" %table
		df = pd.read_sql(sql,con=self.db)
		total_col = MyList(df['Field'].tolist()).try_remove('ID')
		return total_col

	def db_cols_and_pk(self,table):
		sql = "show columns from %s" %table
		df = pd.read_sql(sql,con=self.db)
		total_col = list(map(str, df['Field'].tolist()))
		cols_without_pk = list(map(str,df[df['Key'] != 'PRI']['Field'].tolist()))
		return total_col, cols_without_pk

	def delete_data(self,table,**kw):
		delete_sql = "DELETE FROM %s" %table
		delete_condition_sql = SqlDelete().by_condition(**kw)
		if delete_condition_sql != '':
			delete_sql = "%s where %s" %(delete_sql,delete_condition_sql)
		self.cur.execute(delete_sql)
		self.db.commit()

	def batch_insert_data(self,sql,data):
		try:
			self.cur.execute(sql,data)
		except:
			simple_insert = 10000
			for i in range(1+len(data) // simple_insert):
				self.cur.executemany(sql, data[i*simple_insert:(i+1)*simple_insert])
		self.db.commit()

	def insert_df(self,insert_data,table,insert_col):
		if len(insert_data) == 0:
			return
		if isinstance(insert_data,list):
			comma = MyList(insert_data).get_comma()
			df_values = insert_data
		else:
			df_values = list(map(list, insert_data.values))
			comma = MyList(df_values[0]).get_comma()
		insert_sql = "INSERT INTO %s(%s) VALUES (%s)" %(table,','.join(insert_col),comma)
		self.batch_insert_data(insert_sql,df_values)

	def delete_insert(self,insert_data,table,delete_col=[],insert_col=[]):
		if len(insert_data) == 0:
			return
		##########################
		if not isinstance(delete_col,list):
			logging.error('delete_col should be list,get %s'%delete_col)
			return
		########################
		if len(delete_col) == 0:
			kw = {}
		else:
			if isinstance(insert_data,list):
				kw = {delete_col[0]:insert_data[0]}
			else:
				kw = dict(list(zip(delete_col, [list(insert_data[k])[0] for k in delete_col])))
		self.delete_data(table, **kw)
		################################
		if insert_col == []:
			insert_col = self.db_cols(table)
		self.insert_df(insert_data, table, insert_col)

	def update(self,df,table,usecol):
		if len(df) == 0:
			return
		###########
		df_values = list(map(list, df.values)) 
		comma = MyList(df_values[0]).get_comma()
		pk_col = self.get_db_cols(table,'PK')
		#####################
		update_col = [k for k in usecol if k not in pk_col]
		update_col = ', '.join(['%s = VALUES(%s)'%(k,k) for k in update_col])
		update_sql = "INSERT INTO %s(%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s" %(table, ','.join(usecol), comma, update_col)
		self.batch_insert_data(update_sql,df_values)

	def close_db(self):
		self.db.close()


class StrategyProperty():
	def __init__(self,db,today_str):
		self.today_str = today_str
		self.all = db.read('*','strategy',"Deleted = 0").sort_values('Strategy')
		self.all['Strategy'] = self.all['Strategy'].map(str)

	def all_strategy(self):
		return self.all[self.all['IsOnlyReturn'] == 0]['Strategy'].tolist()

	def full_strategy(self):
		return self.all['Strategy'].tolist()

	def strategy_status(self):
		return dict(list(zip(self.all['Strategy'],self.all['StraStatus'])))

	def in_strategy(self):
		return self.all.query("StraStatus == 'In'")['Strategy'].tolist()

	def pre_strategy(self):
		return self.all.query("StraStatus == 'Pre'")['Strategy'].tolist()

	def only_return_strategy(self):
		return self.all[self.all['IsOnlyReturn'] == 1]['Strategy'].tolist()

	def new_strategy(self):
		return self.all[self.all['CreateDate'] >= self.today_str]['Strategy'].tolist()

	def strategy_attri(self,col):
		assert col in self.all.columns, '%s is not in Strategy attributions.' %col
		return dict(zip(self.all['Strategy'],self.all[col]))

