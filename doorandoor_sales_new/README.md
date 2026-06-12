# DoorAndDoor Sales New

## Objetivo

Este modulo centraliza el nuevo flujo comercial y operativo de DoorAndDoor con la factura como documento maestro.

La meta es soportar un proceso donde:

- la factura origina el pedido comercial interno
- el pago libera cantidades de productos
- la liberacion crea operaciones de inventario o fabricacion
- el usuario pueda seguir todo el flujo desde la factura

## Alcance funcional esperado

El modulo esta pensado para cubrir estas etapas:

1. Factura publicada
   - crear pedido de venta en borrador
   - vincular lineas de factura con lineas de venta
   - crear lineas internas de cumplimiento

2. Pago aplicado
   - calcular liberacion segun politica configurada
   - decidir ruta: stock o fabricacion
   - crear pickings o producciones por la parte cubierta

3. Logistica
   - seguimiento de entregas
   - trazabilidad por factura, pedido, picking y produccion
   - futura integracion con etiquetas Zebra y QR

4. Soporte comercial
   - stock visible en cotizacion
   - bonificaciones por cliente y por grupo
   - soporte visual en ficha de cliente

5. Soporte operativo
   - ordenes de recogida en almacen
   - impresion para cliente desde facturacion
   - seguimiento posterior desde ventas e inventario

## Relacion con otros modulos

Actualmente este modulo depende de `doorandoor_delivery_status`.

La intencion por ahora no es reemplazarlo de inmediato, sino reutilizar sus utilidades visuales para movimientos y operaciones de stock mientras `doorandoor_sales_new` asume la logica principal del nuevo flujo.

## Estructura principal

- `models/account_move.py`
  Extiende factura y concentra el flujo inicial.

- `models/account_move_line.py`
  Agrega enlaces tecnicos hacia lineas de venta y cumplimiento.

- `models/fulfillment_line.py`
  Modelo central para rastrear cantidades facturadas, liberadas, entregadas y pendientes.

- `models/pickup_order.py`
  Controla las ordenes de recogida, sus estados y sus lineas operativas.

- `models/res_config_settings.py`
  Parametros funcionales seleccionables del flujo.

- `models/res_partner.py`
  Reglas comerciales simples por cliente y soporte visual sobre ficha.

- `views/account_move_views.xml`
  Agrega smart buttons, configuracion y pestaña de cumplimiento en factura.

- `views/pickup_order_views.xml`
  Agrega vistas de lista y formulario para ordenes de recogida.

- `views/pickup_order_report.xml`
  Define el reporte imprimible de orden de recogida.

## Estado funcional actual

Al cierre actual del proyecto, el modulo ya cubre:

- factura publicada genera `sale.order` y lineas de cumplimiento
- pago libera cantidades segun politica
- liberacion dispara documentos de stock o fabricacion
- produccion terminada puede completar despacho de salida
- validacion de picking actualiza entrega
- cotizacion muestra stock disponible y detalle por almacen
- cotizacion aplica bonificacion por cliente o grupo con prioridad base
- factura impresa oculta impuestos por item y concentra `Total de impuestos`
- ficha de cliente permite trabajar foto y reglas comerciales
- ordenes de recogida pueden emitirse desde factura y quedar trazadas en listas

## Regla operativa actual para recogida

Una linea entra en orden de recogida si:

- tiene producto
- tiene picking asociado
- el picking no esta cancelado
- existe cantidad liberada no entregada

Una orden de recogida queda:

- `ready` si el picking esta en `assigned` o `done`
- `pending` si la linea es autorizable pero el picking aun no esta listo operativamente
- `delivered` cuando almacen la marca como entregada

## Puntos de uso recomendados

### Desde facturacion

- publicar factura
- aplicar flujo de liberacion
- revisar fulfillment y despacho
- crear `Pickup Order`
- imprimir la orden para el cliente

### Desde ventas

- consultar lista de ordenes de recogida
- revisar estados `new`, `pending`, `ready`
- reimprimir el documento si hace falta

### Desde inventario

- consultar ordenes de recogida entregadas
- localizar historico operativo por cliente, factura o almacen
- confirmar ordenes ya completadas

## Pruebas y validacion

El modulo cuenta con pruebas automaticas para validar:

- creacion de `sale.order` desde factura
- creacion y no duplicacion de lineas de cumplimiento
- liberacion por pago prorrateada y secuencial
- creacion de picking por stock
- creacion de orden de fabricacion
- enlace produccion -> despacho
- stock visible en cotizacion
- bonificacion por cliente y por grupo
- creacion de orden de recogida
- cambio de estado a entregada en orden de recogida

Base usada para verificacion reciente:

- `pruebas`

Resultado reciente validado:

- suite en verde sin errores en la ultima actualizacion operativa del modulo

## Historial de desarrollo

### 18.0.1.0.0

- Se crea el modulo base `doorandoor_sales_new`.
- Se define la estructura inicial de modelos, vistas, menu y configuracion.
- Se establece `doorandoor_delivery_status` como dependencia funcional temporal.

### 18.0.1.0.1

- Se implementa la Fase 1 del flujo.
- Al publicar una factura de cliente se crea un `sale.order` en borrador.
- Se crean lineas de venta desde las lineas facturadas con producto.
- Se enlazan lineas de factura con lineas de venta generadas.
- Se crean registros `doorandoor.fulfillment.line` para seguimiento interno.
- Se agrega archivo de traduccion `es_419.po` para interfaz en español latino.
- Se corrige el autor oficial del modulo a `Hanoi Calvo Fernández (doorandoor)`.

### 18.0.1.0.2

- Se endurece la Fase 1 para que solo actue sobre facturas de cliente (`out_invoice`).
- Se agrega paquete de pruebas automaticas para validar:
  - creacion del pedido de venta al publicar factura
  - creacion de lineas de cumplimiento
  - no duplicacion de registros al resincronizar

### 18.0.1.0.3

- Se implementa la base de la Fase 2 para liberacion por pago.
- Se agrega resincronizacion automatica cuando existe conciliacion contable parcial.
- Se calculan cantidades e importes liberados en `doorandoor.fulfillment.line`.
- Se actualiza el estado general de liberacion en la factura.
- Se agrega modelo de bitacora `doorandoor.payment.release.log`.
- Se incorporan vistas y menu para revisar historico de liberaciones.

### 18.0.1.0.4

- Se corrige el orden de carga de vistas y acciones en el `manifest`.
- Se resuelve el error de actualizacion donde la vista de factura referenciaba una accion aun no cargada.

### 18.0.1.0.5

- Se agrega accion manual `Sync Fulfillment` en factura.
- Permite generar o resincronizar pedido de venta y lineas de cumplimiento en facturas historicas previas al modulo.

### 18.0.1.0.6

- Se corrige el filtro de lineas facturables para compatibilidad con Odoo 18.
- En esta base las lineas de producto usan `display_type = 'product'`, por lo que ahora tambien se consideran validas para crear `sale.order` y `fulfillment_line`.

### 18.0.1.0.7

- Se corrige el problema de seguridad al crear `doorandoor.payment.release.log`.
- La bitacora automatica de liberacion ahora se crea con privilegios de sistema para no bloquear el flujo del usuario final.

### 18.0.1.0.8

- Se simplifica la visualizacion de cumplimiento en factura y en el listado interno.
- Se eliminan de la interfaz las columnas `Qty ...` para enfocar la vista en producto, importes, documentos relacionados y estado.

### 18.0.1.0.9

- Se implementa la primera automatizacion de despacho desde la liberacion por pago.
- Las lineas en ruta de stock ahora generan `stock.picking` y movimientos de salida segun la cantidad liberada.
- Se agrega smart button para consultar los despachos vinculados a la factura.
- Se deja preparada la diferenciacion de estado entre ruta stock y ruta fabricacion para la siguiente fase.

### 18.0.1.0.10

- Se corrige un error de compatibilidad al crear pickings desde la factura.
- El contexto de `account.move` estaba inyectando `default_move_type = out_invoice` sobre `stock.picking`, provocando el fallo al sincronizar cumplimientos.
- Ahora la creacion del picking limpia ese contexto y fija `move_type = direct`, que es el valor valido para operaciones de salida.

### 18.0.1.0.11

- Se implementa el lanzamiento base de ordenes de fabricacion desde lineas liberadas en ruta MRP.
- Las lineas `ready_mrp` ahora crean y confirman `mrp.production`, quedando enlazadas a la factura.
- Se agrega smart button para consultar las ordenes de fabricacion relacionadas.
- Se incorpora prueba automatica para validar la creacion de la orden de fabricacion al liberar el pago.

### 18.0.1.0.12

- Se agregan pies de firma en los documentos impresos mas importantes del flujo.
- Facturas, pedidos de venta y ordenes de entrega ahora incluyen bloques para firma del responsable y del cliente o receptor.
- Los nombres del responsable se completan automaticamente desde el documento cuando existe usuario relacionado.

### 18.0.1.0.13

- Se agrega en la factura la referencia visible a la orden de despacho encima del bloque de firmas.
- Cuando la factura tiene pickings vinculados, el reporte impreso muestra sus numeros para facilitar la firma y trazabilidad en papel.

### 18.0.1.0.14

- Se completa el enlace produccion terminada hacia despacho de salida.
- Al marcar una `mrp.production` como terminada, el modulo genera el picking de salida pendiente para la factura relacionada.
- Al validar el picking, las lineas de cumplimiento actualizan cantidades entregadas, pendientes y estado final.
- Se agregan extensiones tecnicas sobre `mrp.production` y `stock.picking` para cerrar el ciclo completo factura -> fabricacion -> entrega.

### 18.0.1.0.15

- Se amplía la descripcion funcional del `manifest` para reflejar el objetivo, alcance, estructura e historial resumido del modulo dentro de Odoo.

### 18.0.1.0.16

- Se mueve la configuracion visual de cumplimiento desde el cuerpo principal de la factura hacia una pestaña propia dentro del notebook.
- La vista de factura queda mas limpia y la configuracion del flujo permanece accesible en una seccion dedicada.

### 18.0.1.0.17

- Se agrega un backlog documental del proyecto en `docs/project_backlog.md`.
- El archivo organiza estado actual, tareas pendientes, puntos por definir y orden recomendado de trabajo para continuar el desarrollo.

### 18.0.1.0.18

- Se agregan archivos de gestion colaborativa en `docs/`:
  - `task_board.md`
  - `meeting_notes.md`
  - `change_requests.md`
- La idea es usar estos documentos como tablero vivo de tareas, reuniones y solicitudes de cambio dentro del mismo proyecto.

### 18.0.1.0.19

- Se agrega `docs/current_sprint.md` para controlar la fase activa del proyecto.
- Se actualizan tablero, backlog y solicitudes de cambio para reflejar el inicio de la Fase A enfocada en stock visible en cotizacion.

### 18.0.1.0.20

- Inicia la implementacion tecnica de la Fase A.
- Se agrega visualizacion de stock disponible en lineas de cotizacion.
- La primera version usa el almacen del pedido cuando existe y, en su defecto, el contexto general de la compañia activa.

### 18.0.1.0.21

- Se agrega una columna visual por almacenes en la cotizacion con estilo de semaforo.
- Verde indica existencia disponible.
- Rojo indica producto sin existencia.
- Naranja indica que no hay existencia disponible pero el producto puede fabricarse por tener BoM.

### 18.0.1.0.22

- Se compacta la visualizacion por almacenes en cotizacion usando la abreviatura del almacen (`code`) cuando existe.
- La columna queda mas limpia y legible para el equipo comercial.

### 18.0.1.0.23

- Se corrige un error de indentacion en `models/sale_order_line.py` que impedía cargar el modulo y provocaba la caida de la instancia.

### 18.0.1.0.24

- Inicia la base de bonificaciones por cliente.
- Se agrega porcentaje general de bonificacion en la ficha del cliente.
- La cotizacion aplica automaticamente esa bonificacion al agregar productos cuando la linea no trae descuento previo.

### 18.0.1.0.25

- Se agregan pruebas automaticas para validar stock visible en cotizacion y bonificacion automatica por cliente.
- Se adapta el suite de pruebas a esta base de Odoo 18 para mantener la validacion operativa del modulo.

### 18.0.1.0.26

- Se completa la Fase B con bonificacion por grupo de cliente en `res.partner.category`.
- La cotizacion ahora aplica prioridad simple: descuento manual, luego bonificacion del cliente y despues bonificacion del grupo.
- Se agrega trazabilidad del origen de la bonificacion en la linea comercial.
- Se corrige la vista de grupos de cliente para compatibilidad con esta base de Odoo 18.
- La actualizacion del modulo y el suite automatico quedan validados en la base `pruebas`.

### 18.0.1.0.27

- Inicia la Fase C con un ajuste directo sobre la impresion de facturas.
- Se oculta la columna de impuestos por item en el reporte de factura.
- El resumen inferior muestra solo el acumulado fiscal con la etiqueta `Total de impuestos`.
- La actualizacion del modulo queda validada en la base `pruebas`.

### 18.0.1.0.28

- Se agrega la base operativa de ordenes de recogida en almacen.
- Las ordenes se generan desde factura, se listan por estado y pueden marcarse como entregadas.
- La lista queda visible desde ventas e inventario.
- Se agrega reporte imprimible de orden de recogida y pruebas automaticas del flujo.

### 18.0.1.0.29

- Se completa el soporte visual en la ficha del cliente usando `image_1920`.
- La foto del cliente queda visible y editable directamente en el formulario de `res.partner`.
- La actualizacion del modulo queda validada en la base `pruebas`.

## Observaciones

- El `README` describe el estado funcional real del modulo, aunque algunos tableros de `docs/` pueden representar el siguiente frente de trabajo en lugar del ultimo cierre tecnico.
- Cuando se agregan modelos Python nuevos en Odoo, puede ser necesario reiniciar el contenedor web ademas de actualizar el modulo para que el registro cargue completamente.

## Autor

Hanoi Calvo Fernández (doorandoor)
