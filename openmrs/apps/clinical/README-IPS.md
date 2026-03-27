Notas de configuración de IPS (LAC)

- La sección del dashboard se configura en `openmrs/apps/clinical/dashboard.json` bajo `general.sections.ips` con `type: "ipsReact"`.
- No se usa `app.json > config.dashboardSections` para el orden ni visibilidad.
- Requiere que el módulo bahmniapps registre el display control `ipsReact` (repositorio HCSBA-bahmni/openmrs-module-bahmniapps-hcsba-2024).
- No es necesario el control custom `<ips-dashboard>` ni la vista `ipsSection.html`. Pueden eliminarse si no se usan en otros lugares.
