'use strict';
var http = require('http');
var url = require('url');
var RESPONSE = require('./res_ponse');
var getIP = require('ipware')().get_ip;


var server_run = function(request,response){
	var input_data = '';
	var path_name = url.parse(request.url).pathname.replace('\/','')

	if (request.url !== "/favicon.ico"){
		// console.log('url: ' + path_name)//,'   ip:',getIP(request)['clientIp'])
		request.on('data',function(chunk){
			input_data += chunk;
		})

		request.on('end',function(){
			if (path_name === 'get_ip') {
				RESPONSE[path_name](response,getIP(request)['clientIp'])
			} else if (typeof RESPONSE[path_name] === 'function'){
				RESPONSE[path_name](response,input_data);
			} else {
				RESPONSE['*'](response,path_name);
			}
		});
	}
};

var server = http.createServer(server_run);

server.listen(9999,"0.0.0.0",function(){
	console.log("server started");
});


