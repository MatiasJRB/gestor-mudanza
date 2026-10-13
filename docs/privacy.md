# Privacidad

Este repositorio se inicia limpio; no es el historial de una búsqueda personal.
No se copiaron chats, contratos, datos de cuentas, teléfono ni domicilios reales.

Guardar instancias reales fuera del checkout público. `.gitignore` es una defensa
adicional, no una auditoría ni garantía. Antes de publicar, revisar TODOS los archivos
versionados y todo el historial; un secreto borrado del último commit puede seguir
accesible en commits anteriores. No incluir capturas privadas o HTML de una sesión.

Los comandos incluidos no usan red, no envían ni modifican el archivo de entrada.
La salida de una consulta real puede contener datos privados. El usuario decide
qué agente y qué conectores acceden a su instancia, con permisos acotados.

## Instancia operativa v0.2

`init` rechaza un workspace dentro del repo y una carpeta no vacía. En POSIX
crea permisos 0700 para carpeta y 0600 para SQLite/tablero. No cifra el estado:
quien tenga acceso a tu usuario/disco puede leerlo. Proteger backups y exports.

El núcleo guarda mensajes que vos registrás, evidencia, resultados de extracción y
un historial transaccional. El export también contiene esos textos. No recolecta
cookies ni credenciales. La comunicación con fuentes es GET público con un
User-Agent identificable; el servidor recibe la URL solicitada y tu IP como en
cualquier consulta web. No registra el HTML completo.

La skill conversacional se ejecuta en el host que elijas: su tratamiento de datos
no lo controla este proyecto. Compartí sólo lo necesario y verificá permisos del
host. La CLI por reglas funciona localmente sin un modelo ni transmisión a IA.
