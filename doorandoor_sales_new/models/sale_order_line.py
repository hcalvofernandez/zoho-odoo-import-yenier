from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    ddsn_available_qty = fields.Float(
        string="Available Stock",
        compute="_compute_ddsn_stock_visibility",
        digits="Product Unit of Measure",
        readonly=True,
    )

    ddsn_stock_uom_name = fields.Char(
        string="Stock UoM",
        compute="_compute_ddsn_stock_visibility",
        readonly=True,
    )

    ddsn_stock_display = fields.Char(
        string="Stock Available",
        compute="_compute_ddsn_stock_visibility",
        readonly=True,
    )

    ddsn_warehouse_stock_html = fields.Html(
        string="Warehouses",
        compute="_compute_ddsn_stock_visibility",
        sanitize=False,
        readonly=True,
    )

    @api.depends("product_id", "product_uom_qty", "order_id.warehouse_id", "order_id.company_id")
    def _compute_ddsn_stock_visibility(self):
        for line in self:
            line.ddsn_available_qty = 0.0
            line.ddsn_stock_uom_name = False
            line.ddsn_stock_display = False
            line.ddsn_warehouse_stock_html = False

            product = line.product_id
            if not product or product.type not in ("product", "consu"):
                continue

            warehouse = line.order_id.warehouse_id
            product_ctx = product.with_company(line.order_id.company_id)
            if warehouse and warehouse.lot_stock_id:
                product_ctx = product_ctx.with_context(location=warehouse.lot_stock_id.id)

            available_qty = product_ctx.qty_available
            uom_name = product.uom_id.display_name or product.uom_id.name

            line.ddsn_available_qty = available_qty
            line.ddsn_stock_uom_name = uom_name
            line.ddsn_stock_display = f"{available_qty:.2f} {uom_name}"
            line.ddsn_warehouse_stock_html = line._ddsn_get_warehouse_stock_html()

    def _ddsn_get_warehouse_stock_html(self):
        self.ensure_one()
        product = self.product_id
        if not product or product.type not in ("product", "consu"):
            return False

        warehouses = self.env["stock.warehouse"].search(
            [("company_id", "=", self.order_id.company_id.id)],
            order="sequence, id",
        )
        if not warehouses:
            return False

        has_bom = bool(
            self.env["mrp.bom"].search(
                [
                    "|",
                    ("product_id", "=", product.id),
                    "&",
                    ("product_id", "=", False),
                    ("product_tmpl_id", "=", product.product_tmpl_id.id),
                ],
                limit=1,
            )
        )

        badges = []
        for warehouse in warehouses:
            location = warehouse.lot_stock_id
            if not location:
                continue

            qty = product.with_company(self.order_id.company_id).with_context(location=location.id).qty_available
            if qty > 0:
                background = "#d1fae5"
                color = "#065f46"
            elif has_bom:
                background = "#fed7aa"
                color = "#9a3412"
            else:
                background = "#fecaca"
                color = "#991b1b"

            warehouse_label = warehouse.code or warehouse.name

            badges.append(
                (
                    f"<span style='display:inline-block;margin:1px 4px 1px 0;padding:2px 8px;"
                    f"border-radius:999px;background:{background};color:{color};font-weight:600;"
                    f"white-space:nowrap;'>{warehouse_label}: {qty:.2f}</span>"
                )
            )

        return "".join(badges) or False
