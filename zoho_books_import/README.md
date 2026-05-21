# Zoho Books Import (Unidirectional)

## Objetivo

Este modulo importa informacion desde Zoho Books hacia Odoo.

El flujo es unidireccional:

- Zoho Books -> Odoo
- No exporta informacion desde Odoo hacia Zoho

Estado actual del desarrollo:

- Autenticacion OAuth2 funcional
- Deteccion automatica de `organization_id`
- Importacion de partners funcional
- Lectura de productos desde Zoho funcional
- Flujo de productos ajustado para distintas variantes del campo de tipo en `product.template`
- Mapeo corregido de tipos de producto Zoho a Odoo (goods, service, consumable)
- Campo `zoho_product_type` agregado para guardar el tipo original de Zoho
- Manejo mejorado de errores de API de Zoho con extraccion detallada de mensajes
- Logs tecnicos y funcionales disponibles en Odoo y en `config/odoo-server.log`

## Alcance actual

El modulo incluye soporte base para:

- Conectores Zoho Books
- Importacion manual por wizard
- Importacion de productos
- Importacion de stock por producto
- Importacion de clientes y proveedores
- Logs de importacion
- Tareas cron para sincronizacion

## Estructura funcional

Principales componentes del modulo:

- `models/zoho_connector.py`
  Gestiona autenticacion, tokens, URLs de API y pruebas de conexion.
- `models/zoho_product_import.py`
  Gestiona lectura y creacion/actualizacion de productos con mapeo inteligente de tipos.
- `models/product_template.py`
  Extiende `product.template` con campo `zoho_product_type` para guardar el tipo original de Zoho.
- `models/zoho_partner_import.py`
  Gestiona lectura y creacion/actualizacion de clientes y proveedores.
- `wizard/zoho_import_wizard.py`
  Orquesta la ejecucion manual de importaciones desde interfaz.
- `models/zoho_import_log.py`
  Guarda el resultado funcional de cada importacion.

## Configuracion del conector

### Datos requeridos

Cada conector necesita:

- Nombre
- `client_id`
- `client_secret`
- `redirect_url`
- `country_endpoint`
- `auth_code` durante el proceso inicial
- `access_token` y `refresh_token` despues de activar
- `organization_id`

### Flujo recomendado

1. Crear el conector en Odoo.
2. Seleccionar el datacenter correcto.
3. Generar la URL de autorizacion.
4. Autorizar en Zoho.
5. Recibir el `auth_code` en el callback.
6. Activar el conector.
7. Verificar que se detecte `organization_id`.
8. Ejecutar `Test Connection`.

## Operacion correcta de URLs

Este punto es critico. En las pruebas del desarrollo aparecieron errores por usar dominios o rutas incorrectas.

### URLs correctas

Para API de Zoho Books se debe usar:

- `https://www.zohoapis.com/books/v3/...` para `.com`
- `https://www.zohoapis.eu/books/v3/...` para `.eu`
- `https://www.zohoapis.in/books/v3/...` para `.in`
- `https://www.zohoapis.com.au/books/v3/...` para `.com.au`
- `https://www.zohoapis.com.cn/books/v3/...` para `.com.cn`
- `https://www.zohoapis.jp/books/v3/...` para `.jp`

Para autenticacion OAuth se debe usar:

- `https://accounts.zoho.com/oauth/v2/...`
- o el dominio `accounts.zoho.<dc>` segun el datacenter

### URLs incorrectas detectadas durante el desarrollo

Estas variantes provocaron errores en pruebas:

- `https://books.zoho.com/api/v3/...`
- `https://www.zohoapis.com/books/api/v3/...`

Problemas observados:

- Zoho respondio con error pidiendo usar `zohoapis`
- Zoho devolvio `400` por ruta incorrecta al usar `/books/api/v3/...`

### Regla operativa

Para cualquier instancia donde se use este modulo:

- La base API de Books debe construirse como `https://www.zohoapis.<dc>/books`
- Los endpoints deben agregarse como `/v3/<endpoint>`
- No usar `/api/v3/`
- No usar `books.zoho.<dc>` para llamadas API

## Uso del modulo

### Activacion del conector

1. Abrir **Zoho Books > Connectors**
2. Crear o editar el conector
3. Completar credenciales
4. Pulsar **Generate Auth URL**
5. Autorizar en Zoho
6. Confirmar el callback
7. Pulsar **Activate**
8. Pulsar **Test Connection**

### Importacion manual

1. Ir a **Zoho Books > Import Data**
2. Seleccionar el conector activo
3. Elegir si se importan productos y/o partners
4. Definir si se actualizan registros existentes
5. Ejecutar **Import Now**

### Lectura de resultados

Despues de cada importacion revisar:

- La notificacion final en pantalla
- Los registros en **Zoho Books > Logs**
- El archivo `config/odoo-server.log`

## Historial del proceso de desarrollo

Resumen de lo realizado hasta el estado actual.

### Etapa 1: estabilizacion de la conexion con Zoho

Problema detectado:

- El modulo consultaba `https://books.zoho.com/api/v3/items`

Resultado:

- Zoho devolvia error `400`
- El log indicaba que debia usarse el dominio `zohoapis`

Correccion aplicada:

- Se cambio la base API a `https://www.zohoapis.<dc>/books`

### Etapa 2: correccion de la ruta de API

Problema detectado:

- El modulo usaba `/books/api/v3/...`

Resultado:

- Zoho respondia con `400` e `Internal Error`

Correccion aplicada:

- Se cambio la ruta a `/books/v3/...`

### Etapa 3: mejora del diagnostico de errores

Problema detectado:

- Odoo mostraba errores genericos tipo `400 Client Error`

Correccion aplicada:

- Se mejoro la extraccion del mensaje JSON devuelto por Zoho
- El log ahora conserva mensajes tecnicos mas utiles

### Etapa 4: validacion de lectura real desde Zoho

Resultado:

- El modulo comenzo a leer correctamente productos desde Zoho
- Se confirmo en log la lectura paginada de productos

### Etapa 5: correccion del mapeo de tipo de producto

Problemas detectados en distintas pruebas:

- `Wrong value for product.template.type: 'product'`
- `Invalid field 'detailed_type' on model 'product.template'`

Interpretacion:

- La instancia no era compatible con una unica suposicion fija sobre el campo de tipo del producto

Correccion aplicada:

- El importador ahora inspecciona en tiempo de ejecucion si existe `type` o `detailed_type`
- Tambien inspecciona las opciones validas del campo y selecciona una compatible

### Etapa 6: mejora del feedback del wizard

Problema detectado:

- El wizard podia terminar con mensaje de exito generico aunque hubiera fallos por registro

Correccion aplicada:

- Se agrego un resumen final basado en los logs funcionales de importacion

### Etapa 7: correccion del mapeo de tipos de producto Zoho

Problemas detectados:

- Los servicios en Zoho pueden tener cantidad (ej: 10 horas de consultoria)
- En Odoo, el tipo `service` no permite gestion de stock
- El mapeo original no consideraba esta diferencia

Correccion aplicada:

- Se creo metodo `_get_product_type_vals` con mapeo corregido:
  - `goods` (Zoho) → `product` (Odoo) - stockeable
  - `consumable` (Zoho) → `consu` (Odoo) - consumible
  - `service` (Zoho) → `product` (Odoo) - forzado a stockeable para permitir cantidad
- Se agrego campo `zoho_product_type` en `product.template` para guardar el tipo original de Zoho
- El sistema ahora detecta automaticamente si usar `type` o `detailed_type` segun la version de Odoo

### Etapa 8: mejora del manejo de errores de API de Zoho

Problema detectado:

- Los errores de Zoho se mostraban como mensajes genericos `400 Client Error`
- No se podia identificar facilmente la causa raiz del error

Correccion aplicada:

- Se creo metodo `_extract_zoho_error` para extraer mensajes detallados de la respuesta JSON de Zoho
- El log ahora muestra el codigo de error y el mensaje descriptivo de Zoho
- Mejora significativa en el diagnostico de problemas de conexion y autenticacion

## Estado actual conocido

Confirmado en pruebas recientes:

- Partners importan correctamente
- Productos se leen correctamente desde Zoho
- El flujo de creacion de productos ya fue ajustado varias veces contra errores reales del log

Pendiente de validar completamente:

- Creacion exitosa final de productos en esta misma instancia tras el ultimo ajuste
- Importacion de ventas
- Importacion de movimientos de inventario
- Coherencia de impuestos, unidades de medida y stock
- Pruebas integrales en servidor de pruebas del negocio

## Procedimiento recomendado por instancia

Cada nueva instancia donde se despliegue este modulo debe validar lo siguiente antes de una migracion real:

1. Datacenter correcto de Zoho.
2. `redirect_url` correcto para esa instancia.
3. Callback accesible.
4. Activacion correcta del conector.
5. `organization_id` detectado o confirmado manualmente.
6. Prueba de conexion exitosa.
7. Importacion de partners de prueba.
8. Importacion de productos de prueba.
9. Revision de logs funcionales y tecnicos.
10. Validacion con usuarios del negocio.

## Validacion previa a migracion

Antes de usar Zoho de produccion o mover el modulo a un servidor de pruebas:

- Probar con un subconjunto pequeno de productos
- Probar clientes y proveedores reales
- Probar precios e impuestos
- Probar stock por producto
- Probar documentos comerciales
- Validar duplicados por `zoho_item_id` y `zoho_contact_id`
- Confirmar si se desea actualizar registros existentes o solo crear nuevos

## Logs y diagnostico

### Log tecnico principal

- `config/odoo-server.log`

### Que revisar primero

- `Starting product import from Zoho`
- `Fetching page`
- `Response status`
- `Fetched X products from Zoho`
- `Product '...'`
- `Fetched X customer contacts from Zoho`
- `Fetched X vendor contacts from Zoho`

### Observacion importante

Existe un error independiente en esta instancia relacionado con `autovacuum` y modelos transitorios:

- `TypeError: '>' not supported between instances of 'int' and 'str'`

Ese error aparece en muchos modelos del sistema y no forma parte directa del flujo de Zoho Books. Debe tratarse aparte.

## Versionado

Regla de trabajo aplicada durante este desarrollo:

- Cada cambio funcional del modulo debe reflejarse en `__manifest__.py`

## Changelog resumido reciente

- `18.0.1.2.0`
  Base inicial de esta etapa de pruebas.
- `18.0.1.2.1`
  Ajuste del mapeo de tipo de producto para Odoo.
- `18.0.1.2.2`
  Compatibilidad dinamica entre `type` y `detailed_type` y mejora del wizard.
- `18.0.1.2.3`
  Seleccion dinamica de valores validos para el tipo de producto segun la instancia.
- `18.0.1.2.4`
  Correccion del mapeo de tipos de producto Zoho (goods, service, consumable).
- `18.0.1.2.5`
  Agregado campo `zoho_product_type` y mejora del manejo de errores de API de Zoho.

## Siguiente fase sugerida

En la siguiente ronda de pruebas:

- Cargar operaciones de ventas en Zoho
- Cargar movimientos de inventario
- Repetir importacion
- Verificar trazabilidad completa en Odoo
- Confirmar si el modulo queda listo para servidor de pruebas del negocio
