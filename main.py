import discord
from discord.ext import commands
import anthropic
import random
import asyncio

# ===================== CONFIG =====================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY_HERE"

# ===================== SETUP =====================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ===================== ACTIVE GAMES =====================
xo_games = {}       # channel_id -> game state
rps_games = {}      # channel_id -> game state
rpc_games = {}      # channel_id -> حجر ورقة مقص

# ==================== COLORS ====================
COLOR_MAIN   = 0x5865F2
COLOR_WIN    = 0x57F287
COLOR_LOSE   = 0xED4245
COLOR_DRAW   = 0xFEE75C
COLOR_IDEA   = 0xEB459E

# ===================== EVENTS =====================
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.playing,
        name="!help | Powered by AI"
    ))

# ===================== HELP =====================
@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(
        title="🤖 Bot Commands",
        description="Here's everything I can do!",
        color=COLOR_MAIN
    )
    embed.add_field(name="💡 Ideas", value=(
        "`!idea` — Get a random idea (English)\n"
        "`!فكرة` — احصل على فكرة عشوائية (عربي)\n"
        "`!ideas <n>` — Get multiple ideas (max 5)"
    ), inline=False)
    embed.add_field(name="🎮 Games", value=(
        "`!xo [@user]` — Play Tic-Tac-Toe\n"
        "`!rps [@user]` — Rock Paper Scissors\n"
        "`!حجر [@user]` — حجر ورقة مقص"
    ), inline=False)
    embed.add_field(name="🔧 Other", value=(
        "`!translate <text>` — Translate to Arabic\n"
        "`!ترجمة <text>` — Translate to English\n"
        "`!help` — Show this menu"
    ), inline=False)
    embed.set_footer(text="Powered by Claude AI • 10,000+ Ideas!")
    await ctx.send(embed=embed)

# ===================== IDEAS (ENGLISH) =====================
@bot.command(name="idea")
async def idea_english(ctx):
    async with ctx.typing():
        category = random.choice([
            "tech startup", "mobile app", "social platform", "game",
            "browser extension", "AI tool", "Discord bot", "website",
            "productivity tool", "creative project", "hardware gadget",
            "educational platform", "health & fitness app", "finance tool",
            "art project", "music app", "environmental solution",
            "community platform", "automation script", "SaaS product"
        ])
        prompt = (
            f"Give me ONE unique, creative, and detailed {category} idea. "
            f"Make it genuinely interesting and different from common ideas. "
            f"Format:\n**Idea Name:** [name]\n**Category:** {category}\n"
            f"**Description:** [2-3 sentence description]\n"
            f"**Why it's cool:** [one sentence]\n"
            f"Be creative and think outside the box!"
        )
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            idea_text = msg.content[0].text
            embed = discord.Embed(
                title="💡 Random Idea",
                description=idea_text,
                color=COLOR_IDEA
            )
            embed.set_footer(text=f"Requested by {ctx.author.display_name} • Try !فكرة for Arabic")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error generating idea: {e}")

# ===================== IDEAS (ARABIC) =====================
@bot.command(name="فكرة")
async def idea_arabic(ctx):
    async with ctx.typing():
        category = random.choice([
            "تطبيق موبايل", "منصة اجتماعية", "لعبة", "أداة ذكاء اصطناعي",
            "بوت ديسكورد", "موقع إلكتروني", "أداة إنتاجية", "مشروع إبداعي",
            "منصة تعليمية", "تطبيق صحة ولياقة", "أداة مالية", "مشروع فني",
            "تطبيق موسيقى", "حل بيئي", "منصة مجتمعية", "مشروع برمجي",
            "متجر إلكتروني", "منصة ألعاب", "أداة تسويق", "خدمة اشتراك"
        ])
        prompt = (
            f"أعطني فكرة واحدة مميزة وإبداعية في مجال: {category}. "
            f"اجعلها مثيرة للاهتمام وغير مكررة. "
            f"الصيغة:\n**اسم الفكرة:** [الاسم]\n**المجال:** {category}\n"
            f"**الوصف:** [2-3 جمل وصفية]\n"
            f"**لماذا هي رائعة:** [جملة واحدة]\n"
            f"كن مبدعاً وفكر خارج الصندوق! أجب بالعربية فقط."
        )
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )
            idea_text = msg.content[0].text
            embed = discord.Embed(
                title="💡 فكرة عشوائية",
                description=idea_text,
                color=COLOR_IDEA
            )
            embed.set_footer(text=f"طلب بواسطة {ctx.author.display_name} • جرب !idea للإنجليزية")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ خطأ في توليد الفكرة: {e}")

# ===================== MULTIPLE IDEAS =====================
@bot.command(name="ideas")
async def ideas_multi(ctx, count: int = 3):
    count = min(max(count, 1), 5)
    async with ctx.typing():
        prompt = (
            f"Give me {count} completely different and unique creative project ideas. "
            f"Each idea should be from a different category. "
            f"Number them 1 to {count}. Be concise but interesting. "
            f"Format each as: **[number]. [Idea Name]** - [one sentence description]"
        )
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}]
            )
            ideas_text = msg.content[0].text
            embed = discord.Embed(
                title=f"💡 {count} Random Ideas",
                description=ideas_text,
                color=COLOR_IDEA
            )
            embed.set_footer(text="Powered by Claude AI")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {e}")

# ===================== TRANSLATE =====================
@bot.command(name="translate")
async def translate_to_arabic(ctx, *, text: str):
    async with ctx.typing():
        prompt = f"Translate the following text to Arabic naturally. Only return the translation, nothing else:\n\n{text}"
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            result = msg.content[0].text
            embed = discord.Embed(color=COLOR_MAIN)
            embed.add_field(name="🔤 Original", value=text[:1024], inline=False)
            embed.add_field(name="🌙 Arabic", value=result[:1024], inline=False)
            embed.set_footer(text="Translated by Claude AI")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Translation error: {e}")

@bot.command(name="ترجمة")
async def translate_to_english(ctx, *, text: str):
    async with ctx.typing():
        prompt = f"Translate the following text to English naturally. Only return the translation, nothing else:\n\n{text}"
        try:
            msg = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            result = msg.content[0].text
            embed = discord.Embed(color=COLOR_MAIN)
            embed.add_field(name="🌙 النص الأصلي", value=text[:1024], inline=False)
            embed.add_field(name="🔤 English", value=result[:1024], inline=False)
            embed.set_footer(text="Translated by Claude AI")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ خطأ في الترجمة: {e}")

# ===================== XO GAME =====================
def make_xo_board(board):
    symbols = {None: "⬜", "X": "❌", "O": "⭕"}
    rows = []
    for i in range(0, 9, 3):
        rows.append(" ".join(symbols[board[j]] for j in range(i, i+3)))
    return "\n".join(rows)

def check_winner(board):
    wins = [
        [0,1,2],[3,4,5],[6,7,8],
        [0,3,6],[1,4,7],[2,5,8],
        [0,4,8],[2,4,6]
    ]
    for combo in wins:
        if board[combo[0]] and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]
    if all(board):
        return "draw"
    return None

@bot.command(name="xo")
async def xo_game(ctx, opponent: discord.Member = None):
    if ctx.channel.id in xo_games:
        return await ctx.send("❌ A game is already running in this channel! Finish it first.")
    if opponent is None:
        return await ctx.send("❌ Usage: `!xo @user`")
    if opponent == ctx.author:
        return await ctx.send("❌ You can't play against yourself!")
    if opponent.bot:
        return await ctx.send("❌ You can't play against a bot!")

    game = {
        "board": [None]*9,
        "players": {ctx.author.id: "❌", opponent.id: "⭕"},
        "order": [ctx.author, opponent],
        "turn": 0,
        "message": None
    }
    xo_games[ctx.channel.id] = game

    embed = discord.Embed(
        title="❌⭕ Tic-Tac-Toe",
        description=f"**{ctx.author.mention}** (❌) VS **{opponent.mention}** (⭕)\n\n"
                    f"{make_xo_board(game['board'])}\n\n"
                    f"**{ctx.author.display_name}'s turn!** Pick a position (1-9):\n"
                    f"```\n1 | 2 | 3\n4 | 5 | 6\n7 | 8 | 9\n```",
        color=COLOR_MAIN
    )
    msg = await ctx.send(embed=embed)
    game["message"] = msg

    def check(m):
        g = xo_games.get(ctx.channel.id)
        if not g:
            return False
        current = g["order"][g["turn"] % 2]
        return (m.channel == ctx.channel and
                m.author == current and
                m.content.isdigit() and
                1 <= int(m.content) <= 9)

    while ctx.channel.id in xo_games:
        try:
            move_msg = await bot.wait_for("message", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            del xo_games[ctx.channel.id]
            return await ctx.send("⏰ Game timed out!")

        g = xo_games.get(ctx.channel.id)
        if not g:
            break

        pos = int(move_msg.content) - 1
        current_player = g["order"][g["turn"] % 2]
        symbol_key = "X" if g["players"][current_player.id] == "❌" else "O"

        if g["board"][pos] is not None:
            await ctx.send("⚠️ That spot is taken! Pick another.", delete_after=3)
            continue

        g["board"][pos] = symbol_key
        g["turn"] += 1

        result = check_winner(g["board"])
        board_display = make_xo_board(g["board"])

        if result == "draw":
            del xo_games[ctx.channel.id]
            embed = discord.Embed(
                title="❌⭕ Tic-Tac-Toe — Draw!",
                description=f"{board_display}\n\n**It's a draw!** 🤝",
                color=COLOR_DRAW
            )
            return await ctx.send(embed=embed)
        elif result:
            winner = current_player
            del xo_games[ctx.channel.id]
            embed = discord.Embed(
                title="❌⭕ Tic-Tac-Toe — Winner!",
                description=f"{board_display}\n\n🏆 **{winner.mention} wins!**",
                color=COLOR_WIN
            )
            return await ctx.send(embed=embed)
        else:
            next_player = g["order"][g["turn"] % 2]
            embed = discord.Embed(
                title="❌⭕ Tic-Tac-Toe",
                description=f"{board_display}\n\n**{next_player.display_name}'s turn!** Pick (1-9)",
                color=COLOR_MAIN
            )
            await ctx.send(embed=embed)

# ===================== ROCK PAPER SCISSORS =====================
RPS_CHOICES = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}
RPS_WINS = {"rock": "scissors", "paper": "rock", "scissors": "paper"}

@bot.command(name="rps")
async def rps_game(ctx, opponent: discord.Member = None):
    if opponent is None:
        return await ctx.send("❌ Usage: `!rps @user`")
    if opponent == ctx.author:
        return await ctx.send("❌ You can't play against yourself!")
    if opponent.bot:
        return await ctx.send("❌ You can't play against a bot!")

    embed = discord.Embed(
        title="🎮 Rock Paper Scissors",
        description=f"**{ctx.author.mention}** VS **{opponent.mention}**\n\n"
                    f"Both players, check your DMs and reply with:\n"
                    f"`rock` 🪨 | `paper` 📄 | `scissors` ✂️",
        color=COLOR_MAIN
    )
    await ctx.send(embed=embed)

    choices = {}
    players = [ctx.author, opponent]

    async def get_choice(player):
        try:
            await player.send(
                f"🎮 **Rock Paper Scissors** vs {[p for p in players if p != player][0].display_name}\n"
                f"Reply with: `rock`, `paper`, or `scissors`"
            )
            def dm_check(m):
                return (m.author == player and
                        isinstance(m.channel, discord.DMChannel) and
                        m.content.lower() in RPS_CHOICES)
            msg = await bot.wait_for("message", timeout=30.0, check=dm_check)
            choices[player.id] = msg.content.lower()
        except discord.Forbidden:
            await ctx.send(f"❌ {player.mention} has DMs disabled!")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ {player.mention} didn't respond in time!")

    await asyncio.gather(get_choice(ctx.author), get_choice(opponent))

    if len(choices) < 2:
        return await ctx.send("❌ Game cancelled — not all players responded.")

    c1 = choices[ctx.author.id]
    c2 = choices[opponent.id]

    if c1 == c2:
        result_text = "**It's a draw!** 🤝"
        color = COLOR_DRAW
    elif RPS_WINS[c1] == c2:
        result_text = f"🏆 **{ctx.author.mention} wins!**"
        color = COLOR_WIN
    else:
        result_text = f"🏆 **{opponent.mention} wins!**"
        color = COLOR_WIN

    embed = discord.Embed(
        title="🎮 Rock Paper Scissors — Result!",
        description=(
            f"{ctx.author.display_name}: {RPS_CHOICES[c1]} **{c1.capitalize()}**\n"
            f"{opponent.display_name}: {RPS_CHOICES[c2]} **{c2.capitalize()}**\n\n"
            f"{result_text}"
        ),
        color=color
    )
    await ctx.send(embed=embed)

# ===================== حجر ورقة مقص (ARABIC) =====================
HRM_CHOICES = {"حجر": "🪨", "ورقة": "📄", "مقص": "✂️"}
HRM_WINS = {"حجر": "مقص", "ورقة": "حجر", "مقص": "ورقة"}

@bot.command(name="حجر")
async def hrm_game(ctx, opponent: discord.Member = None):
    if opponent is None:
        return await ctx.send("❌ الاستخدام: `!حجر @مستخدم`")
    if opponent == ctx.author:
        return await ctx.send("❌ ما تقدر تلعب ضد نفسك!")
    if opponent.bot:
        return await ctx.send("❌ ما تقدر تلعب ضد بوت!")

    embed = discord.Embed(
        title="🎮 حجر ورقة مقص",
        description=f"**{ctx.author.mention}** ضد **{opponent.mention}**\n\n"
                    f"كلا اللاعبين، تحققوا من الرسائل الخاصة وأجيبوا بـ:\n"
                    f"`حجر` 🪨 | `ورقة` 📄 | `مقص` ✂️",
        color=COLOR_MAIN
    )
    await ctx.send(embed=embed)

    choices = {}
    players = [ctx.author, opponent]

    async def get_choice(player):
        try:
            await player.send(
                f"🎮 **حجر ورقة مقص** ضد {[p for p in players if p != player][0].display_name}\n"
                f"اكتب: `حجر`، `ورقة`، أو `مقص`"
            )
            def dm_check(m):
                return (m.author == player and
                        isinstance(m.channel, discord.DMChannel) and
                        m.content in HRM_CHOICES)
            msg = await bot.wait_for("message", timeout=30.0, check=dm_check)
            choices[player.id] = msg.content
        except discord.Forbidden:
            await ctx.send(f"❌ {player.mention} أقفل رسائله الخاصة!")
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ {player.mention} ما رد في الوقت!")

    await asyncio.gather(get_choice(ctx.author), get_choice(opponent))

    if len(choices) < 2:
        return await ctx.send("❌ اللعبة ملغاة — مو كل اللاعبين ردوا.")

    c1 = choices[ctx.author.id]
    c2 = choices[opponent.id]

    if c1 == c2:
        result_text = "**تعادل!** 🤝"
        color = COLOR_DRAW
    elif HRM_WINS[c1] == c2:
        result_text = f"🏆 **{ctx.author.mention} يفوز!**"
        color = COLOR_WIN
    else:
        result_text = f"🏆 **{opponent.mention} يفوز!**"
        color = COLOR_WIN

    embed = discord.Embed(
        title="🎮 حجر ورقة مقص — النتيجة!",
        description=(
            f"{ctx.author.display_name}: {HRM_CHOICES[c1]} **{c1}**\n"
            f"{opponent.display_name}: {HRM_CHOICES[c2]} **{c2}**\n\n"
            f"{result_text}"
        ),
        color=color
    )
    await ctx.send(embed=embed)

# ===================== ERROR HANDLING =====================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Use `!help` for command info.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument! Make sure to mention a valid user.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands silently

# ===================== RUN =====================
bot.run(BOT_TOKEN)
