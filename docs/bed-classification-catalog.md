# Catálogo de clasificación de camas

Complemento de [Next.js PR #19](https://github.com/HCSBA-bahmni/bahmni-nextjs-hcsba/pull/19).
La definición versionada está en `bed-classification-catalog.json` y el changelog
en `masterdata/configuration/liquibase/hcsba_bed_classification.xml`, incluido
desde el `liquibase.xml` principal. Sigue el contrato del [dominio Liquibase de
Initializer 2.7.0](https://github.com/mekomsolutions/openmrs-module-initializer/blob/2.7.0/readme/liquibase.md).

## Datos y conservación

- Añade 12 `bed_tag`: cuatro complejidades, tres rangos etarios, tres usos
  especiales y dos condiciones administrativas. No añade tipos funcionales.
- Usa UUID estables para etiquetas nuevas. Si ya existe exactamente el mismo
  nombre activo, conserva su ID y UUID, aunque difieran de los del catálogo.
- Crea descripciones faltantes en `hcsba.bedTag.description.{uuid}` y metadatos
  de actividad de las dos condiciones. Conserva los valores personalizados.
- Detiene la aplicación ante nombres duplicados, anulados, diferencias de
  mayúsculas/acentos o UUID reutilizados con otro nombre. Se requiere conciliación
  explícita; no renombra ni resucita etiquetas.
- No cambia `bed`, `bed_type`, `bed_tag_map`, pacientes ni asignaciones. Las camas
  antiguas conservan su complejidad en el tipo hasta una decisión explícita.
- Una condición es clasificación administrativa. El bloqueo para asignaciones
  usa el estado nativo `BLOCKED`; no se provisiona una regla paralela `allowsUse`.
- `gp_bedmanagement.xml` versiona la habilitación de gestión de ubicaciones/salas
  ya requerida por HCSBA. No concede roles ni privilegios.

## Aplicación controlada

1. Verificar destino OpenMRS de desarrollo `.225`, revisión de frontend y respaldo
   de las tablas/metadatos afectados. Verificar `users.user_id=1` y el esquema
   nativo de Bed Management antes de ejecutar.
2. Leer las 12 filas del catálogo y cotejar nombres, UUID, anulaciones,
   descripciones y asociaciones existentes. Resolver precondiciones fallidas sin
   borrar registros ni modificar UUID usados por otras fuentes.
3. Publicar ambos XML y el global property por el flujo de configuración existente.
   No reemplazar configuración remota ajena al alcance ni reiniciar OpenMRS
   indiscriminadamente. Initializer consume el include relativo al master.
4. Para una aplicación dirigida, usar el changelog complementario con el mismo
   identificador de archivo que utilizará Initializer y su ledger. No ejecutar el
   master completo con historial desconocido para instalar sólo este catálogo.
5. Comprobar las 12 etiquetas por REST y la propiedad de gestión; comparar UUID,
   descripciones, asociaciones y tipos antes/después. Una segunda aplicación no
   debe crear etiquetas ni sobreescribir valores. Ensayar la recuperación de la
   categorización en el frontend corregido con datos sintéticos.

La reversión del frontend conserva estas etiquetas y sus asociaciones. No se
incluye un `DOWN` destructivo ni se borran filas/ledger para hacer pasar pruebas.
No se afirma aplicación de esta revisión en `.225` por publicar el PR.

## Prueba reproducible

`scripts/test-bed-classification-mysql.py` utiliza MySQL real y Liquibase, en
esquemas nuevos `pr19_catalog_*` de una instancia **desechable** local en
`127.0.0.1:13319`. Requiere el cliente `mysql`, Java y las dependencias de Liquibase.
Indicar `PR19_MYSQL_CLIENT` y `PR19_LIQUIBASE_CLASSPATH`; el script no acepta un
host remoto, no toca servicios existentes y no elimina esquemas.

Cubre instalación limpia, segunda aplicación, UUID/descripcion personalizados,
asociaciones y tipo heredado conservados, duplicados, anulación, conflicto UUID
y diferencias de mayúsculas. La revisión de 20-11-2026 usó MySQL 8.0.40 y
Liquibase 4.4.3. No sustituye la validación del MariaDB/OpenMRS real de `.225`.
