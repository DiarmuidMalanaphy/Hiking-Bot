import csv
import io
import os

import discord
from discord import app_commands
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')


intents = discord.Intents.default()
intents.members = True

client = discord.Client(command_prefix=',', intents=intents)
tree = app_commands.CommandTree(client)

##I understand global variables are really bad practice
## the issue is I tried to use a class based system but had significant issues with decorators
global checked
global userDict
checked = False
userDict = None

@client.event

async def on_ready():
    await tree.sync(guild=discord.Object(id=896797114493964288))
    for guild in client.guilds:
        print(f'- {guild.name} (ID: {guild.id})')

async def generateDict(interaction: discord.Interaction, attachment: discord.Attachment):
    
    file_content = await attachment.read()
    reader = csv.reader(io.StringIO(file_content.decode('utf-8')))
    
    userDict = {}
    for row in reader:
        # Technically discord usernames can have spaces but I decided to eliminate the ones that had spaces from this
        # as input with spaces was junk like 95 % of the time
        # see "Dont have one", "You know", "What is discord?"
        if row[2].lower() != "n/a" and not (row[2].__contains__(' ')):
            username = row[0]+" "+row[1]
            userDict[row[2]] = username
    guild = interaction.guild
    membersRole = discord.utils.find(lambda r: r.name == 'Members', guild.roles)
    #I've created keys to delete is due to python not liking you iterating over a dictionary of changing size.
    keys_to_delete = []
    #Going through all the usernames in the csv
    for username in userDict.keys():
        # If the username isn't on the server - delete it
        # If the username is already registered - delete it
        if username not in [member.name for member in guild.members] or username in [member.name for member in membersRole.members]:
            keys_to_delete.append(username)
    for key in keys_to_delete:
        del userDict[key]

    return(userDict)
    

@tree.command(name = "member_check", description = "Unregistered Member Check", guild=discord.Object(id=896797114493964288))
async def member_check(interaction: discord.Interaction, attachment: discord.Attachment):
    #MEMBER CHECK WILL ONLY CREATE THE USERDICT AND THEN PRINT OUT THE NAMES
    #THE COMMIT MESSAGE IS TO ALLOW FOR HUMAN CONFIRMATION AS 
    #I WANTED TO PREVENT PROBLEMATIC INPUTS.



    file_content = await attachment.read()
    reader = csv.reader(io.StringIO(file_content.decode('utf-8')))
    # If the user is inputting files of not of 3 columns it's obviously not sanitised.
    try:
        first_row = next(reader)
        num_columns = len(first_row)
    except StopIteration:
        num_columns = 0

    
    if num_columns != 3:
        await interaction.response.send_message("The data is invalid.", ephemeral=True)
    

    # I'm restricting this to exec
    exec_role = discord.utils.get(interaction.guild.roles, name="Exec")
    if exec_role not in interaction.user.roles:
        await interaction.response.send_message("This is an exec only command.", ephemeral=True)
        return
    
    #Technically the user could input anything but this command is limited only to the exec
    global userDict
    userDict = await generateDict(interaction,attachment)
    #Userdict should only have usernames that are on the discord and are on the csv but not currently members
    name_username = []
    for username,name in userDict.items():
        name_username.append(f'{username} - {name}')
    
    

    message = ''
    for line in name_username:
        if len(message) + len(line) > 1900:  # Discord message limit is 2000 characters
            await interaction.response.send_message(message)
            message = ''
        message += line + '\n'

    if message:
        await interaction.response.send_message(message)
    global checked
    checked = True


@tree.command(name = "member_commit", description = "Member Change Commit", guild=discord.Object(id=896797114493964288))
async def member_commit(interaction: discord.Interaction ):
    global checked
    global userDict

    exec_role = discord.utils.get(interaction.guild.roles, name="Exec")
    if exec_role not in interaction.user.roles:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    if checked:
        guild = interaction.guild
        membersRole = discord.utils.find(lambda r: r.name == 'Members', guild.roles)
        for username, real_name in userDict.items():
            member = get(guild.members, name=username)
            if member:
                try:
                    await member.edit(nick=real_name)
                    await member.add_roles(membersRole)
                    # await interaction.response.send_message(f"Updated {username}: set nickname to {real_name} and assigned Member.")
                except discord.Forbidden:
                    await interaction.response.send_message(f"Permission denied to update {username}.")
            else:
                await interaction.response.send_message(f"Member {username} not found.")
    checked = False
    await interaction.response.send_message("Committed")
    


client.run(TOKEN)