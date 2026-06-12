# -*- coding: utf-8 -*-
{
    "name": "DoorAndDoor Sales New",
    "version": "18.0.1.0.29",
    "category": "Sales",
    "summary": "Invoice-driven sales, payment release, delivery and production orchestration",
    "description": """
DoorAndDoor Sales New
=====================

Objetivo
--------

Este modulo centraliza el nuevo flujo comercial y operativo de DoorAndDoor con la factura como documento maestro.

La meta es soportar un proceso donde:
- la factura origina el pedido comercial interno
- el pago libera cantidades de productos
- la liberacion crea operaciones de inventario o fabricacion
- el usuario puede seguir todo el flujo desde la factura

Alcance funcional
-----------------

1. Factura publicada
   - crear pedido de venta en borrador
   - vincular lineas de factura con lineas de venta
   - crear lineas internas de cumplimiento

2. Pago aplicado
   - calcular liberacion segun politica configurada
   - decidir ruta: stock o fabricacion
   - crear pickings o producciones por la parte cubierta

3. Logistica
   - seguimiento de entregas
   - trazabilidad por factura, pedido, picking y produccion
   - integracion gradual con impresion, firmas y documentos operativos

Relacion con otros modulos
--------------------------

Actualmente este modulo depende de doorandoor_delivery_status.

La intencion por ahora no es reemplazarlo de inmediato, sino reutilizar sus utilidades visuales para movimientos y operaciones de stock mientras doorandoor_sales_new asume la logica principal del nuevo flujo.

Estructura principal
--------------------

- models/account_move.py
  Extiende factura y concentra el flujo principal.

- models/account_move_line.py
  Agrega enlaces tecnicos hacia lineas de venta y cumplimiento.

- models/fulfillment_line.py
  Modelo central para rastrear cantidades facturadas, liberadas, enviadas y entregadas.

- models/mrp_production.py
  Sincroniza la produccion terminada con la generacion del despacho de salida.

- models/stock_picking.py
  Actualiza el estado de entrega al validar operaciones de salida.

- views/account_move_views.xml
  Agrega smart buttons, configuracion y pestaña de cumplimiento en factura.

Historial resumido
------------------

- 18.0.1.0.0 a 18.0.1.0.3
  Se crea la base del modulo, la generacion de sale order desde factura y la liberacion por pago con bitacora.

- 18.0.1.0.4 a 18.0.1.0.8
  Se corrigen vistas, sincronizacion historica, compatibilidad con lineas de producto y seguridad de logs, ademas de simplificar la vista de cumplimiento.

- 18.0.1.0.9 a 18.0.1.0.11
  Se incorpora la automatizacion de despachos por stock y el lanzamiento base de ordenes de fabricacion.

- 18.0.1.0.12 a 18.0.1.0.14
  Se agregan bloques de firma en reportes, referencia visible a ordenes de despacho en factura y el cierre del ciclo factura -> fabricacion -> entrega.

Autor
-----

Hanoi Calvo Fernández (doorandoor)
    """,
    "author": "Hanoi Calvo Fernández (doorandoor)",
    "website": "https://doorandoor.com",
    "depends": [
        "account",
        "sale_management",
        "stock",
        "mrp",
        "mail",
        "doorandoor_delivery_status",
    ],
    "data": [
        "data/pickup_order_sequence.xml",
        "security/ir.model.access.csv",
        "views/fulfillment_line_views.xml",
        "views/payment_release_log_views.xml",
        "views/pickup_order_views.xml",
        "views/account_move_views.xml",
        "views/sale_order_views.xml",
        "views/res_partner_views.xml",
        "views/res_partner_category_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu_views.xml",
        "views/report_signature_templates.xml",
        "views/pickup_order_report.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
