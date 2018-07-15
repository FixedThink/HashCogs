from .welcome_moderation import WelcomeModeration


def setup(bot):
    bot.add_cog(WelcomeModeration(bot))
