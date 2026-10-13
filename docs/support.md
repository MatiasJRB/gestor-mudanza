# Un gestor, apoyos especializados

La persona sigue hablando con el gestor. Éste decide qué revisión necesita,
prepara el contexto mínimo y vuelve con una respuesta integrada. No es necesario
abrir tres conversaciones ni aprender tres herramientas.

## Qué se incluye

| Apoyo | Paquete | Alcance |
| --- | --- | --- |
| Fiscal/contador | Referencia a [Monotributo Copilot AR](https://github.com/MatiasJRB/monotributo-copilot-ar) | Documentación fiscal/facturación; no aprobación de garantías ni prueba de cobro por una factura |
| Legal | `skills/apoyo-legal-mudanza/SKILL.md` | Lectura con fuentes, riesgos, opciones y consultas; no representación profesional |
| Financiero | `skills/apoyo-financiero-mudanza/SKILL.md` | Caja, reservas, medios y escenarios explícitos; no banco conectado ni solvencia certificada |

Las skills necesitan el modelo del host. El gestor puede aplicar los roles en la
misma conversación. Si el host permite delegar y la persona lo autoriza, puede
usar agentes separados; no se presupone esa capacidad ni se lanza una tarea remota.
No se distribuye ni se instala automáticamente el contador. La referencia debe
revisarse e instalarse por separado si la persona quiere usar sus herramientas.

## Paquetes verificables de consulta

```sh
python3 bin/mudanza support --role legal --input examples/support-legal.json
python3 bin/mudanza support --role financial --input examples/support-financial.json
python3 bin/mudanza support --role tax --input examples/support-tax.json
```

`support` prepara un pedido JSON con destino, contexto, fuentes, límites y formato
de respuesta. **No ejecuta una consulta de IA, no transmite ni emite un dictamen.**
Los ejemplos son ficticios. En un caso real, guardar paquetes y resultados sólo
fuera del repo. Un adaptador externo futuro podrá consumir el mismo formato;
no hay integración automática con otros repos o servicios hoy.

### Contrato de entrada

`request`: pregunta concreta. `context`: únicamente el ámbito necesario.
`sources[]`: `id`, `reference`, `observed_at` y opcional `certainty`.

- Legal: jurisdicción, fecha, cláusulas con página/sección, preguntas, acciones
  propuestas y plazos. No enviar saldos o documentos de ingresos por defecto.
- Financiero: moneda, costos, liquidez agregada, obligaciones, reservas, ingresos,
  escenarios, preguntas y cobertura. No incluir identidad del garante si no aporta.
- Fiscal: documentos mínimos, requisitos, preguntas y faltantes. No enviar el
  contrato de vivienda entero si sólo se consulta una constancia fiscal.

El helper omite campos ajenos al rol e informa sus nombres. **No anonimiza los
textos dentro de campos permitidos**: podrían contener datos sensibles. Revisar
contenido y destinatario antes de compartir, con autorización específica. Una
URL o ruta fuente no autoriza a leer todo el directorio ni a enviar el documento.

### Aritmética financiera

Cada costo lleva `id`, `axis` (`new_home`, `current_home`, `moving`), `timing`
(`entry` o `monthly`), `amount`, `currency`, `method` (`cash`, `card`,
`unknown_method`), `certainty` y `source_id` para datos declarados confirmados.
El helper no mezcla monedas ni valida documentos contra un servicio. Sólo suma
los costos declarados confirmados con fuente incluida. Importes estimados y
faltantes quedan en `uncertain_cost_ids`, nunca como ceros confirmados. Separa
entrada por eje/medio y total mensual conocido. No descuenta reservas, evalúa
capacidad, calcula cuotas/índices ni predice ingresos automáticamente.

### Respuesta del especialista

- Hallazgos y evidencia identificable.
- Supuestos separados de datos confirmados.
- Información faltante y cobertura/fecha.
- Opciones y consecuencias, sin decisión por la persona.
- Próximos pasos o mensaje exacto por aprobar.
- Límites de revisión y cuándo consultar a un profesional.

El gestor concilia contradicciones: la cifra contractual, la liquidación de una
agencia y la caja estimada no son la misma fuente. No promedia versiones ni elige
la favorable. Presenta un solo resumen y las decisiones mínimas para avanzar.
