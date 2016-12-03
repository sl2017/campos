print "Start."

import datetime
import webtourinterface

current_time = datetime.datetime.now().time()
print current_time.isoformat()

k=webtourinterface.ususer_getbygroupidnoList('333')


current_time = datetime.datetime.now().time()
print current_time.isoformat()

print "Done"