from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _auto_init(self):
        res = super()._auto_init()
        self.env.cr.execute(
            """
            ALTER TABLE product_template
            ADD COLUMN IF NOT EXISTS zoho_product_type varchar
            """
        )
        return res

    zoho_product_type = fields.Char(
        string="Zoho Product Type",
        help="Original product type from Zoho Books (goods, service, consumable)",
        readonly=True,
    )
