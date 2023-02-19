from __future__ import annotations

# Standard library.
import asyncio
import logging

# Required by Red.
import discord
from redbot.core import commands, Config
from redbot.core.bot import Red
from redbot.core.commands import Cog, Context
from redbot.core.utils.chat_formatting import box
from redbot.core.utils.menus import SimpleMenu


class WelcomeModeration(Cog):
    """
    Use custom welcome messages and a verification role on a guild-by-guild basis.

    The verification role will be given to a member if it obtains any role in whatever way,
    except if the role obtained is blacklisted in the settings.

    The use for this is to have one role to set up permissions for. If used properly,
    this role can only be given to those who satisfy the Discord verification level.
    Example usage: a guild that has a role for each rank of a certain game,
    but want one role to manage the permissions of all people that have a role
    (whilst not giving those perms to `@everyone`).

    Both the welcome functionality and verification functionality are optional and customisable.
    """

    __author__ = "#s#8059"
    # Emoji.
    BIN = ":put_litter_in_its_place: "
    DONE = ":white_check_mark: "

    ROLE_ASSIGN_ERROR = (
        "ERROR: Cannot assign the verified role without the `Manage Roles` permission! "
        "Server ID: {}"
    )
    NO_VER_ROLE = (
        ":x: Verification role not found. Please make sure the role is configured and still exists."
    )
    OFF = "Disabled"
    ADDED_VER_ROLE = "Added the verified role to {}."
    UNASSIGN_TITLE = "Members without the verification role"
    # verified_all_members strings.
    ALL_START = (
        "Verified check for all **`{}`** members started. "
        "This may take a while, updates will be sent."
    )
    ALL_UPDATE = "**`{}`** out of `{}` members done. Current user: {}"
    # Ignored roles command strings.
    TO_IGNORE_SET = DONE + "Successfully set the roles to ignore. Amount of ignored roles: {}"
    TO_IGNORE_RESET = BIN + "Successfully cleared the role to ignore."
    # Auto-verification strings.
    ROLE_RECEIVED = "{} you have received a role."
    DELAY_NOTICE = ROLE_RECEIVED + "\nYou will gain access to the rest of the server in {} seconds."
    # Delay command strings.
    DELAY_SET = DONE + "Successfully set the verified role assignment delay to {} seconds."
    DELAY_RESET = BIN + "Successfully deleted the verified role assignment delay."
    UNVERIFIED = (
        "Unverified member count: **{}** \nList of unverified members (sorted on join date):\n{}"
    )
    # Configuration overview strings.
    WM_STATUS_TITLE = "WelcomeModeration configuration for this server"
    # Channel configuration strings.
    CHANNEL_SET = (
        DONE + "Successfully set the {m} messages to {c}. "
        "If you want to disable welcome messages, perform the same command in __this__ channel."
    )
    CHANNEL_RESET = (
        BIN + "Successfully disabled the {m} messages. If you want to re-enable {m} messages, "
        "use this command in the channel you want to enable it in."
    )
    # Role configuration strings.
    ROLE_SET = DONE + "Successfully set the verification role."
    ROLE_RESET = (
        BIN + "Verification role cleared. This also disables its functionality. "
        "If you want to re-enable it, use this command provided with a role."
    )
    # Welcome message strings.
    WELCOME_MSG_SET = DONE + "Successfully set the welcome message."
    WELCOME_MSG_RESET = BIN + "Welcome message cleared."
    # Other constants.
    DEFAULT_VERIFIED_SECONDS = 30
    MAX_PAGE_SIZE = 20

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot
        self.log = logging.getLogger("red.hash_cogs.welcome_moderation")
        self.config = Config.get_conf(self, identifier=7509, force_registration=True)
        self.config.register_guild(
            verified_role_id=None,
            ignored_roles=[],  # Set with role ids.
            verified_delay_seconds=self.DEFAULT_VERIFIED_SECONDS,
            confirm_channel_id=None,
            log_channel_id=None,
            welcome_channel_id=None,
            welcome_message="Welcome, {user}!",
        )

    # Events
    @Cog.listener()
    async def on_member_join(self, member):
        """Sends a customisable welcome message to a guild"""
        gld = member.guild
        welcome_id = await self.config.guild(gld).welcome_channel_id()
        if welcome_id and not member.bot:  # Don't greet bots.
            welcome_message = await self.config.guild(gld).welcome_message()
            welcome_channel = gld.get_channel(welcome_id)
            await welcome_channel.send(welcome_message.format(user=member.mention))

    @Cog.listener()
    async def on_member_update(self, m_old, m_new):
        """Give a member the verified role if they received an eligible role"""
        gld = m_new.guild

        new_role_id = next((r.id for r in m_new.roles if r not in m_old.roles), False)
        if new_role_id:  # Check whether the user gained a role.
            verified_id = await self.config.guild(gld).verified_role_id()
            ignored_roles = await self.config.guild(gld).ignored_roles()

            # Check if the gained role is not the verified role itself,
            # and whether it should be ignored.
            new_role_eligible = new_role_id != verified_id and new_role_id not in ignored_roles
            # Check if the verified role is configured,
            # and whether the user does not have the role yet.
            can_verify_user: bool = verified_id is not None and verified_id not in (
                r.id for r in m_old.roles
            )
            if new_role_eligible and can_verify_user:
                assignment_delay = await self.config.guild(gld).verified_delay_seconds()
                confirmation = await self.config.guild(gld).confirm_channel_id()
                if confirmation and not m_new.bot:  # Bots are not conscious (for now...).
                    if assignment_delay:
                        confirm_msg = self.DELAY_NOTICE.format(m_new.mention, assignment_delay)
                    else:
                        confirm_msg = self.ROLE_RECEIVED.format(m_new.mention)
                    confirm_channel = gld.get_channel(confirmation)
                    await confirm_channel.send(confirm_msg)
                if assignment_delay:
                    await asyncio.sleep(assignment_delay)
                try:
                    check_role = discord.utils.get(gld.roles, id=verified_id)
                    # Assign the check role.
                    await m_new.add_roles(check_role, reason="WelcomeModeration verification.")
                except discord.errors.Forbidden:
                    self.log.error(self.ROLE_ASSIGN_ERROR.format(gld.id))

                send_log = await self.config.guild(gld).log_channel_id()
                self.log.debug(self.ADDED_VER_ROLE.format(m_new.id))
                if send_log:
                    log_msg = self.ADDED_VER_ROLE.format(m_new.mention)
                    log_channel = gld.get_channel(send_log)
                    await log_channel.send(log_msg)

    # Commands
    @commands.command(name="verified_all")
    @commands.guild_only()
    @commands.is_owner()
    async def verified_all_members(self, ctx: Context):
        """Check all guild members for verified role eligibility"""
        gld = ctx.guild
        member_count = gld.member_count
        verified_id = await self.config.guild(gld).verified_role_id()
        verified_role = discord.utils.get(gld.roles, id=verified_id)
        if verified_role:
            await ctx.send(self.ALL_START.format(member_count))
            for i, user in enumerate(gld.members, start=1):
                ignored_roles = await self.config.guild(gld).ignored_roles()
                # Check if someone has a role that is not the default role, and not an ignored role.
                if any(not r.is_default() and r.id not in ignored_roles for r in user.roles):
                    if verified_role in user.roles:
                        self.log.debug(f"{i} ALREADY VERIFIED, {user.id}")
                    else:
                        try:
                            await user.add_roles(verified_role)
                            self.log.debug(f"{i} ELIGIBLE, {user.id}")
                        except discord.errors.Forbidden:
                            self.log.error(self.ROLE_ASSIGN_ERROR.format(gld.id))
                else:
                    self.log.debug(f"{i} INELIGIBLE, {user.id}")
                if i % 20 == 0:
                    to_send = self.ALL_UPDATE.format(i, member_count, user.name)
                    await ctx.send(to_send)
            to_send = f"All **`{member_count}`** members done!"
            await ctx.tick()
        else:
            to_send = self.NO_VER_ROLE
        await ctx.send(to_send)

    @commands.command(aliases=["unassigned", "no_check"])
    @commands.guild_only()
    @commands.mod_or_permissions(manage_roles=True)
    async def unverified(self, ctx: Context):
        """Check who does not have the verified role"""
        gld = ctx.guild
        verified_id = await self.config.guild(gld).verified_role_id()
        verified_role = discord.utils.get(gld.roles, id=verified_id)

        if verified_role:  # Create list of unverified users.
            unverified_members = sorted(
                (m for m in gld.members if verified_role not in m.roles), key=lambda x: x.joined_at
            )
            unverified_n = len(unverified_members)
            embed_list = []
            embed_count = 1 + ((unverified_n - 1) // self.MAX_PAGE_SIZE)
            for i in range(embed_count):
                embed = discord.Embed(colour=discord.Colour.blurple(), title=self.UNASSIGN_TITLE)
                embed.description = "Total unverified members: {}".format(unverified_n)
                embed.set_footer(text=f"Page {i + 1} of {embed_count}.")

                # Get page range
                start: int = i * self.MAX_PAGE_SIZE
                # End is either the start + page size, or the remaining amount of members.
                past_end: int = min(unverified_n, start + self.MAX_PAGE_SIZE)
                field_str = "\n".join(
                    "`{}` {}".format(mem_i + 1, unverified_members[mem_i].mention)
                    for mem_i in range(start, past_end)
                )
                embed.add_field(name=f"{start + 1}-{past_end}", value=field_str)
                embed_list.append(embed)
            await SimpleMenu(embed_list).start(ctx)
        else:
            await ctx.send(self.NO_VER_ROLE)

    @commands.command(name="wm_status")
    @commands.guild_only()
    @commands.admin()
    async def view_config(self, ctx: Context):
        """See how the welcome moderation is configured for this server"""
        gld = ctx.guild
        embed = discord.Embed(title=self.WM_STATUS_TITLE, colour=discord.Colour.green())
        config_dict = await self.config.guild(gld).all()
        # Add the welcome message to the embed description. (not in a field due to character limit)
        welcome_msg = config_dict["welcome_message"]
        embed.description = box(welcome_msg) if welcome_msg else "`welcome message not set`"
        # Add all other configurations to their own fields.
        welcome_id = config_dict["welcome_channel_id"]
        embed.add_field(name="Welcome channel", value=self.channel_mention(welcome_id))

        log_id = config_dict["log_channel_id"]
        embed.add_field(name="Log channel", value=self.channel_mention(log_id))

        confirm_id = config_dict["confirm_channel_id"]
        embed.add_field(name="Confirmation channel", value=self.channel_mention(confirm_id))

        role_id = config_dict["verified_role_id"]
        role_str = (discord.utils.get(gld.roles, id=role_id)).mention if role_id else self.OFF
        embed.add_field(name="Verified role", value=role_str)

        delay = config_dict["verified_delay_seconds"]
        embed.add_field(name="Verified role delay", value=f"{delay} seconds" if delay else self.OFF)

        block_roles = config_dict["ignored_roles"]
        block_str = (
            ", ".join((discord.utils.get(gld.roles, id=r_id)).mention for r_id in block_roles)
            if block_roles
            else "No ignored roles."
        )
        embed.add_field(name="Ignored roles", value=block_str)
        await ctx.send(embed=embed)

    @commands.group(name="wm_set", invoke_without_command=True)
    @commands.guild_only()
    @commands.admin()
    async def _config_guild(self, ctx: Context):
        """Commands to configure automated messages on the guild

        **WARNING:** If you use `ignored_roles`, `verified_role` and `welcome_message`
         without a value, it will __reset__ its configuration!
        Check the configuration first before you accidentally remove something.

        **NOTE:** If you want to use any of these commands,
         please consult their help messages first (see footer).
        """
        await ctx.send_help()

    @_config_guild.command(name="verified_role")
    @commands.guild_only()
    @commands.admin()
    async def set_verified_role(self, ctx: Context, role: discord.Role = None):
        """Set the role that will be given to verified members

        If no role is provided, the currently set role will be deleted.
        Additionally, the verification functionality will be disabled."""
        if not role:
            to_send = self.ROLE_RESET
            await self.config.guild(ctx.guild).verified_role_id.clear()
        else:
            to_send = self.ROLE_SET
            await self.config.guild(ctx.guild).verified_role_id.set(role.id)
        await ctx.tick()
        await ctx.send(to_send)

    @_config_guild.command(name="ignored_roles")
    @commands.guild_only()
    @commands.admin()
    async def set_verified_ignored_roles(self, ctx: Context, *roles: discord.Role):
        """Set the roles to be ignored by the role verification.

        You can ignore as many roles as you'd like, but you must put them all in the same command.
        If the bot does not recognise any of the roles that you provide,
         the command won't be executed.
        """
        if len(roles) == 0:  # No roles provided, clear the config.
            to_send = self.TO_IGNORE_RESET
            await self.config.guild(ctx.guild).ignored_roles.clear()
        else:
            to_send = self.TO_IGNORE_SET.format(len(roles))
            await self.config.guild(ctx.guild).ignored_roles.set([i.id for i in roles])
        await ctx.tick()
        await ctx.send(to_send)

    @_config_guild.command(name="delay")
    @commands.guild_only()
    @commands.admin()
    async def set_verified_delay(self, ctx: Context, seconds: int):
        """Set the delay for the assignment of the verified role

        If the amount of seconds is 0 (or lower), the delay will be disabled."""
        gld = ctx.guild
        if seconds > 0:
            await self.config.guild(gld).verified_delay_seconds.set(seconds)
            to_send = self.DELAY_SET.format(seconds)
        else:
            await self.config.guild(gld).verified_delay_seconds.set(False)
            to_send = self.DELAY_RESET
        await ctx.tick()
        await ctx.send(to_send)

    @_config_guild.command(name="confirmation_channel")
    @commands.guild_only()
    @commands.admin()
    async def set_confirmation_channel(self, ctx: Context):
        """Set the current channel as the verified confirmation channel

        Confirmations will be disabled if the command is used in the channel
         where messages are currently sent to.
        """
        gld = ctx.guild
        channel = ctx.channel
        m_str = "verified confirmation"
        if channel.id == await self.config.guild(gld).confirm_channel_id():
            to_send = self.CHANNEL_RESET.format(m=m_str)
            await self.config.guild(gld).confirm_channel_id.clear()
        else:
            to_send = self.CHANNEL_SET.format(m=m_str, c=channel.mention)
            await self.config.guild(gld).confirm_channel_id.set(channel.id)
        await ctx.tick()
        await ctx.send(to_send)

    @_config_guild.command(name="log_channel")
    @commands.guild_only()
    @commands.admin()
    async def set_log_channel(self, ctx: Context):
        """Set the current channel as the verified log channel

        Logs will be disabled if the command is used in the channel
         where messages are currently sent to.
        """
        gld = ctx.guild
        channel = ctx.channel
        m_str = "verified log"
        if channel.id == await self.config.guild(gld).log_channel_id():
            to_send = self.CHANNEL_RESET.format(m=m_str)
            await self.config.guild(gld).log_channel_id.clear()
        else:
            to_send = self.CHANNEL_SET.format(m=m_str, c=channel.mention)
            await self.config.guild(gld).log_channel_id.set(channel.id)
        await ctx.tick()
        await ctx.send(to_send)

    @_config_guild.command(name="welcome_channel")
    @commands.guild_only()
    @commands.admin()
    async def set_welcome_channel(self, ctx: Context):
        """Set the current channel as the welcome message channel

        Welcome messages will be disabled if the command is used in the channel
         where messages are currently sent to.
        """
        gld = ctx.guild
        channel = ctx.channel
        m_str = "welcome"
        if channel.id == await self.config.guild(gld).welcome_channel_id():
            to_send = self.CHANNEL_RESET.format(m=m_str)
            await self.config.guild(gld).welcome_channel_id.clear()
        else:
            to_send = self.CHANNEL_SET.format(m=m_str, c=channel.mention)
            await self.config.guild(gld).welcome_channel_id.set(channel.id)
        await ctx.tick()
        await ctx.send(to_send)

    @_config_guild.command(name="welcome_message")
    @commands.guild_only()
    @commands.admin()
    async def set_welcome_message(self, ctx: Context, *, message_text=None):
        """Set the message to be used when a new member joins

        In order to specify a user mention, please use `{user}` inside the text.
        Please avoid the usage of any other curly brackets."""
        if message_text is None:
            to_send = self.WELCOME_MSG_RESET
            await self.config.guild(ctx.guild).welcome_message.clear()
        else:
            to_send = self.WELCOME_MSG_SET
            await self.config.guild(ctx.guild).welcome_message.set(message_text)
        await ctx.tick()
        await ctx.send(to_send)

    # Utilities
    def channel_mention(self, channel_id: int | None) -> str:
        """Return a channel ID (if provided) as a channel mention, else give a backup string"""
        return f"<#{channel_id}>" if channel_id else self.OFF
