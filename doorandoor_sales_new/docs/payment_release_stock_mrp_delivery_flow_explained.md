# DoorAndDoor Sales New - Explicacion del flujo liberacion por pago -> stock o fabricacion -> entrega

## Objetivo de esta explicacion

Este documento explica el segundo gran bloque funcional del proyecto:

- pago
- liberacion
- despacho por stock o fabricacion
- entrega

La idea es entender como el sistema pasa del seguimiento base creado desde la factura a la ejecucion operativa real.

## Idea principal del bloque

Si el primer bloque del proyecto crea la trazabilidad base:

- `factura -> venta -> fulfillment`

este segundo bloque convierte esa trazabilidad en accion operativa.

La logica general es esta:

- el cliente paga
- el sistema calcula que parte de la factura queda liberada
- cada linea de `fulfillment` actualiza sus cantidades
- el sistema decide la ruta operativa
- puede crear despacho por stock
- puede crear orden de fabricacion
- al final, la entrega actualiza el estado real del cumplimiento

## Vision general del flujo

La cadena funcional puede explicarse asi:

1. La factura ya existe y ya genero su `sale.order` y sus lineas de `fulfillment`.
2. Se aplica un pago o conciliacion contable.
3. El modulo recalcula cuanto de la factura esta autorizado para avanzar.
4. Cada linea recibe una cantidad liberada.
5. Segun la ruta, esa cantidad puede:
   - salir por stock
   - ir a fabricacion
6. Si sale por stock, se genera `stock.picking`.
7. Si va a fabricacion, se genera `mrp.production`.
8. Cuando la operacion termina, el `fulfillment` actualiza cantidades entregadas y estado.

## Donde vive esta logica

La mayor parte de este flujo esta implementada en:

- [account_move.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/account_move.py)

Y se apoya en:

- [account_partial_reconcile.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/account_partial_reconcile.py)
- [mrp_production.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/mrp_production.py)
- [stock_picking.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/stock_picking.py)
- [fulfillment_line.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/fulfillment_line.py)

## Paso 1 - El pago dispara la sincronizacion

Cuando se crea o elimina una conciliacion contable parcial, el modulo actua.

En [account_partial_reconcile.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/account_partial_reconcile.py):

- al crear una conciliacion, se llama a `_ddsn_sync_related_invoices()`
- al eliminarla, tambien se recalcula el estado relacionado

Eso hace que las facturas vinculadas vuelvan a ejecutar:

- `_ddsn_sync_release_from_payments()`

## Que significa esto funcionalmente

El sistema no espera a que un usuario vaya manualmente a actualizar el estado.

Cuando el pago impacta contablemente, el modulo usa esa señal para revisar cuanto puede liberarse operacionalmente.

## Paso 2 - Se calcula cuanto de la factura esta pagado

Dentro de `_ddsn_sync_release_from_payments()`, el sistema toma:

- el total de la factura
- el residual pendiente

Con eso calcula cuanto ya fue cubierto por pago.

La idea funcional es esta:

- si no hay pago, no se libera nada
- si hay pago parcial, se libera parcialmente
- si el pago cubre todo, se libera completamente

## Paso 3 - Se aplica una politica de liberacion

El modulo maneja politicas de liberacion.

Entre ellas aparecen:

- `prorated`
- `sequential_line`
- `priority`
- `manual`

## Como entenderlas de forma simple

### Prorrateada

Distribuye el pago proporcionalmente entre las lineas.

Ejemplo:

- si la factura esta pagada al 50 por ciento
- cada linea libera aproximadamente el 50 por ciento de su cantidad

### Secuencial por linea

Va liberando lineas en orden, una detras de otra, segun alcance el monto pagado.

### Prioridad

Existe como opcion funcional, aunque en la practica actual la logica base sigue una priorizacion simple por ordenamiento de lineas.

### Manual

Evita la liberacion automatica.

## Paso 4 - Cada linea de fulfillment actualiza sus cantidades

Cada `doorandoor.fulfillment.line` guarda cantidades clave del proceso.

Las mas importantes para esta etapa son:

- `qty_invoiced`
- `qty_released`
- `qty_pending_payment`
- `qty_pending_delivery`
- `amount_released`
- `state`

## Significado practico de estos campos

### `qty_invoiced`

Cuanto se facturo en esa linea.

### `qty_released`

Cuanto de esa linea ya esta autorizado a avanzar operativamente por efecto del pago.

### `qty_pending_payment`

Cuanto sigue bloqueado porque aun no esta cubierto por pago.

### `qty_pending_delivery`

Cuanto aun falta por entregar.

### `amount_released`

Valor monetario de lo ya liberado.

### `state`

Estado operativo de la linea.

Puede pasar por valores como:

- `pending_payment`
- `ready_stock`
- `ready_mrp`
- `in_process`
- `delivered`

## Paso 5 - El sistema decide la ruta operativa

Despues de calcular la cantidad liberada, el sistema decide que camino sigue la linea.

La decision se hace en `_ddsn_get_line_route()` dentro de [account_move.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/account_move.py).

Las rutas principales son:

- `ready_stock`
- `ready_mrp`

## Como explicarlo de forma sencilla

Cuando una linea ya esta liberada por pago, el sistema necesita responder:

"Esto sale del inventario o se manda a fabricar"

Si la respuesta es inventario:

- la linea pasa a `ready_stock`

Si la respuesta es fabricacion:

- la linea pasa a `ready_mrp`

## Importante para explicar bien el estado actual del proyecto

La base de esta decision ya existe.

Pero las reglas mas avanzadas de decision por stock real, faltantes parciales o estrategia por almacen todavia forman parte del siguiente nivel de refinamiento.

O sea:

- la estructura esta implementada
- la logica avanzada aun puede crecer

## Paso 6 - Si la ruta es stock, se crea un picking

Cuando una linea esta en `ready_stock` y hay cantidad liberada pendiente de enviar, el sistema ejecuta:

- `_ddsn_sync_stock_fulfillment_documents()`

Eso hace que:

- se obtenga o cree un `stock.picking`
- se creen `stock.move` para las cantidades liberadas
- la linea quede enlazada al picking
- `qty_sent_stock` aumente
- el estado pase a `in_process`

## Que significa esto operativamente

La linea deja de estar solo autorizada en teoria y pasa a tener un documento logistico real asociado.

Ya no es solo "puede salir".

Ahora es:

- "ya tiene salida preparada o creada en inventario"

## Paso 7 - Si la ruta es fabricacion, se crea una orden MRP

Cuando la linea queda en `ready_mrp`, el sistema ejecuta:

- `_ddsn_sync_mrp_fulfillment_documents()`

Eso hace que:

- calcule la cantidad a fabricar
- busque la BoM del producto
- cree `mrp.production`
- confirme la orden de fabricacion
- enlace esa produccion a la linea de fulfillment
- aumente `qty_sent_mrp`
- cambie el estado a `in_process`

## Que significa esto operativamente

La liberacion por pago no solo autoriza despacho directo.

Tambien puede autorizar arranque de fabricacion.

Eso es importante porque conecta lo financiero con la operacion industrial.

## Paso 8 - Cuando termina la fabricacion, se prepara la salida

En [mrp_production.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/mrp_production.py), al marcar una produccion como terminada, el modulo ejecuta:

- `_ddsn_sync_invoice_fulfillment_after_done()`

Eso busca las lineas de `fulfillment` relacionadas y llama a:

- `_ddsn_sync_finished_mrp_to_outgoing_picking()`

Con eso, el sistema puede crear el picking de salida pendiente para lo fabricado.

## Que significa esto funcionalmente

La fabricacion no queda aislada.

Cuando termina, alimenta el siguiente paso logistico.

O sea:

- fabricar no cierra el ciclo
- fabricar prepara la entrega

## Paso 9 - La validacion del picking actualiza la entrega

En [stock_picking.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/stock_picking.py), cuando se valida un picking:

- se detectan los pickings que pasaron a `done`
- se buscan las lineas de `fulfillment` relacionadas
- se actualizan cantidades entregadas
- se recalcula la cantidad pendiente
- se ajusta el estado

## En la practica, que cambia

Cuando el picking se valida:

- `qty_delivered` sube
- `qty_pending_delivery` baja
- si ya no queda pendiente, la linea pasa a `delivered`

Ademas, la factura recalcula su `release_state`.

## Que significa el `release_state` de la factura

La factura tiene un estado general resumido.

Puede pasar por:

- `not_ready`
- `partially_released`
- `released`
- `delivered`

## Como entenderlo de forma practica

### `not_ready`

Todavia no hay cantidades liberadas.

### `partially_released`

Algo ya fue liberado, pero aun queda parte pendiente de pago.

### `released`

Todo lo pagable ya fue liberado, pero aun falta entrega fisica.

### `delivered`

Ya no queda pendiente de entrega.

## Resumen corto del bloque

Una forma rapida de explicarlo en reunion es esta:

"Despues de crear el seguimiento base desde la factura, el sistema usa el pago como disparador operativo. Cuando entra dinero, calcula cuanto puede liberarse, actualiza las lineas de fulfillment y decide si esa parte va por stock o por fabricacion. A partir de ahi crea los documentos operativos y, cuando se valida la salida, actualiza la entrega real."

## Como presentarlo en una demo

Se puede mostrar en este orden:

1. Crear y publicar una factura.
2. Mostrar el `sale.order` generado y las lineas de `fulfillment`.
3. Aplicar o simular liberacion.
4. Mostrar cambio de cantidades liberadas.
5. Mostrar generacion de `Dispatches` o `Manufacturing`.
6. Si hay picking, mostrar la operacion de salida.
7. Validar el picking.
8. Mostrar como cambia el estado de `fulfillment` y de la factura.

## Que valor de negocio aporta este bloque

Este bloque aporta tres cosas muy importantes:

### 1. Conecta pago con operacion

La operacion no avanza solo por intuicion o coordinacion manual.

Avanza segun lo que financieramente ya esta autorizado.

### 2. Mejora trazabilidad

Cada paso queda enlazado a la factura original y a sus lineas de seguimiento.

### 3. Prepara automatizacion escalable

Con esta base se pueden endurecer despues:

- reglas por almacen
- reglas de stock parcial
- estrategias mixtas stock + fabricacion
- controles mas estrictos de despacho

## Que conviene explicar con cautela

Para presentar el proyecto con precision, conviene aclarar esto:

La base del flujo esta implementada y es funcional.

Sin embargo, algunos criterios mas avanzados aun estan en evolucion, especialmente:

- decision sofisticada por stock real disponible
- comportamiento por varios almacenes
- politicas parciales de stock llevadas a toda su capacidad

Eso no invalida lo que ya existe.

Mas bien indica que:

- el flujo ya funciona
- el siguiente paso es refinar sus reglas de negocio

## Conclusion

El bloque `liberacion por pago -> stock o fabricacion -> entrega` es el puente entre el control financiero y la ejecucion operativa.

Gracias a este flujo:

- el pago deja de ser solo un dato contable
- la liberacion se vuelve accionable
- el sistema puede disparar inventario o produccion
- la entrega actualiza el cumplimiento real

En resumen:

el proyecto no solo registra documentos, sino que empieza a orquestar el movimiento real del negocio dentro de Odoo.
