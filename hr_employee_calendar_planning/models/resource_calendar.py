# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2021-2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    employee_calendar_ids = fields.One2many("hr.employee.calendar", "calendar_id")

    @api.constrains("active")
    def _check_active(self):
        for item in self:
            if not item.active:
                domain = [
                    ("calendar_id", "=", item.id),
                    "|",
                    ("date_end", "=", False),
                    ("date_end", ">=", fields.Date.context_today(self)),
                ]
                total_items = self.env["hr.employee.calendar"].search_count(domain)
                if total_items:
                    raise ValidationError(
                        self.env._(
                            "%(item_name)s is used in %(total_items)s employee(s). "
                            "You should change them first.",
                            item_name=item.name,
                            total_items=total_items,
                        )
                    )

    @api.constrains("company_id")
    def _check_company_id(self):
        for item in self.filtered("company_id"):
            total_items = self.env["hr.employee.calendar"].search_count(
                [
                    ("calendar_id", "=", item.id),
                    ("calendar_id.company_id", "=", item.company_id.id),
                    ("employee_id.company_id", "!=", item.company_id.id),
                    ("employee_id.company_id", "!=", False),
                ]
            )
            if total_items:
                raise ValidationError(
                    self.env._(
                        "%(item_name)s is used in %(total_items)s employee(s) "
                        "related to another company.",
                        item_name=item.name,
                        total_items=total_items,
                    )
                )
