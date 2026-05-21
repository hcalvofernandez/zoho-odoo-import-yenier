from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    zoho_product_type = fields.Char(
        string="Zoho Product Type",
        help="Original product type from Zoho Books (goods, service, consumable)",
        readonly=True,
    )