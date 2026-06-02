# DoorAndDoor - Estado de Entrega en Picking

## Descripción

Módulo para Odoo 18 que muestra en las líneas de movimiento de un picking la información de entrega relacionada con la venta original.

## Campos Agregados

| Campo | Descripción | Editable |
|-------|-------------|----------|
| **Cantidad Pedida** | Lo que el cliente ordenó en la venta original | ❌ No |
| **Entregado** | Cantidad entregada en ESTE picking específico | ✅ Sí |
| **Pendiente** | Cantidad pendiente = Pedida - Entregado | ❌ No |

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

## Instalación

1. Copiar la carpeta `doorandoor_delivery_status` al directorio `addons/` de Odoo
2. Actualizar la lista de aplicaciones
3. Instalar el módulo

## Autor

DoorAndDoor Team
