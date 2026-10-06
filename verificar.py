"""Verificador independiente de la cadena de predicciones de Draconfly.

No importa nada de Draconfly ni instala nada. Solo la biblioteca estandar de
Python. Esta escrito asi a proposito: un verificador que dependa del codigo
del verificado no verifica nada.

    python verificar.py

Hace tres cosas:

  1. RECALCULA LA CADENA. Cada evento incluye el hash del anterior. Alterar un
     evento viejo cambia su hash, lo que invalida el `prev` del siguiente, y
     asi hasta el final del archivo.

  2. RECUENTA LOS RESULTADOS bajo cada regla de clasificacion declarada en la
     propia cadena. Los parametros de cada vara (+400%, 250 espectadores) se
     leen del evento `rule_change`, NO de este archivo. O sea que no hay que
     creerle a este script tampoco: aplica la regla que la cadena dice que rige.

  3. COMPARA con MANIFEST.json.

Lo que esto prueba y lo que no, en el README.
"""
import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CADENA = AQUI / "ledger_chain.jsonl"
MANIFIESTO = AQUI / "MANIFEST.json"
GENESIS = "0" * 64


def canonico(payload):
    """Serializacion estable. Sin ella, dos implementaciones que ordenen las
    claves distinto calcularian hashes distintos sobre los mismos datos.
    """
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def hash_evento(evento):
    material = {k: evento[k] for k in ("seq", "event", "recorded_at", "data", "prev")}
    return hashlib.sha256(canonico(material)).hexdigest()


def cargar(ruta):
    eventos = []
    with open(ruta, encoding="utf-8") as fh:
        for linea in fh:
            linea = linea.strip()
            if linea:
                eventos.append(json.loads(linea))
    return eventos


def verificar_cadena(eventos):
    prev = GENESIS
    for i, ev in enumerate(eventos):
        if ev.get("seq") != i:
            return False, i, "seq esperado %d, encontrado %r" % (i, ev.get("seq"))
        if ev.get("prev") != prev:
            return False, i, "evento %d: prev no coincide con el hash anterior" % i
        esperado = hash_evento(ev)
        if ev.get("hash") != esperado:
            return False, i, "evento %d: hash no coincide (datos alterados)" % i
        prev = ev["hash"]
    return True, len(eventos), prev


def clasificar(regla, growth_pct, peak, baseline):
    piso = regla["insufficient_baseline_below"]
    if baseline < piso and peak < piso:
        return 0, "insufficient_baseline"
    h, f = regla["hit"], regla["fair"]
    if peak >= h["min_peak_viewers"] and growth_pct >= h["min_growth_pct"]:
        return 1, "hit_strong"
    if peak >= f["min_peak_viewers"] and growth_pct >= f["min_growth_pct"]:
        return 0, "fair"
    if growth_pct >= f["min_growth_pct"]:
        return 0, "growth_below_audience"
    if growth_pct > 0:
        return 0, "minor_lift"
    return 0, "miss_or_decline"


def recuento(eventos, regla):
    bases = {}
    for ev in eventos:
        if ev["event"] == "prediction":
            bases[ev["data"]["prediction_id"]] = float(ev["data"].get("baseline_value") or 0)

    conteo, puntuables, aciertos = {}, 0, 0
    for ev in eventos:
        if ev["event"] != "outcome":
            continue
        d = ev["data"]
        hit, resultado = clasificar(
            regla,
            float(d.get("actual_growth_pct") or 0),
            float(d.get("actual_peak_value") or 0),
            bases.get(d["prediction_id"], 0.0),
        )
        conteo[resultado] = conteo.get(resultado, 0) + 1
        if resultado != "insufficient_baseline":
            puntuables += 1
            if hit == 1 or resultado == "fair":
                aciertos += 1
    return conteo, puntuables, aciertos


# La cohorte A, tal como quedo declarada en el codigo congelado:
# predicciones emitidas entre estas dos fechas (la segunda, exclusiva),
# descartando las de audiencia insuficiente, en orden de emision.
COHORTE_A_DESDE = "2026-08-26"
COHORTE_A_HASTA = "2026-09-25"
COHORTE_A_REGLA = "hit-fair-v2"


def cohorte_a(eventos, regla):
    """Reconstruye la cifra publicada leyendo SOLO la cadena.

    Es la comprobacion que mas importa: si el 26.7% no sale de aqui, sale de
    otro lado, y "de otro lado" no es verificable.
    """
    pred = {e["data"]["prediction_id"]: e["data"]
            for e in eventos if e["event"] == "prediction"}

    filas = []
    for ev in eventos:
        if ev["event"] != "outcome":
            continue
        d = ev["data"]
        p = pred.get(d["prediction_id"])
        if p is None:
            continue
        if not (COHORTE_A_DESDE <= p["created_at"][:10] < COHORTE_A_HASTA):
            continue
        hit, resultado = clasificar(
            regla,
            float(d.get("actual_growth_pct") or 0),
            float(d.get("actual_peak_value") or 0),
            float(p.get("baseline_value") or 0),
        )
        if resultado == "insufficient_baseline":
            continue
        filas.append((p["entity_name"], 1 if (hit == 1 or resultado == "fair") else 0))

    exitos = sum(e for _, e in filas)
    return {
        "n": len(filas),
        "exitos": exitos,
        "tasa_pct": round(100.0 * exitos / len(filas), 1) if filas else None,
        "creadores": len({c for c, _ in filas}),
    }


def por_periodo(eventos, regla):
    """El historico partido en tres, bajo la misma vara.

    Esta aqui porque el tramo que peor sale es el mas informativo: muestra que
    la cifra de la cohorte A no es el archivo entero, y permite ver de donde
    sale la diferencia sin tener que preguntarla.
    """
    pred = {e["data"]["prediction_id"]: e["data"]
            for e in eventos if e["event"] == "prediction"}
    tramos = [
        ("antes del congelamiento", "0000-00-00", COHORTE_A_DESDE),
        ("cohorte A", COHORTE_A_DESDE, COHORTE_A_HASTA),
        ("posteriores a A", COHORTE_A_HASTA, "9999-99-99"),
    ]
    salida = []
    for nombre, desde, hasta in tramos:
        n = k = 0
        for ev in eventos:
            if ev["event"] != "outcome":
                continue
            d = ev["data"]
            pr = pred.get(d["prediction_id"])
            if pr is None or not (desde <= pr["created_at"][:10] < hasta):
                continue
            hit, resultado = clasificar(
                regla,
                float(d.get("actual_growth_pct") or 0),
                float(d.get("actual_peak_value") or 0),
                float(pr.get("baseline_value") or 0),
            )
            if resultado == "insufficient_baseline":
                continue
            n += 1
            if hit == 1 or resultado == "fair":
                k += 1
        salida.append((nombre, desde, hasta, n, k))
    return salida


def main():
    if not CADENA.exists():
        print("No encuentro %s" % CADENA)
        return 1

    eventos = cargar(CADENA)
    ok, revisados, detalle = verificar_cadena(eventos)

    print("=" * 68)
    print("CADENA")
    print("=" * 68)
    if not ok:
        print("  FALLA en el evento %d" % revisados)
        print("  %s" % detalle)
        return 1
    print("  %d eventos verificados, todos encadenados" % revisados)
    print("  ultimo hash: %s" % detalle)

    tipos = {}
    for ev in eventos:
        tipos[ev["event"]] = tipos.get(ev["event"], 0) + 1
    print("  " + "   ".join("%s: %d" % (k, v) for k, v in sorted(tipos.items())))

    primero = min(ev["recorded_at"] for ev in eventos)
    ultimo = max(ev["recorded_at"] for ev in eventos)
    print("  del %s al %s" % (primero[:19], ultimo[:19]))

    reglas = [ev["data"] for ev in eventos if ev["event"] == "rule_change"]
    if reglas:
        print()
        print("=" * 68)
        print("RECUENTO BAJO CADA VARA DECLARADA EN LA CADENA")
        print("=" * 68)
        print("  (los umbrales salen del evento rule_change, no de este script)")
    for regla in reglas:
        conteo, puntuables, aciertos = recuento(eventos, regla)
        tasa = (100.0 * aciertos / puntuables) if puntuables else 0.0
        print()
        print("  %s  (vigente desde %s)" % (regla["rule_id"], regla["vigente_desde"]))
        print("    %s" % regla["descripcion"])
        print("    HIT  >= %+.0f%% y >= %.0f espectadores" % (
            regla["hit"]["min_growth_pct"], regla["hit"]["min_peak_viewers"]))
        print("    FAIR >= %+.0f%% y >= %.0f espectadores" % (
            regla["fair"]["min_growth_pct"], regla["fair"]["min_peak_viewers"]))
        print("    %d puntuables   %d aciertos   %.1f%%" % (puntuables, aciertos, tasa))
        for k, v in sorted(conteo.items(), key=lambda kv: -kv[1]):
            print("      %-24s %d" % (k, v))

    reglas_por_id = {r["rule_id"]: r for r in reglas}
    if COHORTE_A_REGLA in reglas_por_id:
        a = cohorte_a(eventos, reglas_por_id[COHORTE_A_REGLA])
        pred_a = {e["data"]["prediction_id"]: e["data"]
                  for e in eventos if e["event"] == "prediction"}
        print()
        print("=" * 68)
        print("LA CIFRA PUBLICADA, RECONSTRUIDA DESDE LA CADENA")
        print("=" * 68)
        print("  cohorte A: emitidas del %s al %s (exclusivo), vara %s" % (
            COHORTE_A_DESDE, COHORTE_A_HASTA, COHORTE_A_REGLA))
        print("    %d predicciones   %d exitos   %s%%   sobre %d creadores" % (
            a["n"], a["exitos"], a["tasa_pct"], a["creadores"]))
        print("    publicado:  450 predicciones   120 exitos   26.7%   sobre 261 creadores")
        cuadra = (a["n"], a["exitos"], a["tasa_pct"], a["creadores"]) == (450, 120, 26.7, 261)
        print("    %s" % ("coincide." if cuadra else "NO COINCIDE con lo publicado."))
        print()
        print()
        print("  El historico entero, partido bajo la misma vara:")
        for nombre, desde, hasta, n, k in por_periodo(eventos, reglas_por_id[COHORTE_A_REGLA]):
            tasa = (100.0 * k / n) if n else 0.0
            print("    %-24s n=%4d   exitos=%3d   %5.1f%%" % (nombre, n, k, tasa))
        print("    El primer tramo es peor a proposito: son predicciones emitidas")
        print("    mientras el pipeline todavia se estaba cambiando. Por eso la")
        print("    cohorte A empieza el %s y no antes." % COHORTE_A_DESDE)
        print()
        # La vara v2 se declaro el 2026-08-27, un dia DESPUES de que A
        # arrancara. Lo que lo hace legitimo es que el primer resultado de A
        # todavia no existia, y eso se lee del archivo en vez de prometerse.
        declarada = next(e["recorded_at"] for e in eventos
                         if e["event"] == "rule_change"
                         and e["data"]["rule_id"] == COHORTE_A_REGLA)
        evaluaciones = [e["data"]["evaluated_at"] for e in eventos
                        if e["event"] == "outcome"
                        and e["data"]["prediction_id"] in pred_a
                        and COHORTE_A_DESDE <= pred_a[e["data"]["prediction_id"]]["created_at"][:10] < COHORTE_A_HASTA]
        if evaluaciones:
            primero_a = min(evaluaciones)
            print("  La vara se fijo antes de ver un solo resultado:")
            print("    %s  se declara la vara %s" % (declarada[:19], COHORTE_A_REGLA))
            print("    %s  se registra el primer resultado de la cohorte A" % primero_a[:19])
            print("    %s" % ("la vara es anterior." if declarada < primero_a
                              else "LA VARA ES POSTERIOR. Eso invalidaria la cifra."))
            print()

        print("  La tasa base de 9.79% contra la que se compara NO sale de este")
        print("  archivo: se calcula sobre el panel completo de ~3,090 creadores,")
        print("  que no es publico. Esa parte hay que creerla o auditarla aparte.")

    if MANIFIESTO.exists():
        man = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
        print()
        print("=" * 68)
        print("CONTRA EL MANIFIESTO")
        print("=" * 68)
        fallas = 0
        for campo, obtenido in (
            ("events", revisados),
            ("last_hash", detalle),
            ("predictions", tipos.get("prediction", 0)),
            ("outcomes", tipos.get("outcome", 0)),
        ):
            declarado = man.get(campo)
            marca = "ok " if declarado == obtenido else "NO "
            if declarado != obtenido:
                fallas += 1
            print("  %s %-12s declarado %s / obtenido %s" % (
                marca, campo, declarado, obtenido))
        if fallas:
            print()
            print("  El manifiesto no corresponde a esta cadena.")
            return 1

    print()
    print("Todo cuadra.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
