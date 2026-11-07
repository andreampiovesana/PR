# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime

from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestHrEmployeeCalendarPlanning(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calendar_full = cls.env["resource.calendar"].create(
            {"name": "Test full time"}
        )
        cls.calendar_part = cls.env["resource.calendar"].create(
            {
                "name": "Test part time",
                "attendance_ids": [
                    (
                        0,
                        0,
                        {
                            "dayofweek": "0",
                            "hour_from": 8,
                            "hour_to": 12,
                        },
                    )
                ],
            }
        )
        cls.employee = cls.env["hr.employee"].create(
            {
                "name": "Planning Employee",
                "resource_calendar_id": cls.calendar_full.id,
                "tz": "UTC",
            }
        )

    def _plan(self, calendar, date_start=False, date_end=False):
        return self.env["hr.employee.calendar"].create(
            {
                "employee_id": self.employee.id,
                "calendar_id": calendar.id,
                "date_start": date_start,
                "date_end": date_end,
            }
        )

    def test_get_planning_calendars(self):
        old = self._plan(self.calendar_full, False, date(2026, 6, 30))
        new = self._plan(self.calendar_part, date(2026, 7, 1), False)
        day = date(2026, 6, 15)
        self.assertEqual(self.employee._get_planning_calendars(day, day), old)
        day = date(2026, 8, 3)
        self.assertEqual(self.employee._get_planning_calendars(day, day), new)

    def test_native_calendar_untouched(self):
        self._plan(self.calendar_part, date(2026, 1, 1), False)
        self.assertEqual(self.employee.resource_calendar_id, self.calendar_full)

    def test_overlap(self):
        self._plan(self.calendar_full, date(2026, 1, 1), date(2026, 6, 30))
        with self.assertRaises(UserError):
            self._plan(self.calendar_part, date(2026, 6, 1), False)

    @mute_logger("odoo.sql_db")
    def test_date_consistency(self):
        with self.assertRaises(Exception), self.env.cr.savepoint():
            self._plan(self.calendar_full, date(2026, 6, 30), date(2026, 1, 1))

    def test_work_days_use_planned_calendar(self):
        self._plan(self.calendar_part, date(2026, 8, 1), False)
        # Monday 2026-08-03: the part time calendar has 4 hours
        data = self.employee._get_work_days_data_batch(
            datetime(2026, 8, 3, 0, 0), datetime(2026, 8, 3, 23, 59)
        )[self.employee.id]
        self.assertAlmostEqual(data["hours"], 4)

    def test_archive_used_calendar(self):
        self._plan(self.calendar_part, date(2026, 1, 1), False)
        with self.assertRaises(ValidationError):
            self.calendar_part.active = False

    def test_employee_copy_data(self):
        self._plan(self.calendar_part, date(2026, 1, 1), False)
        vals = self.employee.copy_data()[0]
        self.assertEqual(vals["calendar_ids"][0][2]["calendar_id"], self.calendar_part.id)
