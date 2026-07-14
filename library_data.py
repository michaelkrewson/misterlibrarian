# -*- coding: utf-8 -*-
"""Curated data for the MisterLibrarian Bible Project's library pages.

Three collections, all grown chapter by chapter as the translation advances:

  DICTIONARY   — Hebrew terms the translator's notes have discussed.
                 Each: (slug, term, hebrew, transliteration, gloss, first_ref)
                 where first_ref = (chapter, verse) of the note that introduces it.

  ENCYCLOPEDIA — people and places the text has named so far.
                 Each entry dict:
                   slug, name, kind ("place" | "person" | "people"),
                   desc (2-4 sentences),
                   refs [(ch, v), ...] — where it appears in the translation,
                   videos [(title, url), ...] — curated archaeology/geography
                     links (Michael supplies; empty until then).
                   coords (lat, lon, span_degrees) — OPTIONAL, place entries only.
                     Powers the Atlas page's live OpenStreetMap embed (build_atlas()
                     in build.py). span_degrees sets the map's zoom (a tight
                     excavated site might use ~0.15, a whole region ~4-7). Omit
                     entirely for a place the text (or the trusted sources below)
                     leave genuinely unfixed (Nod, and a few others) — the atlas
                     then shows an honest "no fixed point" note instead of a guess.
                   approx (bool) — OPTIONAL. True marks a plotted point as a
                     debated/traditional/proposed identification rather than an
                     settled one; the atlas renders an "approximate" badge next to
                     the map. Precise, uncontroversial excavated sites (Ur, Ninevah,
                     Babylon, Nimrud, Harran, Shechem, Hebron) omit it.
                   modern (str) — OPTIONAL, place entries with coords. A short
                     plain-English "modern-day" locator (country/nearest city),
                     rendered as a caption under the map alongside the entry's own
                     English name. OpenStreetMap's free tiles label most Middle
                     Eastern sites in Arabic script only (no `name:en` fallback
                     for anything but a handful of major cities, and paid
                     English-label tile providers like MapTiler still wouldn't
                     tag the small excavated sites) — this caption is the fix:
                     readable English context next to the pin regardless of what
                     script the map itself renders.
                   Location source of record: Expedition Bible (Joel Kramer) is
                   Michael's trusted field-archaeology channel (see VIDEO_CREDITS
                   below) — where Kramer stakes out a specific identification
                   (Eden/Havilah via the Pishon = Wadi Ar-Rummah; Sodom & Gomorrah
                   = Tall el-Hammam; Ai = et-Tell after reconsidering Khirbet
                   el-Maqatir), his claim is the one plotted here, credited in the
                   desc text, even where it differs from an older/traditional
                   default. Otherwise coords follow mainstream archaeological
                   consensus.

  XREFS        — this project's own cross-reference chains: connections the
                 translator's notes establish between OUR verses.
                 Each: ((ch, v), (ch, v), "short reason") — rendered on BOTH
                 verses' pages as ⤷ chips.

The concordance is NOT here — it is generated automatically from the
translation text itself at build time (see build.py).
"""

DICTIONARY = [
    ("adam", "adam", "אָדָם", "adam",
     "Humankind / the human; a personal name only later. Puns on adamah, 'ground' — the groundling from the ground.", (2, 7)),
    ("adamah", "adamah", "אֲדָמָה", "adamah",
     "The ground, soil, arable earth — the stuff the human is formed from, cursed in Eden, and blessed through Abram.", (2, 7)),
    ("afar", "afar", "עָפָר", "afar",
     "Dust — the stuff humanity is formed from and returns to (2:7, 3:19); the same humble material later measures Abram's uncountable offspring (13:16).", (2, 7)),
    ("arum", "arum / arummim", "עָרוּם / עֲרוּמִּים", "arum / arummim",
     "'Crafty' and 'naked' — nearly identical Hebrew words; the pun straddles the Genesis 2/3 chapter break.", (3, 1)),
    ("bara", "bara", "בָּרָא", "bara",
     "'Create' — a verb reserved for God alone in the Bible; marks the thresholds: cosmos (1:1), animal life (1:21), humanity (1:27).", (1, 21)),
    ("brit", "brit", "בְּרִית", "brit",
     "Covenant. First promised at 6:18, first enacted (with all flesh, unconditionally) in Genesis 9 — the word that structures the rest of the Bible.", (6, 18)),
    ("chen", "chen", "חֵן", "chen",
     "Favor, grace. First appearance: 'Noah found favor in the eyes of the LORD' — and chen reverses the letters of Noach.", (6, 8)),
    ("chamas", "chamas", "חָמָס", "chamas",
     "Violence, lawless wrong — the earth's indictment before the flood, named twice.", (6, 11)),
    ("elohim", "Elohim", "אֱלֹהִים", "Elohim",
     "'God' — plural in form, singular in verb: standard Biblical Hebrew for the one God.", (1, 1)),
    ("ezer-kenegdo", "ezer kenegdo", "עֵזֶר כְּנֶגְדּוֹ", "ezer kenegdo",
     "'A helper corresponding to him' — ezer usually describes GOD helping Israel (strength, not servitude); kenegdo = a matching counterpart. Source of the misleading 'helpmeet.'", (2, 18)),
    ("gibbor", "gibbor", "גִּבֹּר", "gibbor",
     "Mighty man, warrior. Used of the Nephilim's era (6:4) and of Nimrod, the first post-flood empire-builder.", (6, 4)),
    ("hineh", "hineh", "הִנֵּה", "hineh",
     "'Look! / Behold' — the attention word; this translation renders it 'look' throughout.", (1, 29)),
    ("hithalekh", "hithalekh", "הִתְהַלֵּךְ", "hithalekh",
     "To walk about, back and forth — the walking-WITH-God verb: God in the garden (3:8), Enoch (5:22,24), Noah (6:9).", (3, 8)),
    ("itsavon", "itsavon", "עִצָּבוֹן", "itsavon",
     "Painful toil — the woman's pain and the man's toil in Eden's sentences; the same root reaches God's own grieved heart at 6:6.", (3, 16)),
    ("kikkar", "kikkar", "כִּכָּר", "kikkar",
     "A disc, circle — hence 'plain': the round, well-watered Jordan valley Lot chooses (13:10-12); elsewhere the same word names a 'talent,' a round ingot of silver or gold.", (13, 10)),
    ("lekh-lekha", "lekh-lekha", "לֶךְ-לְךָ", "lekh-lekha",
     "'Go — you yourself': the emphatic doubled call of Abram; the third parashah takes its name from it.", (12, 1)),
    ("mabul", "mabul", "מַבּוּל", "mabul",
     "THE flood — a technical term used only of this event (plus Psalm 29:10), never of ordinary flooding.", (6, 17)),
    ("min", "min", "מִין", "min",
     "Kind, sort — a farmer's word, not a taxonomy; behind every 'of its own kind.'", (1, 11)),
    ("miqveh", "miqveh", "מִקְוֵה", "miqveh",
     "A gathering (of water) — the word behind the seas' naming, and later Judaism's ritual bath.", (1, 10)),
    ("moadim", "mo'adim", "מוֹעֲדִים", "mo'adim",
     "Appointed times — the festival-calendar word; what the sun and moon are installed to mark.", (1, 14)),
    ("nacham", "nacham", "נָחַם", "nacham",
     "Comfort — and regret. Noah's name-hope (5:29) returns as God's regret (6:6): one root, opposite moods.", (5, 29)),
    ("nasa", "nasa", "נָשָׂא", "nasa",
     "To carry, bear, lift — one root doing three jobs in Genesis 13: the land 'could not bear' Abram and Lot together (13:6), then each of them 'lifts up' his eyes (13:10, 13:14) to opposite ends.", (13, 6)),
    ("nefesh", "nefesh chayah", "נֶפֶשׁ חַיָּה", "nefesh chayah",
     "A living creature/being — fish, birds, animals, and humans alike; not an immaterial 'soul' inside a body.", (1, 20)),
    ("nephilim", "Nephilim", "נְפִלִים", "Nefilim",
     "Beings 'on the earth in those days' (6:4); meaning unknown (possibly 'fallen ones'); LXX rendered 'giants.' Recur only at Numbers 13:33.", (6, 4)),
    ("olah", "olah", "עֹלָה", "olah",
     "Burnt offering — literally an 'ascending' offering: the whole animal goes up in smoke. First at Noah's altar.", (8, 20)),
    ("parad", "parad", "פָּרַד", "parad",
     "To separate — Genesis 13's hinge verb: Abram proposes it (13:9), Lot enacts it (13:11), and the renewed land promise arrives precisely 'after' it happens (13:14).", (13, 9)),
    ("qadash", "qadash", "קָדַשׁ", "qadash",
     "To make holy, set apart — its first biblical object is a day, the sabbath.", (2, 3)),
    ("qeshet", "qeshet", "קֶשֶׁת", "qeshet",
     "A bow — the weapon; Hebrew has no separate word for 'rainbow.' God hangs his war-bow in the clouds.", (9, 13)),
    ("raqia", "raqia", "רָקִיעַ", "raqia",
     "The vault of the sky — from a root meaning 'hammered out'; LXX stereōma → Vulgate firmamentum → 'firmament.'", (1, 6)),
    ("ruach", "ruach", "רוּחַ", "ruach",
     "Wind, breath, spirit — hovering at creation (1:2), sent to end the flood (8:1); one word, three English registers.", (1, 2)),
    ("shachat", "shachat", "שָׁחַת", "shachat",
     "To ruin — the flood's boomerang verb: the earth ruined itself; God completes the ruin (6:11-13).", (6, 11)),
    ("shamayim", "shamayim", "שָׁמַיִם", "shamayim",
     "The heavens / the sky — one Hebrew word for both English registers.", (1, 8)),
    ("shamar", "shamar", "שָׁמַר", "shamar",
     "To keep, guard, watch over — the human's garden vocation (2:15), disowned by Cain ('my brother's keeper?', 4:9).", (2, 15)),
    ("shem", "shem", "שֵׁם", "shem",
     "Name — what Babel grasps at ('let us make a name,' 11:4) and God gives ('I will make your name great,' 12:2). Also Noah's son Shem.", (11, 4)),
    ("sherets", "sherets", "שֶׁרֶץ", "sherets",
     "Swarming things — the cognate behind 'swarm with swarms' (1:20).", (1, 20)),
    ("shuf", "shuf", "שׁוּף", "shuf",
     "To crush / strike at — the rare verb (3× in the Bible) of the serpent's head and the offspring's heel.", (3, 15)),
    ("tannin", "tannin", "תַּנִּין", "tannin",
     "Sea-beast; elsewhere serpent or dragon — the 'chaos monsters' listed as ordinary day-five creations.", (1, 21)),
    ("tehom", "tehom", "תְּהוֹם", "tehom",
     "The deep — the primeval ocean of 1:2, whose springs burst open again at 7:11.", (1, 2)),
    ("teshuqah", "teshuqah", "תְּשׁוּקָה", "teshuqah",
     "Desire — paired with mashal ('rule/master') at both 3:16 and 4:7, three verses apart in the text's own logic.", (3, 16)),
    ("tevah", "tevah", "תֵּבָה", "tevah",
     "The ark — a box or chest, not a ship (no sail, rudder, or helm); its only other use is Moses' basket (Exodus 2:3).", (6, 14)),
    ("toldot", "toldot", "תּוֹלְדֹת", "toldot",
     "'Generations' — Genesis's own structural marker; ten toldot headings organize the book (2:4; 5:1; 6:9; 10:1; 11:10; 11:27; …).", (2, 4)),
    ("tohu-vavohu", "tohu vavohu", "תֹהוּ וָבֹהוּ", "tohu vavohu",
     "'Formless and empty' — the rhyming pair describing the pre-creation earth.", (1, 2)),
    ("tselem", "tselem / demut", "צֶלֶם / דְּמוּת", "tselem / demut",
     "Image / likeness — a king's image stood for his authority in his provinces; humanity bears God's. Restated post-flood as the ground of the first law (9:6).", (1, 26)),
    ("tsela", "tsela", "צֵלָע", "tsela",
     "Side — everywhere else a structural side (tabernacle, ark, temple), never a rib bone; this translation's 'side, not rib' at 2:21 rests on that usage.", (2, 21)),
    ("yhvh", "YHVH", "יְהוָה", "YHVH (the Tetragrammaton)",
     "The personal name of God, first at 2:4 — printed 'the LORD' (small caps) by longstanding convention; 'Jehovah' in the NWT.", (2, 4)),
    ("yada", "yada", "יָדַע", "yada",
     "To know — including Hebrew's own euphemism for intimacy ('the man knew his wife,' 4:1).", (4, 1)),
    ("zakhar-remember", "zakhar", "זָכַר", "zakhar",
     "To remember — divine remembering that acts: 'God remembered Noah' turns the flood (8:1); God looks at the bow 'to remember' (9:16).", (8, 1)),
    # ---- John 1 (Greek) ----
    ("logos", "logos", "λόγος", "logos",
     "Word, reason, account — John's term for the pre-existent Christ, fusing the Hebrew 'word of the LORD' by which the world was made (Genesis 1's ten-fold 'and God said') with the Greek philosophers' logos, the reason that orders the cosmos.", ("John", 1, 1)),
    ("monogenes", "monogenes", "μονογενής", "monogenēs",
     "'One of a kind, an only child' (mono-, 'only,' + genos, 'kind/kin') — NOT 'only-begotten,' which came through the Latin unigenitus and reads a later doctrine into the word. Rendered here 'the only Son.'", ("John", 1, 14)),
    ("eskenosen", "eskenosen", "ἐσκήνωσεν", "eskēnōsen",
     "'Tented, tabernacled' (from skēnē, 'tent') — the Word 'pitched his tent among us,' echoing the tabernacle where the LORD's glory came to dwell with Israel (Exodus 40).", ("John", 1, 14)),
    ("charis", "charis", "χάρις", "charis",
     "Grace, favor, gift — paired with 'truth' (alētheia) it renders the Hebrew chesed ve-emet, 'steadfast love and faithfulness,' the LORD's self-description to Moses in Exodus 34:6.", ("John", 1, 14)),
    ("christos", "Christos", "Χριστός", "Christos",
     "'Anointed' — the Greek for the Hebrew/Aramaic Messiah (mashiach); a title, not a surname. John glosses the Aramaic 'Messiah' with the Greek 'Christ' at 1:41.", ("John", 1, 17)),
    ("amnos", "amnos", "ἀμνός", "amnos",
     "Lamb — 'the Lamb of God who takes away the sin of the world,' gathering the Passover lamb of Exodus 12 and the lamb led to the slaughter of Isaiah 53.", ("John", 1, 29)),
    ("ide", "ide", "Ἴδε", "ide",
     "'Behold, look' — the natural Greek heir of the Hebrew hineh this translation renders 'Look —.' The Baptist uses it of the Lamb (1:29, 1:36), Jesus of Nathanael (1:47).", ("John", 1, 29)),
    ("kephas", "Kephas", "Κηφᾶς", "Kēphas",
     "Aramaic kepha, 'rock,' rendered into Greek as Petros — the new name Jesus gives Simon on sight, a name-change in the line of Abram→Abraham and Jacob→Israel.", ("John", 1, 42)),
]

ENCYCLOPEDIA = [
    # ---- places ----
    dict(slug="eden", name="Eden", kind="place",
         desc="The garden's region, 'in the east' (2:8), watered by a river that splits into four. Two of the four "
              "rivers are certainly the Tigris and Euphrates, anchoring the geography broadly in Mesopotamia; the "
              "other two (Pishon, Gihon) have long been unidentified. Expedition Bible's Joel Kramer proposes the "
              "dry Wadi Ar-Rummah — traced across Arabia by satellite and field survey, matching rock deposits from "
              "its source to its end — as the Pishon, joining the Tigris and Euphrates near the head of the Persian "
              "Gulf; that would place Eden itself in the area of modern Kuwait, or just offshore under the Gulf. "
              "Guarded by cherubim after the expulsion (3:24).",
         refs=[(2, 8), (2, 10), (3, 23), (3, 24), (4, 16)],
         videos=[("Searching for The Garden of Eden's Pishon River", "https://www.youtube.com/watch?v=jwCdZ4CbA-E")],
         coords=(29.6, 48.0, 3.0), approx=True,
         modern="Head of the Persian Gulf, near Kuwait (proposed)"),
    dict(slug="tigris", name="Tigris (Chidekel)", kind="place", aliases=["Tigris"],
         desc="The third river of Eden (2:14), 'running east of Asshur' — one of Mesopotamia's two great rivers, "
              "still flowing through Iraq. The Hebrew name Chidekel matches Akkadian Idiqlat.",
         refs=[(2, 14)], videos=[],
         coords=(33.35, 44.40, 4.0), approx=True,
         modern="Iraq — flows past modern Baghdad"),
    dict(slug="euphrates", name="Euphrates (Perat)", kind="place", aliases=["Euphrates"],
         desc="The fourth river of Eden (2:14), named without description — the audience knew it. The defining river "
              "of Babylonia; later the ideal border of the promised land.",
         refs=[(2, 14)], videos=[],
         coords=(32.90, 44.10, 4.0), approx=True,
         modern="Iraq — flows past modern Hillah, near ancient Babylon"),
    dict(slug="havilah", name="Havilah", kind="place",
         desc="Land of gold, bdellium, and onyx circled by the Pishon (2:11-12). Expedition Bible's Joel Kramer, "
              "tracing the Pishon to the dry Wadi Ar-Rummah, places Havilah along its course through Saudi Arabia — "
              "a region that still hosts dozens of gold mines and the onyx- and resin-bearing Hejaz ravines the "
              "text describes. Also a name in both Cush's and Joktan's lines (10:7, 10:29).",
         refs=[(2, 11), (10, 7), (10, 29)],
         videos=[("Searching for The Garden of Eden's Pishon River", "https://www.youtube.com/watch?v=jwCdZ4CbA-E")],
         coords=(25.0, 41.0, 7.0), approx=True,
         modern="Northern/central Saudi Arabia (proposed)"),
    dict(slug="cush", name="Cush", kind="place",
         desc="The Nile-valley kingdom south of Egypt (roughly Nubia/Sudan), circled by Eden's Gihon (2:13); in the "
              "Table of Nations, a son of Ham and the father of Nimrod (10:6-8).",
         refs=[(2, 13), (10, 6), (10, 7), (10, 8)], videos=[],
         coords=(17.9, 33.9, 6.0), approx=True,
         modern="Sudan (ancient Nubia), south of Egypt"),
    dict(slug="nod", name="Nod", kind="place",
         desc="'The land of Wandering,' east of Eden, where Cain settles (4:16) — the name puns on his sentence to be "
              "a restless wanderer (na vanad).",
         refs=[(4, 16)], videos=[]),
    dict(slug="ararat", name="Ararat", kind="place",
         desc="The mountain REGION where the ark rests (8:4 — 'the mountains of Ararat,' plural): the ancient kingdom "
              "of Urartu in the highlands of eastern Turkey/Armenia. The text names no individual peak; the modern "
              "mountain called Ararat took its name from this verse.",
         refs=[(8, 4)], videos=[],
         coords=(39.4, 43.8, 3.0), approx=True,
         modern="Eastern Turkey, near Lake Van"),
    dict(slug="babel", name="Babel / Babylon", kind="place", aliases=["Babel", "Babylon"],
         desc="First of Nimrod's cities in Shinar (10:10) and the site of the tower (11:1-9). Its own name, Bab-ili, "
              "means 'Gate of God'; Genesis re-derives it from Hebrew balal, 'confuse' — a deliberate, polemical pun. "
              "One of the most excavated cities of the ancient world (the great ziggurat E-temen-anki likely informed "
              "the tower story).",
         refs=[(10, 10), (11, 9)],
         videos=[("Search for the Tower of Babel", "https://www.youtube.com/watch?v=cYc_VgjJfw8")],
         coords=(32.5355, 44.4275, 0.15),
         modern="Babylon ruins, near Hillah, Iraq"),
    dict(slug="shinar", name="Shinar", kind="place",
         desc="The flat southern-Mesopotamian plain (Sumer/Babylonia) — no stone, hence brick and bitumen (11:3); "
              "home of Babel, Erech (Uruk), and Accad (Akkad).",
         refs=[(10, 10), (11, 2)], videos=[],
         coords=(32.2, 45.0, 3.0), approx=True,
         modern="Southern Iraq (ancient Sumer/Babylonia)"),
    dict(slug="nineveh", name="Nineveh", kind="place",
         desc="Great Assyrian capital on the Tigris, founded in the Nimrod tradition (10:11); its mounds (Kuyunjik, "
              "opposite modern Mosul) have been excavated for nearly two centuries. Later the setting of Jonah.",
         refs=[(10, 11), (10, 12)],
         videos=[("Bible Evidence Unearthed at Nineveh!", "https://www.youtube.com/watch?v=34XBkm4QiLo")],
         coords=(36.3605, 43.1575, 0.15),
         modern="Kuyunjik mound, opposite Mosul, Iraq"),
    dict(slug="calah", name="Calah (Nimrud)", kind="place", aliases=["Calah"],
         desc="Assyrian royal city (10:11-12); the modern mound is called Nimrud — the founder-figure's name still "
              "attached to the site.",
         refs=[(10, 11), (10, 12)], videos=[],
         coords=(36.0972, 43.3256, 0.15),
         modern="Nimrud, Iraq, south of Mosul"),
    dict(slug="canaan", name="Canaan (the land and its ancestor)", kind="place", aliases=["Canaan"],
         desc="Both a person — Ham's cursed son (9:25-27), father of Sidon and Heth (10:15) — and, in Genesis's "
              "'genealogy is geography' idiom (see the Genesis 10 notes), the land his descendants settle: the "
              "promised land itself, entered by Abram at 12:5 and central to the rest of the Bible.",
         refs=[(9, 18), (9, 22), (9, 25), (9, 26), (9, 27), (10, 6), (10, 15), (11, 31), (12, 5), (13, 12)], videos=[],
         coords=(31.7, 35.2, 3.5), approx=True,
         modern="Roughly modern Israel, Palestine, Lebanon, and Jordan"),
    dict(slug="sodom-gomorrah", name="Sodom and Gomorrah", kind="place",
         aliases=["Sodom", "Gomorrah", "Sodom and Gomorrah"],
         desc="First mentioned as landmarks on the Canaanite border (10:19) — still standing. Lot drifts toward "
              "them by stages in ch. 13 (their coming ruin already named there, 13:10), and the city's own "
              "wickedness is stated outright at 13:13; the destruction itself is still ahead, in Genesis 19. "
              "Expedition Bible's Joel Kramer identifies the site as Tall el-Hammam, in the northern Jordan Valley — "
              "burned, sulfur-rich debris there matches all four destroyed cities of the plain, while a fifth sample "
              "from Zoar's presumed site, spared in the account, did not burn.",
         refs=[(10, 19), (13, 10), (13, 12), (13, 13)],
         videos=[("Sodom burned—Zoar did NOT: the full story of the discovery of the Cities of the Plain "
                  "(preview — their destruction is still ahead, in Genesis 19)",
                  "https://www.youtube.com/watch?v=QjPcSQUY2W0")],
         coords=(31.8402, 35.6737, 0.4), approx=True,
         modern="Tall el-Hammam, Jordan, in the eastern Jordan Valley"),
    dict(slug="ur", name="Ur of the Chaldeans", kind="place",
         desc="Abram's birthplace (11:28,31) — the great Sumerian city of southern Iraq, whose ziggurat still stands; "
              "Leonard Woolley's 1920s-30s excavations (royal tombs, gold lyres) made it world-famous. 'Of the "
              "Chaldeans' is a later-era label, identifying the city for the text's own readers.",
         refs=[(11, 28), (11, 31)],
         videos=[("EXPEDITION ABRAHAM: from his birthplace at Ur to the Promised Land",
                  "https://www.youtube.com/watch?v=f7-RQZavU3U")],
         coords=(30.9626, 46.1035, 0.15),
         modern="Tell el-Muqayyar, near Nasiriyah, Iraq"),
    dict(slug="haran-city", name="Haran (the city)", kind="place", aliases=["Haran"],
         desc="Caravan city on the northern arc of the route from Ur to Canaan, where Terah's migration stalls and "
              "Terah dies (11:31-32); Abram's call comes here (12:1-4). Spelled differently in Hebrew from Terah's "
              "son Haran, whose death at 11:28 happens before the family even leaves Ur for this place.",
         refs=[(11, 31), (11, 32), (12, 4), (12, 5)], videos=[],
         coords=(36.8636, 39.0328, 0.15),
         modern="Harran, in Turkey's Şanlıurfa Province"),
    dict(slug="shechem", name="Shechem", kind="place",
         desc="Abram's first named stop in Canaan (12:6), at the great tree of Moreh — modern Tell Balata, between "
              "Mounts Ebal and Gerizim. Site of the first land-promise and Abram's first altar (12:7); it will echo "
              "through the whole Bible.",
         refs=[(12, 6), (12, 7)],
         videos=[("The Discovery of Joshua's Great Witness Stone at Shechem "
                  "(preview — this discovery belongs to Joshua 24, centuries after Abram's visit here)",
                  "https://www.youtube.com/watch?v=mnis257Rd3E")],
         coords=(32.2137, 35.2853, 0.15),
         modern="Tell Balata, near Nablus, West Bank"),
    dict(slug="bethel", name="Bethel", kind="place",
         desc="'House of God' — Abram camps east of it and builds his second altar (12:8); the name's own story "
              "(Jacob's ladder) is still ahead. Paired here with Ai to fix the camp's position.",
         refs=[(12, 8)],
         videos=[("BETHEL: Where Jacob Met God "
                  "(preview — Jacob's ladder, the episode that names this site, is still ahead in Genesis 28)",
                  "https://www.youtube.com/watch?v=8cqBePFD9S4")],
         coords=(31.9306, 35.2317, 0.2), approx=True,
         modern="Beitin, West Bank, north of Jerusalem"),
    dict(slug="ai", name="Ai", kind="place",
         desc="Landmark east of Bethel, fixing Abram's campsite (12:8) — 'the city' whose own famous story (Joshua's "
              "defeat, then conquest) is many books away. Joel Kramer, after once favoring the nearby Khirbet "
              "el-Maqatir, now finds et-Tell the better fit for Joshua's Ai — the mainstream identification used here.",
         refs=[(12, 8)],
         videos=[("“The Problem” of Joshua's Ai...SOLVED! "
                  "(preview — Ai's own story is in Joshua 7-8, far ahead of Genesis)",
                  "https://www.youtube.com/watch?v=lK7GQxkEkKk")],
         coords=(31.9276, 35.2664, 0.2), approx=True,
         modern="et-Tell, near Beitin, West Bank"),
    dict(slug="negev", name="The Negev", kind="place", aliases=["Negev"],
         desc="The arid south of Canaan, toward which Abram travels by stages (12:9) — the land's dry margin, "
              "naturally on the way down to Egypt.",
         refs=[(12, 9)], videos=[],
         coords=(30.8, 34.8, 1.5), approx=True,
         modern="Southern Israel's arid desert region"),
    dict(slug="egypt", name="Egypt (Mizraim)", kind="place", aliases=["Egypt", "Mizraim"],
         desc="In Hebrew, Mizraim — also the 'son' of Ham whose name IS the country (10:6,13). Abram goes down in "
              "famine (12:10) and his stay runs the Exodus pattern in miniature: danger, plagues, 'send away,' "
              "wealth out.",
         refs=[(10, 6), (10, 13), (12, 10), (12, 14)], videos=[],
         coords=(30.05, 31.23, 4.0), approx=True,
         modern="Egypt — the Cairo/Nile Delta area"),
    dict(slug="jordan-plain", name="The Plain of the Jordan (Kikkar)", kind="place", aliases=["the plain of the Jordan"],
         desc="The round, well-watered lower Jordan valley (13:10) — 'like the garden of the LORD, like the land "
              "of Egypt' — that Lot chooses (13:11) over staying with Abram. Its beauty and its coming ruin are "
              "named in the very same verse.",
         refs=[(13, 10), (13, 11), (13, 12)], videos=[],
         coords=(31.75, 35.55, 0.8), approx=True,
         modern="The lower Jordan Valley, north of the Dead Sea"),
    dict(slug="zoar", name="Zoar", kind="place",
         desc="A landmark fixing the plain's southern extent at its first mention (13:10) — its own story, where "
              "Lot flees and it alone of the plain's cities is spared, is still six chapters away.",
         refs=[(13, 10)],
         videos=[("Sodom burned—Zoar did NOT: the full story of the discovery of the Cities of the Plain "
                  "(preview — Zoar's own story is still ahead, in Genesis 19)",
                  "https://www.youtube.com/watch?v=QjPcSQUY2W0")],
         coords=(31.033, 35.484, 0.3), approx=True,
         modern="Near Ghor es-Safi, Jordan, southeast of the Dead Sea"),
    dict(slug="hebron", name="Hebron", kind="place",
         desc="Where Abram settles after Lot's departure, among the oaks of Mamre, and builds his third altar "
              "(13:18) — barely introduced here, but central later: Sarah's burial, the cave of Machpelah, "
              "David's first capital.",
         refs=[(13, 18)], videos=[],
         coords=(31.5326, 35.0998, 0.15),
         modern="Hebron, West Bank"),
    dict(slug="mamre", name="Mamre (the oaks of)", kind="place", aliases=["Mamre"],
         desc="The tree-grove near Hebron where Abram pitches his tent and builds an altar (13:18) — the third "
              "named tree at one of his altars, after Shechem's tree of Moreh (12:6). Mamre is also a person, an "
              "Amorite ally of Abram's named in the very next chapter (14:13, 24) — the place and the man are not "
              "shown to be connected beyond sharing the name, the same double-use already flagged at Haran.",
         refs=[(13, 18)], videos=[],
         coords=(31.5566, 35.1027, 0.15), approx=True,
         modern="Ramat el-Khalil, just north of Hebron, West Bank"),

    # ---- people ----
    dict(slug="adam-person", name="Adam", kind="person",
         desc="The first human — ha'adam, 'the human,' for most of the early chapters; the word shades into a "
              "personal name around 4:25-5:5. Formed from dust, placed in the garden, exiled from it; died at 930 "
              "(5:5).",
         refs=[(2, 7), (3, 17), (4, 25), (5, 5)], videos=[]),
    dict(slug="eve", name="Eve (Chavah)", kind="person", aliases=["Eve"],
         desc="'Mother of all the living' — the first personal name given to any human (3:20), punning on chai, "
              "'life.' Named the fallen and the appointed sons alike (4:1, 4:25).",
         refs=[(2, 22), (3, 20), (4, 1)], videos=[]),
    dict(slug="cain", name="Cain", kind="person",
         desc="Firstborn of Eve ('I have gotten,' qaniti — the name is a pun), worker of the ground, first murderer; "
              "marked and exiled to Nod, where he builds the first city (4:17).",
         refs=[(4, 1), (4, 8), (4, 15), (4, 17)], videos=[]),
    dict(slug="abel", name="Abel (Hevel)", kind="person", aliases=["Abel"],
         desc="Keeper of sheep; his name is the Hebrew word for 'breath, vapor' — never explained by the text, "
              "fitting how briefly he lives. His blood 'cries out from the ground' (4:10).",
         refs=[(4, 2), (4, 8), (4, 10)], videos=[]),
    dict(slug="seth", name="Seth", kind="person",
         desc="'Appointed' (shat) in place of Abel (4:25); the line of promise runs through him — and in his days "
              "'people began to call on the name of the LORD' (4:26).",
         refs=[(4, 25), (5, 3)], videos=[]),
    dict(slug="enoch-cain-son", name="Enoch (Cain's son)", kind="person", aliases=["Enoch"],
         desc="Cain's son (4:17) — not the man who walked with God two chapters later (5:21-24), a different Enoch "
              "entirely. Cain names the first city in the Bible after him.",
         refs=[(4, 17), (4, 18)], videos=[]),
    dict(slug="enoch", name="Enoch (who walked with God)", kind="person", aliases=["Enoch"],
         desc="Seventh from Adam: the one man in Genesis 5 who does not die — 'Enoch walked with God, and then he "
              "was not there, for God took him' (5:24), at 365 years. The later Book of Enoch grew from these two "
              "verses (see the Ask Mr. Librarian post). Distinct from Cain's son Enoch (4:17), for whom the first "
              "city was named.",
         refs=[(5, 18), (5, 19), (5, 21), (5, 22), (5, 23), (5, 24)], videos=[]),
    dict(slug="methuselah", name="Methuselah", kind="person",
         desc="The longest-lived man in the Bible — 969 years (5:27); on the Masoretic numbers his death lands "
              "exactly in the flood year.",
         refs=[(5, 25), (5, 27)], videos=[]),
    dict(slug="noah", name="Noah", kind="person",
         desc="'This one will comfort us' (5:29) — righteous, blameless in his generation, walked with God (6:9). "
              "Built the ark, offered the first altar's sacrifice (8:20), received the first covenant (9:9-17), "
              "planted the first vineyard and fell (9:20-21). Died at 950 (9:29). His name's rest-root (n-ch) puns "
              "through the whole flood story.",
         refs=[(5, 29), (6, 9), (8, 20), (9, 20), (9, 29)], videos=[]),
    dict(slug="shem-ham-japheth", name="Shem, Ham, and Japheth", kind="person",
         aliases=["Shem", "Ham", "Japheth"],
         desc="Noah's three sons, fathers of the Table of Nations' seventy peoples (10). Shem — whose name means "
              "'Name' — heads the line the story follows to Abram; Ham's look at his father draws the oracle against "
              "Canaan (9:22-27); Japheth's coastland peoples spread west.",
         refs=[(5, 32), (9, 18), (9, 23), (10, 1)], videos=[]),
    dict(slug="nimrod", name="Nimrod", kind="person",
         desc="'The first mighty man on the earth… a mighty hunter before the LORD' (10:8-9) — the Table of Nations' "
              "only biography. His kingdom starts at Babel and extends to Nineveh: empire, personified, and the "
              "setup for the tower story.",
         refs=[(10, 8), (10, 9), (10, 10)],
         videos=[("Search for the Tower of Babel — the city Nimrod founded (10:10)",
                  "https://www.youtube.com/watch?v=cYc_VgjJfw8")]),
    dict(slug="terah", name="Terah", kind="person",
         desc="Father of Abram, Nahor, and Haran (11:26-27). He, not Abram, first sets out from Ur for Canaan — and "
              "stops halfway, settling and dying in Haran (11:31-32).",
         refs=[(11, 26), (11, 31), (11, 32)], videos=[]),
    dict(slug="haran-person", name="Haran", kind="person", aliases=["Haran"],
         desc="Terah's third son, Lot's father — dies 'during the lifetime of his father Terah, in the land of his "
              "birth,' in Ur (11:28), before the family's migration even begins. His premature death leaves Lot an "
              "orphan in Abram's care, and hands the caravan city the family later stops at (Haran) a name that, "
              "confusingly, doubles his own — the two are not shown to be connected.",
         refs=[(11, 26), (11, 27), (11, 28), (11, 29), (11, 31)], videos=[]),
    dict(slug="abram", name="Abram", kind="person",
         desc="Called at 75 from Haran (12:1-4): land, nation, great name, and blessing for 'all the families of the "
              "ground' — Babel's grasped-at name, given instead. Answers with altars at Shechem and Bethel; flinches "
              "into the wife-sister ruse in Egypt (12:10-20). His story has just begun.",
         refs=[(11, 26), (12, 1), (12, 4), (12, 7), (12, 10)],
         videos=[("EXPEDITION ABRAHAM: his whole journey, from Ur to the Promised Land",
                  "https://www.youtube.com/watch?v=f7-RQZavU3U")]),
    dict(slug="sarai", name="Sarai", kind="person",
         desc="Abram's wife — introduced with the sentence everything turns on: 'Now Sarai was barren; she had no "
              "child' (11:30). Endangered by the sister-story in Pharaoh's house (12:11-20).",
         refs=[(11, 29), (11, 30), (12, 11), (12, 15)], videos=[]),
    dict(slug="lot", name="Lot", kind="person",
         desc="Son of Haran, Abram's orphaned nephew (11:27-28), who travels with him from Haran into Canaan (12:4-5) "
              "— planted in the story for consequences still ahead.",
         refs=[(11, 27), (12, 4), (12, 5)], videos=[]),
    dict(slug="pharaoh", name="Pharaoh (of Genesis 12)", kind="person", aliases=["Pharaoh"],
         desc="The unnamed king whose house takes Sarai in and is struck with plagues (12:15-20). His indignant "
              "'take her and go' makes him, uncomfortably, the moral voice of the scene — and his role rehearses the "
              "Exodus Pharaoh's, four hundred years early.",
         refs=[(12, 15), (12, 17), (12, 18)], videos=[]),
    dict(slug="nephilim-entry", name="The Nephilim", kind="people",
         desc="'On the earth in those days — and afterward too' (6:4), around the sons-of-God episode; 'the mighty "
              "men of old, the men of renown.' Meaning unknown; the Greek translators wrote 'giants.' They reappear "
              "only in the spies' report (Numbers 13:33).",
         refs=[(6, 4)], videos=[]),

    # ---- John 1 (people) ----
    dict(slug="john-the-baptist", name="John the Baptist", kind="person", aliases=["John the Baptist", "John"],
         desc="The witness sent ahead of Jesus, baptizing at the Jordan. He denies being the Messiah, Elijah, or the "
              "Prophet, calls himself only 'a voice crying in the wilderness' (Isaiah 40:3), and points his own "
              "disciples to 'the Lamb of God.' (The Gospel of John never names its own author, so every 'John' in "
              "this book is the Baptist.)",
         refs=[("John", 1, 6), ("John", 1, 15), ("John", 1, 19), ("John", 1, 26), ("John", 1, 29), ("John", 1, 35)],
         videos=[]),
    dict(slug="jesus", name="Jesus", kind="person", aliases=["Jesus"],
         desc="Jesus of Nazareth, son of Joseph — the Word made flesh (1:14). Hailed by the Baptist as 'the Lamb of "
              "God' and 'the Chosen One of God,' and confessed by Nathanael as 'Son of God' and 'King of Israel'; he "
              "names himself 'the Son of Man' (1:51).",
         refs=[("John", 1, 17), ("John", 1, 29), ("John", 1, 36), ("John", 1, 42), ("John", 1, 45), ("John", 1, 50)],
         videos=[]),
    dict(slug="andrew", name="Andrew", kind="person", aliases=["Andrew"],
         desc="Simon Peter's brother and one of the Baptist's disciples — the first to follow Jesus. He finds his "
              "brother with the words 'We have found the Messiah.'",
         refs=[("John", 1, 40), ("John", 1, 44)], videos=[]),
    dict(slug="simon-peter", name="Simon Peter", kind="person", aliases=["Simon Peter", "Simon", "Cephas", "Peter"],
         desc="Simon son of John, Andrew's brother, whom Jesus renames on sight: Cephas — Aramaic kepha, 'rock,' "
              "rendered into Greek as Petros.",
         refs=[("John", 1, 40), ("John", 1, 41), ("John", 1, 42)], videos=[]),
    dict(slug="philip", name="Philip", kind="person", aliases=["Philip"],
         desc="From Bethsaida, the town of Andrew and Peter. Called by Jesus with 'Follow me,' he in turn finds "
              "Nathanael and answers his doubt with 'Come and see.'",
         refs=[("John", 1, 43), ("John", 1, 44), ("John", 1, 45)], videos=[]),
    dict(slug="nathanael", name="Nathanael", kind="person", aliases=["Nathanael"],
         desc="The disciple Jesus greets as 'truly an Israelite, in whom there is no deceit' — a Jacob without "
              "Jacob's guile. Convinced by Jesus' sight of him 'under the fig tree,' he confesses him 'Son of God' "
              "and 'King of Israel.'",
         refs=[("John", 1, 45), ("John", 1, 47), ("John", 1, 49)], videos=[]),

    # ---- John 1 (places) ----
    dict(slug="bethany-jordan", name="Bethany beyond the Jordan", kind="place",
         aliases=["Bethany beyond the Jordan", "Bethany"],
         desc="Where John was baptizing, east of the Jordan — not the Bethany near Jerusalem. The exact site was "
              "lost early: Origen, in the third century, could not find a 'Bethany' there and proposed reading "
              "'Bethabara' instead, a variant that entered some manuscripts. Marked undetermined on the map rather "
              "than guessed.",
         refs=[("John", 1, 28)], videos=[]),
    dict(slug="bethsaida", name="Bethsaida", kind="place", aliases=["Bethsaida"],
         desc="The town of Andrew, Peter, and Philip, on the north shore of the Sea of Galilee near where the Jordan "
              "flows in. The site is debated between the mounds of et-Tell and el-Araj.",
         refs=[("John", 1, 44)], coords=(32.910, 35.631, 0.09),
         modern="et-Tell / el-Araj, northern Sea of Galilee", approx=True, videos=[]),
    dict(slug="nazareth", name="Nazareth", kind="place", aliases=["Nazareth"],
         desc="Jesus' obscure Galilean hometown, never named in the Old Testament — hence Nathanael's 'Can anything "
              "good come out of Nazareth?'",
         refs=[("John", 1, 45), ("John", 1, 46)], coords=(32.702, 35.297, 0.06),
         modern="Nazareth, Israel", videos=[]),
]

# ((from_ch, from_v), (to_ch, to_v), reason) — rendered on BOTH pages.
# ---------------------------------------------------------------------------
# In-text encyclopedia linking. The build turns each ENCYCLOPEDIA entry's
# `name` (or `aliases`, when the literal in-text string differs from the
# display name) into a link on its FIRST occurrence per chapter, wherever
# that exact word appears inside a verse's English text. Most names only
# ever mean one thing, so the resolver just needs to know, for a given
# chapter+verse, which candidate entries could apply there — which is
# exactly what each entry's own `refs` list already records. When more than
# one candidate's refs list contains the verse (Cain's-son-Enoch vs the
# Enoch-who-walked-with-God both have entries touching different verses —
# fine, no clash there), the resolver picks the one whose refs contain that
# verse. The ONE case that genuinely can't be resolved this way is a single
# verse naming two different referents of the same word — so far only
# Genesis 11:31, which names both Haran the man ("his grandson Lot son of
# Haran") and Haran the city ("they came to Haran") in one sentence. For
# that, and any future case like it, LINK_OVERRIDES pins exactly which
# occurrence (1st, 2nd, ...) of a word within one verse goes to which slug.
# ---------------------------------------------------------------------------

LINK_OVERRIDES = [
    # (chapter, verse, word, occurrence_index (1-based), slug)
    (11, 31, "Haran", 1, "haran-person"),   # "his grandson Lot son of Haran"
    (11, 31, "Haran", 2, "haran-city"),     # "they came to Haran, and settled there"
]

XREFS = [
    ((1, 2),  (7, 11),  "the deep (tehom) — sealed at creation, burst open at the flood"),
    ((1, 2),  (8, 1),   "ruach over the waters — creation's opening echoed at re-creation"),
    ((1, 6),  (7, 11),  "the waters above the vault — released as the floodgates of the sky"),
    ((1, 22), (8, 17),  "the day-five blessing — 'swarm, be fruitful, multiply' — reissued after the flood"),
    ((1, 26), (3, 22),  "the divine plural — 'let us make' / 'like one of us'"),
    ((1, 26), (5, 1),   "image and likeness — restated as the genealogy opens"),
    ((1, 26), (9, 6),   "the image of God — the ground of the first law against bloodshed"),
    ((1, 28), (9, 1),   "'be fruitful and multiply, fill the earth' — the blessing reissued to Noah"),
    ((1, 29), (9, 3),   "the food grant — plants only, then widened to meat after the flood"),
    ((1, 31), (7, 19),  "me'od — 'very good' echoed in the waters' 'very, very' triumph"),
    ((2, 7),  (3, 19),  "dust — formed from it, returning to it: Eden's frame"),
    ((2, 7),  (7, 22),  "the breath of life in the nostrils — given at creation, taken at the flood"),
    ((2, 9),  (3, 6),   "nechmad, 'desirable' — the tree's appeal, seeded two chapters early"),
    ((2, 15), (4, 9),   "shamar, 'keep/watch over' — the garden vocation Cain disowns"),
    ((2, 17), (3, 4),   "mot tamut — 'you will surely die,' quoted and negated by the serpent"),
    ((2, 25), (3, 1),   "arummim/arum — naked/crafty: the pun across the chapter break"),
    ((3, 16), (4, 7),   "teshuqah + mashal — desire and mastery, the identical pairing"),
    ((3, 17), (5, 29),  "the cursed ground — Noah named as its hoped-for comfort"),
    ((3, 17), (12, 3),  "the adamah — cursed in Eden, blessed through Abram's family"),
    ((3, 8),  (5, 22),  "hithalekh — God walking in the garden; Enoch walking with God"),
    ((3, 8),  (6, 9),   "hithalekh — the garden verb again: Noah walked with God"),
    ((4, 15), (4, 24),  "sevenfold — God's protective vengeance, inflated to Lamech's seventy-seven"),
    ((4, 17), (5, 21),  "two Enochs — Cain's city-son and the Enoch who walked with God"),
    ((4, 26), (12, 8),  "'called on the name of the LORD' — the formula, from Enosh to Abram's altar"),
    ((5, 29), (6, 6),   "nacham — Noah's 'comfort' returns as the LORD's 'regret'"),
    ((5, 32), (9, 29),  "Noah's ledger entry — opened without a total, closed after the flood"),
    ((6, 4),  (10, 8),  "gibbor — the mighty men of old, and Nimrod the first mighty man after"),
    ((6, 5),  (8, 21),  "the heart's evil inclination — grounds for the flood, then grounds for mercy"),
    ((6, 18), (9, 9),   "the covenant — promised before the flood, established after it"),
    ((7, 2),  (8, 20),  "the seven pairs of clean animals — provisioned for the first altar's sacrifice"),
    ((10, 10), (11, 9), "Babel — planted under Nimrod's flag, judged at the tower"),
    ((9, 25), (10, 15), "Canaan — cursed in the oracle, mapped in the Table"),
    ((10, 21), (11, 16), "Eber — flagged in the Table; likely the name behind 'Hebrew'"),
    ((11, 4), (12, 2),  "shem, 'name' — grasped at Babel, given to Abram"),
    ((11, 30), (12, 2), "'Sarai was barren' — the sentence the great-nation promise is heard against"),
    ((11, 31), (12, 5), "the journey to Canaan — stalled under Terah, finished under Abram"),
    ((12, 10), (12, 20), "down to Egypt and sent away — the Exodus pattern in miniature"),
    # ---- John ↔ Genesis (cross-book) ----
    (("John", 1, 1), (1, 1), "'In the beginning' — John opens on the first words of Genesis, reaching back before creation"),
    (("John", 1, 3), (1, 3), "all things came to be through the Word — as God creates by speaking, 'And God said…'"),
    (("John", 1, 5), (1, 4), "light shining in the darkness — the first thing God separates at creation"),
    (("John", 1, 32), (1, 2), "the Spirit descending and resting — the Spirit of God hovering over the waters"),
]

# ---------------------------------------------------------------------------
# Video sources. Michael trusts Expedition Bible's fieldwork and asked that
# it be worked into the encyclopedia as videos are found — embedded directly
# where the site/place is already in the translation, logged here for later
# placement where it belongs to a chapter not yet reached. Add a channel here
# once trusted; add entries to VIDEO_QUEUE as videos are found, then move
# each into an ENCYCLOPEDIA entry's `videos=[...]` (with a plain (title, url)
# tuple) once the translation actually reaches that book/chapter — deleting
# it from the queue at the same time so nothing is ever listed twice.
# ---------------------------------------------------------------------------

VIDEO_CREDITS = [
    dict(
        channel="Expedition Bible",
        person="Joel Kramer",
        url="https://www.youtube.com/@ExpeditionBible",
        blurb=(
            "Joel Kramer is a biblical archaeologist who grew up in the Middle East and has lived for years "
            "in Jerusalem. Expedition Bible takes viewers to the actual sites behind the text — with drone "
            "footage, 3D reconstructions, and firsthand walk-throughs of the archaeology and the excavators' "
            "own published records. Michael follows this channel's work closely and trusts its fieldwork; "
            "videos are embedded here with gratitude and full credit to Joel Kramer and Expedition Bible."
        ),
        added="2026-07-11",
    ),
]

# (title, url, target, note) — videos found but not yet placed, because the
# translation hasn't reached the book/chapter they belong to. Check this list
# before starting a new chapter or book; move anything relevant into an
# ENCYCLOPEDIA entry (new or existing) as soon as its target is reached.
VIDEO_QUEUE = [
    ("Where God Divided the Sea...Exploring the Exodus!",
     "https://www.youtube.com/watch?v=conaKQoe4hk",
     "Exodus (the sea crossing)",
     "Field evidence for the Red Sea/Sea of Reeds crossing route and location."),
    ("Tomb of the Exodus Pharaoh: What Was Found & Why You Don't Know About It!",
     "https://www.youtube.com/watch?v=mJP4pVjnWpk",
     "Exodus (the plagues / the Pharaoh of the Exodus)",
     "Argues for a specific identification and tomb of the Exodus-era Pharaoh."),
    ("#1 Evidence for Israel's Conquest of the Promised Land...other than the Bible!",
     "https://www.youtube.com/watch?v=mLxE3JmHV2U",
     "Joshua (the conquest)",
     "Extra-biblical evidence for the conquest of Canaan."),
    ("“The Problem” of Joshua's Ai...SOLVED!",
     "https://www.youtube.com/watch?v=lK7GQxkEkKk",
     "Joshua 7-8 (the battle of Ai)",
     "Already lightly placed as a PREVIEW on the 'ai' encyclopedia entry (Genesis 12:8) — "
     "give it its full placement when Joshua 7-8 is translated."),
    ("The Discovery of Joshua's Great Witness Stone at Shechem",
     "https://www.youtube.com/watch?v=mnis257Rd3E",
     "Joshua 24 (the covenant renewal at Shechem)",
     "Already lightly placed as a PREVIEW on the 'shechem' encyclopedia entry (Genesis 12:6) — "
     "give it its full placement when Joshua 24 is translated."),
    ("BETHEL: Where Jacob Met God",
     "https://www.youtube.com/watch?v=8cqBePFD9S4",
     "Genesis 28 (Jacob's ladder)",
     "Already lightly placed as a PREVIEW on the 'bethel' encyclopedia entry (Genesis 12:8) — "
     "give it its full placement when Genesis 28 is translated."),
    ("Sodom burned—Zoar did NOT: the full story of the discovery of the Cities of the Plain!",
     "https://www.youtube.com/watch?v=QjPcSQUY2W0",
     "Genesis 19 (the destruction of Sodom and Gomorrah)",
     "Already lightly placed as a PREVIEW on the 'sodom-gomorrah' entry (Genesis 10:19) — "
     "give it its full placement when Genesis 19 is translated."),
    ("Capernaum Unearthed: Why will this fishing village be judged harsher than Sodom?",
     "https://www.youtube.com/watch?v=N0opJ2qGQs4",
     "The Gospels (Jesus' Galilee ministry)",
     "Capernaum as the base of Jesus' ministry; new encyclopedia entry when the Gospels begin."),
    ("Where Jesus Was Crucified: The archaeological evidence!",
     "https://www.youtube.com/watch?v=ufVXZBrbSsU",
     "The Gospels (the crucifixion narratives)",
     "The case for the crucifixion site; place at the Passion narrative in whichever Gospel is translated first."),
    ("The Temple Mount--Where it IS. Where it ISN'T. What is it FOR?",
     "https://www.youtube.com/watch?v=IrqRoLxa178",
     "1 Kings (Solomon's Temple) and the Gospels (the Second Temple)",
     "Broad relevance — likely worth entries at both Solomon's Temple and the Gospels/Acts Temple scenes."),
    ("Caesarea: The City that Changed the World!",
     "https://www.youtube.com/watch?v=SNnCtAR_8Q8",
     "Acts (Cornelius, Paul's imprisonment)",
     "Herod's port city; the setting for several Acts episodes."),
    ("How we KNOW the dates for the Old Testament!",
     "https://www.youtube.com/watch?v=3DJtVlLRMGw",
     "General reference — Old Testament chronology",
     "Methodology video, not tied to one place. Consider linking from about.html rather than the encyclopedia."),
]

# ---------------------------------------------------------------------------
# Verse of the Day — homepage widget (2026-07-11). Curated by (chapter, verse,
# blurb); the actual English QUOTE is pulled live from the translation text at
# build time (see build.votd_entries), never hand-typed here, so it can never
# drift from what the chapter page actually says. Grow this list as new
# chapters land — it's fine for it to lag behind the newest chapter.
VERSE_OF_DAY = [
    (1, 1, "The opening line — the whole project starts here."),
    (1, 3, "The first command in the Bible, and the first thing it does is make light."),
    (1, 27, "Male and female both, equally, in the image of God."),
    (1, 31, "The refrain that closes creation: very good."),
    (2, 2, "God rests — the first sabbath, before there's a law commanding one."),
    (2, 7, "Formed from dust, animated by breath — humanity's whole biography in one verse."),
    (2, 18, "“Not good for the human to be alone” — the first thing God calls not-good."),
    (2, 24, "One flesh — the Bible's first statement on marriage."),
    (3, 19, "“For dust you are, and to dust you will return” — Eden's closing sentence."),
    (4, 7, "Sin “crouching at the door” — one of the Bible's most vivid images, four chapters in."),
    (4, 9, "“Am I my brother's keeper?” — still asked, five thousand years later."),
    (5, 24, "Enoch: two verses, and then he's simply not there anymore."),
    (6, 8, "One line turns the whole flood story: Noah found favor."),
    (6, 22, "“Exactly so he did” — Noah's entire character, in four words."),
    (7, 16, "“Then the LORD shut him in” — the door closes itself, once the choosing is over."),
    (8, 22, "A promise that the seasons will keep turning, for as long as the earth lasts."),
    (9, 13, "The bow in the clouds — not a rainbow decoration, a hung weapon, put away."),
    (11, 4, "“Let us make a name for ourselves” — the ambition that becomes Babel."),
    (12, 1, "“Go — you yourself” — the call that starts everything that follows."),
    (12, 2, "The promise: a great nation, a great name, and a blessing to be."),
    (13, 9, "Abram's offer to Lot — take either half, so the family doesn't have to break."),
    (13, 16, "Offspring like the dust of the earth — the promise made physical."),
]
