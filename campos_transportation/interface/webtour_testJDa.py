print "Start."

import datetime
import webtourinterface

current_time = datetime.datetime.now().time()
print current_time.isoformat()

request="UserIDno="+"22727"
request=request+"&GroupIDno="+"387"
request=request+"&StartDestinationIDno="+"4389"
request=request+"&StartDateTime="+"2016-12-20"
request=request+"&StartNote="+"aa"
request=request+"&EndDestinationIDno="+"4391"
request=request+"&EndDateTime="+"2016-12-27"
request=request+"&EndNote="+"bb"

response_doc=webtourinterface.usneed_GetPending_ByIDno('https://services.techhouse.dk/webTourManager/1.5/SL2017.svc/rest/xml/','Login?OwnerIDno=107&Alias=testonly&AuthKey=F3ACDD1A-046D-42D7-A3B8-8A20488AA016','221051')

usContent = response_doc.getElementsByTagName("Content")  

element = usContent[0]

for element in usContent:
    print element.nodeName
    for n in element.childNodes:
        if n.firstChild != None:
            print n.nodeName.replace('a:','') , n.firstChild.nodeValue
        else:
            print n.nodeName.replace('a:','')
    
needidno = response_doc.getElementsByTagName("a:IDno")[0].firstChild.data

current_time = datetime.datetime.now().time()
print current_time.isoformat()

print "Done"


  
