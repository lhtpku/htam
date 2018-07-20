

attribution_other_pnl: function(key_col, use_data) {
	var entire_col = ['new',
					 'specu',
					 'cvbond',
					 'cta',
					 'suspend',
					 'alpha',
					 'exposure',
					 'basis',
					 'delta',
					 'gamma',
					 'vega',
					 'theta',
					 'epsilon',
					 'clean',
					 'interest',
					 'trading',
					 'other'];
	var other_pnl = 0;
	for (var key of entire_col) {
		if (key_col.index(key) === -1) {
			other_pnl = other_pnl + tmp[key];
		}
	}
	use_data.push(other_pnl);
	return use_data;

},


attribution_plot: function(sql_data,table_id,graph_title,portfolio_type) {
		var tmp = sql_data[0];
		var use_data = [];
		//////////////////////////////////
		if (portfolio_type === 'Option') {
			var use_chi = ['delta','gamma','vega','theta','epsilon','交易择时','未被解释','可转债','择时','CTA','停牌','新股','其他项'];
			var key_col = ['delta','gamma','vega','theta','epsilon','trading','other','cvbond','specu','cta','suspend','new'];

		} else if (portfolio_type === 'Bond') {
			var use_chi = ['净价损益','利息损益','交易择时','未被解释','可转债','择时','CTA','停牌','新股','其他项'];
			var key_col = ['clean','interest','trading','other','cvbond','specu','cta','suspend','new'];

		} else if (portfolio_type === 'Hedge') {
			var use_chi = ['Alpha','敞口','基差','交易择时','未被解释','可转债','择时','CTA','停牌','新股','其他项'];
			var key_col = ['alpha','exposure','basis','trading','other','cvbond','specu','cta','suspend','new'];

		} else if (portfolio_type === 'Mix') {
			var use_chi = ['Alpha','敞口','基差','交易择时','净价损益','利息损益','delta','gamma','vega','theta','epsilon','未被解释','其他项'];
			var key_col = ['alpha','exposure','basis','trading','clean','interest','delta','gamma','vega','theta','epsilon','other'];
		} else {
			alert('this portfolio type is wrong.');
		}
		///////////////////////////////////
		for (var key of key_col) {
				use_data.push(tmp[key]);
			}
		use_data = this.attribution_other_pnl(key_col, use_data);
		//////////////////////////////////////
		var json = {};
		json.xAxis = {categories:use_chi,labels:{rotation:-45},title:{text:""}};
		json.yAxis = {labels:{formatter: function() { return DATA_TYPE.to_percent(this.value)}},title:{text:""}}
		json.series = [{showInLegend:false, data:use_data,dataLabels:{enabled:true,formatter: function(){
			return DATA_TYPE.to_percent(this.y);
			}}}];
		json.chart = {type:'column',zoomType:'x'};
		json.title = {text: graph_title};
		json.credits = {enabled: true};
		$(table_id).highcharts(json);
	},