# Required by Red.
import discord
from redbot.core import commands
from redbot.core.bot import Red


class SpotifyNP(commands.Cog):
    """Spotify now playing"""

    __author__ = "#s#8059"
    __red_end_user_data_statement__ = "No user data is stored by this cog."
    SPOTIFY_NOT_LISTENING = (
        "User is not currently listening to Spotify, or is listening to a local file."
    )

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot

    # Commands
    @commands.command()
    async def spotify(self, ctx: commands.Context, user: discord.Member = None):
        """Check what someone is listening to"""
        if user is None:
            user = ctx.author
        spot = next((act for act in user.activities if isinstance(act, discord.Spotify)), None)
        if spot:
            # Create value for song field.
            minutes, seconds = divmod(spot.duration.seconds, 60)
            song_length = "{:02d}:{:02d}".format(minutes, seconds)
            song_url = "https://open.spotify.com/track/{}".format(spot.track_id)
            song_value = "[{}]({}) ({})".format(spot.title, song_url, song_length)
            # Create embed.
            embed = discord.Embed(colour=spot.colour)
            embed.title = "Spotify of {} - Currently playing".format(user.name)
            embed.add_field(name="Song", value=song_value, inline=False)
            embed.add_field(name="Artist", value=",".join(spot.artists), inline=False)
            embed.add_field(name="Album", value=spot.album, inline=False)
            embed.set_thumbnail(url=spot.album_cover_url)
            await ctx.reply(embed=embed, mention_author=False)
        else:
            await ctx.reply(self.SPOTIFY_NOT_LISTENING, mention_author=False)

    # Config
    async def red_delete_data_for_user(self, *, _requester, _user_id):
        """Do nothing, as no user data is stored."""
        pass
