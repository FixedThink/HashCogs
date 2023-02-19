from .dm_logger import DMLogger

__red_end_user_data_statement__ = (
    "The owner of this bot has decided to enable DM logging for this bot. "
    "Although this may be for different reasons, the most likely reason is to counter spam.\n"
    "By default, only the bot owner can see and access any logged data."
    "If you have more questions about what is logged, please contact the bot owner for "
    "clarification.\nNote that due to the security reasons behind logging, "
    "users cannot delete or review the data that is logged."
    "Therefore, deletion/inspection requests much go through the bot owner."
)


async def setup(bot):
    await bot.add_cog(DMLogger(bot))
