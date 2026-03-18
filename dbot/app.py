import discord
from discord import app_commands
from discord.ext import commands
from config import Config
from logger import logger
from twitch.clips import SaveClip, UpdateClip, RemoveClip, GetClips, UpdateVodData

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = '/', intents = intents)