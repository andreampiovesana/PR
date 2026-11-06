from odoo import models


class PortalEntry(models.Model):
    _inherit = "portal.entry"

    def _filter_visible_portal_cards(self):
        visible_entries = super()._filter_visible_portal_cards()
        ticket_entry = self.env.ref(
            "helpdesk_mgmt.portal_tickets", raise_if_not_found=False
        )
        if ticket_entry and ticket_entry in self:
            visible_entries |= ticket_entry
        return visible_entries
