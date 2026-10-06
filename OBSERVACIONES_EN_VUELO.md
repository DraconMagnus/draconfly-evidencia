# Observaciones en vuelo — Draconfly

Este archivo guarda **mediciones hechas antes de la fecha de lectura**, con el
número exacto que dieron el día que se hicieron.

Existe por una razón concreta: mirar a mitad de vuelo es *optional stopping*.
Partir una ventana por la mitad y quedarse con la mitad que confirma lo que uno
sospechaba es la forma más común de convencerse de tocar un modelo que no hacía
falta tocar. No se puede prohibir mirar —a veces hay que hacerlo— pero sí se
puede dejar constancia de **qué se miró, cuándo, y qué se decidió no hacer**.

Nada de lo que está aquí es una lectura. La lectura pre-registrada vive en
`prediction_ledger` y tiene su propia fecha declarada.

Para repetir cualquiera de estas mediciones con los mismos cortes:

```bash
python -m draconfly monitoreo-mitades
```

Los cortes están congelados en `draconfly/monitoreo_mitades.py` y hay una prueba
(`test_los_cortes_no_se_mueven`) que falla si alguien los cambia. Si se mueven,
la comparación contra lo que está escrito abajo deja de existir.

---

## 2026-09-29 — ¿bajaron los HIT?

**Qué disparó la pregunta.** La impresión, mirando el salón de predicciones
acertadas, de que los HIT venían escaseando: 3 el 25, 1 el 26, 1 el 27, 0 el 28.

**Lo que se midió.** La ventana pre-registrada partida en dos mitades iguales de
210 predicciones, cada una contra su propio universo de anclas etiquetadas.

| ventana | HIT | tasa base | lift |
|---|---|---|---|
| 1ª mitad · 08-26 a 09-08 | **18.1%** (38/210) · IC (13.5, 23.9) | 5.4% | +12.6 pp · IC (+8.0, +18.4) |
| 2ª mitad · 09-09 a 09-22 | **12.9%** (27/210) · IC (9.0, 18.1) | 4.8% | +8.0 pp · IC (+4.2, +13.2) |

Y lo mismo contando éxitos (HIT o FAIR), que es lo que alimenta la precisión
publicada:

| ventana | éxitos | tasa base | lift |
|---|---|---|---|
| 1ª mitad | **29.5%** (62/210) · IC (23.8, 36.0) | 10.0% | +19.5 pp · IC (+13.7, +26.0) |
| 2ª mitad | **23.3%** (49/210) · IC (18.1, 29.5) | 9.5% | +13.8 pp · IC (+8.6, +20.0) |

**Las diferencias, con Newcombe al 95%:**

```
HIT    1ª - 2ª:  +5.2 pp  IC (-1.7, +12.2)   el cero esta DENTRO
exitos 1ª - 2ª:  +6.2 pp  IC (-2.2, +14.5)   el cero esta DENTRO
```

### Qué se puede afirmar

**La caída se observó, pero no está establecida.** −5.2 pp con un intervalo que
cruza el cero. Con 210 predicciones por mitad, una caída de ese tamaño sale por
azar con frecuencia suficiente como para no poder distinguirla del ruido. No se
puede decir que el modelo empeoró. Tampoco que no.

**El universo sí se puso más difícil, y eso sí es real.** La tasa base de HIT
bajó de 5.4% a 4.8%, y esa diferencia excluye el cero —IC (+0.1, +1.1)— porque
ahí la muestra son ~12,000 anclas por mitad, no 210. Es una caída chica pero
medible: parte de lo que se ve en pantalla es el mercado, no el modelo.

**La ventaja aguanta en las dos mitades.** Los dos lifts excluyen el cero. En
los últimos 7 lotes, que es el peor tramo del período, la selección da 10.5%
(11/105) contra una base de 4.9%: lift +5.6 pp, IC (+1.0, +12.9). Apenas, pero
afuera del cero.

### Qué se descartó

**No es que el modelo empezara a elegir canales más grandes.** Sería la
explicación mecánica obvia —a mayor base, más difícil el +400%— y es falsa: la
mediana de la base elegida **bajó de 362.4 a 264.0** entre una mitad y la otra.
Eso debería haber hecho el HIT más fácil, no más difícil.

### Qué se decidió

**No tocar nada.** Es lo declarado en el congelamiento vigente, y es lo correcto
aunque la caída fuera real: cambiar el modelo antes de la lectura destruye la
lectura. La lectura sigue siendo el **2026-10-01 al llegar a 450 vencidas, o el
2026-10-08, lo que ocurra primero**.

### Qué revisar el 2026-10-08

1. Correr `python -m draconfly monitoreo-mitades` y comparar las dos primeras
   filas contra las de arriba. **Deben salir idénticas.** Si no salen idénticas,
   algo reclasificó el histórico y hay que averiguar qué antes de leer nada más
   — la vara vigente reclasifica tanto el ledger como las etiquetas.
2. Mirar la tercera ventana, **"después del corte" (desde 09-23)**, que el
   2026-09-29 estaba vacía. Es la única que trae información nueva.
3. Con esa tercera ventana encima, la pregunta se contesta sola: si la caída era
   real, el intervalo de la diferencia se habrá encogido y ya no cruzará el
   cero. Si era ruido, la tercera ventana volverá hacia la primera.

---

## 2026-10-05 — relectura: la caída no continuó, pero el lift sigue encogiéndose

Se corrió la lista de verificación que quedó escrita para el 2026-10-08, tres
días antes. No es una lectura cegada: su punto 1 es una prueba de
reproducibilidad, y correrla antes solo agrega un ensayo. La relectura del 08
sigue en pie y dará **este mismo rango**, porque la tercera ventana quedó
cerrada (ver abajo).

### Punto 1 — reproducibilidad: pasa exacto

Las dos primeras ventanas salieron **idénticas, dígito por dígito**, seis días
después de medirlas y con una mudanza de disco, una reescritura de 11.4 millones
de etiquetas y un truncado de WAL entremedias. Nada reclasificó el histórico.

### Punto 2 — la tercera ventana, que el 29 estaba vacía

| ventana | HIT | tasa base | lift de HIT |
|---|---|---|---|
| 1ª · 08-26 a 09-09 | 18.1% (38/210) | 5.4% | **+12.6 pp** |
| 2ª · 09-09 a 09-23 | 12.9% (27/210) | 4.8% | **+8.0 pp** |
| 3ª · 09-23 a 10-06 | 12.2% (11/90) | 5.4% | **+6.8 pp** |

En éxitos: 29.5% → 23.3% → **25.6%** (23/90), con lift +19.5 → +13.8 → +16.1 pp.

### Punto 3 — qué contesta eso

```
HIT    2ª - 3ª:  +0.6 pp  IC ( -8.6,  +8.0)   cero DENTRO
exitos 2ª - 3ª:  -2.2 pp  IC (-13.4,  +7.8)   cero DENTRO
```

**La caída no continuó.** En éxitos la tercera ventana **subió**, que es la rama
de "era ruido" que el 29 se dejó escrita. En HIT se quedó plana en el nivel bajo,
así que tampoco se recuperó.

**Lo que no se comporta como ruido puro.** El lift de HIT bajó en las tres
ventanas —**+12.6 → +8.0 → +6.8**— mientras la tasa base del universo *volvió a
subir* (5.4 → 4.8 → 5.4). La ventaja se encogió en un universo que se puso más
fácil otra vez. Ningún intervalo de diferencia excluye el cero y n=90 es poco, así
que **nada está establecido**; es la única de las tres señales que merece
seguimiento.

**Los tres lifts siguen excluyendo el cero.** La ventaja aguanta en las tres
ventanas, incluida la más reciente: +1.5 pp de piso en HIT, +8.2 en éxitos.

### Qué se decidió

**No tocar nada**, igual que el 29. Y por un motivo nuevo además del anterior:
la cohorte B arrancó el 2026-10-06, así que cualquier cambio que afecte qué
predicciones se emiten la anula y la reinicia desde cero.

### La fuga que esto destapó

La tercera ventana estaba declarada **abierta hasta 2100-01-01**. Con B
arrancando el 10-06, desde ese día habría empezado a absorber predicciones de B
— y este comando imprime aciertos, tasa y lift de cada ventana. Correr
`monitoreo-mitades` mañana habría revelado resultados parciales de B, que es
justo lo que el punto 8 del protocolo prohíbe.

Es la misma fuga que se tapó hoy en `replicacion.informe()`, por el mismo
motivo: el cegado se implementó donde se estaba mirando y no en los otros
caminos que llegan al mismo dato.

Cerrarla **no alteró lo que se midió**: la tercera ventana leída hoy cubría del
09-23 a hoy, que es exactamente el rango que queda al cerrarla en el 10-06. Se
verificó corriendo el comando antes y después del cambio: 11/90 y 23/90 en los
dos casos.

El tope se expresa como igualdad contra `COHORTE_B_DESDE`, no como fecha escrita
a mano, y una prueba lo exige. Si el arranque de B cambiara, la prueba obliga a
mover el cierre en vez de dejar la fuga abierta en silencio.

---

## 2026-10-06 — El primer lote de YouTube elige videos 19 veces más chicos que la mediana

**Qué disparó la pregunta.** El primer lote de la cohorte de YouTube se emitió
hoy a las 15:25 (ancla `2026-10-06T16:00:00+00:00`). Al revisar que hubiera
quedado bien, saltó que **en 11 de las 15 filas `umbral_exito` y `umbral_hit`
son el mismo número**: 10,000.

**La primera lectura era equivocada.** Parecía que el piso de 10,000 vistas
absorbía al ratio y dejaba las dos varas indistinguibles. En la población no es
así:

```
anclas con horizonte 24 h: 1,978,666

el ratio manda (y no el piso) en:
  HIT  (x5.0):  71.0%      hace falta baseline > 2,000
  FAIR (x3.5):  65.7%      hace falta baseline > 2,857

HIT y FAIR son el MISMO umbral en 34.3% de las anclas
```

Para dos tercios de la población las dos varas son criterios distintos. La vara
no es degenerada.

### Lo que sí es el hallazgo

| | mediana de baseline |
| --- | --- |
| población de anclas | **10,836** |
| el lote emitido hoy | **581** |

**El ranker elige videos 19 veces más chicos que la mediana de la población.**
Y eso tiene una consecuencia mecánica que conviene decir en voz alta: para esos
videos la vara declarada es *más difícil*, no más fácil. Un video en 148 vistas
no necesita crecer ×5 —eso serían 740 vistas—: necesita llegar a 10,000, o sea
**×68**.

### La medición que lo resuelve

Tasa de éxito por banda de baseline, sobre la misma población con que se entrenó
el ranker. Para repetirla con los mismos cortes:

```bash
python -m draconfly youtube-bandas
```

Los cortes están congelados en `draconfly/youtube_bandas.py` y hay pruebas
(`test_cortes_congelados`, `test_el_corte_de_2857_es_donde_colapsan_las_varas`)
que fallan si alguien los mueve. El corte de 2,857 no es redondo: es
`PISO_VISTAS / RATIO_FAIR`, puesto exactamente donde el fenómeno empieza.

| banda de baseline | n | éxito | HIT | % del total |
| --- | --- | --- | --- | --- |
| < 500 | 23,736 | **5.039%** | **5.039%** | 1.2% |
| 500 – 1k | 114,945 | 1.932% | 1.932% | 5.8% |
| 1k – 2.9k | 540,781 | 1.680% | 1.558% | 27.3% |
| 2.9k – 10k | 290,705 | **5.314%** | 3.427% | 14.7% |
| 10k – 50k | 501,338 | 1.268% | 0.759% | 25.3% |
| > 50k | 507,161 | 0.566% | 0.252% | 25.6% |
| **total** | **1,978,666** | **1.879%** | **1.359%** | |

**Elegir chico es correcto.** Los videos por debajo de 500 vistas alcanzan el
criterio **5.04%** de las veces, contra **0.57%** de los de más de 50 mil — nueve
veces más, pese a necesitar ×68 en vez de ×5. En HIT estricto la separación es
de **20×** (5.04% contra 0.25%). Es el efecto de los shorts: lo que explota,
explota desde abajo.

Las dos primeras bandas tienen éxito y HIT **idénticos**, que es la otra cara del
34.3% de arriba: por debajo de 2,000 de baseline el piso manda y las dos varas
colapsan en una.

### Lo que queda sin resolver

La relación **no es monótona**. La banda más fuerte no es la más chica sino
**2.9k–10k, con 5.314%**, y entre 500 y 2.9k hay un valle (1.93% y 1.68%) por
debajo del promedio global.

El lote de hoy cae mayormente en ese valle: **9 de 15 por debajo de 700 vistas**,
y sólo los rangos 10 a 13 (2,309 a 5,900) tocan la banda fuerte.

**Esto no dice que las elecciones estén mal.** La tasa por banda es marginal:
condiciona sólo en el baseline e ignora las otras seis features. Un video de 581
vistas con la firma de velocidad y engagement correcta puede perfectamente batir
a uno de 5,000 sin ninguna. Lo que dice es que **la banda** es débil, no que los
picks lo sean — y eso sólo lo contesta el resultado de la cohorte.

### Qué se decidió

**No tocar nada.** La vara se pre-registró el 2026-10-05 y el ranker el mismo
día; las dos cosas se commitearon antes de emitir una sola predicción. Cambiar
cualquiera de las dos ahora —aunque el cambio pareciera una mejora— destruiría
el pre-registro, que es el único activo que esta cohorte tiene todavía.

La lectura es a las 450 predicciones cerradas, con el horizonte de 24 h: unos 30
días desde hoy.

### Qué revisar al cerrar

1. La tasa de éxito del lote **por banda de baseline**, contra la tabla de
   arriba. Si los picks del valle rinden como el valle, el ranker está pagando
   un precio por elegir chico. Si rinden por encima, las otras features están
   haciendo el trabajo y la tasa marginal no decía nada.
2. Si el `score` separó algo. En este lote va de **0.9958 a 0.9969** —un rango de
   0.0011 entre el primero y el decimoquinto— así que `rank_en_lote` es, en la
   práctica, arbitrario. Es el mismo hallazgo ya anotado para Twitch, pero más
   extremo.
3. Si conviene declarar el piso de 10,000 **relativo a la banda** en la cohorte
   siguiente. Es un cambio de vara, así que no puede entrar a ésta.
