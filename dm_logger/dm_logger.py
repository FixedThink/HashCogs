# Default Library.
import csv
import os.path

# Used by Red.
import discord
from redbot.core import commands, Config, data_manager
from redbot.core.bot import Red
from redbot.core.commands import Cog, Context


class DMLogger(Cog):
    """Log DMs sent to the bot to a csv file

    All timestamps used in the DM use UTC.
    Note that DMs sent by the bot owner are completely ignored."""

    __author__ = "#s#8059"

    # Messages.
    X = ":x: Error: "
    AUTO_EXPORT = ":outbox_tray: Periodical DM log export."
    MANUAL_EXPORT = ":outbox_tray: Below is the bot DM log."
    TOO_BIG = X + "the DM log file is too big to send here!\n\n**Size:** {fs}\n**Limit:** {fl}"
    AUTO_TOO_BIG = (
        "Dear bot owner,\nI tried to dm you your periodical DM log export. "
        "However, the size of the log file ({fs}) is too big for Discord's DM size limit ({fl})!\n"
        "Please consider one of the following options:\n"
        "• Disable the periodic DM export and check the DM logs in a channel allowing for it\n"
        "• Manually download the log file, then delete it from the bot, "
        "such that the logs can start fresh."
    )
    # Other constants.
    DELIMITER = ";"
    HEADER_LINE = ("Timestamp", "User ID", "Username", "Message", "Attachments")
    CSV_NAME = "dm_logs.csv"
    ONE_MB = 1024 * 1024  # From bytes to MB.
    EIGHT_MB = ONE_MB * 8

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=120420198059)
        self.FOLDER = str(data_manager.cog_data_path(self))
        self.CSV_FP = os.path.join(self.FOLDER, self.CSV_NAME)
        self.config.register_global(msgs_since_export=0, periodic_log_threshold=None)

    # Events
    @Cog.listener()
    async def on_message(self, msg: discord.Message):
        """Add message info to db"""
        channel = msg.channel
        aut = msg.author
        # Check if a DM is sent by anyone but the bot or its owner.
        if (
            isinstance(channel, discord.abc.PrivateChannel)
            and not await self.bot.is_owner(aut)
            and not aut.bot
        ):
            # Log DM to CSV file.
            self.log_dm_to_csv(msg)
            # Check if the threshold for the periodical export is met.
            export_count = await self.config.msgs_since_export() + 1
            periodic_threshold = await self.config.periodic_log_threshold()
            # Attempt a periodic export.
            if periodic_threshold and export_count >= periodic_threshold:
                owner = (await self.bot.application_info()).owner
                # First, check if file can be sent in DMs (file limit always 8MB).
                csv_filesize = self.csv_filesize()
                dm_size_limit = self.EIGHT_MB
                if csv_filesize > dm_size_limit:  # Inform bot owner that it's too big!
                    fs = self.file_size_in_mb(csv_filesize)
                    fl = self.file_size_in_mb(dm_size_limit)
                    await owner.send(content=self.AUTO_TOO_BIG.format(fs=fs, fl=fl))
                else:  # File can be sent to owner.
                    await owner.send(content=self.AUTO_EXPORT, file=discord.File(self.CSV_FP))
                await self.config.msgs_since_export.set(0)
            else:
                await self.config.msgs_since_export.set(export_count)  # Incremented.

    # Commands
    @commands.command(name="set_dm_threshold")
    @commands.is_owner()
    async def set_periodic_log_threshold(self, ctx: Context, threshold: int):
        """Set the threshold for the periodic DM export (to the bot owner)

        If the threshold is 0 (or less) no periodic messages will be sent.
        If the threshold is changed, the next message sent after the change may trigger an export.
        """
        to_set = None if threshold <= 0 else threshold
        await self.config.periodic_log_threshold.set(to_set)
        await ctx.tick()

    # Command is owner only. If permission granted to non-owner, who then runs this command in DMs,
    #  this will likely result in an error, as the file is updated while a message is being sent.
    @commands.command(name="get_dms")
    @commands.is_owner()
    @commands.bot_has_permissions(attach_files=True)
    async def send_dm_log(self, ctx: Context):
        """Send the DM log csv file as-is

        This also resets the export count if the export was successful."""
        if not os.path.isfile(self.CSV_FP):
            await ctx.reply("I feel lonely, nobody has DMed me yet :cry:")
        else:
            # Check size limit.
            max_size = self.channel_file_limit(ctx)
            filesize = self.csv_filesize()
            if filesize > max_size:
                filesize_mb = self.file_size_in_mb(filesize)
                max_size_mb = self.file_size_in_mb(max_size)
                await ctx.reply(self.TOO_BIG.format(fs=filesize_mb, fl=max_size_mb))
            else:  # Valid file size; send file and reset counter.
                csv_file = discord.File(self.CSV_FP)
                await ctx.reply(self.MANUAL_EXPORT, file=csv_file)
                await self.config.msgs_since_export.set(0)

    # Utilities
    def log_dm_to_csv(self, msg: discord.Message):
        """Log a csv file to the CSV file"""
        aut = msg.author
        stamp = str(msg.created_at.utcnow())
        user_id = "ID: {}".format(aut.id)  # "ID:" prevents number truncations.
        username = str(aut)
        content = "Content: {}".format(msg.content)  # "Content:" prevents prefix issues.
        attach_str = ", ".join(attachment.url for attachment in msg.attachments)
        with open(self.CSV_FP, mode="a", newline="", errors="ignore", encoding="utf-8") as csv_f:
            csv_w = csv.writer(csv_f, delimiter=self.DELIMITER)
            if csv_f.tell() == 0:  # Empty file, append headers.
                csv_w.writerow(self.HEADER_LINE)
            csv_w.writerow((stamp, user_id, username, content, attach_str))

    def csv_filesize(self):
        """Get the size (in bytes) of the dm log csv file"""
        return os.path.getsize(self.CSV_FP)

    def channel_file_limit(self, ctx: Context):
        """Get the filesize limit (in bytes) of the context channel"""
        return ctx.guild.filesize_limit if ctx.guild else self.EIGHT_MB

    def file_size_in_mb(self, size_in_bytes: int) -> str:
        """Get a string representing the file size in MB"""
        return "{} MB".format(round(size_in_bytes / self.ONE_MB, 2))

    # Config
    async def red_delete_data_for_user(self, *, _requester, _user_id):
        """Do nothing, as any user data stored is for security purposes"""
        pass  # See __red_end_user_data_statement__.
