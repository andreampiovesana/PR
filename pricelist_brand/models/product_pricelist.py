# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        res = super()._get_applicable_rules_domain(products, date)
        if products._name == "product.template":
            brand_domain = ("product_brand_id", "in", products.product_brand_id.ids)
        else:
            brand_domain = (
                "product_brand_id",
                "in",
                products.product_tmpl_id.product_brand_id.ids,
            )
        res = expression.AND(
            [
                res,
                [
                    ("|"),
                    ("product_brand_id", "=", False),
                    (brand_domain),
                ],
            ]
        )
        return res


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
        selection_add=[("25_brand", "Brand")], ondelete={"25_brand": "set default"}
    )
    display_applied_on = fields.Selection(
        selection_add=[("25_brand", "Brand")], ondelete={"25_brand": "set default"}
    )

    @api.constrains("product_id", "product_tmpl_id", "categ_id", "product_brand_id")
    def _check_product_consistency(self):
        for item in self:
            if item.applied_on == "25_brand" and not item.product_brand_id:
                raise ValidationError(
                    _("Please specify the brand for which this rule should be applied")
                )
        return super()._check_product_consistency()

    @api.onchange("product_id", "product_tmpl_id", "categ_id", "product_brand_id")
    def _onchange_rule_content(self):
        return super()._onchange_rule_content()

    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'product_brand_id')
    def _compute_name(self):
        for item in self:
            if item.categ_id and item.applied_on == '2_product_category':
                item.name = _("Category: %s", item.categ_id.display_name)
            elif item.product_tmpl_id and item.applied_on == '1_product':
                item.name = _("Product: %s",item.product_tmpl_id.display_name)
            elif item.product_id and item.applied_on == '0_product_variant':
                item.name = _("Variant: %s", item.product_id.display_name)
            elif item.product_brand_id and item.applied_on == '25_brand':
                item.name = _("Brand: %s", item.product_brand_id.display_name)
            elif item.display_applied_on == '2_product_category':
                item.name = _("All Categories")
            else:
                item.name = _("All Products")

    @api.onchange('display_applied_on')
    def _onchange_display_applied_on(self):
        for item in self:
            if not (item.product_tmpl_id or item.categ_id or item.product_brand_id):
                item.update(dict(
                    applied_on='3_global',
                ))
            elif item.display_applied_on == '1_product':
                item.update(dict(
                    applied_on='1_product',
                    categ_id=None,
                    product_brand_id=None,
                ))
            elif item.display_applied_on == '2_product_category':
                item.update(dict(
                    product_id=None,
                    product_tmpl_id=None,
                    applied_on='2_product_category',
                    product_uom=None,
                ))
            elif item.display_applied_on == '25_brand':
                item.update(dict(
                    product_id=None,
                    product_tmpl_id=None,
                    categ_id=None,
                    applied_on='25_brand',
                    product_uom=None,
                ))

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get('product_id') and not values.get('product_tmpl_id'):
                # Deduce product template from product variant if not specified.
                # Ensures that the pricelist rule is properly configured and displayed in the UX
                # even in case of partial/incomplete data (mostly for imports).
                values['product_tmpl_id'] = self.env['product.product'].browse(
                    values.get('product_id')
                ).product_tmpl_id.id
            if not values.get('applied_on'):
                values['applied_on'] = (
                    '0_product_variant' if values.get('product_id') else
                    '1_product' if values.get('product_tmpl_id') else
                    '2_product_category' if values.get('categ_id') else
                    '25_brand' if values.get('product_brand_id') else
                    '3_global'
                )
            # Ensure item consistency for later searches.
            applied_on = values['applied_on']
            if applied_on == '3_global':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
            elif applied_on == '25_brand':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
            elif applied_on == '2_product_category':
                values.update(dict(product_id=None, product_tmpl_id=None))
            elif applied_on == '1_product':
                values.update(dict(product_id=None, categ_id=None))
            elif applied_on == '0_product_variant':
                values.update(dict(categ_id=None))
        return super().create(vals_list)

    def write(self, values):
        if values.get('applied_on', False):
            # Ensure item consistency for later searches.
            applied_on = values['applied_on']
            if applied_on == '3_global':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
            elif applied_on == '25_brand':
                values.update(dict(product_id=None, product_tmpl_id=None, categ_id=None))
            elif applied_on == '2_product_category':
                values.update(dict(product_id=None, product_tmpl_id=None))
            elif applied_on == '1_product':
                values.update(dict(product_id=None, categ_id=None))
            elif applied_on == '0_product_variant':
                values.update(dict(categ_id=None))
        return super().write(values)

