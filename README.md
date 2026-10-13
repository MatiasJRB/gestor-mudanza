# Gestor de mudanza

![Gestor de mudanza: tu agente ordena la búsqueda, vos decidís](docs/demo/cover.svg)

**Volvé a tu búsqueda sin tener que recordar qué quedó pendiente.**

Primera versión local operable: fuentes públicas configurables, viviendas y
conversaciones persistentes, más un agente que prepara el “para mover hoy”.
Vos decidís el gusto, los envíos, las visitas y el dinero. Licencia MIT.

[Empezar de cero](docs/quickstart.md) · [Agente incluido](skills/gestor-mudanza/SKILL.md) · [Fuentes](docs/sources.md) · [Verificación](docs/verification.md)

## El agente es la interfaz

Abrí el checkout en tu host de agentes y pedile:

> «Usá la skill gestor-mudanza incluida. Creá mi búsqueda, preguntame ciudad y
> criterios, registrá mis fuentes y dejame los mensajes pendientes juntos.
> No envíes nada.»

La skill incluida coordina las herramientas de este repo. **El modelo conversacional
lo aporta tu host**; no viene un LLM ni una suscripción empaquetada. También podés
usar `bin/mudanza agent` sin modelo: el coordinador por reglas prepara pendientes
y tablero, pero no entiende conversación libre. No requiere claves ni dependencias.

## Un recorrido real en un minuto

Python 3.9+; desde la carpeta del proyecto:

```sh
W="$HOME/.gestor-mudanza/primera-prueba"
python3 bin/mudanza init --workspace "$W" --city 'Ciudad de ejemplo' --bedrooms 2
python3 bin/mudanza source-add --workspace "$W" --id catalogo \
  --adapter json --url 'https://example.invalid/feed'
python3 bin/mudanza collect --workspace "$W" --source catalogo \
  --snapshot examples/sources/listings.json
python3 bin/mudanza conversation-add --workspace "$W" --id agencia \
  --contact 'Agencia de ejemplo' --url 'https://example.invalid/chat' \
  --draft 'Hola! ¿Las fotos son actuales de esa unidad?'
python3 bin/mudanza agent --workspace "$W" --report
```

Este recorrido crea una instancia SQLite privada, importa dos avisos sintéticos,
guarda un borrador y genera `board.html` en tu instancia. Abrí el `report_path`
impreso. No son capturas ni un estado hardcodeado: los comandos operan sobre datos
persistentes. La fixture no hace red ni contiene precios de mercado.

Para avisos reales reemplazá la fuente por una URL pública y ejecutá `collect`
sin `--snapshot`. `agent --request buscar` revalida las fuentes registradas.
[Cómo importar, decidir y retomar](docs/quickstart.md).

## Qué funciona hoy

| Parte | Implementación |
| --- | --- |
| Fuentes | GET acotado de fichas HTML/OpenGraph/JSON-LD, RSS 2.0 y catálogos JSON; respeta robots, errores visibles y cooldown |
| Evidencia | URL, fecha observada y publicación declarada; aviso siempre sin disponibilidad confirmada |
| Persistencia | SQLite fuera del repo, transacciones y registro de cambios; no pisa una instancia existente |
| Deduplicación | URL normalizada; conserva descartes y registra cambios de metadatos |
| Seguimiento | Borradores, mensajes importados, recibos, espera acordada, cierres y retoma por días hábiles configurables |
| Agente | Skill conversacional portable + coordinador local que prioriza una tanda y genera tablero privado oscuro |
| Costos | Sumatoria JSON por moneda, separando efectivo/tarjeta/medio desconocido y faltantes; no solvencia |

## Límites de esta versión

No es un buscador universal: `page` revisa links registrados; RSS/JSON descubren
avisos sólo dentro del feed configurado. No hay scrapers especiales de todos los
portales ni fuentes preactivadas. Sitios privados/JavaScript pueden requerir
importación manual. No se confunden hora de scrape y fecha de publicación.

WhatsApp, Gmail y Calendar **no están conectados automáticamente**. La CLI registra
intercambios aportados por la persona o un conector autorizado del host. Un silencio
local puede ser falta de importación. Los templates deben revisarse con el hilo.
No hay envío, reserva, pago, rescisión, scheduler, cuotas ni proyección financiera.
Los feriados se configuran. El usuario confirma características y disponibilidad.

## Privacidad

Instancia real fuera del checkout. El repositorio trae sólo código y ejemplos
inventados. Los tableros, exports y registros de mensajes reales son privados.
No subir contratos, credenciales o chats a issues/commits ni demos públicas.
[Política y alcance](docs/privacy.md).

## Desarrollo

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_demo.py
python3 scripts/check_public_bundle.py
```

La demo estática original sigue en `docs/demo/index.html`; el tablero operativo
se genera con `agent --report` sobre una instancia. El scanner es una revisión
heurística del paquete, no una certificación de privacidad. Sin asesoramiento
jurídico, inmobiliario ni financiero.
