from .status_poll import StatusPoll


def setup(bot):
    bot.add_cog(StatusPoll(bot))
