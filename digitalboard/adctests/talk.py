import uhal
import csv
from time import sleep
import sys
import random
import datetime

#Initialize board
def init_board(library,deviceaddress,xmlfile):
	global board
	uhal.setLogLevelTo(uhal.LogLevel.INFO)
	board = uhal.getDevice("glib", "ipbusudp-2.0://"+deviceaddress+":50001", "file://"+xmlfile)
	board.getClient().setTimeoutPeriod(10000)
	nodeslist=board.getNodes()
	deletelist=[]
	# Only use end notes. Depth 2
	#i_a=0
	#nodeslist_ext=[]
	#nodes_a=[]
	#nodes_b=[]
	#for node in nodeslist:
	#	splitnode=node.split('.'))
	#	nodes_a=splitnode[0]
	#	nodes_b=splitnode[-1]
	#for node_a in nodes_a
	#	for node_b in nodes_b
	#		if node_b == node_a
	#			if node_a not in deletelist:
	#				deletelist.append(i_a)
	#	i_a+=1
	#keeplist=[]
	#for i_d in range(0,(i_a-1)):
	#	if i_d not in deletelist:
	#		keeplist.append(i_d)
	#nodeslist=[nodeslist[i] for i in keeplist]
	return nodeslist

def std_address():
	global library,deviceaddress,xmlfile
	library="glib"
	deviceaddress="192.168.235.0"
	xmlfile="ipbus_example.xml"
	

#Initialize node
def init_node(nodename):
	ctrl_reg= board.getNode(nodename)
	return ctrl_reg

# Check if it is possible to read and write the register
def show_permits(node):
	rights=node.getPermission()
	board.dispatch()
	return rights
	
# Read register
def readreg(node):
	readvalue=node.read()
	board.dispatch()
	return readvalue

# Write register
def writereg(node,writevalue):
	node.write(writevalue)
	board.dispatch()
# Write register and do not dispatch board
def writeregandwait(node,writevalue):
	node.write(writevalue)

# Write register, read back and compare values
def testreg(node):
	writevalue=random.randint(0,4294967295) #random uint value
	writereg(node,writevalue)
	readvalue=readreg(node)
	if writevalue==readvalue:
		failure = 0
	else:
		failure = 1
	#print writevalue,readvalue,failure
	return failure

# Create bit array
def bitfield(n,arraylength):
	bitarray=[int(digit) for digit in bin(n)[2:]]
	if len(bitarray)<arraylength:
		lengthtoadd=arraylength-len(bitarray)
		arraytoadd=[]
		for i in range(0,lengthtoadd):
			arraytoadd.append(0)
		bitarray = arraytoadd+bitarray
	print bitarray
	return bitarray 

def parse_clk(filename):
	with open(filename, 'rb') as csvfile:
		cvr= csv.reader(csvfile, delimiter=',', quotechar='|')
		addr_list=[]
		data_list=[]
		for row in cvr:
			print row
			addr_list.append(int(row[0]))
			data_unformatted=str(row[1])
			data_unformatted=data_unformatted.replace(" ", "")
			data_hex="0x"+data_unformatted[0:-1]
			data_list.append(int(data_hex,0))
		return [addr_list,data_list]
	

def main_reliability():
	#Parameters
	std_address()
	totaltests=100000
	loggingperiod=100000/10
	nodes=["reg","clk_i2c.data","ctrl_reg.id"] #leave emty if every node should be checked

	#Logfile
	logfile = open("talk.log","w")
	logfile.write("IP address "+deviceaddress+"\n")
	logfile.write("Importing nodes from "+xmlfile+"\n")
	logfile.write(str(datetime.datetime.now())+"\n")
	logfile.write("----------------------------\n")
	logfile.write("")
	logfile.close()

	#Initialize
	nodeslist=init_board(library,deviceaddress,xmlfile)
	if not nodes:
		nodesToCheck=nodeslist
	else:
		nodesToCheck=nodes

	#Try to read out each node
	for node in nodeslist:
		reg=init_node(node)
		readvalue=readreg(reg)
		nodeinfo="Read out value for node "+node+": "+str(hex(readvalue))+"\n"
		print nodeinfo
		with open("talk.log", "a") as logfile:
			logfile.write(nodeinfo)

	#Test
	for node in nodesToCheck:
		reg=init_node(node)
		if str(show_permits(reg))=="READWRITE":
			i=0
			e=0
			nodeinfo="Testing node "+node+"\n"+\
				"----------------------------\n"
			print(nodeinfo)
			with open("talk.log", "a") as logfile:
				logfile.write(nodeinfo)
			while i<totaltests:
				e+=testreg(reg)
				i+=1
				if i%loggingperiod==0:
					status=str(datetime.datetime.now())+": "+str(i)+" test performed, "+\
						str(e)+" errors detected ("+str(e*100/i)+"%).\n"
					print status	
					with open("talk.log", "a") as logfile:
						logfile.write(status)
		del reg


def main_clockconfig():
	clockconfig=parse_clk("si5326_012016.txt")
	std_address()
	init_board(library,deviceaddress,xmlfile)
	# initialize registers
	ctrl=init_node("clk_i2c.ctrl")	
	ps_lo=init_node("clk_i2c.ps_lo")	
	ps_hi=init_node("clk_i2c.ps_hi")	
	data=init_node("clk_i2c.data")	
	cmd_stat=init_node("clk_i2c.cmd_stat")	
	soft_rst=init_node("ctrl_reg.ctrl.soft_rst")	
	si5326_rst=init_node("ctrl_reg.ctrl.si5326_rst")	
	id=init_node("ctrl_reg.id")	
	# soft reset
	#writereg(soft_rst,0x1)
	# enable I2C
	writereg(ctrl,0x80)
	writereg(cmd_stat,0x0)
	# set clk prescaler
	writereg(ps_lo,0x3F)
	writereg(ps_hi,0x0)
	# read back
	print "readback:"
	print "id: "+ str(hex(readreg(id)))
	print "ctrl: "+ str(hex(readreg(ctrl)))
	print "ps_lo: "+str(hex(readreg(ps_lo)))
	print "ps_hi: "+str(hex(readreg(ps_hi)))
	print "data: "+str(hex(readreg(data)))
	print "cmd_stat: "+str(hex(readreg(cmd_stat)))



	#writereg(cmd_stat,0x41) #stop
	sleeptime=0.01
	sleep(sleeptime)
	#print "cmd_stat: "+str(hex(readreg(cmd_stat)))
	addr_list=clockconfig[0]
	data_list=clockconfig[1]
	i=0
	a="""for byteaddress in addr_list[0:-1]:
		if i%2==0:
			writeregandwait(cmd_stat,0x90) #start
			writeregandwait(data,0xD0) #slave address
			board.dispatch()
			sleep(sleeptime)

			writeregandwait(data,byteaddress) #byte address
			writeregandwait(cmd_stat,0x10)
			board.dispatch()
			sleep(sleeptime)

			writeregandwait(data,data_list[i]) #data 0
			writeregandwait(cmd_stat,0x10)
			board.dispatch()
			sleep(sleeptime)

			writeregandwait(data,data_list[i+1]) #data 1
			writeregandwait(cmd_stat,0x10)
			board.dispatch()
			sleep(sleeptime)

			writereg(cmd_stat,0x40) #stop
			sleep(sleeptime)
			print str(byteaddress)+" and "+str(byteaddress+1)+": "+hex(data_list[i])+ ", "+hex(data_list[i+1])
			sleep(sleeptime)
		i += 1"""
	writeregandwait(cmd_stat,0x90) #start
	writeregandwait(data,0xD0) #slave address
	board.dispatch()
	sleep(sleeptime)
	writeregandwait(data,0x0) #byte address
	writeregandwait(cmd_stat,0x10)
	board.dispatch()
	sleep(sleeptime)
	for writeaddress in range(0,143):
		flag=0
		i=0
		for byteaddress in addr_list:
			if writeaddress==byteaddress:
				data_w=data_list[i]
				flag=1
			i+=1
		if flag==0:
			data_w=0x0
		writeregandwait(data,data_w) #data 0
		writeregandwait(cmd_stat,0x10)
		board.dispatch()
		sleep(sleeptime)
		print str(writeaddress)+": "+hex(data_w)

	writereg(cmd_stat,0x40) #stop
	sleep(sleeptime)
	sleep(sleeptime)

	#writereg(cmd_stat,0x40) #stop
	addr_list_read=[]
	data_list_read=[]
	for byteaddress in range(0,143):
		if byteaddress%2==0:
			writeregandwait(cmd_stat,0x90) #write
			writeregandwait(data,0xD0) #slave address
			board.dispatch()
			sleep(sleeptime)

			writeregandwait(data,byteaddress) #byte address
			writeregandwait(cmd_stat,0x10)
			board.dispatch()
			sleep(sleeptime)

			writeregandwait(cmd_stat,0x90) #write
			writeregandwait(data,0xD1) #slave address
			board.dispatch()
			sleep(sleeptime)

			writereg(cmd_stat,0x20) #read
			sleep(sleeptime)
			readdata=readreg(data)
#			print "Register "+str(byteaddress)+": "+hex(readdata)
			addr_list_read.append(byteaddress)
			data_list_read.append(readdata)
			writereg(cmd_stat,0x20) #read
			sleep(sleeptime)
			readdata=readreg(data)
#			print "Register "+str(byteaddress+1)+": "+hex(readdata)
			addr_list_read.append(byteaddress+1)
			data_list_read.append(readdata)
			writereg(cmd_stat,0x40) #stop
	i=0
	for byteaddress in addr_list:
		j=0
		for byteaddress_read in addr_list_read:
			if byteaddress==byteaddress_read:
				if data_list[i]==data_list_read[j]:
					print "Register "+str(byteaddress)+" match: " + hex(data_list[i])
				else:
					print "Register "+str(byteaddress)+" mismatch "+ hex(data_list[i]) + " vs. " + hex(data_list_read[j])
			j+=1
		i+=1
def main_freq():
	std_address()
	init_board(library,deviceaddress,xmlfile)
	cnt=init_node("freq_ctrl.freq.count")	
	print "Frequency: "+str(int(readreg(cnt))/8388.608)+" MHz"

def main_reset():
	std_address()
	init_board(library,deviceaddress,xmlfile)
	soft_rst=init_node("ctrl_reg.ctrl.soft_rst")	
	si5326_rst=init_node("ctrl_reg.ctrl.si5326_rst")	
	print "Soft reset"
	writereg(soft_rst,0x1)
	print "Resetting SI5326"
	writereg(si5326_rst,0x1)
	writereg(si5326_rst,0x0)

if __name__ == "__main__":
	main_reset()
	main_clockconfig()
	main_freq()
