# De cero a una búsqueda que podés retomar

Necesitás Python 3.9+ y este checkout. No hay instalación de dependencias para
la CLI. Para conversación libre, abrí el repo en tu host de agentes y pedile que
lea `skills/gestor-mudanza/SKILL.md`. El modelo lo aporta el host, no este repo.

## Arranque con agente

Abrí una conversación en el repo y escribí:

> Usá el agente de gestor-mudanza incluido en skills/gestor-mudanza/SKILL.md.
> Creá mi búsqueda. Preguntame ciudad y criterios, guardá mi instancia fuera del
> repositorio y ayudame a registrar fuentes públicas. Mostrame una tanda de
> próximos pasos con mensajes para revisar. No envíes nada.

El agente cuenta con los comandos de abajo. Si preferís no usar un modelo,
`agent --request retomar` genera la tanda por reglas, sin conversación libre.

## Primer recorrido, sin cuentas ni avisos reales

Desde el checkout:

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
python3 bin/mudanza agent --workspace "$W" --request retomar --report
```

Este recorrido **sí crea una instancia, importa registros, guarda una conversación
 y genera un tablero operativo**. Los datos son ficticios; `--snapshot` no hizo red.
La última salida imprime `report_path`: abrí ese `board.html` en tu navegador.
No lo confundas con la demo estática del README. Repetir `init` no pisa tu trabajo.

## Pasar a fuentes reales

Creá otra carpeta para tu búsqueda real. Registrá fichas públicas con `page`, un
RSS de una inmobiliaria que lo ofrezca o un catálogo JSON autorizado. Reemplazá
la URL ficticia por la fuente concreta. No hay feeds inmobiliarios activos por
 defecto ni un buscador que encuentre todas las viviendas de una ciudad.

```sh
python3 bin/mudanza source-add --workspace "$W" --id ficha \
  --adapter page --url 'https://example.invalid/reemplazar-por-ficha-real'
python3 bin/mudanza collect --workspace "$W" --source ficha
python3 bin/mudanza agent --workspace "$W" --request buscar --report
```

`buscar` refresca las fuentes registradas; no navega otros sitios. Ante error,
mirá la cobertura del tablero. No sortees restricciones. El colector no convierte
avisos en disponibilidad confirmada. [Adaptadores y límites](sources.md).

## Registrar tu decisión visual

`export` muestra los IDs de propiedades. Usá el de la unidad concreta:

```sh
python3 bin/mudanza export --workspace "$W"
python3 bin/mudanza decide --workspace "$W" --property ID --state interested
python3 bin/mudanza decide --workspace "$W" --property OTRO_ID --state discarded
```

Los descartados no se reintroducen al colectar de nuevo. Si el sitio no declaró
los dormitorios, podés cargar el dato verificado con `decide --bedrooms 2`.
La ciudad es contexto, no un geofiltro automático del scraper: configurá tus fuentes
para la zona correcta y verificá la ubicación antes de recomendar.

## Seguimiento de conversaciones

La versión inicial registra texto y recibos manualmente. No lee tu WhatsApp/Gmail
por sí sola; tu agente puede importar datos de conectores que vos autorices.

```sh
python3 bin/mudanza message-log --workspace "$W" --conversation agencia \
  --direction outgoing --at '2026-01-05T12:00:00Z' \
  --text 'Hola! ¿Las fotos son actuales de esa unidad?' --receipt 'recibo-verificado-001'
python3 bin/mudanza message-log --workspace "$W" --conversation agencia \
  --direction incoming --at '2026-01-05T13:00:00Z' --text 'Te paso un video mañana'
python3 bin/mudanza wait --workspace "$W" --conversation agencia \
  --until '2026-01-06T20:00:00Z'
python3 bin/mudanza draft --workspace "$W" --conversation agencia \
  --text 'Hola! ¿Me pasás el video cuando lo tengas? Gracias!'
python3 bin/mudanza agent --workspace "$W" --request seguimiento --report
```

Estos comandos **registran** lo sucedido: no envían. El recibo es evidencia que
aportás vos/el conector; la CLI no verifica autenticidad contra el servicio.
Un nuevo entrante invalida el borrador anterior para no responder con texto viejo.
`conversation-close --reason MOTIVO` retira una conversación; `--followup` en un
saliente con recibo incrementa la cuenta de seguimientos confirmados. Después de
dos seguimientos sin respuesta, el agente propone cambiar canal/bajar prioridad.

El motor cuenta 48 horas en fechas hábiles (24 horas por día lunes a viernes),
excluyendo feriados configurados. No supone horario de atención de la inmobiliaria.
`init --timezone ZONA_IANA` usa tu zona; `holidays --dates YYYY-MM-DD ...` permite
configurar feriados. No descubre feriados automáticamente ni agenda recordatorios.
`review_at` es un campo de la instancia; `wait` es el comando de espera explícita.

## Costos y respaldos

Para conservar una copia privada y usar la sumatoria por medio/moneda:

```sh
python3 bin/mudanza export --workspace "$W" > "$W/respaldo.json"
python3 bin/mudanza costs --input "$W/respaldo.json" --currency ARS
```

El export es un respaldo legible, no hay comando de restauración/importación de
estado completo aún. Para respaldo restaurable cerrá los procesos y copiá la carpeta
privada. El núcleo de costos sigue aceptando JSON externo; no hay banco conectado,
ni financiación ni evaluación de solvencia. El tablero real y los exports contienen
información privada: no subir al repo, a issues ni a una preview pública.


## Pedir apoyo sin gestionar otros chats

En el mismo hilo del gestor:

> «Quiero avanzar con esta vivienda. Revisá qué falta de documentación y pedile
> apoyo legal y financiero a los roles incluidos. Devolveme todo junto: riesgos,
> caja, supuestos y próximos pasos. No reserves ni envíes nada.»

El host aplica las skills incluidas; no se inicia un modelo remoto por la CLI.
Para verificar el formato sin datos privados:

```sh
python3 bin/mudanza support --role legal --input examples/support-legal.json
python3 bin/mudanza support --role financial --input examples/support-financial.json
python3 bin/mudanza support --role tax --input examples/support-tax.json
```

La salida es un pedido preparado, no una revisión concluida. En el ejemplo financiero
hay ARS100.000 de entrada declarada en efectivo, ARS30.000 en tarjeta y un flete
sin importe: no representa capacidad de pago. [Coordinación y privacidad](support.md).
