import discord
from discord.ext import commands, tasks
import asyncio

class Radio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.volume = 0.5  
        self.auto_disconnect.start()  

    # Radio play command with select menu
    @commands.slash_command(name="radio", description="Play a radio stream.")
    async def radio_play(self, ctx):
        radios = {
            "ILoveRadio": "https://ilm-stream11.radiohost.de/ilm_iloveradio_mp3-192?_art=dD0xNzI0ODMyMzY2JmQ9OTA5YTNkYzQzZjY1MzFkZWQ0Yzk",
            "ILove2Dance": "https://ilm-stream13.radiohost.de/ilm_ilove2dance_mp3-192?_art=dD0xNzI0ODMyMzkxJmQ9N2YyMzk4ZTkyMWU5MTg3NmJjMjI",
            "ILoveThe90s": "https://ilm-stream13.radiohost.de/ilm_ilovethe90s_mp3-192?_art=dD0xNzI0ODMyNDUxJmQ9MmYyODhhYzA5NTZkYWJhMDdmNmU",
            "ILoveMashup": "https://ilm-stream18.radiohost.de/ilm_ilovemashup_mp3-192?_art=dD0xNzI0ODMyNDE4JmQ9NzUzOTA5OTljYTNhYjlkMjU3ZDQ",
            "ILoveBiggestPopHits": "https://ilm-stream18.radiohost.de/ilm_ilovenewpop_mp3-192?_art=dD0xNzI0ODMyNDg1JmQ9NzYzZWZkZmYxZDAyNDU5YTBiOTE"
        }

        options = [
            discord.SelectOption(label=name, description=f"Play {name}", value=name)
            for name in radios
        ]
        
        select = discord.ui.Select(placeholder="Choose a radio station...", options=options)

        async def select_callback(interaction):
            if interaction.user == ctx.author:
                selected_radio = interaction.data['values'][0]
                selected_url = radios[selected_radio]
                await self.play_radio(ctx, selected_url)
            else:
                await interaction.response.send_message("You cannot select for this command.", ephemeral=True)

        select.callback = select_callback

        view = discord.ui.View()
        view.add_item(select)

        button = discord.ui.Button(label="Own Music", style=discord.ButtonStyle.primary)

        async def button_callback(interaction):
            if interaction.user == ctx.author:
                await interaction.response.send_modal(MP3LinkModal(self))

        button.callback = button_callback
        view.add_item(button)

        embed = discord.Embed(
            title="🎶Wähle einen Radio",
            description="Choose one of the available radio stations or select 'Own Music' to play your own MP3 file.",
            color=discord.Color.blue()
        )
        await ctx.respond(embed=embed, view=view)

    async def play_radio(self, ctx, url: str):
        channel = ctx.author.voice.channel if ctx.author.voice else None
        if channel:
            if not self.voice_client or not self.voice_client.is_connected():
                self.voice_client = await channel.connect()
            elif self.voice_client.channel != channel:
                await self.voice_client.move_to(channel)

            self.voice_client.stop()  # Stop any current audio
            
            # Play the radio stream with the set volume
            source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source=url), volume=self.volume)
            self.voice_client.play(source)

            embed = discord.Embed(
                title="🎶 Now Playing",
                description="Streaming radio from the selected station.",
                color=discord.Color.blue()
            )
            embed.add_field(name="Channel", value=f"{channel.name}", inline=True)
            embed.add_field(name="Requested by", value=f"{ctx.author.mention}", inline=True)
            embed.add_field(name="Volume", value=f"{int(self.volume * 100)}%", inline=True)
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="🚫 Not in a Voice Channel",
                description="You need to be in a voice channel for the bot to join and play music.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)

    # Volume command
    @commands.slash_command(name="volume", description="Set the volume between 0% and 100%.")
    async def set_volume(self, ctx, volume: int):
        if 0 <= volume <= 100:
            self.volume = volume / 100
            if self.voice_client and self.voice_client.is_playing():
                self.voice_client.source.volume = self.volume  
            embed = discord.Embed(
                title="🔊 Volume Adjusted",
                description=f"Volume has been set to {volume}%.",
                color=discord.Color.green()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="🚫 Invalid Volume",
                description="Volume must be between 0 and 100.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)

    # Pause command
    @commands.slash_command(name="pause", description="Pause the radio stream.")
    async def pause_radio(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
            embed = discord.Embed(
                title="⏸️ Paused",
                description="The radio stream has been paused.",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Nothing Playing",
                description="There is no radio stream playing currently.",
                color=discord.Color.yellow()
            )
            await ctx.respond(embed=embed)

    # Resume command
    @commands.slash_command(name="resume", description="Resume the radio stream.")
    async def resume_radio(self, ctx):
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
            embed = discord.Embed(
                title="▶️ Resumed",
                description="The radio stream has been resumed.",
                color=discord.Color.green()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Nothing Paused",
                description="There is no paused radio stream to resume.",
                color=discord.Color.yellow()
            )
            await ctx.respond(embed=embed)

    # Stop command
    @commands.slash_command(name="stop", description="Stop the radio stream.")
    async def stop_radio(self, ctx):
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.stop()
            embed = discord.Embed(
                title="🛑 Radio Stopped",
                description="The radio stream has been stopped.",
                color=discord.Color.orange()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="⚠️ Nothing Playing",
                description="There is no radio stream playing currently.",
                color=discord.Color.yellow()
            )
            await ctx.respond(embed=embed)

    # Leave command
    @commands.slash_command(name="leave", description="Leave the voice channel.")
    async def leave(self, ctx):
        if self.voice_client and self.voice_client.is_connected():
            await self.voice_client.disconnect()
            self.voice_client = None
            embed = discord.Embed(
                title="👋 Left Voice Channel",
                description="The bot has left the voice channel.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="🚫 Not Connected",
                description="The bot is not connected to any voice channel.",
                color=discord.Color.red()
            )
            await ctx.respond(embed=embed)

    @tasks.loop(seconds=60)
    async def auto_disconnect(self):
        if self.voice_client and self.voice_client.is_connected():
            channel = self.voice_client.channel
            if len(channel.members) == 1:  # Only the bot is left
                await asyncio.sleep(600)  # Wait 10 minutes
                if len(channel.members) == 1 and self.voice_client.is_connected():
                    await self.voice_client.disconnect()
                    self.voice_client = None

    def cog_unload(self):
        self.auto_disconnect.cancel()

class MP3LinkModal(discord.ui.Modal):
    def __init__(self, radio_cog):
        super().__init__(title="Enter Your MP3 URL")
        self.radio_cog = radio_cog

        
        self.url_input = discord.ui.InputText(
            label="MP3 URL",
            placeholder="Enter the URL to your MP3 file...",
            required=True
        )
        self.add_item(self.url_input)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Playing your custom MP3...", ephemeral=True)
        await self.radio_cog.play_radio(interaction, self.url_input.value)

def setup(bot):
    bot.add_cog(Radio(bot))

