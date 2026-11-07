# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2022-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.fields import Domain


class HrEmployeeCalendar(models.Model):
    _name = "hr.employee.calendar"
    _description = "Employee Calendar"
    _order = "date_end desc"

    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")
    employee_id = fields.Many2one(
        comodel_name="hr.employee", string="Employee", required=True, ondelete="cascade"
    )
    company_id = fields.Many2one(related="employee_id.company_id")
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Time",
        required=True,
        check_company=True,
        ondelete="restrict",
    )

    _date_consistency = models.Constraint(
        "CHECK(date_start <= date_end)",
        "Date end should be higher than date start",
    )

    def _related_action_format_error_message(self):
        return self.env._(
            "The employee %s has already a calendar assigned that overalps this period",
            self.employee_id.name,
        )

    @api.constrains("date_start", "date_end", "employee_id")
    def _check_overlap(self):
        for record in self:
            domain = Domain(
                [
                    ("employee_id", "=", record.employee_id.id),
                    ("id", "!=", record.id),
                ]
            )
            if record.date_end:
                domain &= Domain(
                    [
                        "|",
                        ("date_start", "<=", record.date_end),
                        ("date_start", "=", False),
                    ]
                )
            if record.date_start:
                domain &= Domain(
                    [
                        "|",
                        ("date_end", ">=", record.date_start),
                        ("date_end", "=", False),
                    ]
                )
            if self.search_count(list(domain)):
                raise UserError(record._related_action_format_error_message())
