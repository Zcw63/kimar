import discord
from discord.ext import commands
from discord.ui import View, Button, Select

TOKEN = "MTM0MTg1MzM2Mzc1ODY5NDQ4MA.G8Whu5.-FB4A_htvtHFGJNEfIuQcm5Y4Lm0grMfhUieiw"

# Configuration des catégories et des rôles associés
TICKET_CATEGORIES = {
    "Besoin d'aide": {"category_id": 1342077190883250206, "role_id": 1341911575354933330},
    "Candidature Staff": {"category_id": 1342076243897483295, "role_id": 1342080451333980221},
    "Candidature Event": {"category_id": 1342076298750726144, "role_id": 1342080579432091810},
    "Community Manager": {"category_id": 1342076156664352849, "role_id": 1342080668674297874},
    "Plainte Staff": {"category_id": 1342077230460960869, "role_id": 1342081118836363294}
}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Commande pour envoyer le message de ticket
@bot.command()
async def ticket(ctx):
    embed = discord.Embed(
        title="📩 Ouvrir un Ticket",
        description="Sélectionnez une catégorie pour ouvrir un ticket.",
        color=discord.Color.orange()
    )
    
    # Charger l'image fournie par l'utilisateur
    file = discord.File("kima_assistance.jpg", filename="kima_assistance.jpg")
    embed.set_image(url="attachment://kima_assistance.jpg")

    view = TicketView()
    await ctx.send(embed=embed, file=file, view=view)

# Vue contenant le menu de sélection
class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

# Sélecteur de catégories de tickets
class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=category, description=f"Ouvrir un ticket pour {category}") 
            for category in TICKET_CATEGORIES.keys()
        ]
        super().__init__(placeholder="Choisissez une catégorie", options=options)

    async def callback(self, interaction: discord.Interaction):
        category_name = self.values[0]
        guild = interaction.guild
        category_info = TICKET_CATEGORIES[category_name]
        category = guild.get_channel(category_info["category_id"])
        role = guild.get_role(category_info["role_id"])

        # Vérifier si un ticket est déjà ouvert
        for channel in category.text_channels:
            if channel.topic == f"Ticket de {interaction.user.id}":
                await interaction.response.send_message("❌ Vous avez déjà un ticket ouvert.", ephemeral=True)
                return

        # Création du salon privé
        ticket_channel = await category.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            topic=f"Ticket de {interaction.user.id}",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, attach_files=True, embed_links=True),
                role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
            }
        )

        # Embed de confirmation
        embed = discord.Embed(
            title=f"🎫 Ticket {category_name}",
            description="Un membre du staff vous répondra bientôt.\nCliquez sur le bouton ci-dessous pour fermer le ticket.",
            color=discord.Color.green()
        )
        embed.set_footer(text="Merci d'utiliser le support.")
        
        view = CloseTicketView()
        await ticket_channel.send(content=interaction.user.mention, embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket ouvert : {ticket_channel.mention}", ephemeral=True)

# Bouton pour fermer un ticket
class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CloseTicketButton())

class CloseTicketButton(Button):
    def __init__(self):
        super().__init__(label="Fermer le Ticket", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("🔒 Fermeture du ticket dans 5 secondes...", ephemeral=True)
        await interaction.channel.send("🔒 Ce ticket sera fermé...")
        await discord.utils.sleep_until(discord.utils.utcnow() + discord.timedelta(seconds=5))
        await interaction.channel.delete()

# Lancement du bot
bot.run(TOKEN)
