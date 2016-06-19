from twisted.internet import protocol,reactor
from twisted.protocols import basic

class FingerProtocol(basic.LineReceiver):
    def lineReceived(self,user):
        self.transport.write(self.factory.getUser(user+"\r\n"))
        self.transport.loseConnection()

class FingerFactory(protocol.ServerFactory):
    protocol = FingerProtocol
    
    def __init__(self,**kwargs):
        self.users = kwargs
    def getUser(self,user):
       return "No such user\r\n"



reactor.listenTCP(1078,FingerFactory(moshez="Hapy and Well"))
print "Listen TCP on port 1079"
reactor.run( )

