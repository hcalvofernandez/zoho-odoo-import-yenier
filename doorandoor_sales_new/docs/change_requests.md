# DoorAndDoor Sales New - Solicitudes de Cambio

## Formato sugerido

### CR-0001

- Fecha:
- Solicitado por:
- Descripcion:
- Impacto funcional:
- Impacto tecnico:
- Estado:

## CR-0001

- Fecha:
  2026-06-09

- Solicitado por:
  Cliente DoorAndDoor

- Descripcion:
  Mejorar y ampliar el flujo comercial y operativo despues de la fase base implementada.

- Impacto funcional:
  Abarca cotizacion, descuentos, impresion, stock, despacho y produccion.

- Impacto tecnico:
  Requiere nuevas extensiones sobre ventas, clientes, reportes y planeacion productiva.

- Estado:
  En analisis

## CR-0002

- Fecha:
  2026-06-09

- Solicitado por:
  Equipo del proyecto DoorAndDoor

- Descripcion:
  Iniciar la Fase A con stock visible en cotizacion para uso inmediato del equipo comercial.

- Impacto funcional:
  Mejora la toma de decision comercial antes de facturar.

- Impacto tecnico:
  Requiere extender vistas y logica de `sale.order.line` con informacion de disponibilidad.

- Estado:
  Implementado

## CR-0003

- Fecha:
  2026-06-10

- Solicitado por:
  Equipo del proyecto DoorAndDoor

- Descripcion:
  Iniciar la base de bonificaciones automaticas por cliente en cotizacion.

- Impacto funcional:
  Permite precargar descuentos comerciales simples desde la ficha del cliente.

- Impacto tecnico:
  Requiere extender `res.partner`, `sale.order.line` y la vista del cliente.

- Estado:
  Implementado

## CR-0004

- Fecha:
  2026-06-11

- Solicitado por:
  Equipo del proyecto DoorAndDoor

- Descripcion:
  Extender la bonificacion comercial para soportar grupos de cliente y definir prioridad frente al descuento manual.

- Impacto funcional:
  La cotizacion puede aplicar descuentos comerciales mas consistentes sin perder control manual del vendedor.

- Impacto tecnico:
  Requiere extender `res.partner.category`, `sale.order.line` y vistas de clientes/cotizacion.

- Estado:
  Implementado y validado en entorno
