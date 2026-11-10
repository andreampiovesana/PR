# Copyright 2023 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestProductCustomerinfoPicking(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.src_location = cls.env.ref("stock.stock_location_stock")
        cls.dest_location = cls.env.ref("stock.stock_location_customers")
        cls.computer_SC234 = cls.env["product.product"].create(
            {"name": "Computer SC234", "default_code": "PCSC234", "is_storable": True}
        )
        cls.agrolait = cls.env["res.partner"].create({"name": "Agrolait"})
        cls.gemini = cls.env["res.partner"].create({"name": "Gemini Furniture"})
        cls.computer_SC234.write(
            {
                "customer_ids": [
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.agrolait.id,
                            "product_code": "test_agrolait",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "partner_id": cls.gemini.id,
                            "product_code": "test_gemini",
                        },
                    ),
                ],
            }
        )

    @classmethod
    def _create_delivery_picking(cls, partner, **kwargs):
        delivery_picking = cls.env["stock.picking"].new(
            {
                "partner_id": partner.id,
                "picking_type_id": cls.env.ref("stock.picking_type_out").id,
            }
        )
        delivery_picking._onchange_picking_type()
        vals = {
            "partner_id": delivery_picking.partner_id.id,
            "picking_type_id": delivery_picking.picking_type_id.id,
            "location_id": cls.src_location.id,
            "location_dest_id": cls.dest_location.id,
            "move_ids": [
                (
                    0,
                    0,
                    {
                        "product_id": cls.computer_SC234.id,
                        "uom_id": cls.computer_SC234.uom_id.id,
                        "product_uom_qty": 1.0,
                        "location_id": cls.src_location.id,
                        "location_dest_id": cls.dest_location.id,
                    },
                )
            ],
        }
        vals.update(kwargs)
        return cls.env["stock.picking"].create(vals)

    def test_product_customerinfo_picking(self):
        delivery_picking = self._create_delivery_picking(self.agrolait)
        move = delivery_picking.move_ids[:1]
        self.assertEqual(move.product_customer_code, "test_agrolait")

    def test_product_customerinfo_two_costumers(self):
        delivery_picking = self._create_delivery_picking(self.gemini)
        move = delivery_picking.move_ids[:1]
        self.assertEqual(move.product_customer_code, "test_gemini")

    def test_product_customerinfo_variant_precedence(self):
        self.env["product.customerinfo"].create(
            {
                "partner_id": self.agrolait.id,
                "product_tmpl_id": self.computer_SC234.product_tmpl_id.id,
                "product_id": self.computer_SC234.id,
                "product_code": "test_agrolait_variant",
                "product_name": "Variant name for agrolait",
            }
        )
        delivery_picking = self._create_delivery_picking(self.agrolait)
        move = delivery_picking.move_ids[:1]
        self.assertEqual(move.product_customer_code, "test_agrolait_variant")
        self.assertEqual(move.product_customer_name, "Variant name for agrolait")

    def test_product_customerinfo_no_partner(self):
        delivery_picking = self._create_delivery_picking(
            self.agrolait, partner_id=False
        )
        move = delivery_picking.move_ids[:1]
        self.assertFalse(move.product_customer_code)

    def test_report_product_display_name(self):
        delivery_picking = self._create_delivery_picking(self.agrolait)
        move = delivery_picking.move_ids[:1]
        self.assertEqual(
            move._get_report_product_display_name(),
            f"[test_agrolait] {self.computer_SC234.name}",
        )
        no_partner_picking = self._create_delivery_picking(
            self.agrolait, partner_id=False
        )
        no_partner_move = no_partner_picking.move_ids[:1]
        self.assertEqual(
            no_partner_move._get_report_product_display_name(),
            self.computer_SC234.display_name,
        )

    def test_delivery_slip_customer_code(self):
        delivery_picking = self._create_delivery_picking(self.agrolait)
        delivery_picking.action_confirm()
        report = self.env["ir.actions.report"]._render_qweb_html(
            "stock.report_deliveryslip", delivery_picking.ids
        )[0]
        self.assertIn("[test_agrolait]", report.decode())
        self.assertNotIn(self.computer_SC234.default_code, report.decode())

    def test_delivery_slip_customer_code_done(self):
        delivery_picking = self._create_delivery_picking(self.agrolait)
        delivery_picking.action_confirm()
        self.env["stock.quant"]._update_available_quantity(
            self.computer_SC234, self.src_location, 1.0
        )
        delivery_picking.action_assign()
        for move in delivery_picking.move_ids:
            move.quantity = move.product_uom_qty
            move.picked = True
        delivery_picking._action_done()
        self.assertEqual(delivery_picking.state, "done")
        report = self.env["ir.actions.report"]._render_qweb_html(
            "stock.report_deliveryslip", delivery_picking.ids
        )[0]
        self.assertIn("[test_agrolait]", report.decode())
        self.assertNotIn(self.computer_SC234.default_code, report.decode())
