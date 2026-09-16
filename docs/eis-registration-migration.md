# Registro de pacientes EIS Chile en HCSBA

## Fuentes fijadas

| Componente | Referencia | Commit |
| --- | --- | --- |
| Configuración HealthMesh | `standard-config-chile`, tag `2026.08.2` | `004884e` |
| Comportamiento legacy | `openmrs-module-bahmniapps-chile`, tag `2026.08.2` | `54bbc13` |
| Módulo de identidad base | `openmrs-module-eis-identity`, tag `v0.1.0` | `81bcbf4` |
| Variante HCSBA | rama `hcsba/eis-registration` | `c092b6d` (sobre `v0.1.0`) |

No actualizar desde ramas móviles sin repetir el inventario de UUID, contratos y
pruebas. La configuración portada conserva los UUID públicos de los metadatos
EIS para mantener la compatibilidad con la UI y el OMOD. La excepción deliberada
es `Pasaporte`: si ya existe en HCSBA, se reutiliza su UUID local para conservar
las referencias de pacientes; una instalación limpia usa el UUID EIS.

## Decisiones HCSBA

- El identificador primario continúa siendo el tipo nativo `Patient Identifier`.
- La fuente histórica `RUT*` y su secuencia no se modifican.
- Los pacientes nuevos usan la fuente institucional `HCSBA`, UUID
  `ed8eead4-146b-4548-84ea-cb897ff82d6e`.
- El RUN es un identificador nacional adicional, no el número de ficha.
- No se aplica la migración HealthMesh que renombra el tipo primario por nombre;
  HCSBA todavía tiene reportes e integraciones que dependen de `Patient Identifier`.
- `layout.name.format=latinamerica` incorpora `familyName2` a los nombres
  renderizados sin cambiar el locale canónico existente.
- Las reglas JavaScript legacy se conservan para rollback. Next.js debe portar
  las condiciones mediante adaptadores TypeScript explícitos y nunca ejecutar
  esos scripts remotos.

## Compuertas de despliegue

1. Ejecutar `db/preflight/eis-registration.sql` en una copia o sesión de sólo
   lectura y resolver cada colisión por nombre o UUID.
2. Respaldar de forma consistente `openmrs` y `eis_identity`.
3. Crear y actualizar `eis_identity` únicamente mediante `db/apply.sh` del OMOD.
   El script alinea la collation con `openmrs`, concede DML al usuario de la
   aplicación y aplica DDL, backfill y limpieza en orden.
4. Instalar e iniciar el OMOD HCSBA; comprobar que OpenMRS puede resolver
   `org.openmrs.module.eisidentity.validation.RunIdentifierValidator`.
5. Importar primero fuentes de conceptos y conceptos EIS, después atributos y
   tipos de identificador, y al final configuración de aplicación.
6. Validar la jerarquía territorial antes de importar: su XML usa `wipe=true`.
   Los valores clínicos históricos no deben transformarse por inferencia.
7. Probar creación, edición y búsqueda con RUN, pasaporte, folio de parto,
   documento extranjero y paciente sin RUN antes de habilitar el corte Next.js.

## Particularidades del despliegue compartido HCSBA

- No se debe inferir el MySQL activo desde el puerto `3306` del host de
  OpenMRS. En el despliegue verificado el 2026-08-25, OpenMRS en `.205` usa el
  JDBC declarado en `/openmrs/data/openmrs-runtime.properties`, cuyo servidor
  es `.222`. Preflight, respaldo, `db/apply.sh` y postflight deben apuntar al
  host obtenido de esa propiedad y al mismo esquema `openmrs`.
- La configuración efectiva persiste en `/openmrs/data/configuration`. Montar
  una imagen nueva en `/etc/bahmni_config` no reemplaza automáticamente los
  archivos ya persistidos. En una promoción incremental se copian sólo los
  dominios EIS aprobados a la ruta activa y se conserva un tar previo de ella.
- Los checksums no sustituyen la validación de base de datos: Initializer puede
  escribirlos aunque un cargador no haya consolidado sus cambios. Después de
  cada importación se comprueban los metadatos tanto por SQL en el JDBC activo
  como por REST. Sólo ante una reejecución diagnosticada se eliminan los
  checksums exactos de los archivos EIS; nunca se vacía el directorio completo.
- El resultado esperado de esta versión es: 12 tipos de identificador clínico
  o normativo, 15 atributos de persona/contacto, 276 conceptos mapeados a
  `EIS-820`, 422 entradas territoriales y los dos orígenes IDGen históricos e
  institucionales asociados a `Patient Identifier`.

## Reversa

- Desactivar primero el validador del tipo RUN y retirar la configuración EIS.
- Volver el prefijo predeterminado al valor anterior sin borrar ninguna fuente
  IDGen ni reasignar identificadores existentes.
- Retirar el OMOD sólo después de eliminar la referencia a su clase validadora.
- Restaurar `openmrs` y `eis_identity` siempre desde el mismo punto temporal.

El despliegue al OpenMRS remoto no forma parte de la carga automática del
entorno frontend y requiere una autorización operativa explícita.
