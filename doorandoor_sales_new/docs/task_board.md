# DoorAndDoor Sales New - Tablero de Tareas

## Pendiente

- Revisar reglas de despacho por almacen.
- Diseñar proyeccion de produccion.

## En analisis

- Reglas avanzadas de bonificacion por categoria de producto.
- Regla exacta para ocultar partidas solo en impresion.
- Definicion de linea o sistema de produccion en producto.

## En desarrollo

- Ajustes adicionales que salgan de la prueba real con el cliente.
- Validacion visual de stock por almacen en lineas de factura.

## En pruebas

- Flujo completo factura -> pago -> produccion -> despacho -> entrega.
- Regla de despacho solo con factura totalmente pagada.
- Regla de fabricacion permitida con pago parcial.
- Reportes impresos con firmas y orden de despacho en factura.
- Validacion operativa de stock visible y lectura por almacenes en cotizacion.
- Validacion operativa de stock visible y lectura por almacenes en facturacion.

## Listo

- Creacion de `sale.order` desde factura.
- Creacion de lineas de cumplimiento.
- Liberacion por pago.
- Despacho automatico por stock.
- Orden de fabricacion automatica.
- Produccion terminada genera despacho de salida.
- Validacion de picking actualiza entrega.
- Pestaña de configuracion de cumplimiento en factura.
- Documentacion funcional del modulo en `manifest`.
- Backlog del proyecto en `docs/project_backlog.md`.
- Estructura documental de trabajo en `docs/`.
- Stock visible en cotizacion.
- Regla base de disponibilidad para equipo comercial.
- Arquitectura lista para futura vista por almacen.
- Regla separada de fabricacion parcial y despacho con pago total.
- Bonificacion automatica por cliente en cotizacion.
- Base de bonificacion por grupo de cliente.
- Prioridad base de bonificacion contra descuento manual.
- Validacion automatica de Fase B en entorno Odoo.
- Factura impresa sin columna de impuestos por item y con total fiscal agrupado.
- Foto visible y editable en ficha del cliente.
- Orden de recogida en almacen desde factura.
- Lista operativa con estados para recogida.
- Visibilidad de la lista desde inventarios.
- Reporte imprimible y reimprimible de orden de recogida.
- Regla base de linea lista para recoger.
