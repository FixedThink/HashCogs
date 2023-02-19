from __future__ import annotations
# Default Library.
import datetime as dt

# Required by Red.
import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.utils.chat_formatting import humanize_timedelta


SLOWMODE_TIMEDELTA_CONVERTER = commands.TimedeltaConverter(
    minimum=dt.timedelta(seconds=0), maximum=dt.timedelta(hours=6), default_unit="seconds"
)


class ChannelSlowmode(commands.Cog):
    """Modify the slowmode in another channel that you are currently in"""

    __author__ = "#s#8059"
    X = ":x: Error: "

    SLOWMODE_SET = ":white_check_mark: The slowmode in {} has been set to {}."
    SLOWMODE_OFF = ":put_litter_in_its_place: The slowmode in {} has been disabled."
    SLOWMODE_NO_PERMS = X + "I need Manage {} permissions in {} to set a slowmode!"

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot

    # Commands
    @commands.command()
    @commands.guild_only()
    @commands.admin_or_permissions(manage_channels=True)
    async def channel_slowmode(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel | discord.Thread,
        *,
        time: SLOWMODE_TIMEDELTA_CONVERTER = dt.timedelta(seconds=0),
    ):
        """Set the Discord slowmode in the specified channel (or thread)

        time can be at most 6 hours. If time is 0 seconds, slowmode will be turned off.
        Requires Manage Channel permissions to be used (also for usage in threads)."""
        seconds = int(time.total_seconds())
        mention = channel.mention
        try:
            await channel.edit(slowmode_delay=seconds)
        except discord.Forbidden:  # Manage channel perms required.
            perm_needed = "Channel" if isinstance(channel, discord.TextChannel) else "Thread"
            notice = self.SLOWMODE_NO_PERMS.format(perm_needed, mention)
        else:
            if seconds == 0:
                notice = self.SLOWMODE_OFF.format(mention)
            else:
                notice = self.SLOWMODE_SET.format(mention, humanize_timedelta(timedelta=time))
        await ctx.reply(notice, mention_author=False)

    # Config.
    async def red_delete_data_for_user(self, *, _requester, _user_id):
        """Do nothing, as no user data is stored."""
        pass
