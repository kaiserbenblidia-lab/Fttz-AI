import discord
from discord.ext import commands
from discord import app_commands
import os
from openai import OpenAI

TOKEN = os.environ.get("TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

ai_channels = set()


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("AI Bot Ready")


# ----------- AI RESPONSE -----------
@bot.event
async def on_message(message):

    if message.author.bot:
        return

    if message.channel.id in ai_channels:

        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Always reply in the same language the user used."
                    },
                    {
                        "role": "user",
                        "content": message.content
                    }
                ]
            )

            reply = response.choices[0].message.content

            if len(reply) > 2000:
                reply = reply[:1990]

            await message.reply(reply)

        except Exception as e:
            await message.reply("AI error")

    await bot.process_commands(message)


# ----------- ADD AI CHANNEL -----------
@bot.tree.command(name="add_ai_channel", description="Enable AI in a channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def add_ai_channel(interaction: discord.Interaction, channel: discord.TextChannel):

    ai_channels.add(channel.id)

    await interaction.response.send_message(
        f"AI enabled in {channel.mention}"
    )


# ----------- REMOVE AI CHANNEL -----------
@bot.tree.command(name="remove_ai_channel", description="Disable AI in a channel")
@app_commands.checks.has_permissions(manage_channels=True)
async def remove_ai_channel(interaction: discord.Interaction, channel: discord.TextChannel):

    if channel.id in ai_channels:
        ai_channels.remove(channel.id)

    await interaction.response.send_message(
        f"AI removed from {channel.mention}"
    )


bot.run(TOKEN)
