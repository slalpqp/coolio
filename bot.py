import discord
from discord.ext import commands
from discord import app_commands
from keep_alive import keep_alive  # Import the keep_alive function
from dotenv import load_dotenv  # Import dotenv to load the .env file
import os  # To access environment variables

# Load environment variables from .env
load_dotenv()

# Define intents
intents = discord.Intents.default()

# Initialize bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Replace this with the role ID you want to use for the 'verified' role
VERIFIED_ROLE_ID = 1331482811646869555

# Track vouches
vouches = {}  # {vouched_user_id: {vouched_by_user_id}}

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f"We have logged in as {bot.user}")

@bot.tree.command(name="vouch", description="Vouch for a user.")
@app_commands.describe(user="The user you'd like to vouch for.")
async def vouch(interaction: discord.Interaction, user: discord.Member):
    if user.id == interaction.user.id:
        await interaction.response.send_message("You cannot vouch for yourself.", ephemeral=True)
        return

    if user.id not in vouches:
        vouches[user.id] = set()

    if interaction.user.id in vouches[user.id]:
        await interaction.response.send_message("You have already vouched for this user.", ephemeral=True)
        return

    # Add the user's vouch
    vouches[user.id].add(interaction.user.id)
    current_vouches = len(vouches[user.id])

    if current_vouches >= 3:  # Check if the user has 3 or more vouches
        verified_role = discord.utils.get(interaction.guild.roles, id=VERIFIED_ROLE_ID)
        if verified_role not in user.roles:
            await user.add_roles(verified_role)
            await interaction.response.send_message(
                f"{user.mention} has been verified with {current_vouches} vouches!"
            )
        else:
            await interaction.response.send_message(
                f"{user.mention} already has the verified role."
            )
    else:
        await interaction.response.send_message(
            f"You have vouched for {user.mention}. They now have {current_vouches}/3 vouches."
        )

@bot.tree.command(name="check_vouches", description="Check how many vouches a user has.")
@app_commands.describe(user="The user you'd like to check.")
async def check_vouches(interaction: discord.Interaction, user: discord.Member):
    current_vouches = len(vouches.get(user.id, []))
    await interaction.response.send_message(
        f"{user.mention} currently has {current_vouches}/3 vouches."
    )

@bot.tree.command(name="unvouch", description="Remove your vouch for a user.")
@app_commands.describe(user="The user you'd like to unvouch.")
async def unvouch(interaction: discord.Interaction, user: discord.Member):
    if user.id not in vouches or interaction.user.id not in vouches[user.id]:
        await interaction.response.send_message(
            "You haven't vouched for this user.", ephemeral=True
        )
        return

    # Remove the vouch
    vouches[user.id].remove(interaction.user.id)
    current_vouches = len(vouches[user.id])

    await interaction.response.send_message(
        f"You have removed your vouch for {user.mention}. They now have {current_vouches}/3 vouches."
    )

keep_alive()  # Keeps the bot alive

# Get the token from the environment variable
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    print("Error: Token not found in the environment variables.")
else:
    bot.run(TOKEN)
