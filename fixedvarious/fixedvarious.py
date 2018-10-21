import csv
import datetime
import re

import discord
from redbot.core import commands  # Changed from discord.ext
from redbot.core import checks, Config, data_manager


class FixedVarious:
    """Various commands that cannot be classified under any other HashCogs"""
    __author__ = "#s#8059"

    ROLE_ROW = "`{:02d} \u200b` {} - **{}**"
    MAX_RMSE = "**Number:** {}\nMax sum of squares: {}\nMax square per position: {}\n\nMax RMSE: {:0.3f}"
    GOTO_LINK = "<https://discordapp.com/channels/{gld_id}/{chn_id}/{msg_id}>"

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=220420188059)
        self.FOLDER = str(data_manager.cog_data_path(self))

    # Events

    # Commands
    @commands.command()
    async def avatar(self, ctx, user: discord.Member=None):
        """Get an enhanced version of someone's avatar"""
        if user is None:
            user = ctx.author
        avatar_url = user.avatar_url

        embed = discord.Embed(colour=discord.Colour.blurple())
        embed.title = f"Avatar of {user.display_name}"
        embed.description = f"**Image link:**  [Click here]({avatar_url})"
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"User ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command()
    async def goto(self, ctx, channel: discord.TextChannel, message_id: int):
        """Get a link to jump to a certain message in a channel.

        channel must be a channel __on a server__ that the bot is on.
        If no valid message ID is used, the link will direct to where the message would have been in chat."""
        await ctx.send(self.GOTO_LINK.format(gld_id=ctx.guild.id, chn_id=channel.id, msg_id=message_id))

    @commands.command()
    async def spotify(self, ctx, user: discord.Member=None):
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

            embed = discord.Embed(colour=spot.colour)
            embed.title = "Spotify of {} - Currently Playing".format(user.name)

            embed.add_field(name="Song", value=song_value, inline=False)
            embed.add_field(name="Artist", value=",".join(spot.artists), inline=False)
            embed.add_field(name="Album", value=spot.album, inline=False)
            embed.set_thumbnail(url=spot.album_cover_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send("User is not currently listening to Spotify.")

    @commands.command(name="rmse")
    async def ranking_max_rmse(self, ctx, n: int):
        """Calculates the biggest RMSE that two different rankings of n items could have

        n must be an integer number."""
        max_avg_sq = (n ** 2 - 1) // 3  # Adaption of Spearman's correlation.
        sum_sq = max_avg_sq * 43
        max_root = max_avg_sq ** 0.5
        await ctx.send(self.MAX_RMSE.format(n, sum_sq, max_avg_sq, max_root))

    @commands.command(aliases=["timestamp"])
    async def snowflake(self, ctx, snowflake_id: int):
        """Convert a Snowflake ID to a datetime"""
        dt = discord.utils.snowflake_time(snowflake_id)
        time_str = dt.strftime("%A %d %B %Y at %H:%M:%S")
        await ctx.send("**Input:** {}\n**Time (UTC):** {}".format(snowflake_id, time_str))

    @commands.command()
    @commands.guild_only()
    @checks.mod_or_permissions(manage_roles=True)
    async def member_csv(self, ctx, delimiter: str= ";"):
        """Export the member list to a csv file

        The delimiter must be exactly one character (or undefined).
        Note: this command also automatically stores the csv file in the cog's data folder."""
        gld = ctx.guild
        if len(delimiter) != 1:
            await ctx.send(":x: Error: the delimiter must be exactly one character.")
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

    @commands.command(name="roles")
    @commands.guild_only()
    async def role_population_embed(self, ctx, hierarchy_sort: bool=None):
        """Show the amount of members of each role

        If `hierarchy_sort` is left empty, `no`, `n`, or `False`, the roles will be sorted on population.
        If `hierarchy_sort` is `yes`, `y`, or `True`, the roles will be sorted on hierarchy."""
        use_hierarchy = True if hierarchy_sort else False
        gld = ctx.guild
        role_tuples = ((r.mention, len(r.members), r.position) for r in gld.roles if not r.is_default())
        if use_hierarchy:
            sorted_roles = sorted(role_tuples, key=lambda x: x[2], reverse=True)
            embed_footer = "Roles sorted on hierarchy."
        else:
            sorted_roles = sorted(role_tuples, key=lambda x: (x[1], x[2]), reverse=True)
            embed_footer = "Roles sorted on role member count."

        role_count = len(sorted_roles)
        if role_count > 0:
            embed = discord.Embed(title="Server roles", colour=discord.Colour.blurple())
            # Split the role list into fields with a maximum of 10 rows.
            for i in range((role_count // 10) + 1):
                start = 10 * i
                end = start + 10 if role_count > (start + 10) else role_count
                field_value = "\n".join((self.ROLE_ROW.format((i + 1), t[0], t[1])
                                         for i, t in enumerate(sorted_roles[start:end], start=start)))
                embed.add_field(name="{}-{}".format(start + 1, end), value=field_value)

            embed.description = "Total members: **{}**".format(gld.member_count)
            embed.set_footer(text=embed_footer)
            await ctx.send(embed=embed)
        else:
            await ctx.send(":x: Error: This server has no roles.")
    # Utilities

    # Config 
