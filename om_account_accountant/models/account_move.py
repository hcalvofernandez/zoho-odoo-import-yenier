from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.model
    def _get_invoice_in_payment_state(self):
        return 'in_payment'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            move_type = vals.get('move_type')
            if move_type in ('out_invoice', 'out_refund') and not vals.get('invoice_date_due'):
                vals['invoice_date_due'] = vals.get('invoice_date') or fields.Date.context_today(self)
        return super().create(vals_list)

    def write(self, vals):
        if 'invoice_date_due' not in vals:
            pending_moves = self.filtered(
                lambda m: m.move_type in ('out_invoice', 'out_refund') and not m.invoice_date_due
            )
            for move in pending_moves:
                move.invoice_date_due = move.invoice_date or fields.Date.context_today(move)
        return super().write(vals)
