# Gestor de mudanza

![Gestor de mudanza: tu agente ordena la búsqueda, vos decidís](docs/demo/cover.svg)

**Volvé a tu búsqueda sin tener que recordar qué quedó pendiente.**

Versión **v0.3 experimental**: herramientas locales y skills para tu host de agentes.
No es un servicio alojado ni una inmobiliaria.

Un agente para acompañarte desde la búsqueda de vivienda hasta organizar el
traslado: investigar, evaluar opciones, ordenar los números, preparar documentación
y empujar lo pendiente sin hacerte reconstruir todo cada vez.

Incluye herramientas locales, seguimiento persistente y agentes de apoyo legal y
financiero; referencia al contador como herramienta externa. **Vos decidís el gusto,
los envíos, las visitas y el dinero.** Licencia MIT.

[Empezar de cero](docs/quickstart.md) · [Proceso completo](docs/process.md) · [Agentes y contador](docs/support.md) · [Fuentes](docs/sources.md) · [Verificación](docs/verification.md)

## El agente es la interfaz

Abrí el checkout en tu host de agentes y pedile:

> «Usá la skill gestor-mudanza incluida. Creá mi búsqueda, preguntame ciudad y
> criterios, registrá mis fuentes y dejame los mensajes pendientes juntos.
> No envíes nada.»

La skill incluida coordina las herramientas de este repo. **El modelo conversacional
lo aporta tu host**; no viene un LLM ni una suscripción empaquetada. También podés
usar `bin/mudanza agent` sin modelo: el coordinador por reglas prepara pendientes
y tablero, pero no entiende conversación libre. No requiere claves ni dependencias.

## Del aviso a la mudanza

| Momento | En qué te ayuda el agente |
| --- | --- |
| **Buscar** | Investigar fuentes, alertas y contactos; distinguir pistas recientes de catálogos viejos |
| **Evaluar** | Mostrar fotos/características, conservar descartes y validar unidad exacta antes de una visita |
| **Mantener el ritmo** | Reconciliar conversaciones primero; traer una tanda accionable, respetar esperas y descanso |
| **Decidir** | Comparar vivienda actual/nueva, ubicación y logística; ordenar caja y escenarios sin comerse planes personales |
| **Tramitar** | Revisar requisitos, ingresos/garantes y documentos; preparar consultas sobre contrato, reserva y salida |
| **Mudarse** | Organizar pintura/reparaciones, inventario, cajas, fletes y entrega de la vivienda anterior |

[El método completo](docs/process.md) detalla ese recorrido. No todas esas tareas
son servicios automáticos: el host aporta investigación, lectura de documentos,
agenda y razonamiento. La matriz de abajo dice qué está implementado y qué no.

## Un gestor, tres apoyos

No hace falta que coordines tres conversaciones. El gestor prepara lo necesario
para cada especialidad y vuelve con una síntesis: qué sabemos, qué falta, opciones
y próxima decisión.

- **Contador referenciado:** [Monotributo Copilot AR](https://github.com/MatiasJRB/monotributo-copilot-ar)
  para documentación fiscal/facturación. No se instala ni se conecta automáticamente.
  Una factura no prueba que cobraste ni que una agencia acepte un garante.
- **Apoyo legal incluido:** [skill](skills/apoyo-legal-mudanza/SKILL.md) para revisar
  cláusulas con fuentes, riesgos y consultas. No es un abogado matriculado.
- **Apoyo financiero incluido:** [skill](skills/apoyo-financiero-mudanza/SKILL.md)
  para caja, financiación y escenarios con supuestos. No es un banco ni certifica
  capacidad. El helper suma costos por vivienda nueva, vivienda actual y traslado.

Las skills corren con el modelo de tu host. El comando `support` prepara paquetes
mínimos y aritmética limitada; no lanza consultas de IA ni transmite datos.
[Formato, límites y ejemplos](docs/support.md).

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
| Apoyos | Skills legal/financiera incluidas, referencia fiscal externa y paquetes mínimos de consulta; subtotales financieros por tres ejes |

## Qué hace el host y qué queda pendiente

| Capacidad del proceso | Estado real |
| --- | --- |
| Lectura de fuentes y seguimiento registrado | Implementados en CLI local |
| Roles legal/financiero y método de mudanza | Skills incluidas, ejecutadas por el modelo del host |
| Revisión fiscal | Repo externo referenciado; instalación/conexión aparte |
| Búsqueda web amplia, fotos, PDFs, cotizaciones y red de contactos | Trabajo del agente con herramientas autorizadas del host; sin cobertura universal |
| Rutina programada, resumen semanal y notificaciones | Método documentado; scheduler del host, no servicio incluido |
| Agenda, mapas, notas/audio de visita | Depende del host y sus conectores; no integración automática |
| Caja a seis meses, índices, cuotas y contrato | Análisis del agente con fuentes; helper local sólo calcula subtotales, no proyecta ni interpreta normas |
| Expediente documental, checklist de salida e inventario integral | Método para el agente; no módulos persistentes especializados todavía |

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
