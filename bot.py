import discord
from discord.ext import commands, tasks
import json
import os

# Boto teisių (Intents) nustatymas
intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

REKORDO_FAILAS = "rekordas.json"

# Funkcijos rekordo užkrovimui ir išsaugojimui
def gauti_rekorda():
    if not os.path.exists(REKORDO_FAILAS):
        with open(REKORDO_FAILAS, "w") as f:
            json.dump({"rekordas": 0}, f)
    with open(REKORDO_FAILAS, "r") as f:
        return json.load(f)["rekordas"]

def issaugoti_rekorda(kiekis):
    with open(REKORDO_FAILAS, "w") as f:
        json.dump({"rekordas": kiekis}, f)

@bot.event
async def on_ready():
    print(f"Botas {bot.user} sėkmingai paleistas!")
    atnaujinti_statusa.start() # Paleidžiame fono užduotį

# Užduotis, kuri kas 5 minutes atnaujina informaciją
@tasks.loop(minutes=5)
async def atnaujinti_statusa():
    for guild in bot.guilds:
        nariu_skaicius = guild.member_count
        rekordas = gauti_rekorda()
        
        # Tikriname, ar pasiektas naujas rekordas
        if nariu_skaicius > rekordas:
            issaugoti_rekorda(nariu_skaicius)
            rekordas = nariu_skaicius
            
        # Nustatome boto statusą (Activity)
        statusas = f"Nariai: {nariu_skaicius} | Rekordas: {rekordas}"
        await bot.change_presence(activity=discord.Game(name=statusas))

# Komanda rolių patikrinimui (pvz., !roles @vartotojas)
@bot.command()
async def roles(ctx, member: discord.Member = None):
    member = member or ctx.author
    roles_list = [role.name for role in member.roles if role.name != "@everyone"]
    
    if roles_list:
        atsakymas = f"**{member.display_name}** turi šias roles: " + ", ".join(roles_list)
    else:
        atsakymas = f"**{member.display_name}** neturi jokių rolių."
        
    await ctx.send(atsakymas)

# Saugiai paimame Tokeną iš aplinkos kintamųjų (Railway)
bot.run(os.environ.get("DISCORD_TOKEN"))
