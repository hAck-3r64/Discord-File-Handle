import discord
from discord.ext import commands
import keep_alive
import aiofiles

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="ch!", intents=intents)
client = discord.Client()
bot.warnings = {}  # guild_id: {member_id: [count, [(admin_id, reason)]]}

m = {}

keep_alive.keep_alive()

@bot.event
async def on_ready():
  await bot.change_presence(status=discord.Status.idle, activity=discord.Game("ch!help"))
  for guild in bot.guilds:
    async with aiofiles.open(f"{guild.id}.txt", mode="a") as temp:
        pass

    bot.warnings[guild.id] = {}

  for guild in bot.guilds:
      async with aiofiles.open(f"{guild.id}.txt", mode="r") as file:
          lines = await file.readlines()

          for line in lines:
              data = line.split(" ")
              member_id = int(data[0])
              admin_id = int(data[1])
              reason = " ".join(data[2:]).strip("\n")

              try:
                  bot.warnings[guild.id][member_id][0] = + 1
                  bot.warnings[guild.id][member_id][1].append((admin_id, reason))

              except KeyError:
                  bot.warnings[guild.id][member_id] = [1, [(admin_id, reason)]]
  
  print(bot.user.name + " is online.")


@bot.event
async def on_guild_join(guild):
    bot.warnings[guild.id] = {}

@bot.command(description="Warns the provided member")
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member = None, *, reason=None):
    if member is None:
        return await ctx.send("The provided choco could not be found or you forgot to provide one.")

    if reason is None:
        return await ctx.send("Please provide a reason for warning this choco.")

    try:
        first_warning = False
        bot.warnings[ctx.guild.id][member.id][0] += 1
        bot.warnings[ctx.guild.id][member.id][1].append((ctx.author.id, reason))

    except KeyError:
        first_warning = True
        bot.warnings[ctx.guild.id][member.id] = [1, [(ctx.author.id, reason)]]

    count = bot.warnings[ctx.guild.id][member.id][0]

    async with aiofiles.open(f"{ctx.guild.id}.txt", mode="a") as file:
        await file.write(f"{member.id} {ctx.author.id} {reason}\n")

    await ctx.send(f"{member.mention} has {count} {'warning' if first_warning else 'warnings'}.")

@bot.command(description="Shows the warnings the provided member has")
@commands.has_permissions(administrator=True)
async def warnings(ctx, member: discord.Member = None):
    if member is None:
        return await ctx.send("The provided choco could not be found or you forgot to provide one.")

    embed = discord.Embed(title=f"Displaying Warnings for {member.name}", description="", colour=discord.Colour.red())
    try:
        i = 1
        for admin_id, reason in bot.warnings[ctx.guild.id][member.id][1]:
            admin = ctx.guild.get_member(admin_id)
            embed.description += f"**Warning {i}** given by: <@{admin_id}> for: *'{reason}'*.\n"
            i += 1

        await ctx.send(embed=embed)

    except KeyError:  # no warnings
        await ctx.send("This choco has no warnings.")

@bot.command()
async def test(ctx):
  await ctx.send("Working!")

@bot.command(description="Displays the current Coco Democracy topic")
async def democracytopic(ctx):
  await ctx.send("There currently is no Coco Democracy topic.")

@bot.command(description="Casts your final vote for a Coco Democracy")
async def democracycastvote(ctx, *, response = None):
  if response == None:
    await ctx.send("There currently is no Coco Democracy topic for you to vote on!")
  response = response.replace("(", "")
  response = response.replace(")", "")
  async with aiofiles.open("votes.txt", mode="w+") as file:
      await file.write(f"{response}\n")
  await ctx.send(f"Cast vote '{response}'.")

@bot.command(description="Shows all the current Coco Democracy votes")
async def democracyvotes(ctx):
    await ctx.send(file=discord.File('votes.txt')


@bot.run(TOKEN)
