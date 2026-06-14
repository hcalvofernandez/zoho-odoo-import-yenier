# DoorAndDoor Sales New - Explicacion del flujo de orden de recogida

## Objetivo de esta explicacion

Este documento explica el bloque funcional de:

- orden de recogida
- seguimiento por estados
- visibilidad desde ventas e inventario
- entrega al cliente desde almacen

La idea es entender como esta parte del proyecto convierte una necesidad operativa de entrega en un flujo controlado dentro de Odoo.

## Idea principal del bloque

La orden de recogida nace para resolver una necesidad concreta:

hay casos donde el cliente no recibe el producto en una entrega tradicional inmediata, sino que debe recogerlo despues en almacen.

En ese escenario, hacia falta un documento operativo propio que permitiera:

- emitir una orden para el cliente
- saber que productos estan autorizados para recoger
- revisar si ya estan listos
- consultar la lista despues desde ventas
- confirmar la entrega desde almacen

## Que problema resuelve

Antes de esta funcionalidad, el flujo podia tener:

- factura
- pago
- picking

Pero faltaba una capa operativa intermedia para las recogidas.

Eso generaba vacios como:

- no tener un documento claro para el cliente
- no tener una lista separada de recogidas
- no tener un estado visible de si estaba pendiente o lista
- no tener una confirmacion operativa simple de entrega en almacen

La orden de recogida viene a cubrir exactamente ese espacio.

## Donde vive esta logica

La parte principal esta implementada en:

- [pickup_order.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/pickup_order.py)
- [account_move.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/account_move.py)
- [pickup_order_views.xml](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/views/pickup_order_views.xml)
- [pickup_order_report.xml](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/views/pickup_order_report.xml)
- [test_pickup_order.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/tests/test_pickup_order.py)

## Vision general del flujo

La cadena funcional puede entenderse asi:

1. Ya existe una factura con su seguimiento de `fulfillment`.
2. Ya existen lineas liberadas y relacionadas con un picking.
3. Desde la factura se crea la orden de recogida.
4. El sistema toma solo las lineas aptas para recogida.
5. Se genera una orden con sus lineas operativas.
6. La orden queda con estado segun la situacion del picking.
7. Ventas e inventario pueden consultarla en listas.
8. Almacen puede marcarla como entregada.
9. La orden puede imprimirse o reimprimirse para el cliente.

## Paso 1 - La orden nace desde la factura

La factura tiene una accion llamada:

- `Create Pickup Order`

Esa accion ejecuta en [account_move.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/account_move.py):

- `action_create_pickup_orders()`

Y esa accion llama a:

- `_ddsn_ensure_pickup_orders()`

## Que significa esto funcionalmente

La orden de recogida no se crea como un documento aislado o manual sin contexto.

Nace desde una factura que ya forma parte del flujo principal del modulo.

Eso garantiza trazabilidad desde el origen.

## Paso 2 - El sistema decide que lineas pueden entrar

No toda linea facturada entra automaticamente en una orden de recogida.

El sistema primero filtra las candidatas mediante:

- `_ddsn_get_pickup_candidate_lines()`

## Regla base actual

Una linea puede entrar en orden de recogida si:

- tiene producto
- tiene `picking_id`
- el picking no esta cancelado
- tiene cantidad liberada no entregada

En la practica esto significa:

- no basta con que la factura exista
- no basta con que la linea este facturada
- tiene que haber sustento operativo real para la recogida

## Como entender la cantidad autorizada

La logica usa la cantidad lista para recogida desde `fulfillment`:

- cantidad liberada
- menos cantidad ya entregada

Eso evita que se impriman o generen recogidas sobre cantidades ya cerradas.

## Paso 3 - Las lineas se agrupan por picking y almacen

Dentro de `_ddsn_ensure_pickup_orders()`, el sistema agrupa las lineas candidatas segun:

- `picking`
- `warehouse`

## Que significa esto operativamente

Si varias lineas pertenecen a una misma operacion de salida, pueden formar parte de una misma orden de recogida.

Esto ayuda a que el documento tenga sentido operativo para almacen y para el cliente.

## Paso 4 - Se crea la orden de recogida

El modelo principal es:

- `doorandoor.pickup.order`

Ese modelo guarda datos como:

- numero de orden
- factura
- cliente
- pedido de venta
- picking
- almacen
- estado
- notas
- usuario que entrego
- fecha de entrega

Las lineas operativas se guardan en:

- `doorandoor.pickup.order.line`

## Que lleva cada linea de recogida

Cada linea puede reflejar:

- producto
- linea de fulfillment relacionada
- cantidad autorizada
- cantidad entregada
- importe relacionado

## Que significa esto funcionalmente

La orden de recogida no es solo una referencia.

Es un documento con detalle real de que puede retirar el cliente.

## Paso 5 - La orden toma un estado operativo

La orden maneja estos estados:

- `new`
- `pending`
- `ready`
- `delivered`
- `cancelled`

## Como se determina el estado base

Cuando el sistema prepara la orden, usa el estado del picking relacionado.

La regla base actual es:

- `ready` si el picking esta en `assigned` o `done`
- `pending` si existe linea autorizable pero la operacion aun no esta lista

Ademas:

- `cancelled` si el picking fue cancelado
- `delivered` cuando almacen confirma la entrega

## Como explicarlo de forma simple

La orden de recogida no responde solo a que el cliente tenga una factura.

Responde a si la operacion realmente esta en condicion de ser retirada.

O sea:

- factura sola no basta
- autorizacion sola no basta
- tiene que haber base operativa para la recogida

## Paso 6 - El sistema evita duplicaciones innecesarias

Si ya existe una orden activa para el mismo picking, el sistema no crea otra sin necesidad.

En lugar de duplicarla:

- reutiliza la existente
- agrega solo lineas faltantes si aparecen nuevas
- vuelve a sincronizar el estado desde la operacion

## Que valor aporta esto

Evita ruido operativo y mantiene una sola orden coherente por operacion cuando corresponde.

## Paso 7 - La orden puede imprimirse

Cada orden tiene una accion para imprimir:

- `Print Pickup Order`

El reporte esta definido en [pickup_order_report.xml](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/views/pickup_order_report.xml).

## Que muestra el documento

El reporte incluye:

- numero de orden
- factura
- cliente
- almacen
- picking
- estado
- lineas con producto, cantidad autorizada e importe
- notas
- total
- bloque de firma de emitido por y recibido por

## Que significa esto funcionalmente

La operacion ya no depende solo de una vista en pantalla.

Existe tambien un documento formal que puede entregarse o reimprimirse cuando haga falta.

## Paso 8 - La orden queda visible en listas operativas

El modulo agrega vistas de lista, formulario y busqueda para `Pickup Orders`.

Desde ahi se puede:

- buscar por numero
- buscar por cliente
- revisar por almacen
- agrupar por estado
- agrupar por cliente
- agrupar por almacen

## Separacion por area

La misma funcionalidad sirve para dos miradas:

### Ventas

Puede consultar:

- nuevas
- pendientes
- listas

### Inventario

Puede consultar especialmente:

- entregadas
- historico operativo

Esto ayuda a que cada area mire la misma informacion con enfoque distinto.

## Paso 9 - Almacen puede marcar la entrega

Cuando el cliente recoge efectivamente, almacen puede ejecutar:

- `Mark Delivered`

Esa accion hace que la orden:

- pase a `delivered`
- registre quien hizo la entrega
- registre la fecha
- actualice las cantidades entregadas en las lineas de la orden

## Que significa esto operativamente

Ya no queda la recogida en una confirmacion verbal o informal.

El sistema deja constancia del cierre operativo.

## Importante para explicar bien esta parte

La orden de recogida complementa el flujo logistico, pero no reemplaza al picking.

Se puede entender asi:

- el picking representa la operacion de inventario
- la pickup order representa el documento y control operativo de recogida del cliente

Ambos se relacionan, pero no cumplen exactamente la misma funcion.

## Relacion con el flujo general del proyecto

La orden de recogida aparece despues de que ya existen:

- factura
- `sale.order`
- `fulfillment`
- liberacion por pago
- picking

Por eso este bloque suele explicarse mejor como una capa operativa posterior.

La secuencia completa se puede contar asi:

1. La factura origina el seguimiento.
2. El pago libera cantidades.
3. El sistema genera la operacion de salida.
4. Si la entrega al cliente sera por recogida, se emite la pickup order.
5. Almacen la usa para confirmar la entrega.

## Beneficios de negocio

### 1. Formaliza la recogida

La entrega en almacen deja de ser algo informal.

### 2. Mejora coordinacion entre areas

Ventas, facturacion e inventario pueden consultar la misma orden.

### 3. Da trazabilidad al cliente y a la operacion

La orden queda ligada a factura, pedido y picking.

### 4. Facilita reimpresion y control posterior

Si hace falta volver a emitir el documento, ya existe dentro del flujo.

## Como presentarlo en una reunion

Una forma ejecutiva de explicarlo es esta:

"La orden de recogida se incorporo para cubrir los casos en que el cliente retira productos en almacen despues de la factura. El sistema genera un documento propio ligado a la factura y al picking, lo clasifica por estado operativo y permite que almacen confirme la entrega final. Con eso se gana control, trazabilidad y visibilidad entre areas."

## Como presentarlo en una demo

Se puede mostrar en este orden:

1. Abrir una factura con picking relacionado.
2. Ejecutar `Create Pickup Order`.
3. Mostrar la orden creada.
4. Explicar sus lineas y el estado.
5. Imprimir el documento.
6. Abrir la lista de `Pickup Orders`.
7. Filtrar por estado.
8. Marcar una orden como `Delivered`.
9. Mostrar fecha y usuario de entrega.

## Como presentarlo en una capacitacion

### Para ventas

- como localizar la orden desde factura
- como consultar estados
- como reimprimir el documento

### Para almacen

- como revisar si una orden esta `pending` o `ready`
- como abrir el detalle
- como marcarla como entregada

### Para administracion

- como entender la relacion entre factura, picking y pickup order
- como usar el documento como soporte de trazabilidad

## Que conviene aclarar con precision

Para explicarlo bien, conviene remarcar esto:

- la pickup order ya esta implementada y funcional
- la regla base de estados ya existe
- el flujo esta pensado para operar sobre lineas realmente autorizadas

Y tambien:

- es una capa operativa complementaria
- no sustituye el control logistico base de Odoo

## Conclusion

El bloque de orden de recogida completa una necesidad operativa importante del proyecto.

Gracias a esta funcionalidad:

- el cliente puede recibir un documento formal de recogida
- ventas puede dar seguimiento posterior
- inventario puede confirmar la entrega
- el sistema mantiene trazabilidad entre factura, operacion y entrega final

En resumen:

la pickup order convierte una necesidad practica de almacen en un flujo visible, controlado y reimprimible dentro de Odoo.
