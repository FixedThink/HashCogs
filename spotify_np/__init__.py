from .spotify_np import SpotifyNP

__red_end_user_data_statement__ = "No user data is stored by this cog."


async def setup(bot):
    await bot.add_cog(SpotifyNP(bot))
