import requests
import datetime
import pytz
import re
import discord
import json
from discord.ext import commands, tasks

token = ""  # Bot login
twitch_url = "http://twitch.tv/BotParArtem_:p_DoncNonPasDeChaineTwitch_:)"  # Just the twitch login

# Bot prefix & command remover, bit useless for the moment
bot = commands.Bot(command_prefix='.')
bot.remove_command('help')


# Scrape Every x seconds (default 600=10minutes)
@tasks.loop(seconds=600)
async def refresh():
    voice_channel = bot.get_channel(911022551214460958)  # Voice Channel ID
    hour_voice_channel = bot.get_channel(920415119706587147)  # Voice Channel ID
    with open("db.json") as f:
        data = json.load(f)

    statspage = requests.get("https://www.funcraft.net/fr/jeux").text
    if "game-icon game-bg-infected game-border-infected" in statspage:
        infectedplayers = re.findall(
            'Infect&eacute;  </h3> <div class="game-status">(.+?)<', statspage  # False warning
        )[0].replace(" joueurs", "")
    else:
        infectedplayers = None
    country_time_zone = pytz.timezone('Europe/Paris')  # Getting France timezone for VPSes with bad hour
    today = datetime.datetime.now(country_time_zone)
    date_time = today.strftime("%H:%M")
    if infectedplayers is None:
        print(f"[LOG {date_time}] ? Joueurs en-ligne ! | Keeping the old value: {data['infected']['before']}")
        with open("db.json") as f:
            data = json.load(f)
        await voice_channel.edit(name=f"〔 ~{data['infected']['before']} 〕joueurs en jeu")
    else:
        print(f"[LOG {date_time}] {infectedplayers} Joueurs en-ligne !")
        data['infected']['before'] = infectedplayers
        with open("db.json", "w") as f:
            json.dump(data, f, indent=4)
        await voice_channel.edit(name=f"〔 {infectedplayers} 〕joueurs en jeu")
        await hour_voice_channel.edit(name=f"〔 {date_time} 〕Heure de MAJ")


@tasks.loop(seconds=3600)
async def ping():
    country_time_zone = pytz.timezone('Europe/Paris')
    today = datetime.datetime.now(country_time_zone)
    date_time = today.strftime("%H:%M:%S")
    ping_channel = bot.get_channel(875740660983021578)
    with open("db.json") as f:
        data = json.load(f)
    players = int(data['infected']['before'])
    if players >= 30:
        print(f"[LOG {date_time}]Plus de 30 joueurs, pinging...")
        embed = discord.Embed(color=16711680)
        embed.add_field(name="Notification - 30+ joueurs",
                        value=f"*Il y a actuellement plus de 30 joueurs en infected*\nJoueurs en-ligne: **{data['infected']['before']}**.",
                        inline=False)
        embed.set_footer(text="Taverne Bot", icon_url="https://i.pinimg.com/originals/ac/65/8a"
                                                      "/ac658a2c0bc1117c6d547170b23dec72.jpg")
        await ping_channel.send("<@&904097505468362844>", embed=embed)  #send the ping


@bot.event
async def on_ready():
    country_time_zone = pytz.timezone('Europe/Paris')  # Wanted timezone
    today = datetime.datetime.now(country_time_zone)
    date_time = today.strftime("%H:%M:%S")
    print(f"[LOG {date_time}] Le bot {bot.user.name} s'est démarré avec succès.")
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Streaming(name=f"{bot.user.name} | v0.1 b3 Beta", url=twitch_url))
    print(f"[LOG {date_time}]Démarrage du détecteur de joueurs")
    refresh.start()
    print(f"[LOG {date_time}]Démarrage de l'auto pinger")
    ping.start()


bot.run(token)
