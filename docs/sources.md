# Fuentes incluidas, sin cobertura inventada

| Adaptador | Qué hace hoy | Qué no hace |
| --- | --- | --- |
| `page` | GET de una URL pública, título/OpenGraph, imagen, campos JSON-LD y dormitorios declarados en metadatos | No interpreta fotos, no recorre todo un portal, no infiere disponibilidad ni extrae todo texto libre |
| `rss` | RSS 2.0: título, link y fecha publicada declarada por el feed | No Atom, grupos privados ni Stories |
| `json` | Catálogo público con `listings[]`: URL, título, dormitorios, precio, moneda e imágenes | No APIs autenticadas ni acceso a bancos/chats |

Una fuente es una URL registrada por el usuario, no una lista de sitios que
supuestamente ya se recorren. Los feeds JSON/RSS permiten descubrir varios avisos;
`page` revisa una ficha que ya tenés. Podés registrar varias fuentes por ciudad.
Los metadatos pueden estar desactualizados o equivocados: son pistas por verificar.

## Registro y revalidación

```sh
python3 bin/mudanza source-add --workspace "$HOME/.gestor-mudanza/mi-busqueda" \
  --id agencia --adapter page --url 'https://example.invalid/una-ficha'
python3 bin/mudanza collect --workspace "$HOME/.gestor-mudanza/mi-busqueda" --source agencia
```

La URL de arriba es ficticia: reemplazala por una ficha pública real. El colector
consulta robots.txt, usa límites de tamaño/tiempo y se detiene ante redirecciones,
restricciones o errores. No sortea captchas/logins ni usa proxies. Reintentos no
son automáticos. Cooldown: una hora por fuente, también después de error.
Máximo 50 entradas por feed. Los errores quedan visibles en el tablero y no cierran
propiedades. La deduplicación usa URL normalizada sin trackers: no fusiona unidades
por compartir dirección, ni detecta automáticamente duplicados entre portales.

Una observación nueva conserva el descarte; diferencias de precio/metadatos se
registran como cambios. Que falte un aviso en el feed no prueba que se alquiló.
Un cambio a `closed` requiere decisión humana documentada.

## Fuentes de Bahía Blanca (catálogo de puntos de entrada, no conectores especiales)

- [Bahía Blanca Propiedades](https://www.bahiablancapropiedades.com/): fichas públicas
  como pistas; no asumir stock por catálogo. El adaptador `page` se verificó contra
  una ficha pública durante el desarrollo, sin incorporar datos a la demo.
- [Grupo IBB](https://www.grupoibb.com/): comprobar URLs y acceso antes de registrar.
  No se verificó un scrape propio para este portal.
- Otros portales/inmobiliarias: usar `page` si exponen metadatos; si el sitio requiere
  JavaScript, importar un export autorizado o trabajar con el agente y navegador.
- Instagram/Facebook: acceso manual autorizado; no scrape incluido ni cobertura
  de cuentas privadas, Stories o grupos cerrados.

No se distribuyen fuentes preactivadas ni datos de una búsqueda personal.

## Formato JSON e importación sin red

`examples/sources/listings.json` es una fixture ficticia. Podés importar un archivo
con ese formato mediante `collect --source ID --snapshot FILE`. La evidencia se
marca `imported_snapshot`, nunca revisión en vivo. No se almacenan páginas completas,
cookies ni credenciales; se guardan los campos extraídos y la fecha de observación.

Referencias: [RSS 2.0](https://www.rssboard.org/rss-specification),
[Schema.org RealEstateListing](https://schema.org/RealEstateListing).
