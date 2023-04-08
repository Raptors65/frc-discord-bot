from discord import app_commands
import discord


class TBACommandTree(app_commands.CommandTree):
    def __init__(self, client: discord.Client):
        super().__init__(client)

    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        embed = discord.Embed(title="Command Error",
                              description="An error occurred. Make sure your parameters are correct.")
        await interaction.response.send_message(embed=embed)
        await super().on_error(interaction, error)
