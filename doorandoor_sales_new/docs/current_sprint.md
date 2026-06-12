# DoorAndDoor Sales New - Sprint Actual

## Objetivo del sprint

Iniciar la Fase E del backlog con foco en recogida operativa en almacen:

- crear ordenes de recogida desde facturacion
- registrar su seguimiento en lista con estados
- dar visibilidad a ventas e inventario

## Alcance inmediato

### Tarea 1

- Nombre:
  Modelo y flujo de orden de recogida

- Objetivo:
  Crear una entidad operativa propia para controlar recogidas posteriores a la factura.

- Resultado esperado:
  Ventas puede emitir una orden de recogida y localizarla despues.

- Estado:
  Pendiente

### Tarea 2

- Nombre:
  Lista operativa y estados

- Objetivo:
  Permitir seguimiento de la orden desde vistas de lista.

- Propuesta inicial:
  Estados propuestos: nueva, pendiente, lista, entregada, cancelada.

- Estado:
  Pendiente

### Tarea 3

- Nombre:
  Visibilidad y reportes por area

- Objetivo:
  Exponer las ordenes desde facturacion e inventario con enfoque distinto por estado.

- Estado:
  Pendiente

## Fuera de alcance de este sprint

- foto de cliente
- proyeccion de produccion
- reglas avanzadas de bonificacion por categoria de producto
- refinamientos adicionales de impresion que no afecten recogida

## Criterio de cierre

Este sprint se considera listo cuando:

- exista una orden de recogida propia ligada a factura
- la orden pueda imprimirse para el cliente
- la orden quede guardada en una lista con estados
- almacen pueda marcarla como entregada
- la lista sea visible desde ventas e inventario
- el cambio quede documentado y validado en el entorno Odoo

## Resultado actual

- Las fases A y B quedan cerradas y validadas.
- La Fase C ya tiene el ajuste inicial de impuestos en factura impresa.
- El siguiente frente activo pasa a ser recogida en almacen como flujo operativo independiente.
