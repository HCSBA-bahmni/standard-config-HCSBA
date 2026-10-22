# Colas operativas e identidad vigente

El 2026-10-19 se corrigieron diez propiedades `emrapi.sqlSearch` que multiplicaban tarjetas después de una consolidación clínica reversible. Conservar un número clínico histórico como alias no implica una segunda visita.

Fuentes: `gp_registration.xml`, `gp_clinical.xml` y `gp_patient_queue_identity.xml` en `masterdata/configuration/globalproperties`. La última incorpora ocho consultas activas del ambiente que no estaban versionadas en esos archivos. Propiedades cubiertas: activePatients, activePatientsByLocation, activePatientsByProvider, admittedPatients, emergencyMedicationToAcknowledge, highRiskPatients, otScheduledQueue, patientsHasPendingOrders, patientsToAdmit y patientsToDischarge.

`tools/normalize-queue-identities.py` transforma SQL revisado, con alias explícitos, usando subconsultas compatibles con MySQL 5.7:

- Un identificador no anulado por paciente y tipo: preferido primero; menor PK como desempate.
- Un nombre no anulado por persona con la misma regla.
- Paciente/persona no anulados.

No cambia filtros de visita, proveedor, ubicación o estado clínico. No borra alias ni compara personas por sus nombres. La selección es por tipo para conservar el contrato de cada consulta. El marcador `EIS_CURRENT_QUEUE_IDENTITY_V1` evita aplicar la transformación dos veces; no utilizar el script indiscriminadamente en SQL sin caracterizar.

Pruebas: `python -m unittest discover -s tools -p test_normalize_queue_identities.py`. Cubren nombres/identificadores preferidos, fallback determinista, tipos independientes, conservación de alias, separación e idempotencia.

## Publicación y recuperación

Las definiciones XML conservan la corrección para futuras cargas de configuración. Publicar una imagen de configuración por sí sola no actualiza los global properties ya persistidos en OpenMRS: aplicar los valores revisados por `systemsetting`, con backup previo y comprobación de concurrencia.

Antes de publicar: comparar consultas con datos reales y comprobar que el conjunto de UUID paciente/visita no cambia. Después: leer de nuevo el valor completo por REST y ejecutar el endpoint nativo `/ws/rest/v1/bahmnicore/sql?q=...`. El filtro XSS de `systemsetting` puede convertir operadores angulares en entidades HTML; el normalizador evita esos operadores en sus expresiones de prioridad, en vez de deshabilitar el filtro.

Publicación validada `.225` con configuración `2026.10.19-clinical.6`. Backup y prueba de equivalencia: `F:/Proyectos/HIS/analisis/2026-10-19/validacion-visual-mpi/queue-settings-before.json` y `queue-repair-verification.json`. Recuperación: restaurar los valores previos de esas diez propiedades mediante la misma API y verificar lectura/consulta; no requiere restaurar historias ni eliminar identificadores.

No se modificaron `bedsGroupedByAdmission` ni `movimientosCamasDia`, que son reportes históricos de camas. No confundir Activo/visita activa con hospitalización.
