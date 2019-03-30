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

class DumbellTopo( Topo ):
   "A linux router connecting a sender"


   def build ( self, **_opts ):

      IP1 = '192.168.1.1/24'   # Ip Address for r0-eth1

      IP2 = '192.168.2.1/24'   # IP address for r1-eth1

      r1 = self.addNode( 'r1', cls=LinuxRouter, ip=IP1 )
      r2 = self.addNode( 'r2', cls=LinuxRouter, ip=IP2 )

      self.addLink( r1, r2 )
      #self.addLink(r1, r2, intfName1='r1-eth1', intfName2='r2-eth1')

      s1,s2 = [ self.addSwitch ( s ) for s in ('s1', 's2') ]

      self.addLink( s1, r1, intfName2='r1-eth1', params2={ 'ip' : IP1} )

      self.addLink( s2, r2, intfName2='r2-eth1', params2={ 'ip' : IP2} )


      h1 = self.addHost( 'h1', ip='192.168.1.100/24', defaultRoute='via 192.168.1.1' )
      h2 = self.addHost( 'h2', ip='192.168.1.101/24', defaultRoute='via 192.168.1.1' )
      h3 = self.addHost( 'h3', ip='192.168.2.100/24', defaultRoute='via 192.168.2.1' )
      h4 = self.addHost( 'h4', ip='192.168.2.101/24', defaultRoute='via 192.168.2.1' )

      self.addLink(h1, s1)
      self.addLink(h2, s1)
      self.addLink(h3, s2)
      self.addLink(h4, s2)


def run():
   "Test"
   topo=DumbellTopo()
   net = Mininet ( topo=topo )
   net.start()
   info( '*** Routing Table on Router:\n' )
   info( net[ 'r1' ].cmd( 'route' ) )
   info( net[ 'r2' ].cmd( 'route ') )
   CLI( net )
   net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()

