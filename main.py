import discord
from discord.ext import commands
from discord import app_commands
import anthropic
import random
import asyncio
import os

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         إعدادات البوت
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DISCORD_TOKEN = os.environ.get("TOKEN")
ANTHROPIC_API_KEY = os.environ.get("anthropic")

# شخصية البوت
BOT_PERSONALITY = """أنت مساعد ذكاء اصطناعي اسمك "Fttz AI" في سيرفر ديسكورد.
- تتكلم بأي لغة يتكلمها المستخدم تلقائياً
- شخصيتك ودودة، مرحة، وذكية
- تساعد بالأسئلة، الألعاب، والترفيه
- ردودك مختصرة ومفيدة (مو طويلة جداً)
- تستخدم إيموجي أحياناً لتكون أكثر حيوية
- إذا تكلم المستخدم عربي ترد عربي، إنجليزي ترد إنجليزي، وهكذا"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
client_ai = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# سجل المحادثات (لكل مستخدم)
conversation_history = {}

# القنوات اللي فيها AI شغال (guild_id -> set of channel_ids)
ai_channels: dict[int, set] = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         دوال مساعدة
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_ai_response(user_id: int, user_message: str) -> str:
    """يحصل على رد من Claude AI مع سجل المحادثة"""
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    # إضافة رسالة المستخدم
    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    # نحافظ على آخر 10 رسائل فقط
    if len(conversation_history[user_id]) > 20:
        conversation_history[user_id] = conversation_history[user_id][-20:]
    
    response = client_ai.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=BOT_PERSONALITY,
        messages=conversation_history[user_id]
    )
    
    assistant_reply = response.content[0].text
    
    # إضافة رد البوت للسجل
    conversation_history[user_id].append({
        "role": "assistant",
        "content": assistant_reply
    })
    
    return assistant_reply

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         أحداث البوت
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.event
async def on_ready():
    print(f"✅ {bot.user} شغال!")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🤖 Fttz AI | /help"
        )
    )
    try:
        synced = await bot.tree.sync()
        print(f"✅ تم مزامنة {len(synced)} أوامر Slash")
    except Exception as e:
        print(f"❌ خطأ في المزامنة: {e}")

@bot.event
async def on_member_join(member):
    """ترحيب بالأعضاء الجدد"""
    channel = discord.utils.get(member.guild.text_channels, name="عام")
    if not channel:
        channel = member.guild.system_channel
    
    if channel:
        embed = discord.Embed(
            title="👋 عضو جديد!",
            description=f"أهلاً {member.mention} في السيرفر! 🎉\nأنا **Fttz AI**، اسألني أي شيء! استخدم `/ask`",
            color=0x00ff88
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    """يرد على المنشن أو الرسائل المباشرة أو القنوات اللي فيها AI"""
    if message.author.bot:
        return

    guild_id = message.guild.id if message.guild else None
    channel_id = message.channel.id

    # رد في قنوات AI على كل رسالة
    if guild_id and guild_id in ai_channels and channel_id in ai_channels[guild_id]:
        async with message.channel.typing():
            response = get_ai_response(message.author.id, message.content)
        await message.reply(response)
        await bot.process_commands(message)
        return

    # رد عند المنشن
    if bot.user in message.mentions:
        user_msg = message.content.replace(f"<@{bot.user.id}>", "").strip()
        if not user_msg:
            user_msg = "مرحبا، قدم نفسك"
        
        async with message.channel.typing():
            response = get_ai_response(message.author.id, user_msg)
        
        await message.reply(response)
    
    # رسائل خاصة (DM)
    elif isinstance(message.channel, discord.DMChannel):
        async with message.channel.typing():
            response = get_ai_response(message.author.id, message.content)
        await message.channel.send(response)
    
    await bot.process_commands(message)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#         أوامر Slash
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@bot.tree.command(name="ask", description="اسأل Fttz AI أي سؤال")
@app_commands.describe(question="سؤالك هنا")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    
    response = get_ai_response(interaction.user.id, question)
    
    embed = discord.Embed(
        description=response,
        color=0x5865F2
    )
    embed.set_author(
        name=f"Fttz AI يرد على {interaction.user.display_name}",
        icon_url=bot.user.display_avatar.url
    )
    embed.set_footer(text=f"❓ {question[:80]}...")
    
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="clear_memory", description="امسح سجل محادثتك مع البوت")
async def clear_memory(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in conversation_history:
        conversation_history.pop(user_id)
    await interaction.response.send_message("🧹 تم مسح سجل محادثتك!", ephemeral=True)

@bot.tree.command(name="roast", description="خلّي Fttz AI يطقطق عليك 😂")
@app_commands.describe(target="من تبغى يطقطق عليه؟")
async def roast(interaction: discord.Interaction, target: discord.Member = None):
    await interaction.response.defer()
    
    person = target.display_name if target else interaction.user.display_name
    prompt = f"اطقطق على شخص اسمه {person} بشكل مضحك وخفيف، جملتين بس"
    
    response = get_ai_response(interaction.user.id, prompt)
    await interaction.followup.send(f"🔥 {response}")

@bot.tree.command(name="trivia", description="سؤال ثقافي عشوائي")
@app_commands.describe(topic="موضوع السؤال (اختياري)")
async def trivia(interaction: discord.Interaction, topic: str = "عام"):
    await interaction.response.defer()
    
    prompt = f"اعطني سؤال ثقافي عشوائي عن موضوع '{topic}' مع 4 خيارات (أ، ب، ج، د) والجواب الصح في الأخير. اكتبه بشكل جميل."
    response = get_ai_response(interaction.user.id, prompt)
    
    embed = discord.Embed(
        title="🧠 سؤال ثقافي",
        description=response,
        color=0xFFD700
    )
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="story", description="Fttz AI يحكيلك قصة")
@app_commands.describe(theme="موضوع القصة")
async def story(interaction: discord.Interaction, theme: str = "مغامرة"):
    await interaction.response.defer()
    
    prompt = f"احكيلي قصة قصيرة ومشوقة عن موضوع: {theme}. ٣-٤ جمل بس."
    response = get_ai_response(interaction.user.id, prompt)
    
    embed = discord.Embed(
        title=f"📖 قصة: {theme}",
        description=response,
        color=0x9B59B6
    )
    await interaction.followup.send(embed=embed)

@bot.tree.command(name="joke", description="نكتة من Fttz AI")
async def joke(interaction: discord.Interaction):
    await interaction.response.defer()
    
    prompt = "قلي نكتة مضحكة خفيفة"
    response = get_ai_response(interaction.user.id, prompt)
    await interaction.followup.send(f"😂 {response}")

@bot.tree.command(name="add_ai_to_channel", description="فعّل Fttz AI في قناة معينة يرد على كل رسالة [للأدمن فقط]")
@app_commands.describe(channel="اختر القناة اللي تبغى البوت يشتغل فيها")
@app_commands.checks.has_permissions(administrator=True)
async def add_ai_to_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild.id

    if guild_id not in ai_channels:
        ai_channels[guild_id] = set()

    if channel.id in ai_channels[guild_id]:
        await interaction.response.send_message(
            f"⚠️ البوت شغال أصلاً في {channel.mention}!", ephemeral=True
        )
        return

    ai_channels[guild_id].add(channel.id)

    embed = discord.Embed(
        title="✅ تم تفعيل Fttz AI",
        description=f"الآن البوت يرد على **كل رسالة** في {channel.mention} 🤖\nلإيقافه استخدم `/remove_ai_from_channel`",
        color=0x00ff88
    )
    await interaction.response.send_message(embed=embed)

    # إرسال رسالة ترحيب في القناة
    await channel.send(f"🤖 **Fttz AI** الآن شغال هنا! تكلموني بأي لغة وأرد عليكم 👋")

@add_ai_to_channel.error
async def add_ai_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ هذا الأمر للأدمن فقط!", ephemeral=True)

@bot.tree.command(name="remove_ai_from_channel", description="أوقف Fttz AI في قناة معينة [للأدمن فقط]")
@app_commands.describe(channel="اختر القناة اللي تبغى توقف البوت فيها")
@app_commands.checks.has_permissions(administrator=True)
async def remove_ai_from_channel(interaction: discord.Interaction, channel: discord.TextChannel):
    guild_id = interaction.guild.id

    if guild_id not in ai_channels or channel.id not in ai_channels[guild_id]:
        await interaction.response.send_message(
            f"⚠️ البوت مو شغال في {channel.mention} أصلاً!", ephemeral=True
        )
        return

    ai_channels[guild_id].discard(channel.id)

    embed = discord.Embed(
        title="🔴 تم إيقاف Fttz AI",
        description=f"البوت توقف عن الرد في {channel.mention}",
        color=0xFF4444
    )
    await interaction.response.send_message(embed=embed)

@remove_ai_from_channel.error
async def remove_ai_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ هذا الأمر للأدمن فقط!", ephemeral=True)

@bot.tree.command(name="list_ai_channels", description="شوف القنوات اللي فيها AI شغال")
async def list_ai_channels(interaction: discord.Interaction):
    guild_id = interaction.guild.id

    if guild_id not in ai_channels or not ai_channels[guild_id]:
        await interaction.response.send_message("📭 ما في أي قناة فيها AI شغال حالياً.", ephemeral=True)
        return

    channels_list = "\n".join(
        [f"• <#{cid}>" for cid in ai_channels[guild_id]]
    )
    embed = discord.Embed(
        title="📡 قنوات AI الشغالة",
        description=channels_list,
        color=0x5865F2
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def help_cmd(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Fttz AI - قائمة الأوامر",
        color=0x00ff88
    )
    
    commands_list = {
        "/ask [سؤال]": "اسأل البوت أي شيء 💬",
        "/add_ai_to_channel [قناة]": "فعّل AI في قناة يرد على الكل 🤖 (أدمن)",
        "/remove_ai_from_channel [قناة]": "أوقف AI في قناة 🔴 (أدمن)",
        "/list_ai_channels": "شوف القنوات اللي فيها AI 📡",
        "/roast [@شخص]": "طقطقة مضحكة 🔥",
        "/trivia [موضوع]": "سؤال ثقافي 🧠",
        "/story [موضوع]": "قصة قصيرة 📖",
        "/joke": "نكتة مضحكة 😂",
        "/clear_memory": "مسح سجل المحادثة 🧹",
        "@Fttz AI [رسالة]": "كلمه مباشرة في أي قناة 💬",
    }
    
    for cmd, desc in commands_list.items():
        embed.add_field(name=cmd, value=desc, inline=False)
    
    embed.set_footer(text="Fttz AI • يتكلم كل اللغات 🌍")
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

bot.run(DISCORD_TOKEN)
