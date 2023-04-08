from math import ceil
from command_tree import TBACommandTree
from page import Page
import tba
import discord
from discord import app_commands
import os
from datetime import datetime
import time
import helpers

from dotenv import load_dotenv
load_dotenv()

GUILD_ID = os.getenv("GUILD_ID")
if GUILD_ID is None:
    raise NameError("GUILD_ID not found in .env file")
MY_GUILD = discord.Object(GUILD_ID)
MAX_MATCHES_PER_PAGE = 8


class FRCClient(discord.Client):
    def __init__(self, team_number, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.team_number = team_number
        self.tree = TBACommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)

    async def on_ready(self):
        print(f"We have logged in as {self.user}")

    async def close(self):
        print("Closing")

        if (tba.session is not None):
            await tba.session.close()
        await super().close()


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True


client = FRCClient(8574, intents=intents)


@client.tree.command()
@app_commands.describe(team_number="The team number")
async def events(interaction: discord.Interaction, team_number: int = client.team_number):
    team_events_data = await tba.team_events_year(
        f"frc{team_number}", datetime.now().year)
    team_events = [f"""**{event["name"]} ({event["key"]})**
                                *{event["start_date"]} - {event["end_date"]}{f' (Week {event["week"]})' if "week" in event else ""}*
                                *{f'@ {event["location_name"]}' if "location_name" in event else ""}*"""
                   for event in team_events_data]
    description = "\n\n".join(team_events)

    embed = discord.Embed(title=f"Events - {team_number}", description=description)
    await interaction.response.send_message(embed=embed)


@client.tree.command()
@app_commands.describe(event_key="The event key")
async def predictions(interaction: discord.Interaction, event_key: str):
    event_predictions_data = await tba.event_predictions(event_key)
    if event_predictions_data["ranking_predictions"] is None:
        await interaction.response.send_message("Predictions not available.")
        return

    rankings = sorted(event_predictions_data["ranking_predictions"],
                      key=lambda prediction: prediction[1][4], reverse=True)

    embed = discord.Embed(title=f"Predictions - {event_key}")
    for rank, team in enumerate(rankings, start=1):
        embed.add_field(name=f"{rank}. {team[0][3:]}", value=f"{round(team[1][4])} RP")
    await interaction.response.send_message(embed=embed)


@client.tree.command()
@app_commands.describe(team_number="The team number")
async def schedule(interaction: discord.Interaction, team_number: int = client.team_number):
    matches = await tba.team_matches_year_simple(
        f"frc{team_number}", datetime.now().year)
    next_matches = sorted(filter(lambda match: match["predicted_time"] is not None
                                 and time.time() < match["predicted_time"],
                                 matches),
                          key=lambda event: event["predicted_time"])  # type: ignore

    if len(next_matches) == 0:
        await interaction.response.send_message(embed=discord.Embed(title="Upcoming Matches",
                                                                    description="No scheduled matches."))
        return

    current_event_key = next_matches[0]["event_key"]

    predictions = await tba.event_predictions(current_event_key)

    num_pages = ceil(len(next_matches) / MAX_MATCHES_PER_PAGE)

    def formatter(page: int):
        page_matches = next_matches[page*MAX_MATCHES_PER_PAGE:(page+1)*MAX_MATCHES_PER_PAGE]
        if (match_predictions := predictions["match_predictions"]) is not None:
            embed = helpers.format_matches(
                page_matches, team_number, f"Upcoming Matches - {team_number} - Page {page + 1}/{num_pages}", match_predictions)
        else:
            embed = helpers.format_matches(
                page_matches, team_number, f"Upcoming Matches - {team_number} - Page {page + 1}/{num_pages}")
        return embed

    if num_pages > 1:
        view = Page(0, num_pages, formatter)
        await interaction.response.send_message(embed=formatter(0), view=view)
    else:
        await interaction.response.send_message(embed=formatter(0))


@client.tree.command()
@app_commands.describe(team_number="The team number")
async def history(interaction: discord.Interaction, team_number: int = client.team_number):

    matches = await tba.team_matches_year_simple(
        f"frc{team_number}", datetime.now().year)
    previous_matches = sorted(filter(lambda match: match["predicted_time"] is not None
                                     and match["predicted_time"] < time.time(),
                                     matches),
                              key=lambda match: match["predicted_time"],  # type: ignore
                              reverse=True)

    num_pages = ceil(len(previous_matches) / MAX_MATCHES_PER_PAGE)

    def formatter(page: int):
        page_matches = previous_matches[page*MAX_MATCHES_PER_PAGE:(page+1)*MAX_MATCHES_PER_PAGE]
        embed = helpers.format_matches(
            page_matches, team_number, f"Previous Matches - {team_number} - Page {page + 1}/{num_pages}")
        return embed

    if num_pages > 1:
        view = Page(0, num_pages, formatter)
        await interaction.response.send_message(embed=formatter(0), view=view)
    else:
        await interaction.response.send_message(embed=formatter(0))

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if DISCORD_TOKEN is None:
    raise NameError("DISCORD_TOKEN not found in .env file")

client.run(DISCORD_TOKEN)
