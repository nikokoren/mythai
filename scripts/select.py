# -*- coding: utf-8 -*-
"""Deterministische Tagesauswahl.

Ziele, in dieser Reihenfolge:

1. Kein Wort wiederholt sich, bevor alle anderen dran waren
   (ein "Zyklus" laeuft einmal durch den kompletten Bestand).
2. Die Woerter eines Tages kommen aus verschiedenen Themen.
3. Auch ueber aufeinanderfolgende Tage hinweg haeufen sich Themen nicht.
4. Gleiches Datum -> gleiche Auswahl (idempotent, testbar).
5. Jeder Zyklus mischt neu.

Der Kern ist ein "Deck": eine Permutation des gesamten Bestands, in der jedes
Thema gleichmaessig ueber die volle Laenge verteilt liegt. Die Tage schneiden
dieses Deck einfach der Reihe nach in Bloecke.
"""
import hashlib
import random
from datetime import date

EPOCH = date(2026, 1, 1)
DEFAULT_COUNT = 5


def _rng(*parts):
    key = "|".join(str(p) for p in parts).encode("utf-8")
    return random.Random(int(hashlib.sha256(key).hexdigest()[:16], 16))


def build_deck(words, cycle, salt=""):
    """Permutation aller Indizes, in der jedes Thema gleichmaessig verteilt ist.

    Jedes Wort bekommt eine Position (j + 0.5) / n innerhalb seines Themas.
    Nach dieser Position sortiert liegen die Themen ineinander verschraenkt
    statt in Bloecken - genau das Gegenteil der bisherigen Lehrplan-Reihenfolge.
    """
    rng = _rng("deck", cycle, salt, len(words))
    by_topic = {}
    for i, w in enumerate(words):
        by_topic.setdefault(w.get("topic") or "ohne Thema", []).append(i)

    keyed = []
    for topic in sorted(by_topic):
        members = by_topic[topic][:]
        rng.shuffle(members)
        n = len(members)
        # Startversatz pro Thema, damit nicht alle Themen im selben Takt liegen
        offset = rng.random()
        for j, idx in enumerate(members):
            pos = ((j + offset) % n) / n
            keyed.append((pos, rng.random(), idx))
    keyed.sort()
    return [idx for _, _, idx in keyed]


def _spread_topics(deck, words, count):
    """Sorgt dafuer, dass innerhalb eines Tagesblocks kein Thema doppelt vorkommt.

    Kollidiert ein Wort mit einem Thema, das im selben Block schon vertreten
    ist, wird es mit dem naechsten passenden Wort weiter hinten getauscht.
    Das Deck bleibt eine Permutation - es wird nur umgestellt, nie ergaenzt.
    """
    deck = deck[:]
    topic = lambda i: words[i].get("topic")
    for start in range(0, len(deck), count):
        block = deck[start:start + count]
        seen = set()
        for k in range(len(block)):
            pos = start + k
            if topic(deck[pos]) not in seen:
                seen.add(topic(deck[pos]))
                continue
            for j in range(start + len(block), len(deck)):
                if topic(deck[j]) not in seen:
                    deck[pos], deck[j] = deck[j], deck[pos]
                    seen.add(topic(deck[pos]))
                    break
            else:
                seen.add(topic(deck[pos]))  # nichts Passendes mehr uebrig
    return deck


def cycle_length(total, count):
    return max(1, -(-total // count))


def selection_for(words, day, count=DEFAULT_COUNT, salt=""):
    """Auswahl fuer ein Datum. Gibt (indices, meta) zurueck."""
    if not words:
        return [], {"cycle": 0, "day_in_cycle": 0, "cycle_days": 0}
    count = max(1, min(count, len(words)))
    days = cycle_length(len(words), count)
    day_index = (day - EPOCH).days
    cycle, day_in_cycle = divmod(day_index, days)

    deck = _spread_topics(build_deck(words, cycle, salt), words, count)
    start = day_in_cycle * count
    picks = deck[start:start + count]
    return picks, {
        "cycle": cycle,
        "day_in_cycle": day_in_cycle,
        "cycle_days": days,
        "day_index": day_index,
    }
