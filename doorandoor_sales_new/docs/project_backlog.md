# DoorAndDoor Sales New - Backlog del Proyecto

## Objetivo

Este archivo concentra el estado funcional del modulo `doorandoor_sales_new`, el alcance ya implementado, las tareas pendientes y el orden recomendado para continuar las mejoras solicitadas por el cliente.

## Estado actual del modulo

Actualmente el modulo cubre este flujo base:

1. Factura publicada
   - crea `sale.order` en borrador
   - crea lineas de venta
   - crea lineas internas de cumplimiento

2. Pago aplicado
   - calcula liberacion segun politica
   - actualiza importes y estados en cumplimiento
   - crea bitacora de liberacion

3. Ruta stock
   - crea `stock.picking`
   - crea `stock.move`
   - enlaza el despacho a la factura

4. Ruta fabricacion
   - crea `mrp.production`
   - confirma la orden de fabricacion
   - al terminar produccion prepara el despacho de salida

5. Entrega final
   - al validar picking actualiza cantidades entregadas
   - recalcula estado de cumplimiento
   - mantiene trazabilidad entre factura, venta, produccion y entrega

6. Reportes
   - firmas en factura
   - firmas en pedido de venta
   - firmas en orden de entrega
   - numero de orden de despacho visible en factura impresa

## Cambios ya implementados

- Generacion de `sale.order` desde factura.
- Sincronizacion manual `Sync Fulfillment`.
- Politicas de liberacion por pago.
- Pestañas de cumplimiento y configuracion en factura.
- Automatizacion de despacho por stock.
- Automatizacion de orden de fabricacion.
- Enlace produccion terminada -> picking de salida.
- Actualizacion de entrega al validar picking.
- Mejoras visuales de la factura.
- Traducciones base al español latino.
- Historial de desarrollo versionado en `README.md`.

## Pendientes provenientes de reunion con cliente

### 1. Cotizacion con informacion de stock

Objetivo:
Mostrar existencias al momento de cotizar, no esperar a la facturacion.

Posibles tareas:
- mostrar disponibilidad por producto en `sale.order.line`
- mostrar disponibilidad por almacen
- decidir si se muestra:
  - stock total
  - stock por almacen principal
  - stock por almacen del pedido
  - proxima disponibilidad
- definir si la cotizacion solo informa o tambien bloquea

Prioridad:
Alta

### 2. Bonificaciones y descuentos por cliente

Objetivo:
Aplicar reglas comerciales diferenciadas segun cliente o grupo.

Posibles tareas:
- agregar bonificacion global en `res.partner`
- agregar grupo de bonificacion
- crear reglas por categoria o grupo comercial
- aplicar bonificacion automaticamente en cotizacion
- permitir prioridad entre:
  - bonificacion del cliente
  - bonificacion por grupo
  - ajuste manual

Prioridad:
Alta

### 3. Ajustes de impresion de documentos

Objetivo:
Completar y refinar la salida impresa para clientes y operaciones.

Posibles tareas:
- revisar texto del total de impuestos
- mostrar impuesto agrupado y total de impuesto en el cuadro de totales
- definir si algunas partidas se ocultan solo al imprimir
- extender el mismo criterio visual a otros reportes si hace falta

Prioridad:
Media

### 4. Reglas mas estrictas para despacho

Objetivo:
Controlar mejor cuando se puede liberar y despachar.

Posibles tareas:
- reforzar la regla de no despachar sin pago
- revisar comportamiento con pago parcial
- decidir politica si hay varios almacenes
- decidir si reserva primero del almacen principal o del que tenga stock

Prioridad:
Alta

### 5. Foto en ficha de cliente

Objetivo:
Agregar soporte visual en el formulario del cliente.

Posibles tareas:
- usar `image_1920` si el cliente no necesita un campo extra
- crear un bloque visual en la ficha
- decidir si se usara tambien en reportes o solo en pantalla

Prioridad:
Media

### 6. Produccion avanzada

Objetivo:
Ampliar la parte industrial mas alla de la orden basica.

Posibles tareas:
- vincular producto con linea o sistema de produccion
- mostrar proyeccion de produccion
- generar vista o resumen de demanda proyectada
- definir si la proyeccion sale desde factura, venta o tablero propio

Prioridad:
Media

## Pendientes de definicion

Estos puntos necesitan decision funcional antes de implementarse:

- que significa exactamente "ocultar una partida" en factura
- como se define el grupo de bonificacion
- que regla exacta debe usarse para stock por almacen
- que significa "ver solo lo que tenga fecha mas proxima" en entregas
- a que se refiere exactamente "linea de produccion" en producto:
  - BoM
  - centro de trabajo
  - ruta
  - linea interna del negocio

## Orden recomendado de trabajo

### Fase A

- cotizacion con stock visible
- comprobacion de stock en tiempo de cotizar

### Fase B

- bonificaciones por cliente y por grupo
- aplicacion automatica en cotizacion

### Fase C

- ajustes de impresion de impuestos y partidas
- afinacion de documentos impresos

### Fase D

- proyeccion de produccion
- vinculo producto -> linea o sistema de produccion

## Riesgos y consideraciones

- algunas mejoras tocan vistas estandar de venta, factura y stock al mismo tiempo
- las reglas de descuentos y stock deben quedar bien definidas para no generar conflictos con el flujo ya automatizado
- si el cliente cambia politicas por almacen o por tipo de producto, convendra mover ciertas reglas a configuraciones seleccionables

## Siguiente paso recomendado

Iniciar por `cotizacion con stock visible`, porque es lo mas directo de la reunion y genera impacto inmediato en el trabajo del equipo comercial.

## Ejecucion actual

La fase activa del proyecto pasa a ser:

- Fase A
  - stock visible en cotizacion
  - regla base de disponibilidad
  - preparacion de evolucion futura por almacen
