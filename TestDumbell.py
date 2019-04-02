#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter( Node ):
    "A Node with IP forwarding enabled."

    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        # Enable forwarding on the router
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()


class NetworkTopo( Topo ):
    "A LinuxRouter connecting three IP subnets"

    def build( self, **_opts ):
        IP= '10.0.1.1/24'
        defaultIP = '10.0.1.2/24'  # IP address for r0-eth1
        router = self.addNode( 'r1', cls=LinuxRouter, ip=defaultIP )
        route = self.addNode('r2', cls=LinuxRouter, ip=IP )


        h1 = self.addHost( 'h1', ip='10.0.2.2/24', defaultRoute='via 10.0.2.1' )
        h2 = self.addHost( 'h2', ip='10.0.2.3/24', defaultRoute='via 10.0.2.1' )
        h3 = self.addHost('h3', ip='10.0.3.2/24', defaultRoute='via 10.0.3.1')
        h4 = self.addHost('h4', ip='10.0.3.3/24', defaultRoute='via 10.0.3.1')

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        self.addLink(route, router)
        self.addLink( s1, router, intfName2='r1-eth1', params2={ 'ip' : '10.0.2.1/24' } )
        self.addLink(s2, route, intfName2='r2-eth1', params2={'ip': '10.0.3.1/24'})


        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s2)
        self.addLink(h4, s2)

def run():
    "Test linux router"
    topo = NetworkTopo()
    net = Mininet( topo=topo )  # controller is used by s1-s3
    net.start()
    net.pingAll()
    CLI( net )
    net.stop()
#*** Ping: testing ping reachability
#h1 -> h2 X X r1 X
#h2 -> h1 X X r1 X
#h3 -> X X h4 X r2
#h4 -> X X h3 X r2
#r1 -> h1 h2 X X r2
#r2 -> X X h3 h4 r1
#*** Results: 53% dropped (14/30 received)

