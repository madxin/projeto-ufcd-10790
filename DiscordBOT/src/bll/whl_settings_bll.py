from src.dal.whl_settings_dal import WhlSettingsDAL


class WhlSettingsBLL:

    @staticmethod
    def set_whl_category(
        guild_id,
        whl_type,
        category_id
    ):
        WhlSettingsDAL.set_whl_category(
            guild_id,
            whl_type,
            category_id
        )

    @staticmethod
    def set_whl_role(
        guild_id,
        whl_type,
        staff_role_id
    ):
        WhlSettingsDAL.set_whl_role(
            guild_id,
            whl_type,
            staff_role_id
        )

    @staticmethod
    def get_whl_config(
        guild_id,
        whl_type
    ):
        return WhlSettingsDAL.get_whl_config(
            guild_id,
            whl_type
        )

    @staticmethod
    def get_all_whl_configs(
        guild_id
    ):
        return WhlSettingsDAL.get_all_whl_configs(
            guild_id
        )