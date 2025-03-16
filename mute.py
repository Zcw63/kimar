import discord
from discord.ext import commands
import asyncio

TOKEN = "MTM0MTg1MzM2Mzc1ODY5NDQ4MA.G8Whu5.-FB4A_htvtHFGJNEfIuQcm5Y4Lm0grMfhUieiw"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

@bot.command()
@commands.has_permissions(manage_messages=True)  # Vérifie si l'utilisateur peut gérer les messages
async def mute(ctx, user_id: int, reason: str, duration: int):
    try:
        user = ctx.guild.get_member(user_id)  # Récupère l'utilisateur dans le serveur
        if not user:
            await ctx.message.delete()
            return await ctx.send("❌ Utilisateur introuvable sur ce serveur.")

        # Rôle "Muted"
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False))
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(mute_role, send_messages=False)

        # Appliquer le mute
        await user.add_roles(mute_role, reason=reason)

        # Supprime le message de la commande
        await ctx.message.delete()

        # Embed de confirmation
        embed = discord.Embed(title="🔇 Mute", color=discord.Color.red())
        embed.add_field(name="👤 Utilisateur", value=user.mention, inline=False)
        embed.add_field(name="📌 Raison", value=reason, inline=False)
        embed.add_field(name="⏳ Durée", value=f"{duration} minutes", inline=False)
        embed.set_footer(text=f"Sanction appliquée par {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

        # Démute après la durée spécifiée
        await asyncio.sleep(duration * 60)

        # Vérifier si l'utilisateur est toujours dans le serveur avant d'essayer de le unmute
        if mute_role in user.roles:
            await user.remove_roles(mute_role, reason="Mute terminé")
            await ctx.send(f"✅ {user.mention} a été unmuted après {duration} minutes.")

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions nécessaires pour mute cet utilisateur.")
    except discord.HTTPException:
        await ctx.send("❌ Erreur lors de l'exécution de la commande.")

@bot.command()
@commands.has_permissions(manage_messages=True)  # Vérifie si l'utilisateur peut gérer les messages
async def unmute(ctx, user_id: int):
    try:
        user = ctx.guild.get_member(user_id)  # Récupère l'utilisateur
        if not user:
            await ctx.message.delete()
            return await ctx.send("❌ Utilisateur introuvable sur ce serveur.")

        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role or mute_role not in user.roles:
            await ctx.message.delete()
            return await ctx.send(f"❌ {user.mention} n'est pas mute.")

        # Retirer le rôle "Muted"
        await user.remove_roles(mute_role, reason="Unmute manuel")

        # Supprime le message de la commande
        await ctx.message.delete()

        # Embed de confirmation
        embed = discord.Embed(title="🔊 Unmute", color=discord.Color.green())
        embed.add_field(name="👤 Utilisateur", value=user.mention, inline=False)
        embed.set_footer(text=f"Sanction retirée par {ctx.author}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    except discord.Forbidden:
        await ctx.send("❌ Je n'ai pas les permissions nécessaires pour unmute cet utilisateur.")
    except discord.HTTPException:
        await ctx.send("❌ Erreur lors de l'exécution de la commande.")

# Lancement du bot
bot.run(TOKEN)
