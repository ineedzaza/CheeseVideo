import discord
from discord.ext import commands
import subprocess
import os
import asyncio

# --- CONFIG ---
TOKEN = "YOUR_BOT_TOKEN"  # put your Discord bot token
PREFIX = "cv "            # CheeseVideo bot prefix
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# --- HELPER: Run FFmpeg ---
async def run_ffmpeg(input_file, output_file, ffmpeg_args):
    cmd = ["ffmpeg", "-y", "-i", input_file] + ffmpeg_args + [output_file]
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    if process.returncode != 0:
        raise Exception(stderr.decode())
    return output_file

# --- COMMANDS ---

@bot.command()
async def fftest(ctx, *, args: str):
    """
    Example: cv fftest -vf "hue=h=90:s=2" 
    or       cv fftest -vf "curves=r='0/0 1/1':g='0/0 1/1'"
    """
    if not ctx.message.attachments:
        await ctx.send("Please attach a video or audio file.")
        return

    # download input
    attachment = ctx.message.attachments[0]
    input_file = f"input_{attachment.filename}"
    output_file = f"output_{attachment.filename}"
    await attachment.save(input_file)

    try:
        ffmpeg_args = args.split(" ")
        await run_ffmpeg(input_file, output_file, ffmpeg_args)
        await ctx.send(file=discord.File(output_file))
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")
    finally:
        if os.path.exists(input_file):
            os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

# --- PREDEFINED EFFECTS ---

@bot.command()
async def huesaturation(ctx, hue: int = 0, saturation: float = 1.0):
    """
    Adjust hue (0-360) and saturation (-100 to 100).
    Example: cv huesaturation 180 2.0
    """
    if not ctx.message.attachments:
        await ctx.send("Attach a video file!")
        return

    att = ctx.message.attachments[0]
    input_file = f"input_{att.filename}"
    output_file = f"output_{att.filename}"
    await att.save(input_file)

    hue_val = hue % 360
    sat_val = saturation
    ffmpeg_args = ["-vf", f"hue=h={hue_val}:s={sat_val}"]

    try:
        await run_ffmpeg(input_file, output_file, ffmpeg_args)
        await ctx.send(file=discord.File(output_file))
    finally:
        os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)


@bot.command()
async def swirl(ctx, angle: int = 90):
    """Swirl effect (-360 to 360)."""
    if not ctx.message.attachments:
        await ctx.send("Attach a video file!")
        return

    att = ctx.message.attachments[0]
    input_file = f"input_{att.filename}"
    output_file = f"output_{att.filename}"
    await att.save(input_file)

    ffmpeg_args = ["-vf", f"swirl=degrees={angle}"]

    try:
        await run_ffmpeg(input_file, output_file, ffmpeg_args)
        await ctx.send(file=discord.File(output_file))
    finally:
        os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)


@bot.command()
async def pitch(ctx, semitones: float = 0.0):
    """Pitch shift (-24 to 24 semitones)."""
    if not ctx.message.attachments:
        await ctx.send("Attach an audio/video file!")
        return

    att = ctx.message.attachments[0]
    input_file = f"input_{att.filename}"
    output_file = f"output_{att.filename}"
    await att.save(input_file)

    # FFmpeg pitch shift using asetrate
    pitch_factor = 2 ** (semitones / 12)
    ffmpeg_args = [
        "-filter:a",
        f"asetrate=44100*{pitch_factor},aresample=44100,atempo=1/{pitch_factor}"
    ]

    try:
        await run_ffmpeg(input_file, output_file, ffmpeg_args)
        await ctx.send(file=discord.File(output_file))
    finally:
        os.remove(input_file)
        if os.path.exists(output_file):
            os.remove(output_file)

# --- START BOT ---
bot.run(TOKEN)
