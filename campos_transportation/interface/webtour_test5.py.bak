print "Start."

import datetime
import webtourinterface

troop_id = "def"
groupidno=webtourinterface.usgroup_getbyname(troop_id)
if groupidno == 0:
    groupidno=webtourinterface.usgroup_create(troop_id)

groupid=webtourinterface.usgroup_getbyname("def")

current_time = datetime.datetime.now().time()
print current_time.isoformat()

tours = webtourinterface.gettours()

current_time = datetime.datetime.now().time()
print current_time.isoformat()

tours.sort()

print tours

current_time = datetime.datetime.now().time()
print current_time.isoformat()

for tourid in tours:
    print webtourinterface.gettour(tourid)

current_time = datetime.datetime.now().time()
print current_time.isoformat()

print "Done"