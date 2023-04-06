import tba
import discord
from discord import app_commands
import os
from datetime import datetime
import time
from discord.ext import commands
import helpers

from dotenv import load_dotenv
load_dotenv()


class FRCClient(commands.Bot):
    def __init__(self, team_number, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.team_number = team_number

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        if message.author != self.user:
            async with message.channel.typing():
                await super().on_message(message)
        else:
            await super().on_message(message)

    async def close(self):
        print("Closing")

        if (tba.session is not None):
            await tba.session.close()
        await super().close()


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True


bot = FRCClient(8574,
                command_prefix="+",
                intents=intents)


@bot.command()
async def events(ctx: commands.Context, team_number: int = bot.team_number):
    team_events_data = await tba.team_events_year(
        f"frc{team_number}", datetime.now().year)
    team_events = [f"""**{event["name"]} ({event["key"]})**
                                *{event["start_date"]} - {event["end_date"]}{f' (Week {event["week"]})' if "week" in event else ""}*
                                *{f'@ {event["location_name"]}' if "location_name" in event else ""}*"""
                   for event in team_events_data]
    description = "\n\n".join(team_events)

    embed = discord.Embed(title="Events", description=description)
    await ctx.send(embed=embed)


@bot.command()
async def predictions(ctx: commands.Context, event_key: str):
    event_predictions_data = await tba.event_predictions(event_key)
    if event_predictions_data["ranking_predictions"] is None:
        await ctx.send("Predictions not available.")
        return

    description = "\n".join(
        f"{team[1][0]}. {team[0][3:]}" for team in event_predictions_data["ranking_predictions"])
    await ctx.send(embed=discord.Embed(title="Predictions", description=description))


@bot.command()
async def schedule(ctx: commands.Context, team_number: int = bot.team_number):
    matches = await tba.team_matches_year_simple(
        f"frc{team_number}", datetime.now().year)
    next_matches = sorted(filter(lambda match: match["predicted_time"] is not None
                                 and time.time() < match["predicted_time"],
                                 matches),
                          key=lambda event: event["match_number"])[:10]

    if len(next_matches) == 0:
        await ctx.send(embed=discord.Embed(title="Upcoming Matches",
                                           description="No scheduled matches."))
        return

    current_event_key = next_matches[0]["event_key"]

    predictions = await tba.event_predictions(current_event_key)

    if (match_predictions := predictions["match_predictions"]) is not None:
        embed = helpers.format_matches(
            next_matches, team_number, "Upcoming Matches", match_predictions)
    else:
        embed = helpers.format_matches(
            next_matches, team_number, "Upcoming Matches")

    await ctx.send(embed=embed)


@bot.command()
async def history(ctx: commands.Context, team_number: int = bot.team_number):

    matches = await tba.team_matches_year_simple(
        f"frc{team_number}", datetime.now().year)
    previous_matches = sorted(filter(lambda match: match["predicted_time"] is not None
                                     and match["predicted_time"] < time.time(),
                                     matches),
                              key=lambda match: match["predicted_time"])[-10:]

    embed = helpers.format_matches(
        previous_matches, team_number, "Past Matches")
    await ctx.send(embed=embed)

bot.run(os.getenv("DISCORD_TOKEN"))
