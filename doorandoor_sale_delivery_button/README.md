# DoorAndDoor - Botón de Entrega desde Ventas

## Descripción

Módulo para Odoo 18 que permite al gestor de ventas navegar directamente al picking de entrega desde un pedido de venta confirmado, con la posibilidad de crear uno nuevo si no existe.

## Características

- **Botón "Entregar"** en el header del formulario de ventas confirmadas
- **Botón inteligente (stat button)** con contador de entregas relacionadas
- **Campo formal `sale_id`** en `stock.picking` para relación robusta venta-picking
- **Soporte para entregas parciales**: múltiples pickings por venta
- **Determinación automática del almacén** según la compañía de la venta
- **Filtro automático** de productos stockeables al crear picking

## Flujo de Negocio

```
Venta Confirmada
    │
    ├──► [Botón "Entregar" en Header]
    │
    ├──► ¿Existe picking en borrador?
    │       ├──► SÍ → Abre ese picking
    │       └──► NO → ¿Existe picking validado?
    │                   ├──► SÍ → Abre el validado
    │                   └──► NO → Crea picking nuevo
    │                               └──► En almacén de la compañía
    │                               └──► Con líneas de productos stockeables
    │
    └──► [Stat Button "Entregas"]
            └──► Muestra contador de pickings relacionados
            └──► Click abre lista de entregas o formulario
```

## Decisiones de Diseño

| # | Decisión | Implementación |
|---|----------|----------------|
| 1 | Si picking validado existe | **Abrir el validado** (no crear nuevo) |
| 2 | Ubicación del botón | **Header + Stat Button** (ambos) |
| 3 | Relación venta-picking | **Campo formal `sale_id`** en stock.picking |
| 4 | Entregas parciales | **Soportadas** (múltiples pickings por venta) |

## Dependencias

- `sale`
- `stock`
- `sale_stock`

## Instalación

1. Copiar la carpeta `doorandoor_sale_delivery_button` al directorio `addons/` de Odoo
2. Actualizar la lista de aplicaciones
3. Buscar "DoorAndDoor - Botón de Entrega desde Ventas"
4. Instalar

## Estructura del Módulo

```
doorandoor_sale_delivery_button/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── sale_order.py          # Lógica del botón y creación de pickings
│   └── stock_picking.py       # Campo sale_id y sincronización
├── views/
│   ├── sale_order_views.xml   # Herencias de vistas de ventas
│   └── stock_picking_views.xml # Herencias de vistas de pickings
├── security/
│   └── ir.model.access.csv
└── static/
    └── description/
```

## Autor

DoorAndDoor Team
