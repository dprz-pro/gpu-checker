# gpu-checker · RTX 5090 en España

Consulta tiendas españolas, guarda cada precio en SQLite, calcula media/mediana/mínimo
(solo ofertas **en stock**) y genera un informe HTML con gráfico y la tabla de ofertas.
Avisa en consola y en el informe cuando hay una 5090 en stock por debajo de tu precio objetivo.

## Uso
```bash
pip install -e ".[dev]"
python -m gpu check     # consulta, guarda y genera report.html
python -m gpu report    # regenera el informe con lo ya guardado
pytest
```
Configura el precio objetivo y las tiendas en `config.toml`.
Cron (cada 3 h): `0 */3 * * * cd /ruta/gpu-checker && python -m gpu check`

## Estado de las tiendas
| Tienda | Estado |
|---|---|
| LDLC | ✅ verificada con HTML real |
| Alternate | ✅ verificada con HTML real (solo 1ª página, 24 resultados) |
| Amazon.es | ⚠️ parser verificado, pero Amazon responde 503 a menudo; incluye vendedores marketplace |
| Nvidia FE | ❓ **sin verificar**: el formato del API del marketplace es una suposición |
| PcComponentes, Neobyte | ⛔ Cloudflare devuelve 403 a peticiones simples; haría falta navegador real |
| Coolmod, Casemod | ⛔ sin probar (redirección / sin respuesta) |

Los tests usan HTML real guardado en `tests/fixtures/`, así que si una tienda cambia
su web, el scraper falla de forma visible en `check` en vez de dar datos falsos.
