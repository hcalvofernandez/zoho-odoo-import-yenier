# DoorAndDoor Sales New - Sprint Actual

## Objetivo del sprint

Iniciar la Fase B del backlog con foco en reglas comerciales:

- bonificaciones por cliente y por grupo
- aplicacion automatica en cotizacion
- prioridad clara entre regla comercial y descuento manual

## Alcance inmediato

### Tarea 1

- Nombre:
  Bonificacion por grupo de cliente

- Objetivo:
  Permitir una bonificacion comercial base definida en categorias de cliente.

- Resultado esperado:
  La cotizacion puede heredar una bonificacion desde el grupo comercial cuando el cliente no tenga una propia.

- Estado:
  Implementada

### Tarea 2

- Nombre:
  Prioridad de bonificacion automatica

- Objetivo:
  Aplicar una regla simple y predecible al cargar productos en cotizacion.

- Propuesta inicial:
  Prioridad: descuento manual > bonificacion del cliente > bonificacion del grupo.

- Estado:
  Implementada

### Tarea 3

- Nombre:
  Trazabilidad de origen de bonificacion

- Objetivo:
  Mostrar de donde sale la bonificacion aplicada en la linea comercial.

- Estado:
  Implementada

## Fuera de alcance de este sprint

- ajustes fiscales de impresion
- foto de cliente
- proyeccion de produccion
- reglas avanzadas por categoria de producto

## Criterio de cierre

Este sprint se considera listo cuando:

- la cotizacion aplique bonificacion automatica sin sobreescribir descuento manual
- exista bonificacion por cliente y por grupo
- la linea muestre el origen de la bonificacion aplicada
- el cambio quede documentado y validado en el entorno Odoo

## Resultado actual

- Ya existia la bonificacion por cliente en cotizacion.
- Se agrega bonificacion por grupo de cliente en `res.partner.category`.
- La prioridad queda asi: descuento manual, luego bonificacion del cliente, luego bonificacion del grupo.
- La linea comercial guarda el origen de la bonificacion aplicada.
- La validacion automatica queda pendiente de reactivar contenedores Docker despues del reinicio del entorno.
