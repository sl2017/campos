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
response_doc=webtourinterface.usneed_create(request)

usContent = response_doc.getElementsByTagName("Content")  

needidno = response_doc.getElementsByTagName("a:IDno")[0].firstChild.data

current_time = datetime.datetime.now().time()
print current_time.isoformat()

print "Done"


  
