# Default Library.
import csv
import datetime
import re

# Required by Red.
import discord
import redbot.core.utils.menus as red_menu
from redbot.core import commands
from redbot.core import checks, Config, data_manager
from redbot.core.bot import Red


class FixedVarious(commands.Cog):
    """Various commands that cannot be classified under any other modules"""
    __author__ = "#s#8059"

    MAX_SLOWMODE_SECS = 60 * 60 * 6  # 6 hours.

    ROLE_ROW = "`{:0{}d}` {} • **{}**"
    GOTO_LINK = "<https://discordapp.com/channels/{gld_id}/{chn_id}/{msg_id}>"
    DELIMITED_TOO_LONG = ":x: Error: the delimiter must be exactly one character."
    GUILD_NO_ROLES = ":x: Error: This server has no roles."
    SLOWMODE_SET = ":white_check_mark: The slowmode in this channel has been set to {} second{}."
    SLOWMODE_OFF = ":put_litter_in_its_place: The slowmode in this channel has been disabled."
    SLOWMODE_INVALID_INT = ":x: Error: seconds must be a value between 0 and {} inclusive.".format(MAX_SLOWMODE_SECS)
    SLOWMODE_NO_PERMS = ":x: Error: I need Manage Channel permissions to set a slowmode!"

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=220420188059)
        self.FOLDER = str(data_manager.cog_data_path(self))

    # Events

    # Commands
    @commands.command()
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        """Get an enhanced version of someone's avatar"""
        if user is None:
            user = ctx.author
        avatar_url = user.avatar_url_as(static_format="png")

        embed = discord.Embed(colour=discord.Colour.blurple())
        embed.title = f"Avatar of {user.display_name}"
        embed.description = f"**Image link:**  [Click here]({avatar_url})"
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"User ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command()
    async def goto(self, ctx: commands.Context, channel: discord.TextChannel, message_id: int):
        """Get a link to jump to a certain message in a channel.

        channel must be a channel __on a server__ that the bot is on.
        If no valid message ID is used, the link will direct to where the message would have been in chat."""
        await ctx.send(self.GOTO_LINK.format(gld_id=ctx.guild.id, chn_id=channel.id, msg_id=message_id))

    @commands.command()
    @checks.admin_or_permissions(manage_channels=True)
    async def set_slowmode(self, ctx: commands.Context, seconds: int):
        """Set the Discord slowmode in this channel.

        seconds must be a number between 0 and 21600 (6 hours) inclusive.
        If seconds is 0, slowmode will be turned off.
        Requires Manage Channel permissions to be used."""
        if 0 <= seconds <= self.MAX_SLOWMODE_SECS:
            try:
                await ctx.channel.edit(slowmode_delay=seconds)
            except discord.Forbidden:  # Manage channel perms required.
                notice = self.SLOWMODE_NO_PERMS
            else:
                plural_s = "" if seconds == 1 else "s"
                notice = self.SLOWMODE_OFF if seconds == 0 else self.SLOWMODE_SET.format(seconds, plural_s)
        else:  # Invalid int for slowmode.
            notice = self.SLOWMODE_INVALID_INT
        await ctx.send(notice)

    @commands.command()
    async def spotify(self, ctx: commands.Context, user: discord.Member = None):
        """Check what someone is listening to"""
        if user is None:
            user = ctx.author
        act = user.activity
        if act and act.name == "Spotify":
            spot = act
            # Create value for song field.
            mins, secs = divmod(spot.duration.seconds, 60)
            song_length = "{:02d}:{:02d}".format(mins, secs)
            song_url = "https://open.spotify.com/track/{}".format(spot.track_id)
            song_value = "[{}]({}) ({})".format(spot.title, song_url, song_length)
            # Create embed.
            embed = discord.Embed(colour=spot.colour)
            embed.title = "Spotify of {} - Currently Playing".format(user.name)
            embed.add_field(name="Song", value=song_value, inline=False)
            embed.add_field(name="Artist", value=",".join(spot.artists), inline=False)
            embed.add_field(name="Album", value=spot.album, inline=False)
            embed.set_thumbnail(url=spot.album_cover_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("User is not currently listening to Spotify.")

    @commands.command(aliases=["timestamp"])
    async def snowflake(self, ctx: commands.Context, snowflake_id: int):
        """Convert a Snowflake ID to a datetime"""
        dt = discord.utils.snowflake_time(snowflake_id)
        time_str = dt.strftime("%A %d %B %Y at %H:%M:%S")
        await ctx.send("**Input:** {}\n**Time (UTC):** {}".format(snowflake_id, time_str))

    @commands.command()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_roles=True)
    async def member_csv(self, ctx: commands.Context, delimiter: str = "\t"):
        """Export the member list to a csv file

        The delimiter must be exactly one character (or undefined), and is a Tab by default.
        Note: this command also automatically stores the csv file in the cog's data folder."""
        gld = ctx.guild
        if len(delimiter) != 1:
            await ctx.send(self.DELIMITED_TOO_LONG)
        else:
            now = datetime.datetime.utcnow()
            srv_name = re.sub(r'\W+', '', gld.name)
            file_stamp = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H_%M_%S")

            csv_name = self.FOLDER + "/{} at {}.csv".format(srv_name, file_stamp)
            with open(csv_name, 'w', newline='', errors="ignore", encoding='utf-8') as csv_f:
                csv_w = csv.writer(csv_f, delimiter=delimiter)
                csv_w.writerow(["Join #", "Username", "UserID", "Joined at", "Account created at",
                                "Days since join", "Account age (days)", "Account age before join (days)"])
                for n, user in enumerate(sorted(gld.members, key=lambda x: x.joined_at)):
                    username = "{}#{}".format(user.name, user.discriminator)
                    userid = "ID: {}".format(user.id)  # Excel truncates plain IDs :(
                    join, born = user.joined_at, user.created_at
                    join_days, born_days = (now - join).days, (now - born).days
                    pre_days = (join - born).days

                    csv_w.writerow([n+1, username, userid, join, born, join_days, born_days, pre_days])

            await ctx.send(content="Here is a csv file with the member list.", file=discord.File(csv_name))

    @commands.command(name="role_stats", aliases=["rolestats"])
    @commands.guild_only()
    async def role_population_embed(self, ctx: commands.Context, hierarchy_sort: bool = None):
        """Show the amount of members of each role

        If `hierarchy_sort` is left empty, `no`, `n`, or `False`, the roles will be sorted on population.
        If `hierarchy_sort` is `yes`, `y`, or `True`, the roles will be sorted on hierarchy."""
        use_hierarchy = True if hierarchy_sort else False
        gld = ctx.guild
        role_tuples = ((r.mention, len(r.members), r.position) for r in gld.roles if not self.ignore_role(r))
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
            for i in range((role_count // 10) + 1):
                start = 10 * i
                end = start + 10 if role_count > (start + 10) else role_count
                field_name = "{}-{}".format(start + 1, end)
                field_value = "\n".join((self.ROLE_ROW.format((i + 1), width, t[0], t[1])
                                         for i, t in enumerate(sorted_roles[start:end], start=start)))
                field_list.append((field_name, field_value))
            # Check whether all fields can be sent within one embed, or whether a menu is needed.
            field_count = len(field_list)
            if field_count < 3:  # All fields fit in one embed.
                embed = discord.Embed(title="Server roles", description=desc_str, colour=discord.Colour.blurple())
                for (f_name, f_value) in field_list:
                    embed.add_field(name=f_name, value=f_value)
                embed.set_footer(text=embed_footer)
                await ctx.send(embed=embed)
            else:  # Multiple embeds needed, use pagified menu.
                embed_list = []
                for n, (f_name, f_value) in enumerate(field_list, start=1):
                    embed = discord.Embed(title="Server roles", description=desc_str, colour=discord.Colour.blurple())
                    embed.add_field(name=f_name, value=f_value)
                    footer_page_n = "{n} of {total}. ".format(n=n, total=field_count)
                    embed.set_footer(text=footer_page_n + embed_footer)
                    embed_list.append(embed)
                await red_menu.menu(ctx, embed_list, red_menu.DEFAULT_CONTROLS, timeout=30.0)

    @staticmethod
    def ignore_role(role: discord.Role) -> bool:
        """Check whether to ignore a role for the population embed

        If True, the role should be ignored. Else False."""
        return role.is_default() or not any(c != "\u2800" for c in role.name)
