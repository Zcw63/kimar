import discord

token = "MTM0MTg1MzM2Mzc1ODY5NDQ4MA.G8Whu5.-FB4A_htvtHFGJNEfIuQcm5Y4Lm0grMfhUieiw"

client = discord.Client(intents=discord.Intents.all())

client.run(token=token)