from discord.ext import commands
import discord, random, aiohttp, config, requests, json, os, pymysql
from bs4 import BeautifulSoup as bs
from collections import Counter

class NSFW:
    """NSFW Commands OwO"""

    def __init__(self, bot):
        self.bot = bot
        self.counter = Counter()

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(200, 20, commands.BucketType.user)
    async def pgif(self, ctx):
        """Posts a Random PrOn GIF"""
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        amount = db.execute(f'SELECT 1 FROM dbl WHERE user = {ctx.message.author.id} AND type = \"upvote\"')
        if amount != 0:
            if not ctx.message.channel.is_nsfw():
                await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
                return
            self.counter['pgif'] += 1
            data = ["517.gif", "132.gif", "gif841.gif", "274.gif", "361.gif", "397.gif", "443.gif", "109.gif",
                    "523.gif", "395.gif", "46.gif", "557.gif", "276.gif", "388.gif", "gif863.gif", "220.gif",
                    "422.gif", "56.gif", "gif878.gif", "339.gif", "gif826.gif", "106.gif", "368.gif", "250.gif",
                    "352.gif", "525.gif", "gif844.gif", "363.gif", "gif917.gif", "gif935.gif", "67.gif", "120.gif",
                    "gif907.gif", "69.gif", "87.gif", "179.gif", "gif866.gif", "338.gif", "393.gif", "437.gif",
                    "486.gif", "479.gif", "293.gif", "278.gif", "149.gif", "gif899.gif", "99.gif", "543.gif",
                    "61.gif", "477.gif", "282.gif", "317.gif", "221.gif", "gif814.gif", "413.gif", "156.gif",
                    "257.gif", "545.gif", "gif875.gif", "468.gif", "452.gif", "360.gif", "552.gif", "267.gif",
                    "183.gif", "gif883.gif", "gif905.gif", "358.gif", "gif816.gif", "428.gif", "571.gif", "548.gif",
                    "461.gif", "243.gif", "565.gif", "560.gif", "137.gif", "gif851.gif", "507.gif", "429.gif",
                    "511.gif", "147.gif", "578.gif", "21.gif", "421.gif", "229.gif", "224.gif", "174.gif",
                    "453.gif", "506.gif", "544.gif", "247.gif", "41.gif", "348.gif", "182.gif", "121.gif",
                    "373.gif", "113.gif", "68.gif", "150.gif", "153.gif", "gif898.gif", "173.gif", "331.gif",
                    "152.gif", "516.gif", "gif911.gif", "365.gif", "13.gif", "gif889.gif", "286.gif", "52.gif",
                    "472.gif", "gif852.gif", "519.gif", "431.gif", "43.gif", "210.gif", "51.gif", "546.gif",
                    "465.gif", "gif849.gif", "386.gif", "172.gif", "259.gif", "gif904.gif", "gif817.gif", "442.gif",
                    "440.gif", "158.gif", "98.gif", "569.gif", "gif842.gif", "481.gif", "185.gif", "142.gif",
                    "57.gif", "209.gif", "334.gif", "187.gif", "102.gif", "372.gif", "91.gif", "263.gif", "382.gif",
                    "gif873.gif", "497.gif", "418.gif", "547.gif", "356.gif", "25.gif", "49.gif", "gif958.gif",
                    "gif834.gif", "165.gif", "258.gif", "215.gif", "241.gif", "575.gif", "gif821.gif", "2.gif",
                    "489.gif", "84.gif", "gif896.gif", "gif882.gif", "97.gif", "89.gif", "469.gif", "405.gif",
                    "399.gif", "464.gif", "gif868.gif", "340.gif", "310.gif", "gif855.gif", "33.gif", "169.gif",
                    "gif854.gif", "gif870.gif", "378.gif", "125.gif", "138.gif", "463.gif", "34.gif", "359.gif",
                    "269.gif", "79.gif", "54.gif", "gif846.gif", "262.gif", "491.gif", "412.gif", "347.gif",
                    "279.gif", "427.gif", "226.gif", "gif970.gif", "301.gif", "gif829.gif", "11.gif", "80.gif",
                    "213.gif", "336.gif", "223.gif", "484.gif", "159.gif", "311.gif", "342.gif", "341.gif",
                    "292.gif", "559.gif", "gif962.gif", "85.gif", "86.gif", "416.gif", "37.gif", "404.gif",
                    "283.gif", "411.gif", "48.gif", "60.gif", "270.gif", "47.gif", "94.gif", "549.gif", "144.gif",
                    "255.gif", "gif884.gif", "242.gif", "214.gif", "501.gif", "161.gif", "504.gif", "460.gif",
                    "553.gif", "454.gif", "123.gif", "369.gif", "316.gif", "160.gif", "6.gif", "gif900.gif",
                    "55.gif", "392.gif", "502.gif", "424.gif", "542.gif", "122.gif", "78.gif", "492.gif", "450.gif",
                    "35.gif", "531.gif", "203.gif", "gif950.gif", "534.gif", "458.gif", "532.gif", "gif952.gif",
                    "gif957.gif", "gif822.gif", "157.gif", "535.gif", "281.gif", "gif890.gif", "370.gif",
                    "gif954.gif", "219.gif", "gif941.gif", "217.gif", "409.gif", "208.gif", "550.gif", "576.gif",
                    "1.gif", "568.gif", "195.gif", "355.gif", "261.gif", "375.gif", "332.gif", "538.gif", "470.gif",
                    "gif903.gif", "573.gif", "175.gif", "364.gif", "gif913.gif", "503.gif", "gif837.gif",
                    "gif825.gif", "gif815.gif", "gif887.gif", "63.gif", "206.gif", "530.gif", "480.gif", "299.gif",
                    "gif934.gif", "318.gif", "58.gif", "gif856.gif", "gif874.gif", "280.gif", "420.gif",
                    "gif832.gif", "111.gif", "gif845.gif", "249.gif", "410.gif", "256.gif", "435.gif", "126.gif",
                    "536.gif", "350.gif", "gif862.gif", "494.gif", "574.gif", "313.gif", "gif901.gif", "gif836.gif",
                    "gif839.gif", "456.gif", "7.gif", "194.gif", "gif859.gif", "509.gif", "268.gif", "554.gif",
                    "gif902.gif", "gif843.gif", "39.gif", "475.gif", "62.gif", "116.gif", "gif867.gif",
                    "gif936.gif", "540.gif", "228.gif", "529.gif", "380.gif", "73.gif", "gif912.gif", "167.gif",
                    "192.gif", "551.gif", "252.gif", "gif943.gif", "357.gif", "134.gif", "82.gif", "117.gif",
                    "512.gif", "gif886.gif", "314.gif", "446.gif", "499.gif", "449.gif", "271.gif", "211.gif",
                    "384.gif", "110.gif", "248.gif", "66.gif", "gif940.gif", "196.gif", "493.gif", "3.gif",
                    "201.gif", "139.gif", "298.gif", "520.gif", "391.gif", "264.gif", "527.gif", "gif929.gif",
                    "96.gif", "gif964.gif", "561.gif", "408.gif", "gif888.gif", "306.gif", "305.gif", "563.gif",
                    "gif944.gif", "gif926.gif", "471.gif", "315.gif", "383.gif", "335.gif", "129.gif", "23.gif",
                    "200.gif", "112.gif", "343.gif", "12.gif", "451.gif", "76.gif", "75.gif", "gif906.gif",
                    "407.gif", "385.gif", "gif838.gif", "gif848.gif", "406.gif", "572.gif", "166.gif", "425.gif",
                    "265.gif", "104.gif", "524.gif", "260.gif", "539.gif", "426.gif", "307.gif", "275.gif",
                    "127.gif", "gif835.gif", "gif830.gif", "119.gif", "gif865.gif", "177.gif", "9.gif", "304.gif",
                    "70.gif", "gif833.gif", "266.gif", "387.gif", "26.gif", "330.gif", "495.gif", "136.gif",
                    "gif872.gif", "367.gif", "556.gif", "162.gif", "gif938.gif", "44.gif", "403.gif", "430.gif",
                    "483.gif", "135.gif", "gif857.gif", "498.gif", "300.gif", "273.gif", "346.gif", "gif1001.gif",
                    "gif853.gif", "353.gif", "29.gif", "gif864.gif", "81.gif", "171.gif", "18.gif", "371.gif",
                    "gif881.gif", "59.gif", "419.gif", "376.gif", "287.gif", "244.gif", "178.gif", "337.gif",
                    "537.gif", "50.gif", "297.gif", "216.gif", "246.gif", "447.gif", "344.gif", "377.gif",
                    "gif947.gif", "101.gif", "191.gif", "gif978.gif", "396.gif", "294.gif", "31.gif", "gif956.gif",
                    "580.gif", "222.gif", "288.gif", "gif948.gif", "438.gif", "133.gif", "204.gif", "414.gif",
                    "218.gif", "522.gif", "457.gif", "564.gif", "88.gif", "22.gif", "533.gif", "24.gif", "398.gif",
                    "366.gif", "205.gif", "141.gif", "93.gif", "514.gif", "402.gif", "28.gif", "83.gif", "72.gif",
                    "146.gif", "308.gif", "gif955.gif", "148.gif", "gif879.gif", "gif916.gif", "284.gif", "245.gif",
                    "415.gif", "gif942.gif", "541.gif", "254.gif", "30.gif", "309.gif", "401.gif", "441.gif",
                    "579.gif", "151.gif", "184.gif", "528.gif", "gif908.gif", "319.gif", "77.gif", "176.gif",
                    "444.gif", "508.gif", "105.gif", "gif831.gif", "555.gif", "199.gif", "433.gif", "473.gif",
                    "100.gif", "354.gif", "202.gif", "193.gif", "240.gif", "65.gif", "188.gif", "467.gif",
                    "gif915.gif", "190.gif", "gif850.gif", "19.gif", "45.gif", "gif959.gif", "36.gif", "485.gif",
                    "181.gif", "374.gif", "gif982.gif", "64.gif", "291.gif", "163.gif", "10.gif", "513.gif",
                    "349.gif", "140.gif", "303.gif", "436.gif", "103.gif", "32.gif", "362.gif", "487.gif",
                    "118.gif", "4.gif", "351.gif", "gif974.gif", "170.gif", "434.gif", "251.gif", "108.gif",
                    "515.gif", "289.gif", "107.gif", "459.gif", "381.gif", "53.gif", "432.gif", "74.gif", "128.gif",
                    "227.gif", "394.gif", "gif880.gif", "42.gif", "518.gif", "207.gif", "566.gif", "0.gif",
                    "478.gif", "143.gif", "417.gif", "272.gif", "466.gif", "gif824.gif", "gif847.gif", "488.gif",
                    "333.gif", "gif861.gif", "8.gif", "490.gif", "500.gif", "567.gif", "145.gif", "302.gif",
                    "16.gif", "114.gif", "577.gif", "17.gif", "130.gif", "277.gif", "168.gif", "124.gif", "92.gif",
                    "390.gif", "295.gif", "345.gif", "189.gif", "570.gif", "gif869.gif", "439.gif", "gif960.gif",
                    "455.gif", "186.gif", "505.gif", "225.gif", "gif885.gif", "38.gif", "gif939.gif", "27.gif",
                    "558.gif", "510.gif", "164.gif", "389.gif", "5.gif", "526.gif", "gif928.gif", "gif914.gif",
                    "423.gif", "197.gif", "462.gif", "71.gif", "312.gif", "gif924.gif", "285.gif", "474.gif",
                    "445.gif", "379.gif", "482.gif", "gif876.gif", "400.gif", "198.gif", "448.gif", "253.gif",
                    "212.gif", "90.gif", "gif877.gif", "14.gif", "40.gif", "gif871.gif", "gif937.gif", "496.gif",
                    "131.gif", "155.gif", "gif953.gif", "115.gif", "296.gif", "gif840.gif", "15.gif", "180.gif",
                    "gif860.gif", "95.gif", "154.gif", "gif976.gif", "290.gif", "476.gif", "521.gif", "562.gif"]
            x = "http://37.59.36.62/pgif/" + random.choice(data)
            em = discord.Embed(color=0xDEADBF)
            em.set_image(url=x)

            await ctx.send(embed=em)
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  title="WOAH",
                                  description="Have you voted yet <:smirkGuns:417969421252952085>\n"
                                              "https://discordbots.org/bot/310039170792030211/vote")
            if not ctx.message.channel.is_nsfw():
                embed.set_footer(text="Use in a NSFW Channel BTW...")
            await ctx.send(embed=embed)

    @commands.command(name="4k")
    @commands.guild_only()
    async def _fourk(self, ctx):
        """Posts a random 4K Image OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter["4k"] += 1
        async with aiohttp.ClientSession() as cs:
            async with cs.get("http://37.59.36.62:10000/4kdata") as r:
                res = await r.json()
                fourkdata = res['msg']
        data = random.choice(fourkdata)
        embed = discord.Embed(color=0xDEADBF)
        url = "http://37.59.36.62/4k/" + data
        embed.set_image(url=url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def phsearch(self, ctx, terms: str):
        """Search from PronHub"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        try:
            self.counter["phsearch"] += 1
            searchurl = "https://www.pornhub.com/video/search?search={}".format(terms.replace(" ", "+"))
            url = requests.get(searchurl).text
            soup = bs(url)
            phtitle = soup.find("a", {"class": "img"})['title']
            phurl = soup.find("a", {"class": "img"})['href']
            href = "https://www.pornhub.com{}".format(phurl)
            em = discord.Embed(title=phtitle,
                               color=0xDEADBF,
                               description=href)
            await ctx.send(embed=em)
        except Exception as e:
            await ctx.send(embed=discord.Embed(title="Error",
                                               color=0xDEADBF,
                                               description="**`{}`**".format(e)))

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(200, 10, commands.BucketType.user)
    async def lewdneko(self, ctx):
        """Posts a Lewd Neko OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter["lewdneko"] += 1
        async with aiohttp.ClientSession() as cs:
            x = random.choice(['https://nekos.life/api/v2/img/nsfw_neko_gif', 'http://nekos.life/api/lewd/neko'])
            async with cs.get(x) as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                try:
                    urla = res['neko']
                except:
                    urla = res['url']
                em.set_image(url=urla)
                em.set_footer(text="nekos.life owo")
                await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def yandere(self, ctx, *tags: str):
        """Search Yande.re OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        if tags == ():
            await ctx.send(":warning: Tags are missing.")
        else:
            try:
                self.counter["yandere"] += 1
                tags = ("+").join(tags)
                query = ("https://yande.re/post.json?limit=42&tags=" + tags)
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(query) as r:
                        res = await r.json()
                if res != []:
                    em = discord.Embed(color=0xDEADBF)
                    em.set_image(url=random.choice(res)['jpeg_url'])
                    await ctx.send(embed=em)
                else:
                    e = discord.Embed(color=0xDEADBF, title="⚠ Error",
                                      description="Yande.re has no images for requested tags.")
                    await ctx.send(embed=e)
            except Exception as e:
                await ctx.send(":x: `{}`".format(e))

    @commands.command()
    @commands.guild_only()
    async def boobs(self, ctx):
        """Get Random Boobs OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        try:
            self.counter["boobs"] += 1
            rdm = random.randint(0, 11545)
            search = ("http://api.oboobs.ru/boobs/{}".format(rdm))
            async with aiohttp.ClientSession() as cs:
                async with cs.get(search) as r:
                    res = await r.json()
                    boob = random.choice(res)
                    boob = "http://media.oboobs.ru/{}".format(boob["preview"])
                    em = discord.Embed(color=0xDEADBF)
                    em.set_image(url=boob)
                    await ctx.send(embed=em)
        except Exception as e:
            await ctx.send("**`{}`**".format(e))

    @commands.command()
    @commands.guild_only()
    async def girl(self, ctx):
        """Get a girl OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['girl'] += 1
        data = config.imgur._get_imgur(self, "bodyperfection", page=random.randint(1, 5))['data']
        x = random.choice(data)
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def bigboobs(self, ctx):
        """Big Boobs"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['bigboobs'] += 1
        sub = random.choice(["bigboobs", "BigBoobsGW"])
        data = config.imgur._get_imgur(self, sub, page=random.randint(1, 5))['data']
        x = random.choice(data)
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def ass(self, ctx):
        """Get Random Ass OwO"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['ass'] += 1
        data = config.imgur._get_imgur(self, "asstastic", page=random.randint(1, 6))['data']
        x = random.choice(data)
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em)

    @commands.command(aliases=["cum"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cumsluts(self, ctx):
        """CumSluts"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['cum'] += 1
        data = config.imgur._get_imgur(self, "cumsluts")['data']
        x = random.choice(data)
        embed = discord.Embed(color=0xDEADBF,
                              title=f"**{x['title']}**")
        embed.set_image(url=x['link'])

        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def thighs(self, ctx):
        """Thighs"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        sub = random.choice(["thighhighs", "stockings"])
        self.counter['thighs'] += 1
        data = config.imgur._get_imgur(self, sub, page=random.randint(1, 5))['data']
        x = random.choice(data)
        em = discord.Embed(title=f"**{x['title']}**",
                           color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def gonewild(self, ctx):
        """r/GoneWild"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['gonewild'] += 1
        data = config.imgur._get_imgur(self, "gonewild", page=random.randint(1, 5))['data']
        x = random.choice(data)
        em = discord.Embed(title=f"**{x['title']}**", color=0xDEADBF)
        em.set_image(url=x['link'])

        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def doujin(self, ctx):
        """Get a Random Doujin"""
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        else:
            url = "http://nhentai.net/random/"
            await ctx.send(embed=discord.Embed(color=0xDEADBF, description=f"{url}"))

    @commands.command()
    @commands.guild_only()
    async def hentai(self, ctx):
        connection = pymysql.connect(host="localhost",
                                     user="root",
                                     password="rektdiscord",
                                     db="nekobot",
                                     port=3306)
        db = connection.cursor()
        if not ctx.message.channel.is_nsfw():
            await ctx.send("This is not a NSFW Channel <:deadStare:417437129501835279>")
            return
        self.counter['hentai'] += 1
        amount = db.execute(f'SELECT 1 FROM dbl WHERE user = {ctx.message.author.id} AND type = \"upvote\"')
        if amount != 0:
            x = random.choice(['bj', 'cum', 'Random_hentai_gif', 'boobs', 'pussy', 'anal'])
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://nekos.life/api/v2/img/{x}") as r:
                    res = await r.json()
                    em = discord.Embed(color=0xDEADBF)
                    em.set_image(url=res['url'])
                    await ctx.send(embed=em)
        else:
            embed = discord.Embed(color=0xDEADBF,
                                  title="oof",
                                  description="Have you voted yet <:smirkGuns:417969421252952085>\n"
                                              "https://discordbots.org/bot/310039170792030211/vote\n"
                                              "ppl broke the bot with this so vote 🤷")
            await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def nsfw(self, ctx):
        """NSFW Stats"""
        embed = discord.Embed(color=0xDEADBF,
                              title="NSFW Stats")
        embed.add_field(name="PGIF", value=self.counter['pgif'])
        embed.add_field(name="4k", value=self.counter['4k'])
        embed.add_field(name="Lewd Neko", value=self.counter['lewdneko'])
        embed.add_field(name="Yande.re", value=self.counter['yandere'])
        embed.add_field(name="Ass", value=self.counter['ass'])
        embed.add_field(name="Boobs", value=self.counter['boobs'])
        embed.add_field(name="Cumsluts", value=self.counter['cum'])
        embed.add_field(name="Thighs", value=self.counter['thighs'])
        embed.add_field(name="GoneWild", value=self.counter['gonewild'])
        embed.add_field(name="Girl", value=self.counter['girl'])
        embed.add_field(name="Big Boobs", value=self.counter['bigboobs'])
        embed.add_field(name="Hentai", value=self.counter['hentai'])

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(NSFW(bot))
