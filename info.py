import discord
from discord.ext import commands

TOKEN = "MTM0MTg1MzM2Mzc1ODY5NDQ4MA.G8Whu5.-FB4A_htvtHFGJNEfIuQcm5Y4Lm0grMfhUieiw"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def info(ctx, user_id: int):
    # Récupérer l'utilisateur via son ID
    user = ctx.guild.get_member(user_id)
    
    if user is None:
        await ctx.send("❌ Utilisateur introuvable. Assurez-vous que l'ID est correct et que l'utilisateur est sur le serveur.")
        return
    
    embed = discord.Embed(title=f"Informations sur {user.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="🆔 ID", value=user.id, inline=False)
    embed.add_field(name="🍷 Nom d'affichage", value=user.display_name, inline=False)
    embed.add_field(name="📅 Compte créé le", value=user.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="📆 A rejoint le serveur le", value=user.joined_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
    embed.add_field(name="🎭 Rôles", value=", ".join([role.name for role in user.roles if role.name != "@everyone"]) or "Aucun rôle", inline=False)
    embed.add_field(name="🤖 Bot", value="Oui" if user.bot else "Non", inline=False)
    
    await ctx.send(embed=embed)

bot.run(TOKEN)