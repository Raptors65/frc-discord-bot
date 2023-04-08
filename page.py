from typing import Any, Callable
import discord


class Page(discord.ui.View):
    def __init__(self, start_page: int, num_pages: int,
                 formatter: Callable[[int], discord.Embed]):
        super().__init__()

        self.page = start_page
        self.num_pages = num_pages
        self.formatter = formatter

    @discord.ui.button(label="\N{Black Left-Pointing Triangle}", style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page - 1) % self.num_pages
        await interaction.response.edit_message(embed=self.formatter(self.page))

    @discord.ui.button(label="\N{Black Right-Pointing Triangle}", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = (self.page + 1) % self.num_pages
        await interaction.response.edit_message(embed=self.formatter(self.page))
