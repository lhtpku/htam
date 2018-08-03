'use strict';
var fs = require('fs');
var xlsx = require('node-xlsx');
var GET_BT_DATA = require('./sql_test').backtest;
var GET_AMS_DATA = require('./sql_test').ams;
var code_exec = require('child_process').exec;


var RESPONSE = {}
// var xx = getIP(request)['clientIp']


RESPONSE = {
	'': function (res,frontDataStrtgy) {
		res.writeHead(200,{'Content-Type':'text/html;charset = utf-8'});
		var streamfr = fs.createReadStream('account_analysis.html');
		streamfr.on('error',function(err){
			res.end("<h1> 404 error</h1>>");
			console.log(err);
		});
		streamfr.pipe(res);
	},

	'*': function (res,file_path) {
		if (file_path.endsWith('.html')){
			res.writeHead(200,{'Content-Type':'text/html;charset = utf-8'});
		} else if (file_path.endsWith('.js')) {
			res.writeHead(200,{'Content-Type':'text/javascript;charset = utf-8'});
		}
		file_path = __dirname + '/' + file_path;
		var streamfr = fs.createReadStream(file_path);
		streamfr.on('error',function(err){
			res.end("<h1> 404 error</h1>>");
			console.log(err);
		});
		// console.log('run response *     ' + file_path)
		streamfr.pipe(res);
	},

	restrict_strategy: function() {
		return "('S1501C','S1601A','S0300','S1104C')";
	},

	get_ip: function(res,ipInfo) {
		res.end(JSON.stringify(ipInfo))
	},

	bt_sql: function(res,table,strategy='',condition='',order='') {
		var sql = `SELECT * from ${table}`;
		var temp = '';
		if (strategy !== '') {
			temp = ` where Strategy = '${strategy}'`;
		} //else { //  else 不需要即可限定策略
		// 	temp = ` where Strategy in ${this.restrict_strategy()}`;
		// }
		var is_temp = (temp === '');
		var is_condition = (condition === '');
		if (!is_temp & !is_condition) {
			sql += temp;
			sql += ` and ${condition}`;
		} else if (is_temp & !is_condition) {
			sql += ` where ${condition}`;
		} else if (!is_temp & is_condition) {
			sql +=temp;
		}

		if (order !== '') {
			sql += ` order by ${order}`;
		}
		return GET_BT_DATA(res,sql);
	},

	load_strategy: function (res,Status) {
		if (Status === '') {
			var condi = 'Deleted = 0'
		} else {
			var condi = `Deleted = 0 and StraStatus = '${Status}'`
		}
		var sql = this.bt_sql(res,'strategy','',condi,'Strategy');
	},

	strategy_description: function (res,Strategy) {
		var sql = this.bt_sql(res,'strategy',Strategy)
	},

	general_result: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_summary',Strategy);
	},

	yearly_statistic: function (res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_annulized_return',Strategy);
	},

	tick_pct: function(res,Strategy) {
		var sql = this.bt_sql(res,'strategy_tick_pct','');
	},

	single_tick_pct: function(res,Strategy) {
		var sql = this.bt_sql(res,'single_strategy_tick_pct',Strategy,'','Weight desc')
	},

	month_return: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_monthly_return',Strategy);
	},

	quarter_return: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_quarterly_return',Strategy);
	},

	latest_20_days: function(res,Strategy) {
		var sql = this.bt_sql(res,'strategy_daily_return',Strategy,'','TradingDay desc limit 20');
	},

	two_stra_corr: function(res,two_stra) {
		two_stra = JSON.parse(two_stra)
		var condi = `Strategy = '${two_stra.stra1}' and sub_Strategy = '${two_stra.stra2}'`;
		var sql = this.bt_sql(res,'alpha_strategy_corr','',condi)
	},

	industry_risk: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_annulized_industry_detail',Strategy);
	},

	pe_risk: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_annulized_pe_detail',Strategy);
	},

	pb_risk: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_annulized_pb_detail',Strategy);
	},

	mv_risk: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_annulized_grade_detail',Strategy);
	},

	turnrate_risk: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_annulized_turnrate_detail',Strategy);
	},

	latest_position: function(res,Strategy) {
		var sql_max_day = `select max(TradingDay) from alpha_strategy_daily_position where Strategy = '${Strategy}'`;
		var condition = `TradingDay = (${sql_max_day})`
		var sql = this.bt_sql(res,'alpha_strategy_daily_position',Strategy,condition,'Weight desc');
	},

	position_describe: function(res,Strategy) {
		var sql_max_day = `select max(TradingDay) from alpha_strategy_daily_position where Strategy = '${Strategy}'`;
		var condition = `TradingDay = (${sql_max_day})`;
		var sql = this.bt_sql(res,'alpha_strategy_sh_sz',Strategy,condition);
	},

	history_position_stat: function(res,Strategy) {
		var sql = this.bt_sql(res,'strategy_weight_stat',Strategy);
	},

	risk_general: function(res,Strategy) {
		var sql = this.bt_sql(res,'factor_risk_all',Strategy)
	},

	industry_exposure: function(res,Strategy) {
		var sql = this.bt_sql(res,'factor_risk',Strategy,"Factor = 'Industry'",'WeightDelta')
	},

	mv_exposure: function(res,Strategy) {
		var sql = this.bt_sql(res,'factor_risk',Strategy,"Factor = 'S_DQ_MV'",'Grade')
	},

	float_mv_exposure: function(res,Strategy) {
		var sql = this.bt_sql(res,'factor_risk',Strategy,"Factor = 'S_VAL_MV'",'Grade')
	},

	pe_exposure: function(res,Strategy) {
		var sql = this.bt_sql(res,'factor_risk',Strategy,"Factor = 'S_VAL_PE_TTM'",'Grade')
	},

	pb_exposure: function(res,Strategy) {
		var sql = this.bt_sql(res,'factor_risk',Strategy,"Factor = 'S_VAL_PB_NEW'",'Grade')
	},

	roe_exposure: function(res,Strategy) {
		var sql = this.bt_sql(res,'factor_risk',Strategy,"Factor = 'S_QFA_ROE'",'Grade')
	},

	alpha_pool: function(res,Strategy) {
		var sql = this.bt_sql(res,'latest_performance','',"Type = 'Alpha'",'Strategy');
	},

	long_pool: function(res,Strategy) {
		var sql = this.bt_sql(res,'latest_performance','',"Type = 'Long'",'Strategy');
	},

	in_week_report: function(res,Strategy) {
		var sql = this.bt_sql(res,'week_report','',"Type = 'In'",'Strategy');
	},

	pre_week_report: function(res,Strategy) {
		var sql = this.bt_sql(res,'week_report','',"Type = 'Pre'",'Strategy');
	},

	strategy_corr: function(res,Strategy) {
		var sql = this.bt_sql(res,'alpha_strategy_corr',Strategy,'Value');
	},

	long_yearly_statistic: function(res,Strategy) {
		var sql = this.bt_sql(res,'long_position_yearly_return',Strategy);
	},

	history_mdd: function(res,Strategy) {
		var sql = this.bt_sql(res,'strategy_return_dd',Strategy,'','Attri');
	},

	multi_basic_attri: function(res,Strategy) {
		var sql = this.bt_sql(res,'multi_simple',Strategy)
	},

	python_calcu: function(res,use_data) {
		this.save_table_to_excel(res,use_data,this.run_python);
	},

	save_table_to_excel: function (res,use_data,funCallBack){
		var data_array = JSON.parse(use_data).array;
		var buff = xlsx.build([{
			name:'sheet1',
			data:data_array
		}]);
		fs.writeFile('./python/multiStrategy.xlsx',buff,{'flag':'w'},function(){
			funCallBack(res);
		});
	},


	run_python: function(res) {
		code_exec(__dirname + '/python/runme.py',function(error,stdout,stderr){
			if (error) {
				console.log('exec error: ' + error);
				return;
			}
			var str_json = JSON.stringify({message:'comutation completed'});
			res.end(str_json);
		})
	},

	restrict_portfolio: function(){
		return '(70,71)';
	},

	ams_sql: function(table,condition = '',order = '') {
		if (table.indexOf('futures') !== -1) {
			var sql = `SELECT a.*,b.ChiName AccountName FROM ${table} a inner join portfolio b on a.PortfolioID = b.PortfolioID`;
		} else {
			var sql = `SELECT a.*,b.ChiName AccountName FROM ${table} a inner join portfolio b on a.PortfolioID = b.PortfolioID`;
			sql += ' and b.Deleted = 0';	
		}
		// sql += ` and b.PortfolioID in ${this.restrict_portfolio()}`;
		if (condition !== '') {
			sql = sql + ' and ' + condition;
		}
		if (order === '') {
			order = 'a.PortfolioID'
		}
		sql = sql + ` order by ${order}`;
		return sql;
	},

	load_account: function(res,Account){
		var sql = `select * from portfolio where Deleted = 0 and PortfolioID in ${this.restrict_portfolio()} order by PortfolioID`;
		var sql = "select * from portfolio where Deleted = 0 order by PortfolioID";
		GET_AMS_DATA(res, sql);
	},

	portfolio_type: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var sql = `select PortfolioType from portfolio where ChiName='${data_ob.account}'`;
		// console.log(GET_AMS_DATA(res, sql))
		GET_AMS_DATA(res, sql);
	},

	strategy_alpha: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}' and a.Weight > 0.015`
		var sql = this.ams_sql('daily_strategy_performance',condition,'b.PortfolioID,a.Strategy')
		GET_AMS_DATA(res,sql)
	},

	strategy_long: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}' and a.Weight > 0.005`
		var sql = this.ams_sql('daily_speculation_performance',condition,'b.PortfolioID,a.Strategy')
		GET_AMS_DATA(res,sql)
	},

	risk_exposure: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}'`
		var sql = this.ams_sql('stock_exposure',condition,'b.PortfolioID')
		GET_AMS_DATA(res,sql)
	},

	risk_match: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}'`
		var sql = this.ams_sql('stock_fut_match',condition,'b.PortfolioID')
		GET_AMS_DATA(res,sql)
	},

	account_general: function(res,data_ob) {
		var sql = this.ams_sql('account_general');
		GET_AMS_DATA(res,sql);
	},

	holding: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}' and b.ChiName='${data_ob.account}' and a.Strategy='${data_ob.strategy}'`
		var sql = this.ams_sql('daily_holding',condition,'a.Code')
		GET_AMS_DATA(res,sql)
	},

	trading: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}' and b.ChiName='${data_ob.account}' and a.Strategy='${data_ob.strategy}'`
		var sql = this.ams_sql('daily_trading',condition,'a.Code')
		GET_AMS_DATA(res,sql)
	},

	new_stock_date: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}'`
		var sql = this.ams_sql('sh_sz_20',condition);
		GET_AMS_DATA(res,sql)
	},

	new_stock_account: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `b.ChiName='${data_ob.account}'`
		var sql = this.ams_sql('sh_sz_20',condition,'a.TradingDay desc limit 20');
		GET_AMS_DATA(res,sql)
	},

	new_stock_revenue: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `b.ChiName='${data_ob.account}'`
		var sql = this.ams_sql('new_stock_revenue_monthly',condition,'a.TradingDay desc limit 12');
		GET_AMS_DATA(res,sql)
	},

	futures_holding: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}'`
		var sql = this.ams_sql('daily_futures_position',condition,'b.PortfolioID');
		GET_AMS_DATA(res,sql)
	},

	futures_uplimit: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}'`
		var sql = this.ams_sql('daily_futures_max',condition,'b.PortfolioID');
		GET_AMS_DATA(res,sql)
	},

	position_strategy: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}'`
		var sql = this.ams_sql('strategy_ratio',condition,'b.PortfolioID');
		GET_AMS_DATA(res,sql)
	},

	position_capital: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}'`
		var sql = this.ams_sql('secu_ratio',condition,'b.PortfolioID');
		GET_AMS_DATA(res,sql)
	},

	attribution_day: function(res,data_ob) {
		// console.log(data_ob)
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}' and b.ChiName = '${data_ob.account}'`
		var sql = this.ams_sql('daily_attribution',condition,'');
		GET_AMS_DATA(res,sql)
	},

	attribution_month: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}' and b.ChiName = '${data_ob.account}'`
		var sql = this.ams_sql('monthly_attribution',condition,'');
		GET_AMS_DATA(res,sql)
	},

	attribution_acc: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `a.TradingDay='${data_ob.date}' and b.ChiName = '${data_ob.account}'`
		var sql = this.ams_sql('acc_attribution',condition,'');
		GET_AMS_DATA(res,sql)
	},

	attribution_interval: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `b.ChiName='${data_ob.account}' and a.TradingDay>='${data_ob.start_date}' and a.TradingDay<='${data_ob.end_date}'`
		var sql = this.ams_sql('daily_attribution',condition,'');
		GET_AMS_DATA(res,sql)
	},

	daily_pct: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `b.ChiName='${data_ob.account}' and a.TradingDay>='${data_ob.start_date}' and a.TradingDay<='${data_ob.end_date}'`
		var sql = this.ams_sql('display_daily_netvalue',condition,'a.TradingDay');
		GET_AMS_DATA(res,sql)
	},

	value_year: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var today = new Date();
		var year_start = today.getFullYear() + '0101';
		var condition = `b.ChiName='${data_ob.account}' and a.TradingDay >= '${year_start}'`;
		var sql = this.ams_sql('display_daily_netvalue',condition,'a.TradingDay');
		GET_AMS_DATA(res,sql)
	},

	value_birth: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `b.ChiName='${data_ob.account}'`
		var sql = this.ams_sql('display_daily_netvalue',condition,'a.TradingDay');
		GET_AMS_DATA(res,sql)
	},

	value_20: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `b.ChiName='${data_ob.account}'`
		var sql = this.ams_sql('display_daily_netvalue',condition,'a.TradingDay desc limit 20');
		GET_AMS_DATA(res,sql)
	},

	value_month: function(res,data_ob) {
		data_ob = JSON.parse(data_ob);
		var condition = `b.ChiName='${data_ob.account}'`
		var sql = this.ams_sql('display_monthly_netvalue',condition,'a.TradingDay desc limit 12');
		GET_AMS_DATA(res,sql)
	},

}

// console.log(RESPONSE.get_ip())
module.exports = RESPONSE;