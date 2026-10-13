# Gestor de mudanza · agente incluido

Para operar una mudanza, leer `skills/gestor-mudanza/SKILL.md` y usar la CLI.
El gestor coordina las skills legal/financiera incluidas y referencia al contador
según docs/support.md, compartiendo sólo el contexto necesario.
El coordinador local es determinista; el host aporta el modelo conversacional.
No se distribuye ningún servicio de IA ni se requieren claves para la CLI.

Para desarrollar, ejecutar los tests y el scanner del README. No cargar instancias
personales, documentos o credenciales para implementar el producto. Fixtures
sintéticas únicamente. No enviar, reservar, pagar ni publicar datos desde tests.
