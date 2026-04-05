import discord
from discord.ext import commands
from discord import app_commands
import os
import random
import time
import openai

TOKEN = os.environ.get("TOKEN")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_KEY

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

ai_channels = set()
level_channels = set()

user_xp = {}
last_message = {}
xp_cooldown = 30


# ---------- READY ----------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print("Bot Ready")


# ---------- AI CHAT ----------
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id in ai_channels:

        response = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "reply in the same language the user used"},
                {"role": "user", "content": message.content}
            ]
        )

        reply = response.choices[0].message.content
        await message.reply(reply)

    # LEVEL SYSTEM
    if message.channel.id in level_channels:

        user = message.author.id
        now = time.time()

        if user not in last_message or now - last_message[user] > xp_cooldown:

            xp = random.randint(5, 15)

            user_xp[user] = user_xp.get(user, 0) + xp
            last_message[user] = now

            level = int(user_xp[user] ** 0.5)

            if user_xp[user] % 100 < 15:
                await message.channel.send(
                    f"{message.author.mention} leveled up! Level {level}"
                )

    await bot.process_commands(message)


# ---------- AI CHANNEL ----------
@bot.tree.command(name="add_ai_channel")
async def add_ai_channel(interaction: discord.Interaction, channel: discord.TextChannel):

    if not interaction.user.guild_permissions.manage_channels:
        return await interaction.response.send_message("No permission", ephemeral=True)

    ai_channels.add(channel.id)

    await interaction.response.send_message("AI activated in channel")


@bot.tree.command(name="remove_ai_channel")
async def remove_ai_channel(interaction: discord.Interaction, channel: discord.TextChannel):

    ai_channels.discard(channel.id)

    await interaction.response.send_message("AI removed from channel")


# ---------- WARN ----------
@bot.tree.command(name="warn")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("No permission", ephemeral=True)

    await interaction.response.send_message(f"{member.mention} warned: {reason}")


# ---------- LEVEL ----------
@bot.tree.command(name="add_level_channel")
async def add_level_channel(interaction: discord.Interaction, channel: discord.TextChannel):

    level_channels.add(channel.id)

    await interaction.response.send_message("Level system activated")


@bot.tree.command(name="remove_level")
async def remove_level(interaction: discord.Interaction):

    level_channels.clear()

    await interaction.response.send_message("Level system removed")


@bot.tree.command(name="edit_exp_time")
async def edit_exp_time(interaction: discord.Interaction, seconds: int):

    global xp_cooldown
    xp_cooldown = seconds

    await interaction.response.send_message(f"XP cooldown set to {seconds}")


# ---------- RANDOM IDEA ----------
ideas = [
    "Create a Discord server about gaming",
    "Start a YouTube channel",
    "Make a mini game bot",
    "Create a meme page",
    "Start learning programming"
]


@bot.tree.command(name="give_me_idea")
async def give_me_idea(interaction: discord.Interaction):

    await interaction.response.send_message(random.choice(ideas))


# ---------- GAME ROCK PAPER SCISSORS ----------
@bot.tree.command(name="games")
async def games(interaction: discord.Interaction, choice: str):

    options = ["rock", "paper", "scissors"]
    bot_choice = random.choice(options)

    if choice not in options:
        return await interaction.response.send_message("choose rock/paper/scissors")

    if choice == bot_choice:
        result = "Draw"

    elif (choice == "rock" and bot_choice == "scissors") or \
         (choice == "paper" and bot_choice == "rock") or \
         (choice == "scissors" and bot_choice == "paper"):

        result = "You win"

    else:
        result = "Bot wins"

    await interaction.response.send_message(
        f"You: {choice}\nBot: {bot_choice}\n{result}"
    )


bot.run(TOKEN)
