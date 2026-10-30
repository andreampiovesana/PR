# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.tools import float_compare


class TestProductPricelist(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_brand = cls.env["product.brand"].create(
            {"name": "Test Brand", "description": "Test brand description"}
        )
        cls.product_categ = cls.env["product.category"].create({"name": "Test Category"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Branded product",
                "list_price": 100.0,
                "product_brand_id": cls.product_brand.id,
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {"name": "Unbranded product", "list_price": 100.0}
        )
        cls.pricelist = cls.env["product.pricelist"].create(
            {
                "name": "Test Pricelist",
                "item_ids": [
                    (
                        0,
                        0,
                        {
                            "product_brand_id": cls.product_brand.id,
                            "base": "list_price",
                            "compute_price": "discount",
                            "price_discount": 10,
                        },
                    ),
                ],
            }
        )

    def test_applied_on_is_computed_from_the_brand(self):
        """A rule carrying only a brand is scoped on that brand."""
        item = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "base": "list_price",
                "compute_price": "discount",
                "product_brand_id": self.product_brand.id,
            }
        )
        self.assertEqual(item.applied_on, "25_brand")
        self.assertEqual(item.name, self.product_brand.display_name)

    def test_applied_on_without_brand_stays_global(self):
        item = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "base": "list_price",
                "compute_price": "discount",
            }
        )
        self.assertEqual(item.applied_on, "3_global")

    def test_more_specific_targets_win_over_the_brand(self):
        """Category, template and variant keep precedence over the brand."""
        for values, expected in [
            ({"categ_id": self.product_categ.id}, "2_product_category"),
            ({"product_tmpl_id": self.product.product_tmpl_id.id}, "1_product"),
            (
                {
                    "product_tmpl_id": self.product.product_tmpl_id.id,
                    "product_id": self.product.id,
                },
                "0_product_variant",
            ),
        ]:
            item = self.env["product.pricelist.item"].create(
                {
                    "pricelist_id": self.pricelist.id,
                    "base": "list_price",
                    "compute_price": "discount",
                    "product_brand_id": self.product_brand.id,
                    **values,
                }
            )
            self.assertEqual(item.applied_on, expected)

    def test_unsetting_the_brand_falls_back_to_global(self):
        item = self.env["product.pricelist.item"].create(
            {
                "pricelist_id": self.pricelist.id,
                "base": "list_price",
                "compute_price": "discount",
                "product_brand_id": self.product_brand.id,
            }
        )
        item.product_brand_id = False
        self.assertEqual(item.applied_on, "3_global")

    def test_calculation_price_of_products_pricelist(self):
        """Test calculation of product price based on pricelist"""
        # Check sale price of branded product
        product_with_context = self.product.with_context(
            pricelist=self.pricelist.id, quantity=1
        )
        self.assertEqual(
            float_compare(
                product_with_context._get_contextual_price(),
                (
                    product_with_context.lst_price
                    - product_with_context.lst_price * (0.10)
                ),
                precision_digits=2,
            ),
            0,
        )

        # Check sale price of not branded product (should not change)
        product_2_with_context = self.product_2.with_context(
            pricelist=self.pricelist.id, quantity=1
        )
        self.assertEqual(
            float_compare(
                product_2_with_context._get_contextual_price(),
                product_2_with_context.lst_price,
                precision_digits=2,
            ),
            0,
        )
