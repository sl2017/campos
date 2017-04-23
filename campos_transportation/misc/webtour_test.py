print "Start.";

import zeep

wwsdl = 'http://www.soapclient.com/xml/soapresponder.wsdl'
client = zeep.Client(wsdl=wwsdl)
print(client.service.Method1('Zeep', 'is cool'))

print "Done.";
