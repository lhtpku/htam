'use strict';

$(document).ready(function(){
	$('#total').load('index.html');
	// $("#single").hide();
	// $("#double").hide();
	// $("#multiple").hide();

	for (var id of ['single','double','multiple']) {
		$('#'+id).hide();
		}

	$("select").empty();
	$("select").append(GLOBAL_ESSENTIAL.strategy_choice());

	for (var id of ['use_account','strategy_in','strategy_pre','strategy_old','strategy_index']) {
		$('#'+id).empty();
	}
	$("#strategy_in").append(GLOBAL_ESSENTIAL.strategy_choice('In'))
	$("#strategy_pre").append(GLOBAL_ESSENTIAL.strategy_choice('Pre'))
	$("#strategy_old").append(GLOBAL_ESSENTIAL.strategy_choice('Old'))
	$("#strategy_index").append(GLOBAL_ESSENTIAL.strategy_choice('Index'))

	GLOBAL_ESSENTIAL.show_multi_table('#multi_table_in');

	// $("#use_account").empty();
	$("#use_account").append(GLOBAL_ESSENTIAL.account_choice());
	ACCOUNT.initial_hide();
});
 
var TABLE = {
	table_reset: function(html_sentence,table_id) {
		$(table_id).empty();
		$(table_id).append(html_sentence);
	},

	general_result: function(sql_data,table_id) {
		var xx = {};
		for (var keyy in sql_data[0]) {
			if (sql_data[0].hasOwnProperty(keyy)) {
				if (['InfoRatio','AnnuTurnover'].indexOf(keyy) !== -1) {
					xx[keyy] = DATA_TYPE.to_num2(sql_data[0][keyy]);
				} else if (keyy === 'CreateDate') {
					xx[keyy] = DATA_TYPE.to_date_str(sql_data[0][keyy]);
				} else if (['longest_neg_day','longest_dd_day','longest_dd_start','longest_dd_end'].indexOf(keyy) !== -1) {
					xx[keyy] = DATA_TYPE.raw(sql_data[0][keyy]);
				} else {
					xx[keyy] = DATA_TYPE.to_percent(sql_data[0][keyy]);
				}
			}
		}
		var html = "";
		html += HTML_FORMAT.add_table_data(["年化收益","年化波动","信息比率","最大回撤","滚动年化平均","滚动年化最小"]);
		html += HTML_FORMAT.add_table_data([xx.AnnuAlphaReturn,
											xx.AnnuAlphaStd,
											xx.InfoRatio,
											xx.MaxDrawdown,
											xx.AvgRollingAlphaReturn,
											xx.MinRollingAlphaReturn]);
		html += HTML_FORMAT.add_table_data(["日胜率","月胜率","年化换手率","去首尾各10%日收益","单日最大涨幅","单日最大跌幅"]);
		html += HTML_FORMAT.add_table_data([xx.DailyWinningRate,
											xx.MonthlyWinningRate,
											xx.AnnuTurnover,
											xx.MediumAlphaReturn,
											xx.MaxDailyProfitAlphaReturn,
											xx.MaxDailyLossAlphaReturn]);

		html += HTML_FORMAT.add_table_data(["赢日均值","输日均值","前10%日收益平均","后10%日收益平均","最长亏损天数","最长回撤天数"]);
		html += HTML_FORMAT.add_table_data([xx.AvgDailyProfitAlphaReturn,
											xx.AvgDailyLossAlphaReturn,
											xx.Top10PctAlphaReturn,
											xx.End10PctAlphaReturn,
											xx.longest_neg_day,
											xx.longest_dd_day]);

		html += HTML_FORMAT.add_table_data(["最长回撤起始","最长回撤结束","更新日期"]);
		html += HTML_FORMAT.add_table_data([xx.longest_dd_start,
											xx.longest_dd_end,
											xx.CreateDate]);
		this.table_reset(html,table_id);
	},

	multi_basic_attri: function(sql_data,table_id) {
		var new_ob = {};
		var data_order = [];
		for (var i=0; i<sql_data.length; i++) {
			new_ob[sql_data[i].attri] = sql_data[i].use_data;
			data_order.push(sql_data[i].use_data);
		}
		var html = HTML_FORMAT.add_table_head(['持仓分析(万): ','沪市市值','深市市值','50成分股','300成分股','500成分股','IH套保','IF套保','IC套保']);
		html += HTML_FORMAT.add_table_data([''].concat(data_order.splice(0,8)));
		html += HTML_FORMAT.add_table_head(['仓位结构: ','50策略','300策略','500策略','纯多头','股指期货','总仓位','更新时间']);
		html += HTML_FORMAT.add_table_data([''].concat(data_order));
		this.table_reset(html,table_id);
	},

	yearly_statistic: function(sql_data,table_id) {
		var col_name = ["年份","收益","标准差","最大回撤","信息比","收益回撤比","最大回撤起始","最大回撤结束",
						"最长亏损天数","最长回撤天数","最长回撤起始","最长回撤结束"];
		var data_col = ['Year','AnnuAlphaReturn','AnnuAlphaStd','MaxDrawdown','InfoRatio','AlphaRetOnMDD','mddStart','mddEnd',
						'longest_neg_day','longest_dd_day','longest_dd_start','longest_dd_end'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,
															1:DATA_TYPE.to_percent,
															2:DATA_TYPE.to_percent,
															3:DATA_TYPE.to_percent,
															4:DATA_TYPE.to_num2,
															5:DATA_TYPE.to_num2},DATA_TYPE.raw);
		var align_direction = LAYOUT.update_format(col_name,{0:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	account_general: function(sql_data,table_id) {
		var col_name = ['日期','账户','最新净值','当日收益','当月业绩','当年业绩','累计收益','年化收益','标准差','夏普比率','最大回撤'];
		var data_col = ['TradingDay','AccountName','NetValue','this_day','this_month','this_year','Acc','Annual','Std','SR','MDD'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.to_date_str,
															1:DATA_TYPE.raw,
															2:DATA_TYPE.to_num4,
															9:DATA_TYPE.to_num2},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	holding: function(sql_data,table_id) {
		var col_name = ['日期','代码','简称','持仓','持仓方向','最新价格','市值'];
		var data_col = ['TradingDay','Code','ChiName','Quantity','Direction','Price1','Volume'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.to_date_str,
															3:DATA_TYPE.to_thousand,
															5:DATA_TYPE.to_num2,
															6:DATA_TYPE.to_thousand},DATA_TYPE.raw);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	trading: function(sql_data,table_id) {
		var col_name = ['日期','代码','简称','交易量','交易方向','交易价格','收盘价'];
		var data_col = ['TradingDay','Code','ChiName','Quantity','Direction','FilledPrice','Price1'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.to_date_str,
															3:DATA_TYPE.to_thousand,
															5:DATA_TYPE.to_num2,
															6:DATA_TYPE.to_num2},DATA_TYPE.raw);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	new_stock_date: function(sql_data,table_id) {
		var col_name = ['日期','账户','SH','SZ','SH_20','SZ_20'];
		var data_col = ['TradingDay','AccountName','SH','SZ','SH_20','SZ_20'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.to_date_str,
															1:DATA_TYPE.raw},DATA_TYPE.to_thousand);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	new_stock_account: function(sql_data,table_id) {
		var col_name = ['日期','SH','SZ','SH_20','SZ_20'];
		var data_col = ['TradingDay','SH','SZ','SH_20','SZ_20'];
		var display_format = LAYOUT.update_format(col_name,{0: DATA_TYPE.to_date_str},DATA_TYPE.to_thousand);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	new_stock_revenue: function(sql_data,table_id) {
		sql_data = sql_data.reverse();
		var use_date = [];
		var use_data = [];
		for (var i=0;i < sql_data.length;i++) {
			var temp_date = new Date(sql_data[i].TradingDay)
			use_date.push(DATA_TYPE.to_month_str(sql_data[i].TradingDay));
			use_data.push(sql_data[i].Revenue);
			}

		var json = {};
		json.xAxis = {categories:use_date,labels:{rotation:-45},title:{text:""}};
		json.yAxis = {labels:{formatter: function() { return DATA_TYPE.to_wan(this.value)}},title:{text:""}}
		json.series = [{showInLegend:false, data:use_data,dataLabels:{enabled:true,formatter: function(){
			return DATA_TYPE.to_wan(this.y);
			}}}];
		json.title = {text: '新股收益'};
		json.chart = {type:'column',zoomType:'x'};
		json.credits = {enabled: true};
		$(table_id).highcharts(json);
	},

	value_plot: function(sql_data,table_id,graph_title) {
		var use_date = [];
		var use_data = [];
		for (var i=0;i < sql_data.length;i++) {
			var temp_date = new Date(sql_data[i].TradingDay)
			use_date.push(DATA_TYPE.to_date_str(sql_data[i].TradingDay));
			use_data.push(sql_data[i].NetValue);
			}

		var json = {};
		var tooltip = {formatter: function(){return DATA_TYPE.to_num4(this.y)}}
		json.xAxis = {categories:use_date,labels:{rotation:-45},title:{text:""}};
		json.series = [{showInLegend:false, data:use_data,dataLabels:{enabled:false,formatter: function(){
			return DATA_TYPE.to_num4(this.y);
			}}}];
		json.title = {text: graph_title};
		json.credits = {enabled: true};
		$(table_id).highcharts(json);
	},

	value_plot_column: function(sql_data,table_id,graph_title) {
		sql_data.reverse();
		var use_date = [];
		var use_data = [];
		for (var i=0;i < sql_data.length;i++) {
			var temp_date = new Date(sql_data[i].TradingDay)
			use_date.push(DATA_TYPE.to_date_str(sql_data[i].TradingDay));
			use_data.push(sql_data[i].PctChange);
			}
		var json = {};
		var tooltip = {formatter: function(){return DATA_TYPE.to_percent(this.y)}}
		json.xAxis = {categories:use_date,labels:{rotation:-45},title:{text:""}};
		json.series = [{showInLegend:false, data:use_data,dataLabels:{enabled:true,formatter: function(){
			return DATA_TYPE.to_percent(this.y);
			}}}];
		json.chart = {type:'column',zoomType:'x'};
		json.title = {text: graph_title};
		json.credits = {enabled: true};
		$(table_id).highcharts(json);
	},

	attribution_plot: function(sql_data,table_id,graph_title) {
		var use_date = ['Alpha','敞口','基差','交易','可转债','门票','新股','债券','择时','多头','碎股']
		var key_col = ['Alpha','Exposure','Basis','Trading','StructA','Ticket','New','Bond','Timing','OtherLong','Mini'];
		var use_data = [];
		for (var key of key_col){
			use_data.push(sql_data[0][key]);
		}
		var json = {};
		json.xAxis = {categories:use_date,labels:{rotation:-45},title:{text:""}};
		json.yAxis = {labels:{formatter: function() { return DATA_TYPE.to_percent(this.value)}},title:{text:""}}
		json.series = [{showInLegend:false, data:use_data,dataLabels:{enabled:true,formatter: function(){
			return DATA_TYPE.to_percent(this.y);
			}}}];
		json.chart = {type:'column',zoomType:'x'};
		json.title = {text: graph_title};
		json.credits = {enabled: true};
		$(table_id).highcharts(json);
	},


	alpha_pool: function(sql_data,table_id) {
		var col_name = ['策略','本周','当月','今年','近5日','近10日','近20日','近60日','近120日','近240日'];
		var data_col = ['Strategy','this_week','this_month','this_year','re_05','re_10','re_20','re_60','re_half','re_year'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw}, DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'left'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	in_week_report: function(sql_data,table_id) {
		var col_name = ['策略','本周','单周最大跌幅','当月','单月最大跌幅','近3月','今年','今年最大回撤',
						'回撤起始','回撤结束','是否处于回撤中','历史最大回撤','今年信息比','近12个月胜率','月胜率'];

		var data_col = ['Strategy','this_week','week_min','this_month','month_min','month_3','this_year','this_year_mdd',
						'start_mdd','end_mdd','is_in_mdd','all_year_mdd','this_year_ir','victory_12','victory_all'];

		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,
															8:DATA_TYPE.raw,
															9:DATA_TYPE.raw,
															10:DATA_TYPE.raw,
															12:DATA_TYPE.to_num2}, DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'left'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	strategy_corr: function(sql_data,table_id) {
		var col_name = ['策略','相关系数','布尔相关系数'];
		var data_col = ['sub_Strategy','Value','bool_Value'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw}, DATA_TYPE.to_num2);
		var align_direction = LAYOUT.update_format(col_name,{0:'left'},'right');
		sql_data.sort(function(a,b){
			if (a.Value < b.Value) {
				return 1;
			} else if (a.Value > b.Value) {
				return -1;
			} else {
				return 0;
			}
		});
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	tick_pct: function(sql_data,table_id) {
		var col_name = ['策略','Alpha收益','多头收益','基准收益','更新时间'];
		var data_col = ['Strategy','tick','long_posi','bench','CreateDate']
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,
															4:DATA_TYPE.raw},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'left'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	single_tick_pct: function(sql_data,table_id) {
		var col_name = ['股票代码','股票名称','股票权重','即时涨跌','更新时间'];
		var data_col = ['Symbol','ChiName','Weight','tick','CreateDate']
		var display_format = LAYOUT.update_format(col_name,{2:DATA_TYPE.to_percent,
															3:DATA_TYPE.to_percent},DATA_TYPE.raw);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'left'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	month_return: function(url,sql_data,table_id) {
		var row_col = 'Year';
		if (url === 'month_return') {
			var col_col = 'Month';
			var display_col = 'MonthlyAlphaReturn';
			var col_order = ['Year','Sum'].concat(['M01','M02','M03','M04','M05','M06','M07','M08','M09','M10','M11','M12']);
		} else if (url === 'quarter_return') {
			var col_col = 'Quarter';
			var display_col = 'QuarterlyAlphaReturn';
			var col_order = ['Year','Sum'].concat(['Q01','Q02','Q03','Q04']);
		}
		var display_format = LAYOUT.update_format(col_order,{0:DATA_TYPE.raw},DATA_TYPE.to_percent)
		var align_direction = LAYOUT.update_format(col_order,{0:'center'},'right')
		var html = GENERATE_PIVOT_TABLE(sql_data,row_col,col_col,display_col,col_order,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	latest_20_days: function(sql_data,table_id) {
		sql_data.reverse();
		var use_date = [];
		var use_data = [];
		for (var i=0;i < sql_data.length;i++) {
			var temp_date = new Date(sql_data[i].TradingDay)
			use_date.push(temp_date.toLocaleDateString());
			use_data.push(sql_data[i].DailyReturn);
		}
		var tooltip = {formatter: function(){return '<b>'+ DATA_TYPE.to_percent(this.y) +'</b>'}}
		var xAxis = {categories:use_date,labels:{rotation:-45},title:{text:""}};
		var yAxis = {labels:{formatter: function() { return DATA_TYPE.to_percent(this.value)}},title:{text:""}}
		var series = [{showInLegend:false, data:use_data,dataLabels:{enabled:true,formatter: function(){
			return DATA_TYPE.to_percent(this.y);
			}}}];

		var json = {};
		json.chart = {type:'column',zoomType:'x'};
		json.title = {text: '近20日表现'};
		json.credits = {enabled: true};
		json.xAxis = xAxis;
		json.yAxis = yAxis;
		json.series = series;
		json.tooltip = tooltip;
		$(table_id).highcharts(json);
	},

	stra_risk_exposure: function(sql_data,table_id) {
		var use_date = [];
		var use_data = [];
		for (var i=0;i < sql_data.length;i++) {
			// var temp_date = new Date(sql_data[i].Grade)
			use_date.push(sql_data[i].Grade);
			use_data.push(sql_data[i].WeightDelta);
		}
		var tooltip = {formatter: function(){return '<b>'+ DATA_TYPE.to_percent(this.y) +'</b>'}}
		var xAxis = {categories:use_date,labels:{rotation:-45},title:{text:""}};
		var yAxis = {labels:{formatter: function() { return DATA_TYPE.to_percent(this.value)}},title:{text:""}}
		var series = [{showInLegend:false, data:use_data,dataLabels:{enabled:true,formatter: function(){
			return DATA_TYPE.to_percent(this.y);
			}}}];

		var json = {};
		json.chart = {type:'column',zoomType:'x'};
		json.title = {text: ''};
		json.credits = {enabled: true};
		json.xAxis = xAxis;
		json.yAxis = yAxis;
		json.series = series;
		json.tooltip = tooltip;
		$(table_id).highcharts(json);
	},

	industry_risk: function(sql_data) {
		var distinct_para = {};
		distinct_para.col_col = 'IndustryName';
		distinct_para.col_order = ['Year',
						'汇总',
						'农林牧渔',
						'采掘',
						'化工',
						'钢铁',
						'有色金属',
						'电子',
						'汽车',
						'家用电器',
						'食品饮料',
						'纺织服装',
						'轻工制造',
						'医药生物',
						'公用事业',
						'交通运输',
						'房地产',
						'商业贸易',
						'休闲服务',
						'银行',
						'非银金融',
						'综合',
						'建筑材料',
						'建筑装饰',
						'电气设备',
						'机械设备',
						'国防军工',
						'计算机',
						'传媒',
						'通信',
					];
		var xx = FACTOR_3_TABLE(sql_data,distinct_para)
	},

	pe_risk: function(sql_data) {
		var xx = FACTOR_3_TABLE(sql_data,{})
	},

	latest_position: function(sql_data,table_id) {
		var col_name = ['代码','名称','权重'];
		var data_col = ['Symbol','ChiName','Weight'];
		var display_format = LAYOUT.update_format(col_name,{2:DATA_TYPE.to_percent},DATA_TYPE.raw);
		var align_direction = LAYOUT.update_format(col_name,{2:'right'},'center');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	two_latest_position: function(sql_data,table_id) {
		var col_name = ['代码','名称','策略1权重','策略2权重','权重差'];
		var data_col = ['Symbol','ChiName','Weight_1','Weight_2','delta_weight'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,
															1:DATA_TYPE.raw},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	position_describe: function(sql_data,table_id) {
		var row_col = 'TradingDay';
		var col_col = 'Market';
		var display_col = 'Weight';
		var col_order = ['TradingDay','SH','SZ','Weight50','Weight300','Weight500','ChangeRate'];
		var col_name = ['最新持仓日期','沪市','深市','50比重','300比重','500比重','换手率'];
		var display_format = LAYOUT.update_format(col_order,{0:DATA_TYPE.to_date_str},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_order,{0:'center'},'right');
		var html = GENERATE_PIVOT_TABLE(sql_data,row_col,col_col,display_col,col_order,display_format,align_direction,col_name);
		this.table_reset(html,table_id);
	},

	risk_general: function (sql_data,table_id) {
		var row_col = 'Strategy';
		var col_col = 'Factor';
		var display_col = 'WeightDelta';
		var col_order = ['','Industry','S_DQ_MV','S_VAL_MV','S_VAL_PE_TTM','S_VAL_PB_NEW','S_QFA_ROE'];
		var col_name = ['风险偏离度','行业','总市值','流通市值','PE','PB','ROE'];
		var display_format = LAYOUT.update_format(col_order,{0:DATA_TYPE.raw},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_order,{0:'center'},'right');
		var html = GENERATE_PIVOT_TABLE(sql_data,row_col,col_col,display_col,col_order,display_format,align_direction,col_name);
		this.table_reset(html,table_id);
	},

	futures_holding: function(sql_data,table_id) {
		var row_col = 'AccountName';
		var col_col = 'Code';
		var display_col = 'Quantity';
		var use_col = [];
		for (var i=0; i<sql_data.length; i++){
			if (use_col.indexOf(sql_data[i][col_col]) === -1) {
				use_col.push(sql_data[i][col_col]);
			}
		}
		use_col.sort();
		var col_order = ['AccountName'].concat(use_col);
		var col_name = ['账户'].concat(use_col);
		var display_format = LAYOUT.update_format(col_order,{},DATA_TYPE.raw);
		var align_direction = LAYOUT.update_format(col_order,{0:'center'},'right');
		var html = GENERATE_PIVOT_TABLE(sql_data,row_col,col_col,display_col,col_order,display_format,align_direction,col_name);
		this.table_reset(html,table_id);
	},

	futures_uplimit: function(sql_data,table_id) {
		var col_name = ['账户','IF持仓','IF上限','IH持仓','IH上限','IC持仓','IC上限'];
		var data_col = ['AccountName','IF_real','IF_uplimit','IH_real','IH_uplimit','IC_real','IC_uplimit'];
		var display_format = LAYOUT.update_format(col_name,{},DATA_TYPE.raw);
		var align_direction = LAYOUT.update_format(col_name,{0:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	strategy_alpha: function(sql_data,table_id) {
		var col_name = ['账户','策略','权重','曝露','偏离度','账户贡献','当日Alpha','近5日Alpha','近10日Alpha','今年以来Alpha'];
		var data_col = ['AccountName','Strategy','Weight','Exposure','Bias','Contribution','AlphaRatio','AlphaRatio5','AlphaRatio10','AlphaRatio01'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,
															1:DATA_TYPE.raw,
															4:DATA_TYPE.raw,
															5:DATA_TYPE.to_num1},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'left'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	strategy_long: function(sql_data,table_id) {
		var col_name = ['账户','策 略','策略权重','偏离度','当日账户贡献','近5日账户贡献','近10日账户贡献','今年以来账户贡献'];
		var data_col = ['AccountName','Strategy','Weight','Bias','Contribution','Contribution5','Contribution10','Contribution01',];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,
															1:DATA_TYPE.raw,
															2:DATA_TYPE.to_percent,
															3:DATA_TYPE.raw},DATA_TYPE.to_num1);
		var align_direction = LAYOUT.update_format(col_name,{0:'center',1:'left'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	risk_exposure: function(sql_data,table_id) {
		var col_name = ['账户','总 曝 露','50 曝 露','300 净 曝露','500 曝露','1800 净 曝露','其他 曝露'];
		var data_col = ['AccountName','expo','expo50','expo300','expo500','expo1000','expo9999'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	risk_match: function(sql_data,table_id) {
		var col_name = ['账户','IH 套保','IF 套保','IC 套保','IH 套保(%)','IF 套保(%)','IC 套保(%)'];
		var data_col = ['AccountName','IHs','IFs','ICs','stock50','stock300','stock500'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,
															4:DATA_TYPE.to_percent,
															5:DATA_TYPE.to_percent,
															6:DATA_TYPE.to_percent,},DATA_TYPE.to_thousand);
		var align_direction = LAYOUT.update_format(col_name,{0:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	position_strategy: function(sql_data,table_id) {
		var col_name = ['账户名称','Alpha','多头','Alpha 50','Alpha 300','Alpha 500','门票','分级 A','新股','债券','碎股','择时','其他多头'];
		var data_col = ['AccountName','Alpha','Speculation','Alpha50','Alpha300','Alpha500','Ticket','StructA','New','Bond','Mini','Timing','OtherLong'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	position_capital: function(sql_data,table_id) {
		var col_name = ['账户名','账户规模','总 现金','总 保证金','已用 保证金','现金','回购','可用 保证金','可 容忍风险'];

		var data_col = ['AccountName','Size','TotalCash','MarginTotal','MarginUsed','Cash','GC001','MarginAvailable','TolerableRisk'];
		var display_format = LAYOUT.update_format(col_name,{0:DATA_TYPE.raw,
															1:DATA_TYPE.to_num2},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_name,{0:'center'},'right');
		var html = GENERATE_TABLE(col_name,data_col,sql_data,display_format,align_direction);
		this.table_reset(html,table_id);
	},

	history_position_stat: function(sql_data,table_id) {
		var row_col = 'Market';
		var col_col = 'Attri';
		var display_col = 'Weight';
		var col_order = ['Market','mean','Q01','Q03','max','min','std','median','count'];
		var col_name = ['','均数','25分位数','75分位数','最大值','最小值','标准差','中位数','样本数'];
		var row_name = {'ChangeRate':'换手率','SH':'沪市','SZ':'深市','Weight50':'50比重','Weight300':'300比重','Weight500':'500比重','TotalWeight':'仓位'}
		var display_format = LAYOUT.update_format(col_order,{0:DATA_TYPE.raw,8:DATA_TYPE.raw},DATA_TYPE.to_percent);
		var align_direction = LAYOUT.update_format(col_order,{0:'center'},'right');
		var html = GENERATE_PIVOT_TABLE(sql_data,row_col,col_col,display_col,col_order,display_format,align_direction,col_name,row_name);
		this.table_reset(html,table_id);
	},

	history_mdd: function(sql_data) {
		var new_sql_data = {};
		for (var i=0;i < sql_data.length; i++) {
			new_sql_data[sql_data[i].Attri] = sql_data[i].Value
		}
		var html = '';
		var xxx = [['当前回撤',DATA_TYPE.to_percent(new_sql_data.DD)],['历史样本',new_sql_data.Sample]];
		for (var i=0; i < xxx.length; i++) {
			html += HTML_FORMAT.add_table_data(xxx[i]);
		}
		this.table_reset(html,'#display_table');
		delete new_sql_data.DD;
		delete new_sql_data.Sample;

		var use_date = [];
		var use_data = [];
		for (var keyy in new_sql_data) {
			if (new_sql_data.hasOwnProperty(keyy)) {
				use_date.push(keyy);
				use_data.push(new_sql_data[keyy]);
			}
		}
		var tooltip = {formatter: function(){return '<b>'+ DATA_TYPE.to_percent(this.y) +'</b>'}}
		var xAxis = {categories:use_date,labels:{rotation:-45},title:{text:""}};
		var yAxis = {labels:{formatter: function() { return DATA_TYPE.to_percent(this.value)}},title:{text:""}}
		var series = [{showInLegend:false, data:use_data,dataLabels:{enabled:true,formatter: function(){
			return DATA_TYPE.to_percent(this.y);
			}}}];
		var json = {};
		json.chart = {type:'column',zoomType:'x'};
		json.title = {text: '历史相同回撤后表现'};
		json.credits = {enabled: true};
		json.xAxis = xAxis;
		json.yAxis = yAxis;
		json.series = series;
		json.tooltip = tooltip;
		$('#chart').highcharts(json);
	},

	multi_table: function(table_id){
		var html = '';
		html += HTML_FORMAT.add_table_head(['Strategy','Weight','HedgeRatio','TotalAsset']);
		var first_1 = "<td><select>" + GLOBAL_ESSENTIAL.strategy_choice() + "</select></td>"
		var last_1 = "<td class='TotalAsset' contentEditable='true' style='text-align: right'>1</td>"
		var first_3 = first_1 + "<td class='Weight' contentEditable='true' style='text-align: right'></td>"
		first_3 +=	"<td class='HedgeRatio' contentEditable='true' style='text-align: right'>1</td>"
		html += HTML_FORMAT.add_tr(first_3 + last_1);
		for (var i=1; i<9; i++) {
			var temp_id = 'multi_'+ i.toString()
			html += HTML_FORMAT.add_tr(first_3)
		}
		this.table_reset(html,table_id)
	},
};


var FACTOR_3_TABLE = function(sql_data,distinct_para){
	var ordinary_para = {
		row_col:'Year',
		col_col:'Grade',
		col_order:['Year',
					'Total',
					'Grade01',
					'Grade02',
					'Grade03',
					'Grade04',
					'Grade05',
					'Grade06',
					'Grade07',
					'Grade08',
					'Grade09',
					'Grade10'],
		display_col_array: ['AlphaReturn','ChoiceAlphaReturn','NeutralAlphaReturn'],
		display_table_id: ['#display_table_1','#display_table_2','#display_table_3']
	};

	var all_para = ['row_col','col_col','col_order','display_col_array','display_table_id'];
	for (var x of all_para){
		if (distinct_para.hasOwnProperty(x)){
			ordinary_para[x] = distinct_para[x];
		}
	}
	ordinary_para.display_format = LAYOUT.update_format(ordinary_para.col_order,{0:DATA_TYPE.raw},DATA_TYPE.to_percent);
	ordinary_para.align_direction = LAYOUT.update_format(ordinary_para.col_order,{0:'center'},'right');

	for (var i=0; i < ordinary_para.display_col_array.length; i++) {
		var html = GENERATE_PIVOT_TABLE(sql_data,
			ordinary_para.row_col,
			ordinary_para.col_col,
			ordinary_para.display_col_array[i],
			ordinary_para.col_order,
			ordinary_para.display_format,
			ordinary_para.align_direction);
		TABLE.table_reset(html,ordinary_para.display_table_id[i]);
	}
	$('.pivot_table_title').show();	
};


var GENERATE_PIVOT_TABLE = function(sql_data,row_col,col_col,display_col,col_order,display_format,align_direction,col_name='',row_name={}){
	var html = '';
	if (col_name === '') {
		html = HTML_FORMAT.add_table_head(col_order);
	} else {
		html = HTML_FORMAT.add_table_head(col_name);
	}
	var new_sql_data = {};
	var new_row = []
	for (var i=0;i < sql_data.length; i++) {
		if (! new_sql_data.hasOwnProperty(sql_data[i][row_col])) {
			new_row.push(sql_data[i][row_col]);
			new_sql_data[sql_data[i][row_col]] = {};
			if (row_name.hasOwnProperty(sql_data[i][row_col])) {
				new_sql_data[sql_data[i][row_col]][row_col] = row_name[sql_data[i][row_col]];
			} else {
				new_sql_data[sql_data[i][row_col]][row_col] = sql_data[i][row_col];
			}
		}
		new_sql_data[sql_data[i][row_col]][sql_data[i][col_col]] = sql_data[i][display_col];
	}
	new_row.sort();
	for (var i=0; i < new_row.length;i++) {
		html += HTML_FORMAT.add_table_data_object(new_sql_data[new_row[i]],col_order,display_format,align_direction)
	}
	return html;
};


var GENERATE_TABLE = function (col_name,data_col,sql_data,display_format,align_direction){
	if (col_name.length !== data_col.length) {
		alert('列名长度对应不上');
		return ;
	}
	for (var i=0; i<data_col.length; i++){
		if (!sql_data[0].hasOwnProperty(data_col[i])){
			alert('数据中没有属性: '+ data_col[i])
			return ;
		}
	}
	var html = '';
	html = HTML_FORMAT.add_table_head(col_name)
	for (var i=0; i<sql_data.length; i++) {
		html += HTML_FORMAT.add_table_data_object(sql_data[i],data_col,display_format,align_direction);
	}
	return html;
};
 

var HTML_FORMAT = {
	add_start: function(tag) {
		return `<${tag}>`;
	},
	add_end: function(tag) {
		return `</${tag}>`;
	},
	add_tr: function(data) {
		return `<tr>${data}</tr>`;
	},
	add_start_end: function(data,align_direction,tag) {
		return `<${tag} style='text-align:${align_direction}'}>${data}</${tag}>`;
	},

	add_table_head: function(data,align_direction='center'){
		var html = this.add_start('tr');
		for (var i=0; i<data.length; i++){
			html += this.add_start_end(data[i],align_direction,'th');
		}
		html += this.add_end('tr');
		return html;
	},

	add_table_data: function(data) {
		var html = this.add_start('tr');
		for (var i = 0; i < data.length; i++) {
			html += this.add_start_end(data[i],'center','td');
		}
		html += this.add_end('tr');
		return html;
	},

	add_table_data_object: function(data,data_col,display_format,align_direction) {
		var html = this.add_start('tr');
		for (var i = 0; i < data_col.length; i++) {
			if (typeof data[data_col[i]] === 'undefined') {
				var write_data = '';
			} else {
				var write_data = display_format[i](data[data_col[i]]);
			}
			html += this.add_start_end(write_data,align_direction[i],'td');
		}
		html += this.add_end('tr');
		return html;
	},
};


var DATA_TYPE = {
	raw: function(num) {
		return num;
	},
	to_percent: function(num,digit=2) {
		return (100*num).toFixed(digit) + "%";
	},
	to_num4: function(num,digit=4) {
		return num.toFixed(digit);
	},
	to_num1: function(num) {
		return num.toFixed(1);
	},
	to_num2: function(num,digit=2) {
		return num.toFixed(digit);
	},
	to_thousand: function(num) {
		var out = [];
		num = parseInt(num).toString();
		if (num.length <= 3) {
			return num;
		}
		var xx = parseInt(num.length / 3);
		var yy = num.length % 3;

		var temp_xx;
		if (yy === 0) {
			temp_xx = 1;
		} else {
			temp_xx = 0
		}

		for (var i=xx; i >= temp_xx; i--){
			out.unshift(num.substring(3*(i-1)+yy,3*i+yy));
		}
		return out.join(',')
	},

	to_int: function(num) {
		return parseInt(num);
	},
	to_date_str: function(num) {
		var temp_date = new Date(num)
		return temp_date.toLocaleDateString();
	},
	to_month_str: function(num) {
		var temp_date = new Date(num);
		return temp_date.toLocaleDateString().substring(0,7);
	},
	to_wan: function(num) {
		return parseInt(num/10000);
	},
	last_week_day: function() {
		var date = new Date();
		var offset_day = 2*(date.getDay() === 1) + 1;
		date = new Date(date - offset_day * (24*60*60*1000));
		return date.toLocaleDateString();
	},
};


var LAYOUT = {
	data_to_list: function(num,col) {
		var out = [];
		for (var i=0;i < col.length;i++){
			out[i] = num;
		}
		return out;
	},
	update_format: function(data,detail,default_detail){
		var out = this.data_to_list(default_detail,data);
		for(var i in detail){
			if (detail.hasOwnProperty(i)){
				out[i] = detail[i];
			}
		}
		return out;
	},
};



var GLOBAL_ESSENTIAL = {
	ontab: function(table_id){
		$("#single").hide();
		$("#double").hide();
		$("#multiple").hide();
		$('.pivot_table_title').hide()
		$(table_id).show();
	},

	strategy_choice: function(strategy_status = ''){
		var all_strategy = this.get_sql_data('load_strategy',strategy_status);
		var html = '<option selected="selected"></option>';
		for(var i = 0;i<all_strategy.length;i++) {
			html += `<option value='${all_strategy[i].Strategy}'>${all_strategy[i].Strategy}</option>`;
		}
		return html;
	},

	account_choice: function() {
		var all_account = this.get_sql_data('load_account','');
		var html = '<option selected="selected"></option>';
		for (var i = 0; i<all_account.length; i++) {
			html += `<option value='${all_account[i].ChiName}'>${all_account[i].ChiName}</option>`;
		}
		return html;
	},

	sub_inital_hide: function() {
		for (var id of ['risk_split','pool_strategy_performance','risk_exposure']) {
			$('#'+id).hide();
		}
	},

	sub_button_show: function(table_id){
		this.sub_inital_hide();
		this.inital_web();
		$(table_id).show();
	},

	show_multi_table: function(table_id){
		TABLE.multi_table(table_id);
	},

	inital_web: function() {
		$('#display_table').empty();
		$('#chart').empty();
		$('#display_table_1').empty();
		$('#display_table_2').empty();
		$('#display_table_3').empty();
	},

	is_two_strategy_different: function() {
		var strategy_1 = $('#double_strategy_1').val();
		var strategy_2 = $('#double_strategy_2').val();
		if ((strategy_1 === '') | (strategy_2 === '') | (strategy_1 === strategy_2)) {
			alert('策略必须填写且不能相同');
			return;
		}

		var corr = this.get_sql_data('two_stra_corr',JSON.stringify({stra1:strategy_1,stra2:strategy_2}))
		
		corr = DATA_TYPE.to_num2(corr[0].Value)
		$('#stra1_stra2_corr').val(corr);

		return [strategy_1,strategy_2];
	},

	show_double_table: function(two_strategy,url,show_id) {
		var sql_data_1 = this.get_sql_data(url,two_strategy[0]);
		var sql_data_2 = this.get_sql_data(url,two_strategy[1]);
		return [sql_data_1,sql_data_2]
	},

	double_describe: function(sql_data) {
		var all_code = [];
		var all_code_1 = [];
		var all_code_2 = [];
		var new_sql_data_1 = {};
		var new_sql_data_2 = {};
		var out = [];
		for (var i=0;i<sql_data[0].length;i++){
			var code = sql_data[0][i]['Symbol']
			if (all_code.indexOf(code) === -1) {
				all_code.push(code)
			}
			all_code_1.push(code)
			new_sql_data_1[code] = sql_data[0][i]
		}

		for (var i=0;i<sql_data[1].length;i++){
			var code = sql_data[1][i]['Symbol']
			if (all_code.indexOf(code) === -1) {
				all_code.push(code)
			}
			all_code_2.push(code)
			new_sql_data_2[code] = sql_data[1][i]
		}
		for (var i=0;i < all_code.length;i++) {
			var weight_1 = 0;
			var weight_2 = 0;
			if (all_code_1.indexOf(all_code[i]) !== -1) {
				weight_1 = new_sql_data_1[all_code[i]]['Weight']
				var chiname = new_sql_data_1[all_code[i]]['ChiName']
			}
			if (all_code_2.indexOf(all_code[i]) !== -1) {
				weight_2 = new_sql_data_2[all_code[i]]['Weight']
				var chiname = new_sql_data_2[all_code[i]]['ChiName']
			}
			out[i] = {
				'Symbol':all_code[i],
				'Weight_1':weight_1,
				'Weight_2':weight_2,
				'ChiName':chiname,
				'delta_weight':weight_1 - weight_2
			};
		}
		out.sort(function(a,b){
			if (a.delta_weight < b.delta_weight) {
				return 1;
			} else if (a.delta_weight > b.delta_weight) {
				return -1;
			} else {
				return 0;
			}
		});
		return out

	},

	request_double_table: function(url) {
		// ,'strategy_name_1','strategy_name_2'
		for (var id of ['double_table_1','double_table_2','chart_1','chart_2','double_table_1_2']) {
			$('#'+id).empty();
		}
		var stra = this.is_two_strategy_different();
		// $('#strategy_name_1').val(stra[0]+':')
		// $('#strategy_name_2').val(stra[1]+':')
		var sql_data = this.show_double_table(stra,url);

		if (['yearly_statistic','long_yearly_statistic'].indexOf(url) !== -1) {
			TABLE.yearly_statistic(sql_data[0],'#double_table_1');
			TABLE.yearly_statistic(sql_data[1],'#double_table_2');
		} else if (['month_return','quarter_return'].indexOf(url) !== -1) {
			TABLE.month_return(url,sql_data[0],'#double_table_1');
			TABLE.month_return(url,sql_data[1],'#double_table_2');
		} else if (url === 'latest_20_days') {
			TABLE.latest_20_days(sql_data[0],'#chart_1');
			TABLE.latest_20_days(sql_data[1],'#chart_2');
		} else if (url === 'history_position_stat') {
			TABLE.history_position_stat(sql_data[0],'#double_table_1');
			TABLE.history_position_stat(sql_data[1],'#double_table_2');
		} else if (url === 'general_result') {
			TABLE.general_result(sql_data[0],'#double_table_1');
			TABLE.general_result(sql_data[1],'#double_table_2');
		} else if (url === 'latest_position') {
			var position_describe_1 = this.get_sql_data('position_describe',stra[0]);
			var position_describe_2 = this.get_sql_data('position_describe',stra[1]);
			TABLE.position_describe(position_describe_1,'#double_table_1');
			TABLE.position_describe(position_describe_2,'#double_table_1_2');
			sql_data = this.double_describe(sql_data)
			TABLE.two_latest_position(sql_data,'#double_table_2');
		}
		return

	},

	get_sql_data: function(use_url,strategy){
		var get_data;
		var setting = {
				url:use_url,
				data:strategy,
				type:'post',
				dataType:'json',
				async:false,
				success:function(rtn){
					get_data = rtn;
				}
			}
		$.ajax(setting);
		if (typeof get_data === 'undefined') {
			alert('未从数据库中得到数据.');
			wrong;
		} else if (get_data.length === 0) {
			alert('数据为空');
			wrong;
		} else {
			return get_data;
		}
	},

	strategy_check: function() {
		var strategy_in = $('#strategy_in').val()
		var strategy_pre = $('#strategy_pre').val()
		var strategy_old = $('#strategy_old').val()
		var strategy_index = $('#strategy_index').val()
		var strategy = strategy_in || strategy_pre || strategy_old ||strategy_index
		return strategy;
	},

	strategy_reset: function(select_id){
		if (select_id === '#double_strategy_1') {
			var strategy = $(select_id).val();
			var strategy_description = this.get_sql_data('strategy_description',strategy)
			$('#BenchName_1').val(strategy_description[0].BenchName);
			$('#Description_1').val(strategy_description[0].Description);
			return;
		} else if (select_id === '#double_strategy_2') {
			var strategy = $(select_id).val();
			var strategy_description = this.get_sql_data('strategy_description',strategy)
			$('#BenchName_2').val(strategy_description[0].BenchName);
			$('#Description_2').val(strategy_description[0].Description);
			return;
		}
		this.inital_web();
		for (var stra of ['#strategy_in','#strategy_pre','#strategy_old','#strategy_index']){
			if (select_id !== stra) {
				$(stra).val("")
			}
		}
		var strategy = this.strategy_check();
		var strategy_description = this.get_sql_data('strategy_description',strategy)
		$('#BenchName').val(strategy_description[0].BenchName);
		$('#Description').val(strategy_description[0].Description);
		return strategy;
	},

	request_table: function(url,strategy_id) {
		var strategy = this.strategy_check()
		if (strategy === '') {
			alert('请选择策略');
			return;
		}
		this.inital_web();
		
		if (['industry_risk','pe_risk','pb_risk','mv_risk','turnrate_risk'].indexOf(url) === -1){
			$('#risk_split').hide();
			$('.pivot_table_title').hide();
		} 
		if (['alpha_pool','long_pool','in_week_report','pre_week_report'].indexOf(url) === -1){
			$('#pool_strategy_performance').hide();
			$('.pivot_table_title').hide();
		}
		if (['industry_exposure','mv_exposure','float_mv_exposure','pe_exposure','pb_exposure','roe_exposure'].indexOf(url) === -1){
			$('#risk_exposure').hide();
			$('.pivot_table_title').hide();
		}

		var sql_data = this.get_sql_data(url,strategy)
		if (['yearly_statistic','long_yearly_statistic'].indexOf(url) !== -1) {
			TABLE.yearly_statistic(sql_data,'#display_table');
		} else if (['month_return','quarter_return'].indexOf(url) !== -1) {
			TABLE.month_return(url,sql_data,'#display_table');
		} else if (url === 'tick_pct') {
			TABLE.tick_pct(sql_data,'#display_table');
		} else if (url === 'single_tick_pct') {
			TABLE.single_tick_pct(sql_data,'#display_table');
		} else if (url === 'latest_20_days') {
			TABLE.latest_20_days(sql_data,'#chart');
		} else if (['pe_risk','pb_risk','mv_risk','turnrate_risk'].indexOf(url) !== -1) {
			TABLE.pe_risk(sql_data);
		} else if (url === 'industry_risk') {
			TABLE.industry_risk(sql_data);
		} else if (url === 'latest_position') {
			var position_describe = this.get_sql_data('position_describe',strategy);
			TABLE.position_describe(position_describe,'#display_table');
			TABLE.latest_position(sql_data,'#display_table_1');
		} else if (url === 'history_position_stat') {
			TABLE.history_position_stat(sql_data,'#display_table');
		} else if (['alpha_pool','long_pool'].indexOf(url) !== -1) {
			TABLE.alpha_pool(sql_data,'#display_table');
		} else if (['in_week_report','pre_week_report'].indexOf(url) !== -1) {
			TABLE.in_week_report(sql_data,'#display_table')
		} else if (url === 'strategy_corr') {
			TABLE.strategy_corr(sql_data,'#display_table');
		} else if (url === 'history_mdd') {
			TABLE.history_mdd(sql_data)
		} else if (url === 'general_result') {
			TABLE.general_result(sql_data,'#display_table');
		} else if (['industry_exposure','mv_exposure','float_mv_exposure','pe_exposure','pb_exposure','roe_exposure'].indexOf(url) !== -1){
			var risk_general = this.get_sql_data('risk_general',strategy);
			// console.log(risk_general)
			TABLE.risk_general(risk_general,'#display_table');
			TABLE.stra_risk_exposure(sql_data,'#chart');
		}
	},

	multi_table: function(url) {
		var strategy = 'Multi';
		$('#multi_table').empty();
		$('#multi_chart').empty();
		var ipInfo = GLOBAL_ESSENTIAL.get_sql_data('get_ip','fuck');

		if (url === 'multi_yearly_statistic') {
			var sql_data = this.get_sql_data('yearly_statistic',ipInfo);
			TABLE.yearly_statistic(sql_data,'#multi_table');
		} else if (url === 'multi_general_result') {
			var sql_data = this.get_sql_data('general_result',ipInfo);
			TABLE.general_result(sql_data,'#multi_table');
		} else if (url === 'multi_month_return') {
			var sql_data = this.get_sql_data('month_return',ipInfo);
			TABLE.month_return('month_return',sql_data,'#multi_table');
		} else if (url === 'multi_quarter_return') {
			var sql_data = this.get_sql_data('quarter_return',ipInfo);
			TABLE.month_return('quarter_return',sql_data,'#multi_table');
		} else if (url === 'multi_latest_20_days') {
			var sql_data = this.get_sql_data('latest_20_days',ipInfo);
			TABLE.latest_20_days(sql_data,'#multi_chart');
		} else if (url === 'multi_basic_attri') {
			var sql_data = this.get_sql_data(url,ipInfo);
			TABLE.multi_basic_attri(sql_data,'#multi_table');
		}
	},
}

var MULTI_CALCU = {
	claculate_data: function(table_id) {
		var table_data = this.get_data(table_id);
		var table_data = this.data_add_ip(table_data);
		// console.log(GLOBAL_ESSENTIAL.get_sql_data('get_ip','S1104C'));
		var table_data = this.check_data(table_data);
		var table_data_json = JSON.stringify({array:table_data});
		var python_calcu = GLOBAL_ESSENTIAL.get_sql_data('python_calcu',table_data_json);
		alert(python_calcu.message + "\ntotal strategy: " + (table_data.length - 1).toString());
		return;
	},

	get_data: function(table_id) {
		var table = $(table_id);
		var table_content = [];
		table.find('tr').each(function(index_1,element){
			var row = $(this);
			var row_content = [];
			row.children().each(function(index_2,element) {
				var cell = $(this);
				if (index_1 === 0) {
					row_content.push(cell.html())
				} else if (index_2 === 0) {
					row_content.push(cell.children('select').val());
				} else {
					row_content.push(Number(cell.html()));
				}	
			});
			table_content.push(row_content);
		});
		return table_content;
	},

	data_add_ip: function(table_data) {
		table_data[0].push('IP');
		var ipInfo = GLOBAL_ESSENTIAL.get_sql_data('get_ip','fuck');
		for (var i=1;i < table_data.length;i++) {
			table_data[i].push(ipInfo);
		}
		return table_data;
	},

	check_data: function(table_data) {
		var del_row = 0;
		if (table_data.length <= 1) {
			alert('策略不能为空');
			wrong;
		} else if (table_data[1][0] === '') {
			alert('策略需从第一行开始写');
			wrong;
		}
		table_data = table_data.filter(function(ele){
			return ele[0] !== "";
		});
		for (var i=1; i<table_data.length; i++) {
			if ((table_data[i][1]< -101) | (table_data[i][1] > 101) | (table_data[i][1] === '')) {
				alert('权重需要在-100到100之间,不能为'+table_data[i][1].toString());
				wrong;
			} else if ((table_data[i][2]< -0.001) | (table_data[i][2] > 1.001) | (table_data[i][1] === '')) {
				alert('对冲比例需要在0到1之间,不能为'+table_data[i][2].toString());
				wrong;
			} else if (table_data[0][3] < 0) {
				alert('总资产需要大于0,不能为'+table_data[0][3].toString());
				wrong;
			}
		}
		return table_data;
	},

}

var ACCOUNT = {
	all_id: ['account_select','date_select','strategy_select',
			'account_value','account_attribution','account_position',
			'account_risk','account_strategy','account_futures','account_new_stock','account_holding','account_trading'],

	initial_hide: function() {
		for (var id of this.all_id) {
			$('#'+id).hide();
		}
	},

	choice_show: function(array_show,table_id,show_id){
		if (array_show.indexOf(table_id) !== -1) {
			$(show_id).show();
		}
	},

	show: function(table_id) {
		this.initial_hide();
		$('#'+table_id).show();
		$('#display_table').empty();
		$('#graph').empty();
		var account_show = ['account_value','account_attribution','account_new_stock','account_holding','account_trading'];
		this.choice_show(account_show,table_id,"#account_select");

		var date_show = ['account_attribution','account_position','account_risk','account_strategy','account_futures',
						'account_new_stock','account_holding','account_trading'];
		this.choice_show(date_show,table_id,"#date_select");

		var strategy_show = ['account_holding','account_trading'];
		this.choice_show(strategy_show,table_id,"#strategy_select");
	},

	para_process: function(use_para) {
		// $('#para_select').show();
		// $('#sub_button').show();
		var all_para = [];
		all_para[0] = $('#use_account').val();
		all_para[1] = $('#use_date').val() || DATA_TYPE.last_week_day();
		all_para[2] = $('#use_strategy').val();
		for (var x of use_para) {
			if ((all_para[x] === "") | (typeof all_para[x] === 'undefined')) {
				if (x === 0) {
					alert('账户不能为空');
				} else if (x === 1) {
					alert('日期不能为空');
				} else {
					alert('策略不能为空');
				}
				wrong;	
			} 
		}
		return JSON.stringify({account:all_para[0],date:all_para[1],strategy:all_para[2]});
	},

	request_table:function(url) {
		$('#display_table').empty();
		$('#graph').empty();
		if (url === 'account_general') {
			// $('#para_select').hide();
			// $('#sub_button').hide();
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,{});
			TABLE.account_general(sql_data,'#display_table');
		} else if (url === 'holding') {
			var para = this.para_process([0,1,2]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.holding(sql_data,'#display_table');
		} else if (url === 'trading') {
			var para = this.para_process([0,1,2]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.trading(sql_data,'#display_table');
		} else if (url === 'new_stock_date') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.new_stock_date(sql_data,'#display_table');
		} else if (url === 'new_stock_account') {
			var para = this.para_process([0]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.new_stock_account(sql_data,'#display_table');
		} else if (url === 'new_stock_revenue') {
			var para = this.para_process([0]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.new_stock_revenue(sql_data,'#graph');
		} else if (url === 'futures_holding') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.futures_holding(sql_data,'#display_table');
		} else if (url === 'futures_uplimit') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.futures_uplimit(sql_data,'#display_table');
		} else if (url === 'strategy_alpha') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.strategy_alpha(sql_data,'#display_table');
		} else if (url === 'strategy_long') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.strategy_long(sql_data,'#display_table');
		} else if (url === 'risk_exposure') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.risk_exposure(sql_data,'#display_table');
		} else if (url === 'risk_match') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.risk_match(sql_data,'#display_table');
		} else if (url === 'position_strategy') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.position_strategy(sql_data,'#display_table');
		} else if (url === 'position_capital') {
			var para = this.para_process([1]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			TABLE.position_capital(sql_data,'#display_table');
		} else if (['attribution_day','attribution_month','attribution_acc'].indexOf(url) !== -1) {
			var para = this.para_process([0,1]);
			var portfolio_type = GLOBAL_ESSENTIAL.get_sql_data('portfolio_type',para)[0]['PortfolioType'];
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			var graph_title = "";
			if (url === 'attribution_day') {
				graph_title = '当日业绩归因';
			} else if (url === 'attribution_month') {
				graph_title = '当月业绩归因';
			} else {
				graph_title = '累计业绩归因';
			}
			TABLE.attribution_plot(sql_data,'#graph',graph_title, portfolio_type);
		} else if (['value_year','value_birth'].indexOf(url) !== -1) {
			var para = this.para_process([0]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			var graph_title = "";
			if (url === 'value_year') {
				graph_title = '今年以来';
			} else {
				graph_title = '成立以来';
			}
			TABLE.value_plot(sql_data,'#graph',graph_title);
		} else if (['value_20','value_month'].indexOf(url) !== -1) {
			var para = this.para_process([0]);
			var sql_data = GLOBAL_ESSENTIAL.get_sql_data(url,para);
			var graph_title = "";
			if (url === 'value_20') {
				graph_title = '近20日表现';
			} else {
				graph_title = '月度业绩';
			}
			TABLE.value_plot_column(sql_data,'#graph',graph_title);
		}
	},
}