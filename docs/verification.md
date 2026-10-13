# Verificación v0.2

Revisión del 13 de octubre de 2026. Repositorio privado; ninguna web publicada.

## Evidencia ejecutada

- **38 pruebas** pasando: CLI anterior, flujo completo de usuario nuevo, persistencia
  transaccional/rollback, cierres/recibos/esperas, zonas y feriados, adaptadores,
  robots, URLs privadas, escape de HTML, deduplicación y preservación de descartes.
- `scripts/walkthrough.py` ejecuta init → registro de fuente → importación → decisión
  visual → conversaciones → recibo ficticio → agente → tablero. Usa una instancia
  temporal nueva y conserva sólo su copia HTML sintética para mostrar el resultado.
- Consulta HTTP real a una ficha pública de Bahía Blanca Propiedades: robots leído,
  GET exitoso, una pista importada con dos dormitorios declarados. No prueba stock,
  exactitud de fotos, precio vigente ni disponibilidad. No se guardaron datos de esa
  ficha en fixture, demo o repositorio; el workspace temporal se eliminó al terminar.
- Auditoría de rutas/patrones del conjunto candidato a distribuir sin hallazgos;
  revisión de documentación y fixture: sin contratos, chats, contactos o credenciales
  de una instancia real. El scanner es heurístico, no una certificación absoluta.
- Tablero oscuro responsive verificado en navegador. Snapshot rotulado como
  importación, no consulta live. Contenido de publicaciones/mensajes se escapa.

## Lo que no se probó ni se promete

No extracción exhaustiva de portales ni conectores autenticados. RSS/JSON probados
con fixtures, no un feed inmobiliario vivo. No hay scraping de Stories/grupos
privados, envío, reserva, pagos o scheduler. No se ejecutó un modelo remoto: la
skill conversacional necesita el host del usuario; el coordinador por reglas sí
fue ejecutado de punta a punta. No se afirma soporte de todos los sistemas operativos.

## Reproducir

```sh
python3 -m unittest discover -s tests -v
python3 scripts/walkthrough.py
python3 scripts/check_public_bundle.py
```

Mantener instancias y resultados reales fuera del repo. Antes de hacer público,
volver a revisar todo el diff y el historial, no sólo archivos ignorados.
