# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2022-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    calendar_ids = fields.One2many(
        comodel_name="hr.employee.calendar",
        inverse_name="employee_id",
        string="Calendar planning",
        copy=True,
    )

    def _get_planning_calendars(self, from_date, to_date):
        self.ensure_one()
        # sudo: calendar_ids is not available on the employee public profile
        return self.sudo().calendar_ids.filtered(
            lambda x: (not x.date_start or (from_date and x.date_start <= from_date))
            and (not x.date_end or (to_date and x.date_end >= to_date))
        )

    def _get_work_days_data_batch(
        self,
        from_datetime,
        to_datetime,
        compute_leaves=True,
        calendar=None,
        domain=None,
    ):
        # Use the planned calendar of the date instead of the employee one
        if len(self) == 1 and self.calendar_ids:
            from_dt_tz = fields.Datetime.context_timestamp(self, from_datetime)
            check_date = from_dt_tz.date()
            planned_line = self._get_planning_calendars(check_date, check_date)
            if planned_line:
                best_line = sorted(
                    planned_line,
                    key=lambda c: (c.date_end - c.date_start).days
                    if c.date_start and c.date_end
                    else 9999,
                )[0]
                calendar = best_line.calendar_id
        return super()._get_work_days_data_batch(
            from_datetime,
            to_datetime,
            compute_leaves=compute_leaves,
            calendar=calendar,
            domain=domain,
        )
