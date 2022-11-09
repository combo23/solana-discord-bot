import discord
from discord.ext import commands
import requests
from forex_python.converter import CurrencyRates
from solana.keypair import Keypair
import helheim
import cloudscraper
from datetime import datetime
guilds = []
white = 0xffffff
helheim.auth('')
helheim_path = ""
def log(content):
        print(f'[{datetime.now()}] [SOLCHEFS] {content}')
def loadhelheim():
    def injection(session, response):
            if helheim.isChallenge(session, response):
                return helheim.solve(session, response)
            else:
                return response

    session = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome', 
                'mobile': False, 
                'platform': 'windows' 
            },
            requestPostHook=injection,

        )
    session.bifrost_clientHello = 'chrome'
    helheim.bifrost(session,helheim_path) 
    return session



bot = commands.Bot()

def walletsave(pub,priv):
    logs = open("wallets.csv", 'a')
    logs.write(f"{pub},{priv}\n")
    logs.close()


@bot.slash_command(name="price", guild_ids=guilds) 
async def get_price(ctx, crypto, howmany): 
    getprice = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={str(crypto).upper()}USDT")
    baseprice = getprice.json()['price']
    fullprice = float(baseprice) * int(howmany)
    c = CurrencyRates()
    fullplnprice = c.convert('USD', 'PLN', fullprice)
    fullresponse = f"{round(fullprice, 2)} USD\n{round(fullplnprice, 2)} PLN"
    
    embed=discord.Embed(title=f"{str(howmany)} {str(crypto).upper()} Price", url="https://twitter.com/sol_chefs", color=white)
    embed.add_field(name="USD", value=round(fullprice, 2), inline=False)
    embed.add_field(name="PLN", value=round(fullplnprice, 2), inline=False)
    embed.set_thumbnail(url="https://pbs.twimg.com/profile_images/1502650525816397824/HFcwTzh1_400x400.jpg")
    embed.set_footer(text="SolChefs | by Combo#2137", icon_url="https://pbs.twimg.com/profile_images/1502650525816397824/HFcwTzh1_400x400.jpg")
    await ctx.respond(embed=embed)
    log(f"{ctx.author} used price command")
    #await ctx.respond(f"{fullresponse}")


@bot.slash_command(name="generate_solana_wallet", guild_ids=guilds)
async def get_wallets(ctx, howmany): 
    open("wallets.csv", "w").close()
    walletsave("public_key","private_key")
    for x in range(int(howmany)):
        keypair = Keypair()
        private_key =keypair.secret_key.hex()
        public_key =keypair.public_key
        walletsave(str(public_key),str(private_key))


    await ctx.respond(f"Generated {howmany} wallets")
    await ctx.author.send(file=discord.File(r'wallets.csv'))
    log(f"{ctx.author} generated {howmany} wallets")

@bot.slash_command(name="get_collection_data", guild_ids=guilds) 
async def get_data(ctx, link):
    session = loadhelheim()
    slug = link.split("/")[-1]
    getdata = session.get(f"https://api-mainnet.magiceden.io/collections/{slug}?edge_cache=true")
    if getdata.status_code != 200:
        await ctx.respond(f"Error: [{getdata.status_code}]")
    ogimage = getdata.json()['image']
    name = getdata.json()['name']

    getotherdata = session.get(f"https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/{slug}?edge_cache=true")
    floorprice = int(getotherdata.json()['results']['floorPrice']) /1000000000
    listedcount = int(getotherdata.json()['results']['listedCount']) 
    avgprice = int(getotherdata.json()['results']['avgPrice24hr']) /1000000000
    volume24hr = int(getotherdata.json()['results']['volume24hr']) /1000000000

    embed=discord.Embed(title=f"{str(name)}", url=link, color=white)
    embed.add_field(name="Floorprice", value=f"{floorprice}◎", inline=False)
    embed.add_field(name="Listed count", value=f"{listedcount}", inline=False)
    embed.add_field(name="Average price 24h", value=f"{avgprice}◎", inline=False)
    embed.add_field(name="Volume 24h", value=f"{volume24hr}◎", inline=False)
    embed.set_thumbnail(url=ogimage)
    embed.set_footer(text="SolChefs | by Combo#2137", icon_url="https://pbs.twimg.com/profile_images/1502650525816397824/HFcwTzh1_400x400.jpg")
    await ctx.respond(embed=embed)
    log(f"{ctx.author} used get_collection_data command")




bot.run("")