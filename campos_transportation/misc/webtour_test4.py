print "Start."

import datetime
from ..interface import webtourinterface

current_time = datetime.datetime.now().time()
print current_time.isoformat()

response_doc=webtourinterface.usgroup_getall()
usgroups = response_doc.getElementsByTagName("a:IDno")

current_time = datetime.datetime.now().time()
print current_time.isoformat()

print "Done"