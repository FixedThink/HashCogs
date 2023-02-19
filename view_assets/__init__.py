from .view_assets import ViewAssets


__red_end_user_data_statement__ = "No user data is stored by this cog."


async def setup(bot):
    await bot.add_cog(ViewAssets(bot))
