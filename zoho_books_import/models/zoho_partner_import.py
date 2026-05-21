from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class ZohoPartnerImport(models.TransientModel):
    _name = "zoho.partner.import"
    _description = "Import Partners from Zoho"
    _transient_max_hours = 0.25
    
    connector_id = fields.Many2one("zoho.connector", string="Zoho Connector", required=True)
    partner_type = fields.Selection([
        ("customer", "Customers Only"),
        ("vendor", "Vendors Only"),
        ("both", "Both Customers and Vendors")
    ], string="Partner Type", default="both", required=True)
    update_existing = fields.Boolean(string="Update Existing Partners", default=True)

    def _extract_zoho_error(self, response):
        try:
            error_data = response.json()
        except ValueError:
            return response.text[:500] or str(response.status_code)

        message = error_data.get("message") or error_data.get("error") or response.text[:500]
        code = error_data.get("code")
        if code:
            return f"[{code}] {message}"
        return message
    
    def action_import_partners(self):
        self.ensure_one()
        connector = self.connector_id
        
        if connector.state != "active":
            raise UserError(_("Connector is not active!"))
        
        import_types = []
        if self.partner_type in ["customer", "both"]:
            if not connector.import_customers:
                raise UserError(_("Customer import is not enabled in connector settings."))
            import_types.append("customer")
        
        if self.partner_type in ["vendor", "both"]:
            if not connector.import_vendors:
                raise UserError(_("Vendor import is not enabled in connector settings."))
            import_types.append("vendor")
        
        results = {}
        for imp_type in import_types:
            log = self.env["zoho.import.log"].create({
                "connector_id": connector.id,
                "import_type": imp_type,
                "state": "in_progress",
                "start_time": fields.Datetime.now(),
            })
            
            try:
                result = self._import_contacts(connector, imp_type, log)
                results[imp_type] = result
                connector.write({"last_partner_sync": fields.Datetime.now()})
                
            except Exception as e:
                log.write({
                    "state": "error",
                    "error_details": str(e),
                    "end_time": fields.Datetime.now(),
                })
                raise UserError(_("Failed to import %s: %s") % (imp_type, str(e)))
        
        total_imported = sum(r.get("imported", 0) for r in results.values())
        total_updated = sum(r.get("updated", 0) for r in results.values())
        total_failed = sum(r.get("failed", 0) for r in results.values())
        
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Import Complete"),
                "message": _("Partners: %(imported)s created, %(updated)s updated, %(failed)s failed") % {
                    "imported": total_imported, "updated": total_updated, "failed": total_failed
                },
                "type": "success" if total_failed == 0 else "warning",
                "sticky": False,
            }
        }
    
    def _import_contacts(self, connector, contact_type, log):
        all_contacts = self._fetch_contacts(connector, contact_type)
        total = len(all_contacts)
        imported = 0
        updated = 0
        failed = 0
        errors = []
        created_partners = self.env["res.partner"]
        
        for contact in all_contacts:
            try:
                result = self._create_or_update_partner(connector, contact, contact_type)
                if result.get("created"):
                    created_partners |= result.get("partner")
                    imported += 1
                elif result.get("updated"):
                    updated += 1
            except Exception as e:
                failed += 1
                error_msg = f"Contact '{contact.get('contact_name', 'Unknown')}': {str(e)}"
                errors.append(error_msg)
                _logger.error(error_msg)
        
        state = "done"
        if failed > 0 and (imported > 0 or updated > 0):
            state = "partial"
        elif failed > 0 and imported == 0 and updated == 0:
            state = "error"
        
        log.write({
            "state": state,
            "total_records": total,
            "imported_records": imported,
            "updated_records": updated,
            "failed_records": failed,
            "error_details": "\n".join(errors) if errors else False,
            "partner_ids": [(6, 0, created_partners.ids)],
            "end_time": fields.Datetime.now(),
        })
        
        return {
            "imported": imported,
            "updated": updated,
            "failed": failed,
        }
    
    def _fetch_contacts(self, connector, contact_type):
        all_contacts = []
        page = 1
        
        while True:
            url = connector._get_api_url("contacts")
            params = {
                "page": page,
                "per_page": 200,
                "contact_type": contact_type,
            }
            
            try:
                response = requests.get(url, headers=connector._get_headers(), 
                                       params=params, timeout=60)
                if response.status_code != 200:
                    raise UserError(_("Zoho API error while fetching contacts: %s") % self._extract_zoho_error(response))
            except requests.exceptions.RequestException as e:
                raise UserError(_("Failed to fetch contacts: %s") % str(e))
            
            data = response.json()
            contacts = data.get("contacts", [])
            
            if not contacts:
                break
            
            all_contacts.extend(contacts)
            page += 1
            
            if page > 200:
                _logger.warning("Reached max page limit for contacts")
                break
        
        _logger.info("Fetched %s %s contacts from Zoho", len(all_contacts), contact_type)
        return all_contacts
    
    def _create_or_update_partner(self, connector, zoho_data, contact_type):
        Partner = self.env["res.partner"]
        
        zoho_id = zoho_data.get("contact_id")
        name = zoho_data.get("contact_name")
        email = zoho_data.get("email")
        
        if not name:
            return {"partner": False, "created": False, "updated": False}
        
        domain = [("zoho_contact_id", "=", zoho_id)]
        if email:
            domain = ["|"] + domain + [("email", "=", email)]
        
        existing = Partner.search(domain, limit=1)
        
        is_customer = contact_type == "customer"
        is_vendor = contact_type == "vendor"
        
        billing = zoho_data.get("billing_address", {}) or {}
        
        vals = {
            "name": name,
            "zoho_contact_id": zoho_id,
            "zoho_synced": True,
            "zoho_sync_date": fields.Datetime.now(),
            "email": email,
            "phone": zoho_data.get("phone"),
            "mobile": zoho_data.get("mobile"),
            "website": zoho_data.get("website"),
            "vat": zoho_data.get("tax_id") or zoho_data.get("gst_no"),
            "street": billing.get("address"),
            "street2": billing.get("street2"),
            "city": billing.get("city"),
            "zip": billing.get("zip"),
            "state_id": self._get_state(billing.get("state")),
            "country_id": self._get_country(billing.get("country")),
            "customer_rank": 1 if is_customer else 0,
            "supplier_rank": 1 if is_vendor else 0,
            "is_company": zoho_data.get("contact_type") == "company",
            "company_type": "company" if zoho_data.get("contact_type") == "company" else "person",
            "comment": zoho_data.get("notes"),
        }
        
        if zoho_data.get("currency_code"):
            currency = self.env["res.currency"].search([
                ("name", "=", zoho_data["currency_code"])
            ], limit=1)
            if currency:
                pricelist = self.env["product.pricelist"].search([
                    ("currency_id", "=", currency.id)
                ], limit=1)
                if pricelist:
                    vals["property_product_pricelist"] = pricelist.id
        
        if existing and self.update_existing:
            existing.write(vals)
            return {"partner": existing, "created": False, "updated": True}
        elif not existing:
            partner = Partner.create(vals)
            return {"partner": partner, "created": True, "updated": False}
        
        return {"partner": existing, "created": False, "updated": False, "skipped": True}
    
    def _get_state(self, state_name):
        if not state_name:
            return False
        state = self.env["res.country.state"].search([
            ("name", "ilike", state_name)
        ], limit=1)
        return state.id if state else False
    
    def _get_country(self, country_name):
        if not country_name:
            return False
        country = self.env["res.country"].search([
            ("name", "ilike", country_name)
        ], limit=1)
        return country.id if country else False
