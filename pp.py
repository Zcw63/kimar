import discord
from discord.ext import commands

# Remplace par ton token de bot
TOKEN = "MTM0MTg1MzM2Mzc1ODY5NDQ4MA.G8Whu5.-FB4A_htvtHFGJNEfIuQcm5Y4Lm0grMfhUieiw"

# Définition des intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.command()
async def pp(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)  # Récupère l'utilisateur via son ID
        avatar_url = user.avatar.url if user.avatar else user.default_avatar.url  # Prend l'avatar ou l'avatar par défaut

        embed = discord.Embed(title=f"📷 Avatar de {user.name}", color=discord.Color.blue())
        embed.set_image(url=avatar_url)  # Affiche l'avatar en grand
        embed.set_footer(text=f"Demandé par {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    except discord.NotFound:
        await ctx.send("❌ Utilisateur introuvable. Vérifie l'ID.")
    except discord.HTTPException:
        await ctx.send("❌ Erreur lors de la récupération de l'avatar.")

# Lancement du bot
bot.run(TOKEN)

