from .welcome_moderation import WelcomeModeration

__red_end_user_data_statement__ = (
    "No user data is stored by this cog. The only use of user data is "
    "to detect server joins and role additions, but this data is not stored upon usage."
)


async def setup(bot):
    await bot.add_cog(WelcomeModeration(bot))
