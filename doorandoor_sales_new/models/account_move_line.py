from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    generated_sale_line_id = fields.Many2one(
        "sale.order.line",
        string="Generated Sale Order Line",
        copy=False,
        readonly=True,
    )

    fulfillment_line_id = fields.Many2one(
        "doorandoor.fulfillment.line",
        string="Fulfillment Line",
        copy=False,
        readonly=True,
    )
