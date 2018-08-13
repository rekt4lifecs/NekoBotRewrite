import rethinkdb as r
import numpy as np
import time

r_conn = r.connect(db="nekobot")

user = input("User: ")
data = r.table("economy").get(str(user)).run(r_conn)

lasttime = data["bettimes"][0]
i = []
for times in data["bettimes"]:
    x = (int(times) - int(lasttime))
    i.append(x)
    print("Seconds Since: %s" % x)
    lasttime = times

print("Seconds since last: %s" % (int(time.time()) - int(lasttime)))
print("Amount: %s" % len(data["bettimes"]))
print("Average: %s" % np.mean(i))

r_conn.close()
