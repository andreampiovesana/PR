# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.fields import Domain


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_rules_domain(
        self, products, *, date=None, quantity=None, uom=None, **kwargs
    ):
        domain = super()._get_applicable_rules_domain(
            products, date=date, quantity=quantity, uom=uom, **kwargs
        )
        if not products:
            return domain
        if products._name == "product.template":
            brands = products.product_brand_id
        else:
            brands = products.product_tmpl_id.product_brand_id
        return domain & (
            Domain("product_brand_id", "=", False)
            | Domain("product_brand_id", "in", brands.ids)
        )


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    product_brand_id = fields.Many2one(
        comodel_name="product.brand",
        string="Brand",
        ondelete="cascade",
        help="Specify a brand if this rule only applies to products"
        "belonging to this brand. Keep empty otherwise.",
    )
    applied_on = fields.Selection(
        selection_add=[("25_brand", "Brand")], ondelete={"25_brand": "set 3_global"}
    )

    @api.depends("categ_id", "product_id", "product_tmpl_id", "product_brand_id")
    def _compute_applied_on(self):
        super()._compute_applied_on()
        for item in self:
            if item.applied_on == "3_global" and item.product_brand_id:
                item.applied_on = "25_brand"

    @api.depends("applied_on", "categ_id", "product_tmpl_id", "product_id", "product_brand_id")
    def _compute_name(self):
        super()._compute_name()
        for item in self:
            if item.applied_on == "25_brand" and item.product_brand_id:
                item.name = item.product_brand_id.display_name

    @api.constrains("product_id", "product_tmpl_id", "categ_id", "product_brand_id")
    def _check_product_consistency(self):
        for item in self:
            if item.applied_on == "25_brand" and not item.product_brand_id:
                raise ValidationError(
                    item.env._(
                        "Please specify the brand for which this rule should be applied"
                    )
                )
        return super()._check_product_consistency()
