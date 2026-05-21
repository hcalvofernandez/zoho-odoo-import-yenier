from odoo import models, fields

class ProductTemplate(models.Model):
    _inherit = "product.template"
    
    zoho_item_id = fields.Char(
        string="Zoho Item ID",
        index=True,
        copy=False,
        help="Unique identifier from Zoho Books"
    )
    zoho_synced = fields.Boolean(
        string="Synced from Zoho",
        default=False,
        readonly=True,
        help="Indicates this product was imported from Zoho Books"
    )
    zoho_sync_date = fields.Datetime(
        string="Last Zoho Sync",
        readonly=True,
        help="Date of last synchronization with Zoho Books"
    )

class ResPartner(models.Model):
    _inherit = "res.partner"
    
    zoho_contact_id = fields.Char(
        string="Zoho Contact ID",
        index=True,
        copy=False,
        help="Unique identifier from Zoho Books"
    )
    zoho_synced = fields.Boolean(
        string="Synced from Zoho",
        default=False,
        readonly=True,
        help="Indicates this partner was imported from Zoho Books"
    )
    zoho_sync_date = fields.Datetime(
        string="Last Zoho Sync",
        readonly=True,
        help="Date of last synchronization with Zoho Books"
    )