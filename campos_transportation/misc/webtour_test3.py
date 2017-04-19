print "Start."

import requests

from xml.dom import minidom

url="https://services.techhouse.dk/webTourManager/0.6/Service.svc/basHttps"
#headers = {'content-type': 'application/soap+xml'}
headers = {'content-type': 'text/xml', 'SOAPAction' : 'https://services.techhouse.dk/webTourManager/IPlanning/Login'}
body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="https://services.techhouse.dk/webTourManager">
   <soapenv:Header/>
   <soapenv:Body>
      <web:Login>
         <!--Optional:-->
         <web:OwnerIDno>107</web:OwnerIDno>
         <!--Optional:-->
         <web:Alias>testonly</web:Alias>
         <!--Optional:-->
         <web:AuthKey>4057640D-4C9B-424C-A88C-DC9EE42B1032</web:AuthKey>
      </web:Login>
   </soapenv:Body>
</soapenv:Envelope>"""

response = requests.post(url,data=body,headers=headers)
print (response.content)

c = response.cookies

headers2 = {'content-type': 'text/xml', 'SOAPAction' : 'https://services.techhouse.dk/webTourManager/ITour/Tour_GetFromStatusAndDateRange_WithSalesperson'}

body2 = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:web="https://services.techhouse.dk/webTourManager">
   <soapenv:Header/>
   <soapenv:Body>
      <web:Tour_GetFromStatusAndDateRange_WithSalesperson>
         <web:Status>10</web:Status>
         <web:From>2016-09-01</web:From>
         <web:To>2016-09-30</web:To>
         <web:SalespersonID>JDa</web:SalespersonID>
      </web:Tour_GetFromStatusAndDateRange_WithSalesperson>
   </soapenv:Body>
</soapenv:Envelope>"""

doc = minidom.parseString(response.content)

authenticated = doc.getElementsByTagName("b:IsAuthenticated")[0]

if authenticated.firstChild.data == "true":
 response2 = requests.post(url,data=body2,headers=headers2,cookies=c)
 print (response2.content)

 doc = minidom.parseString(response2.content)

 tours = doc.getElementsByTagName("b:TourIDnoItem")

 for TourIDnoItem in tours:
  tourid = TourIDnoItem.getElementsByTagName("b:TourIDno")[0]
  print(tourid.firstChild.data)

print "Done."
