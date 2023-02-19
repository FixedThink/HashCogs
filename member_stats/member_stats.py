# Default Library.
import csv
import datetime
import datetime as dt
import re

# Required by Red.
import discord
from redbot.core import commands, Config, data_manager
from redbot.core.bot import Red
from redbot.core.utils.menus import SimpleMenu


class MemberStats(commands.Cog):
    """Commands to gain insights into your server's population"""

    __author__ = "#s#8059"

    # Messages.
    X = ":x: Error: "
    DELIMITED_TOO_LONG = X + "the delimiter must be exactly one character."
    GUILD_NO_ROLES = X + "this server has no roles."
    FILE_MSG = "Here is a csv file with the member list."
    CSV_TOO_BIG = X + "the member csv is too big to send here!\n\n**Size:** {fs}\n**Limit:** {fl}"

    # Other constants.
    ROLE_ROW = "`{:0{}d}` {} • **{}**"
    FIELD_N = 10
    ONE_MB = 1024 * 1024  # From bytes to MB.
    MEMBER_CSV_HEADER = (
        "Join #",
        "Username",
        "UserID",
        "Joined at",
        "Account created at",
        "Days since join",
        "Account age (days)",
        "Account age before join (days)",
    )

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=220420188059)
        self.FOLDER = str(data_manager.cog_data_path(self))

    # Events

    # Commands
    @commands.command()
    @commands.guild_only()
    @commands.mod_or_permissions(manage_roles=True)
    @commands.bot_has_permissions(attach_files=True)
    async def member_csv(self, ctx: commands.Context, delimiter: str = "\t"):
        """Export the member list to a csv file

        The delimiter must be exactly one character (or undefined), and is a Tab by default.
        Note: this command also automatically stores the csv file in the cog's data folder."""
        gld = ctx.guild
        if len(delimiter) != 1:
            await ctx.send(self.DELIMITED_TOO_LONG)
        else:
            srv_name = re.sub(r"\W+", "", gld.name)
            file_stamp = dt.datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")

            csv_name = self.FOLDER + "/{} at {}.csv".format(srv_name, file_stamp)
            now = dt.datetime.now(datetime.timezone.utc)
            with open(csv_name, "w", newline="", errors="ignore", encoding="utf-8") as csv_f:
                csv_w = csv.writer(csv_f, delimiter=delimiter)
                csv_w.writerow(self.MEMBER_CSV_HEADER)
                for n, user in enumerate(sorted(gld.members, key=lambda x: x.joined_at)):
                    username = "{}#{}".format(user.name, user.discriminator)
                    userid = "ID: {}".format(user.id)  # Excel truncates plain IDs :(
                    join, born = user.joined_at, user.created_at
                    join_days, born_days = (now - join).days, (now - born).days
                    pre_days = (join - born).days
                    csv_w.writerow(
                        [n + 1, username, userid, join, born, join_days, born_days, pre_days]
                    )
                csv_filesize: int = csv_f.tell()  # In bytes.
            size_limit = ctx.guild.filesize_limit
            if csv_filesize > size_limit:
                fs = self.file_size_in_mb(csv_filesize)
                fl = self.file_size_in_mb(size_limit)
                await ctx.reply(self.CSV_TOO_BIG.format(fs=fs, fl=fl))
            else:
                await ctx.reply(content=self.FILE_MSG, file=discord.File(csv_name))

    @commands.command(name="role_stats", aliases=["rolestats"])
    @commands.guild_only()
    async def role_population_embed(self, ctx: commands.Context, hierarchy_sort: bool = None):
        """Show the amount of members of each role

        If `hierarchy_sort` is left empty, `no`, `n`, or `False`,
         the roles will be sorted on population.
        If `hierarchy_sort` is `yes`, `y`, or `True`,
         the roles will be sorted on hierarchy."""
        use_hierarchy = True if hierarchy_sort else False
        gld = ctx.guild
        role_tuples = (
            (r.mention, len(r.members), r.position) for r in gld.roles if not self.ignore_role(r)
        )
        if use_hierarchy:
            sorted_roles = sorted(role_tuples, key=lambda x: x[2], reverse=True)
            embed_footer = "Roles sorted on hierarchy."
        else:
            sorted_roles = sorted(role_tuples, key=lambda x: (x[1], x[2]), reverse=True)
            embed_footer = "Roles sorted on role member count."

        role_count = len(sorted_roles)
        if role_count == 0:
            await ctx.send(self.GUILD_NO_ROLES)
        else:  # At least one role.
            desc_str = "Total members: **{}**".format(gld.member_count)
            width = len(str(role_count))
            # Split the role list into fields with a maximum of 10 rows.
            field_list = []
            field_count = ((role_count - 1) // self.FIELD_N) + 1
            for i in range(field_count):
                start = self.FIELD_N * i
                end = start + self.FIELD_N if role_count > (start + self.FIELD_N) else role_count
                field_name = "{}-{}".format(start + 1, end)
                field_value = "\n".join(
                    (
                        self.ROLE_ROW.format((i + 1), width, t[0], t[1])
                        for i, t in enumerate(sorted_roles[start:end], start=start)
                    )
                )
                field_list.append((field_name, field_value))
            # Check whether all fields can be sent within one embed, or whether a menu is needed.
            if field_count <= 2:  # All fields fit in one embed.
                embed = discord.Embed(
                    title="Server roles", description=desc_str, colour=discord.Colour.blurple()
                )
                for f_name, f_value in field_list:
                    embed.add_field(name=f_name, value=f_value)
                embed.set_footer(text=embed_footer)
                await ctx.send(embed=embed)
            else:  # Multiple embeds needed, use pagified menu.
                embed_list = []
                for n, (f_name, f_value) in enumerate(field_list, start=1):
                    embed = discord.Embed(
                        title="Server roles", description=desc_str, colour=discord.Colour.blurple()
                    )
                    embed.add_field(name=f_name, value=f_value)
                    footer_page_n = f"{n} of {field_count}. "
                    embed.set_footer(text=footer_page_n + embed_footer)
                    embed_list.append(embed)
                await SimpleMenu(embed_list).start(ctx)

    # Utilities.
    @staticmethod
    def ignore_role(role: discord.Role) -> bool:
        """Check whether to ignore a role for the population embed

        If True, the role should be ignored. Else False."""
        return role.is_default() or not any(c != "\u2800" for c in role.name)

    def file_size_in_mb(self, size_in_bytes: int) -> str:
        """Get a string representing the file size in MB"""
        return "{} MB".format(round(size_in_bytes / self.ONE_MB, 2))

    # Config
    async def red_delete_data_for_user(self, *, _requester, _user_id):
        """Do nothing, as no user data is stored."""
        pass
