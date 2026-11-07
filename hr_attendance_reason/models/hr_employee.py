# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.fields import Command


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _attendance_action_change(self, geo_information=None, check_in_image_data=None):
        res = super()._attendance_action_change(
            geo_information=geo_information, check_in_image_data=check_in_image_data
        )
        reason_id = self.env.context.get("attendance_reason_id")
        if reason_id:
            self._attendance_reason_link(reason_id)
        return res

    def _attendance_reason_link(self, reason_id):
        """Link the reason to the last attendance of the employee, the one the
        check in/out just created or closed."""
        self.ensure_one()
        attendance = self.env["hr.attendance"].search(
            [("employee_id", "=", self.id)], order="check_in desc", limit=1
        )
        if attendance:
            attendance.attendance_reason_ids = [Command.link(reason_id)]
