# HashCogs

Hey there!

This is my first GitHub repository, meaning that I have yet to properly find out how GitHub works.

Please treat it gently, as it *may* need to be polished and cleaned up etc!

All the cogs listed on here should work properly though, so if there are any issues do not hesitate to inform me!

**None of the cogs in this repository require additional packages!**

# About the cogs

## assign_roles
This is the RedBot V3 version of the assign_roles cog, which was published on [ZeLarpMaster's V2 repository](https://github.com/ZeLarpMaster/ZeCogs) as I did not have a GitHub account back then.

The cog essentially simulates the Manage Roles permission, but for specific to pairs of roles. For example, role A can be allowed to give role B to anyone else, without allowing the same role A to give role C, D, etc.

#### Example usage
This cog makes it possible to facilitate "Helpers" on the server by allowing them to assign some harmless roles, such as platform roles, without allowing them to assign some more powerful roles like a bot role.

## welcome_moderation

This bot allows you to set custom welcome messages, and to set a verification role on a guild-by-guild basis. Both the welcome functionality and verification functionality are optional and customisable, meaning that you can use the welcome messages whilst not using the verification roles, and vice versa.

#### Welcome message
The channel in which the welcome message will be sent can be easily configured by performing a command in the desired channel. Additionally, the welcome message can be modified directly through the Discord client, rather than having to save a text file somewhere or something similar. This welcome message allows you to put a user mention anywhere in the message by putting `{user}` where you want the message to be. Additionally, the bot ignores other bots being added, thus making someone able to add bots without generating a welcome message.

#### Verification role
If enabled, the verification role will be given to a member if it obtains any role in whatever way, except if the role obtained is configured to be blacklisted. By doing so, a guild can have one role to give some basic permissions to (such as change nickname permissions), whilst not giving these permissions to `@everyone` for moderation reasons. If used properly, this role can be configured such that it's only given to those who satisfy the Discord verification level.
Optionally, the bot can send logs of verification role additions in a certain channel. Additionally, a delay for obtaining the verification role may be configured.

#### Example usages
- A guild wants to give every member some basic permissions, but only if they have given themselves a role from a list of assignable roles. Rather than configuring appropriate permissions for each of the assignable roles, and having to adapt all of the roles in every channel in case of a rule change, the verification role could add as an "umbrella role" which would be only one that needs to be changed.
- A guild may have a human barrier to roles on a server, to prevent giving access to certain places for those who aren't authorised to be on the server. With such a role, authorisation can be automatically granted if a moderator gives a user any role available (not counting those that are added to a blacklist).

## FixedVarious

This is the cog where I add general-purpose commands to, that do not require any configuration and are generally standalone commands. In the future, it may occur that a particular command will be moved to a separate cog to enhance its functionality with related commands, or removed altogether if it's no longer deemed useful.

#### Current commands (as of 3 March 2019)
- **avatar** – Allows any user to see their own avatar (or someone else's) in a rich embed. In the embed, there is also a hyperlink that allows any user to download their avatar (in PNG or, if animated, GIF format).
- **goto** – Allows any user to "jump" to a certain moment in time in a certain channel, with the used of a snowflake ID. The output of the command will be a Discord link. Please be aware that Discord can possibly be bugged after clicking such a link if the snowflake ID does not belong to an existing message in that channel.
- **member_csv** – Allows users with `Manage Roles` permission to download the member list of a server in csv format. As the delimiter for csv files varies from country to country, this command allows the user to modify the delimiter with an argument.
- **roles** – This command shows the amount of members for each role on the server. By default, this is sorted by role population (i.e. the amount of members per role). With the use of a boolean argument, it can be sorted by the role hierarchy (with the role highest in hierarchy on top). To facilitate servers with a lot of roles, the embed puts the roles in embed fields of at most 10 roles.
- **snowflake** / **timestamp** – This command converts a Discord snowflake ID to a timestamp that is friendly to read.
- **spotify** - This command allows someone to quickly show what they're listening to on Spotify (in a rich embed). Alternatively, you can add a user as an argument to see what they are listening to.
