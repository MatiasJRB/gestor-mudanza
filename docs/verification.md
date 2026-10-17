# Verificación v0.3 · apoyos y proceso completo

Revisión actualizada el 17 de octubre de 2026 para la distribución v0.3 experimental.
Esta entrega es un repositorio de código y skills; no despliega una web ni un servicio.

## Evidencia ejecutada

- **48 pruebas** pasando: CLI anterior, flujo completo de usuario nuevo, persistencia
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


## Apoyos incluidos

Skills legal y financiera presentes y referenciadas por el gestor. Contador externo
referenciado, sin instalación ni llamadas automáticas. `support` probado para los
tres roles: contexto mínimo, destinos explícitos y estado de pedido no revisado.
Aritmética financiera por tres ejes, moneda única, mensual separado de entrada,
fuentes para costos declarados confirmados y faltantes/estimados fuera de esos
subtotales. Tests verifican que no se transmite información ni se decide solvencia.
No se ejecutó una consulta profesional ni un modelo de IA: las skills dependen del
host. La matriz README distingue método, herramientas locales y capacidades pendientes.

## Gate de distribución · 17/10/2026

- Clon nuevo desde el repositorio remoto, sin depender del workspace del autor.
- 48 pruebas pasando y recorrido sintético completo ejecutado: inicialización,
  fuente, importación, decisiones, conversaciones, recibo ficticio y tablero.
- Scanner del paquete: 36 archivos sin alertas. Escaneo del historial previo:
  50 blobs únicos sin patrones sensibles detectados; revisados código, ejemplos,
  skills, documentación y metadatos de commits. Sólo datos sintéticos en demos.
- La revisión no certifica ausencia absoluta de secretos ni soporte universal.
  No se probaron conectores privados, envíos, un LLM externo ni nuevos portales.
- El recorrido escribe de nuevo la demo sintética y puede cambiar su fecha de
  observación. No modifica una instancia personal ni necesita una cuenta externa.
