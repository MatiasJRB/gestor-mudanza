# Gestor de mudanza

![Gestor de mudanza: tu agente ordena la búsqueda, vos decidís](docs/demo/cover.svg)

**Volvé a tu búsqueda sin tener que recordar qué quedó pendiente.**

Un núcleo local para que un agente organice viviendas, conversaciones y costos.
Vos elegís qué te gusta, qué mensaje se envía y cuándo asumir un compromiso.

[Ver la demo ficticia](docs/demo/index.html) · [Cómo usarlo con un agente](docs/agent-interface.md) · [Privacidad](docs/privacy.md)

> **Estado: experimental.** No hay servicio alojado ni
> agente incluido. La demo muestra resultados del núcleo sobre datos inventados;
> no consulta avisos ni manda mensajes.

## Qué se siente usarlo

Le decís a tu agente:

> «Retomemos la mudanza. Mostrame qué nos toca responder y qué plata falta
> confirmar. Prepará los mensajes juntos, pero no envíes nada.»

El agente consulta el archivo local y te devuelve una tanda con contexto,
próximo paso y texto para revisar. Este proyecto aporta los estados y las cuentas;
la conversación y las integraciones las pone el agente que uses.

| Tu pregunta | Lo que aporta el núcleo |
| --- | --- |
| ¿Esta vivienda está confirmada? | Separa aviso, confirmación de unidad y descarte. Hasta una confirmación debe revalidarse. |
| ¿Ya mandamos ese mensaje? | Distingue borrador, envío con recibo y respuesta por revisar. |
| ¿Cuánto necesito? | Separa efectivo, tarjeta, medio desconocido e importes faltantes por moneda. No evalúa solvencia. |

## Probalo en un minuto

Desde la carpeta del proyecto, con **Python 3.9 o posterior**. No instala paquetes,
no pide cuenta ni usa red:

```sh
python3 bin/mudanza validate --input examples/demo.json
python3 bin/mudanza status --input examples/demo.json
python3 bin/mudanza costs --input examples/demo.json --currency ARS
```

En la muestra ficticia vas a encontrar:

- Una casa pendiente de tu filtro visual: su aviso no prueba disponibilidad.
- Un departamento descartado: no vuelve al pool activo.
- Un mensaje preparado: sigue sin enviarse.
- ARS 100.000 en efectivo, ARS 30.000 en tarjeta y traslado sin importe.

Los importes son ejemplos, no precios de mercado. La suma está incompleta.
Abrí `docs/demo/index.html` para ver esta misma salida en una portada legible.

## Usalo con tu agente

1. Mantené tu archivo real **fuera de este repositorio**. La estructura está en
   `examples/demo.json` y en [la interfaz v1](docs/agent-interface.md).
2. Dale a tu agente acceso acotado al archivo y a la CLI. Puede ser cualquier
   runtime que lea archivos y ejecute Python; no requiere una marca o suscripción.
3. Usá el [prompt de operación](docs/agent-interface.md#prompt-de-operación).
   Pedile contexto, mensajes completos y accesos a los hilos en una sola tanda.
4. Aprobá cada acción externa por destinatario y texto. El núcleo no envía.
   Tu runtime debe verificar el recibo antes de registrar un envío.

No pegues contratos, chats o credenciales en un issue ni en la demo.

## Incluido y pendiente

**Funciona hoy:** CLI JSON de sólo lectura, estados por vivienda y conversación,
sumas decimales por moneda/medio, fixture sintética y tests. Los comandos no
modifican tu entrada ni llaman servicios externos.

**No está implementado:** scrapers, conectores de WhatsApp/Gmail/Calendar/bancos,
agente embebido, scheduler, cálculo de 48 horas hábiles, alertas, envío de mensajes,
cuotas, proyección de ingresos, reserva ni cálculo legal de rescisión. El campo
`review_at` se conserva; no dispara recordatorios. La demo no es un panel operativo.

El runtime tiene que leer ambos lados de cada conversación y obtener evidencia
reciente. Una suma no demuestra que puedas mudarte. Tarjeta y descubierto no son
ahorro. Asuntos legales y financieros necesitan la revisión correspondiente.

## Desarrollo y verificación

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_demo.py
python3 scripts/check_public_bundle.py
```

`build_demo.py` regenera la demo desde la fixture y el núcleo. El último comando
revisa el conjunto candidato a distribuir, incluidas rutas y patrones sensibles;
no sustituye la revisión humana ni audita repositorios ajenos o archivos ignorados.

[Reglas de privacidad](docs/privacy.md) · [Contrato de datos y salidas](docs/agent-interface.md)

Licencia MIT. Sin asesoramiento jurídico, inmobiliario ni financiero.
