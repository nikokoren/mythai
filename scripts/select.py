# -*- coding: utf-8 -*-
"""Reihenfolge des Bestands, damit die Recipe-Auswahl abwechslungsreich wird.

Die TRMNL-Vorlage waehlt selbst aus, und zwar so:

    day_index  = local_time / 86400            # Tage seit der Unix-Epoche
    pick_index = (day_index + seed) modulo N
    selected   = thai_words[pick_index]

Das ist ein Schritt pro Tag durch das Array - die Reihenfolge der Datei *ist*
die Reihenfolge der Tage. Solange der Bestand nach Lehrplan sortiert war, kamen
darum neun Farben am Stueck.

Deshalb greift die Loesung hier an der Reihenfolge an und nicht an der Auswahl:
`build_order` legt den Bestand so, dass die Themen gleichmaessig ineinander
verschraenkt liegen. Die Vorlage bleibt unveraendert, laeuft weiter auf lokaler
Zeit (Wechsel um lokal Mitternacht) und zeigt trotzdem jeden Tag ein anderes
Thema.
"""
import hashlib
import random
from datetime import date

UNIX_EPOCH = date(1970, 1, 1)
# Kein Thema darf sich innerhalb von so vielen aufeinanderfolgenden Tagen
# wiederholen.
WINDOW = 5


def day_index(day):
    """Derselbe Tageszaehler, den die Vorlage aus local_time berechnet."""
    return (day - UNIX_EPOCH).days


def _rng(*parts):
    key = "|".join(str(p) for p in parts).encode("utf-8")
    return random.Random(int(hashlib.sha256(key).hexdigest()[:16], 16))


def _topic(word):
    return word.get("topic") or "ohne Thema"


def interleave(words, cycle=0, salt=""):
    """Permutation der Indizes, in der jedes Thema gleichmaessig verteilt liegt.

    Jedes Wort bekommt eine Position (j + versatz) / n innerhalb seines Themas.
    Danach sortiert liegen die Themen verschraenkt statt in Bloecken.
    """
    rng = _rng("order", cycle, salt, len(words))
    by_topic = {}
    for i, w in enumerate(words):
        by_topic.setdefault(_topic(w), []).append(i)

    keyed = []
    for topic in sorted(by_topic):
        members = by_topic[topic][:]
        rng.shuffle(members)
        n = len(members)
        offset = rng.random()  # damit nicht alle Themen im selben Takt liegen
        for j, idx in enumerate(members):
            keyed.append((((j + offset) % n) / n, rng.random(), idx))
    keyed.sort()
    return [idx for _, _, idx in keyed]


def repair(order, words, window=WINDOW):
    """Raeumt Themen-Wiederholungen innerhalb eines Fensters weg.

    Sitzt ein Wort zu nah an einem gleichen Thema, wird es mit dem naechsten
    passenden Wort weiter hinten getauscht. Bleibt eine Permutation.
    """
    order = order[:]
    n = len(order)
    for i in range(n):
        recent = {_topic(words[order[k]]) for k in range(max(0, i - window + 1), i)}
        if _topic(words[order[i]]) not in recent:
            continue
        for j in range(i + 1, n):
            cand = _topic(words[order[j]])
            if cand in recent:
                continue
            # der Tausch darf hinten keine neue Kollision erzeugen
            after = {_topic(words[order[k]])
                     for k in range(max(0, j - window + 1), min(n, j + window))
                     if k != j and k != i}
            if _topic(words[order[i]]) in after:
                continue
            order[i], order[j] = order[j], order[i]
            break
    return order


def build_order(words, cycle=0, salt="", window=WINDOW):
    return repair(interleave(words, cycle, salt), words, window)


def cycle_for(day, total):
    """Welcher Durchlauf durch den Bestand - passend zum modulo der Vorlage."""
    return day_index(day) // total if total else 0


def pick_index(day, total, seed=0):
    """Der Index, den die Vorlage fuer diesen Tag zieht."""
    return (day_index(day) + seed) % total if total else 0
