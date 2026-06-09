---
title: MFA Failures
type: note
permalink: rhyme-dna/mfa-failures
tags:
- mfa
- alignment
- failures
---

# MFA_FAILURES.md — Known MFA Alignment Failures

A living catalogue of cases where MFA (Montreal Forced Aligner — the tool that lines up
the lyrics to the audio and labels each sound) produces phonemes that do not match what
was actually said, and how that hurts rhyme detection.

This replaces the former **Milestone 18** (a one-off "evaluate MFA" milestone). Instead
of a single evaluation pass, failures are recorded here as they are found. It is fed two
ways:

1. **Ad hoc** — whenever a mis-alignment is spotted while working on any milestone.
2. **Automatically (via M19b)** — when a human rhyme-breakdown video (screenshot labels)
   says two words rhyme but our pipeline does not group them, that disagreement is either
   a scorer error or an MFA error; the MFA ones are logged here.

**Scope:** this file lists only **current, unfixed** failures on the **current verse**.
Drop a row once the failure is resolved or its verse is no longer in use.

For each entry record: the **word/phrase**, the **expected** sounds, what **MFA produced**,
the **effect** on rhyme detection, the **category**, and the **source** it was found in.

---

## Failure categories

- **Mis-alignment** — wrong phonemes for a clearly-pronounced word.
- **Unaligned** — MFA produced no usable phonemes for the word at all.
- **Stray segments** — extra sounds inserted (e.g. a trailing schwa `ə`).

---

## Catalogue (current verse only)

| Word / phrase | Expected | MFA produced | Effect | Category | Source |
|---|---|---|---|---|---|
| *change* | /tʃ eɪ n dʒ/ | unaligned (no usable phonemes) | invisible to the detector; cannot join the "ay uh o er" compound scheme | Unaligned | compound-scheme verse |
| *trader* | /t r eɪ d ər/ | unaligned (partial) | invisible to the detector in *Trader Joe* | Unaligned | compound-scheme verse |
| *sofas* | /s oʊ f ə z/ | partially unaligned | weakens the *change in sofas* drift match | Unaligned (partial) | compound-scheme verse |

---

## Open question (deferred)

The decision point M18 framed — *"is MFA sufficient, or is a hybrid acoustic approach
needed?"* — stays open. The long-term vision already lists a **custom audio-to-phoneme
model** to replace MFA for non-standard pronunciations; this catalogue is the evidence
base for when/whether that becomes necessary.
