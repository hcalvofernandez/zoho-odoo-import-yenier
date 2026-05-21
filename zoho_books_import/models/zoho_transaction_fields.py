from odoo import models, fields

class AccountMove(models.Model):
    _inherit = "account.move"
    
    zoho_invoice_id = fields.Char(
        string="Zoho Invoice/Bill ID",
        index=True,
        copy=False,
        help="Unique identifier from Zoho Books"
    )
    zoho_synced = fields.Boolean(
        string="Synced from Zoho",
        default=False,
        readonly=True
    )
    zoho_sync_date = fields.Datetime(
        string="Last Zoho Sync",
        readonly=True
    )

class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    zoho_salesorder_id = fields.Char(
        string="Zoho Sales Order ID",
        index=True,
        copy=False,
        help="Unique identifier from Zoho Books"
    )
    zoho_synced = fields.Boolean(
        string="Synced from Zoho",
        default=False,
        readonly=True
    )
    zoho_sync_date = fields.Datetime(
        string="Last Zoho Sync",
        readonly=True
    )

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    zoho_payment_id = fields.Char(
        string="Zoho Payment ID",
        index=True,
        copy=False,
        help="Unique identifier from Zoho Books"
    )
    zoho_synced = fields.Boolean(
        string="Synced from Zoho",
        default=False,
        readonly=True
    )
    zoho_sync_date = fields.Datetime(
        string="Last Zoho Sync",
        readonly=True
    )