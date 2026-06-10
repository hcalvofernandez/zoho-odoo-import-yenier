# DoorAndDoor Sales New - Tablero de Tareas

## Pendiente

- Definir e implementar bonificaciones por cliente y por grupo.
- Ajustar impresion de impuestos y partidas segun notas del cliente.
- Revisar reglas de despacho por almacen y por pago.
- Agregar foto en ficha de cliente.
- Diseñar proyeccion de produccion.

## En analisis

- Regla exacta de bonificacion por grupos.
- Definicion de linea o sistema de produccion en producto.

## En desarrollo

- Stock visible en cotizacion.
- Regla base de disponibilidad para equipo comercial.

## En pruebas

- Flujo completo factura -> pago -> produccion -> despacho -> entrega.
- Reportes impresos con firmas y orden de despacho en factura.
- agragar las funciones necesarias para las fotos de los clientes en este proceso.

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
- listo arquitectura para futura vista por almacen.
