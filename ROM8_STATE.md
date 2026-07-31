# Romans 8 — verified findings, ready to build
Handoff note, 2026-07-31. Worktree `rom-8`, branch `worktree-rom-8`, off main.
Greek text (39 verses, sigla stripped) is in `ROM8_greek.json` in this worktree.
Nothing has been appended to source/ yet. Slug will be **rom8**; anchors **v8-N / n8-N**
(not chapter 1, so NOT bare anchors). ES file: `source/es/romans-8.html`.

## THE HEADLINE — verified programmatically, 9 hits
Romans 8 is built on the preposition **with**. Nine *syn-* compounds:

| v | word | force |
|---|---|---|
| 16 | συμμαρτυρεῖ | witnesses WITH our spirit |
| 17 | συγκληρονόμοι | heirs TOGETHER |
| 17 | συμπάσχομεν | suffer WITH |
| 17 | συνδοξασθῶμεν | glorified TOGETHER |
| 22 | συστενάζει | groans TOGETHER |
| 22 | συνωδίνει | travails TOGETHER |
| 26 | συναντιλαμβάνεται | takes hold TOGETHER WITH |
| 28 | συνεργεῖ | works TOGETHER |
| 29 | συμμόρφους | formed WITH / same-formed |

**v28's συνεργεῖ is one of the nine** — so the most-quoted promise in the chapter is
part of a pattern, not an isolated guarantee. English versions render almost none of
them with "with/together" consistently ("helpeth", "work together", "conformed"), so
the thread is invisible. Same species of finding as *paga* (Isaiah 53) and *katargeō*
(1 Cor 13). This is the info-block headline.

## TWO CRUXES — both confirmed from the SBLGNT apparatus, quote verbatim
1. **v1** — `Ἰησοῦ WH Treg NA28 ] + μὴ κατὰ σάρκα περιπατοῦσιν ἀλλὰ κατὰ πνεῦμα RP`
   The Byzantine text ADDS "who walk not according to flesh but according to spirit";
   WH/Treg/NA28 lack it. This is exactly the KJV's clause at 8:1, and it appears to have
   migrated up from v4 (check v4 wording when writing the note). Modern versions drop it
   usually without telling the reader. ⚠ Print both, take no vote.
2. **v28** — `συνεργεῖ Treg NA28 RP ] + ὁ θεὸς WH`
   Westcott-Hort ADDS ὁ θεός: "**God** works all things together for good" vs "all things
   work together." One reading has events cooperating; the other has an agent. ⚠ No vote.
   (P46 is usually cited for the ὁ θεός reading — VERIFY before asserting manuscript names.)

## OTHER MATERIAL (verified present in the text)
- **v15 `Αββα ὁ πατήρ`** — Aramaic surfacing inside a Greek letter, with the Greek
  translation immediately appended. Same doubling at Mark 14:36 and Galatians 4:6.
- **v26 `στεναγμοῖς ἀλαλήτοις`** — "unspoken/inexpressible groanings"; and the verb is
  `ὑπερεντυγχάνει`, a double compound (hyper + en + tugchanō). Note *alalētos* is
  privative — un-speakable, not merely unspoken.
- **v29 `προέγνω` / `προώρισεν`** — proginōskō and **proorizō**, the predestination crux;
  the most disputed word in the chapter and arguably in Christian history. Set the
  Calvinist and Arminian readings side by side, take no vote (the Isaiah 53 pattern).
- **v34** has 5 minor variants in the apparatus (κατακρινῶν/κατακρίνων, +Ἰησοῦς, +καί,
  +ἐκ νεκρῶν) — worth one honest sentence that this verse is textually busy but that
  none of the variants change the sense.

## CHECKLIST (per feedback_check_library_additions_every_chapter)
- [ ] DICTIONARY: coin `syn-compounds`? better: `sympascho`, `systenazo`, `synergeo`,
      `proorizo`, `alaletos`, `huiothesia` (v15 adoption), `abba` (CHECK COLLISION —
      abba may already exist). Extend any that collide.
- [ ] **DICTIONARY_ES for every one of them** — no exceptions
- [ ] ENCYCLOPEDIA: `rome` and `paul` exist; check whether `rome` has ES.
      ⚠ Still no `kind` for texts, so no Septuagint/Vulgate entry — decision pending.
- [ ] ENCYCLOPEDIA_ES for anything added
- [ ] atlas: coords on any new place
- [ ] XREFS — **check reverses with the frozenset sweep first** (a 4th Isaiah xref was
      already present and only the check caught it)
- [ ] build.py CHAPTERS + TEASERS_ES (`("rom1", "Romans", 1,` is the EN anchor;
      TEASERS_ES key `"rom1"` — note the file MIXES single and double quotes, so match
      the actual delimiter, don't assume)
- [ ] art + collision check; PD-Art only (2-D only — no sculpture)
- [ ] validate: per-file anchors against BUILT filenames (`romans-1.html`, NOT `rom1.html`
      — that mistake cost a dead link on 1 Cor 13), div balance, ES leak sweep, sigla
- [ ] nav_strip vs info-block agreement (Romans is at ch.1 only, so next-in-sequence
      is Romans 2 and the nav will say so — the info-block must match)
- [ ] screenshot BOTH languages and actually look
- [ ] commit → push branch → merge into main FROM THE MAIN CHECKOUT → push → verify live

---

## PROGRESS — 2026-07-31, second pass

**DONE: the 39 EN verse blocks** are written and saved as `ROM8_verses_en.html` in this
worktree (NOT yet appended to source/mister_translation.html). Verified: 39 verses,
&ldquo;/&rdquo; balanced 2/2, and **all nine syn- compounds render visibly** as
"together with" (16, 26), "heirs together" / "suffer with" / "glorified together" (17),
"groans together" / "travails together" (22), "work together" (28), "formed with" (29).

Note anchors used, 9 groups: **n8-1** (vv1-4), **n8-5** (5-11), **n8-12** (12-14),
**n8-15** (15-17), **n8-18** (18-22), **n8-23** (23-27), **n8-28** (28-30),
**n8-31** (31-34), **n8-35** (35-39).

Translation choices already made in those blocks, for consistency in the notes:
- v19 "waits with its head craned" for *apokaradokia* (literally head-outstretched watching)
- v21 "slavery of decay" for *phthora*; v18 "present season" for *kairos*
- v26 "groanings unspeakable" for *stenagmois alalētois* (privative — un-speakable)
- v29 "knew beforehand" / "marked out beforehand" for *proegnō* / *proōrisen* — kept as
  transparent compounds rather than "foreknew/predestined", so the note can discuss what
  the "pre-" is actually doing without the English having already decided
- vv26,27,34 all use "pleads for" for *hyperentugchanei* / *entugchanei* — the same verb
  family in all three, deliberately consistent

## STILL TO DO
1. **EN notes** — 9 grouped notes at the anchors above. Headline goes in n8-15/n8-18/n8-28
   (the syn- thread crosses them); the two ⚠ cruxes are n8-1 (the Byzantine/KJV addition)
   and n8-28 (WH's ὁ θεός); *proorizō* is n8-28 too, so that note carries the most weight.
   ⚠ Still MUST verify the P46 attribution before naming manuscripts for the v28 reading.
2. **Shelf fetch** — not yet done for this chapter. KJV/ASV via
   `raw.githubusercontent.com/wldeh/bible-api/main/bibles/en-kjv/books/romans/chapters/8.json`;
   RV 1909 same host, `es-rv09/books/romanos/chapters/8.json` (VERIFY the slug "romanos");
   NWT 1984 `wol.jw.org/en/wol/b/r1/lp-e/Rbi8/45/8` and TNM `/es/wol/b/r4/lp-s/nwt/45/8`
   (Romans = book 45). Aim for 20+ tags EN given 39 verses.
3. EN info-block, then assemble panel `id="chapter-rom8"` (assert div balance first)
4. ES twin `source/es/romans-8.html` (.panel closes BEFORE the notes header) — needs its
   own shelf tags, t-rv/t-tnm, NOT zero
5. The full library checklist above — dictionary + ES, encyclopedia + ES, xrefs w/ reverse
   sweep, build.py registration, art, validation, screenshots, deploy
