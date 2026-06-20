# DoorAndDoor Sales New - Notas de Reuniones

## Formato sugerido

### Fecha

Fecha -- 14 de junio 2026

- Participantes: todo personal de direccion 
- Tema: revision de los cambios hechos hasta ahora. y los flujos
- Acuerdos:
- Dudas:
- Acciones:

## Reunion base de analisis con cliente 14-06-26 

- Tema:
  Revision del flujo comercial, impresion, stock, bonificaciones y produccion.

- Puntos detectados:
  - Las factura para generar la orden de despacho deben estar pagadas completamente.
  - la Regla de facturación debe tener al menos el pago parcial para para poder generar la orden de fabricación.
  - mostrar stock al momento de cotizar. en las facturas . sacarlo de las ordenes de ventas y pasar esas columnas para factura..
  - pasar la pestaña de las firmas que estan en ordenes de ventas  para las facturas.
  - mover los semaforos de iventarios dispobibles de Sale Order a las Factura. o mantenerlos en los dos lugares. de ser posible.
  - revisar reglas de despacho segun pago y almacen
  - agregar foto en cliente
  - definir bonificaciones por cliente y grupo
  - ampliar visualizacion y proyeccion de produccion

- Resultado:
  Los puntos fueron pasados a backlog funcional en `docs/project_backlog.md`.

## Seguimiento interno posterior 15-06-26

- Tema:
  Cierre tecnico de los puntos ya resueltos y congelacion temporal de los puntos aun no definidos por el cliente.

- Acuerdos:
  - se da por cerrado el ajuste de despacho solo con factura totalmente pagada
  - se da por validado el flujo donde fabricacion puede generarse con pago parcial
  - se deja implementada la visualizacion de stock por almacen tambien en facturas
  - no se continuara desarrollando reglas adicionales por almacen ni refinamientos visuales no definidos hasta nueva confirmacion del cliente

- Dudas:
  - si el stock visible debe solo informar o tambien bloquear
  - cual es la regla exacta de seleccion de almacen
  - si los semaforos de stock deben mantenerse en venta, en factura o en ambos lugares
  - que refinamientos de impresion siguen siendo realmente necesarios

- Acciones:
  - mantener documentado como cerrado solo lo implementado y probado
  - congelar los puntos aun abiertos hasta nueva reunion con el cliente

## Ajuste tecnico interno 19-06-26

- Tema:
  Correccion de duplicidad potencial en historial de despacho entre flujo de venta y flujo de factura.

- Puntos detectados:
  - una misma salida podia reaparecer duplicada cuando ya existia un picking abierto de la venta y la factura intentaba crear otro
  - el riesgo mayor estaba en dejar dos movimientos para la misma `sale_line_id` en el historial operativo

- Acuerdos:
  - facturacion debe reutilizar el `stock.picking` abierto de la venta relacionada si corresponde a la misma operacion
  - no deben crearse `stock.move` paralelos para la misma linea de venta dentro del mismo picking

- Acciones:
  - dejar prueba automatizada para el caso de reutilizacion
  - validar el ajuste final directamente en contenedor Docker de Odoo

## Ajuste tecnico interno 19-06-26 - Nota 2

- Tema:
  Bloqueo de ajustes manuales de inventario cuando ya existen cantidades comprometidas por facturas pagadas o parcialmente pagadas.

- Problemas detectados:
  - un usuario podia intentar cuadrar stock a mano despues del cobro, dejando la existencia fisica por debajo de lo ya liberado para entrega
  - eso rompia la consistencia entre factura, pago, liberacion y stock real
  - el riesgo era mayor en facturas con pago parcial porque parte de la cantidad ya quedaba comprometida aunque aun no estuviera entregada

- Soluciones aplicadas:
  - se agrego una validacion sobre `stock.quant` para revisar ajustes manuales de inventario
  - el sistema calcula la cantidad liberada y pendiente de entrega desde `doorandoor.fulfillment.line`
  - si el ajuste intenta dejar el stock por debajo de esa cantidad comprometida, el sistema bloquea la operacion con error funcional
  - se dejaron pruebas automatizadas para el caso bloqueado y para el caso permitido
  - se identifico como antecedente conocido que algunos productos migrados desde Zoho venian como consumibles o servicios y por eso no podian usarse para inventario fisico en Odoo
  - se deja constancia de que ese punto ya fue contemplado al preparar la futura base de produccion

- Anexo de mejora visual:
  - la columna de stock visible en lineas de factura ya no muestra solo stock fisico bruto
  - ahora descuenta tambien las unidades ya comprometidas por pagos anteriores que siguen pendientes de entrega
  - con esto la cifra visible se acerca al stock realmente vendible y ayuda a evitar doble venta por lectura desactualizada
  - el ajuste fue validado con prueba automatizada en entorno Docker Odoo

- Acciones:
  - mantener este criterio como regla base mientras no exista una politica mas avanzada de conciliacion manual
  - conservar la validacion cubierta por pruebas en entorno Docker Odoo
