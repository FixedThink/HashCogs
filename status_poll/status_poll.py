# Default Library.
import asyncio
import datetime as dt
from collections import Counter, defaultdict
from typing import List

# Used by Red.
import discord
from redbot.core import commands
from redbot.core import checks, Config
from redbot.core.bot import Red
from redbot.core.commands import Cog, Context
from redbot.core.utils.chat_formatting import humanize_timedelta


POLL_TIMEDELTA_CONVERTER = commands.TimedeltaConverter(
    minimum=dt.timedelta(seconds=15), maximum=dt.timedelta(minutes=30), default_unit="seconds")


class StatusPoll(Cog):
    """Poll a question through people's custom statuses"""
    __author__ = "#s#8059"

    ERROR = ":x: Error: "
    HASH_ERROR = ERROR + "Don't include the # in the tag. The command will add it for you."
    NO_RESPONSE = "**Results:** Nobody voted!"
    POLL_END = "---\n\nPoll ended! Results:\n"
    OPEN_POLL_START = "**{q}**\nVote by changing your custom status, with **#{ht}** at the end! You have {time}."
    MC_POLL_START = "**{q}**\nVote by setting your custom status to the number of choice, " \
                    "with **#{ht}** at the end! You have {time}. Options:\n{lst}"
    MC_ONE_OPTION = ERROR + "We're not in North Korea, please provide more than one option."
    MC_NO_OPTIONS = ERROR + "Please provide options!"
    POLL_TIME_SET = ":white_check_mark: Set the poll time to {}."

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.config = Config.get_conf(self, identifier=859991)
        self.config.register_guild(poll_seconds=90)

    # Events

    # Commands
    @commands.guild_only()
    @checks.admin_or_permissions(administrator=True)
    @commands.command()
    async def poll_duration(self, ctx: Context, duration: POLL_TIMEDELTA_CONVERTER):
        """Set the duration of polls

        The duration must be at least 15 seconds and at most 30 minutes"""
        await self.config.guild(ctx.guild).poll_seconds.set(duration.total_seconds())
        await ctx.send(self.POLL_TIME_SET.format(humanize_timedelta(timedelta=duration)))

    @commands.guild_only()
    @checks.admin_or_permissions(manage_messages=True)
    @commands.command(aliases=["simple_poll"])
    async def open_poll(self, ctx: Context, tag: str, *, question: str):
        """Poll a question through people's custom status

        Answers are case-insensitive, i.e. answers get combined if they're identical besides case"""
        if self.attempts_mass_mention(ctx.message.content.lower()):
            final_msg = "Nice try."
        elif "#" in tag:
            final_msg = self.HASH_ERROR
        else:
            hashtag = tag.lower()
            seconds = await self.config.guild(ctx.guild).poll_seconds()

            await ctx.send(
                self.OPEN_POLL_START.format(q=question, ht=hashtag, time=humanize_timedelta(seconds=seconds)))
            await asyncio.sleep(seconds - 10)
            await ctx.send("10 seconds left!")
            await asyncio.sleep(10)
            results = Counter()
            case_dict = defaultdict(Counter)
            for vote in self.get_votes_by_hashtag(ctx, hashtag):
                vote_lower = vote.lower()
                case_dict[vote_lower][vote] += 1
                results[vote_lower] += 1
            if not results:
                final_msg = self.NO_RESPONSE
            else:
                width = len(str(len(results)))
                line_list = []
                for n, (option, count) in enumerate(results.most_common(), start=1):
                    cased_option = case_dict[option].most_common(1)[0][0]  # Key (=str) of most common element.
                    to_append = "`{n:0{w}d}` **{opt}** - {x} vote{s}".format(n=n, w=width, opt=cased_option,
                                                                             x=count, s=self.plural(count))
                    line_list.append(to_append)
                final_msg = self.POLL_END + "\n".join(line_list)
        await ctx.send(final_msg)

    @commands.guild_only()
    @checks.admin_or_permissions(manage_messages=True)
    @commands.command(aliases=["number_poll"])
    async def multiple_choice(self, ctx: Context, tag: str, *, question_and_options: str):
        """Poll a multiple choice question through people's custom status

        The amount of options are set by the author.
        The questions and all answers must be separated by ;"""
        if self.attempts_mass_mention(ctx.message.content.lower()):
            final_msg = "Nice try."
        elif "#" in tag:
            final_msg = self.HASH_ERROR
        else:
            options = [x.strip() for x in question_and_options.split(";") if x.strip()]
            question = options.pop(0)  # Extract the questions from the answers.
            option_count = len(options)
            if option_count == 0:
                final_msg = self.MC_NO_OPTIONS
            elif option_count == 1:
                final_msg = self.MC_ONE_OPTION
            else:
                hashtag = tag.lower()
                seconds = await self.config.guild(ctx.guild).poll_seconds()
                mc_str = "\n".join((f"**{n}** - {v}" for n, v in enumerate(options, start=1)))
                await ctx.send(self.MC_POLL_START.format(
                    q=question, ht=hashtag, time=humanize_timedelta(seconds=seconds), lst=mc_str))
                await asyncio.sleep(seconds - 10)
                await ctx.send("10 seconds left!")
                await asyncio.sleep(10)
                results = Counter({v: 0 for v in range(1, option_count + 1)})
                for vote in self.get_votes_by_hashtag(ctx, hashtag):
                    vote_number = int(vote) if vote.isdigit() else 0
                    if 0 < vote_number <= option_count:
                        results[vote_number] += 1
                if not results:
                    final_msg = self.NO_RESPONSE
                else:
                    width = len(str(len(results)))
                    line_list = []
                    for n, (answer_n, count) in enumerate(results.most_common(), start=1):
                        answer = options[answer_n - 1]
                        to_append = "`{n:0{w}d}` **{opt}** - {x} vote{s}".format(n=n, w=width, opt=answer,
                                                                                 x=count, s=self.plural(count))
                        line_list.append(to_append)
                    final_msg = self.POLL_END + "\n".join(line_list)
        await ctx.send(final_msg)

    # Utilities
    @staticmethod
    def plural(n: int) -> str:
        """Determine whether plural should be used or not."""
        return "" if n == 1 else "s"

    @staticmethod
    def attempts_mass_mention(text: str) -> bool:
        return "@everyone" in text or "@here" in text

    def get_votes_by_hashtag(self, ctx: Context, hashtag: str) -> List[str]:
        """Get a list of responses to a poll based on a hashtag in someone's custom status"""
        votes = []
        for m in ctx.guild.members:
            custom_activity = discord.utils.get(m.activities, type=4)
            if custom_activity:
                status: str = custom_activity.state
                if status:
                    try:
                        choice, m_tag = status.rsplit("#", 1)
                    except ValueError:
                        pass
                    else:
                        if m_tag.lower() == hashtag and not self.attempts_mass_mention(choice):
                            votes.append(choice)
        return votes
