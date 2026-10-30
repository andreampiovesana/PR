# Copyright 2018 Daniel Campos <danielcampos@avanzosc.es> - Avanzosc S.L.
# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon


class CommonCase(BaseCommon):
    # BaseCommon runs the tests as a plain internal user, which cannot write
    # on products since 20.0
    _test_user_groups = ("base.group_user", "product.group_product_manager")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env.ref("product.product_product_4")
        cls.supplier = cls.env.ref("base.res_partner_2")
        cls.product_brand_obj = cls.env["product.brand"]
        cls.product_brand = cls.product_brand_obj.create(
            {
                "name": "Test Brand",
                "description": "Test brand description",
                "partner_id": cls.supplier.id,
            }
        )
