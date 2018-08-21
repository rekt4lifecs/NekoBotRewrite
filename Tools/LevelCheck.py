import rethinkdb as r
import math
import numpy as np
import time

r_conn = r.connect(db="nekobot")

def get_single():
    userid = str(input("Userid: "))
    data = r.table("levelSystem").get(userid).run(r_conn, array_limit=500000)

    if not data:
        print("User not found")
        exit(0)

    print("Blacklisted? %s" % data["blacklisted"])
    print("Last XP %s" % data["lastxp"])
    print("Amount of xp times %s" % len(data["lastxptimes"]))
    print("XP %s" % data["xp"])
    print("Level %s" % (int((1 / 278) * (9 + math.sqrt(81 + 1112 * (data["xp"]))))))

    lasttime = data["lastxptimes"][0]
    i = []
    for times in data["lastxptimes"]:

        x = (int(times) - int(lasttime))
        i.append(x)
        print("Seconds Since: %s" % x)

        lasttime = times

    print("Seconds since last: %s" % (int(time.time()) - int(lasttime)))
    print("Average: %s" % np.mean(i))

def get_top():
    top_amount = int(input("Top: "))
    top_seconds = int(input("Seconds: "))
    top = r.table("levelSystem").order_by(r.desc("xp")).limit(top_amount).run(r_conn, array_limit=500000)
    print("Retrieved Data")

    users = []

    for user in top:
        lasttime = user["lastxptimes"][0]
        i = []
        for times in user["lastxptimes"]:
            x = (int(times) - int(lasttime))
            i.append(x)
            lasttime = times

        average = int(float(np.mean(i)))

        if average < top_seconds:
            users.append(f"ID: {user['id']} Average: {average} Amount: {len(i)}")

    print("\n".join(users))

if __name__ == "__main__":
    # get_single()
    get_top()
    r_conn.close()
