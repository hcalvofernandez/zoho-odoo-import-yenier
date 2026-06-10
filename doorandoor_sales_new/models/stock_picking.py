from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        pending_pickings = self.filtered(lambda picking: picking.state not in ("done", "cancel"))
        result = super().button_validate()
        done_pickings = pending_pickings.filtered(lambda picking: picking.state == "done")
        done_pickings._ddsn_sync_invoice_delivery_status()
        return result

    def _ddsn_sync_invoice_delivery_status(self):
        for picking in self:
            fulfillment_lines = self.env["doorandoor.fulfillment.line"].search([("picking_id", "=", picking.id)])
            for fulfillment_line in fulfillment_lines:
                delivered_qty = max(fulfillment_line.qty_sent_stock, fulfillment_line.qty_delivered)
                values = {
                    "qty_delivered": delivered_qty,
                    "qty_pending_delivery": max(fulfillment_line.qty_invoiced - delivered_qty, 0.0),
                }
                values["state"] = "delivered" if values["qty_pending_delivery"] <= 0 else "in_process"
                fulfillment_line.write(values)
                fulfillment_line.move_id._ddsn_set_release_state()

