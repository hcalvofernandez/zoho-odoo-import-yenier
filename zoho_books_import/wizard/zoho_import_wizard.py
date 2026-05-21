from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ZohoImportWizard(models.TransientModel):
    _name = "zoho.import.wizard"
    _description = "Zoho Import Wizard"
    _transient_max_hours = 0.25
    
    connector_id = fields.Many2one("zoho.connector", string="Zoho Connector", required=True,
                                   domain=[("state", "=", "active")])
    
    import_products = fields.Boolean(string="Import Products", default=True)
    import_partners = fields.Boolean(string="Import Customers/Vendors", default=True)
    import_stock = fields.Boolean(string="Import Stock Levels", default=False)
    
    update_existing = fields.Boolean(string="Update Existing Records", default=True)
    partner_type = fields.Selection([
        ("customer", "Customers Only"),
        ("vendor", "Vendors Only"),
        ("both", "Both")
    ], string="Partner Type", default="both")
    
    @api.onchange("connector_id")
    def _onchange_connector(self):
        if self.connector_id:
            self.import_products = self.connector_id.import_products
            self.import_partners = self.connector_id.import_customers or self.connector_id.import_vendors
    
    def action_execute_import(self):
        self.ensure_one()
        notifications = []
        
        if not self.connector_id:
            raise UserError(_("Please select an active Zoho connector."))
        
        if self.import_products:
            if not self.connector_id.import_products:
                raise UserError(_("Product import is not enabled in connector settings."))
            
            product_wizard = self.env["zoho.product.import"].create({
                "connector_id": self.connector_id.id,
                "update_existing": self.update_existing,
                "import_stock": self.import_stock,
            })
            product_wizard.action_import_products()
            product_log = self.env["zoho.import.log"].search([
                ("connector_id", "=", self.connector_id.id),
                ("import_type", "=", "product"),
            ], order="create_date desc", limit=1)
            if product_log:
                notifications.append(_("Products: %(imported)s created, %(updated)s updated, %(failed)s failed") % {
                    "imported": product_log.imported_records,
                    "updated": product_log.updated_records,
                    "failed": product_log.failed_records,
                })
        
        if self.import_partners:
            if not self.connector_id.import_customers and not self.connector_id.import_vendors:
                raise UserError(_("Partner import is not enabled in connector settings."))
            
            partner_wizard = self.env["zoho.partner.import"].create({
                "connector_id": self.connector_id.id,
                "partner_type": self.partner_type,
                "update_existing": self.update_existing,
            })
            partner_wizard.action_import_partners()
            partner_logs = self.env["zoho.import.log"].search([
                ("connector_id", "=", self.connector_id.id),
                ("import_type", "in", ["customer", "vendor"]),
            ], order="create_date desc", limit=2)
            if partner_logs:
                notifications.append(_("Partners: %(imported)s created, %(updated)s updated, %(failed)s failed") % {
                    "imported": sum(partner_logs.mapped("imported_records")),
                    "updated": sum(partner_logs.mapped("updated_records")),
                    "failed": sum(partner_logs.mapped("failed_records")),
                })
        
        message = "\n".join(notifications) if notifications else _("Import process has been completed.")

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import Completed"),
                "message": message,
                "type": "success",
                "sticky": False,
            }
        }
