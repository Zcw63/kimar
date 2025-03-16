import discord
from discord.ext import commands

# Remplace par ton token de bot
TOKEN = "MTM0MTg1MzM2Mzc1ODY5NDQ4MA.G8Whu5.-FB4A_htvtHFGJNEfIuQcm5Y4Lm0grMfhUieiw"

# Définition des intents (avec Message Content activé)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.command()
async def dance(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)  # Récupère l'utilisateur via son ID
        file = discord.File("kimadance.gif", filename="kimadance.gif")  # Charge le fichier GIF

        embed = discord.Embed(
            title="💃 Danse Offerte !",
            description=f"💝 {ctx.author.mention} offre une danse spéciale ! 🎶",
            color=discord.Color.red()  # Couleur rouge
        )
        embed.set_image(url="attachment://kimadance.gif")  # Affiche le GIF en grand
        embed.set_footer(text="Profite bien de la danse ! 💃🔥")

        # Supprime le message de commande après 1 seconde
        await ctx.message.delete(delay=1)

        # Envoie d'abord la mention, puis l'embed avec le fichier
        await ctx.send(f"{user.mention} 🎁 Tu as reçu une danse ! 💃", embed=embed, file=file)

    except discord.NotFound:
        await ctx.send("❌ Utilisateur introuvable. Vérifie l'ID.")
    except discord.HTTPException:
        await ctx.send("❌ Erreur lors de l'envoi de la danse.")

# Lancement du bot
bot.run(TOKEN)

