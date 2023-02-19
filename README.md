# HashCogs

Hey there, welcome to my first repository!

All the cogs listed on here should work properly, so if there are any issues do not hesitate to inform me!

**None of the cogs in this repository require additional packages!**

Readme last updated: **2023-02-19**

### Compatibility note
All cogs in this repository have RedBot 3.5 (including dev) as their minimum supported version!
For support of earlier versions of RedBot 3, please check out 
[this revision](https://github.com/FixedThink/HashCogs/tree/1d6ff7f1d2c066713ec137fc5edfe1088cb5de1f)
of the repository.

Furthermore, the `FixedVarious` module has been split up in several modules. 
The MemberStats module inherited its config identifier, as the commands in there were the only ones using Config anyway.

# About the cogs

## AssignRoles
The cog essentially simulates the Manage Roles permission, but for specific to pairs of roles. 
For example, role A can be allowed to give role B to anyone else, without allowing the same role A to give role C, D, etc.

#### Example usage
This cog makes it possible to facilitate "Helpers" on the server by allowing them to assign some harmless roles, 
such as platform/region roles, without allowing them to assign some more powerful roles like a bot role.

#### Legacy note
This is the RedBot V3 version of my `assign_roles` cog, which was published on 
[ZeLarpMaster's V2 repository](https://github.com/ZeLarpMaster/ZeCogs) as I did not have a GitHub account back then.


## ChannelSlowmode

Does the same as `[p]slowmode` from the built-in Mod module, except that it can set a slowmode in another channel/thread. 
If you wonder why this is necessary, consider the elaboration right below.

The issue at hand: suppose you want to enable (or increase) a slowmode in a channel because it is too active. 
How would you change it? By executing a command inside that channel? 
The command + response adds 2 more message on top of an already active channel, 
and users responding to the modified slowmode may even cause _more_ traffic! Not nice!

Because of that, this one-command cog allows members with the manage channel permission to 
modify the slowmode of a channel/thread anywhere on a server. This makes it easier to run those commands inside staff channels 
(where moderation discussion usually takes place), whilst *also* not overloading public channels with bot commands.
A win-win.

## DMLogger
Logs every DM sent to the bot (except by the bot owner), and exports the log to a simple csv file.
The log can be retrieved through a command, or can be sent periodically to the bot owner 
with a customisable message interval.

## MemberStats
Currently, this cog can list the amount of members per role , either sorted by count or by hierarchy. 
Useful if your server has console platforms for example, or if you're just interested.
Additional, the cog can export a list of your members, including how long they have been on the server. Handy if you want to see who are the long-time members of your servers, for detecting growth patterns, or for other organisational purposes.

Technical details: 
- `[p]rolestats` shows the amount of members for each role on the server. By default, this is sorted by role population (i.e. the amount of members per role). 
With the use of a boolean argument, it can be sorted by the role hierarchy (with the role highest in hierarchy on top). 
For servers with a lot of roles, the embed puts the roles in embed fields of at most 10 roles. 
- `[p]member_csv` allows users with the `Manage Roles` permission to download the member list of a server in csv format. 
As the delimiter for csv files varies from country to country, this command allows the user to modify the delimiter with an argument.


## SnowflakeTools
Every ID within Discord is a so-called Snowflake ID. 
This is an ID which has some information embedded inside it, like a timestamp. 
More info about it can be found in Discord's 
[API reference](https://discord.com/developers/docs/reference#snowflakes).

The goal of this cog is to make use of the information that snowflakes can give us. The following features are currently implemented:
- **snowflake** – Convert a snowflake into a human-readable timestamp.
- **goto** – Use a snowflake ID to create a link to jump to a specific message in a channel. 
If a message is deleted, this allows you to nevertheless jump to its context. 
Please be aware, however, that Discord can possibly be bugged after clicking such a link 
if the snowflake ID does not belong to an existing message in that channel.

## SpotifyNP
This cog has one command, `[p]spotify`. NP in this case stands for "now playing".  

This command allows someone to quickly show what they're listening to on Spotify (in a rich embed). 
Alternatively, you can add a user as an argument to see what they are listening to.

## ViewAssets

See enhanced version of assets, right inside Discord. This cog has the following commands:

- **avatar** – Allows any user to see their own avatar (or someone else's) in a rich embed. In the embed, there is also a hyperlink that allows any user to download their avatar (in PNG or, if animated, GIF format).
- **serveravatar** – Does the same as avatar, but for server-specific avatars. Consequently, this command is server-only.
- **assets** – Displays the server's assets (logo, and banner and splashes if available) in a menu.

## WelcomeModeration
Allows you to set custom welcome messages, and to set a verification role on a guild-by-guild basis. 
Both the welcome functionality and verification functionality are optional and customisable, 
meaning that you can use the welcome messages whilst not using the verification roles, and vice versa.

#### Welcome message
The channel in which the welcome message will be sent can be easily configured by performing a command in the desired channel. 
Additionally, the welcome message can be modified directly through the Discord client, 
rather than having to save a text file somewhere or something similar. 
This welcome message allows you to put a user mention anywhere in the message by putting `{user}` where you want the message to be. 
Additionally, the bot ignores other bots being added, thus making someone able to add bots without generating a welcome message.

#### Verification role
If enabled, the verification role will be given to a member if it obtains any role in whatever way, 
except if the role obtained is configured to be blacklisted. By doing so, 
a guild can have one role to give some basic permissions to (such as change nickname permissions), 
whilst not giving these permissions to `@everyone` for moderation reasons. 
If used properly, this role can be configured such that it's only given to those who satisfy the Discord verification level.
Optionally, the bot can send logs of verification role additions in a certain channel. 
Additionally, a delay for obtaining the verification role may be configured.

#### Example usages
- A guild wants to give every member some basic permissions, but only if they have given themselves a role from a list of assignable roles. 
Rather than configuring appropriate permissions for each of the assignable roles, 
and having to adapt all of the roles in every channel in case of a rule change, 
the verification role could add as an "umbrella role" which would be only one that needs to be changed.
- A guild may have a human barrier to roles on a server, 
to prevent giving access to certain places for those who aren't authorised to be on the server. 
With such a role, authorisation can be automatically granted if a moderator gives a user any role available 
(not counting those that are added to a blacklist).

# Licensing

I am aware that this repository currently does not have a license. 
While I am thinking of which license suits this repository best, 
you have my consent to use the modules enlisted in this repository on your own RedBot instance.
I hope that for now this suffices to use the commands in here :D