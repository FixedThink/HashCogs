from .assign_roles import AssignRoles


__red_end_user_data_statement__ = "No user data is stored by this cog."


async def setup(bot):
    await bot.add_cog(AssignRoles(bot))
