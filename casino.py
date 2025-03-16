import discord
from discord.ext import commands
import random
import json
import asyncio
from discord.ext import tasks


# 🔹 CONFIGURATION
TOKEN = "MTM0MTg1MzM2Mzc1ODY5NDQ4MA.G8Whu5.-FB4A_htvtHFGJNEfIuQcm5Y4Lm0grMfhUieiw"
CASINO_CHANNEL_ID = 1343357246310060163 # Remplace avec l'ID du salon casino
GERANT_ROLE_ID = 1347032689294708838  # ID du rôle "Gérant Casino"
DATA_FILE = "casino_data.json"

# 🔹 CHARGER OU CRÉER LE FICHIER JSON
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 🔹 CONFIG BOT
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# 🔹 VÉRIFIER LE SALON
def check_channel(ctx):
    return ctx.channel.id == CASINO_CHANNEL_ID

# 🔹 VÉRIFIER LE COMPTE DU JOUEUR
def check_user(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = 1000  # Début avec 1000 Coins
        save_data(data)
    return data


# 🔹 COMMANDE : !balance
@bot.command()
async def balance(ctx):
    if not check_channel(ctx): return
    data = check_user(ctx.author.id)
    embed = discord.Embed(title="💰 Solde", description=f"Vous avez **{data[str(ctx.author.id)]} Coins**.", color=discord.Color.red())
    await ctx.send(embed=embed)


# 🔹 CLASSES POUR LA ROULETTE (AVEC MENU DÉROULANT)
class RouletteView(discord.ui.View):
    def __init__(self, ctx, mise):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.mise = mise
        self.add_item(RouletteSelect(ctx, mise))

class RouletteSelect(discord.ui.Select):
    def __init__(self, ctx, mise):
        options = [
            discord.SelectOption(label="Parier sur une couleur", description="Rouge ou Noir"),
            discord.SelectOption(label="Parier sur Pair/Impair", description="Pair ou Impair"),
            discord.SelectOption(label="Parier sur un nombre", description="Un nombre entre 0 et 36"),
        ]
        super().__init__(placeholder="Choisissez votre pari", options=options)
        self.ctx = ctx
        self.mise = mise

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Ce n'est pas votre pari !", ephemeral=True)
            return

        choix = self.values[0]

        await interaction.response.send_message(f"Vous avez choisi : **{choix}**. Répondez dans le chat avec votre pari.", ephemeral=True)

        try:
            def check(msg):
                return msg.author == self.ctx.author and msg.channel == self.ctx.channel

            if choix == "Parier sur une couleur":
                await self.ctx.send("🎨 Choisissez une couleur : **Rouge** ou **Noir**.")
                msg = await bot.wait_for("message", check=check, timeout=30)
                pari = msg.content.lower()
                if pari not in ["rouge", "noir"]:
                    await self.ctx.send("❌ Réponse invalide ! Pari annulé.")
                    return
            elif choix == "Parier sur Pair/Impair":
                await self.ctx.send("🔢 Choisissez : **Pair** ou **Impair**.")
                msg = await bot.wait_for("message", check=check, timeout=30)
                pari = msg.content.lower()
                if pari not in ["pair", "impair"]:
                    await self.ctx.send("❌ Réponse invalide ! Pari annulé.")
                    return
            elif choix == "Parier sur un nombre":
                await self.ctx.send("🔢 Entrez un **nombre entre 0 et 36**.")
                msg = await bot.wait_for("message", check=check, timeout=30)
                try:
                    pari = int(msg.content)
                    if pari < 0 or pari > 36:
                        await self.ctx.send("❌ Nombre invalide ! Pari annulé.")
                        return
                except ValueError:
                    await self.ctx.send("❌ Réponse invalide ! Pari annulé.")
                    return

            # 🔹 LANCEMENT DE LA ROULETTE
            await asyncio.sleep(2)
            resultat = random.randint(0, 36)
            couleur = "rouge" if resultat % 2 == 0 else "noir"
            pair_ou_impair = "pair" if resultat % 2 == 0 else "impair"

            # 🔹 GESTION DU GAIN/PERTE
            data = load_data()
            user_id = str(self.ctx.author.id)
            mise = self.mise
            gain = 0

            if choix == "Parier sur une couleur":
                if pari == couleur:
                    gain = mise * 2
            elif choix == "Parier sur Pair/Impair":
                if pari == pair_ou_impair:
                    gain = mise * 2
            elif choix == "Parier sur un nombre":
                if pari == resultat:
                    gain = mise * 35

            if gain > 0:
                data[user_id] += gain
                result_text = f"🎉 **Gagné !** Vous remportez **{gain} Coins**."
            else:
                data[user_id] -= mise
                result_text = f"😢 **Perdu...** Vous perdez **{mise} Coins**."

            save_data(data)

            # 🔹 AFFICHAGE DU RÉSULTAT
            embed = discord.Embed(title="🎰 Résultat de la Roulette", description=result_text, color=discord.Color.green())
            embed.add_field(name="🎯 Numéro tiré :", value=f"**{resultat}** ({couleur})", inline=False)
            embed.set_image(url="attachment://casinomakima.gif")

            await self.ctx.send(file=discord.File("casinomakima.gif"), embed=embed)

        except asyncio.TimeoutError:
            await self.ctx.send("⏳ Temps écoulé ! Pari annulé.")

# 🔹 COMMANDE : !roulette
@bot.command()
async def roulette(ctx, mise: int):
    if not check_channel(ctx): return
    data = check_user(ctx.author.id)

    if mise > data[str(ctx.author.id)] or mise <= 0:
        await ctx.send("❌ Mise invalide ou manque de fond.")
        return

    embed = discord.Embed(title="🎰 Roulette", description="Choisissez votre pari dans le menu déroulant.", color=discord.Color.red())
    embed.set_image(url="attachment://casino.gif")

    await ctx.send(file=discord.File("casino.gif"), embed=embed, view=RouletteView(ctx, mise))

# 🔹 DÉMARRAGE DU BOT
@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")

# 🔹 FONCTION POUR TIRER UNE CARTE
def tirer_carte():
    cartes = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    return random.choice(cartes)

# 🔹 FONCTION POUR CALCULER LE SCORE
def calculer_score(main):
    score = 0
    as_count = 0
    for carte in main:
        if carte in ["J", "Q", "K"]:
            score += 10
        elif carte == "A":
            as_count += 1
            score += 11
        else:
            score += int(carte)
    while score > 21 and as_count:
        score -= 10
        as_count -= 1
    return score

# 🔹 CLASSE POUR LE BLACKJACK
class BlackjackView(discord.ui.View):
    def __init__(self, ctx, mise, joueur_main, bot_main):
        super().__init__(timeout=30)
        self.ctx = ctx
        self.mise = mise
        self.joueur_main = joueur_main
        self.bot_main = bot_main

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Ce n'est pas ton jeu !", ephemeral=True)
            return
        
        self.joueur_main.append(tirer_carte())
        score_joueur = calculer_score(self.joueur_main)
        
        if score_joueur > 21:
            await interaction.response.defer()
            await self.finir_partie("lose")
            return
        
        embed = discord.Embed(title="🃏 Blackjack", description="Vous avez tiré une carte !", color=discord.Color.red())
        embed.add_field(name="Votre main", value=" - ".join(self.joueur_main))
        embed.add_field(name="Score", value=f"**{score_joueur}**")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("Ce n'est pas ton jeu !", ephemeral=True)
            return
        
        await interaction.response.defer()
        await self.finir_partie("stand")

    async def finir_partie(self, resultat):
        data = load_data()
        user_id = str(self.ctx.author.id)
        
        score_joueur = calculer_score(self.joueur_main)
        score_bot = calculer_score(self.bot_main)
        
        if resultat == "lose":
            msg = f"😢 **Perdu...** Vous avez dépassé 21 ! Vous perdez **{self.mise} Coins**."
            data[user_id] -= self.mise
        else:
            while score_bot < 17:
                self.bot_main.append(tirer_carte())
                score_bot = calculer_score(self.bot_main)
            
            if score_bot > 21 or score_joueur > score_bot:
                msg = f"🎉 **Gagné !** Vous remportez **{self.mise * 2} Coins**."
                data[user_id] += self.mise * 2
            elif score_joueur < score_bot:
                msg = f"😢 **Perdu...** Le bot a gagné avec **{score_bot}** ! Vous perdez **{self.mise} Coins**."
                data[user_id] -= self.mise
            else:
                msg = "🤝 **Égalité !** Votre mise est remboursée."
        
        save_data(data)
        
        embed = discord.Embed(title="🃏 Résultat du Blackjack", description=msg, color=discord.Color.red())
        embed.add_field(name="Votre main", value=" - ".join(self.joueur_main), inline=False)
        embed.add_field(name="Score", value=f"**{score_joueur}**", inline=False)
        embed.add_field(name="Main du bot", value=" - ".join(self.bot_main), inline=False)
        embed.add_field(name="Score du bot", value=f"**{score_bot}**", inline=False)
        embed.set_image(url="attachment://makimablackjack.gif")
        
        await self.ctx.send(file=discord.File("makimablackjack.gif"), embed=embed)
        self.stop()

# 🔹 COMMANDE : !blackjack
@bot.command()
async def blackjack(ctx, mise: int):
    if not check_channel(ctx): return
    data = check_user(ctx.author.id)
    if mise > data[str(ctx.author.id)] or mise <= 0:
        await ctx.send("❌ Mise invalide ou manque de fond.")
        return
    joueur_main = [tirer_carte(), tirer_carte()]
    bot_main = [tirer_carte(), tirer_carte()]
    embed = discord.Embed(title="🃏 Blackjack", description="Choisissez **Hit** pour tirer une carte ou **Stand** pour rester.", color=discord.Color.red())
    embed.add_field(name="Votre main", value=" - ".join(joueur_main))
    embed.add_field(name="Score", value=f"**{calculer_score(joueur_main)}**")
    embed.set_image(url="attachment://blackjack.gif")
    await ctx.send(file=discord.File("blackjack.gif"), embed=embed, view=BlackjackView(ctx, mise, joueur_main, bot_main))

# 🔹 COMMANDE : !addcoins (Gérant Casino)
@bot.command()
@commands.has_role(GERANT_ROLE_ID)
async def addcoins(ctx, user: discord.Member, montant: int):
    data = check_user(user.id)
    data[str(user.id)] += montant
    save_data(data)
    await ctx.send(f"✅ Ajouté **{montant} Coins** à {user.mention}.")


# 🔹 COMMANDE : !removecoins (Gérant Casino)
@bot.command()
@commands.has_role(GERANT_ROLE_ID)
async def removecoins(ctx, user: discord.Member, montant: int):
    data = check_user(user.id)
    data[str(user.id)] = max(0, data[str(user.id)] - montant)
    save_data(data)
    await ctx.send(f"❌ Retiré **{montant} Coins** à {user.mention}.")

# 🔹 COMMANDE : !resetcoins (Gérant Casino
@bot.command()
@commands.has_role(GERANT_ROLE_ID)
async def resetcoins(ctx, user: discord.Member):
    data = check_user(user.id)
    data[str(user.id)] = 1000
    save_data(data)
    await ctx.send(f"🔄 Réinitialisé le solde de {user.mention} à **1000 Coins**.")

# 🔹 COMMANDE : !topcasino
@bot.command()
async def top(ctx):
    data = load_data()
    top = sorted(data.items(), key=lambda x: x[1], reverse=True)[:20]  # Top 20

    embed = discord.Embed(title="🏆 **Classement Casino**", color=discord.Color.gold())
    embed.set_image(url="attachment://topcasino.gif")  # Ajout du GIF

    leaderboard = "\n".join([f"**{i+1}. <@{player[0]}>** - {player[1]} Coins" for i, player in enumerate(top)])
    embed.description = leaderboard or "Aucun joueur classé."

    file = discord.File("topcasino.gif", filename="topcasino.gif")
    await ctx.send(embed=embed, file=file)

# 🔹 ERREUR : MISSING ROLE
@addcoins.error
@removecoins.error
@resetcoins.error
async def missing_role(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("❌ Vous n'avez pas la permission d'utiliser cette commande.")

# 🏆 Gain automatique toutes les 20 minutes en vocal
@tasks.loop(minutes=20)
async def reward_voice_users():
    guild = bot.get_guild(CASINO_CHANNEL_ID)
    if not guild:
        return

    for vc in guild.voice_channels:
        for member in vc.members:
            if not member.bot:
                data = check_user(member.id)
                data[str(member.id)] += 500
                save_data(data)
                print(f"✅ 500 coins ajoutés à {member.name}")
        



bot.run(TOKEN)