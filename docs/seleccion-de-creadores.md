# Cómo Draconfly elige sus 15 creadores diarios

Versión canónica · 2026-10-04 · verificada contra el código

Nadie escoge a mano. Este documento describe el pipeline exacto y define sin
ambigüedad qué queda congelado durante la cohorte B.

## El embudo

Cada hora, a las **:05**, Draconfly consulta las 10 categorías principales de
Twitch y descubre unos **5,000 canales** activos. De ese universo mantiene un
panel fijo de ~3,090 creadores.

La entrada al panel **no depende de que el creador esté creciendo**: se usa una
regla pseudoaleatoria sobre el hash de su identificador, que no mira
espectadores, crecimiento ni ninguna señal de éxito. Y una vez dentro, **no se
vuelve a sortear**: los integrantes permanecen y la regla solo cubre vacantes.

A cada uno se le toma una fotografía horaria — espectadores, categoría, idioma,
si está al aire — que va construyendo su historial.

```
                                                 medido el 2026-10-03
 panel fijo     ███████████████████████████████  3,090  sorteo por hash
 transmitiendo  ███████                            663  filtro: al aire ahora
 elegibles      ███████                            662  filtro: 24 obs / 7 días
 Top 400        ████                               400  el modelo puntúa a 662
 Top 15 del día ▏                                   15  Score + piso de 50
```

**El corte a 400 no es un sorteo.** El modelo puntúa a **los 662 elegibles** y
se queda con los 400 de mayor `opportunity_score`. Es una truncación del
ranking: como solo se publican 15, descartar el 40% inferior ahorra trabajo sin
escoger a nadie a mano.

**La caída real está en el primer escalón.** De 3,090 a 663 — el 79% del panel
simplemente no estaba transmitiendo en ese instante. Lo que parece el filtro más
duro del sistema es en realidad el horario de la gente.

## El Draconfly Score

Sobre los 400 que sobreviven a la truncación actúa una segunda fórmula, y **aquí
el modelo deja de decidir solo**. Es la que ordena el ranking final:

```
Score = 0.65 × (modelo)
      + 0.12 × (crecimiento proyectado)
      + 6      si hay presencia cross-platform
      + b_sat  por baja saturación de categoría   (máximo 3.75)
      + 10     si la categoría es de evento
      acotado entre 5 y 95
```

**Cross-platform es 6 o 0, no gradual.** El creador tiene presencia en otra
plataforma o no la tiene.

> **Y en la práctica ese término casi no opera.** La tarea que llena la tabla de
> presencia lleva fallando desde el **2026-08-31** —falta un binario de
> Playwright— y los datos no se actualizan desde el **2026-07-26**: cubren **32
> creadores de los ~3,090 del panel**, con 23 marcados como presentes en otra
> plataforma. O sea que el `+6` dispara para alrededor del **0.7%**.
>
> Se descubrió el 2026-10-06, al poner bajo vigilancia tareas que no lo estaban.
> **No invalida ninguna cohorte:** el código de selección está congelado y tanto
> la cohorte A como la B corren con exactamente los mismos datos. Lo que sí hace
> es que este documento describiera como vivo un componente que está casi
> inerte, y por eso queda anotado aquí.
>
> **No se arregla hasta que cierre la cohorte B** (~2026-11-06). Refrescar de
> golpe una tabla congelada dos meses y medio cambiaría qué 15 creadores se
> publican en mitad de la replicación, que es justo lo que una replicación debe
> evitar.

**El bono de saturación llega como máximo a 3.75**, no a 5. Sale de
`max(0, 20 − saturación) × 0.25`, y como la saturación está acotada por abajo en
5, el techo real es `(20 − 5) × 0.25`.

**El bono de evento es +10, y es el más pesado de los tres** — más que
cross-platform y el máximo de saturación juntos.

Después del ranking se aplica un **piso de audiencia: baseline ≥ 50 espectadores
promedio**. Un canal muy pequeño puede tener señales interesantes y aun así no
publicarse.

### Por qué esto importa al describir el sistema

Lo que la cohorte A midió **no es "un modelo de machine learning"**, es el
pipeline completo: modelo más heurísticas ajustadas a mano más piso de
audiencia. Decir *"nuestro modelo acierta el 26.7%"* sería impreciso. Lo correcto
es **"el sistema"**.

No es una debilidad: los rankings comerciales mezclan modelos estadísticos con
reglas de negocio todo el tiempo. Pero la afirmación tiene que corresponder a lo
que se midió.

## Cómo se mide el acierto

Hay **dos varas**, y confundirlas es el error más fácil de cometer con estas
cifras.

| vara | criterio |
| --- | --- |
| **HIT** | creció **+400%** o más y llegó a **250 espectadores** o más |
| **FAIR** | creció **+250%** o más y llegó a esos mismos 250 |
| **ÉXITO** | HIT **o** FAIR |

### La trampa: cada vara tiene su propia tasa base

| criterio | Draconfly | tasa base | lift | razón |
| --- | --- | --- | --- | --- |
| **ÉXITO** | **26.7%** (120/450) | **9.79%** | +16.9 pp | **2.72×** |
| **HIT estricto** | **16.2%** (73/450) | **5.18%** | +11.0 pp | **3.13×** |

El intervalo publicado corresponde al criterio **pre-registrado**, que es
ÉXITO: el lift de +16.9 pp va con un intervalo de **(+11.9, +21.8) pp** por
bootstrap de conglomerados sobre creadores — 20,000 muestras, semilla 20261001.
El piso defendible del lift es **+12.0 puntos**.

No se publica un intervalo para la fila de HIT estricto, porque esa no es la
cifra pre-registrada y su intervalo no quedó en el registro congelado del
2026-10-01. Las dos tasas y la razón sí son derivaciones directas de los
conteos ya leídos.

Dos lecturas falsas que este cuadro impide, y las dos se cometieron antes de
escribirlo:

**"Draconfly tiene 26.7% de HIT."** Falso. Los HIT estrictos son **73**, no 120.
El 26.7% incluye FAIR.

**"El HIT estricto apenas supera al azar."** También falso, y es el error al
revés. Quien lea *16.2%* junto a *tasa base 9.8%* concluye que el HIT casi no
separa. Pero el 9.79% es la tasa base de **ÉXITO**; la de HIT estricto es
**5.18%**.

### Y de ahí sale el hallazgo más fuerte

**El HIT estricto separa más que el ÉXITO: 3.13× contra 2.72×.**

Cuanto más exigente la vara, más se despega Draconfly del fondo. Es exactamente
lo que se espera de un sistema que de verdad discrimina — y exactamente lo que
**no** se vería si fuera ruido, porque el ruido se diluye igual contra cualquier
vara.

### La frase defendible

> En las primeras 450 predicciones prospectivas cerradas, el **26.7%** alcanzó
> al menos el umbral FAIR contra una tasa base de **9.79%**, y el **16.2%**
> alcanzó el criterio HIT más exigente contra una tasa base de **5.18%**.

## La garantía metodológica

Que nadie escoja a mano no basta. Hace falta además que **nadie haya ajustado el
sistema después de ver sus resultados**. Las fechas, verificadas contra el
historial del repositorio:

| pieza | congelada desde |
| --- | --- |
| pesos 0.65 / 0.12 y los tres bonos | **2026-07-26** |
| piso de audiencia y Top 400 | **2026-08-01** |
| modelo `horizon_model.joblib` | **2026-08-06** |
| vara HIT / FAIR | **2026-08-27** |
| *empieza la cohorte A* | *2026-08-26* |

Entre el 26 de agosto y el 24 de septiembre **no hubo un solo commit** en
`intelligence.py` ni en `analytics.py`, que son los dos archivos que deciden qué
se publica.

O sea que la cohorte A **no se usó para desarrollar nada**: el pipeline quedó
fijado entre tres y cuatro semanas antes de su primera predicción.

### La historia completa, en dos frases

> Nadie escoge manualmente los creadores que Draconfly recomienda, y el sistema
> que los seleccionó tampoco fue reajustado después de observar sus resultados.
>
> Las predicciones se registran primero; siete días después se mide qué ocurrió.

### Qué es el sorteo y qué no es

El panel pseudoaleatorio de ~3,090 **no es el producto. Es una protección
metodológica**: impide que el sistema escoja a quién se le mide.

El producto es lo que ocurre **desde los elegibles hasta los 15 nombres**: tomar
una población de creadores activos y encontrar dentro de ella quince señales con
una concentración de éxitos sustancialmente superior a la tasa base.

Insistir demasiado en el sorteo deja la impresión de que el sorteo *es* el
mérito, y no lo es: es la garantía de que el mérito se mide limpio.

## Qué congela la cohorte B

**Todo lo descrito arriba.** Este documento no es solo una explicación: define
sin ambigüedad qué queda prohibido tocar hasta que B cierre, a mediados de
noviembre.

Queda congelado:

- el descubrimiento — 10 categorías, 5 páginas, cada hora
- la regla pseudoaleatoria del panel y los 10 cupos por categoría y banda
- los dos filtros de elegibilidad — en vivo, 24 observaciones o más
- el modelo `horizon_model.joblib` del 2026-08-06
- la truncación al Top 400
- **los cinco términos del Draconfly Score, con sus coeficientes exactos**
- el piso de audiencia de 50
- las 15 diarias
- la vara HIT / FAIR

**Cualquier cambio en esta lista anula B y la reinicia desde cero.**

Lo que **no** la anula: mantenimiento operativo. Arreglar una ventana rota, mover
una base a otro disco, acelerar una consulta, añadir vigilancia. Nada de eso toca
qué predicciones se emiten — se verificó que el lote diario llama a
`decision_brief()` en vivo y no lee ninguna caché.

### El caso de la capa de explicación

Una capa que **narre por qué** se eligieron las 15 ya elegidas es segura: va
después de la selección y no la toca.

Un router que decida **cuáles de las 15 merecen más análisis** también es seguro,
por lo mismo.

Un router que cambie **qué 15 se emiten** es un cambio de selección, y anula B.

### Por qué el congelamiento es el activo

B no existe para mejorar el número. Existe porque la cohorte A mide **un solo
mes**, y un tramo de 30 días no distingue *"el sistema funciona"* de *"ese mes
era predecible"*.

Si B replica con el pipeline intacto, la afirmación pasa de *"tenemos una
evaluación prospectiva buena"* a **"congelamos el sistema y replicamos el
resultado en una segunda cohorte prospectiva, temporalmente separada y
completamente predeclarada"**.

Para un evaluador técnico, esa segunda frase vale más que subir el 26.7% a 30%
mediante ajustes.
