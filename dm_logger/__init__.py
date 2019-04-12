from .dm_logger import DMLogger


def setup(bot):
    bot.add_cog(DMLogger(bot))
