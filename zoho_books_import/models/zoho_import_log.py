from odoo import models, fields, api, _

class ZohoImportLog(models.Model):
    _name = "zoho.import.log"
    _description = "Zoho Import Log"
    _order = "create_date desc"
    _inherit = ["mail.thread"]
    
    name = fields.Char(string="Reference", required=True, copy=False, readonly=True,
                       default=lambda self: self.env["ir.sequence"].next_by_code("zoho.import.log"))
    connector_id = fields.Many2one("zoho.connector", string="Connector", required=True, ondelete="cascade")
    
    import_type = fields.Selection([
        ("product", "Product"),
        ("stock", "Product Stock"),
        ("customer", "Customer"),
        ("vendor", "Vendor"),
        ("sale_order", "Sale Order"),
        ("invoice", "Customer Invoice"),
        ("bill", "Vendor Bill"),
        ("customer_payment", "Customer Payment"),
        ("vendor_payment", "Vendor Payment"),
        ("customer_credit", "Customer Credit"),
        ("vendor_credit", "Vendor Credit"),
    ], string="Import Type", required=True)
    
    state = fields.Selection([
        ("draft", "Draft"),
        ("in_progress", "In Progress"),
        ("done", "Done"),
        ("error", "Error"),
        ("partial", "Partial")
    ], string="Status", default="draft", tracking=True)
    
    total_records = fields.Integer(string="Total Records")
    imported_records = fields.Integer(string="Imported")
    updated_records = fields.Integer(string="Updated")
    failed_records = fields.Integer(string="Failed")
    skipped_records = fields.Integer(string="Skipped")
    
    error_details = fields.Text(string="Error Details")
    warning_details = fields.Text(string="Warning Details")
    
    product_ids = fields.Many2many("product.template", string="Imported Products")
    partner_ids = fields.Many2many("res.partner", string="Imported Partners")
    sale_ids = fields.Many2many("sale.order", string="Imported Sale Orders")
    invoice_ids = fields.Many2many("account.move", string="Imported Invoices")
    
    start_time = fields.Datetime(string="Start Time")
    end_time = fields.Datetime(string="End Time")
    duration_seconds = fields.Float(string="Duration (seconds)", compute="_compute_duration", store=True)
    
    zoho_page = fields.Integer(string="API Page")
    zoho_per_page = fields.Integer(string="Per Page", default=200)
    
    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for log in self:
            if log.start_time and log.end_time:
                delta = log.end_time - log.start_time
                log.duration_seconds = delta.total_seconds()
            else:
                log.duration_seconds = 0.0
    
    def action_view_products(self):
        self.ensure_one()
        return {
            "name": _("Imported Products"),
            "type": "ir.actions.act_window",
            "res_model": "product.template",
            "view_mode": "list,form",
            "domain": [("id", "in", self.product_ids.ids)],
        }
    
    def action_view_partners(self):
        self.ensure_one()
        return {
            "name": _("Imported Partners"),
            "type": "ir.actions.act_window",
            "res_model": "res.partner",
            "view_mode": "list,form",
            "domain": [("id", "in", self.partner_ids.ids)],
        }