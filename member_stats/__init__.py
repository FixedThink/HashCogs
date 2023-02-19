from .member_stats import MemberStats


__red_end_user_data_statement__ = (
        "This cog does not store user data. However, this cog may allow elevated server members "
        "to export some basic user data (username, join date, account age) to a file."
    )


async def setup(bot):
    await bot.add_cog(MemberStats(bot))
