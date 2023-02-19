# Required by Red.
import discord
from redbot.core import commands
from redbot.core.bot import Red


class SnowflakeTools(commands.Cog):
    """Convert snowflake IDs for various uses"""

    __author__ = "#s#8059"
    GOTO_LINK = "<https://discordapp.com/channels/{gld_id}/{chn_id}/{msg_id}>"

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot

    # Commands
    @commands.command()
    async def goto(self, ctx: commands.Context, channel: discord.TextChannel, message_id: int):
        """Get a link to jump to a certain message in a channel.

        channel must be a channel __on a server__ that the bot is on.
        If no valid message ID is used, the link goes to where the message would have been in chat.
        """
        to_send = self.GOTO_LINK.format(gld_id=ctx.guild.id, chn_id=channel.id, msg_id=message_id)
        await ctx.reply(to_send, mention_author=False)

    @commands.command(aliases=["timestamp"])
    async def snowflake(self, ctx: commands.Context, snowflake_id: int):
        """Convert a Snowflake ID to a timestamp"""
        snow = discord.utils.snowflake_time(snowflake_id)
        time_str = snow.strftime("%A %d %B %Y at %H:%M:%S")
        msg = "**Input:** {}\n**Time (UTC):** {}".format(snowflake_id, time_str)
        await ctx.reply(msg, mention_author=False)

    # Config
    async def red_delete_data_for_user(self, *, _requester, _user_id):
        """Do nothing, as no user data is stored."""
        pass
