from src.dal.ticket_settings_dal import TicketSettingsDAL


class TicketSettingsBLL:

    @staticmethod
    def set_ticket_category(
        guild_id,
        ticket_type,
        category_id
    ):
        TicketSettingsDAL.set_ticket_category(
            guild_id,
            ticket_type,
            category_id
        )

    @staticmethod
    def set_ticket_role(
        guild_id,
        ticket_type,
        staff_role_id
    ):
        TicketSettingsDAL.set_ticket_role(
            guild_id,
            ticket_type,
            staff_role_id
        )

    @staticmethod
    def get_ticket_config(
        guild_id,
        ticket_type
    ):
        return TicketSettingsDAL.get_ticket_config(
            guild_id,
            ticket_type
        )

    @staticmethod
    def get_all_ticket_configs(
        guild_id
    ):
        return TicketSettingsDAL.get_all_ticket_configs(
            guild_id
        )