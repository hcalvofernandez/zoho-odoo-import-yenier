from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import urllib.parse
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)

class ZohoConnector(models.Model):
    _name = "zoho.connector"
    _description = "Zoho Books Connector"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    
    name = fields.Char(string="Name", required=True, default="Zoho Production", tracking=True)
    state = fields.Selection([
        ("draft", "Draft"),
        ("active", "Active"),
        ("expired", "Token Expired")
    ], string="Status", default="draft", tracking=True)
    
    client_id = fields.Char(string="Client ID", required=True)
    client_secret = fields.Char(string="Client Secret", required=True)
    redirect_url = fields.Char(string="Redirect URL", required=True, 
                               default="http://localhost:8069/zoho/callback")
    country_endpoint = fields.Selection([
        ("com", "United States (.com)"),
        ("eu", "Europe (.eu)"),
        ("in", "India (.in)"),
        ("com.au", "Australia (.com.au)"),
        ("com.cn", "China (.com.cn)"),
        ("jp", "Japan (.jp)"),
    ], string="Data Center", required=True, default="com")
    
    auth_code = fields.Char(string="Authorization Code")
    access_token = fields.Char(string="Access Token")
    refresh_token = fields.Char(string="Refresh Token")
    expires_in = fields.Datetime(string="Token Expires On")
    
    organization_id = fields.Char(string="Organization ID", help="Zoho Books Organization ID")
    
    import_products = fields.Boolean(string="Import Products", default=True)
    import_stock = fields.Boolean(string="Import Product Stock", default=False)
    import_customers = fields.Boolean(string="Import Customers", default=True)
    import_vendors = fields.Boolean(string="Import Vendors", default=True)
    import_sale_orders = fields.Boolean(string="Import Sale Orders", default=False)
    import_invoices = fields.Boolean(string="Import Invoices", default=False)
    import_bills = fields.Boolean(string="Import Vendor Bills", default=False)
    import_customer_payments = fields.Boolean(string="Import Customer Payments", default=False)
    import_vendor_payments = fields.Boolean(string="Import Vendor Payments", default=False)
    import_customer_credits = fields.Boolean(string="Import Customer Credits", default=False)
    import_vendor_credits = fields.Boolean(string="Import Vendor Credits", default=False)
    
    last_product_sync = fields.Datetime(string="Last Product Sync")
    last_partner_sync = fields.Datetime(string="Last Partner Sync")
    last_sale_sync = fields.Datetime(string="Last Sale Sync")
    last_invoice_sync = fields.Datetime(string="Last Invoice Sync")
    
    is_token_valid = fields.Boolean(string="Token Valid", compute="_compute_token_valid")
    
    _sql_constraints = [
        ("unique_connector", "UNIQUE(name)", "Connector name must be unique!")
    ]

    @api.model
    def name_create(self, name):
        raise UserError(_(
            "Zoho connectors require a full configuration. "
            "Please use 'Create and Edit...' to enter the Client ID and Client Secret."
        ))
    
    @api.depends("access_token", "expires_in")
    def _compute_token_valid(self):
        for rec in self:
            rec.is_token_valid = bool(
                rec.access_token and rec.expires_in and rec.expires_in > datetime.now()
            )
    
    def _get_base_url(self):
        self.ensure_one()
        return f"https://www.zohoapis.{self.country_endpoint}/books"
    
    def _get_accounts_url(self):
        self.ensure_one()
        return f"https://accounts.zoho.{self.country_endpoint}"
    
    def _get_api_url(self, endpoint):
        self.ensure_one()
        base = self._get_base_url()
        org_id = self.organization_id
        if org_id:
            return f"{base}/v3/{endpoint}?organization_id={org_id}"
        return f"{base}/v3/{endpoint}"
    
    def _get_headers(self):
        self.ensure_one()
        if not self.access_token:
            raise UserError(_("No access token available. Please authenticate first."))
        
        if self.expires_in and self.expires_in <= datetime.now():
            self._refresh_access_token()
            
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _refresh_access_token(self):
        self.ensure_one()
        if not self.refresh_token:
            raise UserError(_("No refresh token available. Please re-authenticate."))
        
        url = f"{self._get_accounts_url()}/oauth/v2/token"
        data = {
            "refresh_token": self.refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token"
        }
        
        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise UserError(_("Token refresh failed: %s") % result.get("error"))
            
            self.write({
                "access_token": result.get("access_token"),
                "expires_in": datetime.now() + timedelta(seconds=result.get("expires_in", 3600))
            })
            _logger.info("Zoho token refreshed successfully for connector %s", self.name)
            
        except requests.exceptions.RequestException as e:
            raise UserError(_("Connection error during token refresh: %s") % str(e))
    
    def action_generate_auth_url(self):
        self.ensure_one()
        if not self.client_id or not self.redirect_url:
            raise UserError(_("Client ID and Redirect URL are required."))
        
        base_url = f"{self._get_accounts_url()}/oauth/v2/auth"
        params = {
            "scope": "ZohoBooks.fullaccess.all",
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_url,
            "access_type": "offline",
            "prompt": "consent"
        }
        auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        return {
            "type": "ir.actions.act_url",
            "url": auth_url,
            "target": "new",
            "name": _("Zoho Authorization")
        }
    
    def action_activate(self):
        self.ensure_one()
        if not self.auth_code:
            raise UserError(_("Please enter the authorization code first."))
        
        url = f"{self._get_accounts_url()}/oauth/v2/token"
        data = {
            "code": self.auth_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_url,
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise UserError(_("Authentication failed: %s") % result.get("error"))
            
            self.write({
                "access_token": result.get("access_token"),
                "refresh_token": result.get("refresh_token"),
                "expires_in": datetime.now() + timedelta(seconds=result.get("expires_in", 3600)),
                "state": "active"
            })
            
            self._detect_organization()
            
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _("Zoho connector activated successfully!"),
                    "type": "success",
                    "sticky": False,
                }
            }
            
        except requests.exceptions.RequestException as e:
            raise UserError(_("Connection error: %s") % str(e))
    
    def _detect_organization(self):
        self.ensure_one()
        try:
            url = f"{self._get_base_url()}/v3/organizations"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            if response.status_code == 200:
                data = response.json()
                organizations = data.get("organizations", [])
                if organizations:
                    self.organization_id = str(organizations[0].get("organization_id"))
                    _logger.info("Auto-detected organization ID: %s", self.organization_id)
        except Exception as e:
            _logger.warning("Could not auto-detect organization: %s", str(e))
    
    def action_test_connection(self):
        self.ensure_one()
        if self.state != "active":
            raise UserError(_("Connector must be active to test connection."))
        
        try:
            url = self._get_api_url("organizations")
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            
            data = response.json()
            orgs = data.get("organizations", [])
            org_name = orgs[0].get("name", "Unknown") if orgs else "Unknown"
            
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Successful"),
                    "message": _("Connected to Zoho Books organization: %s") % org_name,
                    "type": "success",
                    "sticky": False,
                }
            }
            
        except requests.exceptions.RequestException as e:
            raise UserError(_("Connection failed: %s") % str(e))
    
    def action_refresh_token(self):
        self.ensure_one()
        self._refresh_access_token()
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Token Refreshed"),
                "message": _("Access token has been refreshed successfully."),
                "type": "success",
                "sticky": False,
            }
        }
    
    def action_reset(self):
        self.ensure_one()
        self.write({
            "state": "draft",
            "access_token": False,
            "refresh_token": False,
            "expires_in": False,
            "auth_code": False,
        })
        return True
    
    def _cron_auto_sync_products(self):
        connectors = self.search([("state", "=", "active"), ("import_products", "=", True)])
        for connector in connectors:
            try:
                wizard = self.env["zoho.product.import"].create({
                    "connector_id": connector.id,
                    "update_existing": True,
                })
                wizard.action_import_products()
            except Exception as e:
                _logger.error("Auto-sync products failed for %s: %s", connector.name, str(e))
    
    def _cron_auto_sync_partners(self):
        connectors = self.search([
            ("state", "=", "active"),
            "|", ("import_customers", "=", True), ("import_vendors", "=", True)
        ])
        for connector in connectors:
            try:
                wizard = self.env["zoho.partner.import"].create({
                    "connector_id": connector.id,
                    "partner_type": "both",
                    "update_existing": True,
                })
                wizard.action_import_partners()
            except Exception as e:
                _logger.error("Auto-sync partners failed for %s: %s", connector.name, str(e))
