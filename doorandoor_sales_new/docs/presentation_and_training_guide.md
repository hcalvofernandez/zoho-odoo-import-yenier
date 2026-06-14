# DoorAndDoor Sales New - Guia de Presentacion y Capacitacion

## Objetivo del documento

Este documento sirve como guia para presentar el estado actual del proyecto `doorandoor_sales_new`, explicar las funcionalidades agregadas en las ultimas etapas y apoyar la capacitacion operativa de los usuarios del sistema.

Se puede usar en:

- presentaciones con cliente
- reuniones internas del equipo
- sesiones de capacitacion funcional
- cierre de etapas y definicion de siguientes pasos

## Mensaje principal del proyecto

El modulo `doorandoor_sales_new` transforma la factura en el documento maestro del flujo comercial y operativo.

A partir de la factura, el sistema puede:

- generar el pedido de venta interno
- crear lineas de seguimiento de cumplimiento
- liberar cantidades segun el pago recibido
- disparar operaciones de inventario o fabricacion
- dar trazabilidad hasta la entrega
- apoyar al equipo comercial con stock y bonificaciones
- apoyar al area operativa con ordenes de recogida

## Resumen ejecutivo para abrir la presentacion

En las ultimas etapas del proyecto se consolidaron mejoras sobre cuatro frentes:

- automatizacion del flujo comercial desde factura
- apoyo comercial en cotizacion
- mejoras visuales y documentales
- control operativo de recogida en almacen

El proyecto ya tiene una base funcional estable para ventas, facturacion, inventario y seguimiento de entregas.

El siguiente nivel de trabajo no es crear la base, sino endurecer reglas operativas mas avanzadas por pago, stock, almacen y produccion.

## Matriz de cierre recomendada

### Cerrar ahora

- Factura publicada crea `sale.order` y lineas de cumplimiento.
- Flujo base de seguimiento `factura -> venta -> fulfillment` disponible.
- Stock visible en cotizacion.
- Bonificacion por cliente en cotizacion.
- Bonificacion por grupo de cliente en cotizacion.
- Prioridad base entre descuento manual, bonificacion de cliente y bonificacion de grupo.
- Foto visible y editable en la ficha del cliente.
- Ajuste de impresion de factura sin impuestos por linea.
- Total fiscal agrupado como `Total de impuestos`.
- Firmas en reportes principales.
- Orden de recogida creada desde factura.
- Lista operativa de ordenes de recogida.
- Visibilidad de recogida desde ventas e inventario.
- Reporte imprimible y reimprimible de orden de recogida.
- Cambio manual a entregada por almacen.

### Cerrar con validacion funcional

- Liberacion por pago con casos reales de pago parcial.
- Creacion automatica de picking por stock.
- Creacion automatica de orden de fabricacion.
- Flujo produccion terminada -> picking de salida.
- Validacion de picking actualiza entrega y estado final.

### Continuar desarrollo

- Reglas mas estrictas de despacho segun pago.
- Reglas mas avanzadas por almacen.
- Decision real entre stock y fabricacion cuando no hay existencia completa.
- Uso efectivo de politicas parciales de stock.
- Bonificaciones por categoria de producto.
- Proyeccion o tablero de produccion.
- Ajustes adicionales de impresion segun decision del cliente.

## Agenda sugerida para la presentacion

### 1. Contexto del proyecto

Explicar brevemente que el objetivo del modulo es unificar el flujo comercial y operativo tomando la factura como origen del proceso.

Mensaje sugerido:

"El proyecto busca que una factura no sea solo un documento contable, sino el punto de partida para ventas internas, liberacion por pago, despacho, fabricacion y entrega final."

### 2. Problemas que el proyecto viene resolviendo

- evitar trabajo manual entre factura, venta y operacion
- mejorar trazabilidad entre areas
- ayudar al vendedor a cotizar con mejor informacion
- documentar mejor la salida operativa al cliente
- controlar recogidas posteriores a la facturacion

### 3. Nuevas funcionalidades agregadas

Presentar por bloques para que la audiencia entienda mejor el valor funcional.

## Bloque 1 - Flujo comercial y operativo base

### Que hace

- al publicar una factura se genera un `sale.order`
- se crean lineas internas de cumplimiento
- el sistema guarda trazabilidad entre factura y venta

### Beneficio

- se elimina recreacion manual de informacion
- se centraliza el seguimiento operativo

### Que mostrar en demo

- una factura de cliente
- el smart button del pedido generado
- la pestana o lista de `Fulfillment`

### Mensaje de cierre del bloque

"Con esta base, cada factura ya deja preparado el seguimiento comercial y operativo sin depender de pasos manuales separados."

## Bloque 2 - Liberacion por pago y ruta operativa

### Que hace

- el pago aplicado libera cantidades
- la liberacion puede generar despacho por stock
- la liberacion puede generar orden de fabricacion
- el sistema mantiene trazabilidad del proceso

### Beneficio

- el area operativa trabaja sobre cantidades autorizadas
- se conecta mejor el pago con la ejecucion real

### Que mostrar en demo

- factura con estado de liberacion
- smart button de `Releases`
- smart button de `Dispatches`
- smart button de `Manufacturing`

### Mensaje de cierre del bloque

"La liberacion por pago ya no queda solo en contabilidad; se convierte en un disparador operativo para despacho o fabricacion."

### Nota para presentar con cautela

Conviene explicar que la base ya existe, pero que las reglas mas finas por almacen y disponibilidad total o parcial siguen como siguiente etapa de refinamiento.

## Bloque 3 - Mejoras para el equipo comercial

### Stock visible en cotizacion

#### Que hace

- muestra disponibilidad del producto en la cotizacion
- muestra lectura por almacen

#### Beneficio

- el vendedor puede responder mejor antes de facturar
- reduce incertidumbre comercial

#### Que mostrar en demo

- cotizacion
- linea de producto
- columnas de stock y almacenes

### Bonificaciones por cliente y grupo

#### Que hace

- aplica bonificacion por cliente
- aplica bonificacion por grupo de cliente
- respeta prioridad base frente a descuento manual

#### Beneficio

- mejora consistencia comercial
- reduce errores de aplicacion manual

#### Que mostrar en demo

- ficha del cliente con bonificacion
- grupo de cliente con bonificacion
- cotizacion donde se aplique automaticamente

### Foto en ficha de cliente

#### Que hace

- permite ver y editar la foto del cliente en `res.partner`

#### Beneficio

- mejora identificacion visual y apoyo operativo

#### Que mostrar en demo

- ficha de cliente
- bloque de foto
- pestana de reglas comerciales

## Bloque 4 - Mejoras documentales e impresion

### Que hace

- la factura impresa oculta impuestos por linea
- el total fiscal aparece agrupado
- se agregan bloques de firma en documentos principales
- la factura puede mostrar referencias de despacho

### Beneficio

- los documentos se vuelven mas claros para cliente y operacion
- mejora la trazabilidad en papel

### Que mostrar en demo

- impresion de factura
- impresion de pedido
- impresion de entrega

### Mensaje de cierre del bloque

"No solo se automatizo el flujo; tambien se mejoro la forma en que ese flujo se comunica en documentos."

## Bloque 5 - Orden de recogida en almacen

### Que hace

- crea una orden de recogida propia ligada a la factura
- permite imprimirla para el cliente
- guarda la orden en una lista operativa
- maneja estados como `new`, `pending`, `ready`, `delivered`, `cancelled`
- permite marcar la entrega desde almacen
- queda visible desde ventas e inventario

### Beneficio

- formaliza la recogida posterior a la factura
- da control operativo y trazabilidad
- mejora la coordinacion entre ventas y almacen

### Regla base actual

Una linea entra en orden de recogida si:

- tiene producto
- tiene picking asociado
- el picking no esta cancelado
- existe cantidad liberada no entregada

La orden queda:

- `ready` si el picking esta en `assigned` o `done`
- `pending` si la linea es autorizable pero la operacion aun no esta lista
- `delivered` cuando almacen confirma la entrega

### Que mostrar en demo

- factura con accion `Create Pickup Order`
- lista de ordenes de recogida
- formulario de la orden
- impresion del reporte
- cambio manual a `Delivered`

### Mensaje de cierre del bloque

"Esta funcionalidad cierra la necesidad operativa de entregar al cliente un documento de recogida y seguir su estado hasta la entrega real."

## Guion sugerido de capacitacion

## Perfil 1 - Ventas

### Lo que debe aprender

- como la factura genera seguimiento interno
- como leer stock en cotizacion
- como funcionan las bonificaciones
- como consultar y reimprimir ordenes de recogida

### Flujo de entrenamiento

1. Crear una cotizacion.
2. Revisar stock visible por producto.
3. Confirmar aplicacion de bonificacion si corresponde.
4. Generar y revisar una factura.
5. Crear una orden de recogida desde la factura.
6. Consultarla despues desde ventas.

## Perfil 2 - Facturacion / administracion

### Lo que debe aprender

- publicar factura dentro del nuevo flujo
- interpretar el estado de liberacion
- usar `Sync Fulfillment` cuando haga falta
- imprimir documentos actualizados

### Flujo de entrenamiento

1. Crear factura de cliente.
2. Publicarla.
3. Revisar pedido generado y lineas de cumplimiento.
4. Revisar liberaciones y documentos operativos.
5. Crear e imprimir orden de recogida.

## Perfil 3 - Almacen / inventario

### Lo que debe aprender

- consultar ordenes de recogida
- distinguir estados operativos
- marcar orden como entregada
- revisar historico de entregas

### Flujo de entrenamiento

1. Abrir lista de `Pickup Orders`.
2. Filtrar por `Pending`, `Ready` y `Delivered`.
3. Abrir una orden.
4. Confirmar entrega.
5. Reimprimir documento si hace falta.

## Preguntas que pueden surgir en presentacion

### 1. Ya esta terminado todo el proyecto

Respuesta sugerida:

"La base funcional principal ya esta implementada y varias mejoras ya se pueden cerrar. Lo siguiente es una etapa de refinamiento de reglas operativas mas avanzadas."

### 2. Que partes ya estan listas para uso

Respuesta sugerida:

"Estan listas la trazabilidad desde factura, el apoyo comercial en cotizacion, las bonificaciones base, la mejora documental y la orden de recogida operativa."

### 3. Que partes necesitan definicion adicional

Respuesta sugerida:

"Principalmente las reglas finas de despacho por almacen, stock parcial, priorizacion entre stock y fabricacion, y la proyeccion de produccion."

## Recomendacion de mensaje final

Se recomienda cerrar la presentacion con tres ideas:

- ya existe una base funcional real y demostrable
- varias mejoras de alto valor para usuarios ya estan operativas
- el siguiente esfuerzo debe enfocarse en reglas avanzadas, no en reconstruir la base

Mensaje sugerido:

"En estas ultimas etapas el proyecto dejo de ser una idea de flujo y paso a convertirse en una operacion visible dentro de Odoo. Ya tenemos una base para trabajar ventas, facturacion, inventario y recogida de forma mas conectada. El siguiente paso natural es afinar reglas avanzadas para que el sistema responda aun mejor a la operacion real del cliente."

## Siguiente uso recomendado de este documento

Este archivo puede reutilizarse como:

- guion de demo funcional
- minuta de cierre de etapa
- base para diapositivas
- apoyo de onboarding para nuevos usuarios del modulo
