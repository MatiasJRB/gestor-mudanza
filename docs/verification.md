# Verificación del paquete local

Revisión del 13 de octubre de 2026, realizada antes del primer commit y de la subida al repositorio privado.

- 16 pruebas unitarias/CLI: estados, descartes, unidad exacta, recibos,
  sumas por medio/moneda, importes faltantes y entradas inválidas.
- Los tres comandos se ejecutan contra la fixture. Las pruebas confirman que
  no modifican el archivo de entrada.
- Demo regenerada desde el núcleo; prueba de reproducción byte a byte.
- Auditoría de rutas y patrones del conjunto candidato a distribuir: sin hallazgos.
  Es heurística, no certifica ausencia universal de información sensible.
- Revisados README, documentación, fixture y SVG: sólo datos sintéticos,
  sin conversaciones, contratos o credenciales de una instancia real.
- Preview comprobada en navegador con modo oscuro y tamaños amplios/estrechos;
  sin desborde horizontal según medidas del DOM. El JSON se puede desplegar.
- Checkout sin historial anterior al momento de la auditoría inicial. La subida
  posterior autorizada es a un repositorio privado; la demo web sigue siendo local.

La demo es estática. No ejecuta una búsqueda ni prueba conectores externos.
Antes de publicar, volver a revisar el diff y todos los archivos que se vayan
al primer commit. No incluir archivos ignorados, instancias privadas o capturas.
