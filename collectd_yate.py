import collectd
import socket

HOST = '127.0.0.1'
PORT = 5038

def get_status(module):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST,PORT))
	s.settimeout(0.5)
	# allocate buffer
	rawdata = ""
	# request status
	s.send("status " + module + "\r\n")
	# receive multiple times awating timeout
	for i in range(0,3):
		try:
			rawdata += s.recv(4096)
		except socket.timeout:
			print "socket timeout"
	s.send("quit\r\n")
	try:
		print s.recv(4096)
	except socket.timeout:
		print "socket timeout"
	s.close()
	# remove CR from received string
	rawdata = rawdata.replace("\r","")
	# split data by new lines
	lines = rawdata.split("\n")
	# search for line with %%+status: and take the following
	data_line = "###unset###"
	catch_next = False
	for line in lines:
		if catch_next:
			data_line = line
			catch_next = False
		if "%%+status:"+module in line:
			catch_next = True
	if "###unset###" in data_line:
			return {}
	# split information blocks by ;
	rawelements = data_line.split(";")
	data = {}
	index = 0
	# split each block into key/value structure
	for element in rawelements:
			data[index] = {}
			for kvpair in element.split(","):
					pair = kvpair.split('=')
					if len(pair) > 1:
							data[index][pair[0]] = pair[1]
			index = index + 1
	return data


def config_func(config):
	host_set = False
	port_set = False
	for node in config.children:
			key = node.key.lower()
			val = node.values[0]
	
			if key == 'host':
					global HOST
					HOST = val
					host_set = True
			elif key == 'port':
					global PORT
					PORT = int(val)
					port_set = True
			else:
					collectd.info('yate plugin: Unknown config key "%s"' % key)
	
	if host_set:
			collectd.info('yate plugin: Using overridden host %s' % HOST)
	else:
			collectd.info('yate plugin: Using default host %s' % HOST)

def submit_data(prefix, data):
    for key in data.keys():
        instance = prefix+key
        if not data[key].isdigit():
            continue
        val = collectd.Values(type='pending_operations',type_instance=instance)
        val.plugin = 'yate'
        val.dispatch(values=[float(data[key])])

def read_func():
	# get rtp-status and submit it
	rtp_status = get_status("yrtp")
	submit_data('rtp_', rtp_status[1])
	# get sip-status and submit it	
	sip_status = get_status("sip")
	submit_data('sip_', sip_status[1])
	# get engine-status and submit it	
	engine_status = get_status("engine")
	submit_data('engine_', engine_status[1])

# register callbacks
collectd.register_config(config_func)
collectd.register_read(read_func)
