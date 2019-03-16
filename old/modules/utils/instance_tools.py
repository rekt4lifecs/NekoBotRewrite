class InstanceTools:

    def __init__(self, instances, redis_conn):
        self.instances = instances
        self.redis_conn = redis_conn

    async def get_all_guilds(self):

        guilds = 0

        for x in range(self.instances):
            z = int((await self.redis_conn.get("instance%s-guilds" % x)).decode("utf8"))
            guilds += z

        return guilds

    async def get_all_users(self):

        users = 0

        for x in range(self.instances):
            z = int((await self.redis_conn.get("instance%s-users" % x)).decode("utf8"))
            users += z

        return users

    async def get_all_messages(self):

        msgs = 0

        for x in range(self.instances):
            z = int((await self.redis_conn.get("instance%s-messages" % x)).decode("utf8"))
            msgs += z

        return msgs

    async def get_all_commands(self):

        commands = 0

        for x in range(self.instances):
            z = int((await self.redis_conn.get("instance%s-commands" % x)).decode("utf8"))
            commands += z

        return commands

    async def get_all_channels(self):

        channels = 0

        for x in range(self.instances):
            z = int((await self.redis_conn.get("instance%s-channels" % x)).decode("utf8"))
            channels += z

        return channels
