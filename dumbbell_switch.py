from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class DumbellTopo(Topo):
    "A linux router connecting a sender"

    def build(self, **_opts):
        IP1 = '192.168.1.1/24'  # Ip Address for r0-eth1

        IP2 = '192.1.56.1/56'  # IP address for r1-eth1

        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        s4 = self.addSwitch('s4')

        self.addLink(s1, s2)
        self.addLink(s1, s3 )
        self.addLink(s2, s4 )

        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        h4 = self.addHost('h4')

        self.addLink(h1, s3)
        self.addLink(h2, s3)
        self.addLink(h3, s4)
        self.addLink(h4, s4)


def run():
    "Test"
    topo = DumbellTopo()
    net = Mininet(topo=topo)
    net.start()
    net.pingAll()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()

