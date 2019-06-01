# Default Library.
import csv

# Used by Red.
import discord
from redbot.core import commands
from redbot.core.commands import Cog
from redbot.core import checks, Config, data_manager
from redbot.core.bot import Red


# Local files.

class DMLogger(Cog):
    """Log DMs sent to the bot to a csv file

    Note that DMs sent by the bot owner are completely ignored."""
    __author__ = "#s#8059"

    DELIMITER = ";"
    HEADER_LINE = ("Timestamp", "User ID", "Username", "Message", "Attachments")
    CSV_NAME = "/dm_logs.csv"

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=120420198059)
        self.FOLDER = str(data_manager.cog_data_path(self))
        self.CSV_FP = self.FOLDER + self.CSV_NAME
        self.config.register_global(msgs_since_export=0, periodic_log_threshold=None)

    # Events
    @Cog.listener()
    async def on_message(self, msg: discord.Message):
        """Add message info to db"""
        channel = msg.channel
        aut = msg.author
        # Check if a DM is sent by anyone but the bot owner.
        if isinstance(channel, discord.abc.PrivateChannel) and not await self.bot.is_owner(aut) and not aut.bot:
            # Log DM to CSV file.
            self.log_dm_to_csv(msg)
            # Check if the threshold for the periodical export is met.
            export_count = await self.config.msgs_since_export() + 1
            periodic_threshold = await self.config.periodic_log_threshold()
            if periodic_threshold and export_count >= periodic_threshold:
                owner = (await self.bot.application_info()).owner
                await owner.send(content="Periodical DM log export.", file=discord.File(self.CSV_FP))
                await self.config.msgs_since_export.set(0)
            else:
                await self.config.msgs_since_export.set(export_count)  # Incremented.

    # Commands
    @commands.command(name="set_dm_threshold")
    @checks.is_owner()
    async def set_periodic_log_threshold(self, ctx: commands.Context, threshold: int):
        """Set the threshold for the periodic DM export (to the bot owner)

        If the threshold is 0 (or less) no periodic messages will be sent.
        If the threshold is changed, the next message sent after the change may trigger an export."""
        to_set = None if threshold <= 0 else threshold
        await self.config.periodic_log_threshold.set(to_set)
        await ctx.tick()

    @commands.command(name="get_dms")
    @checks.is_owner()
    async def send_dm_log(self, ctx: commands.Context):
        """Send the DM log csv file as-is

        This also resets the export count."""
        await ctx.send(content="Below is the bot DM log.", file=discord.File(self.CSV_FP))
        await self.config.msgs_since_export.set(0)

    # Utilities
    def log_dm_to_csv(self, msg: discord.Message):
        """Log a csv file to the CSV file"""
        aut = msg.author
        stamp = str(msg.created_at)
        user_id = "ID: {}".format(aut.id)  # "ID:" prevents number truncations.
        username = str(aut)
        content = "Content: {}".format(msg.content)  # "Content:" prevents prefix issues.
        attach_str = ", ".join(attachment.url for attachment in msg.attachments)
        with open(self.CSV_FP, mode="a", newline='', errors="ignore", encoding='utf-8') as csv_f:
            csv_w = csv.writer(csv_f, delimiter=self.DELIMITER)
            if csv_f.tell() == 0:  # Empty file, append headers.
                csv_w.writerow(self.HEADER_LINE)
            csv_w.writerow((stamp, user_id, username, content, attach_str))
