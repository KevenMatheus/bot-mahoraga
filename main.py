import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# 🔥 yt-dlp estável 2026
YDL_OPTIONS = {
    "format": "bestaudio[ext=m4a]/bestaudio/best",
    "noplaylist": True,
    "quiet": True
}

FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

# Fila global
queue = []

@bot.event
async def on_ready():
    print(f"Bot logado como {bot.user}")

@bot.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return

    await msg.reply("Eu quero gozar")
    await bot.process_commands(msg)

# -------- TOCAR PRÓXIMA -------- #

async def tocar_proxima(ctx):
    if not queue:
        await ctx.send("📭 Fila vazia.")
        return

    url, titulo = queue.pop(0)

    source = discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS)

    def after_playing(error):
        if error:
            print("Erro ao tocar:", error)
        fut = asyncio.run_coroutine_threadsafe(
            tocar_proxima(ctx), bot.loop
        )
        try:
            fut.result()
        except:
            pass

    ctx.voice_client.play(source, after=after_playing)
    await ctx.send(f"🎵 Tocando agora: {titulo}")

# ---------------- COMANDOS ---------------- #

@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

@bot.command()
async def entrar(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send("Entrei na call 😈")
    else:
        await ctx.send("Você precisa estar em um canal de voz primeiro.")

@bot.command()
async def sair(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Saí da call.")
    else:
        await ctx.send("Eu não estou em uma call.")

# ---------------- MÚSICA ---------------- #

@bot.command()
async def iniciar(ctx, *, busca):
    if not ctx.author.voice:
        await ctx.send("Você precisa estar em um canal de voz.")
        return

    if not ctx.voice_client:
        await ctx.author.voice.channel.connect()

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            if "http" in busca:
                info = ydl.extract_info(busca, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{busca}", download=False)['entries'][0]

            audio_url = info["url"]
            titulo = info["title"]

    except Exception as e:
        await ctx.send("❌ Erro ao buscar a música.")
        print("Erro yt-dlp:", e)
        return

    queue.append((audio_url, titulo))
    await ctx.send(f"➕ Adicionado à fila: {titulo}")

    if not ctx.voice_client.is_playing():
        await tocar_proxima(ctx)

@bot.command()
async def pular(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏭ Música pulada.")
    else:
        await ctx.send("Não estou tocando nada.")

@bot.command()
async def fila(ctx):
    if not queue:
        await ctx.send("📭 Fila vazia.")
        return

    lista = "\n".join(
        [f"{i+1}. {titulo}" for i, (_, titulo) in enumerate(queue)]
    )

    await ctx.send(f"🎶 Fila atual:\n{lista}")

@bot.command()
async def parar(ctx):
    queue.clear()
    if ctx.voice_client:
        await ctx.voice_client.stop()
        await ctx.voice_client.disconnect()
        await ctx.send("🛑 Música parada e fila limpa.")
    else:
        await ctx.send("Não estou em uma call.")

# ----------------------------------------- #

bot.run(os.getenv("MTQ3NTE4ODIzMDQ4MjY5NDE0NA.GzDbUu.MQ4soYQxIxX8KZzhHKOW4zl5LRC_eU0NNpYJm4"))
