import logging
import warnings
from configparser import ConfigParser
warnings.filterwarnings('ignore')
################################
def start_logging():
	data_format = '%Y-%m-%d %H:%M:%S'
	log_format = '%(asctime)s -stephen- %(filename)s[line%(lineno)d] %(levelname)-3s: %(message)s'
	logging.basicConfig(level=logging.INFO, format=log_format, datefmt=data_format, filename='lht.log', filemode='a')
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter(log_format)
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)

start_logging()
##################################
cfg = ConfigParser()
cfg.read('lht.ini')

def get_config_para(section, key, func=eval):
	para = cfg.get(section,key)
	return func(para)
