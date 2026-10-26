# Acceso a Pabellón oculto — 2026-10-26

Se retira la extensión `bahmniOT` (`bahmni.ot`, enlace `../ot/`) de
`openmrs/apps/home/extension.json` a petición del usuario, para evitar confundir
el módulo de pabellón de Bahmni con el sistema de pabellones del hospital cuya
integración se analizará por separado.

Next.js (`loadExtensions("home")`) y el inicio AngularJS (`appService` /
`AppDescriptor.getExtensions`) consumen esta configuración. No se usa
`online: false`, porque el inicio AngularJS no aplica ese filtro.

El cambio afecta la visibilidad del acceso desde Inicio. Se conservan el módulo
OT, su configuración, permisos, endpoints y datos; la URL directa continúa
existiendo. `extension copy.json` es una copia que no consume el cargador de
Inicio y no se modifica. Para revertir, restaurar sólo el bloque `bahmniOT`
desde la revisión anterior de Git.

No se implementa todavía el intercambio con el sistema hospitalario. Antes de
decidirlo se debe caracterizar ese sistema, los datos de Bahmni que necesita
leer, sus contratos disponibles, identificación de pacientes y contexto de
atención, autenticación, permisos y auditoría.

## Verificación local

- JSON válido; comparación con `HEAD` confirma que únicamente se retiró
  `bahmniOT` y que las otras 13 extensiones conservan su contenido.
- `/bahmni_config/openmrs/apps/home/extension.json` devuelve el mismo contenido
  que el checkout. El override de Inicio en `/implementation_config` responde
  404, condición opcional admitida por el cargador.
- Inicio Next.js comprobado en `https://localhost/bahmni/home` con sesión de
  administrador: el listado ya no muestra `Operation Theatre` ni enlaces a OT.
- `dev-environment.ps1 verify` completo pasó, incluido WebSocket Fast Refresh.
- Fue necesario renovar el certificado local, vencido el 23 de octubre,
  mediante el generador del repositorio. Se conservó la misma CA y se reinició
  únicamente el proxy para actualizar sus montajes TLS. No se reconstruyeron
  imágenes ni se reinició Next.js ni los servicios clínicos.
- Evidencia: `F:/Proyectos/HIS/analisis/2026-10-26/pabellon/inicio-sin-pabellon.jpg`.

No se modificó código de aplicación ni se ejecutó build o suite de frontend
para este cambio de configuración.

## Entrega en el remoto de desarrollo .225

Publicado y comprobado también en `https://10.68.174.225/bahmni/home`, con
imagen de configuración `hcsba/standard-config:2026.10.26-hide-ot.2`. Se partió de
la imagen y configuración remotas vigentes, retirando sólo `bahmniOT`; las 14
extensiones restantes conservan su contenido, incluida `patientManagement`,
que no estaba en el checkout local utilizado para este cambio.

Se recreó únicamente `bahmni-config`; Next.js, OpenMRS, MPI y los demás
contenedores no se recrearon. Se actualizó también el archivo fuente remoto
de Inicio y el tag de configuración del overlay Compose local/remoto. Se
preservaron las demás diferencias de esos archivos, incluidos sus tags Next.

Respaldo remoto en
`/home/arki/bahmni/bahmni-docker-HCSBA/bahmni-standard/production-225/releases/2026.10.26-hide-ot.2`:
configuración servida, fuente y overlay anteriores. Para revertir, restaurar
el overlay y fuente respaldados y recrear sólo `bahmni-config` con la imagen
anterior `hcsba/standard-config:2026.10.21-patient-management.1`.

La primera comprobación de entrega intentó leer por HTTP y recibió una
redirección; se revirtió automáticamente antes de publicar la versión `.2`,
comprobada por HTTPS con validación de CA. Las imágenes `.1` y `.2` tienen
el mismo contenido de configuración.

Inicio comprobado en navegador con administrador, sin Pabellón y con Gestión
de pacientes. Evidencias y scripts:
`F:/Proyectos/HIS/analisis/2026-10-26/pabellon/` (`publication225.json`,
`verification225.json`, `inicio225-sin-pabellon.jpg`).

La preferencia de mantener las entregas disponibles en `.225`, confirmada por
el usuario el 2026-10-26, queda registrada en `DEV_VERSION/AGENTS.md`.
