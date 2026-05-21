from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ZohoAuthController(http.Controller):
    
    @http.route("/zoho/callback", type="http", auth="public", website=False)
    def zoho_callback(self, **kwargs):
        """Handle Zoho OAuth2 callback"""
        code = kwargs.get("code")
        error = kwargs.get("error")

        _logger.info("Zoho callback received: code=%s, error=%s", code[:10] if code else None, error)

        if error:
            return request.render("zoho_books_import.zoho_auth_error", {
                "error": error,
                "error_description": kwargs.get("error_description", "")
            })

        if not code:
            return request.render("zoho_books_import.zoho_auth_error", {
                "error": "No code provided",
                "error_description": "Zoho did not return an authorization code."
            })

        # Buscar el conector más reciente en estado draft
        connector = request.env["zoho.connector"].sudo().search([
            ("state", "=", "draft"),
        ], limit=1, order="create_date desc")

        if not connector:
            return request.render("zoho_books_import.zoho_auth_error", {
                "error": "No connector found",
                "error_description": "No pending Zoho connector found. Please create one first."
            })

        _logger.info("Found connector: %s (ID: %s)", connector.name, connector.id)
        connector.sudo().write({"auth_code": code})
        _logger.info("Auth code saved successfully for connector %s", connector.name)

        return request.render("zoho_books_import.zoho_auth_success", {
            "connector_name": connector.name,
            "code": code[:10] + "...",  # Solo mostrar primeros 10 caracteres por seguridad
        })