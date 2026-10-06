# Registro de cambios de metodología — Draconfly

Este archivo documenta **únicamente los cambios que movieron los números
publicados** en el tablero (precisión de predicción e índice de confiabilidad),
con la fecha en que ocurrieron, qué se cambió exactamente, y qué se puede
afirmar con honestidad después del cambio.

Existe para que cualquiera —un inversionista, un socio, o nosotros mismos en
seis meses— pueda comparar dos capturas de pantalla separadas en el tiempo y
entender por qué un número subió o bajó, sin tener que confiar en la memoria de
nadie.

Los cambios de interfaz, traducción, rendimiento o infraestructura **no** se
listan aquí salvo que hayan alterado lo que el tablero mostraba.

Al final hay una segunda sección, **Compromisos abiertos**, para instrumentación
que todavía no mueve ningún número pero que sí compromete cómo se van a mover en
el futuro. Se separa a propósito: mezclar lo que ya pasó con lo que prometimos
haría este archivo menos útil para auditar.

---

# Cambios que movieron los números

## 2026-08-01 — HIT exige audiencia real, no solo porcentaje

**Commit:** `07059f7`

**Qué encontramos.** Al revisar 105 predicciones ya evaluadas, la probabilidad
que el modelo emitía estaba **inversamente correlacionada** con el acierto:

| probabilidad emitida | acierto real |
|---|---|
| 31.7% (la más baja) | 96.2% |
| 76.1% (la más alta) | 28.0% |

**Causa.** 63 de esas 105 predicciones eran de creadores con menos de 5 viewers
promedio. HIT se definía solo como "creció ≥100%", sin exigir a dónde llegó.
Para un canal de 2 viewers, doblar significa llegar a 4 — trivial y sin valor
comercial. El modelo estaba ordenando bien; la vara de medición medía otra cosa.

**Cambio A → B.**

- **Antes:** `HIT = crecimiento ≥ 100%`
- **Después:** `HIT = crecimiento ≥ 100%` **Y** `pico ≥ 100 viewers`
- Se añadió el resultado `growth_below_audience` para el caso "creció mucho pero
  nunca alcanzó audiencia útil", en vez de llamarlo *crecimiento leve* (falso) o
  *acierto* (exagerado).

**Cambio en el pipeline (mismo día, igual de importante).**

- **Antes:** `record-predictions` tomaba los 15 mejores candidatos sin importar
  su tamaño.
- **Después:** descarta candidatos con menos de 50 viewers promedio y evalúa un
  universo mucho más amplio para llenar el lote.

Justificación medida: predicciones sobre creadores por debajo de 50 viewers
acertaban **4.1%**; las de 50 o más, **48.4%** (con la vara corregida).

**Cómo se modificó el tablero.**

| indicador | antes | después |
|---|---|---|
| Precisión de predicción | 58.5% | 16.2% |
| Índice de confiabilidad | 46.0 ▲ +41.2% | 9.3 ▼ −16.3% |
| Calibración: prob. alta | 29.6% | 29.6% |
| Calibración: prob. baja | 57.7% | 5.1% |

Composición del lote diario, antes y después del filtro:

| lote | base mínima | base promedio |
|---|---|---|
| 2026-07-31 (sin filtro) | 1.0 viewers | 2.2 |
| 2026-08-01 (con filtro) | 76.2 viewers | 1,763 |

**Qué transparencia permite.** Que "acierto" signifique una sola cosa
verificable: *el creador dobló su audiencia y llegó a un tamaño que una marca
puede patrocinar*. Antes, el número publicado estaba dominado por canales de 1 a
5 viewers, y las predicciones en las que el sistema decía tener más confianza
eran justamente las que peor funcionaban — algo que cualquiera que abriera los
datos habría encontrado.

**Nota sobre la caída.** El 16.2% refleja historial acumulado bajo el criterio
viejo (predicciones sobre creadores diminutos). Las predicciones emitidas a
partir de esta fecha usan el filtro nuevo; el acierto histórico del modelo sobre
creadores de tamaño relevante es **29.0%**, y hacia ahí debería converger el
número conforme el historial viejo se diluya.

---

## 2026-07-27 — Los fallos volvieron a ser visibles

**Commit:** `488a447`

**Qué encontramos.** La sección "Cola de verificación" ordenaba con los aciertos
primero y mostraba solo 20 filas, con un presupuesto de consulta compartido de
50. Cuando los aciertos crecieron a 29, **las predicciones fallidas dejaron de
aparecer en cualquier parte del tablero**, y FAIR/MINOR se mostraban incompletas.

**Cambio A → B.**

- **Antes:** una sola consulta con límite 50, ordenada por acierto primero.
- **Después:** consulta dedicada (`load_investor_non_hit_evaluated`) con su
  propio presupuesto, más una sección explícita de *Predicciones fallidas*.

**Cómo se modificó el tablero.** Apareció la sección de fallos (4 predicciones
MISS que estaban ocultas). FAIR pasó de mostrar 3 de 9 a las 9 completas; MINOR
de parcial a las 14 completas.

**Qué transparencia permite.** Que el historial muestre los fallos con el mismo
detalle que los aciertos, por diseño y no por casualidad. Un registro de
precisión que solo enseña sus éxitos no es un registro de precisión.

---

## 2026-07-27 — Breakouts reales dejaron de descartarse como "sin señal"

**Commit:** (incluido en el trabajo de reclasificación de ese día)

**Qué encontramos.** Una predicción se descartaba como `insufficient_baseline`
("N/D", excluida del cálculo de precisión) si el creador **partía** de menos de 5
viewers, sin importar a dónde llegara. Eso descartaba casos como pasar de 2 a 36
viewers (+1,276%), que son exactamente los despegues que el producto busca
detectar.

**Cambio A → B.**

- **Antes:** se descartaba si `base < 5`.
- **Después:** se descarta solo si `base < 5` **Y** `pico < 5` — es decir, si
  ambos extremos siguen siendo ruido.

**Cómo se modificó el tablero.** 13 predicciones pasaron de "N/D" a HIT o FAIR.
La precisión publicada subió de **29.4% a 44.7%**.

**Advertencia honesta, en retrospectiva.** Este cambio corrigió un error real,
pero casi todas las predicciones que rescató eran de creadores diminutos, así
que empujó la muestra hacia ese sesgo y **contribuyó a la calibración invertida
que se detectó y corrigió el 2026-08-01**. Se documenta aquí porque el registro
sirve poco si solo anota los aciertos de quien lo escribe.

---

## 2026-08-01 — El tablero mostraba datos de hace 4 días

**Commits:** `e1a402f`, `8cd017a`

**Qué encontramos.** Los indicadores del encabezado no leen el ledger
directamente: leen un caché materializado. Ese caché tenía fecha del
**2026-07-28**. La tarea horaria sí corría, pero refresca siete cosas en
secuencia y el índice de atención es la cuarta; las corridas se cortaban antes de
llegar.

**Causa raíz.** El archivo WAL de SQLite había crecido a **8.1 GB** (contra una
base de 12.6 GB). SQLite hace *checkpoint* automáticamente, pero sin
`journal_size_limit` el archivo nunca devuelve el espacio: se queda en su marca
máxima. Cada conexión nueva tenía que recorrerlo antes de hacer nada, lo que
volvía lento todo el sistema (una consulta del analizador llegó a tardar 16
horas).

**Cambio A → B.**

- **Antes:** sin `journal_size_limit`; el WAL solo podía crecer.
- **Después:** `journal_size_limit = 256 MB` en todas las conexiones, más un
  *checkpoint* explícito en la tarea diaria de archivado.
- Se añadió vigilancia del tamaño del WAL al `health-check` (alerta a 500 MB,
  crítico a 2 GB), porque nada lo estaba observando — esa es la única razón por
  la que llegó a 8 GB.
- Se añadió el índice compuesto `(topic, source, observed_at, phrase)` que le
  faltaba a la consulta del analizador.

**Cómo se modificó el tablero.** Los indicadores volvieron a reflejar el estado
real. Contar las filas de un tema pasó de agotar 280 s a **0.1–0.4 s**.

**Qué transparencia permite.** Que los números del encabezado correspondan a los
datos de hoy y no a los de hace cuatro días. Un indicador congelado es peor que
uno bajo: parece vivo y no lo está.

---

## 2026-08-03 — No hubo lote de predicciones: el día se perdió

**Qué pasó.** El lote diario del **3 de agosto de 2026 no existe**. No se
atrasó ni se registró parcialmente: no se emitió ninguna predicción ese día. El
historial salta del lote del 2 de agosto (vence el 9) al del 4 de agosto (vence
el 11).

**Causa inmediata.** La tarea `Draconfly Record Predictions` corrió a las 21:40
y murió con `sqlite3.OperationalError: database is locked`. Los tres reintentos
automáticos, separados 15 minutos, murieron igual.

**Causa raíz.** Una corrida de `refresh-market-signals` se quedó colgada
reteniendo la conexión a SQLite. La tarea tenía `ExecutionTimeLimit = PT72H`
—el valor por omisión de Windows— así que el sistema tenía permiso de dejar ese
proceso vivo **tres días**, y con `IgnoreNew` cada disparo horario siguiente
simplemente devolvía "ya hay una instancia corriendo". El 4 de agosto se observó
el mismo patrón en vivo: un proceso arrancado a las 04:55 seguía ahí a las 11:20,
con 145 segundos de CPU acumulados en 6.5 horas —esperando, no trabajando— y
bloqueando a todo lo demás.

**Corrección a lo que escribimos el 2026-08-01.** En la entrada anterior
atribuimos el WAL de 8.1 GB únicamente a la falta de `journal_size_limit`. Eso
era incompleto. Un *checkpoint* de SQLite necesita que ningún otro proceso tenga
el archivo abierto; un proceso colgado impide el checkpoint por sí solo, sin
importar cómo esté configurado el límite de tamaño. El WAL gigante y el lote
perdido no eran dos problemas: eran dos síntomas del mismo proceso colgado.
`journal_size_limit` era necesario pero no suficiente.

**Por qué no se rellenó.** Se podía generar el lote faltante en cualquier
momento del 4 de agosto. **No se hizo, deliberadamente.** Una predicción emitida
con fecha del 3 de agosto pero calculada el 4 se escribe conociendo parte del
período que dice predecir. Un registro de precisión que admite eso no mide nada.
El hueco del 3 de agosto es real y se queda, igual que los del 22 al 24 de julio.

**Cambio A → B.**

- **Antes:** `ExecutionTimeLimit` por omisión (72 h) en *Market Signals
  Refresh*, *Record Predictions* y *Evaluate Predictions*.
- **Después:** 45 min, 1 h y 2 h respectivamente — siempre por debajo del
  intervalo de su propio disparador, de modo que una corrida colgada muera antes
  de que llegue la siguiente.
- **Antes:** los tres reintentos de `record-predictions` ocurrían la misma
  noche, con 15 minutos de separación.
- **Después:** se añadió un segundo disparador a las **05:30**, después de la
  ventana de mantenimiento de las 04:40. Reintentar en las mismas condiciones
  congestionadas no iba a funcionar —no funcionó—; reintentar con el WAL recién
  truncado y sin nadie más escribiendo es un intento genuinamente distinto. El
  lote llega ~8 horas tarde en vez de nunca.
- Para que ese segundo disparador no produzca lotes dobles, `record-predictions`
  aceptó `--min-gap-hours` (20 por omisión) y no registraba nada si el último
  lote era más reciente que eso. **Este guard se reemplazó al día siguiente;
  ver la entrada del 2026-08-05.**

**Cómo se modificó el tablero.** "Predicciones en curso" no muestra ningún lote
emitido el 3 de agosto, y no lo mostrará nunca. El total de predicciones
evaluables será 15 menor de lo que habría sido.

**Qué transparencia permite.** Que un hueco en el historial sea visible como
hueco. La alternativa —rellenarlo después— habría dejado el tablero completo y
el registro sin valor.

---

## 2026-08-05 — Se publica la cohorte del sistema actual junto al histórico

**Commit:** `d763a1b`

**Qué encontramos.** El número publicado, 27.3%, no describía un sistema: era
el promedio de dos que no tienen nada que ver.

| Cohorte | Evaluables | Éxitos | Precisión |
|---|---|---|---|
| baseline **< 50** viewers | 61 | 6 | **9.8%** |
| baseline **≥ 50** viewers | 38 | 21 | **55.3%** |

Las 61 de la primera fila no son predicciones malas. Son predicciones que el
pipeline **ya no emite** desde el 1 de agosto, cuando `record_decision_predictions()`
empezó a descartar candidatos por debajo de 50 viewers promedio. Esa parte del
historial mide un producto retirado.

**Cambio A → B.**

- **Antes:** una sola cifra de precisión, mezclando ambas cohortes.
- **Después:** dos cifras, ambas visibles y etiquetadas — *Precisión de
  predicción* (histórico completo) y *Precisión del sistema actual* (solo
  baseline ≥ 50), cada una con su índice de Wilson.

**Qué NO cambió, y es lo importante.**

- La vara de HIT y FAIR es **idéntica**: ≥100% y ≥50% de crecimiento, ambas
  exigiendo un pico de al menos 100 viewers.
- **Ni una sola predicción fallida se excluye.** La cohorte del sistema actual
  incluye todos sus fracasos; simplemente no incluye predicciones que hoy no se
  emitirían.
- **Nada se borra ni se recalifica.** El histórico completo se sigue publicando,
  al lado y con el mismo tamaño.
- El número no se calcula desde el caché materializado sino en vivo desde
  `prediction_ledger`, porque ese caché se quedó congelado dos días (mostraba
  25.3% cuando el valor real era 27.3%). Una cifra que se presenta como
  auditable no puede depender de que una tarea horaria haya sobrevivido la
  noche.

**Cómo se modificó el tablero.** Dos tarjetas nuevas en el encabezado del
Investor Demo, más una nota al pie que explica la diferencia entre las dos
cifras y declara cuántas predicciones del sistema actual siguen sin vencer (63
al momento de escribir esto).

**Qué transparencia permite.** Que se pueda responder "¿qué tan bueno es esto
*hoy*?" sin esconder de dónde viene. Es la misma distinción que hace un fondo
al reportar resultados desde un cambio de estrategia: ambas series a la vista.
Publicar solo el 55.3% sería mover la portería; publicar solo el 27.3% describe
un pipeline que ya no existe.

**Advertencia registrada por adelantado.** De las 105 predicciones pendientes,
42 son de la cohorte vieja y vencen primero, entre el 6 y el 8 de agosto. Es
probable que el histórico **baje antes de subir**. Se deja escrito aquí, antes
de que ocurra, para que la caída no se pueda presentar después como otra cosa.

---

## 2026-08-05 — El lote diario ahora se define por día, no por horas

**Qué pasó.** El 5 de agosto no hubo lote hasta que se forzó a mano. Ninguna
tarea falló: el Task Scheduler reportó éxito en todas.

```
Wed 08/05/2026  5:30:02  Sin cambios: ya hay un lote de hace 19.5 h.
```

**Causa.** El guard puesto el día anterior exigía 20 horas de separación entre
lotes. El lote del 4 de agosto se escribió a mano a las 10:00 en vez de las
21:40 habituales, así que a las 05:30 del día 5 tenía 19.5 horas — media hora
por debajo del umbral. El disparador se abstuvo, correctamente según su propia
regla, y el siguiente no llegaba hasta las 21:40. **Dos corridas se comportaron
exactamente como estaban especificadas y el ledger pasó ~36 horas sin lote.**

La regla medía "al menos 20 horas de separación". Lo que se quería era "uno por
día". No son lo mismo, y la diferencia solo se nota cuando un lote cae fuera de
horario — que es justo lo que había pasado.

**Cambio A → B.**

- **Antes:** `--min-gap-hours 20`, guard por antigüedad del último lote.
- **Después:** un lote por **día calendario local**. Un lote fuera de horario ya
  no empuja al siguiente; simplemente satisface su propio día. `--allow-same-day`
  lo omite para corridas manuales deliberadas.
- **Antes:** 21:40 principal, 05:30 respaldo.
- **Después:** **05:30 principal**, 21:40 respaldo. Las 05:30 caen justo después
  de la ventana de mantenimiento, con el WAL recién truncado y sin colectores
  escribiendo — el momento más tranquilo del día para la base, y lo contrario de
  las condiciones en que murió la corrida del 3 de agosto.

**Día local, no UTC:** "un lote al día" es una promesa hecha a una persona
mirando un tablero en su propia zona horaria.

**Cómo se modificó el tablero.** El 5 de agosto tiene su lote
(`2026-08-05T16:00`, vence el 12). El 3 de agosto sigue vacío y así se queda.

**Qué transparencia permite.** Que la regla publicada —"cada día se emite un
nuevo set de predicciones"— sea la regla que el código realmente aplica. La
anterior era una aproximación que fallaba exactamente cuando más importaba.

---

## 2026-08-06 — Se retira el pronóstico de crecimiento: estaba invertido

**Qué encontramos.** Revisando por qué el "Error medio" del Accuracy Report
marcaba **205.55%**, apareció algo peor que una métrica mal calculada.

Sobre la cohorte actual (41 predicciones evaluadas, baseline ≥ 50):

| Medición | Valor |
|---|---|
| Correlación entre crecimiento pronosticado y real | **r = −0.308** |
| Aciertos (HIT o FAIR) | 23 |
| …de esos, con pronóstico **negativo** | **10 (43.5%)** |

`predicted_growth_pct` no es impreciso: está **anticorrelacionado**. En 10 de
nuestros 23 aciertos, nuestro propio número decía que el creador iba a encoger.

```
viperriven247   pronosticado -20.3%   real +2202.8%   -> hit_strong
ltdigilusion    pronosticado  -8.8%   real +1386.5%   -> hit_strong
```

**Y la métrica además estaba mal calculada:** incluía `insufficient_baseline`
—los canales diminutos que ya excluimos de la precisión— y usaba `coalesce(...,
0)` para datos faltantes. Corregida daba **315.9** puntos porcentuales en vez de
205.6. Más honesta y aún más confusa junto a una precisión del 27%, porque miden
cosas distintas.

**Qué NO invalida esto.** El registro de aciertos sigue en pie. HIT mide si el
creador que **seleccionamos** despegó, y eso funciona: 55.3% en la cohorte
actual. Son dos afirmaciones distintas y solo una está respaldada:

- *"Identificamos creadores que van a despegar"* → **respaldado**
- *"Pronosticamos cuánto van a crecer"* → **no**, va al revés

**Cambio A → B.**

- **Antes:** el Accuracy Report mostraba "Error medio"; la gráfica de replay
  dibujaba una línea de "meta pronosticada"; el desglose de "¿por qué?"
  calculaba su componente de novedad a partir del crecimiento pronosticado.
- **Después:** las tres cosas fuera. La novedad ahora se deriva de la audiencia
  base —cuanto más chico el canal, más pesa la novedad frente a su historial—,
  que es lo que la palabra significa.
- La gráfica conserva la línea del **baseline**, que es un hecho medido y no un
  pronóstico.

**Lo que sí se conserva, a propósito.** `predicted_growth_pct` sigue en
`prediction_ledger` y sigue en la cadena pública `public/ledger_chain.jsonl`.
Esa cadena es un registro de lo que hicimos, no una superficie comercial:
borrarle un campo que resultó poco fiable sería exactamente el tipo de gesto que
la cadena existe para hacer imposible. Queda como constancia de que lo
calculamos y de que dejamos de sostenerlo.

**Cómo se modificó el tablero.** El Accuracy Report pasa de cinco indicadores a
cuatro. Desaparece un "205.55%" que un inversionista leería, con razón, como
*"sus predicciones se equivocan por 200%"*.

**Qué transparencia permite.** Que lo que se publica sea lo que se sostiene. La
alternativa —dejar el número visible y explicarlo cada vez— era pedirle al
interlocutor que confiara en una distinción que la pantalla contradecía.

---

## 2026-08-06 — El filtro funciona; el ranking todavía no está demostrado

**De dónde salió.** De una pregunta directa: *¿las predicciones se toman al
azar?* No — cada día se puntúan ~400 candidatos, se descartan los de menos de 50
espectadores y **se emiten los 15 mejores por puntaje**. Es una selección
deliberada de la cima. Justamente por eso hay que comprobar si esa cima rinde
más que el resto.

**Qué encontramos.**

| | Casos | Acierto | IC 95% |
|---|---|---|---|
| Universo elegible (cualquier candidato ≥ 50) | 8,456 | **56.3%** | 55.2 – 57.3% |
| Nuestra selección (los 15 mejores) | 41 | **56.1%** | 41.0 – 70.1% |

Diferencia: **−0.2 puntos porcentuales**. El intervalo de nuestra selección
**contiene** la tasa base: son estadísticamente indistinguibles.

**Qué significa, separando las dos partes del sistema.**

- **El piso de audiencia SÍ funciona.** Es lo que llevó el acierto de 9.8% a
  56%. Valor demostrado.
- **El ranking no ha demostrado nada todavía.** Ordenar por puntaje y tomar los
  15 mejores rindió igual que tomar 15 cualesquiera del grupo ya filtrado.

**Por qué era esperable.** Las 41 predicciones evaluadas se emitieron **todas
antes del 6 de agosto**, con el modelo entrenado para "breakout en 6–24 horas".
Ya habíamos medido que su probabilidad correlacionaba con el acierto real a
**r = −0.204**. Este resultado lo confirma desde el lado de los resultados: no
aportaba. El modelo de horizonte de 7 días se activó el 6 de agosto y en
backtest da 76.8% en el decil superior contra esa base de 56.3%.

**Cambio A → B.**

- **Antes:** el tablero mostraba "Precisión del sistema actual: 56.1%" sin nada
  contra qué compararla.
- **Después:** la nota al pie declara la tasa base del universo elegible junto a
  esa cifra, y dice explícitamente que el aporte del ranking no está probado con
  predicciones vencidas.

Va pegada a la cifra y no en un panel aparte a propósito: separarlas invita a la
lectura que los datos no sostienen —*"el modelo acierta 56 de cada 100"*— que le
da crédito a la parte del sistema que todavía no lo ha ganado.

**Qué transparencia permite.** Que la pregunta *"¿su modelo le gana al azar?"*
tenga una respuesta preparada y verificable: *el filtro sí, el ranking aún no
está demostrado, y el primer veredicto llega el 13 de agosto*. Es una afirmación
más débil que un 56.1% a secas, y es la que se sostiene.

---

## 2026-08-27 — Se aplica la vara nueva, y una columna se queda atrás

**Commits:** `be1409b` (se aplica la vara), `3f46ee5` (la tasa base llega a la
pantalla), `39dc1a0` (HIT estricto y reparación de las etiquetas)

Este es el cambio que ejecuta el compromiso registrado el 2026-08-26. Se aplica
a todo el histórico: 197 filas del ledger reclasificadas, 600 entran y 600
salen. Ninguna predicción se borra ni se rehace —reclasificar es aritmética
sobre el pico y el crecimiento ya observados— y el cambio queda declarado en la
cadena pública como dos eventos `rule_change`, sin reescribir una sola línea
existente.

**Lo que cambió en pantalla.**

| cifra publicada | vara vieja | vara nueva |
|---|---|---|
| precisión del sistema actual (n=341) | 48.8% | **12.6%** |
| en la ventana comparable (n=297) | 51.9% | **13.8%** |
| tasa base pareada | 50.3% | **8.1%** |
| lift | +1.6 pp (−4.1 a +7.3) | **+5.7 pp** (+2.2 a +10.1) |
| veredicto | no concluyente | **supera** |

El titular se ve cuatro veces peor y es defendible por primera vez. El anterior
se veía bien y no lo era.

**Dos cifras que nunca habían llegado a la pantalla.** La tarjeta de tasa base y
la de lift se escribieron el 2026-08-19 en respuesta a una crítica que pedía
exactamente eso, y no se dibujaron ni una vez: la línea que fusiona el caché con
el resumen del ledger copiaba una lista de claves escrita a mano, y
`matched_base_rate_pct` y `lift_pp` no estaban en ella. Se calculaban en cada
carga y se descartaban una línea después. En pantalla eso no se ve como un
error, se ve como una ausencia, y por eso sobrevivió ocho días. Se encontró
porque un analista miró el tablero y preguntó cuál era la tasa base.

### El hallazgo de las etiquetas

**Qué pasó.** Al reclasificar `twitch_horizon_labels` el 2026-08-27 solo se
escribieron las filas donde cambiaba la **bandera de éxito**. Para 860 anclas no
cambiaba: eran acierto bajo la vara vieja (crecer +100%) y siguen siéndolo bajo
la nueva, solo que ahora como FAIR en vez de HIT. Esas filas no se tocaron, y su
columna `outcome` se quedó diciendo `hit_strong`. En total **1,090 filas con el
resultado desfasado** de 22,135.

**Qué NO afectó.** La tasa base publicada se calcula con `sum(success)`. Al
recalcular las 22,135 filas desde cero, **0 tenían la bandera de éxito
incorrecta**. El 8.1% se sostiene, y el lift publicado el 26 y el 27 no estaba
inflado. Esto se verifica, no se supone: el conteo de discrepancias en `success`
es parte de la salida del script de reparación.

**Qué sí habría afectado.** La tasa base del HIT estricto se calcula con
`outcome = 'hit_strong'`. Sin reparar habría devuelto 1,936 donde la respuesta
es 1,076:

| | sin reparar | reparado |
|---|---|---|
| `hit_strong` | 1,936 | 1,076 |
| `fair` | 0 | 860 |
| tasa base solo HIT | 8.7% | **4.9%** |

Con 8.7% de base, nuestro 9.1% habría parecido *apenas mejor que el azar*. Con
la cifra correcta es **el doble**. La diferencia entre esas dos lecturas es toda
la afirmación, y se habría publicado como hecho.

**Por qué se encontró.** No por la auditoría, que revisa el ledger y no las
etiquetas. Se encontró porque se pidió publicar el HIT estricto, y esa cifra
depende de la columna rota: al ir a calcularla apareció un cero imposible —cero
FAIR en 22,135 anclas cuando el ledger tenía 14— que no cuadraba con nada. La
lección no es "revisar mejor": es que **una escritura condicionada a que cambie
el campo A deja el campo B atrás**, y que los ceros imposibles hay que
perseguirlos aunque el número que se estaba calculando salga bonito.

La reparación recalcula `outcome` de **todas** las filas, no solo de las que
cambian de éxito. Tarda 1.0 s.

**Lo que se publica ahora.** El HIT estricto —el megaéxito— con su propia tasa
base, contada con la misma definición en los dos lados. Sumar HIT+FAIR de un
lado y solo HIT del otro daría un lift inflado que nada en la pantalla podría
desmentir:

| | Draconfly | azar | ratio | IC del lift |
|---|---|---|---|---|
| HIT + FAIR | 13.8% | 8.1% | 1.71× | +2.2 a +10.1 |
| **solo HIT** | **9.1%** | **4.3%** | **2.09×** | **+2.0 a +8.6** |

Cuanto más dura la vara, mejor se ve la selección contra el azar. Es la forma
que debería tener si el sistema discrimina de verdad, y la contraria a la que
produciría un sistema optimizando su propia métrica.

**Qué se puede afirmar después de esto.** Lo mismo que el 26: nada todavía. Las
cifras de arriba son retrospectivas y la vara se fijó después de ver estos
datos. Lo que va a contar sigue siendo lo que den las predicciones emitidas
desde el 2026-08-26.

---

## 2026-10-01 — La lectura pre-registrada: supera

**Commit de la cadena:** `3100460`, publicado el 2026-10-01 a las 10:59:09 -0500.

**Hash final de la cadena el día de la lectura:**

```
3961c149b642e6c5f1d2d130dae872f1b5029c5b461b28877d552a48c1070732
```

2,147 eslabones · 1,125 emisiones · 1,020 resultados · 0 eslabones rotos.

Ese hash fija el estado exacto del archivo público en el momento de leer. Quien
clone el repositorio y recalcule la cadena debe obtener ese mismo valor; si no lo
obtiene, el archivo fue alterado después y nada de lo que sigue se sostiene.

**Se cumplió la condición declarada el 2026-09-05**: 450 predicciones vencidas,
antes del 2026-10-08. La cohorte va del 2026-08-26 al 2026-09-24 y cubre 261
creadores distintos.

### Las dos cifras

Como se comprometió el 2026-09-16, se publican las dos. La tasa base es 9.8%,
medida sobre 46,394 anclas etiquetadas con la misma vara y el mismo día.

| unidad | aciertos | tasa | lift | IC del lift |
|---|---|---|---|---|
| **por predicción** (la pre-registrada) | 120/450 | **26.7%** | **+16.9 pp** | (+13.0, +21.1) |
| **por despegue distinto** | 104/450 | **23.1%** | **+13.3 pp** | (+9.6, +17.4) |

Solo HIT, el caso extremo: **73/450 = 16.2%**.

**La unidad que cuenta es la predicción**, porque es la que se pre-registró. La
segunda cifra se publica porque sin ella la primera está unos 3.6 puntos arriba
de lo que sostiene un conteo por evento: 16 de los 120 aciertos son el mismo
despegue visto por dos predicciones con ventanas solapadas. Los casos, por
tamaño de pico: `haitani0904` (3→2), `eslcs` (4→2), `lacyoffline_` (5→4),
`ssaab` (2→1), `singollo` (5→2), `franciscoow` (2→1), `kusaka6e` (2→1),
`assiikun` (2→1), `viperriven247` (7→3), `allinyonok` (2→1).

### El intervalo es una cota optimista, y cuánto

También se comprometió decirlo. El IC de Wilson supone 450 ensayos
independientes y no lo son: 261 creadores en 450 predicciones. Un bootstrap por
conglomerados —remuestreando creadores enteros, 20,000 muestras, semilla
20261001— da el intervalo que aguanta esa correlación:

| intervalo del lift (por predicción) | piso | ancho |
|---|---|---|
| Wilson, supone independencia — **cota optimista** | +13.0 pp | 8.1 pp |
| bootstrap por conglomerados — **el honesto** | **+12.0 pp** | 9.8 pp |

**El piso defendible del lift es +12.0 puntos.** Ningún intervalo de los cuatro
publicados aquí se acerca al cero.

### Qué se auditó antes de leer

Un número favorable merece más auditoría que uno malo. Lo verificado el mismo
día, contra el repositorio y contra el archivo público:

- **La vara no se movió.** HIT +400%/250 y FAIR +250%/250 quedaron fijados en
  `be1409b` el 2026-08-27 y no cambiaron en los 35 días de la cohorte.
- **El modelo no se reentrenó.** `models/horizon_model.joblib` es del 2026-08-05
  a las 23:38, anterior al inicio de la cohorte.
- **La selección no cambió.** Dos commits tocaron ese camino desde el 08-26 y
  ninguno modificó una regla de clasificación.
- **Ninguna de las 450 se publicó después de vencer.** Margen mínimo 5.99 días,
  mediana 6.99.
- **Ningún resultado se anotó antes que su predicción.**
- **La auditoría de invariantes pasó 11 de 11**, incluida
  `ledger_reclasificado`: recalcular la vara vigente sobre todo el histórico
  devuelve exactamente lo guardado.

**Un defecto encontrado y corregido el mismo día.** A las 06:10:02 se evaluaron
los últimos 15 y la tarea de publicación corrió a las 06:10:10 — ocho segundos
después, pero leyó la base antes de que la escritura se confirmara. Durante cinco
horas la cadena pública sostuvo 105/435 mientras el tablero mostraba 120/450. Se
publicó a mano a las 10:59 y se verificó que el archivo público reconstruye el
26.7% por sí solo. Vale registrarlo porque es exactamente el tipo de hueco que
invalida una prueba sin que nadie lo note: la cifra era correcta y la evidencia
todavía no.

### Qué se puede afirmar después de esto

Que sobre 450 predicciones emitidas con siete días de anticipación y publicadas
antes de conocer su resultado, la selección acertó **2.7 veces más que tomar un
candidato elegible al azar**, y que el piso estadístico de esa ventaja —
descontando que algunos creadores se repiten — es **+12 puntos porcentuales**.

Qué **no** se puede afirmar: nada fuera de Twitch, nada sobre categorías que
nunca entran al top 10, y nada sobre los lotes emitidos después del 2026-09-24,
que son una cohorte nueva y todavía no vencen.

**Para el próximo pre-registro**, lo que este dejó claro: la unidad debería ser
el despegue y no la predicción, o imponerse un enfriamiento por creador. Mantener
la unidad declarada fue lo correcto —cambiarla con el resultado a la vista sería
mover la portería— pero obligó a publicar dos cifras donde una habría bastado.

---

# Compromisos abiertos

Instrumentación que **todavía no mueve ningún número publicado**, pero que fija
por adelantado bajo qué condiciones se permitirá moverlos. Se escribe antes de
tener resultados a propósito: declarar el criterio de éxito después de ver los
datos es la forma más fácil de engañarse.

## 2026-10-06 — El bono cross-platform opera sobre datos congelados desde julio

**No invalida ninguna cohorte.** Se anota porque el documento de selección
describía como vivo un componente que está casi inerte, y porque la decisión de
*cuándo* arreglarlo es metodológica.

### Qué se encontró

`Draconfly Check Cross-Platform Presence` lleva fallando desde el **2026-08-31**
—falta el binario de Playwright— y nadie lo vio porque esa tarea **no estaba
bajo vigilancia**. Seis corridas semanales fallidas seguidas: 08-31, 09-07,
09-14, 09-21, 09-28 y 10-05.

Los datos están peor que el fallo:

```
checked_at: de 2026-07-25 a 2026-07-26
32 creadores   118 filas   23 con presencia encontrada
```

**Dos meses y medio sin actualizarse, sobre 32 creadores de un panel de ~3,090.**
El `+6` de presencia cross-platform —uno de los cinco términos del Draconfly
Score— dispara para alrededor del **0.7%** del panel.

### Por qué no invalida A ni B

El **código** de selección está congelado desde el 2026-08-01 y no se ha tocado.
Lo que está congelado de más son los **datos** que alimentan uno de sus términos,
y eso vale **igual** para la cohorte A (08-26 a 09-25) y para la B (desde
10-06). Las dos corren bajo las mismas condiciones, que es justamente lo que una
replicación necesita.

### Por qué NO se arregla ahora

Arreglar Playwright refrescaría de golpe una tabla parada dos meses y medio: de
32 creadores con datos a potencialmente miles. El bono empezaría a disparar para
gente nueva y **cambiaría qué 15 creadores se publican**, en mitad de la cohorte
B.

Eso introduciría en B un cambio que A no tuvo — exactamente lo que una
replicación debe evitar. Se arregla **al cerrar B** (~2026-11-06), corriendo
`playwright install`.

### El aviso se difiere CON FECHA, no se silencia

El health check avisaría cada lunes sobre algo que ya se decidió no arreglar, y
un aviso semanal que no se va a atender enseña a ignorar los avisos. Pero
silenciarlo sin fecha lo entierra para siempre.

`TAREAS_DIFERIDAS` lo reporta como `ok` con el motivo y la fecha a la vista hasta
el **2026-11-06**; pasada esa fecha vuelve a ser `warning`. Una prueba verifica
que el diferimiento **venza**, porque un diferimiento que no vence es silencio
con mejor nombre.

### Cómo apareció

Mirando otra cosa. Al revisar si había arrancado la verificación del respaldo de
señales, el health check reportó un falso aviso de `Collect Requested Topics`
—cadencia desactualizada por un cambio de horario mío del día anterior—, y al
corregirlo salió la pregunta de fondo: **ocho de veinte tareas vivas no estaban
vigiladas**. Entre ellas ésta, y `Publish Ledger Chain`, que es la que empuja la
cadena con hash a GitHub.

## 2026-10-05 (6) — Brazo ciego: quince predicciones diarias que no se publican

**`BRAZO_DESDE = "2026-10-06"`.** Declarado hoy, arranca mañana. Tabla propia,
`blind_prediction_ledger`, en la base principal — que vive en el SSD.

### Qué objeción cierra

Draconfly afirma 26.7% contra una tasa base de 9.79%, y esa tasa base sale de
creadores **que nadie señaló**. El día que publicar lleve audiencia a los
señalados, van a crecer en parte **porque** se los señaló, y el lift deja de
medir predicción para medir influencia.

Lo grave no es el sesgo: es que **se vuelve inseparable hacia atrás**. Una vez que
existe audiencia, ya no se puede distinguir "lo vimos venir" de "lo causamos"
para ese período, nunca.

Hoy hay blindaje completo contra *"escogiste a dedo"* y **cero** respuesta a
*"¿no lo causaste tú?"* — que es la segunda pregunta de cualquier evaluador
serio.

### Por qué la fecha importa más que el diseño

**Hoy no hay audiencia**, y se verificó en vez de suponerlo: el repositorio es
**privado** y el tablero escucha en la red local. Así que las cohortes A y B
están limpias.

Ese período sin audiencia es la **línea base** contra la que se medirá el efecto
de publicar, y solo existe si se registra antes. Cada día sin brazo ciego era un
día irrecuperable.

### Los puestos 16 al 30, y por qué no un sorteo

Lo correcto sería sortear entre los 30 mejores: ahí los dos grupos quedan
estadísticamente iguales. **Pero eso cambia cuáles 15 se publican, y anula la
cohorte B.**

Lo que funciona sin tocar la selección es comparar **en la frontera**. El corte en
15 es una decisión de producto, no una frontera natural: el puesto 15 y el 16 son
casi idénticos en score, y lo único distinto entre ellos es que uno se publicó.
Cualquier salto ahí es el efecto de publicar — regresión por discontinuidad.

**Declarado hoy para que no parezca decidido después:** al cerrar la cohorte B, el
diseño pasa a sorteo entre los 30 mejores.

### Los mismos filtros, o no hay comparación

El lote publicado son los primeros 15 en orden de score que pasan el piso de
audiencia, de `decision_brief(limit=300, candidate_pool=400)`. El brazo repite esa
llamada con los mismos parámetros y el mismo piso, se salta los primeros 15 y
toma los siguientes 15.

### La limitación que no se tapa

`decision_brief()` se llama por **segunda vez**, minutos después. El ranking
podría diferir. En vez de suponer que coincide, **se verifica**: el top 15 de esta
llamada se compara contra lo que `prediction_ledger` registró ese día, y el
resultado queda en la columna `coincide_publicado`. Los días que no coincidan
quedan **marcados como frontera sospechosa**, no descartados en silencio.

### También cegado para nosotros, hasta que B cierre

Sus resultados no son los de B, pero están correlacionados: mismo día, mismo
universo. Mirarlos sería un canal de inferencia sobre B — débil pero real, y el
punto 8 existe para no tener ninguno. Como hoy no hay audiencia, el efecto a medir
es ~cero y no se pierde nada esperando.

### Qué compra, además de cerrar la objeción

1. **Una medida de predicción permanentemente limpia.** El brazo no se publica
   nunca, así que su tasa es predicción sin influencia **para siempre**, aunque
   Draconfly termine con cien mil usuarios.
2. **Dice si el Top 15 debería ser Top 30.** Ya se midió que el score no ordena
   *dentro* del Top 15 (entrada del 10-03). Esto dice si discrimina **cruzando** el
   corte.

### Seis pruebas que no probaban

Hoy seis pruebas mías fallaron contra código correcto o pasaron sin garantizar
nada. Las cinco primeras, por escanear texto y tropezar con la prosa que
explicaba el arreglo. **La sexta es la peor:** verificaba que ninguna escritura
apuntara a `prediction_ledger`, y no detectaba `insert or ignore into
prediction_ledger` — porque la palabra antes de `into` es `ignore`, no `insert`.
Habría pasado como garantía sin garantizar nada.

Se encontró corriéndola contra siete casos construidos a mano, no leyéndola. Desde
hoy, toda prueba de esta clase se verifica contra el caso que debe detectar antes
de darla por buena.

20 pruebas nuevas, suite completa en 314.

## 2026-10-05 (5) — Búsqueda sistemática de fugas: no hay una tercera

Después de encontrar dos fugas del cegado el mismo día, se buscó una tercera de
forma sistemática en vez de por intuición. **No existe.**

El criterio: un camino filtra si lee `prediction_ledger`, incluye filas con
`created_at >= 2026-10-06`, expone desenlace, y es alcanzable antes del cierre.

| verificación | resultado |
|---|---|
| consultas que ventanean el ledger por `created_at` | **5 en todo el código**, las cinco justificadas |
| consumidores externos de `replicacion` | los 3 importan solo `estado_b`, nunca `cargar()` |
| tablero, modo inversionista | ciega primero **y** pone `f_issued = 0` |
| `continuation.py` | lee `twitch_horizon_labels`, no predicciones |
| `ledger_audit.py` | verifica coherencia, no calcula tasas |

Las cinco consultas con ventana: tres en `replicacion.py` (cegadas por diseño y
solo alcanzables desde dentro del módulo), una en `monitoreo_mitades.py` (cerrada
hoy en el arranque de B) y una en `youtube_cohorte.py` (tabla propia).

### Lo que sí hay, y es distinto de una fuga

**Seis superficies agregan todo el histórico sin aislar a B**, y desde el
2026-10-06 la incluyen:

- `ledger_summary()` → la precisión publicada del tablero
- `materialized.py:618` → la caché que la alimenta
- `growth_scoring.accuracy_report()` → por confianza y por horizonte
- el bloque "lo que se publica" del reporte matutino
- la sala de predicciones, que muestra desenlaces individuales

**No es una violación del cegado.** B no queda aislada: aporta ~105 de ~1,275
predicciones tras una semana, un 8%. Y la cohorte A corrió en condiciones
idénticas — el producto mostró sus desenlaces conforme caían, y A sigue siendo
una evaluación prospectiva válida porque lo congelado era la **selección** y lo
pre-registrado era el **análisis**. Cegar el producto un mes significaría
apagarlo.

**Sí es una brecha de divulgación.** Desde el 10-06 la cifra publicada cambia de
significado en silencio: "precisión 22.2%" pasa a ser una mezcla de pre-A, A y B.
Quien compare dos capturas a través de esa frontera necesita saberlo, y para eso
existe este archivo.

**Y queda un canal de inferencia débil:** con aritmética deliberada día contra
día se puede despejar la contribución de B del agregado. No se puede cerrar sin
apagar el producto; la mitigación es el compromiso de no hacerlo, que es lo que
el punto 8 ya dice.

### El invariante, para no depender de volver a auditar

`test_fugas_cohorte_b.py` fija por AST que nadie fuera de `replicacion.py` pueda
importar `cargar`, `diferencia_entre_cohortes`, `por_novedad`,
`intervalo_agrupado`, `Cohorte`, `_predicciones` ni `_tasa_base`; que los
consumidores sigan siendo exactamente tres; que las consultas con ventana sigan
siendo cinco; y que ninguna ventana de monitoreo alcance el arranque de B.

Verificado que no es vacuo: rechaza un import de `cargar` y acepta uno de
`estado_b`.

### Una nota sobre las pruebas de hoy

Cuatro veces hoy una prueba que escaneaba **texto** se tropezó con la prosa que
explicaba el arreglo: el comentario que cita `_linea(b)`, el docstring que cita
`select * from prediction_ledger`, el que menciona `youtube_channels`, y los tres
archivos que mencionan `replicacion.py` sin importarlo. Las cuatro se rehicieron
con AST, donde los comentarios no existen. Y una quinta era **vacua** —buscaba la
fuga dentro de una rama cuando estaba antes de ella— y se detectó corriéndola
contra el código viejo, no leyéndola.

## 2026-10-05 (4) — Cohorte B DECLARADA, y el cegado que faltaba

**`COHORTE_B_DESDE = "2026-10-06"`.** Ese commit es la declaración, y su fecha en
GitHub es la prueba de que precede a toda predicción de B.

### Por qué el 6 y no el 8

El 8 de octubre **nunca fue un compromiso de protocolo**. Era la fecha de lectura
de la cohorte A —o al alcanzar 450 vencidas, lo que ocurra primero— que se
cumplió antes, el 2026-10-01. El plan de arrancar B el 8 era calendario propio, y
una frase escrita en este mismo archivo que queda corregida.

Declarar dos días antes no toca el riesgo que el pre-registro cubre: las dos
fechas eran futuras al momento de elegir, así que ninguna se escogió mirando sus
propios resultados. Lo que cambia es que B cierra dos días antes.

### Por qué el valor es 2026-10-06

Verificado contra el Task Scheduler antes de escribirlo: los dos disparadores de
`record-predictions` —05:30 y 08:00— ya habían corrido al momento del commit
(12:06), los dos con código 0. El próximo lote es el del **2026-10-06 05:30**.

O sea que la fecha es literalmente el primer lote emitido después de commitear,
como exige el punto 1, y **no incluye ni una predicción ya existente**.

### El cegado estaba a medias, y se descubrió al declararla

`informe()` —el comando `replicacion`, el que corre una persona— llamaba a
`_linea(b)` **de forma incondicional** e imprimía las seis cifras de B: aciertos,
tasa, tasa base, razón, lift y los dos intervalos. Después cerraba diciendo que
lo de arriba era monitoreo y no la lectura.

Esa etiqueta no arreglaba nada. El punto 8 dice que mientras B siga abierta **no
se miran** resultados parciales; el cegado existe para no **haber visto** el
número, no para verlo con una advertencia al lado.

Lo llamativo es dónde estaba el agujero: `estado_b()` se blindó con todo cuidado
—su docstring dice que a propósito no devuelve ni un acierto— y el reporte
matutino lo usaba bien. Las siete pruebas de `test_cegado_cohorte_b.py` cubrían
`estado_b()` y **ninguna tocaba `informe()`**. El cegado se implementó y se probó
en el camino que ya estaba cegado.

Se descubrió al declarar la cohorte, con **cero predicciones emitidas**, así que
no se vio ningún resultado parcial. Ahora `informe()` muestra el censo operativo
—emitidas, cerradas, días con lote— y calcula las cifras solo al cerrar.

### Un crash que apareció en el mismo instante

Con B declarada y n=0, `razon` devuelve `None` y `_linea` lo formateaba sin
comprobar: `TypeError`. El comando pre-commiteado para analizar B se caía el día
que B empezaba. Lo resuelve el mismo cambio, porque la rama abierta ya no llama a
`_linea`.

### Tres pruebas que no probaban

Vale anotarlo porque es el patrón del día:

1. La primera versión partía el código por texto y buscaba `_linea(b)`. **Falló
   contra el código corregido**, porque el comentario que explica el arreglo lo
   menciona al contarlo.
2. La segunda lo buscaba por AST **dentro** de la rama `if faltan > 0`. Era
   **vacua**: en el código viejo la fuga estaba *antes* de la rama, así que daba
   cero en el código roto y en el arreglado.
3. La tercera verifica el **orden** —ninguna llamada a `_linea(b)` en una línea
   anterior a la rama— y se comprobó contra el código viejo antes de darla por
   buena.

Las cuatro pruebas del tercer estado del reporte matutino fallaron al declarar B,
correctamente: ese estado terminó. Se hicieron deterministas en vez de depender
de qué día es, y se agregó el estado vigente.

### Qué queda congelado desde hoy

Modelo `horizon_model.joblib`, pesos 0.65 y 0.12, los tres bonos, piso de 50,
Top 400, Top 15 y la vara HIT/FAIR. **Cualquier cambio que afecte QUÉ
predicciones se emiten anula B y la reinicia desde cero.**

Lo operativo no la anula, y hoy hubo bastante: mover `collect-requested-topics`
de 07:20 a 11:30, subir el límite de `generate-labels` a 4 h, reactivar la
comprobación de integridad, arreglar los instaladores. Nada de eso toca
`intelligence.py` ni `analytics.py`, que siguen sin un commit desde el
2026-08-26.

## 2026-10-05 (3) — Pre-registro de la cohorte de YouTube

**Commit:** este mismo. **La cohorte todavía NO está declarada**: en
`draconfly/youtube_cohorte.py`, `COHORTE_YT_DESDE` vale `None`. Ponerle fecha y
commitear ese cambio **es** el acto de declararla.

### Tabla propia, no `prediction_ledger`

De las ~40 consultas a `prediction_ledger`, **solo dos filtran por plataforma**.
Escribir predicciones de YouTube ahí habría contaminado en silencio la cadena
pública, la cohorte B, la medición congelada del 29-sep y el número de precisión
del tablero. `youtube_prediction_ledger` deja los 40 sitios correctos por
construcción.

### Lo que se congela

La vara de `youtube_vara.py` (commiteada en `831b186` **antes** de medir su tasa
base), el modelo `youtube_ranker_v1.joblib` con sus siete features y sus
coeficientes, el Top 15 diario y el horizonte de 24 h.

**La unidad es el video-ancla**, no el canal: es lo que la vara mide, y no
obliga a inventar una agregación que habría que justificar aparte. El canal se
deriva después —cada predicción guarda su `channel_id`— y de hecho el intervalo
que manda ya se agrupa por canal.

### El protocolo, declarado antes

1. **Arranque.** El primer lote emitido después de commitear
   `COHORTE_YT_DESDE`. No se usa ninguna fecha anterior: las cifras del backtest
   ya se vieron y cubren hasta el 2026-10-04.
2. **Cierre.** 450 cerradas, a 15 diarias: 30 días de emisión más 1 de
   maduración. ~31 días, contra los ~37 de Twitch — la ventaja viene del
   horizonte de 24 h, no de emitir más.
3. **Éxito primario.** Lift positivo sobre su propia tasa base **y** su
   intervalo **agrupado por canal** excluye el cero. El que manda es el
   agrupado, no el de Wilson.
4. **Éxito secundario, obligatorio.** El sistema tiene que **superar al mejor
   ranking trivial de una sola columna**, con un intervalo de la **diferencia**
   que excluya el cero.
5. **Las dos cifras, siempre juntas:** razón y diferencia en puntos
   porcentuales.
6. **Nunca la razón entre plataformas** sin las tasas base al lado.
7. **Concentración:** canales distintos detrás de las predicciones y de los
   aciertos, y el máximo que aporta uno solo.
8. **Transparencia:** si falla, se publica igual.
9. **Cegado:** mientras siga abierta no se miran resultados parciales.

### El punto 4 no existe en las cohortes de Twitch, y es el que más importa

Lo obligó el backtest de hoy. Dio razón **10.40×** contra el azar — pero ordenar
por aceleración sola ya daba **4.53×**. Una razón alta contra el azar **no
demuestra que el modelo aporte**.

Así que superar al nulo es **requisito, no extra**: si el sistema no lo supera,
la cohorte se publica como **fallida** aunque su lift contra la tasa base sea
enorme. Es la lección de `breakout` aplicada un nivel más arriba — ahí lo
definicional era el denominador, aquí sería el lift.

### Potencia

Con la tasa base de 1.885%, el azar esperaría **8.5 aciertos** en 450. El piso
del IC95 supera la tasa base incluso si el sistema solo acertara el 4%. A 200 ya
alcanzaría; no se baja a 200 porque **la paridad con Twitch vale más que cerrar
dos semanas antes**.

### Qué falta antes de poder declararla

Crear la tabla y enganchar la emisión diaria. Declarar antes de eso dejaría una
fecha de arranque anterior al primer lote, que es justo lo que el punto 1
prohíbe. 18 pruebas nuevas, suite completa en 225.

## 2026-10-05 (2) — El backtest de YouTube, y por qué el 10.40× no es la cifra

**Esto es un backtest, no un resultado.** Mide si vale la pena correr la cohorte
prospectiva, y nada más. Lo único afirmable hacia afuera sale de predicciones
registradas antes de conocer su desenlace. Se anota aquí porque fija la decisión
de arrancar.

### El ranker

Módulo propio (`draconfly/youtube_ranker.py`), aislado por tres razones
distintas: no importa `intelligence.py` ni `analytics.py` —cuyos cero commits
desde el 2026-08-26 sostienen la afirmación de las cohortes—, no toca
`prediction_ledger`, y no entrena contra `breakout`.

Regresión logística sobre **siete** features de instante de ancla, corte temporal
**2026-09-01** declarado antes de entrenar. 1,146,582 anclas de entrenamiento y
796,216 de prueba.

### Sobre `prediction_ledger`: el hallazgo que cambió la arquitectura

Auditadas las ~40 consultas a esa tabla: **solo dos filtran por plataforma.**
Escribir predicciones de YouTube ahí habría contaminado, en silencio:

- **la cadena pública** — `public_ledger.py` hace `select * from
  prediction_ledger` sin condición
- **la cohorte B** — `replicacion.py` cuenta por rango de fechas, y empareja su
  tasa base contra `twitch_horizon_labels`
- **la medición congelada del 29-sep** — `monitoreo_mitades.py` tampoco filtra
- **el número publicado del tablero** — `ledger_summary()` agrega la tabla entera

La cohorte B arranca el **2026-10-06** (declarada el 05, ver la entrada de ese
día). Esta frase decía "el 8 de octubre" cuando se escribió, unas horas antes; se
corrige aquí en vez de dejarla contradiciendo al código. YouTube recibe su propia
tabla, y así los 40 sitios quedan correctos por construcción en vez de arreglados
uno por uno.

### El primer resultado, y por qué obligó a desconfiar

| | |
|---|---|
| AUC | **0.9744** |
| las 15 de cada día, 33 días | 94 de 495 = **18.990%** |
| tasa base del periodo | 1.827% |
| lift | +17.163 pp · razón **10.40×** |

El modelo de Twitch saca AUC 0.576. Un 0.97 sobre una tasa base de 1.8% no es un
logro, es una alarma. Y el coeficiente más fuerte lo explicaba:
`log_edad_horas` en **−1.64**, o sea *"elige videos jóvenes"*.

Tiene una razón mecánica: en vistas **acumuladas**, un video casi tiene que ser
joven para triplicar en 24 h. El 65% de las anclas son de 72 h+ y solo el 12% de
0-24 h. La edad no es una fuga —se conoce en el ancla— pero **el lift podía ser
una propiedad de la vara y no del sistema.** Es la misma clase de error que usar
`breakout`, solo que ahí lo definicional era el denominador y aquí sería el lift.

### Los nulos: cuánto del lift da un ordenamiento trivial

| ranking | tasa | razón |
|---|---|---|
| **modelo v1** | **18.990%** | **10.40×** |
| más aceleración | 8.283% | 4.53× |
| más joven | 7.677% | 4.20× |
| menos vistas | 6.667% | 3.65× |
| más velocidad reciente | 5.657% | 3.10× |
| azar (200 sorteos) | 1.804% | 0.99× |

Ordenar por **una sola columna** ya da 3–4.5×. Así que **el aporte del modelo es
2.3× sobre el mejor nulo, no 10.4× sobre el azar**, y esa es la cifra que se
presenta.

El control de azar cae en 1.804% contra una tasa base de 1.827%: el muestreo por
día no está sesgado. La primera versión usaba **un** sorteo y dio 1.010%, que
parecía raro y no lo era —rango de los 200 sorteos: 0.61% a 3.64%—. Un sorteo no
distingue un muestreo sesgado de un sorteo bajo.

### La concentración por canal: la preocupación no se materializó

| | Twitch cohorte A | YouTube backtest |
|---|---|---|
| unidades | 450 predicciones | 495 selecciones |
| grupos distintos | 261 creadores (58%) | **449 canales (90.7%)** |
| aciertos / grupos | 120 | 94 / **88 canales** |
| máximo de un grupo | — | **3** |

Con esa dispersión el bootstrap agrupado apenas castiga: IC95 **(15.447%,
22.653%)**, piso del lift **+13.621 pp**.

### El intervalo de la DIFERENCIA, que es la prueba correcta

Quedó un intervalo para el modelo y un **punto** para el nulo, y concluir "le
gana" porque no se traslapan es exactamente la prueba laxa contra la que advierte
el docstring de `lift_interval()`. Corregido con un bootstrap de la diferencia,
remuestreando **días enteros** —el día es la unidad que genera la dependencia:
una jornada viral levanta a los dos rankings a la vez—:

| nulo | diferencia | IC95 de la diferencia |
|---|---|---|
| **más aceleración** *(el más duro)* | **+10.707 pp** | **(+7.071, +14.343)** |
| más joven | +11.313 pp | (+6.667, +15.960) |
| menos vistas | +12.323 pp | (+7.879, +16.768) |
| más velocidad reciente | +13.333 pp | (+9.091, +17.778) |

Ninguno cruza cero.

### Un bug disfrazado de hallazgo

`diferencia_contra_nulo()` usaba `nlargest` para **todos** los nulos. Para "más
aceleración" era correcto. Para "más joven" eligió los videos más **viejos** —0
aciertos de 495— y reportó eso como una diferencia de **+18.990 pp con IC
(+15.152, +23.030)**, que no cruza cero y se veía espectacular.

Era una comparación contra el **peor ranking posible**. Lo delató que ese 0.000%
no cuadraba con el 7.677% que "más joven" había dado en la tabla de nulos: la
inconsistencia entre dos mediciones de la misma cosa, no una revisión del código.

Arreglado leyendo la dirección de `NULOS` y con una clase de pruebas
(`DireccionDeLosNulos`) que fija que cada nulo la declare, que coincida con su
nombre, y que un nulo inventado falle con la lista de opciones. Se anota aquí
porque un registro que solo apunta los aciertos no sirve para auditar.

*Dato de paso:* ordenar por los videos más **viejos** da exactamente 0 de 495.
Confirma que el mecanismo de la edad es casi absoluto.

### Qué falta para que exista un resultado

Ni pre-registro, ni tabla propia, ni una sola predicción de YouTube emitida.
`prediction_ledger` tiene 1,168 de Twitch y 2 anotadas cross-platform.

## 2026-10-05 — La vara absoluta de YouTube, declarada antes de medirla

Para que YouTube pueda tener una cohorte prospectiva hacía falta primero una
vara. La que ya existía en el código, `breakout`, **no sirve para afirmar nada
hacia afuera**, y conviene decir por qué antes de lo demás.

### Por qué no se usó la etiqueta que ya existía

`breakout` exige `cohort_percentile >= 0.9` más un lift absoluto mínimo. Su tasa
base a 24 h es **9.54%** — sospechosamente parecida al 9.79% de Twitch, y por eso
mismo peligrosa: **el decil superior es 10% por construcción**, y el filtro de
lift lo recorta a 9.54%. Ese número no es un hallazgo sobre el universo de
YouTube; es la definición devuelta.

El 9.79% de Twitch es otra cosa: sale de umbrales absolutos (+250% de
crecimiento y 250 espectadores), así que es una propiedad real del universo
medido. Superar un decil que uno mismo definió es una afirmación más débil y
**distinta**. Presentar las dos como equivalentes —"YouTube también tiene una
tasa base de ~9.5%"— es lo primero que detecta un revisor técnico.

### Por qué las vistas obligan a un diseño distinto

Los espectadores de Twitch son **concurrentes**: suben y bajan, así que +400% es
un pico real. Las vistas de YouTube son **acumuladas** — solo pueden subir. Un
video de seis horas quintuplica sus vistas nada más por seguir existiendo.

De ahí que el piso absoluto cargue más peso aquí que en Twitch: el multiplicador
solo, en YouTube, mide sobre todo juventud del video.

### La vara

| criterio | definición |
|---|---|
| **HIT** | crecimiento **≥ 5.0×** (+400%) **y** ≥ 10,000 vistas |
| **FAIR** | crecimiento **≥ 3.5×** (+250%) **y** ≥ 10,000 vistas |
| **ÉXITO** | HIT **o** FAIR — es el criterio que se pre-registra |

Horizonte **24 h**, no 7 días: `predictive_labels.HORIZONS` es `(6, 24)` en horas
y no existen etiquetas a 168 h. Una prueba lo verifica, para que la vara no pueda
declarar un horizonte que nadie etiqueta. No es una limitación que haya que
arreglar — un horizonte corto verifica más rápido — pero obliga a decir, en toda
comparación con Twitch, que son predicciones a 24 h contra predicciones a 7 días.

Los dos multiplicadores son **idénticos a los de Twitch** a propósito: mantener
la estructura de la vara igual deja limpia la comparación entre plataformas y
elimina dos parámetros libres. El único parámetro genuinamente nuevo es el piso
de vistas, porque 250 espectadores concurrentes no se traducen a vistas
acumuladas.

### El orden, que es el punto

Los tres umbrales se escribieron, probaron y **commitearon en `831b186` antes de
medir** la tasa base que iban a producir. Elegirlos después de ver los números
sería escoger el denominador más conveniente: un piso más alto baja la tasa base
y agranda el lift sin que el sistema prediga nada mejor.

### La tasa base, medida después

Sobre **1,942,798 anclas** etiquetadas a 24 h, mismas unidades que las 46,394
anclas con que se midió la tasa base de Twitch:

| criterio | aciertos | tasa base | IC95 |
|---|---|---|---|
| **ÉXITO** | 36,615 | **1.885%** | (1.866, 1.904) |
| **HIT** | 26,451 | **1.361%** | (1.345, 1.378) |

**Cinco veces más estricta que la de Twitch** (9.79%). La consecuencia hay que
decirla antes de tener resultados, no después: si el sistema lograra un 10% en
YouTube, el lift sería **+8.1 pp con razón 5.31×**, contra los **+16.9 pp y
2.72×** de Twitch. **Menos puntos porcentuales y una razón mucho mayor.**

Las dos cifras son verdaderas, y publicar solo la razón sería halagador y
engañoso. Se publican las dos, igual que para Twitch, y **nunca la razón entre
plataformas sin las tasas base al lado.**

### La sensibilidad queda pública

Para que nadie tenga que confiar en que los umbrales no se movieron hacia el
número bonito, `rejilla()` reporta la tasa base en 20 combinaciones, de un solo
barrido:

| | 1,000 | 10,000 | 50,000 | 100,000 |
|---|---|---|---|---|
| ratio ≥ 2.0 | 5.211% | 3.486% | 1.431% | 0.976% |
| ratio ≥ 3.0 | 3.046% | 2.194% | 0.852% | 0.560% |
| **ratio ≥ 3.5** | 2.540% | **1.885%** | 0.731% | 0.477% |
| **ratio ≥ 5.0** | 1.714% | **1.361%** | 0.541% | 0.348% |
| ratio ≥ 10.0 | 0.817% | 0.723% | 0.335% | 0.218% |

La vara elegida está **a media tabla, no en la esquina**. La esquina
(ratio ≥ 10, piso 100,000) daría una tasa base de 0.218% — nueve veces menor, y
por lo tanto una razón muchísimo más vistosa. No se eligió.

### Lo que salió peor de lo esperado, y se deja como está

El tramo FAIR resultó **delgado**: 10,164 de los 36,615 aciertos, apenas el 28%.
En Twitch FAIR eran 47 de 120, el 39%. En YouTube, cruzar 3.5× casi siempre
significa pasarse de 5× — **no hay término medio**, y la estructura de dos
niveles carga mucha menos información aquí.

**La vara no se cambia por eso.** Se declaró, se commiteó y se midió en ese
orden; revisarla porque una de sus decisiones salió menos útil de lo esperado es
exactamente lo que el pre-commit existe para impedir. Si algún día se cambia,
será una vara nueva, con fecha nueva y su propia entrada en este archivo.

### Potencia: 450 predicciones alcanzan de sobra

Con una tasa base de 1.885%, el azar esperaría **8.5 aciertos** en 450
predicciones. El piso del IC95 supera la tasa base incluso si el sistema solo
acertara el 4% (18 de 450, piso 2.54%). A 200 predicciones ya alcanza.

Esos intervalos son de Wilson, o sea la **cota optimista** — suponen
independencia, y las anclas de un mismo canal no lo son. El intervalo que se
publique será el agrupado por canal, como en Twitch.

### Lo que todavía NO existe

Ni ranker, ni pre-registro, ni una sola predicción de YouTube emitida:
`prediction_ledger` tiene 1,168 de Twitch y 2 anotadas "Twitch + YouTube", que
son notas cross-platform. **Esta entrada no reporta ningún resultado de
YouTube** — fija la vara con la que se van a medir.

## 2026-10-03 — El score no está calibrado, y dentro del Top 15 no ordena

**Commit:** este mismo. **No cambia todavía ninguna cifra publicada**, pero sí
fija qué se puede y qué no se puede decir del número que el tablero muestra
junto a cada creador.

`trend_probability_pct` se muestra hoy etiquetado como *probabilidad*. Se midió
contra la cohorte A, ya cerrada:

| score emitido | n | aciertos | tasa real | IC 95% |
|---|---|---|---|---|
| 95.0 | 98 | 27 | **27.6%** | (19.7, 37.1) |
| 92.4 | 60 | 19 | **31.7%** | (21.3, 44.2) |
| 87.2 | 57 | 13 | **22.8%** | (13.8, 35.2) |
| 79.2 | 127 | 33 | **26.0%** | (19.1, 34.2) |
| 70.3 | 108 | 28 | **25.9%** | (18.6, 34.9) |

**Dos hallazgos.** Un 95 significa 27.6%, no 95%: el score no está calibrado
como probabilidad. Y más importante, **dentro de las 15 publicadas el score no
ordena**: los cinco tramos caen entre 22.8% y 31.7% y todos los intervalos se
solapan entre sí.

**Qué NO significa.** No significa que el sistema no funcione. La discriminación
ocurre al entrar al Top 15, no dentro de él: el score separa a los elegidos del
universo con una razón de 2.72×. Una vez que te quedas con los 15 mejores de
662, el rango publicado (70 a 95) es toda cola derecha y ahí dentro ya no queda
señal utilizable. Es restricción de rango, y es esperable.

**Hecho en este mismo commit.** Las seis etiquetas de interfaz que decían
*Probabilidad* ahora dicen **Draconfly Score**: la columna del salón, la del
replay, la métrica ejecutiva, la del gráfico, la de oportunidades y el título
"Probabilidad de breakout". **El campo interno `trend_probability_pct` no se
toca**: renombrarlo hoy sería riesgo operativo sin beneficio, y lo que engañaba
al lector era la etiqueta, no el nombre de la columna.

**Y el símbolo de porcentaje, también en este commit.** Dejar el `%` después
de renombrar sería contradecir el renombre: si 68.3 no significa 68.3% de
probabilidad, el símbolo lo vuelve a afirmar. Ahora se muestra **`68.3 / 100`**
en los cinco sitios donde se imprimía con `%`, incluida la tarjeta ejecutiva,
que es la más visible. La escala 0–100 es honesta: `trend_probability` está
acotado entre 5 y 95 por el `clamp()` de `intelligence.py`.

Dos etiquetas más que decían *Prob. %*: la columna del TUI pasa a **Score**, y
el filtro que el Copilot anuncia en su respuesta pasa de *"probabilidad >= 75"*
a *"Draconfly Score >= 75"*.

**Lo que sí se puede afirmar del score:** que sirve para elegir a los 15.
**Lo que no:** que ordene dentro de los 15.

## 2026-10-03 — Cohorte B: replicación prospectiva predeclarada

**Commit:** este mismo. **La cohorte todavía NO está declarada**: en
`draconfly/replicacion.py`, `COHORTE_B_DESDE` vale `None`. Ponerle fecha y
commitear ese cambio **es** el acto de declararla, y ese commit es la marca de
tiempo que prueba que la declaración precede a la primera predicción de B.

**Por qué.** La cohorte A, leída el 2026-10-01, es una evaluación prospectiva de
un sistema pre-especificado: el pipeline de selección quedó congelado el
**2026-08-01** —pesos 0.65 y 0.12 desde el commit inicial del 07-26, piso de 50
y Top 400 desde el 08-01— el modelo el **2026-08-06**, y entre el 08-26 y el
09-24 **no hubo un solo commit** en `intelligence.py` ni `analytics.py`. A no se
tuneó con sus propios resultados.

Su debilidad real es otra, y es doble. Primero, **parte del protocolo de lectura
se formalizó a mitad del periodo**: la fecha de lectura se declaró el 09-05 con
n=60. Segundo, y más importante, **A mide un solo mes**. Un tramo de 30 días no
distingue "el sistema funciona" de "ese mes era predecible".

B corrige las dos cosas: protocolo completo antes de la primera predicción, y un
periodo temporalmente separado.

### Qué queda congelado

Modelo `horizon_model.joblib`, pesos 0.65 y 0.12, los tres bonos
(cross-platform, baja saturación, categoría de evento), piso de 50 espectadores,
Top 400, Top 15, y la vara HIT/FAIR.

**Cualquier cambio que afecte QUÉ predicciones se emiten anula B y la reinicia
desde cero.** Los cambios puramente operativos no la anulan: arreglar una
ventana rota, mover la base a otro disco, acelerar una consulta. Se verificó que
el lote diario llama a `decision_brief()` en vivo y **no lee** ninguna caché, así
que el estado de las cachés materializadas no influye en la selección.

### El protocolo, declarado antes

1. **Arranque.** El primer lote emitido después de commitear `COHORTE_B_DESDE`.
   No se usa el 2026-09-25 —la frontera natural de A— porque a esa altura ya se
   habían visto cifras agregadas que incluían esos días.
2. **Cierre.** 450 predicciones cerradas. A 15 diarias son 30 días de emisión
   más 7 de maduración: unos 37 días desde el arranque.
3. **Éxito primario.** El lift de B sobre su propia tasa base es positivo **y su
   intervalo agrupado por creador excluye el cero**. El intervalo que manda es
   el agrupado, no el de Wilson, que es una cota optimista.
4. **Estabilidad temporal.** Se estima `lift_B − lift_A` con bootstrap por
   creador en ambas cohortes. Si ese intervalo incluye el cero, no hay evidencia
   de que el efecto cambiara entre periodos. **No se usa el solape de los dos
   intervalos de lift como prueba de diferencia**: es una prueba distinta y más
   laxa, el mismo error que el docstring de `lift_interval()` ya advierte para
   la comparación contra la tasa base.
5. **Consistencia.** Se reportan razón, diferencia en puntos porcentuales,
   intervalo agrupado y solape de creadores entre A y B.
6. **Novedad del creador.** B se parte entre creadores ya vistos en A y
   creadores nuevos, y se reporta el lift de cada parte. Responde a la objeción
   de que el sistema solo haya aprendido quiénes eran los candidatos recurrentes
   buenos. Si funciona también sobre creadores nuevos, esa objeción se cae.
7. **Transparencia.** Si B falla, se publica igual.
8. **Cegado.** Mientras B siga abierta **no se miran resultados parciales de
   B**: ni aciertos, ni tasa, ni lift acumulado. Vigilar la ejecución —lotes
   emitidos, huecos, errores, datos faltantes— es obligatorio; mirar el
   resultado, no. No porque mirarlo cambie las predicciones, que están
   congeladas, sino porque sostiene una afirmación mucho más limpia: *no se
   realizaron análisis intermedios del resultado*.

   **Esto está implementado, no confiado a la disciplina.** `estado_b()` en
   `replicacion.py` devuelve un censo puramente operativo y hay una prueba que
   falla si alguna de sus claves permite deducir el resultado; otra comprueba
   que dos cohortes con 40 de 40 aciertos y 0 de 40 devuelven exactamente el
   mismo censo. Mientras B esté abierta, el `morning-report` sustituye el bloque
   de la cohorte por ese censo más la línea *"aciertos: en reserva hasta el
   cierre, por diseño"*.

   **Y el tablero también.** El primer intento cegó solo el reporte matutino y
   dejó el Investor Demo intacto, que mostraba `forward_successes`,
   `forward_rate_pct` y `forward_lift_pp`: la promesa se rompía igual, por otra
   puerta. Ahora, con B abierta, ese bloque muestra **la cohorte A congelada**
   —120/450, 26.7%, tasa base 9.8%, lift +16.9 pp con el intervalo agrupado por
   creador (+11.9, +21.8)— y declara que hay una replicación en curso con las
   predicciones cerradas de B, sin una sola cifra de resultado.

   Eso corrige además un defecto que ya existía: hasta hoy ese bloque mostraba
   una cohorte que crecía sin parar desde el 2026-08-26, mezclando las 450 ya
   leídas con todo lo emitido después. Hoy marcaba 465 vencidas, que no es la
   cohorte A ni es B. Los números de A se leen de `LECTURA_A`, fijos, y no se
   recalculan en cada carga de página.

   **Fuga residual, declarada.** El bloque *"lo que se publica"* sigue mostrando
   la precisión histórica de todo el ledger, que incluirá las predicciones de B
   diluidas entre más de mil. Se deja a propósito: es la cifra que el tablero
   publica al mundo y apagarla sería apagar el producto. Pero no es cegado
   perfecto y conviene decirlo antes que después.

### El análisis ya está escrito

`draconfly/replicacion.py` y sus 13 pruebas se commitean **con esta nota**, antes
de que exista la primera predicción de B. El código que va a producir la cifra
queda fechado antes que los datos que va a leer, así que no se puede ajustar al
resultado. Se ejecuta con:

```bash
python -m draconfly replicacion
```

Hoy ese comando imprime la cohorte A y dice que B no está declarada.

### Qué se podrá afirmar si B replica

Que Draconfly fue evaluado prospectivamente en dos periodos temporales separados
con el pipeline de selección congelado, que la segunda cohorte quedó
completamente predeclarada antes de emitir su primera predicción, y que el
análisis usó inferencia agrupada por creador.

Lo que **no** se podrá afirmar aunque replique: nada fuera de Twitch, nada sobre
categorías que no entran al top 10, y nada sobre el orden *dentro* de las 15
publicadas — ver la nota del 2026-10-03 sobre la calibración del score.

## 2026-08-26 — Se fija una vara nueva ANTES de aplicarla

**Commit:** pendiente — esta nota se escribe deliberadamente antes de tocar código.

**El problema que se descubrió.** Un porcentaje de acierto no significa nada sin
la tasa base. Medida sobre 11,730 anclas reales de 7 días en la ventana
comparable, la tasa base del universo elegible es **52.7%**: más de la mitad de
los canales con 50+ espectadores cumple la definición actual de éxito por su
cuenta. La mediana de crecimiento a 7 días en ese universo es **+57.4%**, y el
umbral de FAIR está en +50%.

Es decir: la vara actual marca como "acierto" algo que le ocurre al canal mediano
en una semana normal. No mide si un canal despega; mide si tuvo una semana
normal. Contra ese objetivo la selección rinde **−7.5 pp por debajo del azar**
(IC95 −14.7 a −0.1).

**Lo que se midió al endurecerla.** Reclasificando el histórico —posible porque
tanto `prediction_ledger` como `twitch_horizon_labels` guardan el pico y el
crecimiento reales observados, así que aplicar otro umbral es aritmética sobre
datos ya escritos, no una predicción rehecha— el lift sube de forma monótona
conforme la vara se endurece:

| piso del acierto | Draconfly | tasa base | lift | IC95 |
|---|---|---|---|---|
| +50% / pico 100 *(actual)* | 45.2% | 52.7% | −7.5 pp | −14.7 a −0.1 |
| +100% / pico 250 | 25.4% | 24.1% | +1.3 pp | −4.6 a +8.3 |
| +200% / pico 250 | 16.4% | 12.1% | +4.2 pp | −0.5 a +10.4 |
| **+250% / pico 250** | **13.6%** | **8.7%** | **+4.8 pp** | **+0.5 a +10.7** |
| +300% / pico 250 | 11.3% | 7.2% | +4.1 pp | +0.2 a +9.6 |

**La vara que se fija desde hoy**, para medirse hacia adelante:

- **HIT**: crecer **+400%** llegando a **250 espectadores o más**
- **FAIR**: crecer **+250%** llegando a **250 espectadores o más**
- Acierto = HIT o FAIR, así que el piso efectivo es **+250% / 250**

**Por qué esta nota existe y se escribe ahora.** La vara se eligió DESPUÉS de
probar trece combinaciones y quedarse con la de mayor lift. Eso es exactamente
cómo se fabrica un falso positivo: con trece pruebas, encontrar una que cruce el
umbral al 95% es casi esperable. El +4.8 pp de arriba está inflado por esa
selección, y la cifra real hacia adelante será probablemente menor.

Por eso el criterio queda registrado **antes** de medirlo con predicciones
nuevas. Lo que valga como evidencia no es la tabla de arriba: es lo que den las
predicciones emitidas a partir de hoy, contra una vara que ya no se puede
reelegir.

**Qué se afirmará y qué no.** El lift se dará por demostrado solo si, sobre
predicciones emitidas desde el 2026-08-26 y con esta vara fijada, el intervalo
de la diferencia queda entero por encima de cero. Hasta entonces se publica
como hipótesis registrada, no como resultado.

**Lo que la vara NO cambia.** Ni el modelo, ni el filtro de audiencia, ni qué
creadores se seleccionan. Es un instrumento de medición distinto sobre el mismo
producto. Ninguna predicción se borra: el histórico se sigue publicando bajo
ambas varas, etiquetado.

**Qué distingue de verdad la vara nueva.** No el tamaño alcanzado —el 72.3% de
las selecciones llega a 250 espectadores y al azar lo hace el 69.8%, así que ese
piso no discrimina nada— sino el múltiplo de crecimiento: 14.1% contra 9.2%.
El piso de 250 está para que un acierto sea comercialmente útil, no para medir
al modelo.

### Actualización del 2026-08-27 — la base de comparación estaba incompleta

Las cifras de arriba se calcularon contra 11,730 anclas, porque
`twitch_horizon_labels` llevaba desde el 19 de agosto sin reconstruirse y solo
llegaba al día 12. La ventana de mantenimiento de hoy las regeneró: **22,135
anclas**, y en la ventana comparable pasan de 11,730 a **17,390**, con 25 días
en vez de 17 y 297 predicciones en vez de 177.

Con la base completa el panorama cambia de forma sustancial:

| piso del acierto | Draconfly | tasa base | lift | IC95 | veredicto |
|---|---|---|---|---|---|
| +50% / 100 *(vigente)* | 51.9% | 50.3% | +1.6 pp | −4.1 a +7.3 | no concluyente |
| +100% / 250 | 29.0% | 23.2% | +5.8 pp | +0.9 a +11.2 | supera |
| +150% / 250 | 22.9% | 15.4% | **+7.5 pp** | +3.1 a +12.7 | supera |
| +200% / 250 | 17.5% | 11.3% | +6.2 pp | +2.3 a +11.0 | supera |
| **+250% / 250** *(pre-registrada)* | **13.8%** | **8.2%** | **+5.7 pp** | **+2.2 a +10.1** | **supera** |
| +300% / 250 | 11.8% | 6.6% | +5.2 pp | +2.0 a +9.4 | supera |

Dos cosas que hay que decir con precisión:

**La vara vigente ya no está por debajo del azar.** Pasaba de −7.5 pp a +1.6 pp.
La conclusión de ayer —"la selección rinde peor que el azar"— era un artefacto de
comparar contra una base incompleta, no un hecho sobre el sistema. Queda
corregida aquí en vez de borrada, porque el error importa tanto como el dato.

**La vara pre-registrada NO se cambia.** Hoy +150% da más lift (+7.5 pp) que el
+250% que fijamos ayer, y reajustar por eso sería exactamente lo que la
pre-registración existe para impedir: elegir el criterio después de ver los
resultados. La vara sigue siendo **+250% / pico 250**, y sale bien parada por
sus propios méritos: +5.7 pp, IC95 +2.2 a +10.1, un 69% mejor que el azar.

Lo que cambió es la calidad de la evidencia retrospectiva, no la de la evidencia
prospectiva. Sigue valiendo lo mismo que ayer: lo que cuente será lo que den las
predicciones emitidas desde el 2026-08-26 contra una vara que ya no se puede
reelegir. Siete de ocho varas superando al azar es señal de que el sistema
discrimina; no es todavía la demostración.

> La vara se aplicó al día siguiente. Lo que movió en pantalla, y el error que
> apareció al aplicarla, están en **2026-08-27 — Se aplica la vara nueva, y una
> columna se queda atrás**, en la sección anterior.

## 2026-09-27 — La red de seguridad estaba matando lo que debía proteger

**Commit:** pendiente.

La reconstrucción **completa** de etiquetas es semanal y existe como red: si la
incremental se saltara algo, fallaría en silencio y una tasa base equivocada no
se cae, devuelve un número. Pero corría **antes** que la incremental, y hoy eso
costó la medición del día.

| hora | paso |
|---|---|
| 04:40 | arranca la ventana |
| 06:01 | el lote termina — **81 min** |
| 06:35 | las cachés terminan, con cinco de siete pasos omitidos |
| 06:35 | arranca la reconstrucción **completa** |
| 10:40 | el límite de 6 h la mata sin terminar |

La incremental nunca llegó a ejecutarse y la tasa base amaneció anclada en el
2026-09-19.

**Y se iba a repetir todos los días.** La marca de "última completa" solo se
escribe si el paso termina bien. Como murió, al día siguiente lo habría
intentado otra vez — y otra, y otra — matando las etiquetas cada mañana hasta
que la máquina mejorara. Cuatro días antes de la lectura.

**El arreglo es de orden, no de código:** la incremental va primero. Lo que el
día necesita se hace antes que la red de seguridad, no después. La completa
puede seguir fallando todo lo que quiera; lo único que se pierde es la red.

**Lo que sí funcionó hoy, y es la primera vez:** el matador de huérfanos actuó
solo. Terminó **seis procesos** de entre 8.0 y 8.1 h, el WAL bajó de 458 MB a
cero y la limpieza volvió a decir *truncado* en vez de *ocupada* — sin que el
dueño corriera un `taskkill`.

---

## 2026-09-26 (2) — Los tres hallazgos restantes de la revisión

**Commit:** pendiente. Ninguno toca la cohorte pre-registrada ni las cifras que
se leen el 1 de octubre.

### P2 dejaba fuera el último registro de su ventana

`evaluate_episodes()` comparaba `observed_at` —ISO con `T` y zona— contra
`datetime(?, '+N days')` de SQLite, que devuelve `YYYY-MM-DD HH:MM:SS` con
**espacio y sin zona**. Como texto, la `T` es mayor que el espacio: el límite
inferior *incluía* el registro que debía excluir y el superior *excluía* el que
debía incluir. La ventana quedaba corrida un registro en cada extremo, sesgando
las etiquetas `continuation`, `plateau`, `reversion` y `offline`.

Ahora los límites se calculan en Python y se pasan en el mismo formato que
`observed_at`. Medido sobre un episodio real: 106 snapshots por ambos métodos —
que los totales empaten no prueba que sean idénticos, porque el desfase movía un
registro en cada extremo; la prueba unitaria fija el comportamiento del límite.

### El Copilot anunciaba filtros que no aplicaba

El motor extraía filtros de la pregunta —"probabilidad > 75", "gaming"—, los
guardaba en el objeto de respuesta y **nadie los usaba**: los rankings se
cargaban enteros mientras la respuesta imprimía *"Filtros detectados"*. Quien
leía creía estar viendo una consulta filtrada.

Ahora se aplican de verdad sobre las columnas que existen, y la respuesta dice
**"Filtros aplicados"** con lo que realmente ocurrió. Un filtro que no encuentra
su columna se reporta aparte como *detectado pero no aplicable*: la corrección no
es solo filtrar, es no prometer de más.

**Y al probarlo contra datos reales apareció lo de verdad interesante:**
`"gaming"` **no es ninguna categoría**. En Twitch son títulos de juego —`IRL`,
`Always On`, `PERSONA3 RELOAD`, `Arena Breakout: Infinite`—, así que el filtro
literal no casa con nada y vaciaba la respuesta. El primer arreglo cambió una
mentira por un silencio, que no es mejor. Un filtro que deja cero filas ahora se
anota como `(0 resultados)`, de modo que el lector sabe *por qué* no ve nada.

Verificado con la pregunta real: `"probabilidad > 75"` sola devuelve 6 de 12
filas; con `"gaming"` añadido, cero y dicho.

**Pendiente, y es decisión de producto, no de código:** si `"gaming"` debe
significar "todo menos IRL, Just Chatting, Always On y Música". Inventar esa
taxonomía por cuenta propia sería el mismo pecado que se acaba de corregir.

### El panel de Twitch no reponía los huecos

`fill_tracking_cohorts()` calculaba cuántos huecos había y tomaba los primeros
candidatos **sin excluir los canales que ya se siguen**. El upsert posterior solo
los reactivaba o actualizaba, así que el hueco seguía ahí y el panel quedaba
corto — menos cobertura y un dataset predictivo sesgado hacia los canales
antiguos.

Ahora se excluyen los activos antes de repartir, y cada elegido se suma al
conjunto para que dos grupos distintos no tomen el mismo canal.

**Suite: 96 pruebas, todas verdes.**

---

## 2026-09-26 — El archivado recortaba la base equivocada, y la reja de regresión llevaba semanas roja

**Commit:** pendiente. Dos hallazgos más de la misma revisión externa del
2026-09-25. Ninguno toca cifras publicadas.

### El archivado apuntaba a la copia muerta

`archive_old_signal_observations()` tenía `DEFAULT_DB_PATH` por omisión. Desde
el 2026-08-25 `signal_observations` vive en su propio archivo, así que durante un
mes el archivado habría recortado **la copia congelada de la base principal —la
que ya nadie lee— mientras la base viva crecía sin tope**: 51 GB al 2026-09-26,
~1.9 GB al día.

Ahora apunta a `SIGNALS_DB_PATH`. Para tocar la copia muerta hay que pasar la
ruta a mano, y lo que corresponde con ella no es archivarla sino borrarla.

### La base de señales no entraba en ningún respaldo

`backup --what` solo aceptaba `archive`, `live` y `both`. Los 51 GB de
histórico de señales no tenían copia en ninguna parte. Ya acepta `signals`.

**Deliberadamente fuera de `both`**, y esto es lo importante: hoy los respaldos
viven en el **mismo disco** que la base de señales. Copiarla allí protege de una
corrupción del archivo, no de que ese disco falle. Para que sea un respaldo de
verdad hace falta `--dest` a otro disco. Queda la capacidad; **la protección
real sigue pendiente de un destino**.

### La reja de regresión: un mes en rojo por comentarios de CSS

El detector de texto sin traducir marcaba el bloque `<style>` del tablero: 34,182
caracteres cuyos **comentarios de CSS están en español** (`/* Un score se
recalcula hoy... */`). No es texto que nadie lea en pantalla.

Ahora se descartan los comentarios de CSS y de HTML antes de buscar. Un bloque
de HTML con prosa visible en español **sigue detectándose**, que es lo que la
prueba existe para encontrar; se añadieron seis pruebas que fijan esa frontera.

Importa más de lo que parece: una reja que siempre está roja no protege de nada,
porque una violación nueva de verdad pasa inadvertida entre el ruido. **La suite
queda en 89 pruebas, todas en verde** — la primera vez desde que se lleva esta
bitácora.

---

## 2026-09-25 — La ventana de medición era 2.8 h más corta de lo declarado

**Commit:** pendiente. **Se declara seis días antes de la lectura**, con el
número medido antes de tocar una sola línea.

Una revisión externa del código encontró que `due_at` se guarda con desfase
local y se comparaba **como texto** contra un instante en UTC:

```
due_at   '2026-09-25T06:00:00-05:00'   (= 11:00 UTC)
ahora    '2026-09-25T06:10:19+00:00'
```

Como cadenas, `'06:00:00-05:00' < '06:10:19+00:00'`, aunque ocurra cinco horas
después. La tarea horaria de las 06:10 UTC seleccionaba el lote del día cuando
su ventana aún no había cerrado — cierra a las 09:00 UTC.

**Medido sobre la cohorte pre-registrada, antes de corregir:**

| | |
|---|---|
| evaluadas antes de cerrar su ventana | **315 de 360** |
| adelanto promedio | **2.79 h** (máx. 2.83 h) |
| ventana real medida | 6 d 21 h en vez de 7 d |

**La dirección del sesgo va contra el sistema.** Un máximo sobre una ventana más
corta solo puede ser menor o igual, nunca mayor: el pico se midió de menos. Y
como la tasa base sí usa 7 días exactos, el lift publicado también sale por
debajo del real.

**Cuánto costó, recalculado con la ventana completa** (solo lectura, sin tocar
el ledger): de las 315, **9** tenían un pico mayor en el tramo que faltaba,
**2** cambiaban de resultado y **1** pasaba a ser acierto. Un acierto sobre 345:
la cohorte iría de 28.4% a 28.7%.

**Qué se corrige y qué no.** Se corrige la comparación —instantes, no texto— en
los **cuatro** sitios donde estaba el mismo defecto: la selección para evaluar,
el detector de inanición, el health check y el reporte matutino. Ninguno tocaba
la vara ni el ranking.

**No se recalculan las dos predicciones afectadas.** Reescribir resultados ya
publicados en la cadena, seis días antes de la lectura y en dirección favorable,
se ve peor que el error — aunque sea correcto. Queda declarado y se lee el 1 de
octubre con la cifra tal como está.

**Efecto visible desde hoy:** las evaluaciones pasan de ocurrir a las 06:10 UTC
a hacerlo a las 11:10, que es cuando de verdad vencen. Los resultados del día
aparecerán unas cinco horas más tarde que antes.

**Consecuencia para la cohorte:** las ~345 ya resueltas se midieron con 6 d 21 h
y las ~105 restantes se medirán con los 7 días declarados. La inconsistencia se
declara aquí; corregir hacia la regla pre-registrada pareció mejor que sostener
un defecto conocido por homogeneidad.

---

## 2026-09-23 (2) — El health check ya mata los procesos huérfanos

**Commit:** pendiente.

El patrón se repitió todo septiembre: el Task Scheduler mata una tarea al
cumplirse su límite, pero eso solo termina el `cmd.exe` que la envuelve. El
python hijo sobrevive **sin supervisión y sin límite**, con la base abierta.

| fecha | daño medido |
|---|---|
| 09-11 | tres huérfanos impedían truncar el WAL ("ocupada" cada 10 min) sin escribir nada |
| 09-21 | WAL de 456 MB: el lote tardó 47 min y `attention_index` pasó de 3 s a 926 s |
| 09-23 | un escaneo de mercado llevaba **15 h** escribiendo ~2 MB/s; el tablero tardaba minutos por clic |

Hasta hoy la única salida era que el dueño corriera `taskkill` como
administrador. El health check corre como **S4U, el mismo usuario que lanzó esos
procesos**, así que puede matarlos él.

**Dos reglas, y ninguna es "está huérfano, muere":**

1. **Viejo de verdad** (más de 8 h). Ningún trabajo legítimo dura tanto: el
   límite más largo de una tarea de python es 1 h.
2. **Huérfano y quieto**: más de 2 h de vida y sin consumir CPU ni tocar disco
   entre dos revisiones consecutivas (20 min de separación). Esto atrapa al que
   solo ocupa —el caso del 09-11— sin tocar al que trabaja, como el escaneo de
   mercado en sus primeras horas.

**Nunca se toca** el tablero, nada cuyo padre siga vivo, ni nada cuya línea de
comandos no se pueda leer. Ante la duda no se mata: un falso positivo cuesta el
lote del día; un falso negativo cuesta un tablero lento que el dueño ya sabe
reportar. 13 pruebas, una por cada caso de "no se toca".

**Verificado en la tarea real**, no solo en pruebas: al dispararla, la corrida
S4U no emitió el aviso de "no se puede leer la línea de comandos" —que es el
discriminador— y no mató nada, porque el único huérfano era el tablero. Desde
una sesión interactiva ese mismo código sí emite el aviso, porque ahí las líneas
de comando de un proceso S4U no se pueden leer.

---

## 2026-09-23 — El vigilante mató el respaldo que debía proteger

**Commit:** pendiente.

El respaldo semanal salió **corrupto**, y lo atrapó la verificación automática
en su primera corrida real:

> `[CRIT] El respaldo mas reciente NO paso la verificacion: FALLIDA:
> quick_check=*** in database main ***`

**La cadena, minuto a minuto:**

| hora | qué pasó |
|---|---|
| 04:40 | la ventana apaga las 7 tareas |
| 06:05 | el lote termina — tardó **85 min**, con el disco saturado |
| 06:23 | el vigilante ve 103 min sin reactivación, da la ventana por muerta y **enciende las 7 tareas** |
| 06:05–07:10 | la ventana, viva, hace la copia secuencial de 30 GB |
| 06:45 / 06:55 / 07:05 | colector de YouTube, escaneo de mercado y colector de Twitch **escriben en la base** |
| 07:10 | copia terminada, marcada para verificar |
| ~09:20 | el health check lanza la verificación |
| ~09:40 | `quick_check` la rechaza |

La copia secuencial **exige que nadie escriba**. Su propio comentario lo
advertía: *"una copia hecha bajo escritura no falla — sale corrupta y parece
buena"*. Esta vez no lo pareció, porque desde el 2026-09-15 se verifica.

**La causa raíz.** `check_stuck_maintenance()` decidía solo con el reloj:
pasados 90 minutos daba la ventana por muerta. Contar minutos **no distingue
"lenta" de "muerta"**. El archivo de estado guardaba el `pid` de la ventana
desde el principio; nadie lo miraba.

**El arreglo.** Si el proceso vive, no se toca, por lento que vaya — y se avisa
como `warning` en vez de reparar. Con dos defensas contra el reciclaje de PID de
Windows: se comprueba que el ejecutable sea `powershell`, y por encima de un
tope absoluto de 6 h se repara igual. Si no se puede consultar el nombre —un
proceso S4U visto desde una sesión interactiva responde "acceso denegado"— se
cree al PID: equivocarse hacia ese lado retrasa una reparación; hacia el otro
corrompe respaldos. 15 pruebas.

**Lo que esto dice del diseño.** El vigilante se construyó el 2026-08-06 para
reparar una ventana muerta, y su riesgo conocido siempre fue interrumpir una
viva: el umbral ya se había subido de 15 a 90 minutos por eso mismo. El error
fue creer que el problema era el *número* y no el *criterio*.

**Lo que sí funcionó:** todo lo construido la semana pasada. El resumen del
respaldo imprimió sin reventar, la ventana dejó la marca, el health check lanzó
la verificación fuera de la ventana entre las 09:00 y las 19:00, y reportó el
fallo como crítico. **Sin ese trabajo, hoy tendríamos un respaldo corrupto
presentándose como bueno durante ocho días.**

**Estado:** la base viva está intacta — lo que falló es la copia. El respaldo
verificado del 2026-09-15 sigue en el disco externo.

**El archivo corrupto se borró el mismo día** (30.70 GB), con el visto bueno del
dueño y tras comprobar que el manifiesto lo declaraba `FALLIDA` y que el
respaldo bueno seguía presente. No era solo higiene: la ventana decide si copiar
mirando la fecha del respaldo **más nuevo**, así que dejarlo habría hecho que el
sistema se creyera protegido por otros ocho días con un archivo roto.

El detalle del fallo no deja duda de qué clase de daño fue — `invalid page
number` y `2nd reference to page` repartidos por dos árboles distintos: páginas
que cambiaron mientras se las copiaba. No es un disco defectuoso.

**El límite de la ventana se subió a 6 h ese mismo día** (`fix_maintenance_time_limit.ps1`,
verificado: `PT6H`, principal S4U, disparador y acción intactos). Estaba previsto
para cuando llegara el SSD, pero al borrar la copia corrupta el respaldo volvía a
tocar al día siguiente, y con 4 h el límite habría vuelto a cortar las etiquetas
al final — como pasó el 15 y el 23. Las dos defensas quedan separadas y hacen
cosas distintas: el vigilante arreglado evita que la copia salga corrupta; el
límite más ancho evita que se corten los pasos de después.

---

## 2026-09-18 — Una tarea apagada a propósito dejó de gritar, y una apagada sin permiso empezó a hacerlo

**Commit:** pendiente.

`Archive Signal Observations` corrió por última vez el 2026-08-26, falló, y se
apagó después. Durante **23 días** el health check repitió cada 20 minutos ese
código de error de una tarea que ya no corre. Peor que el ruido: por cómo estaba
escrito el chequeo, encontrar ese código viejo hacía un `continue` que **impedía
revisar cualquier otra cosa** de esa tarea. Un aviso permanente no vigila, tapa.

Lo que cambia no reduce la vigilancia, la aumenta:

| situación | antes | ahora |
|---|---|---|
| apagada a propósito | aviso eterno por un código de agosto | `ok`, "deshabilitada a propósito" |
| **cualquier otra deshabilitada** | nada hasta pasarse su cadencia | **crítico de inmediato** |
| si se reactiva y falla | aviso | aviso igual |

La segunda fila es la que importa: es el fallo del 2026-08-06, ocho tareas
apagadas 4.5 horas en silencio. Antes, una tarea deshabilitada con su último
código en 0 no decía nada hasta que se pasara su cadencia; ahora se reporta al
instante.

La lista de apagadas a propósito vive en el código (`TAREAS_APAGADAS_A_PROPOSITO`),
no en un archivo suelto, para que apagar algo sea una decisión que se lee en el
repositorio. Tiene una sola entrada. El riesgo que queda, dicho para que quede
dicho: si algún día esa tarea debe volver a correr y no se saca de la lista,
nadie lo va a recordar.

La decisión de clasificación se extrajo a `clasificar_tarea()` para poder
probarla sin Task Scheduler, que es justo la parte que no se puede simular:
9 pruebas nuevas.

**Efecto inmediato:** el único aviso que queda en el health check es real —
`Collect Requested Topics` cortada por su límite de tiempo— en vez de estar
escondido detrás de uno permanente.

---

## 2026-09-16 — Las 225 predicciones de la cohorte no son 225 pruebas independientes

**Commit:** pendiente. **No cambia nada medido ni publicado**: se declara antes
de la lectura del 2026-10-08, que es cuando una limitación todavía cuenta como
honestidad y no como excusa.

Revisando por qué la cohorte saltó de 27.7% a 30.7% en un día —un número bueno
de más merece más auditoría que uno malo— el salto resultó legítimo: las
etiquetas están sanas (entre **8.0% y 11.1%** de éxito por día ancla, coherente
con la tasa base de 10.2%) y los lotes recientes, 26.7% tres días seguidos, caen
dentro del rango ya observado, que va de **6.7% a 33.3%** por lote.

Pero al mirar de cerca aparecieron dos cosas sobre la **independencia** de la
muestra:

**1. Siete aciertos son el mismo despegue contado otra vez.** Dos predicciones
del mismo creador con ventanas solapadas pueden mirar el mismo pico:

| creador | pico | lotes |
|---|---|---|
| eslcs | 8,324 | 08-27, 08-30, 09-02 |
| lacyoffline_ | 2,393 | 09-07, 09-08 |
| franciscoow | 1,632 | 09-03, 09-07 |
| allinyonok | 483 | 09-05, 09-06 |
| kusaka6e | 1,172 | 09-02, 09-03 |
| viperriven247 | 479 | 08-30, 09-02 |

De 69 aciertos hay **62 despegues distintos**. Contando cada uno una sola vez la
tasa pasa de **30.7% a 27.6%** — sigue muy por encima del 10.2% de la tasa base,
pero la cifra publicada está unos 3 puntos arriba de lo que sostiene un conteo
por evento.

**2. El intervalo es más estrecho de lo que la muestra justifica.** Hay **155
creadores distintos en 225 predicciones**, y 44 aparecen más de una vez. Las
pruebas correlacionadas reducen el tamaño efectivo de muestra, así que el IC real
es algo más ancho que el ±6 pp que se imprime.

**Qué NO se hace.** No se toca la regla, que es lo correcto: la unidad
pre-registrada es la predicción, no el creador, y cambiarla ahora sería mover la
portería con el resultado a la vista. La tasa base se calcula sobre las mismas
anclas repetidas, así que el sesgo no es obviamente a favor.

**Qué sí se hará el 2026-10-08:** publicar las dos cifras, por predicción y por
despegue distinto, y decir que el intervalo es una cota optimista. Para un
pre-registro futuro, la unidad debería ser el evento o imponerse un enfriamiento
por creador.

**CUMPLIDO el 2026-10-01** (la lectura llegó por las 450 vencidas, antes de la
fecha límite). Se publicaron las dos cifras — 26.7% por predicción y 23.1% por
despegue distinto, 16 aciertos colapsados de 120 — y el intervalo optimista se
contrastó contra un bootstrap por conglomerados. Ver la entrada del 2026-10-01 en
los cambios de arriba.

---

## 2026-09-15 — Un mes de respaldos buenos reportados como fallidos, y nunca verificados

**Commit:** pendiente.

El respaldo semanal de la base viva copió bien los tres últimos domingos, y los
tres quedaron en el log como fallidos:

| fecha | log de la ventana | archivo real en F: |
|---|---|---|
| 2026-08-30 | `RESPALDO FALLIDO` | 29.63 GB, completo |
| 2026-09-07 | `RESPALDO FALLIDO` | 29.99 GB, completo |
| 2026-09-15 | `RESPALDO FALLIDO` | 30.32 GB, completo |

**La causa.** Desde el 2026-08-06 la ventana usa `backup_database_offline()`
(copia secuencial) en vez de `backup_database()` (copia por páginas). Las dos
devuelven manifiestos **distintos**: la offline no cuenta filas ni corre
`integrity_check`, a propósito, y deja `sha256` en `None` por encima de 2 GB. El
resumen del comando seguía pidiendo `filas_totales` → `KeyError` **después** de
copiar, renombrar y escribir el MANIFEST → código de salida 1.

**La consecuencia que importa.** La ventana solo verifica un respaldo si la copia
salió con código 0 (`$script:copiaHecha = ($cod -eq 0)`). Con el `KeyError`
nunca salió con 0, así que **el paso de verificación no ha corrido ni una vez**:
el log no tiene una sola línea de "verificando el respaldo". Los respaldos
existen y tienen el tamaño correcto, pero ninguno se ha comprobado. La nota de
pausa de integridad que dice *"Hay respaldo verificado en F:"* no tiene respaldo
en ningún log.

**El arreglo.** `resumen_respaldo()` en `backup.py` entiende los dos manifiestos
y cada dato opcional aparece solo si existe. Prueba nueva con el manifiesto
**real** del 15 de septiembre, que es exactamente la forma que fallaba.

**Decidido el mismo día: la verificación sale de la ventana.** Al quitar el
error, el respaldo del 2026-09-22 habría disparado por primera vez un
`quick_check` sobre ~30 GB por USB (6,397 s sobre 21.5 GB) dentro de una ventana
con límite de 4 h que ese día ya gasta ~50 min copiando. Con el mismo principio
que el vigilante de la ventana —la protección vive fuera del proceso que puede
morir—:

1. La ventana, si la copia sale con código 0, solo deja la marca
   `data/respaldo_por_verificar.json`.
2. El health check, la única tarea que la ventana nunca apaga, ve la marca y,
   sin ventana corriendo y entre 09:00 y 19:00, lanza `verify-pending-backup`
   como proceso independiente.
3. Esa verificación escribe un candado con su PID; borra la marca solo si
   terminó —bien o mal—, y la conserva si revienta, para reintentar.

Si el MANIFEST dice `FALLIDA`, el health check lo marca crítico; si una marca
lleva más de 3 días, avisa. Dos trampas cubiertas por pruebas: en Windows
`os.kill(pid, 0)` **mata** el proceso en vez de preguntar, y un proceso S4U visto
desde la sesión interactiva responde "acceso denegado", que significa que existe.

**El respaldo de hoy se verificó a mano y pasó** — la primera verificación de un
respaldo de la base viva desde el 2026-08-06:

```
draconfly_20260915T094308Z.sqlite3
  quick_check: ok
  prediction_ledger      885 (origen 885)   twitch_horizon_labels 35,502 (35,502)
  twitch_tracked_channels 5,441 (origen 5,475)
VERIFICACION OK   —   356 min
```

Ninguna tabla tiene MÁS filas que el origen, que es lo que delataría una copia
hecha bajo escritura; los 34 canales de diferencia son crecimiento normal de la
base viva durante las 6 h posteriores a la copia.

**356 min, no las 3-4 h estimadas.** La estimación se quedó corta al doble y el
número medido quedó en el comentario de `HORA_DESDE/HORA_HASTA`: con 6 h reales,
un lanzamiento a las 18:59 termina cerca de la 01:00, todavía con ~3.5 h de
margen antes de la ventana.

**Efecto colateral del mismo día.** La copia de 50.6 min, sumada a un refresco de
cachés de 77 min con el disco saturado, empujó las etiquetas incrementales hasta
las 06:50, y el límite de 4 h mató la ventana a las 08:40 con ellas a medias. Por
eso el 15 amaneció con 15 vencidas sin tasa base. La ventana del 16 las cubre:
reconstruye siempre los últimos 12 días.

---

## 2026-09-14 — El reporte ahora verifica la prueba, no solo el archivo

**Commit:** pendiente.

La publicación de las 06:10 escribió y verificó 30 eventos nuevos (1,637 en
total), y el límite de 15 min de la tarea la cortó antes del `git add`. GitHub
se quedó en 1,607. A las 21:38 el `morning-report` dijo **"todo en orden"**,
porque solo verificaba la cadena en disco.

Eso es media prueba. El encadenamiento por hash demuestra que nada se alteró; el
push, fechado por el reloj de GitHub que no controlamos, es lo que demuestra
**cuándo** existía cada evento. Se publicó a mano a las 21:40 con el mismo script
de la tarea (commit `e7e0ea6`). Los 15 pronósticos del día se verifican el
2026-09-21, así que igual quedaron públicos una semana antes de conocerse su
resultado.

El reporte agrega una línea `GitHub` con tres comprobaciones, todas sin red:

- **eventos sin subir:** cadena local contra `origin/master`, que se actualiza
  sola con cada push exitoso (esta máquina es la única que publica);
- **prefijo:** el último hash publicado tiene que coincidir con el local en esa
  misma posición; contar no basta;
- **último push:** cada publicación sube el MANIFEST aunque no haya eventos, y
  corre a las 06:10 y 22:10, así que más de 17 h sin commit en `public/`
  significa que la tarea dejó de funcionar.

Probado contra el commit `9f5843f` (1,607 eventos): el reporte habría dicho
*"30 eventos sin subir a GitHub; GitHub sin publicar hace 23.7 h"*.

La causa del corte de las 06:10 no está establecida: se atoró entre la
verificación y el `git add`, un paso que funcionó las tres mañanas anteriores.
Un solo caso no alcanza para afirmar nada; si se repite, se investiga.

---

## 2026-09-12 — Lo que la mudanza del 25 de agosto dejó atrás

**Commit:** pendiente.

Revisando por qué el health-check marcaba YouTube en rojo aparecieron tres
defectos encadenados, todos del mismo origen: la mudanza de
`signal_observations` a su propio archivo (2026-08-25) movió la tabla pero
**dejó cosas apuntando al lugar viejo**, y ninguna se notaba en la base viva.

**1. El monitor de YouTube medía el reloj equivocado.** `observed_at` no es la
hora de recolección: `four_hour_bucket()` trunca al múltiplo de 4 h más bajo,
así que es la **etiqueta del casillero** de observación. La corrida de las 19:45
UTC del 12 de septiembre escribió en el casillero de las 16:00, y el monitor la
leyó como *"sin datos hace 338 min"* cuando acababa de terminar bien (código 0,
4,819 snapshots).

Consecuencia: este chequeo llevaba avisando **entre 18 y 27 veces diarias desde
antes del 3 de septiembre**, sin una sola falla real detrás. Es el mismo pecado
que el escaneo de mercado el 2026-09-11: un monitor que grita todos los días no
vigila nada, entierra la alarma de verdad.

Ahora se compara contra el **fin** del casillero (etiqueta + 4 h). La edad sana
va de 0 a ~225 min, una corrida perdida da ~465 (alerta) y dos dan ~705
(crítico), que es justo lo que 300/600 pretendían decir. No hubo que mover los
umbrales, solo medir bien.

**2. `init_db()` llevaba 18 días roto para cualquier base nueva.** El esquema
principal se quedó con el índice `idx_signal_observations_series_time` sobre una
tabla que ya no declara. En la base viva el índice existe de antes, así que
`if not exists` no hace nada y nadie se entera. Sobre una base **nueva**,
`executescript()` muere con `no such table: main.signal_observations`.

Eso significa que una instalación limpia o una restauración desde respaldo
habrían fallado. Se descubrió porque dos pruebas de `predictive_labels` llevaban
18 días en rojo por esa línea. `init_materialized()` tenía exactamente el mismo
defecto con `idx_signal_observations_phrase_latest`. Los dos índices eran
además redundantes: `SIGNALS_SCHEMA` ya declara equivalentes.

**3. Una gráfica llevaba 18 días dibujando una serie muerta.** La mudanza copió
la tabla al archivo nuevo pero **nunca borró la original**, y `load_signal_series()`
en el tablero seguía leyéndola con `dashboard_connect`, que apunta a la base
principal. Medido hoy:

| | desde | hasta |
|---|---|---|
| copia en la base principal | 2026-06-06 | **2026-08-25T15:00** |
| archivo de señales (vivo) | 2026-06-06 | **2026-09-12T11:00** |

Y no era solo un rezago de fechas. Medido sobre una serie concreta
(`topic='fortnite'`, `phrase='games'`):

| ruta | rango | filas |
|---|---|---|
| archivo de señales | 2026-06-20 → 2026-09-12 | **30** |
| base principal | 2026-06-20 → 2026-06-20 | **2** |

La gráfica dibujaba **dos puntos donde había treinta**. Se veía **plana, no
rota**, que es la forma más cara de equivocarse en un tablero: nada avisa. Ahora
usa `connect_signals_read()`.

**Lo que queda pendiente y no se tocó.** Esa copia congelada sigue ocupando
espacio en la base principal de 30 GB. Borrarla es destructivo y es decisión del
dueño, no mía; queda anotado con la medición que la respalda.

**La lección.** Los tres defectos son invisibles en la base que ya existe y solo
aparecen en una base nueva o mirando fechas con cuidado. Una migración no
termina cuando los datos llegan al destino: termina cuando nada apunta al
origen. Conviene que la suite corra sobre una base nueva justamente por esto.

---

## 2026-09-10 — Las señales se mudan al disco externo, y un incidente propio

**Commit:** pendiente.

**El problema.** La base de señales pasó de 13.1 GB el 30 de agosto a 29.2 GB
más 2.7 GB de WAL el 9 de septiembre: **1.88 GB diarios**. Con 48 GB libres en
C:, el disco se llenaba en **26 días** — tres antes de la fecha de lectura del
experimento. Y sin disco no hay lote diario.

El 84% de ese crecimiento era del escaneo horario de mercado (`_market_scan`),
12.6 M de filas en cinco días. Las 20 categorías que se pusieron en vigilancia el
30 de agosto aportaban ~1.3 M: la proyección de 2.6 GB/mes para ellas era
correcta.

**Lo que se hizo, y por qué mover en vez de archivar.** Archivar recorta el
histórico, que es justamente el activo que no se compra ni se acelera. F: tenía
773 GB libres, así que la base entera se mudó allí. `SIGNALS_DB_PATH` ahora
resuelve en tiempo de ejecución y cae de vuelta a la copia local si el disco
externo no está; la ausencia no rompe nada porque el lote diario nunca consulta
esa base.

Verificado antes de borrar el original: `quick_check ok`, **79,764,364 filas** y
el mismo rango de fechas en ambos lados. C: pasó de 56 a 85.2 GB libres.

Y una medición inesperada: recorrer los 29 GB tomó **3.8 h en el disco externo
por USB y 6.7 h en el disco interno**. El disco mecánico de C: bajo carga es
peor que un USB, lo cual refuerza la mudanza en vez de cuestionarla.

**El incidente, que fue error mío.** Lancé esa verificación de 10.5 horas a las
17:03, sin calcular que 29 GB a 18 MB/s no caben en una noche. Estimé 45-60
minutos. La consecuencia se encadenó:

| hora | qué pasó |
|---|---|
| 18:10–20:10 | la evaluación horaria se salta: *"la base esta ocupada"* |
| 04:40 | la ventana arranca y desactiva 7 tareas |
| 04:45 | empieza el lote del día y el log se corta ahí |
| 05:30 | el respaldo dispara, pero la ventana lo tenía desactivado |
| 08:00 | el segundo respaldo corre 1 h y su límite lo mata (código 267014) |
| 13:00 | el día llevaba **cero predicciones** |

El lote se emitió a mano a las 14:00 y entró: 15 predicciones, sin hueco. Las 15
vencidas se evaluaron después. Nada se perdió.

**Lo que sí funcionó, y no fue lo que parecía.** El fallo del 2026-08-06 —ocho
tareas apagadas 4.5 horas— no se repitió, pero el mérito no es del bloque
`finally`: el log de la ventana se corta en *"emitiendo el lote"* a las 04:45 y
**nunca escribió "tareas reactivadas"**. Un kill por tiempo límite no ejecuta los
bloques de limpieza de PowerShell, exactamente como se documentó en agosto.

Quien reactivó fue el vigilante externo que se construyó por esa lección:
`data/maintenance_state.json` más `check_stuck_maintenance()` en
`health_monitor.py`. Disparó **21 minutos** después del inicio de la ventana:

> `[CRIT] Ventana de mantenimiento: La ventana empezo hace 21 min y nunca
> reactivo las tareas: se reactivaron 8 automaticamente.`

Es la primera vez que esa protección se ejerce en producción, y funcionó. La
lección de agosto —*la protección tiene que vivir fuera del proceso que puede
morir*— queda validada por un incidente distinto al que la motivó.

El `morning-report`, por su parte, marcó las tres cosas en su línea de veredicto:
sin lote, sin evaluar y sin tasa base.

**Umbrales del monitor que quedaron desfasados por el mismo cambio.** Al pasar el
escaneo de mercado a cada seis horas no se movieron sus umbrales de frescura, que
seguían en 90 min de alerta y 180 de crítico. El chequeo quedó en CRITICAL
permanente, que es la peor falla posible en un monitor: entierra la alarma real.
Se corrigen a 780 y 1560 min. La medición que los justifica: la corrida del
2026-09-10 arrancó 06:55 y terminó cerca de las 14:00, y con la tarea en
`IgnoreNew` las horas intermedias se saltan, así que en la práctica recolecta dos
veces al día, no cuatro.

**La regla que faltaba.** Una operación de disco larga no se lanza en las horas
previas a la ventana de mantenimiento. Este trabajo era mantenimiento legítimo
durante el congelamiento, pero el momento estuvo mal elegido: casi cuesta el
único hueco que este proyecto no se puede permitir.

**Efecto en el registro.** El lote del 2026-09-10 lleva `issued_at` sobre las
19:00 UTC en vez de las 09:47 habituales, y se construyó sobre el snapshot de la
tarde. No invalida la medición —la ventana sigue empezando donde termina la
observación— pero es un día distinto de los demás y queda visible.

---

## 2026-09-08 — El 17.6% histórico nunca fue la tasa del sistema actual

**Commit:** pendiente.

**Qué disparó la revisión.** La cohorte pre-registrada llegó a n=105 con 26.7%
de acierto, muy por encima del 17.6% retrospectivo. Lo normal es lo contrario:
una cifra retrospectiva está inflada por haber elegido la vara mirando los datos,
así que hacia adelante suele **bajar**. Que suba pide explicación antes de
creérsela.

**Lo que se descartó primero.** Que el sistema hubiera cambiado bajo el
experimento. `horizon_model.joblib` es del 2026-08-05 y ninguna tarea programada
lo reentrena — se verificó. El modelo está congelado desde antes del
pre-registro.

**Lo que sí ocurrió.** El acierto sube de forma monótona desde finales de julio,
y la tasa base del universo no:

| semana | n | acierto | tasa base del universo |
|---|---|---|---|
| W30 | 53 | 9.4% | 9.0% |
| W31 | 90 | 11.1% | 7.7% |
| W32 | 105 | 17.1% | 8.7% |
| W33 | 105 | 25.7% | 7.7% |
| W34 | 90 | 27.8% | 10.8% |
| W35 | 30 | 30.0% | 10.2% |

La base oscila entre 7.7% y 10.8% sin tendencia, así que **no estaba más fácil
para todos**. Lo que mejoró fueron los insumos del mismo modelo: el piso de 50
espectadores (2026-08-01), el WAL de 31 GB, el lote que tardaba 399 minutos y
llegaba con snapshots viejos, y las etiquetas que llevaban dos semanas sin
reconstruirse.

**Y el detalle que importa para el experimento:** ese ascenso terminó en la
W33–W34, *antes* del pre-registro del 26 de agosto. Para cuando se congeló, el
sistema ya corría entre 25% y 28%.

| cohorte | acierto | IC95 |
|---|---|---|
| emitidas antes del 2026-08-26 | 68/401 = **17.0%** | 13.6 – 20.9 |
| emitidas desde el 2026-08-26 | 28/105 = **26.7%** | 19.1 – 35.8 |

**Qué se afirma y qué no.** El 26.7% prospectivo **no es una mejora ni suerte:
es continuidad** con lo que el sistema ya venía haciendo desde mediados de
agosto. Lo que estaba mal era usar el promedio histórico como si describiera al
sistema de hoy.

El 17.6% **no se corrige ni se retira**: es el histórico verdadero y se sigue
publicando. Lo que se añade es qué es — el promedio de un sistema que se estaba
arreglando, y por eso subestima al actual. Decir en cambio "en realidad vamos en
26.7%" sería exactamente la lectura selectiva que este archivo existe para
impedir.

**Señal de que son poblaciones distintas y no una cifra inflada:** el intervalo
prospectivo (19.1 – 35.8) ya casi no contiene al 17.6%.

**Lo que NO cambia.** La fecha de lectura sigue siendo el 2026-10-08. Este
hallazgo no adelanta nada ni justifica leer antes.

---

## 2026-09-05 — Se fija CUÁNDO se lee el resultado, con el número ya a favor

**Commit:** pendiente — se escribe antes de saber si el resultado aguanta.

**El agujero.** El 2026-08-26 se fijó la vara pero no *cuándo se lee*. El
criterio quedó como "el lift se da por demostrado si el intervalo de la
diferencia queda entero por encima de cero" — sin decir en qué momento se
comprueba eso. Y "esperar a que el intervalo excluya el cero, revisando cada
mañana" es una regla que se cumple sola.

**Medido con simulación**, con la tasa verdadera IGUAL a la tasa base, o sea sin
ningún efecto real, mirando el intervalo cada día conforme llegan lotes de 15:

| días mirando | cruza el cero por azar |
|---|---|
| 5 | 9.1% |
| 10 | 10.9% |
| 20 | 14.0% |
| 30 | **15.6%** |

Una sola mirada daría ~2.5%. Uno de cada seis experimentos **sin efecto alguno**
acaba cruzando si se mira a diario durante un mes. Es *optional stopping*, y es
la versión temporal del mismo error que se corrigió el 2026-08-26: probar trece
varas y quedarse con la mejor.

**Lo que se declara desde hoy.**

> El resultado de la cohorte pre-registrada se lee el **2026-10-08**, o al
> alcanzar **450 predicciones vencidas**, lo que ocurra primero. Las lecturas
> diarias son monitoreo, no resultado. Si el intervalo cruza el cero antes y
> vuelve a cruzarlo después, ninguna de las dos cosas cuenta.

**Por qué hoy y no en octubre.** El 2026-09-04 el veredicto pasó a `supera` con
n=45 (lift +11.0 pp, IC +1.2 a +25.1) y el 09-05 se mantuvo con n=60 (+10.6 pp,
IC +2.0 a +22.6). O sea que **la cifra ya está a favor**, y comprometerse ahora a
esperar cuesta algo. Declarar la misma regla en octubre, con el resultado en la
mano, no valdría nada.

**Qué NO cambia.** Nada operativo. El veredicto solo elige un texto en pantalla
—se verificó: `record-predictions` y `evaluate-predictions` no lo consultan— así
que el lote diario, la evaluación al vencer y todo lo que muestra el Investor
Demo siguen igual y siguen actualizándose. Ninguna predicción queda en espera.

**Qué sí cambia en pantalla.** El veredicto se muestra como **provisional** hasta
la fecha de lectura. Sin eso, la casilla diría `supera` un día y `no concluyente`
al siguiente, y quien la viera dos veces concluiría que el sistema es errático
cuando lo errático sería leer un intervalo de veinte puntos como si fuera una
respuesta.

**CUMPLIDO el 2026-10-01.** Se disparó la primera de las dos condiciones — 450
vencidas — siete días antes de la fecha límite. Se esperó 26 días desde esta
declaración sin tocar la vara, el modelo ni la selección, y sin leer el resultado
como si fuera definitivo. El veredicto quedó en `supera`, ya sin la etiqueta de
provisional. Ver la entrada del 2026-10-01 en los cambios de arriba.

---

## 2026-08-30 — P2 (Continuación): se define el episodio ANTES de medirlo

**Commit:** pendiente — esta nota se escribe antes de que exista una sola cifra
pre-registrada de P2.

**La pregunta.** P1 responde *"¿este creador va a romper?"*. P2 responde la
siguiente, que es la que un comprador realmente paga: *"ya rompió — ¿todavía
vale la pena entrar, o llegué tarde?"*. Para una marca, saber que alguien ya
creció tiene valor limitado; saber si le queda recorrido es una decisión de
dinero.

**Qué es un episodio de breakout.** Un canal recibe un ancla por día, así que un
mismo despegue aparece como diez anclas `hit_strong` seguidas. Contarlas como
diez episodios inflaría cualquier resultado.

- **Episodio** = racha máxima de anclas `hit_strong` del mismo canal, tolerando
  huecos de hasta 1 día.
- **Detección** = el **primer** ancla de la racha, no el de mayor pico.
- **Referencia P** = el pico de la ventana de breakout de ese primer ancla.

El primero, y no el máximo, a propósito: la pregunta del producto es *"lo vimos
en 52K, ¿queda recorrido?"*, así que el punto de comparación tiene que ser el
momento en que lo habríamos avisado. Tomar el pico máximo pregunta otra cosa
—*"¿superará su mejor día?"*— que es más difícil y no es la que se vende.

**Esa sola elección movía la tasa base de 14.3% a 2.6%.** Por eso se fija por
escrito antes de medir, y por eso queda registrado que se probaron las dos.

**Qué cuenta como continuación**, sobre `[detección+7d, detección+21d]` contra P:

| resultado | criterio |
|---|---|
| CONTINUATION | pico posterior ≥ 1.5 × P |
| PLATEAU | pico posterior ≥ 0.5 × P |
| REVERSION | pico posterior < 0.5 × P |
| OFFLINE | sin un solo snapshot en vivo |

Solo snapshots con `live = 1`: un canal apagado reporta 0, y eso no es una caída
de audiencia, es que no estaba al aire.

**El horizonte es 14 días, no 30/60/90.** Los snapshots empiezan el 2026-07-11.
A 30 días hay 241 episodios etiquetables; **a 60 y a 90 hay cero**, y los habrá
a finales de octubre y de noviembre. Publicar hoy una probabilidad a 60 días
sería inventarla.

**La tasa base, medida sobre el histórico:**

| resultado | n | % de los que siguieron al aire |
|---|---|---|
| CONTINUATION | 47 | **14.3%** (IC95 10.9–18.5) |
| PLATEAU | 166 | 50.6% |
| REVERSION | 115 | **35.1%** |
| OFFLINE | 7 | — |

Sobre 335 episodios evaluados de 531 detectados.

**Qué hace esto prometedor.** Solo 1 de cada 7 sigue acelerando, así que hay
ventaja que demostrar — no es una moneda al aire, que era el problema de la vara
vieja de P1. Y 1 de cada 3 se desploma: *"no entres"* es tan vendible como
*"entra"*.

**Qué NO se afirma todavía.** Nada. Las cifras de arriba son retrospectivas y la
definición de episodio se fijó mirando ese mismo histórico. Lo que valdrá como
evidencia son los episodios detectados **desde el 2026-08-30**, con esta
definición ya cerrada. Hoy son cero.

**Qué NO cambia.** P1 no se toca. Su cohorte pre-registrada del 2026-08-26 sigue
intacta, con 75 predicciones emitidas y la primera venciendo el 2026-09-02. P2
tiene tabla propia (`continuation_ledger`), vara propia y reloj propio.

**Un hallazgo que hay que verificar con más datos.** Entre los episodios
evaluados, los breakouts **más grandes** son los que más se desploman: el
crecimiento mediano de los que revirtieron fue mayor que el de los que
continuaron. Es reversión a la media y sería comercialmente valioso —diría que
el breakout más llamativo es la peor apuesta— pero con esta muestra es una
hipótesis, no un resultado.

---

## 2026-08-01 — Trend Uncertainty Index (TUI): recolección iniciada

**Commit:** `e2b97d3`

**Qué se empezó a guardar.** Desde esta fecha, cada predicción registra cinco
variables que describen **cuánto sabíamos del creador en el momento de predecir**
(columnas `u_*` en `prediction_ledger`):

| variable | qué captura |
|---|---|
| `u_observations` | lecturas horarias disponibles del canal |
| `u_tracked_days` | días desde la primera observación |
| `u_viewer_cv` | volatilidad de la audiencia en vivo (desviación / media) |
| `u_direction_changes` | veces que el movimiento hora a hora cambió de signo |
| `u_live_ratio` | proporción de lecturas con el canal transmitiendo |

Todas se calculan **únicamente con datos anteriores a la predicción**, de modo que
no pueden contener información del futuro.

**Qué NO se hizo, y por qué.** No se calculó ni se publicó ningún índice. El
2026-08-01 el pipeline empezó a filtrar a creadores con más de 50 viewers
promedio; las 105 predicciones anteriores describen una población que el sistema
ya no produce. Ajustar un índice a ellas sería ajustarlo a un pasado
descontinuado.

**Cómo se modificó el tablero.** Se agregó la pestaña *TUI (incertidumbre)*, que
muestra las variables recolectadas y declara de forma explícita que todavía no
existe un índice. **Ningún indicador publicado cambió.**

**El compromiso, por escrito y por adelantado.** Un índice de incertidumbre solo
se publicará si supera esta prueba contra el historial verificado:

> Las predicciones con TUI bajo deben acertar **significativamente más** que las
> de TUI alto. Cada variable que no aporte a esa separación se descarta en vez de
> conservarse por parecer razonable.

Si la prueba falla, el resultado honesto es no publicar índice alguno y decirlo.
Esta entrada existe para que esa promesa quede fechada antes de conocer el
resultado, y no pueda reescribirse después.

**Cuándo será evaluable.** Cuando existan del orden de 200 predicciones emitidas
bajo el pipeline actual y ya verificadas — aproximadamente tres semanas a un
ritmo de 15 diarias con ventana de verificación de 7 días.

---

# Cómo leer los números de este tablero

- **Precisión de predicción** — porcentaje crudo de aciertos sobre predicciones
  evaluadas. HIT exige crecimiento ≥100% **y** pico ≥100 viewers.
- **Índice de confiabilidad** — límite inferior del intervalo de Wilson al 95%
  sobre ese mismo acierto. Castiga muestras pequeñas a propósito, por eso siempre
  es menor que la precisión cruda, y se acerca a ella conforme crece la muestra.
- **La flecha** compara el acierto de la mitad más reciente de predicciones
  evaluadas contra la mitad anterior.

Ningún número de este tablero es una proyección ni una estimación: todos salen
de predicciones registradas antes de conocerse el resultado y verificadas
después contra datos observados.
