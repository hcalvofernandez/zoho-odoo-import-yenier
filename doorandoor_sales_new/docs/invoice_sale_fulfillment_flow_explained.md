# DoorAndDoor Sales New - Explicacion del flujo base factura -> venta -> fulfillment

## Objetivo de esta explicacion

Este documento explica de forma informativa como funciona la parte base del proyecto que conecta:

- factura
- venta
- fulfillment (cumplimiento)

La idea es que sirva como apoyo para presentaciones, capacitacion y estudio interno del modulo.

## Idea principal del flujo

El flujo base `factura -> venta -> fulfillment` es la columna vertebral del modulo.

La logica principal es que la factura de cliente deja de ser solo un documento contable y pasa a convertirse en el punto de arranque del seguimiento comercial y operativo.

Antes:

- la factura cumplia una funcion contable
- el seguimiento posterior dependia de otros pasos manuales

Ahora:

- la factura publicada genera un pedido de venta interno
- ese pedido queda ligado a la factura
- se crean lineas de seguimiento de cumplimiento
- desde ahi se puede continuar con liberacion por pago, despacho, fabricacion y entrega

## Que ocurre cuando se publica una factura

Cuando se publica una factura de cliente `out_invoice`, el modulo actua sobre ese momento.

En [account_move.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/account_move.py), el metodo `action_post()` llama a:

- `_ddsn_create_sale_orders_and_fulfillment()`

Esa funcion hace lo siguiente:

1. Verifica que el documento sea una factura de cliente.
2. Verifica que la factura este publicada.
3. Toma las lineas de producto validas de la factura.
4. Si aun no existe pedido generado, crea un `sale.order`.
5. Crea lineas de venta relacionadas con las lineas facturadas.
6. Crea lineas de `fulfillment` para llevar el seguimiento operativo.

## Como se forma el flujo

## Paso 1 - La factura es el origen

La factura es el documento maestro.

Desde ella nace el flujo posterior.

La factura conserva la referencia principal del proceso y sirve como punto de entrada para consultar:

- el pedido generado
- las lineas de cumplimiento
- los despachos
- las ordenes de fabricacion
- los registros de liberacion
- las ordenes de recogida

## Paso 2 - Se crea un pedido de venta interno

El sistema crea un `sale.order` asociado a la factura.

Ese pedido no nace desde el proceso comercial habitual de una cotizacion, sino como representacion comercial interna de lo que ya fue facturado.

El enlace queda guardado en la factura mediante el campo:

- `sale_order_id`

Esto permite que desde la propia factura se pueda abrir el pedido generado y usarlo como parte de la trazabilidad.

## Paso 3 - Se crean lineas de venta

Por cada linea de producto de la factura, el sistema crea una linea de venta en el `sale.order`.

La informacion base que se traslada incluye:

- producto
- descripcion
- cantidad
- unidad de medida
- precio unitario
- descuento
- impuestos

De esta forma, el pedido refleja comercialmente lo que la factura contiene.

## Paso 4 - Se crean lineas de fulfillment

Ademas del pedido de venta, el sistema crea registros en `doorandoor.fulfillment.line`.

Ese modelo esta definido en [fulfillment_line.py](/home/hanoi/Documentos/doorandoor/odoo/addons/doorandoor_sales_new/models/fulfillment_line.py).

Estas lineas son el verdadero centro del seguimiento operativo.

Cada `fulfillment_line` representa una linea facturada que luego necesita control sobre:

- cantidad facturada
- cantidad liberada por pago
- cantidad enviada a stock
- cantidad enviada a fabricacion
- cantidad entregada
- cantidad pendiente
- documentos relacionados
- estado operativo

## Como queda enlazada la informacion

La fortaleza del flujo esta en que todo queda conectado.

Una linea de factura puede quedar enlazada con:

- su linea de venta generada
- su linea de fulfillment

La factura queda enlazada con:

- su `sale.order`
- sus `fulfillment_line_ids`

Cada `fulfillment_line` queda enlazada con:

- la factura
- la linea de factura
- el pedido de venta
- la linea de venta
- el picking, si existe
- la orden de fabricacion, si existe

Eso permite una trazabilidad completa sin rehacer la informacion varias veces.

## Que significa esto funcionalmente

En la practica, este flujo resuelve un problema importante:

la informacion ya no se rompe entre contabilidad, ventas y operacion.

Ahora el sistema deja preparado un camino continuo:

- la factura origina el seguimiento
- la venta interna refleja lo vendido
- el fulfillment controla lo que falta por liberar, fabricar, despachar o entregar

## Como explicarlo de forma sencilla

Una forma simple de explicarlo es esta:

"Antes, la factura cerraba contabilidad. Ahora, ademas de eso, abre el seguimiento del negocio. Al publicarla, el sistema crea el pedido interno y las lineas de cumplimiento para que desde ese momento podamos controlar pago, despacho, fabricacion y entrega desde una misma trazabilidad."

## Por que `fulfillment` es tan importante

El pedido de venta ayuda a representar comercialmente la operacion.

Pero el `fulfillment` es el que realmente sirve para seguir la ejecucion.

Es como una capa de control interno por linea.

Gracias a esa capa, el sistema puede saber:

- cuanto de la linea ya fue autorizado por pago
- cuanto ya fue enviado a almacen
- cuanto fue mandado a fabricar
- cuanto ya se entrego
- que estado tiene esa linea dentro del proceso

## Beneficios del flujo base

### 1. Evita trabajo manual repetido

No hace falta volver a crear a mano un pedido interno despues de facturar.

### 2. Centraliza la trazabilidad

Desde la factura se puede seguir el resto del ciclo.

### 3. Prepara el sistema para automatizaciones posteriores

Sin esta base no seria posible sostener bien:

- liberacion por pago
- creacion automatica de picking
- creacion automatica de MRP
- ordenes de recogida

### 4. Reduce inconsistencias

Como la informacion nace conectada, se reducen errores entre documentos.

## Que pasa si hace falta resincronizar

El flujo fue pensado para soportar resincronizacion.

Existe una accion llamada:

- `Sync Fulfillment`

Esa accion vuelve a ejecutar la logica y ayuda a completar lo que falte sin duplicar lo que ya existe.

Esto es util, por ejemplo, para:

- facturas anteriores a una actualizacion
- casos donde se necesita reconstruir enlaces
- validaciones funcionales despues de cambios

## Relacion con el stock visible en factura

Una vez creada la base `factura -> venta -> fulfillment`, esa misma estructura se usa para mostrar mejor la disponibilidad comercial en las lineas de factura.

Eso significa que la columna de stock visible no debe interpretarse como simple existencia fisica bruta.

Ahora se usa tambien para descontar cantidades que ya quedaron comprometidas por pagos anteriores y siguen pendientes de entrega.

## Que significa esto para el usuario

Cuando una factura nueva se esta preparando, el usuario ve una cifra mas realista de lo que aun puede comprometer comercialmente.

En la practica:

- si hay stock fisico pero parte ya fue liberada por otra factura
- esa parte ya no debe verse como totalmente libre

De esa manera, la base de `fulfillment` no solo sirve para seguimiento interno, sino tambien para mejorar decisiones operativas y comerciales en pantalla.

## Que rol cumple cada pieza

### Factura

- documento maestro
- origen del proceso
- punto principal de consulta

### Sale Order

- representacion comercial interna
- reflejo de lo facturado
- apoyo a trazabilidad comercial

### Fulfillment Line

- control operativo por linea
- base para liberacion, despacho, fabricacion y entrega
- pieza central del seguimiento

## Como presentarlo en una reunion

Si necesitas explicarlo con lenguaje ejecutivo, puedes usar este guion:

"El cambio principal de esta parte del proyecto es que la factura pasa a ser el origen del flujo. Al publicarla, el sistema crea automaticamente un pedido de venta interno y lineas de fulfillment. El pedido refleja comercialmente lo facturado, mientras que el fulfillment permite controlar el avance operativo por cada producto. Con eso logramos trazabilidad desde factura hasta entrega."

## Como presentarlo en una capacitacion

Si necesitas explicarlo de forma mas didactica a usuarios:

1. Crear una factura de cliente.
2. Publicarla.
3. Mostrar que aparece un `sale.order` generado.
4. Mostrar la pestana o lista de `Fulfillment`.
5. Explicar que cada linea de fulfillment es una linea bajo seguimiento.
6. Explicar que desde ahi despues se controlan pago, despacho, fabricacion y entrega.

## Conclusión

El flujo base `factura -> venta -> fulfillment` no es un detalle tecnico aislado.

Es la base que hace posible el resto del proyecto.

Gracias a este flujo:

- la factura ya no termina el proceso
- la venta interna nace automaticamente
- el cumplimiento queda trazado por linea
- el sistema queda listo para coordinar mejor ventas, administracion, almacen y produccion
