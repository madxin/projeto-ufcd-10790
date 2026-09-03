from src.dal.settings_dal import SettingsDAL

class SettingsBLL:

    @staticmethod
    def set_autorole(guild_id, role_id):
        SettingsDAL.set_autorole(guild_id, role_id)

    @staticmethod
    def get_autorole(guild_id):
        return SettingsDAL.get_autorole(guild_id)

    @staticmethod
    def clear_autorole(guild_id):
        SettingsDAL.clear_autorole(guild_id)

    @staticmethod
    def set_logs_channel(guild_id, channel_id):
        SettingsDAL.set_logs_channel(guild_id, channel_id)

    @staticmethod
    def get_logs_channel(guild_id):
        return SettingsDAL.get_logs_channel(guild_id)

    @staticmethod
    def set_whl_block_role(guild_id, role_id):
        SettingsDAL.set_whl_block_role(guild_id, role_id)

    @staticmethod
    def get_whl_block_role(guild_id):
        return SettingsDAL.get_whl_block_role(guild_id)

    @staticmethod
    def clear_whl_block_role(guild_id):
        SettingsDAL.clear_whl_block_role(guild_id)
    
