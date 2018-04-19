from discord.ext import commands
import discord, aiohttp, random, config, datetime, asyncio, base64, hashlib, textwrap, uuid
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageOps
import os, time
import aiomysql
import json
from googleapiclient import discovery

key = config.weeb
auth = {"Authorization": "Wolke " + key}

food = [
    "🍪",
    "🍣",
    "🍟",
    "🍕",
    "🍚",
    "🍇",
    "🍓",
    "🍔",
    "🍰",
    "🍄",
    "🍡",
    "🍛",
    "🌵",
    "🍜",
    "🌽",
    "🍶",
    "🍆",
    "🍌",
    "🍬",
    "🍋",
    "🍹",
    "🍝",
    "🍮",
    "🎂",
    "🍏",
    "🍈",
    "🍠",
    "☕",
    "🍺",
    "🍷",
    "🍥",
    "🥚",
    "🍨",
    "🍭",
    "🍊",
    "🍉",
    "🍞",
    "🍍",
    "🍘",
    "🍧"
]

class Fun:
    """Fun Commands"""

    def __init__(self, bot):
        self.bot = bot

    async def execute(self, query: str, isSelect: bool = False, fetchAll: bool = False, commit: bool = False):
        connection = await aiomysql.connect(host='localhost', port=3306,
                                              user='root', password=config.dbpass,
                                              db='nekobot')
        async with connection.cursor() as db:
            await db.execute(query)
            if isSelect:
                if fetchAll:
                    values = await db.fetchall()
                else:
                    values = await db.fetchone()
            if commit:
                await connection.commit()
        connection.close()
        if isSelect:
            return values

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def toxicity(self, ctx, *, text:str):
        """Get text toxicity levels"""
        try:
            API_KEY = "AIzaSyAc49LROgPF9IEiLDavWqwb2z8UndUUbcM"
            service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)
            analyze_request = {
                'comment': {'text': f'{text}'},
                'requestedAttributes': {'TOXICITY': {},
                                        'SEVERE_TOXICITY': {},
                                        'SPAM': {},
                                        'UNSUBSTANTIAL': {},
                                        'OBSCENE': {},
                                        'INFLAMMATORY': {},
                                        'INCOHERENT': {}}
            }
            response = service.comments().analyze(body=analyze_request).execute()
            em = discord.Embed(color=0xDEADBF, title="Toxicity Levels")
            em.add_field(name="Toxicity",
                         value=f"{round(float(response['attributeScores']['TOXICITY']['summaryScore']['value'])*100)}%")
            em.add_field(name="Severe Toxicity",
                         value=f"{round(float(response['attributeScores']['SEVERE_TOXICITY']['summaryScore']['value'])*100)}%")
            em.add_field(name="Spam",
                         value=f"{round(float(response['attributeScores']['SPAM']['summaryScore']['value'])*100)}%")
            em.add_field(name="Unsubstantial",
                         value=f"{round(float(response['attributeScores']['UNSUBSTANTIAL']['summaryScore']['value'])*100)}%")
            em.add_field(name="Obscene",
                         value=f"{round(float(response['attributeScores']['OBSCENE']['summaryScore']['value'])*100)}%")
            em.add_field(name="Inflammatory",
                         value=f"{round(float(response['attributeScores']['INFLAMMATORY']['summaryScore']['value'])*100)}%")
            em.add_field(name="Incoherent",
                         value=f"{round(float(response['attributeScores']['INCOHERENT']['summaryScore']['value'])*100)}%")
            await ctx.send(embed=em)
        except discord.Forbidden:
            pass
        except:
            await ctx.send("Error getting data.")

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def food(self, ctx):
        """Grabs Random Food Recipes"""
        url = "https://www.themealdb.com/api/json/v1/1/random.php"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
                res = res['meals'][0]
        meal = res['strMeal']
        meal_type = res['strCategory']
        instructions = res['strInstructions']
        thumb = res['strMealThumb']

        ingredient1 = res['strIngredient1']
        ingredient2 = res['strIngredient2']
        ingredient3 = res['strIngredient3']
        ingredient4 = res['strIngredient4']
        ingredient5 = res['strIngredient5']
        ingredient6 = res['strIngredient6']
        ingredient7 = res['strIngredient7']
        ingredient8 = res['strIngredient8']
        ingredient9 = res['strIngredient9']
        ingredient10 = res['strIngredient10']
        ingredient11 = res['strIngredient11']
        ingredient12 = res['strIngredient12']
        ingredient13 = res['strIngredient13']
        ingredient14 = res['strIngredient14']
        ingredient15 = res['strIngredient15']
        ingredient16 = res['strIngredient16']
        ingredient17 = res['strIngredient17']
        ingredient18 = res['strIngredient18']
        ingredient19 = res['strIngredient19']
        ingredient20 = res['strIngredient20']

        e = discord.Embed(color=0xDEADBF,
                          title=f"{meal} | {meal_type}",
                          description=instructions)
        e.add_field(name="Ingredients:", value=f"{ingredient1} {ingredient2} {ingredient3} {ingredient4} {ingredient5}"
                                               f" {ingredient6} {ingredient7} {ingredient8} {ingredient9} {ingredient10}"
                                               f" {ingredient11} {ingredient12} {ingredient13} {ingredient14} {ingredient15}"
                                               f" {ingredient16} {ingredient17} {ingredient18} {ingredient19} {ingredient20}")

        e.set_image(url=thumb)

        try:
            await ctx.send(embed=e)
        except discord.Forbidden:
            pass
        except:
            await ctx.send("There was an error. Please try again.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def achievement(self, ctx, *, achievement:str):
        """Achievement Generator"""
        if not os.path.isfile(f"data/achievement/{achievement.lower().replace(' ', '%20')}.png"):
            try:
                url = f"https://www.minecraftskinstealer.com/achievement/a.php?i=2&h=Achievement%20Get!" \
                      f"&t={achievement.replace(' ', '%20')}"
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(url) as r:
                        res = await r.read()
                img = Image.open(BytesIO(res))
                img.save(f"data/achievement/{achievement.lower().replace(' ', '-')}.png")
            except Exception as e:
                return await ctx.send(f"**{e}**")
        try:
            await ctx.send(file=discord.File(f"data/achievement/{achievement.lower().replace(' ', '-')}.png"))
        except discord.Forbidden:
            pass

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def threats(self, ctx, user:discord.Member):
        await ctx.trigger_typing()
        userurl = user.avatar_url_as(format='png')
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=threats&url={userurl}") as r:
                res = await r.json()
        await ctx.send( embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))

    @commands.command(aliases=['pillow'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def bodypillow(self, ctx, user: discord.Member):
        """Bodypillow someone"""
        await ctx.trigger_typing()
        userurl = user.avatar_url_as(format='png')
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=bodypillow&url={userurl}") as r:
                res = await r.json()
        em = discord.Embed(color=0xDEADBF, title=f"{user.name}'s body pillow.")
        await ctx.send(embed=em.set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def baguette(self, ctx, user:discord.Member):
        """:^)"""
        await ctx.trigger_typing()
        if user is None:
            user = ctx.message.author
        userurl = user.avatar_url_as(format='png')
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=baguette&url={userurl}") as r:
                res = await r.json()
        try:
            await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))
        except discord.Forbidden:
            pass

    @commands.command(name="b64", aliases=['b64encode', 'base64encode'])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def base_encode(self, ctx, *, encode_to: str):
        """Encode with Base64"""
        try:
            encoded = base64.b64encode(encode_to.encode())
            await ctx.send(embed=discord.Embed(color=0xDEADBF, title=f"{encode_to}",
                                               description=f"```\n{encoded}\n```"))
        except discord.Forbidden:
            pass
        except Exception as e:
            await ctx.send(f"Could not encode.\n`{e}`")

    @commands.command(name="md5")
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def md_five(self, ctx, *, encode_to: str):
        """Encode with Base64"""
        try:
            encoded = hashlib.md5(encode_to.encode('utf-8')).hexdigest()
            await ctx.send(embed=discord.Embed(color=0xDEADBF, title=f"{encode_to}",
                                               description=f"```\n{encoded}\n```"))
        except discord.Forbidden:
            pass
        except Exception as e:
            await ctx.send(f"Could not encode.\n`{e}`")

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def clyde(self, ctx, *, text : str = None):
        if text is None:
            text = "ReKT is best bot maker"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=clyde&text={text}") as r:
                res = await r.json()
        try:
            await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))
        except discord.Forbidden:
            pass

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def monkaS(self, ctx):
        try:
            emoji = self.bot.get_emoji(385481793853194240)
            await ctx.message.add_reaction(emoji)
        except:
            pass

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def joke(self, ctx):
        """Sends a Joke OwO"""
        async with aiohttp.ClientSession(headers={"Accept": "application/json"}) as cs:
            async with cs.get('https://icanhazdadjoke.com/') as r:
                res = await r.json()
                e = discord.Embed(color=0xDEADBF, description=f"**{res['joke']}**")\
                    .set_thumbnail(url="https://vignette.wikia.nocookie.net/2b2t8261/images/e/ed/LUL.png")
                await ctx.send(embed=e)

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def ship(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """Ship OwO"""
        if user2 is None:
            user2 = ctx.message.author

        await ctx.trigger_typing()
        ranxd = random.randint(1, 2)
        if ranxd == 1:
            if not os.path.isfile(f"data/ship/mode1-{user1.id}-{user2.id}.png"):
                async with aiohttp.ClientSession() as session:
                    async with session.post('https://api.weeb.sh/auto-image/love-ship',
                                            headers={'Authorization': f'Wolke {config.weeb}'},
                                            data={'targetOne': user1.avatar_url, 'targetTwo': user2.avatar_url}) as response:
                        t = await response.read()
                        with open(f"data/ship/mode1{user1.id}-{user2.id}.png", "wb") as f:
                            f.write(t)
                        score = random.randint(0, 100)
                        filled_progbar = round(score / 100 * 10)
                        counter_ = '█' * filled_progbar + '‍ ‍' * (10 - filled_progbar)

                        self_length = len(user1.name)
                        first_length = round(self_length / 2)
                        first_half = user1.name[0:first_length]
                        usr_length = len(user2.name)
                        second_length = round(usr_length / 2)
                        second_half = user2.name[second_length:]
                        finalName = first_half + second_half
                        e = discord.Embed(color=0xDEADBF, title=f'{user1.name} ❤ {user2.name}', description=f"**Love %**\n"
                                                                                            f"`{counter_}` **{score}%**\n\n"
                                                                                            f"{finalName}")
            await ctx.send(file=discord.File(fp=f'data/ship/mode1{user1.id}-{user2.id}.png'),
                           embed=e.set_image(url=f'attachment://mode1{user1.id}-{user2.id}.png'))
        else:
            user2url = user2.avatar_url
            user1url = user1.avatar_url

            self_length = len(user1.name)
            first_length = round(self_length / 2)
            first_half = user1.name[0:first_length]
            usr_length = len(user2.name)
            second_length = round(usr_length / 2)
            second_half = user2.name[second_length:]
            finalName = first_half + second_half

            score = random.randint(0, 100)
            filled_progbar = round(score / 100 * 10)
            counter_ = '█' * filled_progbar + '‍ ‍' * (10 - filled_progbar)
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://nekobot.xyz/api/imagegen?type=ship&user1={user1url}&user2={user2url}") as r:
                    res = await r.json()
            e = discord.Embed(color=0xDEADBF, title=f'{user1.name} ❤ {user2.name}', description=f"**Love %**\n"
                                                                                                f"`{counter_}` **{score}%**\n\n"
                                                                                                f"{finalName}")
            await ctx.send(content="{}".format(finalName),
                           embed=e.set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 45, commands.BucketType.user)
    async def shitpost(self, ctx):
        """Shitpost ofc"""
        await ctx.trigger_typing()
        shitpost = [
            "I am 11 yeears oLD and ready to hurt myself by STEPPING ON. Lego . I yell at brother telling leggomy eggo because it came from Walmart and I want to step on a Lego. Never but Legos I it not gonna eat them and step on them 💀 they kill!!!1!!1 I want 35 dollars to buy some robuxxx.",
            "In 2001, Microsoft legally had to ship every version of windows with a folder known today as System32 it is a folder that lets the government and/or hackers spy on you. You do not legally have to have it installed. It is best that the first thing you do is delete system32. To do it, ask someone else I cant be bothered.",
            "Hiii guys~ 😆🖑 im🕴11 years 🤖 old😉🤗 and my favrit 👍👍❤ raper 🕶🔊🎤 is xxxtentacion🙃🙃 one ☝️ time🕐🕐 my mom👰👰 tooke away my ipad😔🙄🖕🏼 awaay and i got rlly 😡mad and angry😠 rite so thenn i 📣🎧listend🎧 to xxtenshun's 💞 songg🔊🎤 nd i rllly rlated to it 😩😩 and know hes my fav rpaper🙂🙂🙂",
            "Ok, I am going to explain you idiots why being alive is actually gay. So as you guys may know, being alive requires breathing the atmosphere, which is approximately 78.084% Nitrogen, 20.946% Oxygen, 0.9340% Argon etc. There's a lot of other things including the vapor of whatever liquids you're around at the moment. Now, to get to the point, every man that ever ejaculated has traces of sperm in his penis, sperm is a liquid which means it evaporates all the time and escapes into the atmosphere. That means that by breathing you're swallowing sperm, and that's gay.",
            "Listen up bitch. I have my girlfriend right here next to me as my fucking SLAVE. I am a fucking ALPHAMALE who eats meat, fucks your girlfriend and female relatives, and otherwise...is superior to people who don't eat animal proteins. If you ate a 100% Non-GMO Full Vegan diet VERSUS me...a typical American who eats meats, carbs, and some vegetables; Who would win in a fight? We can set this up now, just for the amusement of people online/youtube/etc. Me versus You. A simple fight to prove which diet is actually better for a human male? You can brag about how much you spend to keep so fucking healthy, but the truth is...l would dominate you in a fight until you either gave up, started crying, or were knocked unconscious. Ahhhh, what am I saying? You are probably too much of a coward to fight anyone anyway. lol.",
            "You just insulted my favorite game of all time. Somehow this tells me that you're not old enough to understand the pain and complexity that people can hold. Doki Doki isn't just a visual novel. It illustrates the pain of everyone. Every single bit of it makes perfect sense. I can tell you're pretty young because you play minecraft. Also because you put your real name on a social site where everybody can access it. So obviously you wouldn't understand any of DDLC because it's not meant for little kids because 1) it's disturbing in some parts and 2) it illustrates many concepts that won't usually be encountered until later in life and 3) it has a lot of profanity. DDLC is a work of art; something to be admired and enjoyed. Each character is crafted with very fine precision.",
            "A Weeaboo has been detected in this post. The Weeaboo has been identified with the Keyword (replace with something a weeb would say). Please evacuate from this post immediately.",
            "I was born with glass bones and paper skin. Every morning I break my legs and every afternoon I break my arms. At night, I lay awake in agony until my heart attacks put me to sleep.",
            "⚠🚫🚫🚫🚧🚧HALT🚧🚧🚫🚫🚫⚠[scanning... 10%] [scanning... 48%] [scanning... 72%] [scanning complete.] system consensus: a THOT has been detected. entering lockdown mode.",
            "hey man i just want to be friends this is different <insert picture of black cock> WHAT I WILL RAGE AFTER YOU AND YOUR FAGGOT FRIENDS RA RA RAH RAGE I WILL MAKE 25 DISCORD ACCOUNTS AND EVENTUALLY ONE OF THEM WILL WIN AND TAKE ADMIN I will delete my discord",
            "Now that draws the line, I'm completely fine with the mass genocide of an entire race but when someone targets roblox accounts, that just ticks me off. That just grinds my metaphorical gears, that just forces me to scale the walls of my residence. It just stirs emotions of anger, fear, hatred, all of it, it just makes me feel emotionally high. Roblox is a gift from god, roblox accounts are like lives, you don't steal them, you don't steal god's gifts, it's a sin as much as murder is. It's morally wrong, even though I'm fine with the mass murder of a race, roblox account stealing is just totally wrong. Please stop, please.﻿",
            "🚶You owned a car 🚗🚗 for 4⏰📅 years⏰👍. You🚶 named it👱 Brad👱. You💑❤💗 loved💕Brad💕😙. And then you🚶⚠ totaled⚠🚧🚗🚙 him🚦. You two 💏💑had been through everything 👬together🎭. 👬2 boyfriends👬, 🔨🔧3 jobs🔫,❌ nothing ❌could replace👱 Brad🍆🍆. Then Liberty Mutual",
            "Ok listen here piece of american shit. You may think yourself as the greatest fucking retard out in this world , but let me say this to you : You're an arrogant cunt that acts like an adult and shut the fuck up. i mean SHUT THE FUCK UP you fucking braindead retard that probably hot beaten by your drunk father while while your mom killed herself in the bathtub swallowing the soap like the bitch she is. You're just a self-centered morron that likes making people feel bad . people like you deserve death on the electric chair . you bring only hate while you fuck others for your own enjoyment. fucking downgrade bastard. i treat everyone equally but i hate narcissits . and that's what you are. a narcissist with internet connection that shows of on sites at how good he is at shit while you have nothing to show in the real like. btw thanks for making me write this shit on christmas , by how quick you respond it means that your familly hates you and they dont spend time with you. i bet your mother commited suicide after she saw the retard she raised. now eat shit and die in the closest pub.﻿",
            "you are worst turk. you are the turk idiot you are the turk smell. return to croatioa. to our croatia cousins you may come our contry. you may live in the zoo….ahahahaha ,bosnia we will never forgeve you. cetnik rascal FUck but fuck asshole turk stink bosnia sqhipere shqipare..turk genocide best day of my life. take a bath of dead turk..ahahahahahBOSNIA WE WILL GET YOU!! do not forget ww2 .albiania we kill the king , albania return to your precious mongolia….hahahahaha idiot turk and bosnian smell so bad..wow i can smell it. REMOVE KEBAB FROM THE PREMISES. you will get caught. russia+usa+croatia+slovak=kill bosnia…you will ww2/ tupac alive in serbia, tupac making album of serbia . fast rap tupac serbia. we are rich and have gold now hahahaha ha because of tupac… you are ppoor stink turk… you live in a hovel hahahaha, you live in a yurt tupac alive numbr one #1 in serbia ….fuck the croatia ,..FUCKk ashol turks no good i spit﻿ in the mouth eye of ur flag and contry. 2pac aliv and real strong wizard kill all the turk farm aminal with rap magic now we the serba rule .ape of the zoo presidant georg bush fukc the great satan and lay egg this egg hatch and bosnia wa;s born. stupid baby form the eggn give bak our clay we will crush u lik a skull of pig. serbia greattst countrey",
            "Oh my fuck- Oh my fucking god! Have you seen her? She’s so beautiful. I’ve never felt this way before for anyone. She makes my heart beat a million miles a minute. I will do anything for her. I would die for her; to protect someone so precious. I wish I could comfort her and give her head pats. Imagine how beautiful our kids would be! Let us sing and dance together. Imagine us laying in bed and whispering sweet nothings to each other. Imagine how cute that would be. Imagine playing dress up with her and choosing what clothes she will wear. She’ll say “it’s too tight, but I’ll wear it for you...” Imagine how passionate we would be for each other during sex. Oh how I long for that feeling. I have chosen to retain my virginity just for her, my love. But God has other plans for us... he separates us even though we are meant to be together. God why have you forsaken me?! Let me love who I love! Let me be with her... One day, my dream and goal in life is that I will be come a scientist, with my intellect, and develop an invention to bring her into our plan of existence. She may not be real to the world, but she is real in my heart. Yes, Sans from Undertale, it will not be long until I will see you.",
            "One day in 1938 hitlers mom told hitler, 'gas the jews'. Hitler was shocked by this statement, but still agreed and began a worldwide conquest. In 1945 hitler stumbled back to his barrack, defeated and humiliated. 'Well mom i did what you asked at least' he said. Hitlers mom glared at him before saying' i asked for a glass of juice, not gas the jews'. After hearing this, hitler shot himself. So hitler did nothing wrong it was his mother.",
            "I do my best to include my workout into my game playing while I wait for the next round to start all I do is pushups and situps. In between my competitive (CSGO) sessions I tend to do more intensive cardio related workouts.",
            "back off shes mine teleports behind caity and swoops into arms, taking her into cover and then teleporting back my name's sponic, i'm 13, red and black, and i'll beat you up because i can't die and i can dodge all attacks. come at me you f***er. sorry my mom is looking at the screen . nothing personnel kid. heil hitler. did i mention my oc is a nazi? i'll pound you into submission and save m'lady so hard and finally have someone to play minecraft with. caity what's your minecraft mine is awesomekraftr06 because i love minecraft . i hate you sonic the ehdgehog 123 face my rath.",
            "i come to study Mechanical Engineering at American university. i am here little time and i am very hard stress. i am gay also and this very difficult for me, i am very religion person. i never act to be gay with other men before. but after i am in america 6 weeks i am my friend together he is gay also. He was show me American video game and then we are kiss. We sex together. I never before now am tell my mother about gay because i am very shame. As i ** this American boy it is very good to me but also i am feel so guilty. I feel extreme guilty as I begin orgasm. I feel so guilty that I pick up my telephone and call Mother in Russia. I awaken her. It too late for stopping so I am cumming sex. I am very upset and guilty and crying, so I yell her, 'I AM CUM FROM SEX' (in Russia). She say what? I say 'I AM CUM FROM SEX' and she say you boy, do not marry American girl, and I say 'NO I AM CUM FROM SEX WITH MAN, I AM IN ASS, I CUM IN ASS' and my mother very angry me. She not get scared though. I hang up phone and am very embarrass. My friend also he is very embarrass. I am guilt and feel very stupid. I wonder, why do I gay with man? But I continue because when it spurt it feel very good in American ass.",
            "_-kun.. d-do you.. really have feelings for me?~ UwU B-Baka!!! I-It's not like i like you back or anything... OwO Hehe nuzzles _-kun i wuv chu~ O//////O yur su kawaii sugoi.. >< aishteru <3 _-kun..~ y-your my sugoi U/////U senpai~~ Ow< hehe nyaa~~ XDDD wiggles ears and tail X////X you make me sekimen~~ <333 UwU",
            "The banana is an edible fruit – botanically a berry[1][2] – produced by several kinds of large herbaceous flowering plants in the genusMusa.[3] In some countries, bananas used for cooking may be called plantains, in contrast to dessert bananas. The fruit is variable in size, color, and firmness, but is usually elongated and curved, with soft flesh rich in starch covered with a rind, which may be green, yellow, red, purple, or brown when ripe. The fruits grow in clusters hanging from the top of the plant. Almost all modern edible parthenocarpic (seedless) bananas come from two wild species – Musa acuminata and Musa balbisiana. The scientific names of most cultivated bananas are Musa acuminata, Musa balbisiana, and Musa × paradisiaca for the hybrid Musa acuminata × M. balbisiana, depending on their genomic constitution. The old scientific name Musa sapientum is no longer used.",
            "When I was in 8th grade one of my teachers told everyone in my class one of us had autism and he couldn’t tell us who because that person didn’t know and now at least once a month I lay awake at night wondering if I’m autistic and everyone is just treating me normal, but I’m at an Italian restaurant with my parents and the waitress just asked me for soup or salad and for the 5th time in my life I responded with yes thinking she said 'super salad' and I realized that finally gave me the answer that I am in fact, the one with autism."
            "I bet when you touch your filthy genitals with your sinner hands and you're about to squirt, you orgasm. Take your caveman habits and your prehistoric noises along with you. If you want to scream out of pleasure, just go to a cave like the animal you are. Fucking humanoid. What a filthy whore you are. Loving yourself and wanting to feel pleasure. Tsk tsk tsk, go to church, maybe there's still hope for you, you cock-loving slut. If I could hit you with a stick I certainly would but thanks to the new legislations and laws, something like that is far from legal. The only measure one could take is exclaiming \"BEGONE THOT\" while referring to you, but your screams are so loud you have made yourself deaf. What a fucking wanker you are. Your ass by now is probably some random dude's cumdumpster. You smell of sin. Fucking slut.",
            "Hello , this is the owner of HentaiHaven.org We are currently making a catalog with anime babes inside to sell to our veiwers. Would you be interested in sketching one for us? We understand that you are a huge fan of our website and have over 3000 hours watchtime! We would love it if you could draw us an 11 year old girl called Natsuki! We have also seen your artwork of Earth Chan hentai comics and we loved it! We can give you a free Premium account on our website and throw in a little extra episode for you ;). Dont miss out on this Amazing Deal!",
            "Think about it, Roblox is a form of cancer. Vaccines have a little bit of what they cure in them. So Roblox cures cancer right? Maybe not. The game is cancer enough, but the 10 year old squeakers are as well. These grade school kids will make your ears bleed so badly that you'll be jealous of Helen Keller. Also the youtube intros are the bloody WORST. I mean take Minecraft intros and inject them with ultra AIDS and mecha-Ebola. I mean the community is just a tumor in it of itself. Based on this evidence Roblox is more cancer than cancer itself. And since cancer is a mild form of Roblox, cancer is the cure to Roblox. Cancer also has the added benefit of taking you out of your misery if it fails to cure you. In short: GOD IS DEAD AND ROBLOX KILLED HIM!!",
            "Loli? Really? Loli. Is that the level you'd stoop to just to get off? You know that's basically anime childporn, right? You do know that it'd be halfway less bad-looking on you if you were a furry, right? Do you know where furries go to talk to other furries? Furry conventions. But for the lolicon, wanna know where they go to talk with other lolicons? Prison. FUCKING PRISON. Get out of my sights, just looking at you is making me fucking sick. That you'd even think of saying something like that in my presence. Know your place you perverted piece of shit. I bet you only wanna fuck a loli because they're the only ones that'll feel your micro-chode baby dick. A full-grown woman wouldn't even bother looking at you. Ugh... fucking ew. Go away! Go! GO!!! GET THE FUCK OUT!!!! No one wants you here, you pedophile! Hey, everyone, Frank is a fucking pedophile! They like lolis! Hahaha!~ Have fun in prison, you fucking cuck. <3",
            "Well 🤔I 👳wrote📝 this song 🎵for the christian👼 youth👶. I wanna teach kids👨‍👨‍👧‍👧 the christian truth🗣. If you 👊wanna reach🖐 those kids👦👦 on the street🌆. Then you gotta do a rap🎤 to a hip-hop 🎙beat. So I gave my summon an urban kick⚽. And my rhymes are fly🐦, my beats are sick😷. My crew is big👦👼👶👳👥👨‍👨‍👧‍👧 and it keeps getting bigga, That's cause Jesus 👼christ is my nigga🙊. He's a life changer👷, miracle arranger. Born to the virgin 🤓mom in the manger. Water to wine🍷, he's a drink exchanger. And he died😵 for your sins. I preach✊ the word, that's my gig. And I am better than the notorious big💩. And the other MC's 😎are wishing well. But if you live in sin, you burn 🔥in hell. Now pass my mic🎙 to my lovely wife👩. She's a fly MC and a love❤ of my life. So lets bust 🍆a rhyme with a further-a-do. Take it away, mary sue.👧. Jesus christ is my nigga. He's the son of the original g↪.And he was sent to earth🌎 to the way we should be. Like if another MC says \"Your a freak,😠 your a lame butt 🍑rapper and your rhymes are weak🤓\". I don't get mad😡 and I don't critique. I forgive him🤗, and turn the other cheek. I don't blaspheme and I don't brag, I don't cuss😤, and my pants👖 don't sag. I do a little christian swag and I'm proud to be an american🇺🇸. Jesus Christ is a nigga. Let the light 🌞shine through ya. Now lets pop a cap in your butt 🍑and say \"Hallelujah\". Jesus Christ is a nigga. He's a homie MC, JC, you see👀. He's an honest, caring, peace loving nigga like me😇. If you do drugs☣ and you think your cool😎. You need to come to the sunday school⛪. Put those drugs in a garbage can🗑, stand up tall🕴 you're a christian man.",
            "femboys awe the futuwe of ouw genyewation uwu, they awe cute, giwwy and wuvs putting things up theiw wittwe swutty boipussy, they awe the pewfect giwwfwiends owo and they wiww wuv you fowevew and evew so they nyuzzwes with you O//W//O wooks at daddy c-can I be youw sexy femboy so you can use me as a c-cummies wag pweaseeeee?"
        ]
        await ctx.send(embed=discord.Embed(description=random.choice(shitpost),
                                           color=0xDEADBF))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def captcha(self, ctx, user: discord.Member):
        """Captcha a User OWO"""
        url = user.avatar_url
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=captcha&url={url}&username={user.name}") as r:
                res = await r.json()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def whowouldwin(self, ctx:commands.Context, user1: discord.Member, user2: discord.Member = None):
        """Who would win"""
        await ctx.trigger_typing()
        if user2 is None:
            user2 = ctx.message.author
        user1url = user1.avatar_url
        user2url = user2.avatar_url
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=whowouldwin&user1={user1url}&user2={user2url}") as r:
                res = await r.json()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def duck(self, ctx):
        """Gets a duck image /shrug"""
        self.bot.counter['duck'] += 1
        url = "https://api.random-d.uk/random"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        em = discord.Embed(color=0xDEADBF)
        await ctx.send(embed=em.set_image(url=res['url']).set_footer(text=f"Ducks sent since last restart: {self.bot.counter['duck']}"))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def changemymind(self, ctx, *, text:str):
        votes = await self.execute("SELECT user FROM dbl", isSelect=True, fetchAll=True)
        voters = []
        for vote in votes:
            voters.append(vote[0])
        weebsh = self.bot.get_guild(300407204987666432)
        if str(ctx.message.author.id) in voters or weebsh.get_member(ctx.message.author.id):
            await ctx.trigger_typing()
            url = f"https://nekobot.xyz/api/imagegen?type=changemymind&text={text}"
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as r:
                    res = await r.json()
            await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))
        else:
            em = discord.Embed(color=0xDEADBF, description="https://discordbots.org/bot/nekobot/vote", title="owo whats this")
            return await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def owoify(self, ctx, *, text:str = None):
        if text is None:
            return await ctx.send("oopsie whoopsie you made a fucky wucky, you gave me no text to owoify")
        else:
            text = text.replace(' ', '%20')
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekos.life/api/v2/owoify?text={text}") as r:
                res = await r.json()
        try:
            em = discord.Embed(color=0xDEADBF, description=f"{res['owo']}", title="OwOified Text")
            await ctx.send(embed=em)
        except:
            return await ctx.send("Failed to get the OwOified Text or you input is over 100 characters.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lizard(self, ctx):
        """Get a lizard owo"""
        url = "https://nekos.life/api/lizard"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['url']))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def meme(self, ctx):
        """Get a dank meme OwO"""
        # NoSteal kthx
        sub = ["dankmemes", "animemes"] #Add more?
        url = f'https://api.imgur.com/3/gallery/r/{random.choice(sub)}/hot/{random.randint(1, 5)}'
        headers = {"Authorization": f"Client-ID {config.imgur}"}
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url, headers=headers) as r:
                res = await r.json()
        js = random.choice(res['data'])
        if js['nsfw'] or js['is_ad'] == True:
            while True:
                js = random.choice(res['data'])
                if js['nsfw'] or js['is_ad'] == False:
                    break
        embed = discord.Embed(color=0xDEADBF,
                              description=f"**{js['title']}**")
        embed.set_image(url=js['link'])
        time = datetime.datetime.fromtimestamp(int(js['datetime'])).strftime('%Y-%m-%d %H:%M')
        embed.set_footer(text=f"Posted on {time}")

        await ctx.send(embed=embed)


    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def penis(self, ctx, *, user : discord.Member):
        """Detects user's penis length"""
        if not ctx.message.channel.is_nsfw(): return
        state = random.getstate()
        random.seed(user.id)
        dong = "8{}D".format("=" * random.randint(0, 30))
        random.setstate(state)
        em = discord.Embed(title="{}'s Dick Size".format(user), description="Size: " + dong, colour=0xDEADBF)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vagina(self, ctx, *, user: discord.Member):
        """Detects user's vaginas depth"""
        if not ctx.message.channel.is_nsfw(): return
        state = random.getstate()
        random.seed(user.id)
        dong = "{} Meters Deep".format(str(random.randint(0, 30)))
        random.setstate(state)
        em = discord.Embed(title="{}'s Puss Depth".format(user), description="Size: " + dong, colour=0xDEADBF)
        await ctx.send(embed=em)

    @commands.command(pass_context=True)
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def jpeg(self, ctx, user : discord.Member = None):
        """OwO Whats This"""
        if user is None:
            user = ctx.message.author
        url = f"https://nekobot.xyz/api/imagegen?type=jpeg&url={user.avatar_url_as(format='jpg')}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def isnowillegal(self, ctx, legal : str):
        """Make Stuff Illegal!"""
        legal = legal.upper()
        url = "https://storage.googleapis.com/is-now-illegal.appspot.com/gifs/" + legal +".gif"
        em = discord.Embed(title="{} is now Illegal!".format(legal))
        em.set_image(url=url)
        await ctx.send(embed=em)

    @commands.command(pass_context=True, no_pm=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def gif(self, ctx, *keywords):
        """Retrieves first search result from giphy"""
        if keywords:
            keywords = "+".join(keywords)
        else:
            await self.bot.send_cmd_help(ctx)
            return

        url = ("http://api.giphy.com/v1/gifs/search?&api_key={}&q={}&rating=g"
               "".format(config.giphy_key, keywords))

        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
                if res["data"]:
                    await ctx.send(res["data"][0]["url"])
                else:
                    await ctx.send("No results found.")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def cat(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=animal_cat') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dog(self, ctx):
        async with aiohttp.ClientSession(headers=auth) as cs:
            async with cs.get('https://api.weeb.sh/images/random?type=animal_dog') as r:
                res = await r.json()
                em = discord.Embed(color=0xDEADBF)
                em.set_image(url=res['url'])
                await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bitconnect(self, ctx):
        videos = ["https://www.youtube.com/watch?v=d1oZ6P8ZBoM", "https://www.youtube.com/watch?v=CJe0rWOP4fE",
                  "https://www.youtube.com/watch?v=A8M70M7tzTI", "https://www.youtube.com/watch?v=lc2-ImMRMC8",
                  "https://www.youtube.com/watch?v=GLQAXo0xonI", "https://www.youtube.com/watch?v=9wlDhciUDD0",
                  "https://www.youtube.com/watch?v=vhyAREaWfyU", "https://www.youtube.com/watch?v=Ii_D-Fcks_A",
                  "https://www.youtube.com/watch?v=lsgvcCnztJ4", "https://www.youtube.com/watch?v=PDiSLXcAU3U",
                  "https://www.youtube.com/watch?v=d4a88-IhAVw", "https://www.youtube.com/watch?v=8tOFoEP-2f4",
                  "https://www.youtube.com/watch?v=e5nyQmaq4k4", "https://www.youtube.com/watch?v=upejO2mFqX0",
                  "https://www.youtube.com/watch?v=aPD9Mj1OWo4", "https://www.youtube.com/watch?v=Dy7RnUOmNcQ",
                  "https://www.youtube.com/watch?v=d4a88-IhAVw", "https://www.youtube.com/watch?v=vabXXkZjKiw",
                  "https://www.youtube.com/watch?v=W2GKSZdPgrY", "https://www.youtube.com/watch?v=axKTFLkFzDM",
                  "https://www.youtube.com/watch?v=FRA9FZSZKlg"]
        await ctx.send(random.choice(videos))

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def feed(self, ctx, user : discord.Member):
        if user == ctx.message.author:
            await ctx.send(f"-- {ctx.message.author.mention} eats {random.choice(food)} --")
        else:
            await ctx.send(f"-- Forces {random.choice(food)} down {user.name}'s throat --")

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def lovecalculator(self, ctx, user1 : discord.Member, user2 : discord.Member = None):
        """Love Calculator"""
        if user2 == None:
            user2 = ctx.message.author
        rnd = random.randint(1, 20)
        l1 = (len(user1.name))
        l2 = (len(user2.name))
        score = 100 - (l1 * l2) - rnd
        if score > 40:
            heart = "❤"
        else:
            heart = "💔"
        embed = discord.Embed(color=0xDEADBF,
                              title="Love Calculator",
                              description=f"{user1.name} {heart} {user2.name} = {score}%")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def iphonex(self, ctx:commands.Context, *, url: str):
        """Generate an iPhone X Image"""
        await ctx.trigger_typing()
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://nekobot.xyz/api/imagegen?type=iphonex&url={url}") as r:
                res = await r.json()
        if res['success'] is False:
            return await ctx.send("**Error generating image with that url.**")
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def kannagen(self, ctx, *, text:str):
        """Generate Kanna"""
        await ctx.trigger_typing()
        url = f"https://nekobot.xyz/api/imagegen?type=kannagen&text={text}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        await ctx.send(embed=discord.Embed(color=0xDEADBF).set_image(url=res['message']))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def butts(self, ctx):
        await ctx.send("ლ(́◉◞౪◟◉‵ლ)")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def boom(self, ctx):
        """BOOM"""
        await ctx.message.add_reaction("🅱")
        await ctx.message.add_reaction("🇴")
        await ctx.message.add_reaction("💥")
        await ctx.message.add_reaction("🇲")

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rude(self, ctx):
        """RUDE"""
        await ctx.message.add_reaction("🇷")
        await ctx.message.add_reaction("🇺")
        await ctx.message.add_reaction("🇩")
        await ctx.message.add_reaction("🇪")

    @commands.command(aliases=['fite', 'rust'])
    @commands.cooldown(1, 7, commands.BucketType.user)
    async def fight(self, ctx, user1: discord.Member, user2: discord.Member = None):
        """Fite sum1"""
        if user2 == None:
            user2 = ctx.message.author

        map = "https://vignette.wikia.nocookie.net/callofduty/images/3/33/Rust.jpg"
        em = discord.Embed(color=0xDEADBF,
                           title="Intense Rust 1v1")
        em.set_image(url=map)
        em.add_field(name=f"Round | {user1.name} vs {user2.name}",
                     value=f"***pew pew*** {random.choice([user1.name, user2.name])} got the first hit and won OwO")
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Fun(bot))
