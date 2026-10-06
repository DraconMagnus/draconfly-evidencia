# Draconfly — evidencia pública

Draconfly predice qué creadores de Twitch van a despegar. Este repositorio
existe para que **no haya que creernos nada**.

Aquí está el registro encadenado por hash de cada predicción emitida y cada
resultado medido, más el script que lo verifica. Es la respuesta a la única
pregunta que importa cuando alguien enseña sus aciertos: *¿cómo sé que no
escribiste eso después de ver el resultado?*

## Verifícalo tú mismo

No hay que instalar nada. Solo Python 3.

```bash
python verificar.py
```

El script no importa una sola línea de Draconfly. Está escrito así a propósito:
un verificador que dependa del código del verificado no verifica nada.

Hace cuatro cosas:

1. **Recalcula la cadena entera.** Cada evento incluye el hash del anterior.
   Alterar un evento viejo cambia su hash, lo que invalida el `prev` del
   siguiente, y así hasta el final del archivo. No se puede editar el pasado
   sin reescribir todo lo posterior.
2. **Recuenta los resultados** bajo cada vara declarada. Los umbrales
   (+400%, 250 espectadores) los lee del propio evento `rule_change`, no de una
   copia en el script. O sea que tampoco hay que creerle al verificador.
3. **Reconstruye la cifra que publicamos** — 450 predicciones, 120 éxitos,
   26.7% — desde el archivo, sin tocar ninguna base de datos.
4. **Imprime el histórico completo**, incluido el tramo que sale peor.

## La cifra

En la cohorte A — 450 predicciones emitidas entre el 2026-08-26 y el
2026-09-24, cerradas y medidas siete días después de cada una:

| | |
| --- | --- |
| aciertos (HIT o FAIR) | **26.7%** · 120 de 450 |
| tasa base del mismo período | **9.79%** |
| lift | **+16.9 pp**, IC95 **(+11.9, +21.8)** |
| razón | **2.72×** |

El intervalo es por bootstrap de conglomerados sobre creadores — 20,000
muestras, semilla 20261001 — porque las 450 predicciones cayeron sobre 261
creadores y no son 450 ensayos independientes. El piso defendible del lift es
**+12.0 puntos**.

La vara: **HIT** = creció +400% o más y llegó a 250 espectadores o más.
**FAIR** = creció +250% o más y llegó a esos mismos 250. **ÉXITO** = HIT o FAIR,
y es el criterio pre-registrado al que corresponde el 26.7%.

## El número que no te vamos a esconder

Si corres `verificar.py` vas a ver que el archivo completo da **20.7%**, no
26.7%. No es una contradicción y no queremos que lo descubras tú:

| tramo | n | éxitos | tasa |
| --- | --- | --- | --- |
| antes del congelamiento (< 2026-08-26) | 481 | 71 | **14.8%** |
| **cohorte A** (08-26 a 09-24) | 450 | 120 | **26.7%** |
| posteriores a A (≥ 09-25) | 60 | 14 | 23.3% |

El primer tramo es peor **a propósito**: son predicciones emitidas mientras el
pipeline todavía se estaba cambiando — los pesos se congelaron el 2026-07-26,
el piso de audiencia y el Top 400 el 2026-08-01, el modelo el 2026-08-06, la
vara el 2026-08-27. Medir un sistema con las predicciones que hizo mientras lo
estabas ajustando no mide el sistema.

Por eso la cohorte A empieza el 2026-08-26, veinte días después de congelar el
modelo. La vara es el caso que hay que mirar de cerca: se fijó el **2026-08-27,
un día después** de que A arrancara. Lo que la salva no es el calendario sino el
horizonte — cada predicción se mide siete días más tarde. **El primer resultado
de la cohorte A se registró el 2026-09-02**, seis días después de que la vara
quedara declarada en la cadena. Las dos fechas están en el archivo y las puedes
comprobar: la vara se eligió sin poder ver a quién iba a favorecer, y quedó
escrita en `METODOLOGIA_CAMBIOS.md` antes de aplicarse.

La ventana de A se declaró en el código antes de leer su resultado, y ese commit
tiene fecha.

## Qué prueba esto, exactamente

**Que el archivo no fue alterado.** La cadena de hashes lo garantiza por
construcción, y lo compruebas tú corriendo el script.

**Que las predicciones existían antes de conocerse su resultado.** Esta parte
no la prueba el hash: la prueba el reloj de GitHub. El archivo se sube después
de cada lote, dos veces al día, y GitHub fecha cada push con su propio reloj,
que no controlamos. Una predicción fechada el 6 de agosto que aparece en un
push que GitHub certifica como subido el 6 de agosto no pudo escribirse el 13.

**Que los números publicados salen de los datos.** `verificar.py` reconstruye
el 26.7% desde el archivo. Si no coincidiera, el script lo diría.

## Qué NO prueba

Decir esto es la mitad del punto.

**La cadena solo cubre lo que pasó desde que existe.** Su primer evento se
registró el 2026-08-06. Las predicciones anteriores a esa fecha —emitidas desde
el 2026-07-05— entraron con la fecha en que se incorporaron, no con una prueba
independiente de su fecha de emisión. Presentarlas como demostradas sería justo
el tipo de afirmación que este repositorio existe para hacer innecesaria. Son
las del tramo de 14.8%, y no forman parte de ninguna cifra que publiquemos.

**La tasa base de 9.79% no está aquí.** Se calcula sobre el panel completo de
~3,090 creadores vigilados cada hora, que no es público. El `26.7%` lo
verificas; el `9.79%` contra el que se compara, no — esa parte hay que
auditarla aparte, con acceso a los datos.

**El fechado por push anterior a hoy vive en el repositorio privado.** Este
repositorio público se creó el **2026-10-06**, así que GitHub certifica que
*todo lo anterior se subió aquí hoy*. El historial de push lote por lote está
en el repositorio de desarrollo, privado, y es auditable dando acceso. De hoy
en adelante, cada lote se publica también aquí y el fechado es público.

**Una cadena verificable no hace cierta una predicción.** Prueba que no se
reescribió, no que el método sea bueno. Para eso está la réplica.

## La réplica

Una cohorte de un mes no distingue *"el sistema funciona"* de *"ese mes era
predecible"*. La cohorte B arrancó el **2026-10-06** con el pipeline congelado
y se lee a las 450 predicciones cerradas, hacia mediados de noviembre.

Está **cegada**: no se miran resultados parciales. Lo que se declaró antes de
empezar —ventana, tamaño, vara, umbrales— está en `METODOLOGIA_CAMBIOS.md` con
su fecha de commit.

## Los archivos

| archivo | qué es |
| --- | --- |
| `ledger_chain.jsonl` | la cadena. Un evento por línea: `prediction`, `outcome`, `rule_change` |
| `MANIFEST.json` | conteos y último hash, para comparar de un vistazo |
| `verificar.py` | el verificador independiente |
| `docs/seleccion-de-creadores.md` | cómo se eligen los 15 creadores diarios, con los pesos exactos |
| `METODOLOGIA_CAMBIOS.md` | bitácora de cada decisión metodológica, con fechas |
| `OBSERVACIONES_EN_VUELO.md` | lo que se está observando y todavía no concluye |

### El formato de la cadena

```json
{"seq": 0, "event": "prediction", "recorded_at": "...", "prev": "000...0",
 "data": {...}, "hash": "3348a8..."}
```

El hash es `sha256` sobre `{seq, event, recorded_at, data, prev}` serializado en
JSON canónico: `sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=False`,
UTF-8. El `prev` del primer evento son 64 ceros.

Un evento nunca se modifica. Una predicción que hoy se emite y en siete días se
evalúa genera **dos eventos separados** que se agregan al final — si se
rellenara la fila original, la cadena se rompería, y *"tuvimos que regenerar la
cadena"* es indistinguible de haber manipulado los datos.

Lo mismo con las varas: cuando el 2026-08-26 se descubrió que la vara original
marcaba como acierto lo que le pasa al canal mediano en una semana normal, **no
se reescribió ningún resultado**. Se agregó un evento `rule_change` declarando
la vara nueva y el motivo, y cualquiera recalcula el histórico aplicándola. Las
dos varas están en el archivo y `verificar.py` recuenta bajo las dos.

## Qué cambia por publicar esto

Publicar quince nombres al día les manda audiencia, y audiencia hace crecer a un
creador. O sea que a partir de ahora parte del crecimiento que midamos lo
causamos nosotros, y un acierto deja de ser solo un acierto.

Draconfly mide eso en vez de ignorarlo: desde el **2026-10-06** se registran
cada día quince predicciones más que **no se publican**, escogidas por el mismo
sistema y justo debajo del corte. Si las publicadas crecen más que esas, la
diferencia es el efecto de publicar. Si crecen igual, el efecto no existe.

Esa tabla ciega se abre cuando cierre, no antes.

---

Código y datos: privados. Preguntas y auditorías: abran un issue.
