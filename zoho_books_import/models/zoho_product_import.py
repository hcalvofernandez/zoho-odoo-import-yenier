from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class ZohoProductImport(models.TransientModel):
    _name = "zoho.product.import"
    _description = "Import Products from Zoho"
    _transient_max_hours = 1

    connector_id = fields.Many2one("zoho.connector", string="Zoho Connector", required=True)
    update_existing = fields.Boolean(string="Update Existing Products", default=True)
    import_stock = fields.Boolean(string="Import Stock Levels", default=False)
    create_categories = fields.Boolean(string="Create Missing Categories", default=True)

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

    def action_import_products(self):
        self.ensure_one()
        connector = self.connector_id

        if connector.state != "active":
            raise UserError(_("Zoho connector is not active! Please activate it first."))

        if not connector.import_products:
            raise UserError(_("Product import is not enabled in connector settings."))

        log = self.env["zoho.import.log"].create({
            "connector_id": connector.id,
            "import_type": "product",
            "state": "in_progress",
            "start_time": fields.Datetime.now(),
        })

        try:
            products = self._fetch_zoho_products(connector)
            total = len(products)
            imported = 0
            updated = 0
            failed = 0
            skipped = 0
            errors = []
            created_products = self.env["product.template"]

            for zoho_product in products:
                try:
                    result = self._create_or_update_product(connector, zoho_product, log)
                    if result.get("created"):
                        created_products |= result.get("product")
                        imported += 1
                    elif result.get("updated"):
                        updated += 1
                    else:
                        skipped += 1

                    if self.import_stock and zoho_product.get("item_id"):
                        self._import_stock(connector, result.get("product"), zoho_product["item_id"])

                except Exception as e:
                    failed += 1
                    error_msg = f"Product '{zoho_product.get('name', 'Unknown')}': {str(e)}"
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
                "skipped_records": skipped,
                "error_details": "\n".join(errors) if errors else False,
                "product_ids": [(6, 0, created_products.ids)],
                "end_time": fields.Datetime.now(),
            })

            connector.write({"last_product_sync": fields.Datetime.now()})

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Import Complete"),
                    "message": _("Products: %(imported)s created, %(updated)s updated, %(failed)s failed") % {
                        "imported": imported, "updated": updated, "failed": failed
                    },
                    "type": "success" if state == "done" else "warning",
                    "sticky": False,
                }
            }

        except Exception as e:
            log.write({
                "state": "error",
                "error_details": str(e),
                "end_time": fields.Datetime.now(),
            })
            raise UserError(_("Import failed: %s") % str(e))

    def _fetch_zoho_products(self, connector, page=1):
        all_products = []

        _logger.info("Starting product import from Zoho. Organization ID: %s", connector.organization_id)

        while True:
            url = connector._get_api_url("items")
            params = {
                "page": page,
                "per_page": 200,
            }

            _logger.info("Fetching page %s. URL: %s", page, url)

            try:
                headers = connector._get_headers()
                _logger.info("Headers: %s", {k: v[:20] + "..." if len(str(v)) > 20 else v for k, v in headers.items()})

                response = requests.get(url, headers=headers,
                                        params=params, timeout=60)

                _logger.info("Response status: %s", response.status_code)

                if response.status_code != 200:
                    error_message = self._extract_zoho_error(response)
                    _logger.error("Response body: %s", response.text[:500])
                    raise UserError(_("Zoho API error while fetching products: %s") % error_message)

            except requests.exceptions.RequestException as e:
                _logger.error("Request failed: %s", str(e))
                raise UserError(_("Failed to fetch products from Zoho: %s") % str(e))

            data = response.json()
            products = data.get("items", [])

            _logger.info("Page %s returned %s products", page, len(products))

            if not products:
                break

            all_products.extend(products)
            page += 1

            if page > 200:
                _logger.warning("Reached max page limit (200) for product import")
                break

        _logger.info("Fetched %s products from Zoho", len(all_products))
        return all_products

    def _create_or_update_product(self, connector, zoho_data, log):
        ProductTemplate = self.env["product.template"]

        zoho_id = zoho_data.get("item_id")
        sku = zoho_data.get("sku") or zoho_data.get("item_code")
        name = zoho_data.get("name")

        if not name:
            return {"product": False, "created": False, "updated": False}

        domain = [("zoho_item_id", "=", zoho_id)]
        if sku:
            domain = ["|"] + domain + [("default_code", "=", sku)]

        existing = ProductTemplate.search(domain, limit=1)

        product_type = zoho_data.get("product_type", "goods")

        vals = {
            "name": name,
            "default_code": sku,
            "zoho_item_id": zoho_id,
            "zoho_synced": True,
            "zoho_sync_date": fields.Datetime.now(),
            "list_price": float(zoho_data.get("rate", 0) or 0),
            "standard_price": float(zoho_data.get("purchase_rate", 0) or 0),
            "description": zoho_data.get("description"),
            "weight": float(zoho_data.get("weight", 0) or 0),
            "sale_ok": True,
            "purchase_ok": True,
            # NUEVO: Guardar el tipo original de Zoho para referencia futura
            "zoho_product_type": product_type,
        }

        vals.update(self._get_product_type_vals(ProductTemplate, product_type))

        category_name = zoho_data.get("category_name")
        if category_name and self.create_categories:
            vals["categ_id"] = self._get_or_create_category(category_name)

        uom_name = zoho_data.get("unit")
        if uom_name:
            uom_id = self._get_uom(uom_name)
            if uom_id:
                vals["uom_id"] = uom_id
                vals["uom_po_id"] = uom_id

        if zoho_data.get("tax_id"):
            tax = self._map_tax(connector, zoho_data["tax_id"])
            if tax:
                vals["taxes_id"] = [(6, 0, [tax.id])]

        if existing and self.update_existing:
            existing.write(vals)
            return {"product": existing, "created": False, "updated": True}
        elif not existing:
            product = ProductTemplate.create(vals)
            return {"product": product, "created": True, "updated": False}

        return {"product": existing, "created": False, "updated": False, "skipped": True}

    def _get_product_type_vals(self, product_model, zoho_product_type):
        """
        MAPEO CORREGIDO DE TIPOS DE PRODUCTO ZOHO -> ODOO
        
        Zoho envia: goods | service | consumable
        Odoo acepta: product (stockeable) | consu (consumible) | service (servicio)
        
        Problema original: service y consumable en Zoho SI llevan cantidad,
        pero en Odoo 'service' NO tiene stock. Solucion: mapear todo lo
        cuantificable a 'product' o 'consu' para que Odoo permita cantidad.
        """
        target_field = None

        # Detectar qué campo usar según la versión de Odoo
        if "detailed_type" in product_model._fields:
            target_field = "detailed_type"
        elif "type" in product_model._fields:
            target_field = "type"
        else:
            return {}

        field = product_model._fields[target_field]
        selection = field.selection(product_model) if callable(field.selection) else field.selection
        valid_values = [value for value, _label in selection] if selection else []

        # MAPEO CORREGIDO POR TIPO ZOHO
        if zoho_product_type == "goods":
            # Bienes: siempre stockeable (product) si está disponible
            preferred_value = "product" if "product" in valid_values else "consu"
            
        elif zoho_product_type == "consumable":
            # Consumibles: consumible en Odoo (lleva cantidad, sin valoración estricta)
            preferred_value = "consu"
            
        elif zoho_product_type == "service":
            # Servicios con cantidad en Zoho: forzamos a stockeable para que Odoo
            # permita cantidad (ej: 10 horas de consultoría, 5 días de soporte)
            # Se marca con zoho_product_type="service" para saber que es servicio
            preferred_value = "product" if "product" in valid_values else "consu"
            
        else:
            # Fallback para cualquier otro tipo no esperado
            preferred_value = "consu"

        if preferred_value in valid_values:
            return {target_field: preferred_value}

        # Fallbacks por si no está el valor preferido
        for candidate in ("product", "consu", "service"):
            if candidate in valid_values:
                return {target_field: candidate}

        if valid_values:
            _logger.warning(
                "Unexpected selection values for product type field '%s': %s. Falling back to '%s'",
                target_field, valid_values, valid_values[0]
            )
            return {target_field: valid_values[0]}

        return {}

    def _get_or_create_category(self, category_name):
        if not category_name:
            return self.env.ref("product.product_category_all").id

        Category = self.env["product.category"]
        category = Category.search([("name", "=ilike", category_name)], limit=1)
        if not category:
            category = Category.create({"name": category_name})
        return category.id

    def _get_uom(self, uom_name):
        if not uom_name:
            return False

        UOM = self.env["uom.uom"]
        uom = UOM.search([("name", "ilike", uom_name)], limit=1)
        if uom:
            return uom.id
        return False

    def _map_tax(self, connector, zoho_tax_id):
        if not zoho_tax_id:
            return False

        try:
            url = connector._get_api_url(f"taxes/{zoho_tax_id}")
            response = requests.get(url, headers=connector._get_headers(), timeout=30)
            if response.status_code != 200:
                return False

            tax_data = response.json().get("tax", {})
            tax_name = tax_data.get("tax_name")
            tax_rate = float(tax_data.get("tax_percentage", 0))

            if not tax_name:
                return False

            Tax = self.env["account.tax"]
            tax = Tax.search([
                ("name", "=", tax_name),
                ("amount", "=", tax_rate),
                ("type_tax_use", "=", "sale")
            ], limit=1)

            if not tax:
                tax = Tax.create({
                    "name": tax_name,
                    "amount": tax_rate,
                    "type_tax_use": "sale",
                    "amount_type": "percent",
                })
            return tax

        except Exception as e:
            _logger.warning("Failed to map tax %s: %s", zoho_tax_id, str(e))
            return False

    def _import_stock(self, connector, product, zoho_item_id):
        if not product or not product.product_variant_id:
            return False

        try:
            url = connector._get_api_url(f"items/{zoho_item_id}")
            response = requests.get(url, headers=connector._get_headers(), timeout=30)
            if response.status_code != 200:
                return False

            data = response.json().get("item", {})
            stock_on_hand = float(data.get("stock_on_hand", 0))

            Quant = self.env["stock.quant"]
            product_variant = product.product_variant_id

            internal_quants = Quant.search([
                ("product_id", "=", product_variant.id),
                ("location_id.usage", "=", "internal"),
            ])

            if internal_quants:
                internal_quants[0].write({"quantity": stock_on_hand})
            else:
                internal_loc = self.env["stock.location"].search([
                    ("usage", "=", "internal"),
                ], limit=1)

                if internal_loc:
                    Quant.create({
                        "product_id": product_variant.id,
                        "location_id": internal_loc.id,
                        "quantity": stock_on_hand,
                    })

            return True

        except Exception as e:
            _logger.warning("Failed to import stock for product %s: %s", product.name, str(e))
            return False