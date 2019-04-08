[200~#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.util import quietRun
import subprocess
import time
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from os import path




class DumbellTopo(Topo):
    #"Creating a dumbell topology for mininet"

    def build(self,delay):



        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        self.addLink(s1, s2 ,cls=TCLink, bw=984, delay='{0}ms'.format(delay), max_queue_size=82*delay, use_htb=True )
        self.addLink(s1, s3, cls=TCLink, bw=252, delay='0ms', max_queue_size=21*delay*0.2,  use_htb=True )
        self.addLink(s2, s4, cls=TCLink, bw=252, delay='0ms', max_queue_size=21*delay*0.2, use_htb=True )

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        self.addLink(h1, s3 ,cls=TCLink, bw=960)
        self.addLink(h2, s3 ,cls=TCLink, bw=960)
        self.addLink(h3, s4 ,cls=TCLink, bw=960)
        self.addLink(h4, s4 ,cls=TCLink, bw=960)

def cleanProbe():
    print("Removing existing TCP_Probe")
    procs = quietRun('pgrep -f /proc/net/tcpprobe').split()
    for proc in procs:
        output= quietRun('sudo kill -KILL {0}'.format(proc.rstrip()))


def run(algorithm,delay):
    if(path.exists("{0}_tcpprobe_{1}.txt".format(algorithm,delay))):
        print "removing existing file"
        os.remove("{0}_tcpprobe_{1}.txt".format(algorithm,delay))
    cleanProbe()
    print("Starting TCP_PROBE........")
    output = quietRun('sudo rmmod tcp_probe')
    output = quietRun('sudo modprobe tcp_probe')
    print("Storing the TCP_Probe results")
    subprocess.Popen('sudo cat /proc/net/tcpprobe > {0}_tcpprobe_{1}.txt'.format(algorithm,delay), shell=True)

    topo = DumbellTopo(delay)
    net = Mininet(topo=topo)
    net.start()
    h1, h2, h3, h4 = net.getNodeByName('h1', 'h2', 'h3','h4')
    global h3_ip,h4_ip
    h3_ip=h3.IP()
    h4_ip=h4.IP()
    if(path.exists("{0}-{1}-{2}".format(algorithm,h1,delay))):
        print "removing existing file"
        os.remove("{0}-{1}-{2}".format(algorithm,h1,delay))

    if(path.exists("{0}-{1}-{2}".format(algorithm,h2,delay))):
        print "removing existing file"
        os.remove("{0}-{1}-{2}".format(algorithm,h2,delay))
    popens = dict()
    print("Starting the server on the host h1 and h2")
    popens[h3]= h3.popen(['iperf','-s','-p','5001'])
    popens[h4]=h4.popen(['iperf','-s','-p','5001'])
    time.sleep(5)
    print("Client started on the host h1 ")
    popens[h1]=h1.popen('iperf -c {0} -p 5001 -i 1 -w 16m -Z {1} -t 1000>{2}-{3}-{4}'.format(h3_ip,algorithm,algorithm,h1,delay), shell=True)
    print("250 seconds wait to start client on host2")
    time.sleep(250)
    print("Client started on host h2")
    popens[h2] = h2.popen('iperf -c {0} -p 5001 -i 1 -w 16m -Z {1} -t 750>{2}-{3}-{4}'.format(h4_ip,algorithm,algorithm, h2, delay),
                          shell=True)
    popens[h1].wait()
    popens[h2].wait()
    print("done")

def tcpprobe_extract(algorithn,delay):
    if (path.exists("{0}_tcpprobe_h1_{1}.txt".format(algorithn,delay))):
        print "Removing old TCPProbe file for host 1"
        os.remove("{0}_tcpprobe_h1_{1}.txt".format(algorithn,delay))
    if (path.exists("{0}_tcpprobe_h2_{1}.txt".format(algorithn,delay))):
        print"Removing old TCPProbe file for host 2"
        os.remove("{0}_tcpprobe_h2_{1}.txt".format(algorithm,delay))
    #os.remove("tcpprobewirte_h2.txt")
    f1 = open("{0}_tcpprobe_h1_{1}.txt".format(algorithn,delay), "a")
    f2 = open("{0}_tcpprobe_h2_{1}.txt".format(algorithn,delay), "a")
    f=open("{0}_tcpprobe_{1}.txt".format(algorithn,delay),"r")
    print "Reading from file {0}_tcpprobe_{1}.txt to plot the tcpprobe graph".format(algorithn,delay)


    if f.mode=='r':

        for contents in f:

            contents=contents.split(" ")

            if contents[0] != '' and contents[6] !='' and contents[1].startswith('10.0.0.1'):
                data= contents[0]+" "+contents[6]+'\n'
                #print data
                f1.writelines(data)
            if contents[0] != '' and contents[6] != '' and contents[1].startswith('10.0.0.2'):
                data = contents[0] + " " + contents[6]+'\n'
                #print data
                f2.writelines(data)

    f.close()
    f2.close()
    f1.close()



def iperf_extract(algorithm,delay):

    if (path.exists("{0}_h1_{0}_iperf.txt".format(algorithm,delay))):
        os.remove("{0}_h1_{0}_iperf.txt".format(algorithm,delay))
    if (path.exists("{0}_h2_{0}_iperf.txt".format(algorithm,delay))):
        os.remove("{0}_h2_{0}_iperf.txt".format(algorithm,delay))
    print("Creating the files for IPERF to plot the TCP fairness graph ")
    subprocess.Popen("cat {0}-h1-{1} | grep sec | tr - ' '| awk '{{print $4, $8}}'> {2}_h1_{3}_iperf.txt".format(algorithm,delay,algorithm,delay), shell=True)
    subprocess.Popen("cat {0}-h2-{1} | grep sec | tr - ' '| awk '{{print $4, $8}}'> {2}_h2_{3}_iperf.txt".format(algorithm,delay,algorithm,delay), shell=True)
    print("done")

def plot_iperf(algorithm,delay):
    p1=[]
    p2=[]
    p3=[]
    p4=[]
    time.sleep(2)
    f1=open("{0}_h1_{1}_iperf.txt".format(algorithm,delay),"r")
    f2=open("{0}_h2_{1}_iperf.txt".format(algorithm,delay),"r")
    for contents in f1:
        contents=contents.split(" ")
        p1.append(float(contents[0].rstrip()))
        p2.append(float(contents[1].rstrip()))
    f1.close()
    for contents in f2:
        contents=contents.split(" ")
        p3.append(float(contents[0].rstrip())+250)
        p4.append(float(contents[1].rstrip()))
    f2.close()



    fig, ax = plt.subplots()
    ax.plot(p1, p2,)
    ax.plot(p3, p4,)

    ax.set(xlabel='Time (s)', ylabel='Bandwidth',
           title="TCP {0} DELAY {1}ms".format(algorithm,delay))
    fig.savefig("{0}_iperf_{1}.png".format(algorithm,delay))
    plt.show()



def plot(algorithm,delay):
    p1=[]
    p2=[]
    p3=[]
    p4=[]
    f1=open("{0}_tcpprobe_h1_{1}.txt".format(algorithm,delay),"r")
    f2=open("{0}_tcpprobe_h2_{1}.txt".format(algorithm,delay),"r")
    for contents in f1:
        contents=contents.split(" ")
        p1.append(float(contents[0].rstrip()))
        p2.append(float(contents[1].rstrip()))
    f1.close()
    for contents in f2:
        contents=contents.split(" ")
        p3.append(float(contents[0].rstrip()))
        p4.append(float(contents[1].rstrip()))
    f2.close()
    #print p3.__sizeof__()



    fig, ax = plt.subplots()
    ax.plot(p1, p2, label="TCP IPERF Sender 1")
    ax.plot(p3, p4, label="TCP IPERF Sender 2")

    ax.set(xlabel='Time (s)', ylabel='Congestion Window',
           title="TCP {0} DELAY {1}ms".format(algorithm,delay))
    fig.savefig("{0}_tcpprobe_{1}.png".format(algorithm,delay))
    plt.show()


if __name__ == '__main__':
    delay=21
    algorithm='htcp'
    setLogLevel('info')
    run(algorithm,delay)
    print"Grap plot started..............."
    time.sleep(1)
    tcpprobe_extract(algorithm, delay)
    plot(algorithm, delay)
    iperf_extract(algorithm, delay)
    plot_iperf(algorithm, delay)

