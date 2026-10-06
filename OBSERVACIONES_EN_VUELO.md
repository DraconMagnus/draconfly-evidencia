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
