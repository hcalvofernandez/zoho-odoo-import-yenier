# DoorAndDoor - Estado de Entrega en Picking

## Descripción

Módulo para Odoo 18 que muestra en las líneas de movimiento de un picking la información de entrega relacionada con la venta original, facilitando el control de entregas parciales.

Estado actual del desarrollo:

- Campos compute para cantidad pedida, entregada y pendiente
- Compatibilidad robusta con diferentes configuraciones de Odoo 18
- Columnas visibles en todas las vistas de entregas
- Enfoque seguro con fallback para campos de cantidad

## Estructura funcional

Principales componentes del módulo:

- `models/stock_move.py`
  Extiende `stock.move` con campos compute para seguimiento de entregas.
- `views/stock_move_views.xml`
  Herencias de vistas de movimientos para mostrar columnas de estado.
- `views/stock_picking_views.xml`
  Herencias de vistas de picking para mostrar columnas en líneas de movimiento.

## Campos Agregados

| Campo | Descripción | Editable |
|-------|-------------|----------|
| **Cantidad Pedida** (qty_ordered) | Lo que el cliente ordenó en la venta original | ❌ No |
| **Entregado** (qty_delivered_this) | Cantidad entregada en ESTE picking específico | ❌ No |
| **Pendiente** (qty_pending) | Cantidad pendiente = Pedida - Entregado | ❌ No |

## Vistas Afectadas

- **Formulario de Picking** (`stock.view_picking_form`)
  - Líneas de movimiento (`move_ids_without_package`)
  - Operaciones detalladas (`move_line_ids_without_package`)

- **Vista Tree de Movimientos** (`stock.view_move_tree`)
- **Vista Tree de Movimientos (Picking)** (`stock.view_move_tree_picking`)
- **Vista Form de Movimiento** (`stock.view_move_form`)

## Dependencias

- `doorandoor_sale_delivery_button`
- `stock`
- `sale`
- `sale_stock`

## Historial del proceso de desarrollo

### Etapa 1: desarrollo inicial

Implementación base del módulo con campos compute para mostrar cantidad pedida, entregada y pendiente en las líneas de movimiento de picking.

### Etapa 2: corrección de compatibilidad con Odoo 18 (quantity_done)

Problema detectado:

- El campo `quantity_done` no existe directamente en `stock.move` en Odoo 18
- Error: `AttributeError: 'stock.move' object has no attribute 'quantity_done'`

Corrección aplicada:

- `_compute_qty_delivered_this`: Intenta usar `move_line_ids.qty_done` o `quantity` como fallback

### Etapa 3: corrección de compatibilidad con Odoo 18 (qty_done en move_line_ids)

Problema detectado:

- El campo `qty_done` no existe en `stock.move.line` en todas las instalaciones de Odoo 18
- Error: `ValueError: Wrong @depends on '_compute_qty_delivered_this'. Dependency field 'qty_done' not found in model stock.move.line`

Corrección aplicada:

- `@api.depends('move_line_ids')`: Depende solo de la relación, no del campo específico
- `_compute_qty_delivered_this`: Usa `hasattr` para verificar existencia de campos (`qty_done`, `quantity`, `product_uom_qty`) con fallbacks progresivos
- Enfoque compatible con diferentes configuraciones de Odoo 18

## Estado actual conocido

Confirmado en pruebas recientes:

- El módulo instala correctamente después de las correcciones de compatibilidad
- Los campos compute se calculan correctamente con el enfoque robusto
- Compatible con diferentes configuraciones de Odoo 18

Pendiente de validar completamente:

- Pruebas de entregas parciales con múltiples pickings
- Comportamiento en diferentes configuraciones de Odoo 18

## Changelog resumido reciente

- `18.0.1.0.0`
  Base inicial del módulo.
- `18.0.1.0.1`
  Corrección de compatibilidad con Odoo 18 (uso de move_line_ids.qty_done en lugar de quantity_done).
- `18.0.1.0.4`
  Corrección robusta de compatibilidad con Odoo 18 (enfoque seguro con hasattr y fallbacks para qty_done/quantity/product_uom_qty).

## Datos técnicos

- **Versión de Odoo**: 18.0
- **Ruta del módulo**: `/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_delivery_status`
- **Modelos extendidos**:
  - `stock.move`
- **Campos agregados**:
  - `qty_ordered`: Float, compute, readonly
  - `qty_delivered_this`: Float, compute, readonly
  - `qty_pending`: Float, compute, readonly
  - `has_sale_order`: Boolean, compute, readonly
- **Vistas heredadas**:
  - `stock.view_picking_form` (2 herencias)
  - `stock.view_move_tree`
  - `stock.view_move_tree_picking`
  - `stock.view_move_form`

## Instalación

1. Copiar la carpeta `doorandoor_delivery_status` al directorio `addons/` de Odoo
2. Actualizar la lista de aplicaciones
3. Instalar el módulo

## Autor

DoorAndDoor Team
