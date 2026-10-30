# Copyright 2017 Creu Blanca
# Copyright 2017-2024 ForgeFlow, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models


class WizardStockRequestKanbanAbstract(models.AbstractModel):
    _name = "wizard.stock.request.kanban.abstract"
    _description = "Stock Request Kanban Abstract Wizard"

    _barcode_scanned = fields.Char(
        "Barcode Scanned", help="Value of the last barcode scanned.", store=False
    )
    kanban_id = fields.Many2one("stock.request.kanban", readonly=True)
    status = fields.Text(readonly=True, default="Start scanning")
    status_state = fields.Integer(default=0, readonly=True)

    @api.onchange("_barcode_scanned")
    def _on_barcode_scanned(self):
        barcode = self._barcode_scanned
        if barcode:
            self._barcode_scanned = ""
            return self.on_barcode_scanned(barcode)

    def on_barcode_scanned(self, barcode):
        self.kanban_id = self.env["stock.request.kanban"].search_barcode(barcode)
        if not self.kanban_id:
            self.status = (
                self.env._(
                    "Barcode %s does not correspond to any "
                    "Kanban. Try with another barcode or "
                    "press Close to finish scanning."
                )
                % barcode
            )
            self.status_state = 1
            return
        if self.validate_kanban(barcode):
            self.status_state = 0
            self.barcode_ending()
            return

    def barcode_ending(self):
        pass

    def validate_kanban(self, barcode):
        """
        It must return True if the kanban is valid, False otherwise
        :param barcode:
        :return:
        """
        return True
