from discord.ext import commands
import discord, aiohttp

class Crypto:
    """Cryptocurrency Information"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def crypto(self, ctx, crypto: str):
        """Get cryptocurrency info"""
        coin = "USD,EUR,GBP,JPY,CHF,AUD,CAD,INR,IDR,NZD,ZAR,SEK,SGD,KRW,NOK,MXN,BRL,HKD,RUB,MYR,THB,"
        tsyms = coin + "BTC,BCH,ETH,ETC,LTC,XMR,DASH,ZEC,DOGE,DCR"
        url = f"https://min-api.cryptocompare.com/data/price?fsym={crypto.upper()}&tsyms={tsyms}"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(url) as r:
                res = await r.json()
        try:
            USD  = res['USD']
            EUR  = res['EUR']
            GBP  = res['GBP']
            JPY  = res['JPY']
            CHF  = res['CHF']
            AUD  = res['AUD']
            CAD  = res['CAD']
            INR  = res['INR']
            IDR  = res['IDR']
            NZD  = res['NZD']
            ZAR  = res['ZAR']
            SEK  = res['SEK']
            SGD  = res['SGD']
            KRW  = res['KRW']
            NOK  = res['NOK']
            MXN  = res['MXN']
            BRL  = res['BRL']
            HKD  = res['HKD']
            RUB  = res['RUB']
            MYR  = res['MYR']
            THB  = res['THB']

            BTC  = res['BTC']
            BCH  = res['BCH']
            ETH  = res['ETH']
            LTC  = res['LTC']
            XMR  = res['XMR']
            DASH = res['DASH']
            ZEC  = res['ZEC']
            DOGE = res['DOGE']
            DCR  = res['DCR']

            e = discord.Embed(color=0xDEADBF, title=f"{crypto.upper()} Conversion",
                              description=f"🇺🇸 US Dollar: **${USD}**\n"
                                          f"🇪🇺 Euro: **€{EUR}**\n"
                                          f"🇬🇧 British Pound: **£{GBP}**\n"
                                          f"🇯🇵 Japanese Yen: **¥{JPY}**\n"
                                          f"🇨🇭 Swiss Franc: **Fr.{CHF}**\n"
                                          f"🇦🇺 Australian Dollar: **${AUD}**\n"
                                          f"🇨🇦 Canadian Dollar: **${CAD}**\n"
                                          f"🇮🇳 Indian Rupee: **₹{INR}**\n"
                                          f"🇮🇩 Indonesian Rupiah: **IDR {IDR}**\n"
                                          f"🇳🇿 New Zealand Dollar: **${NZD}**\n"
                                          f"🇿🇦 South African Rand: **R{ZAR}**\n"
                                          f"🇸🇪 Swedish Krona: **kr {SEK}**\n"
                                          f"🇸🇬 Singapore Dollar: **${SGD}**\n"
                                          f"🇰🇷 South Korean Won: **₩{KRW}**\n"
                                          f"🇳🇴 Norwegian Krone: **kr {NOK}**\n"
                                          f"🇲🇽 Mexican Peso: **Mex${MXN}**\n"
                                          f"🇧🇷 Brazilian Real: **R${BRL}**\n"
                                          f"🇭🇰 Hong Kong Dollar: **HK${HKD}**\n"
                                          f"🇷🇺 Russian Ruble: **₽{RUB}**\n"
                                          f"🇲🇾 Malaysian Ringgit: **RM {MYR}**\n"
                                          f"🇹🇭 Thai Baht: **฿ {THB}**")
            e.add_field(name="Cryptocurrency",
                        value=f"<:bitcoin:423859742281302036> Bitcoin: **₿{BTC}**\n"
                              f"<:bitcoincash:423863215840034817> Bitcoin Cash: {BCH}**\n"
                              f"<:eth:423859767211982858> Ethereum: ♦{ETH}**\n"
                              f"<:ltc:423859753698197507> Litecoin: Ł{LTC}**\n"
                              f"<:monero:423859744936034314> Monero: ɱ{XMR}**\n"
                              f"<:dash:423859742520377346> Dash: {DASH}**\n"
                              f"<:yellowzcashlogo:423859752045379594> Zcash: ⓩ{ZEC}**\n"
                              f"<:dogecoin:423859755384045569> Dogecoin: Đ{DOGE}**\n"
                              f"<:decred:423859744361676801> Decred: {DCR}**", inline=True)
        except:
            e = discord.Embed(color=0xDEADBF, title="⚠ Error", description="Not a valid currency format.")
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Crypto(bot))