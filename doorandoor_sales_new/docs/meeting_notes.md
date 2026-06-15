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
