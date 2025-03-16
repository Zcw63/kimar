import discord
from discord.ext import commands
from discord.ui import Button, View
import random
from datetime import datetime, timedelta

TOKEN = "MTM0MTg1MzM2Mzc1ODY5NDQ4MA.G8Whu5.-FB4A_htvtHFGJNEfIuQcm5Y4Lm0grMfhUieiw"  # Remplace par ton token
GUILD_ID = 1341082844054687815  # ID du serveur
GIVEAWAY_CHANNEL_ID = 1342071005816029235  # ID du salon où lancer le giveaway
AUTHORIZED_ROLE_ID = 1341187919872000113  # Remplace par l'ID du rôle autorisé

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Permet de voir qui est en vocal

bot = commands.Bot(command_prefix="!", intents=intents)

class GiveawayButton(View):
    def __init__(self, end_time):
        super().__init__(timeout=None)
        self.participants = []
        self.end_time = end_time

    @discord.ui.button(label="🍷 Participer", style=discord.ButtonStyle.green, custom_id="join_giveaway")
    async def join_giveaway(self, interaction: discord.Interaction, button: Button):
        user = interaction.user

        # Vérifier si l'utilisateur est connecté dans un salon vocal
        if user.voice and user.voice.channel:
            if user.id not in self.participants:
                self.participants.append(user.id)
                await interaction.response.send_message("✅ Participation enregistrée !", ephemeral=True)
            else:
                await interaction.response.send_message("⚠️ Tu es déjà inscrit au giveaway !", ephemeral=True)

            # Mettre à jour le message du giveaway
            embed = interaction.message.embeds[0]
            embed.set_field_at(0, name=" Participants :", value=f"{len(self.participants)}", inline=True)
            await interaction.message.edit(embed=embed, view=self)
        else:
            await interaction.response.send_message("❌ Tu dois être connecté dans **un salon vocal** pour participer !", ephemeral=True)

async def end_giveaway(message, view):
    await discord.utils.sleep_until(view.end_time)

    if view.participants:
        winner_id = random.choice(view.participants)
        winner = message.guild.get_member(winner_id)
        await message.channel.send(f"🎉 Félicitations {winner.mention} ! Tu as gagné le Nitro ! 🚀")
    else:
        await message.channel.send("❌ Personne n'a participé, aucun gagnant.")

@bot.command()
async def giveawaynitro(ctx):
    """Lance un giveaway Nitro avec un créneau de 2h"""

    # Vérification du rôle avant d'exécuter la commande
    role = discord.utils.get(ctx.guild.roles, id=AUTHORIZED_ROLE_ID)
    if role not in ctx.author.roles:
        await ctx.send("❌ **Tu n'as pas la permission d'utiliser cette commande !**")
        return

    now = datetime.now()
    end_time = now + timedelta(hours=2)  # Fin dans 2 heures
    formatted_time = now.strftime("%Hh")  # Heure actuelle
    formatted_end_time = end_time.strftime("%Hh")  # Heure de fin

    embed = discord.Embed(
        title="🎉 Giveaway Nitro Boost !",
        description=(
            f"@everyone\n"
            f"Appuie sur le bouton pour participer !\n"
            f"⚠️ **Condition :** Être connecté dans **n'importe quel salon vocal**\n"
            f"🕒 **Heure requise :** Entre {formatted_time} et {formatted_end_time}"
        ),
        color=discord.Color.pink()
    )
    embed.set_footer(text="Le gagnant sera tiré au sort automatiquement après la fin du giveaway. L'équipe Kima")
    embed.add_field(name="🍷 Participants :", value="0", inline=True)

    view = GiveawayButton(end_time)
    message = await ctx.send(content="@everyone 🎁", embed=embed, view=view)
    await end_giveaway(message, view)

bot.run(TOKEN)

