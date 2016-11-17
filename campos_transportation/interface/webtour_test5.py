print "Start."

import datetime
import webtourinterface

response_doc=webtourinterface.usdestinations_getall()

destinations = response_doc.getElementsByTagName("a:usDestination")

for usDestination in destinations:
    destinationidno = usDestination.getElementsByTagName("a:IDno")[0].firstChild.data

print "Done"