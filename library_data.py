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
     "Favor, grace. First appearance: 'Noah found favor in the eyes of Jehovah' — and chen reverses the letters of Noach.", (6, 8)),
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
     "Burnt offering — literally an 'ascending' offering (from alah, 'to go up'): unlike every other sacrifice, the WHOLE animal goes up in smoke, none of it eaten. First at Noah's altar (8:20); its full law opens Leviticus (ch. 1), where it is the offering of total self-gift. Douay-Rheims calls it a 'holocaust' — the Greek holokauston, 'wholly burnt.'", (8, 20)),
    ("qorban", "qorban", "קָרְבָּן", "korban",
     "Offering — literally 'that which is brought near' (from qarav, 'to draw near, approach'). The Bible's basic word for a sacrifice frames it not as destruction but as APPROACH: the worshipper draws near to God by bringing a gift near to the altar. The KJV renders it 'oblation'/'offering'; Mark 7:11 preserves the very word, 'Corban.' Leviticus 1:2 is its first occurrence.", ("Leviticus", 1, 2)),
    ("nichoach", "reyach nichoach", "רֵיחַ נִיחוֹחַ", "reyach nichoach",
     "A soothing aroma — the 'restful, pleasing smell' of an offering (nichoach shares the root nuach, 'to rest,' the root behind Noah's name). Its FIRST appearance is Noah's burnt-offering after the flood: 'Jehovah smelled the soothing aroma' and swore never again to curse the ground (8:21). Leviticus makes the same phrase the refrain of the whole sacrificial system (1:9, 13, 17) — what Noah did once at the altar becomes Israel's daily worship. KJV 'a sweet savour.'", ("Leviticus", 1, 9)),
    ("kaphar", "kipper", "כִּפֶּר", "kipper",
     "To make atonement — to cover, wipe away, or ransom (the piel of kaphar). Its plain root is 'to cover': Noah's ark was coated with 'pitch' (kopher, 6:14), the same three letters. In Leviticus it becomes the great cultic verb: the offering makes atonement 'for him' (1:4), the sin is covered over before God — the root behind kapporet, the atonement-cover on the ark of the covenant, and Yom Kippur, the Day of Atonement.", ("Leviticus", 1, 4)),
    ("samakh", "samakh", "סָמַךְ", "samakh",
     "To lean, press, lay firmly — the worshipper 'lays his hand upon the head' of the offering (1:4), pressing down, not merely touching (semikhah). The gesture identifies the offerer with the victim: this dies in my place. The same verb later ordains: Moses lays his hands on Joshua and the spirit passes (Numbers 27:18-23) — the root of both substitution and ordination.", ("Leviticus", 1, 4)),
    ("shechitah", "shachat", "שָׁחַט", "shachat",
     "To slaughter ritually — the precise verb for killing an offering (1:5, 11), the root of shechitah, kosher slaughter. ⚠ Not to be confused with its near-twin shachat (שָׁחַת, final tav), 'to ruin,' the flood's boomerang verb (6:11) — a different root that only sounds alike. This one, spelled with a final tet, means a clean, deliberate killing at the altar 'before Jehovah.'", ("Leviticus", 1, 5)),
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
     "The personal name of God (יהוה), first here at 2:4. Most English Bibles hide it behind the title 'the LORD' (small caps); this translation restores it as <strong>Jehovah</strong> — the traditional English form since about the 1200s, used throughout the ASV and by the NWT. ('Jehovah' is a hybrid, the consonants with Adonai's vowels; scholars reconstruct the original as 'Yahweh.') The full discussion is on the <a href=\"ask-jehovah.html\">Ask Mr. Librarian page</a>.", (2, 4)),
    ("yada", "yada", "יָדַע", "yada",
     "To know — including Hebrew's own euphemism for intimacy ('the man knew his wife,' 4:1).", (4, 1)),
    ("yom", "yom", "יוֹם", "yom",
     "DAY — one of the most elastic words in the Hebrew Bible, and the reason the length of the creation 'days' has been debated for two thousand years. It means the daylight hours (Genesis 1:5, 'God named the light DAY'), a 24-hour calendar day, AND an indefinite stretch of time — an age: 'in the DAY that Jehovah made earth and heaven' (2:4) folds the whole creation week into a single yom, and 'the DAY of Jehovah' names a whole era of judgment. So the six 'days' of Genesis 1 can be read as ordinary days OR as long ages (the 'day-age' reading — ancient, going back to Augustine, and the way many hold the text and the ~13.8-billion-year cosmos together). This translation renders it plainly 'day' and lays out the readings without voting — see the note at 1:5, or the fuller discussion on the <a href=\"ask-creation-days.html\">Ask Mr. Librarian page</a>.", (1, 5)),
    ("zakhar-remember", "zakhar", "זָכַר", "zakhar",
     "To remember — divine remembering that acts: 'God remembered Noah' turns the flood (8:1); God looks at the bow 'to remember' (9:16).", (8, 1)),
    # ---- John 1 (Greek) ----
    ("logos", "logos", "λόγος", "logos",
     "Word, reason, account — John's term for the pre-existent Christ, fusing the Hebrew 'word of Jehovah' by which the world was made (Genesis 1's ten-fold 'and God said') with the Greek philosophers' logos, the reason that orders the cosmos.", ("John", 1, 1)),
    ("monogenes", "monogenes", "μονογενής", "monogenēs",
     "'One of a kind, an only child' (mono-, 'only,' + genos, 'kind/kin') — NOT 'only-begotten,' which came through the Latin unigenitus and reads a later doctrine into the word. Rendered here 'the only Son.'", ("John", 1, 14)),
    ("eskenosen", "eskenosen", "ἐσκήνωσεν", "eskēnōsen",
     "'Tented, tabernacled' (from skēnē, 'tent') — the Word 'pitched his tent among us,' echoing the tabernacle where Jehovah's glory came to dwell with Israel (Exodus 40).", ("John", 1, 14)),
    ("charis", "charis", "χάρις", "charis",
     "Grace, favor, gift — paired with 'truth' (alētheia) it renders the Hebrew chesed ve-emet, 'steadfast love and faithfulness,' Jehovah's self-description to Moses in Exodus 34:6.", ("John", 1, 14)),
    ("christos", "Christos", "Χριστός", "Christos",
     "'Anointed' — the Greek for the Hebrew/Aramaic Messiah (mashiach); a title, not a surname. John glosses the Aramaic 'Messiah' with the Greek 'Christ' at 1:41.", ("John", 1, 17)),
    ("amnos", "amnos", "ἀμνός", "amnos",
     "Lamb — 'the Lamb of God who takes away the sin of the world,' gathering the Passover lamb of Exodus 12 and the lamb led to the slaughter of Isaiah 53.", ("John", 1, 29)),
    ("ide", "ide", "Ἴδε", "ide",
     "'Behold, look' — the natural Greek heir of the Hebrew hineh this translation renders 'Look —.' The Baptist uses it of the Lamb (1:29, 1:36), Jesus of Nathanael (1:47).", ("John", 1, 29)),
    ("kephas", "Kephas", "Κηφᾶς", "Kēphas",
     "Aramaic kepha, 'rock,' rendered into Greek as Petros — the new name Jesus gives Simon on sight, a name-change in the line of Abram→Abraham and Jacob→Israel.", ("John", 1, 42)),
    # ---- Genesis 14 (Hebrew) ----
    ("ivri", "ivri", "עִבְרִי", "ivri",
     "'Hebrew' — its first appearance in the Bible, on Abram (14:13). Most naturally 'a descendant of Eber' (10:21), the name flagged back in the Table of Nations; an older theory instead links it to the apiru, the landless outsiders of the ancient Near East.", (14, 13)),
    ("elyon", "El Elyon", "אֵל עֶלְיוֹן", "El Elyon",
     "'God Most High' — the title under which Melchizedek, a Canaanite priest-king, blesses Abram (14:18); Abram then identifies his own YHWH with this Most High God (14:22).", (14, 18)),
    ("qoneh", "qoneh", "קֹנֵה", "qoneh",
     "'Maker, creator, possessor' (from qanah) — 'Maker of heaven and earth' (14:19); the same root Eve punned on at Cain's birth, 'I have gotten/made a man' (4:1).", (14, 19)),
    ("maaser", "ma'aser", "מַעֲשֵׂר", "ma'aser",
     "A tenth, a tithe — the Bible's first, given by Abram to Melchizedek (14:20).", (14, 20)),
    # ---- Genesis 15 (Hebrew) ----
    ("aman", "he'emin / aman", "הֶאֱמִן / אָמַן", "he'emin / aman",
     "To trust, to lean one's weight on — the root behind 'amen.' 'Abram believed Jehovah, and he counted it to him as righteousness' (15:6), the verse Paul and James both build on.", (15, 6)),
    ("tzedaqah", "tzedaqah", "צְדָקָה", "tzedaqah",
     "Righteousness, right standing — reckoned to Abram on account of his trust (15:6), granted rather than earned.", (15, 6)),
    ("magen", "magen", "מָגֵן", "magen",
     "A shield — 'I am a shield to you' (15:1), echoing the root of 'delivered' (miggen) in Melchizedek's blessing (14:20).", (15, 1)),
    ("tardemah", "tardemah", "תַּרְדֵּמָה", "tardemah",
     "A deep, God-sent sleep — laid on Abram at the covenant of the pieces (15:12), the same word as the sleep God laid on the human in the garden (2:21); the sleep in which God does the work.", (15, 12)),
    # ---- Genesis 16 (Hebrew) ----
    ("shiphchah", "shiphchah", "שִׁפְחָה", "shiphchah",
     "A female slave — the word the shelf renders 'handmaid.' Hagar's title, used insistently through Genesis 16 (her status IS the plot); Pharaoh's gifts back at 12:16 included such women.", (16, 1)),
    ("anah", "anah / innah", "עָנָה", "anah",
     "To afflict, oppress, humble. Prophesied of Israel in Egypt (15:13), dealt by Sarai to an Egyptian (16:6), accepted in the angel's hard 'submit yourself' (16:9), heard by God in Hagar's 'affliction' (16:11) — the Exodus verb, running backward.", (15, 13)),
    ("malakh", "mal'akh", "מַלְאָךְ", "mal'akh",
     "Messenger — human or heavenly; 'angel' is simply the Greek for it (angelos). 'The angel of Jehovah' first appears at 16:7, speaking in God's own first person — see the note there for the three readings.", (16, 7)),
    ("el-roi", "El Ro'i", "אֵל רֳאִי", "El Ro'i",
     "'God of seeing' — the name Hagar confers at 16:13: 'the God who sees me,' or 'the God whom I have seen'; the grammar holds both. The only name a person gives TO God in the Bible; the well Beer-lahai-roi preserves it.", (16, 13)),
    ("pere", "pere", "פֶּרֶא", "pere",
     "The wild donkey of the steppe — untamable, masterless, at home in the wilderness (Job 39:5-8 sings its freedom). 'A wild donkey of a man' (16:12) is Ishmael's freedom-oracle, not a slur.", (16, 12)),
    # ---- Genesis 17 (Hebrew) ----
    ("shaddai", "El Shaddai", "אֵל שַׁדַּי", "El Shaddai",
     "The name God announces at 17:1. 'Almighty' is the Greek-and-Latin guess (LXX pantokrator, Vulgate omnipotens); the Hebrew meaning is uncertain — 'God of the mountain' (Akkadian shadu), the steppe, or a fertility word (Genesis 49:25 sets 'Shaddai' beside 'blessings of the breasts, shaddayim, and of the womb'). Kept untranslated here, as a name.", (17, 1)),
    ("tamim", "tamim", "תָּמִים", "tamim",
     "Whole, sound, blameless — integrity of a piece, not sinless perfection. Noah's word (6:9); asked of Abraham at 17:1: 'walk before me and be blameless.' In Leviticus the same word becomes the standard for every sacrifice: the animal must be tamim, 'without blemish' (1:3, 10) — the whole, unflawed victim mirrors the whole, unflawed walk God asks of the worshipper. The New Testament reaches for exactly this word: 'a lamb without blemish' (1 Peter 1:19).", (6, 9)),
    ("mul", "mul / himmol", "מוּל", "mul",
     "To circumcise — the covenant's sign cut into the flesh (17:10-14), at eight days old, house-born and money-bought alike; the male who refuses the cutting is himself 'cut off' (karet) — the penalty rhymes with the refusal.", (17, 10)),
    ("hamon", "hamon", "הֲמוֹן", "hamon",
     "A multitude, a roaring crowd — the word folded into Abraham's new name: av hamon goyim, 'father of a multitude of nations' (17:4-5).", (17, 4)),
    ("tsachaq", "tsachaq", "צָחַק", "tsachaq",
     "To laugh — Abraham's face-down laugh at 17:17 mints the name Isaac (Yitschaq, 'he laughs'); Sarah's laugh (18:12) and her 'God has made laughter for me' (21:6) keep the pun running — until its sting: at 21:9 Sarah sees Ishmael metsacheq, 'laughing,' the participle of Isaac's own name-verb. Whatever he was doing, in Hebrew he was doing ISAAC — and it costs him his home (KJV 'mocking'; Douay 'playing'; Paul, 'persecuted,' Galatians 4:29).", (17, 17)),
    # ---- Genesis 18 (Hebrew) ----
    ("tseaqah", "za'aqah / tse'aqah", "זְעָקָה / צְעָקָה", "za'aqah / tse'aqah",
     "The outcry — the legal scream of the wronged. Abel's blood 'cries out' from the ground (4:10), the outcry of Sodom's victims reaches heaven (18:20-21), and Israel's own cry in Egypt will rise the same way (Exodus 3:7, 9).", (18, 20)),
    ("mishpat", "mishpat / shaphat", "מִשְׁפָּט / שָׁפַט", "mishpat / shaphat",
     "Justice — and the verb to judge. Sarai invokes it in anger (16:5), a desert spring is named for it (En-mishpat, 14:7), and Abraham aims it at heaven itself: 'Shall not the Judge of all the earth do justice?' (18:25).", (16, 5)),
    ("pala", "pala", "פָּלָא", "pala",
     "Wonder — what only God does. 'Is anything too wondrous for Jehovah?' (18:14) — the shelf's 'too hard' flattens it; Jeremiah asks the question back almost word for word (Jeremiah 32:17, 27).", (18, 14)),
    ("ednah", "ednah", "עֶדְנָה", "ednah",
     "Delight — Sarah's word for what age has ended (18:12), almost certainly from the same root as Eden, the garden of delight: shall the garden's word come back, at ninety?", (18, 12)),
    ("chalilah", "chalilah", "חָלִלָה", "chalilah",
     "'Far be it from you!' — literally something close to 'profane be it to you': Abraham's gasp, twice in one verse (18:25), at the thought of the Judge acting unjustly.", (18, 25)),
    # ---- Genesis 19 (Hebrew) ----
    ("haphakh", "haphakh", "הָפַךְ", "haphakh",
     "To overturn, overthrow — THE Sodom verb (19:21, 25, 29). In verse 29 the event becomes a noun, 'the overthrow' (hahafekhah), and from then on 'like the overthrow of Sodom' is the Bible's standing measure of total ruin (Deuteronomy 29:23; Isaiah 13:19). Jeremiah's chapter of the stocks is bracketed by this root: the mahpekhet ('twister,' 20:2) that bent the prophet, and the birth-curse's 'cities that Jehovah overthrew' (20:16).", (19, 25)),
    ("gophrit", "gophrit", "גָּפְרִית", "gophrit",
     "Sulfur — the old Bibles' 'brimstone' — rained with fire on the cities (19:24); afterwards the fixed image of scorched judgment (Deuteronomy 29:23; Job 18:15; Revelation keeps it to the end).", (19, 24)),
    ("chesed", "chesed", "חֶסֶד", "chesed",
     "Steadfast love, covenant kindness — one of the Bible's great untranslatables, first here on Lot's lips (19:19). The word behind the Psalms' 'mercy,' and — paired with 'truth' (chesed ve-emet, see emet) — behind John's 'grace and truth' (see charis). It saturates Genesis 24, where the servant asks God to 'do chesed' with Abraham (24:12) and designs a sign that tests it — not the girl's beauty but her spontaneous kindness to a stranger and his ten thirsty camels.", (19, 19)),
    ("chemlah", "chemlah", "חֶמְלָה", "chemlah",
     "Compassion, pity — 'in the compassion of Jehovah on him' (19:16): the only reason Lot's lingering doesn't kill him; four people dragged out by the hand.", (19, 16)),
    ("shalshelet", "shalshelet", "שַׁלְשֶׁלֶת", "shalshelet",
     "Not a word but a MUSICAL MARK — the rarest cantillation sign in the Torah (four occurrences), a zigzag sung as a long wavering trill. It hangs over 'but he lingered' (19:16): the melody itself dawdles with Lot.", (19, 16)),
    # ---- Genesis 20 (Hebrew) ----
    ("navi", "navi", "נָבִיא", "navi",
     "Prophet — its FIRST occurrence in the Bible is Abraham (20:7), and note what defines the office there: not prediction but INTERCESSION — 'he will pray for you, and you shall live.' A prophet is one who stands between.", (20, 7)),
    ("tom", "tom", "תֹּם", "tom",
     "Integrity, wholeness — the noun of tamim (17:1's 'blameless'). Abimelech pleads it ('in the integrity of my heart,' 20:5) and God confirms it (20:6): in Gerar the tom belongs to the pagan king, and the scheming to the prophet.", (20, 5)),
    ("gur", "gur / ger", "גּוּר / גֵּר", "gur / ger",
     "To sojourn — the resident-stranger's verb, and his noun. Israel will be gerim in Egypt (15:13), Abraham holds the land only as 'sojournings' (17:8), the Sodom mob sneers 'this one came to sojourn' (19:9) — and Abraham sojourns (gur) in GERAR (20:1), a town that nearly rhymes with the word.", (15, 13)),
    ("atsar", "atsar", "עָצַר", "atsar",
     "To restrain, hold back, shut up. Sarai's own word for her childlessness — 'Jehovah has kept me from bearing' (16:2) — returns doubled at 20:18: the house that took Sarah is given, for a season, Sarah's condition.", (16, 2)),

    # ---- Daniel 1 (Hebrew) ----
    ("patbag", "pat-bag", "פַּתְבַּג", "pat-bag",
     "The king's food-portion (Daniel 1:5) — a PERSIAN loanword sitting in a Hebrew sentence (patibaga, 'allotment'), one of Daniel's tell-tale foreign words. KJV 'the king's meat' (meat = food), ASV 'the king's dainties.'", ("Daniel", 1, 5)),
    ("gaal-defile", "ga'al", "גָּאַל", "ga'al",
     "To defile — 'Daniel set on his heart that he would not DEFILE himself with the king's food' (Daniel 1:8). Why it defiled — idol-offered meat? unclean species? the dependence of eating at the king's table? — is debated; the wine, never unclean in the law, sharpens the question.", ("Daniel", 1, 8)),
    ("zeroim", "zero'im", "זֵרֹעִים", "zero'im",
     "Seed-food, vegetables — a word found only in Daniel 1 (vv 12, 16), the diet of history's first recorded controlled trial. KJV gave English a treasure for it: 'give us PULSE to eat.'", ("Daniel", 1, 12)),
    ("saris", "saris", "סָרִיס", "saris",
     "Eunuch — or simply 'court official': the word covers both (Potiphar, a married saris, shows the broader sense). Ashpenaz is 'chief of the sarisim' (Daniel 1:3); Isaiah had told Hezekiah his descendants would be sarisim in Babylon's palace (Isaiah 39:7), and tradition heard Daniel in the prophecy.", ("Daniel", 1, 3)),
    # ---- Daniel 11 (Hebrew) ----
    ("tsvi", "erets ha-tsvi", "אֶרֶץ הַצְּבִי", "erets ha-tsvi",
     "'The land of BEAUTY' — Daniel's title for the promised land (11:16, 41; 'the beautiful holy mountain,' 11:45): tsvi is both 'beauty, glory' and 'gazelle.' KJV 'the glorious land'; NWT, memorably, 'the land of the Decoration.'", ("Daniel", 11, 16)),
    ("shiqquts", "shiqquts meshomem", "שִׁקּוּץ מְשֹׁמֵם", "shiqquts meshomem",
     "'The abomination that desolates' (Daniel 11:31) — shiqquts, the standing slur-word for an idol, plus 'desolating.' 1 Maccabees 1:54 uses this very phrase for the altar Antiochus IV set up on the temple's altar, 15 Kislev 167 BC; Jesus lifts it toward a horizon of his own — 'spoken of by Daniel the prophet' (Matthew 24:15).", ("Daniel", 11, 31)),
    ("maskilim", "maskilim", "מַשְׂכִּילִים", "maskilim",
     "'The wise' — those with insight, who 'give understanding to many' and fall by sword and flame (Daniel 11:33-35): the book's heroes are teachers, not warriors (the armed revolt itself may be only 'a little help,' 11:34). Daniel 12:3 gives them the shining reward.", ("Daniel", 11, 33)),
    ("kittim", "Kittim", "כִּתִּים", "Kittim",
     "Javan's son in the Table of Nations (Genesis 10:4) — Cyprus (Kition) first, then the whole Greek west, and by Daniel 11:30 the newest western sea-power: ROME, whose ships turn Antiochus back (the Dead Sea Scrolls read Kittim as the Romans too). KJV 'Chittim'; NIV translates the name away as 'western coastlands.'", (10, 4)),
    ("ketiv-qere", "ketiv / qere", "כְּתִיב / קְרֵי", "ketiv / qere",
     "'Written' / 'read' — the Masoretes' double track: where tradition READ a word differently than the consonants WRITE it, they left the written letters in the column and set the reading beside them. Daniel 11 shows several (vv 10, 12, 18, 39 — an unpointed word beside its pointed twin in the Hebrew column here). The manuscript's own honesty, kept.", ("Daniel", 11, 10)),
    # ---- Exodus 1 (Hebrew) ----
    ("sharats", "sharats", "שָׁרַץ", "sharats",
     "To SWARM, teem — the creation-word for life multiplying (Genesis 1:20, the waters 'swarm with swarms'; 9:7, Noah told to 'swarm'). Exodus 1:7 stacks it into the five-verb increase — Israel 'were fruitful, and SWARMED, and multiplied, and grew mighty' — so the opening of the bondage is the CREATION BLESSING still at full volume on a slave people. KJV flattens it to 'increased abundantly.'", (1, 7)),
    ("perekh", "perekh", "פֶּרֶךְ", "perekh",
     "Crushing harshness — pitiless, breaking labor (Exodus 1:13, 14). KJV 'with rigour'; NWT 'under tyranny.' A rare, heavy word (also Leviticus 25's law against ruling a fellow Israelite be-farekh, 'with harshness') — the opposite of the discipline a father gives; this is cruelty made a system.", (1, 13)),
    ("avodah", "avodah", "עֲבֹדָה", "avodah",
     "Service, labor — and, in the same breath, SLAVERY (from eved, 'servant/slave,' the root the exodus turns on: Israel serves Pharaoh, then is freed to SERVE God — same verb). Exodus 1:14's avodah kashah, 'hard service,' the mortar and the bricks. The word will pivot: the goal of the exodus is not idleness but a change of masters — 'let my people go, that they may serve me.'", (1, 14)),
    ("yeor", "ye'or", "יְאוֹר", "ye'or",
     "The NILE — Egypt's OWN word for its river (Egyptian itrw), used in Hebrew almost only of the Nile (KJV 'the river'; NWT 'the Nile River'). The babies are thrown into the ye'or (1:22) — the same river a basket will float on (2:3), and the first the plagues turn to blood (7:20). Borrowed once, memorably, for the Tigris of Daniel's vision (Daniel 12:5).", (1, 22)),
    ("moshe", "Mosheh (Moses)", "מֹשֶׁה", "Mosheh",
     "The NAME — given a Hebrew reason, 'because I DREW HIM OUT (meshitihu) of the water' (2:10), from mashah, 'to draw out.' But the form Mosheh is ACTIVE ('the one who draws out'), not the passive mashuy ('drawn out') the reason would need — the tell of a Hebrew pun laid over a genuinely EGYPTIAN name: mose / mes, 'born of, son,' the element in Thut-mose, Ah-mose, Ra-messes. The full case (and why the Egyptian name argues the story is authentic) is in the encyclopedia's <a href=\"encyclopedia.html#moses\">Moses</a> entry.", ("Exodus", 2, 10)),
    ("suph", "suph", "סוּף", "suph",
     "REEDS — the papyrus-marsh growth of the Nile's edge, where the baby's ark is set (2:3, 5). The same word names the sea Israel crosses: the YAM SUPH, 'Sea of Reeds' (Exodus 13:18; 15:4), which the KJV and most versions render 'Red Sea' (following the Greek Septuagint's eruthra thalassa). So the deliverer is drawn from the reeds before the nation is drawn through the reed-sea — the book plants its rescue in its opening scene. NWT keeps 'Red Sea' by convention but footnotes 'Reed Sea.'", ("Exodus", 2, 3)),
    # ---- Exodus 3 (Hebrew) ----
    ("ehyeh", "ehyeh", "אֶהְיֶה", "ehyeh",
     "'I WILL BE / I AM' — God's answer at the bush, 'ehyeh asher ehyeh' (3:14), from hayah, 'to be,' in the Hebrew IMPERFECT: a form that spans I am / I will be / I will prove to be, so the shelf splits (KJV 'I AM THAT I AM'; ASV footnotes 'I WILL BE'; NWT 'I Will Become What I Choose to Become'; the Greek 'ho ōn,' 'the One who is,' handed to Revelation 1:8). This translation keeps it 'I WILL BE' to match v12's ehyeh immakh, 'I WILL BE with you' — the Presence promised to Moses IS the Name given to Israel. And ehyeh (first person, 'I will be') is the verb the third-person Name YHWH is built on ('He will be'): God names himself, Israel names him. See the <a href=\"encyclopedia.html#jehovah\">Jehovah</a> entry.", ("Exodus", 3, 14)),
    ("seneh", "seneh", "סְנֶה", "seneh",
     "The BUSH — a thornbush or bramble, the one Moses sees burning unconsumed (3:2). Rare (almost only this scene, plus Deuteronomy 33:16, 'him who dwelt in the seneh'), and it carries a quiet pun: seneh sounds like SINAI, the mountain it burns on — as if the bush names the mountain, or the mountain is a bush grown to stone. The fire that does not devour is the whole sign: a Presence that can dwell in the fragile without destroying it.", ("Exodus", 3, 2)),
    ("qodesh", "qodesh", "קֹדֶשׁ", "qodesh",
     "HOLY, holiness — the root sense is 'set apart, cut off from the common.' 'The place on which you stand is holy ground' (admat-qodesh, 3:5) is the first patch of EARTH in the Bible called holy — and the ground is admah, Adam's own soil (Genesis 2:7), made holy by nothing but the Presence standing on it. (The seventh day was 'made holy' first, Genesis 2:3 — holiness begins in TIME, then touches a PLACE here, and will fill the tabernacle by the book's end.) Not a quality of the dirt, but of Who is there.", ("Exodus", 3, 5)),
    ("zavat-chalav-udevash", "zavat chalav u-devash", "זָבַת חָלָב וּדְבָשׁ", "zavat chalav u-devash",
     "'Flowing with milk and honey' — the land-promise's signature phrase, first spoken here (3:8, 17) and repeated some twenty times through the Torah. 'Milk' from flocks on good pasture, 'honey' (devash — wild bee-honey, or the thick syrup of dates/figs) from fruited hills: not luxury but a land that FEEDS its people, the opposite of Egypt's rationed bricks-and-straw. Literally 'flowing (zavah) with milk and honey' — the land itself pouring out sustenance.", ("Exodus", 3, 8)),
    ("natsal", "natsal", "נָצַל", "natsal",
     "A root that runs both ways in this chapter — TO RESCUE, snatch away (hifil, hitsil): 'I have come down to RESCUE them from the hand of Egypt' (3:8) — and TO STRIP, plunder, despoil (piel, nitsel): 'you will STRIP Egypt bare' (3:22). One verb for the deliverance and for the spoil: Israel is snatched out of Egypt's hand, and carries Egypt's silver out in the same motion — the wages of four centuries, and the down payment on Genesis 15:14's 'great possessions.' KJV 'spoil'; the pun on 'deliver' is only visible in the Hebrew.", ("Exodus", 3, 22)),
    # ---- Genesis 23 (Hebrew) ----
    ("ger", "ger / toshav", "גֵּר / תּוֹשָׁב", "ger / toshav",
     "Two distinct legal statuses the shelf often merges (KJV 'a stranger and a sojourner,' Genesis 23:4; NWT keeps them, 'an alien resident and a settler'). A GER is a resident foreigner — living among a people, protected by law, but WITHOUT citizenship or the right to own land (Torah's great charge: 'love the ger, for you were gerim in Egypt'). A TOSHAV is a settled outsider, more rooted but still landless. Abraham names himself both — the man promised the whole land cannot legally buy a grave in it.", (23, 4)),
    ("achuzzah", "achuzzah", "אֲחֻזָּה", "achuzzah",
     "A HOLDING — a permanent, inheritable land-possession, from achaz, 'to grasp, hold fast' (KJV 'possession'). The loaded word of Genesis 23: Abraham seeks an achuzzat-qever, a 'burial holding' — and it is the very term God used for the promised land itself, 'all the land of Canaan for an everlasting HOLDING' (17:8). In his lifetime the everlasting holding comes down to one field with a grave in it.", (23, 4)),
    ("nasi", "nasi", "נָשִׂיא", "nasi",
     "A prince, chief — 'one lifted up' (from nasa, 'to lift, carry'). The Hittites call Abraham nesi Elohim, 'a prince of GOD' (23:6): NWT 'a chieftain of God'; KJV reads Elohim as a superlative, 'a mighty prince.' Both live in the phrase — a prince who belongs to God, and a godlike-great prince — and this translation keeps the divine name the Hittites actually spoke. In Numbers the plural nesi'im titles the twelve tribal CHIEFTAINS who stand with Moses at the census (Numbers 1:16, 44) — one lifted-up head per tribe; and it later titles Ezekiel's coming ruler.", (23, 6)),
    # ---- Genesis 24 (Hebrew) ----
    ("yarekh", "yarekh", "יָרֵךְ", "yarekh",
     "The THIGH / loins — under which the servant puts his hand to swear (24:2, 9). Not an idle gesture: the yarekh is the seat of procreation, the region of the covenant-of-circumcision sign (17:11), and 'those who came out of the yarekh' is the Hebrew for a man's own offspring (46:26; Exodus 1:5). To swear by it is to swear by the seed the whole promise runs through — fitting for an oath about the son who will carry the line. The Bible knows this gesture only twice, both about the promised posterity: here, and Jacob making Joseph swear to bury him in the land (47:29).", (24, 2)),
    ("emet", "emet", "אֱמֶת", "emet",
     "Truth, faithfulness, reliability — from aman, 'to be firm, trustworthy' (the root of amen). Its home is the pair chesed ve-EMET, 'kindness and truth' (24:27, 49): not two things but one — loyal love that can be RELIED ON, love that keeps faith. The servant blesses Jehovah for not forsaking his chesed ve-emet toward Abraham, and asks Laban's house to deal in chesed ve-emet with his master. The same pair becomes a title of God himself, 'abundant in chesed and emet' (Exodus 34:6).", (24, 27)),
    ("almah", "almah", "עַלְמָה", "almah",
     "A young woman of marriageable age — Rebekah is called almah at 24:43 in the servant's retelling, though the narrator called her na'arah ('girl,' 24:14) and betulah ('virgin,' 24:16) when she first appeared. That overlap is the crux of the famous Isaiah 7:14 debate ('a almah shall conceive'): almah marks a young woman, YOUNG enough to be presumed unmarried and chaste, without betulah's technical focus on virginity — and here the same Rebekah is all three words at once. The Greek Bible rendered Isaiah's almah as parthenos, 'virgin,' the reading Matthew 1:23 carries.", (24, 43)),
    ("suach", "suach", "שׂוּחַ", "suach",
     "A rare verb — Isaac 'went out la-SUACH in the field toward evening' (24:63), and no one is quite sure what he was doing. The old readings: to MEDITATE (KJV; a quiet turning-over in the mind), to PRAY (the rabbis made this the origin of the evening prayer), to walk/muse, or even to lament (still grieving his mother, v67). The word occurs only here in this sense, so the shelf spreads out — NWT 'to meditate'; some 'to stroll.' This translation keeps 'to meditate,' the reading that best fits a solitary man in a field at dusk, looking up to see camels — and a bride — on the horizon.", (24, 63)),
    # ---- Genesis 25 (Hebrew) ----
    ("neesaf-el-ammav", "ne'esaf el-ammav", "וַיֵּאָסֶף אֶל-עַמָּיו", "ne'esaf el-ammav",
     "'And he was GATHERED to his people' — the death-formula, spoken over Abraham (25:8) and Ishmael (25:17), and later Isaac, Jacob, Moses, Aaron. It is distinct from burial (Abraham is 'gathered' in v8, then buried in v9) — the phrase reaches past the grave to a JOINING of the ancestors, a quiet, undogmatic hint of continued existence long before the Hebrew Bible speaks plainly of resurrection (Daniel 12:2). Not a tomb but a homecoming; the same dignity is given Ishmael as Abraham.", (25, 8)),
    ("bekhorah", "bekhorah", "בְּכֹרָה", "bekhorah",
     "The BIRTHRIGHT — the firstborn's (bekhor) privilege: a double share of the inheritance (Deuteronomy 21:17), the headship of the family, and here, in the line of promise, the covenant blessing itself. Esau trades it for a bowl of stew (25:29-34) and 'despised' it (see bazah); Jacob will later steal the matching blessing (ch. 27). The New Testament makes Esau the type of the 'profane' person who sells the eternal for one meal (Hebrews 12:16). Genesis keeps overturning it — the younger again and again takes the bekhorah (Isaac over Ishmael, Jacob over Esau, Ephraim over Manasseh).", (25, 31)),
    ("aqev", "aqev", "עָקֵב", "aqev",
     "The HEEL — Jacob is born gripping Esau's aqev, 'and his name was called Ya'aqov' (25:26), 'heel-holder.' The name turns into a verb of treachery: 'is he not rightly named Ya'aqov (Jacob)? He has SUPPLANTED me (ya'aqveni) these two times' (27:36) — to grab the heel is to trip, to overreach, to supplant. And it is the very word of the first promise-and-curse: 'he will strike your head, and you will strike his HEEL' (3:15). The whole Jacob cycle is folded into a newborn's fist.", (25, 26)),
    ("atar", "atar", "עָתַר", "atar",
     "To ENTREAT, plead — and the same verb, turned around, for GRANTING the plea: 'Isaac ENTREATED (va-ye'tar) Jehovah for his wife … and Jehovah was ENTREATED (va-ye'ater) of him' (25:21). One word for the asking and the answering, the prayer and the yes — the Hebrew's neat way of showing the circuit close. KJV keeps the echo ('intreated … was intreated'); Rebekah, barren twenty years, conceives.", (25, 21)),
    # ---- Genesis 26 (Hebrew) ----
    ("esek", "esek", "עֵשֶׂק", "esek",
     "'CONTENTION' — the name Isaac gives the first re-dug well, whose water the herdsmen of Gerar claim: 'he called it Esek, because they CONTENDED (hit'assequ) with him' (26:20). From a root for quarreling, wrangling, disputing a right. The first of three wells named for what happened there — Esek (contention), then Sitnah (enmity), then Rehoboth (room): a small parable of a patient man who keeps yielding until God gives him space.", (26, 20)),
    ("sitnah", "sitnah", "שִׂטְנָה", "sitnah",
     "'ENMITY, opposition' — the name of the second contested well (26:21). From the verb satan, 'to oppose, accuse, be an adversary' — the very root behind ha-SATAN, 'the accuser/adversary' (Job 1; Zechariah 3), and the name Satan the New Testament carries over untranslated. The related noun sitnah later heads a legal 'accusation' filed against the returning exiles (Ezra 4:6). Here it is just a well fought over — but the word already carries the whole Bible's idea of the one who stands against.", (26, 21)),
    ("rehoboth", "rehovot", "רְחֹבוֹת", "rehovot",
     "'BROAD PLACES, room' — the name of the third well, the one no one fought over: 'he called it Rehoboth, and said, For now Jehovah has made ROOM (hirchiv) for us, and we will be fruitful in the land' (26:22). From rachav, 'to be wide,' the root of rechov, a city's open 'square.' After Esek (contention) and Sitnah (enmity), the patient man is given room — the Hebrew for relief and enlargement, when the pressing-in finally opens out. (A modern Israeli city keeps the name.)", (26, 22)),
    # ---- Genesis 27 (Hebrew) ----
    ("berakhah", "berakhah", "בְּרָכָה", "berakhah",
     "The BLESSING — from barak, 'to bless' (and 'to kneel'), the thing the whole chapter is fought over. In Genesis a father's deathbed blessing is not a fond wish but a PERFORMATIVE, near-irrevocable word: once spoken it takes effect and cannot be recalled — 'I have blessed him; yes, and he will be blessed' (27:33). It carries the covenant itself (dew and fatness, dominion, and Abraham's own 'cursed be those who curse you,' 12:3). Jacob steals Esau's berakhah as he had bought his bekhorah (birthright); Esau's cry 'have you but one blessing?' (27:38) is the anguish of a word that cannot be unsaid. Hebrews 12:17 makes him the man who 'found no place for repentance, though he sought it with tears.'", (27, 4)),
    ("matamim", "mat'ammim", "מַטְעַמִּים", "mat'ammim",
     "SAVORY FOOD — 'tasty things,' a delicacy (from ta'am, 'taste'): the dish of game Isaac craves and the disguise Rebekah cooks from two kids to fool him (27:4, 9, 31). KJV 'savoury meat'; NWT 'a tasty dish.' A small, human detail — the old blind man's love of a favorite meal — turned into the very instrument of the deception; the taste that was meant to confirm his son is the taste that helps steal the blessing.", (27, 4)),
    ("mirmah", "mirmah", "מִרְמָה", "mirmah",
     "DECEIT, treachery — 'your brother came with mirmah and took your blessing' (27:35; KJV 'subtilty,' NWT 'deception'). It becomes a thread running through Jacob's whole life, the deceiver repeatedly deceived: he cheats Esau with mirmah here, and Laban will cheat HIM ('why have you deceived me?', Leah for Rachel, 29:25), and his own sons will deceive him with Joseph's blood-dipped coat (37:31-33). The man named 'supplanter' (Ya'aqov) traffics in mirmah until God wrestles a new name out of him — Israel; the true Israelite, John's Gospel will later say, is the one 'in whom is no mirmah / deceit' (John 1:47).", (27, 35)),
    # ---- Genesis 28 (Hebrew) ----
    ("sullam", "sullam", "סֻלָּם", "sullam",
     "The famous 'LADDER' of Jacob's dream — a word that appears only ONCE in the whole Bible (28:12), so its exact shape is uncertain. KJV 'ladder' gave English 'Jacob's ladder,' but the likely root is salal, 'to heap up, cast up (a highway or ramp),' which points instead to a STAIRWAY or ramp — the monumental temple-stair of a Mesopotamian ziggurat, built precisely as a stepped bridge for the gods between earth and heaven. NWT and most modern scholars read 'stairway.' The broad steps also fit the traffic the dream shows: angels 'ascending and descending' both at once. This translation renders 'stairway,' keeping 'Jacob's ladder' in view as the traditional name.", (28, 12)),
    ("matsevah", "matsevah", "מַצֵּבָה", "matsevah",
     "A standing STONE, a pillar set upright (from natsav, 'to stand') as a memorial or marker of a holy encounter. Jacob takes his stone pillow, stands it up, and pours oil on it — the Bible's first anointing of a sacred object — to mark where he met God (28:18, 22; he does it again at 35:14). The patriarchs raise matsevot freely; but because the Canaanites used them in idol-worship, the Law later BANS them ('you shall not set up a matsevah, which Jehovah your God hates,' Deuteronomy 16:22) — one of the places where a patriarchal practice becomes a forbidden one once Israel has the Law.", (28, 18)),
    # ---- Genesis 29 (Hebrew) ----
    ("rakkot", "rakkot", "רַכּוֹת", "rakkot",
     "'Leah's eyes were rakkot' (29:17) — and the shelf cannot agree what that means, because the word runs from 'weak, dull' to 'tender, delicate, soft.' KJV 'tender eyed'; many read it as a DEFECT — weak or watery eyes — set against Rachel's full-bodied beauty, so the sister no one chose is marked from the start; others hear a compliment, 'soft/lovely eyes,' her one loveliness. The Hebrew leaves it open, and the ambiguity is almost kind: whether her eyes were her flaw or her charm, she was the unloved one (see senuah), and it is she God will bless with the sons.", (29, 17)),
    ("senuah", "senuah", "שְׂנוּאָה", "senuah",
     "'HATED' — literally, from sane, 'to hate'; but Hebrew uses it for the LESS-loved of two, so 'unloved' catches the sense: 'Jehovah saw that Leah was senuah, and opened her womb' (29:31, 33). The same idiom governs a real law — the man with a loved wife and a 'hated' (unloved) one may not deny the unloved wife's firstborn his double portion (Deuteronomy 21:15-17), the exact situation this chapter sets up. The heart of it: God SIDES WITH THE UNLOVED. Rachel is adored and barren; Leah is unloved and fruitful — and from unloved Leah come Levi (the priesthood) and Judah (the kings, and the Messiah).", (29, 31)),
    # ---- Genesis 30 (Hebrew) ----
    ("dudaim", "dudaim", "דּוּדָאִים", "dudaim",
     "MANDRAKES — a low plant of the nightshade family whose forked, vaguely human root and sweet, heady fruit made it the ancient Near East's great love-charm and fertility-drug (KJV 'mandrakes'; the name echoes dod, 'beloved,' so 'love-apples'). Reuben finds them at the wheat harvest, and Rachel trades a night with Jacob for them (30:14-16) — hoping they will open her womb. The chapter's irony is pointed: it is LEAH who conceives from that night, not Rachel; the mandrakes do nothing, and Rachel bears only later, when 'God remembered' her (30:22). The plant returns in the Song of Songs, where the lovers' mandrakes 'give forth fragrance' (7:14).", (30, 14)),
    ("aqod-naqod", "aqod · naqod · talu", "עָקֹד נָקֹד טָלוּא", "aqod, naqod, talu",
     "The FLOCK-MARKINGS at the heart of Jacob's wage-deal, kept distinct: aqod 'streaked / banded,' naqod 'speckled' (small spots), talu 'spotted / patched' (large blotches), and chum 'dark, brown.' In a flock of white sheep and dark goats these off-colored animals are the odd minority — which is exactly why Jacob asks for them as his wages (30:32-43): a bargain that looks generous to Laban and becomes, through Jacob's peeled rods and selective breeding, a fortune. KJV renders the trio 'ringstraked, speckled, and spotted.'", (30, 32)),
    # ---- Proverbs 1 (Hebrew) ----
    ("mashal", "mashal", "מָשָׁל", "mashal",
     "Proverb — the book's own title is its plural, Mishlei, 'the proverbs of Solomon' (1:1). A mashal is a saying that rules by LIKENESS (the root means both 'to be like' and 'to rule'): a comparison compact enough to govern a life. It stretches from a one-line saw to a taunt-song to Jesus' parables (the Greek Bible renders both mashal and its cousins parabolē).", (1, 1)),
    ("chokhmah", "chokhmah", "חָכְמָה", "chokhmah",
     "WISDOM — the master-word, and the head of a family Proverbs keeps carefully distinct (see da'at, binah, mezimmah, haskel): not raw intellect but SKILL for living — the same word names the CRAFTSMANSHIP of the tabernacle artisans (Exodus 31:3). Wisdom is knowledge (da'at) and understanding (binah) put to work rightly. In 1:20 it stands up as a woman, 'Wisdom' personified, crying in the streets — the Lady Wisdom of chapter 8.", (1, 2)),
    ("daat", "da'at", "דַּעַת", "da'at",
     "KNOWLEDGE — from yada, 'to know': not only facts held in the head but knowing by acquaintance (the same verb knows a friend, or a spouse). It is what 'the fear of Jehovah is the beginning of' (1:7), and what fools 'hate' (1:22, 29). Distinct from wisdom (chokhmah, the skill that USES knowledge) and understanding (binah, the discernment that SORTS it).", (1, 4)),
    ("binah", "binah", "בִּינָה", "binah",
     "UNDERSTANDING — from bin, 'to separate, to discern BETWEEN': the faculty that tells one thing from another, true from false, this road from that. Not the same as knowledge (da'at, what you know) but the power to DISCERN it — comprehension by distinguishing. Its close sibling tevunah, 'discernment' (from the same root), enters at Proverbs 2:3 and 3:19; binah is 'understanding,' tevunah the applied 'discernment.'", (1, 2)),
    ("mezimmah", "mezimmah", "מְזִמָּה", "mezimmah",
     "DISCRETION, discernment — shrewd forethought, the ability to think a matter through to its end (1:4). From zamam, 'to plan, to devise' — the same root serves for scheming EVIL (Psalm 37:12), so mezimmah is morally neutral shrewdness, the planning-faculty pointed the right way. KJV 'discretion'; NWT 'thinking ability'; it is what keeps the wise out of the trap the simple walk into.", (1, 4)),
    ("haskel", "haskel", "הַשְׂכֵּל", "haskel",
     "INSIGHT — prudent skill that SUCCEEDS: from sakal, 'to be prudent, to act wisely and prosper.' 'The discipline of insight' (musar haskel, 1:3) is training that produces competent, effective living — not just right ideas but the deft handling of real situations. KJV 'wise dealing'; the noun-form maskil titles the 'skillful' psalms.", (1, 3)),
    ("musar", "musar", "מוּסָר", "musar",
     "DISCIPLINE — this translation's rendering, with the ASV and NWT, over the KJV/NIV's softer 'instruction': from yasar, 'to chasten, correct, train,' musar is the corrective sense that dominates Proverbs — 'do not despise the discipline of Jehovah' (3:11), 'he who spares the rod hates his son' (13:24, the same word). Not neutral information but formation that COSTS: the lesson and the rod behind it, given by a parent (1:8) and despised by a fool (1:7).", (1, 2)),
    ("yirat-yhwh", "yirat Jehovah", "יִרְאַת יְהוָה", "yirat Jehovah",
     "'The fear of Jehovah' — the motto and refrain of Proverbs: 'the beginning of knowledge' (1:7), 'the beginning of wisdom' (9:10). Not fright but reverent awe — the posture the angel found in Abraham at the altar, 'now I know you fear God' (Genesis 22:12). ASV reads 'the fear of Jehovah' with this translation; KJV prints its small-caps divine name in the slot.", (1, 7)),
    ("ormah", "ormah", "עָרְמָה", "ormah",
     "Shrewdness, prudence — the survival-craft Wisdom gives the naive (1:4). Its root is the serpent's: the snake of Genesis 3:1 was arum, 'crafty' (KJV 'subtil'), and KJV renders THIS word 'subtilty' too — the same cunning that ruined Eden, redeemed here into the sense that keeps the simple alive.", (1, 4)),
    ("peti", "peti", "פֶּתִי", "peti",
     "The simple one — from a root meaning 'open': the wide-open, gullible, un-made-up mind, easily persuaded either way (plural petayim, 1:4, 22). Not stupid — UNFORMED; Proverbs' prime student, and prime target for the sinner's enticement (the same root as patah, 'to entice,' 1:10). KJV 'the simple.'", (1, 4)),
    ("kesil-evil-lets", "kesil / evil / lets", "כְּסִיל / אֱוִיל / לֵץ", "kesil / evil / lets",
     "Proverbs' gallery of fools — three distinct kinds, kept distinct in this translation: the EVIL (1:7), the moral fool who despises wisdom; the KESIL (1:22), the thick, dull fool, complacent (KJV 'fool' for both); and the LETS (1:22), the SCOFFER, the cynic who mocks all correction (KJV 'scorner') — the hardest case, past teaching. Hebrew has a whole thesaurus for folly, and chapter 1 opens the drawer.", (1, 22)),
    # ---- Genesis 22 (Hebrew) ----
    ("hineni", "hineni", "הִנֵּנִי", "hineni",
     "'Here I am' — the word of total availability, sounded three times in the Aqedah: to God (22:1), to Isaac (22:7), and to the angel at the knife (22:11). Not a report of location but of readiness — the same answer Moses gives at the bush and Isaiah before the throne ('here I am, send me'). KJV 'Here am I.'", (22, 1)),
    ("aqad", "aqad", "עָקַד", "aqad",
     "To bind — the verb of Genesis 22:9, 'he BOUND Isaac his son,' and it occurs ONLY this once in all of scripture. Yet from this one word Jewish tradition names the whole episode the Aqedah, 'the Binding' — memory resting on the binding, not the near-killing. KJV 'bound.'", (22, 9)),
    ("ahav", "ahav", "אָהַב", "ahav",
     "To love — and its FIRST appearance in the Bible is Genesis 22:2, 'your son, your only one, whom you LOVE.' Love enters scripture at the exact moment it is asked to be surrendered. The Greek Bible softened yachid ('only one') to agapēton, 'beloved' — the very word the voice at Jesus' baptism will use of a son.", (22, 2)),
    ("yhwh-yireh", "Jehovah-Yireh", "יְהוָה יִרְאֶה", "Jehovah yireh",
     "'Jehovah sees / provides' — the name Abraham gives Moriah after the ram (22:14), sealing the chapter's pun: yireh (he will see to it, v8) and yera'eh (it is seen to, v14) are one root, ra'ah, 'to see.' English 'provide' carries the same logic (Latin pro-videre, 'to see ahead'). It joins Hagar's El Roi, 'the God who sees' (16:13). KJV 'Jehovah-jireh.'", (22, 14)),
    ("yachid", "yachid", "יָחִיד", "yachid",
     "'Only one, only child' — 'take your son, your ONLY ONE' (22:2, 12, 16). Ishmael was sent away one chapter before, so Isaac is now the only son of the covenant; the word also means 'darling, precious' (Psalm 22:20 uses it for one's own life). KJV 'only son'; the Septuagint's agapēton, 'beloved,' set up the baptism echo.", (22, 2)),
    # ---- Genesis 21 (Hebrew) ----
    ("paqad", "paqad", "פָּקַד", "paqad",
     "To visit, attend to — for good or for ill: 'Jehovah VISITED Sarah' with a son (Genesis 21:1; KJV 'visited'), and the same verb 'visits' Jerusalem's doings upon her in judgment (Jeremiah 21:14). The Bible's word for God turning his attention toward someone — what happens next depends on the ledger. In Numbers the same verb runs the census: to paqad is to MUSTER, to number an army (Numbers 1:3, 19); the pequdim are 'those mustered.' And in one chapter it turns three ways — the fighting tribes are paqad-mustered, the Levites are NOT paqad-counted (1:47) but are paqad-APPOINTED over the tabernacle (1:50). One root: to turn attention toward, whether to count, to charge, or to visit.", (21, 1)),
    # ---- Numbers 1 (Hebrew) ----
    ("eda", "eda", "עֵדָה", "edah",
     "The congregation, community, assembly — the whole gathered people of Israel (Numbers 1:2), from the root ya'ad, 'to appoint, to meet by appointment' (the same family as mo'ed, the 'appointed time' and the 'tent of MEETING'). Not a random crowd but the summoned assembly; its chieftains are literally 'the CALLED ones of the eda' (1:16). KJV 'congregation,' NWT 'assembly.'", ("Numbers", 1, 2)),
    ("matteh", "matteh", "מַטֶּה", "matteh",
     "A tribe — but the word's plain meaning is a STAFF, a rod, a branch (from natah, 'to stretch out, extend'). Israel's tribes are 'staffs': shoots off the one stock of Jacob, each a branch of the family tree, and each led by a man holding a chief's staff. Numbers prefers matteh where Genesis often used shevet (also 'rod/tribe'); the picture is the same — a people that is one tree with twelve branches.", ("Numbers", 1, 4)),
    ("tsava", "tsava", "צָבָא", "tsava",
     "A host, an army — massed ranks for war (Numbers 1:3, 'all who go out to the tsava'). The census is a military muster: everyone counted is a soldier. The same word makes the divine title 'Jehovah of HOSTS' (the armies of heaven), and names the 'host of heaven' — sun, moon, and stars arrayed like troops. For the Levites the tsava is redefined: their 'service/warfare' is the tabernacle, not the battlefield (Numbers 4:23).", ("Numbers", 1, 3)),
    ("gulgolet", "gulgolet", "גֻּלְגֹּלֶת", "gulgolet",
     "A skull, a head — the census counts 'by their gulgolot,' head by head, each person reckoned singly (Numbers 1:2, 18; KJV 'by their polls'). The word for a rounded skull gives us, through Aramaic Gulgalta and Latin Calvaria, the two names of one hill: GOLGOTHA, 'the place of the skull' (Matthew 27:33). Every head is numbered and known — the same word that tallies an army will one day name a place of execution outside Jerusalem.", ("Numbers", 1, 2)),
    ("el-olam", "El Olam", "אֵל עוֹלָם", "El Olam",
     "'The Everlasting God' — the fourth El-name collected at a landmark: El Elyon at Salem (14:18), El Roi at Hagar's well (16:13), El Shaddai at the covenant (17:1), and El Olam at a tamarisk beside a sworn well (21:33). NWT, keeping its clock, 'the indefinitely lasting God.'", (21, 33)),
    ("eshel", "eshel", "אֵשֶׁל", "eshel",
     "The tamarisk — a desert tree that lives for centuries; planting one at a well (Genesis 21:33) is filing a claim on the future in slow motion. KJV, following an older guess, 'planted a GROVE'; ASV 'a tamarisk tree.'", (21, 33)),
    ("sheva", "sheva / nishba", "שֶׁבַע / נִשְׁבַּע", "sheva / nishba",
     "Seven — and the oath: Hebrew's verb 'to swear' (nishba) is literally 'to SEVEN oneself.' So Be'er Sheva (Genesis 21:31) reads two ways that are one — 'well of the seven' (the ewe-lambs, v30) and 'well of the oath' (v31): one word wearing both faces, and the text offers both etymologies on purpose.", (21, 31)),
    # ---- Jeremiah 20 (Hebrew) ----
    ("magor-missaviv", "Magor-Missaviv", "מָגוֹר מִסָּבִיב", "magor missaviv",
     "'Terror all around' — magor (dread) + missaviv (from every side): the name Jeremiah gives his jailer Pashhur after a night in the stocks (20:3), and the prophet's own signature phrase of dread (6:25; 46:5; 49:29; Psalm 31:13 borrows it). By 20:10 the street is chanting it back at him as a taunt. KJV runs it together as one grim word: 'Magormissabib.'", ("Jeremiah", 20, 3)),
    ("patah", "patah", "פָּתָה", "patah",
     "To persuade — entice — seduce — deceive: the whole scandalous range of Jeremiah 20:7, 'You enticed me, Jehovah, and I was enticed.' The same verb sends the lying spirit to 'entice' Ahab (1 Kings 22) and names the seducer of Exodus 22:16. KJV/NIV read 'deceived'; NWT 'fooled'; this translation 'enticed,' with the darker readings carried in the note. His enemies use it too (20:10): 'perhaps he will be enticed.'", ("Jeremiah", 20, 7)),
    ("mahpekhet", "mahpekhet", "מַהְפֶּכֶת", "mahpekhet",
     "The stocks — literally 'the TWISTER,' a frame that bent the prisoner's body (Jeremiah 20:2; paired with the collar at 29:26). Built on haphakh, the overturning-verb of Sodom — so Jeremiah's chapter is bracketed by one root: twisted in the mahpekhet at its start, wishing 'the cities Jehovah overthrew' on the world at its end (20:16).", ("Jeremiah", 20, 2)),
    ("kelayot", "kelayot", "כְּלָיוֹת", "kelayot",
     "Kidneys — Hebrew's seat of the hidden self, the innermost person: 'who sees kidneys and heart' (Jeremiah 20:12). KJV renders 'the REINS' (Latin renes, kidneys) — four centuries of English readers picturing bridles by accident. Revelation quotes the pair back in Greek: 'I am the one who searches kidneys and hearts' (2:23).", ("Jeremiah", 20, 12)),
    # ---- Jeremiah 21 (Hebrew) ----
    ("niflaot", "niflaot", "נִפְלָאוֹת", "niflaot",
     "'Wondrous works' — the Exodus-wonder word (pele, wonder): the sea, the plagues, Sennacherib's melted army. Zedekiah's delegation asks for one more (Jeremiah 21:2) — 'perhaps Jehovah will deal with us according to all his wondrous works' — and the answer is that the Exodus God is already on the field, on the other side.", ("Jeremiah", 21, 2)),
    ("shalal", "shalal", "שָׁלָל", "shalal",
     "Spoil, plunder — and the grimmest idiom built on it: nefesh li-shalal, 'his life as SPOIL' (Jeremiah 21:9; KJV 'his life shall be unto him for a prey'): the only plunder you will carry out of this war is yourself. Jeremiah later hands it to the two men who trusted him, as a personal promise — Ebed-melech (39:18) and Baruch (45:5).", ("Jeremiah", 21, 9)),
    ("dever", "dever", "דֶּבֶר", "dever",
     "Pestilence — the third leg of Jeremiah's drumbeat triad, SWORD–FAMINE–PESTILENCE, which tolls through the book from 21:7 on (some fifteen times). The same word names the Exodus cattle-plague; in the siege oracles it is the death that needs no army.", ("Jeremiah", 21, 6)),
    ("zeroa-netuyah", "zeroa netuyah", "זְרוֹעַ נְטוּיָה", "zeroa netuyah",
     "'Outstretched arm' — the redemption formula: 'a mighty hand and an outstretched arm' is how Deuteronomy says Israel was brought out of Egypt, repeated like a creed. Jeremiah 21:5 turns it around — 'I myself will fight AGAINST you with an outstretched hand and with a strong arm': the most chilling diplomatic note in the book.", ("Jeremiah", 21, 5)),
    # ---- Jeremiah 22 (Hebrew) ----
    ("hoy", "hoy", "הוֹי", "hoy",
     "A cry that does double duty in this chapter — and the Hebrew makes both edges sound alike. It is the prophet's 'WOE!', the funeral-toll flung at the living: 'HOY, him who builds his house without righteousness' (22:13). But hoy is ALSO the wail cried OVER a corpse — 'Alas (hoy), my brother! … Alas (hoy), lord!' (22:18) — the customary lament. So the woe that opens over Jehoiakim alive is the very cry his death will be denied: he gets the prophet's hoy, never the mourners'. KJV 'Woe' in v13, 'Ah!' in v18 — the same word.", ("Jeremiah", 22, 13)),
    ("chotam", "chotam", "חוֹתָם", "chotam",
     "A SIGNET — the engraved seal-ring pressed into wax or clay to stamp a document with a king's authority (the same word for the seals archaeologists dig up as clay bullae). To be God's signet 'on my right hand' (22:24) is to carry delegated royal power itself; to be 'torn off' it is to be un-authorized, decommissioned. The image is deliberately reversed for Coniah's own grandson: 'I will make you like a SIGNET, for I have chosen you,' God tells Zerubbabel (Haggai 2:23) — the ring pressed back onto the cursed line.", ("Jeremiah", 22, 24)),
    ("ariri", "ariri", "עֲרִירִי", "ariri",
     "'Childless / stripped' — the sentence on Coniah, 'write this man ariri' (22:30). Not that he had no children (he fathered seven sons in exile, 1 Chronicles 3:17) — the verse defines its own sense in the next line: childless AS TO THE THRONE, 'for none of his seed will prosper, sitting on the throne of David.' The root sense is 'stripped bare' (Genesis 15:2, Abram 'goes childless'). KJV/NWT both 'childless'; the qualification, not the word, is where the whole puzzle of the messianic line turns.", ("Jeremiah", 22, 30)),
    ("betsa", "betsa", "בֶּצַע", "betsa",
     "Dishonest gain, unjust profit — from a root meaning 'to cut off (a piece for oneself).' Jehoiakim's 'eyes and heart are on nothing but your betsa' (22:17): the greed that builds a cedar palace on unpaid labor. It is the disqualifying vice of a ruler (the corrupt judges 'turn aside after betsa,' 1 Samuel 8:3) — the exact opposite of the father who 'judged the cause of the poor and needy' (22:16). KJV 'covetousness.'", ("Jeremiah", 22, 17)),
    ("moledet", "moledet", "מוֹלֶדֶת", "moledet",
     "Native land, kindred, birthplace — 'the land of his birth (erets moladto)' that exiled Shallum will never see again (22:10). It is Abram's word, the thing the call told him to LEAVE: 'go from your land and your moledet and your father's house' (Genesis 12:1). Abraham surrendered his homeland by promise and gained a nation; the last kings lose theirs by force and gain a grave in a foreign land — the call run backward.", ("Jeremiah", 22, 10)),
    # ---- Daniel 12 (Hebrew) ----
    ("zohar", "zohar", "זֹהַר", "zohar",
     "'Radiance, shining' — Daniel 12:3's wise 'shine like the SHINING of the vault' (yazhiru ke-zohar, the cognate kept). Rare: only here and Ezekiel 8:2. Eight centuries later the masterwork of Jewish mysticism took its title from this verse's word — the Zohar, 'Radiance.'", ("Daniel", 12, 3)),
    ("diron", "dir'on", "דֵּרָאוֹן", "dir'on",
     "'Abhorrence' — the dark pole of Daniel 12:2's double waking ('these to everlasting life, and these to... everlasting abhorrence'; KJV 'contempt'). Only twice in the Hebrew Bible: here, and Isaiah 66:24's closing image of corpses 'whose worm shall not die' — the picture Jesus borrows for Gehenna.", ("Daniel", 12, 2)),
    ("qets", "qets", "קֵץ", "qets",
     "'End' — from a root meaning CUT OFF: the drumbeat of Daniel 12. 'The time of the end' (et qets, 12:4, 9), 'the end of the wonders' (12:6), and the book's last breath — 'go on to the end... at the end of the days' (12:13). Genesis 6:13 uses it first: 'the end of all flesh has come before me.'", ("Daniel", 12, 4)),
    ("goral", "goral", "גּוֹרָל", "goral",
     "'Lot' — the pebble drawn or cast to divide land, duty, destiny; hence one's allotted PORTION (Joshua's tribal allotments are goral country). Daniel's last word of destiny: 'you shall stand up to your LOT at the end of the days' (12:13) — a share with your name on it, not a game of chance.", ("Daniel", 12, 13)),
    ("moed", "mo'ed", "מוֹעֵד", "mo'ed",
     "'Appointed time' — Genesis 1:14's word: the lights are hung 'for appointed times' (mo'adim), this translation's fixed rendering. In Daniel 12:7 time itself is measured in them — 'an appointed time, appointed times, and a half': the broken seven, three and a half, sworn by the One who lives forever. Later the word also names the tent of MEETING (ohel mo'ed) — appointed time, appointed place.", (1, 14)),
    # ---- Matthew 5 (Greek) ----
    ("makarios", "makarios", "μακάριος", "makarios",
     "'Happy, fortunate' — the Beatitude word (Matthew 5:3-11, nine times), and the Greek Bible's standing rendering of the Hebrew ashrei (Psalm 1:1; Daniel 12:12). It declares an enviable CONDITION, not a blessing pronounced (that's eulogētos). KJV/Geneva/Douay 'Blessed'; this translation reads 'Happy,' with the NWT — the same call it made for ashrei.", ("Matthew", 5, 3)),
    ("geenna", "Gehenna", "γέεννα", "geenna",
     "The Greek shape of gei-hinnom, the Valley of Hinnom below Jerusalem — the child-sacrifice valley of the kings (Josiah defiled its burning-place, 2 Kings 23:10), which became the standing name for the fiery end of the wicked; its unquenched fire and undying worm come from Isaiah 66:24. KJV translates it away as 'hell fire' (Matthew 5:22); this translation keeps the place-name — real geography doing figurative work.", ("Matthew", 5, 22)),
    ("raca", "Raca", "Ῥακά", "raca",
     "Aramaic rēqa, 'empty-head' — the insult Matthew 5:22 makes actionable, transliterated (not translated) by Matthew himself and left standing by nearly every version since. One of the New Testament's little windows into the Aramaic Jesus actually spoke.", ("Matthew", 5, 22)),
    ("iota", "iota / keraia", "ἰῶτα / κεραία", "iōta / keraia",
     "'Not one iota, not one little hook' (Matthew 5:18) — a GREEK sentence pointing at HEBREW letters: iōta stands for yod (י), the alphabet's smallest letter; keraia ('little horn') is the serif-stroke distinguishing near-twin letters. KJV 'one jot or one tittle' — 'jot' IS iota, worn smooth by English mouths.", ("Matthew", 5, 18)),
    ("angareuo", "angareuō", "ἀγγαρεύω", "angareuō",
     "'To press into service' — a Persian word from the royal courier-post (Herodotus' angaroi), by Roman times the soldier's legal right to commandeer a civilian for one mile (milion — a Latin loanword; Rome audible in the Greek). Matthew 5:41: go the second one. The verb returns on Simon of Cyrene, pressed into carrying a cross (27:32).", ("Matthew", 5, 41)),
    ("teleios", "teleios", "τέλειος", "teleios",
     "'Whole, complete, full-grown' — traditionally 'perfect' (KJV, Matthew 5:48), but the word means completeness, not flawlessness: the Greek Bible's counterpart to the Hebrew tamim, El Shaddai's charge to Abram ('walk before me, and be blameless,' Genesis 17:1). Luke's parallel reads 'merciful' (6:36) — the wholeness in question is love without a fence.", ("Matthew", 5, 48)),
    # ---- Matthew 6 (Greek) ----
    ("epiousios", "epiousios", "ἐπιούσιος", "epiousios",
     "The hardest word in the Lord's Prayer — and found NOWHERE else in Greek literature (Origen said the evangelists appear to have coined it). Likely from epienai, 'the coming day': bread FOR THE DAY AHEAD, asked for today (Matthew 6:11) — the manna rhythm. KJV 'daily'; Douay, translating the Vulgate literally, prints the shelf's strangest word: 'supersubstantial bread.'", ("Matthew", 6, 11)),
    ("mamonas", "Mammon", "μαμωνᾶς", "mamōnas",
     "Aramaic mamona, 'wealth, property' — from the same root as amen: that in which one trusts. Left untranslated by Matthew ('You cannot be slaves to God and to Mammon,' 6:24) and by nearly every version since (NIV breaks ranks: 'money'). Not a Canaanite deity — capital personified by the sentence's own grammar: only masters have slaves.", ("Matthew", 6, 24)),
    ("hypokrites", "hypokritēs", "ὑποκριτής", "hypokritēs",
     "In ordinary Greek: a STAGE ACTOR — the masked professional (the theater at Sepphoris stood an hour's walk from Nazareth). The Sermon's word for piety performed to an audience (Matthew 6:2, 5, 16), beside a matching verb in 6:1: righteousness done 'to be GAZED AT' (theathēnai — the root of 'theater'). English 'hypocrite' is this word, worn smooth.", ("Matthew", 6, 2)),
    ("oligopistoi", "oligopistoi", "ὀλιγόπιστοι", "oligopistoi",
     "'Little-faiths' — one Greek word, Matthew's pet name for disciples (6:30; the storm, 8:26; the water, 14:31; the forgotten bread, 16:8). Not FAITHLESS — chronically under-supplied: a diagnosis with affection in it. This translation keeps it as the single word it is: 'you little-faiths.'", ("Matthew", 6, 30)),
    ("battalogeo", "battalogeō", "βατταλογέω", "battalogeō",
     "'To babble on' (Matthew 6:7) — a word found almost nowhere before this verse, quite possibly built to sound like what it means (batta-batta…), and glossed by the next phrase: 'their many words.' KJV 'use not vain repetitions.' The target is pagan-style prayer as word-count — 'your Father knows what you need before you ask him.'", ("Matthew", 6, 7)),
    ("haplous", "haplous", "ἁπλοῦς", "haplous",
     "'Single, simple, undivided' — the healthy eye of Matthew 6:22 (KJV 'single'; NWT 'simple'; NIV 'healthy'), opposed to the 'evil eye,' which in Hebrew idiom is the STINGY eye (Deuteronomy 15:9). Generosity as optics: the undivided eye lights the whole body — and the very next sentence is about divided service: no one can be a slave to two masters.", ("Matthew", 6, 22)),
    # ---- Matthew 7 (Greek) ----
    ("dokos", "karphos / dokos", "κάρφος / δοκός", "karphos / dokos",
     "The splinter and the BEAM (Matthew 7:3-5) — karphos is a chip, a fleck of straw (KJV's famous 'mote'); dokos is a roof-timber, the piece a builder lays across a house. Workshop comedy drawn to scale — from, tradition remembers, a builder's household ('the carpenter's son,' 13:55).", ("Matthew", 7, 3)),
    ("metron", "metron", "μέτρον", "metron",
     "'Measure' — 'with the measure you measure, it will be measured out to you' (Matthew 7:2): the rabbis' own principle, middah keneged middah, measure for measure. The judgment you dispense is the container your own verdict arrives in.", ("Matthew", 7, 2)),
    ("anomia", "anomia", "ἀνομία", "anomia",
     "'Lawlessness' — literally no-Torah-ness (a-nomos). The verdict-word of Matthew 7:23, 'depart from me, you workers of lawlessness' — Psalm 6:8 with the psalmist's seat taken. The charge is not failed performance (the résumé of wonders goes undisputed) but a life unaligned with the will of the Father (7:21).", ("Matthew", 7, 23)),
    ("phronimos", "phronimos", "φρόνιμος", "phronimos",
     "'Prudent, sensible' — the man who built on rock (Matthew 7:24; KJV 'wise'). Matthew's word for practical foresight: it returns picking the wise virgins (25:2), the faithful steward (24:45), and — paired with doves — the serpents (10:16). Opposite: mōros, the fool who built on sand.", ("Matthew", 7, 24)),
    ("exousia", "exousia", "ἐξουσία", "exousia",
     "'Authority' — what astounded the crowds (Matthew 7:29): the scribes taught by citation, rulings in the names of earlier teachers; this preacher's only footnote was 'but I say to you.' Planted where the book can reach it: Matthew's last sentence claims 'ALL authority, in heaven and on earth' (28:18).", ("Matthew", 7, 29)),
    # ---- Revelation 1 (Greek) ----
    ("ekklesia", "ekklēsia", "ἐκκλησία", "ekklēsia",
     "Assembly, the called-out gathering — in secular Greek a city's voting assembly (Acts 19 uses this very word for the Ephesus RIOT), in the Greek Bible the assembly of Israel (qahal). No building, no institution. Tyndale therefore rendered it 'congregation' — and King James's Rule 3 ordered his translators to keep 'the old ecclesiastical words… the word Church not to be translated Congregation.' This translation reads CONGREGATION (with Tyndale, and the NWT after him); 'church' descends from a different word entirely — kyriakon, 'the Lord's house' — and carries the later building with it.", ("Revelation", 1, 4)),
    ("apokalypsis", "apokalypsis", "ἀποκάλυψις", "apokalypsis",
     "Unveiling, uncovering — the book's first word and its name ('Apocalypse' is this word left untranslated). Not 'catastrophe' but disclosure: the pulling-back of a curtain (Revelation 1:1).", ("Revelation", 1, 1)),
    ("pantokrator", "pantokratōr", "παντοκράτωρ", "pantokratōr",
     "'The Almighty' — literally 'the all-holding.' The Greek Bible's rendering of El Shaddai and 'Jehovah of armies'; the word the old English Bibles retro-fitted onto Shaddai (Genesis 17:1) is NATIVE at Revelation 1:8 — Revelation uses it nine times, the rest of the New Testament once.", ("Revelation", 1, 8)),
    ("ho-on", "ho ōn", "ὁ ὢν", "ho ōn",
     "'The One Who Is' — the Greek Bible's rendering of the divine name's explanation at the burning bush (Exodus 3:14). Revelation unfolds it into three tenses ('who is, and who was, and who is coming') and refuses to decline it — the deliberate grammar-break of 1:4.", ("Revelation", 1, 4)),
    ("martys", "martys", "μάρτυς", "martys",
     "Witness — Jesus 'the faithful witness' (Revelation 1:5). In Revelation the word begins its migration toward English 'martyr': the witness whose testimony costs blood.", ("Revelation", 1, 5)),
    ("hades", "hadēs", "ᾅδης", "hadēs",
     "Hades — the Greek Bible's rendering of the Hebrew Sheol, the grave-realm of the dead; NOT the fiery hell of later imagery (KJV prints 'hell' at Revelation 1:18). Christ holds its keys.", ("Revelation", 1, 18)),
    # ---- John 2 (Greek) ----
    ("semeion", "sēmeion", "σημεῖον", "sēmeion",
     "Sign — John's own word for the miracles: a deed that points past itself. Cana is 'the beginning of the signs' (2:11), first of the seven that structure the Gospel's first half — and the same root opens Revelation: 'he made it known in signs' (Rev 1:1).", ("John", 2, 11)),
    ("hora", "hōra", "ὥρα", "hōra",
     "The hour — 'my hour has not yet come' (2:4): John's clock-word for the cross-and-glory, ticking through the Gospel (7:30; 8:20) until at last 'the hour has come' (12:23; 13:1; 17:1).", ("John", 2, 4)),
    ("ti-emoi-kai-soi", "ti emoi kai soi", "τί ἐμοὶ καὶ σοί", "ti emoi kai soi",
     "'What to me and to you?' — a Hebrew idiom in Greek dress (mah-li valakh, Judges 11:12; 2 Samuel 16:10): 'is that our business?' Distance, not disrespect — Jesus to his mother at Cana (2:4).", ("John", 2, 4)),
    ("metretes", "metrētēs", "μετρητής", "metrētēs",
     "A liquid measure, roughly 39 liters. Six stone jars 'of two or three measures each' (2:6) — KJV's 'firkins' — put the good wine in the several-hundred-bottle range: the abundance is the point.", ("John", 2, 6)),
    ("naos", "naos / hieron", "ναός / ἱερόν", "naos / hieron",
     "Two temple-words: hieron, the whole precinct with its courts (where the traders sat, 2:14), and naos, the sanctuary-house itself — the word Jesus chooses for 'destroy this temple' (2:19), and John glosses: the naos of his body (2:21).", ("John", 2, 14)),
    # ---- Revelation 2 (Greek) ----
    ("nikao", "ho nikōn", "ὁ νικῶν", "ho nikōn",
     "'The one who overcomes' — the victor. Each of the seven letters ends with a promise to ho nikōn (Rev 2:7, 11, 17, 26…), and every promise is paid at the book's end: the tree of life (22:2), immunity to the second death (20:6), the new name, the morning star (22:16).", ("Revelation", 2, 7)),
    ("paradeisos", "paradeisos", "παράδεισος", "paradeisos",
     "Paradise — a Persian loan-word for a walled garden, and the very word the Greek Bible chose for EDEN (Genesis 2:8 LXX). 'The tree of life in the paradise of God' (Rev 2:7) is Eden's tree, promised back.", ("Revelation", 2, 7)),
    ("stephanos", "stephanos", "στέφανος", "stephanos",
     "The victor's wreath — the laurel of the games, not a monarch's diadem: 'the crown of life' (Rev 2:10), promised to a city whose ringed acropolis ancient writers praised as 'the crown of Smyrna.'", ("Revelation", 2, 10)),
    ("psephos", "psēphos leukē", "ψῆφος λευκή", "psēphos leukē",
     "The white stone — literally a pebble (NWT's 'white pebble' is exact), with uses all over ancient life: a juror's acquittal vote, an admission token to a feast, an amulet bearing a secret name. Which the promise of Rev 2:17 means is honestly unknown; all three fit a letter about verdicts, banquets, and a new name.", ("Revelation", 2, 17)),
    ("morning-star", "ho astēr ho prōinos", "ὁ ἀστὴρ ὁ πρωϊνός", "ho astēr ho prōinos",
     "The morning star (Rev 2:28) — Venus at dawn, the promise the book decodes only on its last page: 'I am the root and the offspring of David, the bright morning star' (22:16). The gift is the giver.", ("Revelation", 2, 28)),
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
    dict(slug="babel", name="Babel", kind="place", aliases=["Babel"],
         desc="First of Nimrod's cities in Shinar (10:10) and the site of the tower (11:1-9). Its own name, Bab-ili, "
              "means 'Gate of God'; Genesis re-derives it from Hebrew balal, 'confuse' — a deliberate, polemical pun. "
              "One of the most excavated cities of the ancient world (the great ziggurat E-temen-anki likely informed "
              "the tower story). And the story is long: this is the same city that, under Nebuchadnezzar II, became "
              "the empire that besieged Jerusalem and carried Judah captive — for that later chapter of its life, "
              "see Babylon, which has its own entry.",
         refs=[(10, 10), (11, 9)],
         videos=[("Search for the Tower of Babel", "https://www.youtube.com/watch?v=cYc_VgjJfw8")],
         coords=(32.5355, 44.4275, 0.15),
         modern="Babylon ruins, near Hillah, Iraq"),
    dict(slug="shinar", name="Shinar", kind="place",
         desc="The flat southern-Mesopotamian plain (Sumer/Babylonia) — no stone, hence brick and bitumen (11:3); "
              "home of Babel, Erech (Uruk), and Accad (Akkad). The name resurfaces, deliberately archaic, when "
              "Nebuchadnezzar carries the temple vessels 'to the land of Shinar' (Daniel 1:2): the narrator filing "
              "the new empire under the tower's old country.",
         refs=[(10, 10), (11, 2), ("Daniel", 1, 2)], videos=[],
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
         desc="First mentioned as landmarks on the Canaanite border (10:19). Lot drifts toward them by stages in "
              "ch. 13 (their coming ruin already named there, 13:10), the city's wickedness is stated outright at "
              "13:13, in ch. 18 their 'outcry' reaches heaven and Abraham argues the Judge of all the earth down "
              "to ten righteous — and in ch. 19 the sentence falls: sulfur and fire out of the heavens, the cities "
              "and the whole plain overthrown (19:24-29); 'like the overthrow of Sodom' is the prophets' byword "
              "for total ruin ever after. "
              "Expedition Bible's Joel Kramer identifies the site as Tall el-Hammam, in the northern Jordan Valley — "
              "burned, sulfur-rich debris there matches all four destroyed cities of the plain, while a fifth sample "
              "from Zoar's presumed site, spared in the account, did not burn.",
         refs=[(10, 19), (13, 10), (13, 12), (13, 13), (18, 20), (19, 24), (19, 28)],
         videos=[("Sodom burned—Zoar did NOT: the full story of the discovery of the Cities of the Plain",
                  "https://www.youtube.com/watch?v=QjPcSQUY2W0"),
                 ("Sulfur Balls of Sodom and Gomorrah",
                  "https://www.youtube.com/watch?v=jQl4KaRtef8")],
         coords=(31.8402, 35.6737, 0.4), approx=True,
         modern="Tall el-Hammam, Jordan, in the eastern Jordan Valley"),
    dict(slug="ur", name="Ur of the Chaldeans", kind="place",
         desc="Abram's birthplace (11:28,31) — the great Sumerian city of southern Iraq, sacred to the moon god "
              "Nanna (Akkadian Sin), whose ziggurat — his temple — still stands; John Taylor's 1850s dig first fixed "
              "the identification from inscribed cylinders found in the ziggurat, and Leonard Woolley's 1920s-30s "
              "excavations (royal tombs, gold lyres) made it world-famous. 'Of the Chaldeans' is a later-era label, "
              "identifying the city for the text's own readers. Ur's moon-cult, shared with Haran, is the usual "
              "thread offered for why Terah's family migrated between the two (see Haran).",
         refs=[(11, 28), (11, 31)],
         videos=[("EXPEDITION ABRAHAM: from his birthplace at Ur to the Promised Land",
                  "https://www.youtube.com/watch?v=f7-RQZavU3U")],
         coords=(30.9626, 46.1035, 0.15),
         modern="Tell el-Muqayyar, near Nasiriyah, Iraq"),
    dict(slug="haran-city", name="Haran (the city)", kind="place", aliases=["Haran"],
         desc="Caravan city on the northern arc of the route from Ur to Canaan, where Terah's migration stalls and "
              "Terah dies (11:31-32); Abram's call comes here (12:1-4). Like Ur, it was a great cult center of the "
              "moon god (Sin) — the shared devotion is the usual explanation for why the family settled here (the "
              "Bible recalls that Terah 'served other gods,' Joshua 24:2). Babylon's last king Nabonidus later "
              "restored its moon-temple, and David Storm Rice's 1950s excavation of Harran's Great Mosque recovered "
              "the inscriptions that name the site. Spelled differently in Hebrew from Terah's son Haran, whose death "
              "at 11:28 happens before the family even leaves Ur for this place.",
         refs=[(11, 31), (11, 32), (12, 4), (12, 5)],
         videos=[("EXPEDITION ABRAHAM: retracing the route through Haran, from Ur to the Promised Land",
                  "https://www.youtube.com/watch?v=f7-RQZavU3U")],
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
         desc="'House of God' (Beit-El) — the site that gives Genesis one of its great scenes. Abram first camps "
              "east of it and builds his second altar (12:8), but the name is minted later, by his grandson: "
              "fleeing to Haran, Jacob sleeps here on a stone and dreams of a stairway between earth and heaven "
              "with angels ascending and descending, wakes crying 'this is the house of God, the gate of heaven,' "
              "sets his stone up as a pillar, and names the place Bethel — the city having been called LUZ before "
              "(28:11-19). He returns and re-consecrates it after Peniel (35). Centuries on it turns tragic: "
              "Jeroboam sets one of his two golden calves here to keep the northern kingdom from worshipping in "
              "Jerusalem (1 Kings 12:29), and the prophets thereafter pun its name to 'Beth-aven,' house of "
              "iniquity (Hosea 4:15; Amos names it a royal sanctuary he will smash). Identified with Beitin, "
              "north of Jerusalem.",
         refs=[(12, 8), (28, 19)],
         videos=[("BETHEL: Where Jacob Met God", "https://www.youtube.com/watch?v=8cqBePFD9S4")],
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
         refs=[(10, 6), (10, 13), (12, 10), (12, 14), ("Exodus", 1, 1), ("Exodus", 1, 8), ("Exodus", 1, 13)], videos=[],
         coords=(30.05, 31.23, 4.0), approx=True,
         modern="Egypt — the Cairo/Nile Delta area"),
    dict(slug="jordan-plain", name="The Plain of the Jordan (Kikkar)", kind="place", aliases=["the plain of the Jordan"],
         desc="The round, well-watered lower Jordan valley (13:10) — 'like the garden of Jehovah, like the land "
              "of Egypt' — that Lot chooses (13:11) over staying with Abram. Its beauty and its coming ruin are "
              "named in the very same verse.",
         refs=[(13, 10), (13, 11), (13, 12)], videos=[],
         coords=(31.75, 35.55, 0.8), approx=True,
         modern="The lower Jordan Valley, north of the Dead Sea"),
    dict(slug="zoar", name="Zoar", kind="place",
         desc="'Little' — named from Lot's own plea, mid-apocalypse: 'is it not a little one (mits'ar)?' (19:20-22). "
              "A landmark fixing the plain's southern extent at its first mention (13:10), it alone of the plain's "
              "cities is spared, at Lot's asking — the destruction literally waits until he arrives (19:22). Then "
              "Lot, afraid of the town he begged for, leaves it for a cave in the hills (19:30).",
         refs=[(13, 10), (19, 20), (19, 22), (19, 23), (19, 30)],
         videos=[("Sodom burned—Zoar did NOT: the full story of the discovery of the Cities of the Plain",
                  "https://www.youtube.com/watch?v=QjPcSQUY2W0")],
         coords=(31.033, 35.484, 0.3), approx=True,
         modern="Near Ghor es-Safi, Jordan, southeast of the Dead Sea"),
    dict(slug="hebron", name="Hebron", kind="place", aliases=["Hebron", "Kiriath-arba"],
         desc="Where Abram settles after Lot's departure, among the oaks of Mamre, and builds his third altar "
              "(13:18); also called KIRIATH-ARBA, 'town of Arba' (a giant of the Anakim) or 'town of the four.' "
              "It becomes central: Sarah dies here and Abraham buys the cave of Machpelah for her tomb (ch. 23), "
              "the patriarchs' burial place; and it is David's FIRST royal capital, where he reigns seven years "
              "before taking Jerusalem (2 Samuel 5:5). One of the oldest continuously-inhabited towns on earth.",
         refs=[(13, 18), (23, 2), (23, 19)], videos=[],
         coords=(31.5326, 35.0998, 0.15),
         modern="Hebron, West Bank"),
    dict(slug="mamre", name="Mamre (the oaks of)", kind="place", aliases=["Mamre"],
         desc="The tree-grove near Hebron where Abram pitches his tent and builds an altar (13:18) — the third "
              "named tree at one of his altars, after Shechem's tree of Moreh (12:6). Mamre is also a person, an "
              "Amorite ally of Abram's named in the very next chapter (14:13, 24) — the place and the man are not "
              "shown to be connected beyond sharing the name, the same double-use already flagged at Haran. Here, "
              "in the heat of the day, the three visitors arrive and Isaac is promised within the year (18:1-15).",
         refs=[(13, 18), (18, 1), (23, 17), (23, 19), (25, 9)], videos=[("MAMRE — Where God Appeared to Abraham!", "https://www.youtube.com/watch?v=WzunDBINbS4")],
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
              "'people began to call on the name of Jehovah' (4:26).",
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
         desc="'The first mighty man on the earth… a mighty hunter before Jehovah' (10:8-9) — the Table of Nations' "
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
    dict(slug="abram", name="Abram / Abraham", kind="person", aliases=["Abram", "Abraham"],
         desc="Called at 75 from Haran (12:1-4): land, nation, great name, and blessing for 'all the families of the "
              "ground' — Babel's grasped-at name, given instead. Answers with altars at Shechem and Bethel; flinches "
              "into the wife-sister ruse in Egypt (12:10-20). At 99, in the covenant of circumcision, God renames him "
              "ABRAHAM — 'father of a multitude of nations' (17:5), the first person in the Bible God renames — and "
              "he laughs face-down at the promise of a son (17:17). At Mamre he feasts three visitors, then stands "
              "in the road and argues the Judge of all the earth down to ten righteous for Sodom's sake (18:22-33). "
              "At Gerar he replays Egypt's sister-ruse — and is called the Bible's first 'prophet' anyway, defined "
              "by intercession: he prays, and Abimelech's house is healed (20:7, 17).",
         refs=[(11, 26), (12, 1), (12, 4), (12, 7), (12, 10), (17, 1), (17, 5), (17, 17), (17, 23), (18, 2), (18, 23),
               (20, 2), (20, 7), (20, 17)],
         videos=[("EXPEDITION ABRAHAM: his whole journey, from Ur to the Promised Land",
                  "https://www.youtube.com/watch?v=f7-RQZavU3U")]),
    dict(slug="sarai", name="Sarai / Sarah", kind="person", aliases=["Sarai", "Sarah"],
         desc="Abram's wife — introduced with the sentence everything turns on: 'Now Sarai was barren; she had no "
              "child' (11:30). Endangered by the sister-story in Pharaoh's house (12:11-20). After ten childless "
              "years in Canaan she gives her slave-girl Hagar to Abram as a surrogate (16:1-3) — then, despised "
              "in the pregnant girl's eyes, afflicts her until she flees (16:4-6). At the covenant of circumcision "
              "God renames her SARAH — both forms mean 'princess' — and fastens the promise to her own body: 'kings "
              "of peoples shall come from her' (17:15-16); the first woman in the Bible God renames. Behind the "
              "tent flap at Mamre she laughs at the one-year promise, then denies it, afraid — 'No, you did laugh' "
              "(18:12-15); the laugh is kept, and named, in her son. At Gerar the old ruse takes her into a second "
              "royal house — and the disclosure finally comes: she is Abraham's half-sister, his father's daughter "
              "(20:12).",
         refs=[(11, 29), (11, 30), (12, 11), (12, 15), (16, 1), (16, 5), (16, 6), (17, 15), (17, 19), (17, 21),
               (18, 9), (18, 12), (18, 15), (20, 2), (20, 14), (20, 16), (20, 18), (23, 2), (23, 19)], videos=[]),
    dict(slug="lot", name="Lot", kind="person",
         desc="Son of Haran, Abram's orphaned nephew (11:27-28), who travels with him from Haran into Canaan (12:4-5). "
              "He chooses the well-watered plain and pitches his tent toward Sodom (13:10-12), is carried off in the "
              "war of the kings and rescued by his uncle (14:12-16), and by ch. 19 sits in Sodom's own gate. On the "
              "last night he hosts the two angels, offers his daughters to the mob (the text reports, it does not "
              "approve), lingers until he is dragged out by the hand, bargains his refuge down to little Zoar — and "
              "ends in a cave, wine-blind, made ancestor of Moab and Ammon by his own daughters. He speaks his last "
              "recorded word at Zoar; Genesis lets him leave in silence.",
         refs=[(11, 27), (12, 4), (12, 5), (13, 10), (13, 12), (14, 12), (19, 1), (19, 16), (19, 26), (19, 30), (19, 36)], videos=[]),
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
              "names himself 'the Son of Man' (1:51). In Revelation's opening vision he is 'the faithful witness, "
              "the firstborn of the dead, and the ruler of the kings of the earth' (Rev 1:5) — one like a son of man "
              "among the lampstands, wearing the Ancient of Days' own description, who says 'I am the first and the "
              "last... and I was dead, and look: I am alive forever' (Rev 1:13-18).",
         refs=[("Matthew", 7, 28), ("John", 1, 17), ("John", 1, 29), ("John", 1, 36), ("John", 1, 42), ("John", 1, 45), ("John", 1, 50),
               ("Revelation", 1, 1), ("Revelation", 1, 5), ("Revelation", 1, 9)],
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
    dict(slug="cana", name="Cana of Galilee", kind="place", aliases=["Cana"],
         desc="The Galilean village of the first sign — water into wine at a wedding (John 2:1-11); Nathanael's "
              "hometown too (John 21:2), which salts his 'can anything good come out of Nazareth?' with local "
              "rivalry. The site is disputed: Kafr Kanna, on the pilgrim route near Nazareth, has the churches; "
              "Khirbet Qana, across the Bet Netofa valley, has the better archaeology (first-century village, "
              "stone vessels, early pilgrim cave). Coordinates below take Khirbet Qana, marked approximate.",
         refs=[("John", 2, 1), ("John", 2, 11)],
         coords=(32.8214, 35.3010, 0.1), approx=True,
         modern="Khirbet Qana (or Kafr Kanna), Galilee, Israel", videos=[]),
    dict(slug="capernaum", name="Capernaum", kind="place", aliases=["Capernaum"],
         desc="Kefar Nachum, 'village of Nahum' — a fishing town on the north shore of the Sea of Galilee that "
              "becomes the base camp of Jesus' whole Galilean ministry ('his own city,' Matthew 9:1). It enters "
              "this Gospel by a travel-verse (John 2:12) and hosts the bread-of-life discourse in its synagogue "
              "(John 6:59); the synoptics add Peter's house and a string of healings — and Jesus' verdict on the "
              "town that saw the most and believed the least: 'more bearable for Sodom' (Matthew 11:23-24). The "
              "excavated site — the basalt-and-limestone synagogue and the house-church over Peter's house — is "
              "among the best-preserved Gospel settings anywhere.",
         refs=[("John", 2, 12)],
         coords=(32.8809, 35.5753, 0.06),
         modern="Tell Hum (Capernaum), north shore of the Sea of Galilee, Israel",
         videos=[("Capernaum Unearthed: Why will this fishing village be judged harsher than Sodom?",
                  "https://www.youtube.com/watch?v=N0opJ2qGQs4")]),
    dict(slug="jerusalem", name="Jerusalem", kind="place", aliases=["Jerusalem"],
         desc="The holy city — entered by name in this translation's published chapters at John 2:13, though its "
              "story here is far older, and it wore other names first. Its heart, the Temple Mount, is the MORIAH "
              "of Genesis 22 (see that entry): the hill of the Aqedah, drawn into the city only when David and "
              "Solomon expanded it northward to build the Temple. The nearby town of the patriarchs' day is SALEM, "
              "Melchizedek's city (Genesis 14:18), traditionally identified with Jerusalem (Psalm 76:2 makes the "
              "equation); the Jebusites called it JEBUS (Judges 19:10); and the name Jerusalem itself (Urusalim) "
              "appears in the Amarna letters of about 1400 BC — so the city was named centuries before Israel "
              "held it. David took the Jebusite stronghold and made it his capital (2 Samuel 5); Solomon built "
              "the first Temple on Moriah, c. 966 BC (2 Chronicles 3:1). In John, Jesus goes up for the festivals "
              "— three Passovers structure the Gospel — and clears the temple's courts at the first of them "
              "(2:13-22). Nebuchadnezzar besieges it in 605 BC and carries off its temple vessels and its "
              "brightest youths (Daniel 1:1-6). The city of the temple, the exile, the passion — and, in "
              "Revelation's last vision, the descending New Jerusalem with no temple in it at all (Rev 21:22).",
         refs=[("Daniel", 1, 1), ("Matthew", 5, 35), ("John", 2, 13), ("John", 2, 23), ("Jeremiah", 22, 19)],
         coords=(31.7784, 35.2354, 0.12),
         modern="Jerusalem", videos=[]),
    dict(slug="mary-mother", name="Mary (the mother of Jesus)", kind="person",
         aliases=["the mother of Jesus"],
         desc="Never once named in John's Gospel — she is simply 'the mother of Jesus,' present at exactly two "
              "scenes that frame the whole story: the wedding at Cana, where her 'whatever he tells you, do it' "
              "(2:5) is her last recorded sentence in scripture, and the foot of the cross, where Jesus gives "
              "her to the beloved disciple ('Woman, look — your son,' 19:26-27). The synoptics and Acts supply "
              "the name; John keeps her a role: the mother, first and last.",
         refs=[("John", 2, 1), ("John", 2, 3), ("John", 2, 5), ("John", 2, 12)], videos=[]),
    dict(slug="nazareth", name="Nazareth", kind="place", aliases=["Nazareth"],
         desc="Jesus' obscure Galilean hometown, never named in the Old Testament — hence Nathanael's 'Can anything "
              "good come out of Nazareth?'",
         refs=[("John", 1, 45), ("John", 1, 46)], coords=(32.702, 35.297, 0.06),
         modern="Nazareth, Israel", videos=[]),

    # ---- Genesis 14 ----
    dict(slug="melchizedek", name="Melchizedek", kind="person", aliases=["Melchizedek"],
         desc="King of Salem and 'priest of God Most High' (El Elyon) — the Bible's first priest, who meets Abram "
              "returning from battle with bread and wine, blesses him, and receives a tenth of everything. His name "
              "means 'my king is righteousness.' He appears only here and in Psalm 110:4, and the letter to the "
              "Hebrews (chapters 5–7) makes his order the type of Christ's own priesthood.",
         refs=[(14, 18)], videos=[]),
    dict(slug="salem", name="Salem", kind="place", aliases=["Salem"],
         desc="Melchizedek's city (14:18) — almost certainly the old name of Jerusalem ('in Salem is his tent,' "
              "Psalm 76:2); shalem carries the sense of 'peace, whole.'",
         refs=[(14, 18)], coords=(31.777, 35.234, 0.05), approx=True, modern="Jerusalem", videos=[]),
    dict(slug="siddim", name="Valley of Siddim (the Salt Sea)", kind="place",
         aliases=["Valley of Siddim", "Siddim"],
         desc="Where the kings gave battle, glossed by the text itself as 'the Salt Sea' — the Dead Sea basin, "
              "'pit after pit of tar' (14:3, 8, 10). The bitumen the basin still seeps trapped the fleeing kings. "
              "The exact cities of the plain are debated (see Sodom and Gomorrah).",
         refs=[(14, 3), (14, 8), (14, 10)], coords=(31.4, 35.45, 0.7), approx=True,
         modern="the Dead Sea basin", videos=[]),
    dict(slug="dan-city", name="Dan", kind="place", aliases=["Dan"],
         desc="The northern point Abram pursued the raiders to (14:14) — and an anachronism: the town was not "
              "called Dan until the tribe of Dan captured and renamed it centuries later (Judges 18:29), so a later "
              "editor has updated an older place-name.",
         refs=[(14, 14)], coords=(33.248, 35.652, 0.05), modern="Tel Dan, northern Israel", videos=[]),
    dict(slug="damascus", name="Damascus", kind="place", aliases=["Damascus"],
         desc="Abram pursued the eastern kings as far as Hobah, 'north of Damascus' (14:15) — the ancient Aramean "
              "city, already a fixed landmark in the patriarch's day. The north-south corridor past Damascus is the "
              "very road Abram had come down from Haran on his migration into Canaan (retraced in the Expedition "
              "Abraham film catalogued on the Ur and Abram entries) — here it simply runs the other way: the route "
              "up which the eastern kings retreated, and he chased them.",
         refs=[(14, 15)], coords=(33.513, 36.292, 0.06), modern="Damascus, Syria", videos=[]),

    # ---- Genesis 15 ----
    dict(slug="eliezer", name="Eliezer of Damascus", kind="person", aliases=["Eliezer of Damascus", "Eliezer"],
         desc="Abram's servant and, before a son was born, his heir-presumptive (15:2) — 'the steward of my house.' "
              "The Hebrew that names him (ben-mesheq beiti) is famously obscure. Jewish tradition identifies him "
              "with the UNNAMED 'senior servant who ruled over all Abraham had' sent to find Isaac's bride in "
              "Genesis 24 — the most-developed servant in Genesis, and pointedly left nameless there so that his "
              "whole character is his faithfulness: he prays for his master's success, tests the girl for kindness "
              "rather than beauty, and refuses even to eat until his errand is told (24:33). The chapter never "
              "confirms the identification, but the man who once stood to inherit everything is a fitting choice "
              "to go win the heir's wife and hand the inheritance on.",
         refs=[(15, 2), (24, 2)], videos=[]),
    dict(slug="river-of-egypt", name="the river of Egypt", kind="place",
         aliases=["the river of Egypt", "river of Egypt"],
         desc="The south-western boundary of the land granted in the covenant (15:18), paired with the Euphrates. "
              "Usually identified not with the Nile but with the Wadi el-Arish, the seasonal 'Brook of Egypt' on "
              "Egypt's frontier.",
         refs=[(15, 18)], coords=(31.13, 33.80, 0.2), approx=True,
         modern="Wadi el-Arish (the Brook of Egypt), Sinai", videos=[]),

    # ---- Genesis 16 ----
    dict(slug="hagar", name="Hagar", kind="person",
         desc="Sarai's Egyptian slave-girl, given to Abram as a surrogate (16:1-3). When she flees, the angel of "
              "Jehovah — the Bible's first — finds her on the desert road home to Egypt: she is the first person "
              "in the Bible he visits, the only woman in Genesis to receive the offspring-beyond-counting promise "
              "from God directly (16:10), and the only person in the Bible who confers a name on God — El Ro'i, "
              "'the God who sees me' (16:13). Her story resumes in Genesis 21.",
         refs=[(16, 1), (16, 4), (16, 8), (16, 13), (16, 15), (21, 9), (21, 14), (21, 17)], videos=[]),
    dict(slug="ishmael", name="Ishmael", kind="person",
         desc="'God hears' (yishma-El) — named by the angel for the affliction Jehovah heard (16:11), born when "
              "Abram was 86 (16:15-16), and his only son for the next thirteen years. The oracle makes him 'a "
              "wild donkey of a man' (16:12): steppe-free, masterless. At thirteen he is circumcised beside his "
              "father on the covenant's first day (17:23-26), and 'as for Ishmael, I have heard you' (17:20) "
              "honors his name even as the covenant passes to Isaac. Genesis gives him twelve princes (25:12-16) "
              "and a place beside Isaac at their father's grave (25:9); later tradition — Jewish, Christian, and "
              "Islamic — remembers him as ancestor of the Arab peoples.",
         refs=[(16, 11), (16, 15), (16, 16), (17, 18), (17, 20), (17, 25), (25, 9), (25, 12), (25, 17), (28, 9)], videos=[]),
    dict(slug="shur", name="Shur", kind="place",
         desc="'Wall' — the desert fronting Egypt's north-east frontier, possibly named for the Egyptian line of "
              "border forts, and crossed by the caravan road from Canaan. Hagar is found 'on the way to Shur' "
              "(16:7): an Egyptian, running home. Israel will cross the same wilderness from the other side "
              "after the sea-crossing (Exodus 15:22).",
         refs=[(16, 7)], videos=[]),
    dict(slug="beer-lahai-roi", name="Beer-lahai-roi", kind="place",
         desc="'The well of the Living One who sees me' — the desert spring where the angel found Hagar, its "
              "name minted from her own sentence (16:13-14). Fixed 'between Kadesh and Bered,' but Bered appears "
              "nowhere else, so the spot is lost to the map. Isaac — the son who will displace Ishmael — later "
              "arrives from, and settles beside, this same well (24:62; 25:11).",
         refs=[(16, 14), (24, 62)], videos=[]),
    dict(slug="kadesh", name="Kadesh", kind="place",
         desc="The great oasis of the north-east Sinai / Negev frontier — Kadesh-barnea, usually identified with "
              "the springs at Ein el-Qudeirat / Ein Qadis. Named in the war of the kings as En-mishpat, 'spring "
              "of judgment' (14:7); a fixed point for Beer-lahai-roi (16:14); and, centuries on, the wilderness "
              "base-camp of the Exodus generation (Numbers 13-20).",
         refs=[(14, 7), (16, 14)], coords=(30.6486, 34.4214, 0.2),
         modern="Ein el-Qudeirat (Tell el-Qudeirat), north-east Sinai", videos=[]),

    # ---- Genesis 17 ----
    dict(slug="isaac", name="Isaac", kind="person",
         desc="Yitschaq, 'he laughs' — named by God before he is conceived, from Abraham's own face-down laugh "
              "(17:17-19), and given the first hard date on the promise: 'at this appointed time next year' "
              "(17:21). The covenant's appointed heir — 'my covenant I will establish with Isaac' — announced a "
              "chapter before Sarah herself hears of it. Born in Genesis 21; Beer-lahai-roi, Hagar's well, will "
              "later be his home (24:62; 25:11).",
         refs=[(17, 19), (17, 21), (21, 3), (21, 5), (21, 10), (22, 2), (22, 9), (25, 11), (25, 19), (25, 21), (26, 1), (26, 12), (26, 24), (27, 1), (27, 22), (28, 1)], videos=[]),

    # ---- Genesis 19 ----
    dict(slug="moab-ammon", name="Moab and Ammon", kind="people",
         aliases=["Moab", "Ben-Ammi", "Ammon"],
         desc="Israel's two kin-nations across the Jordan, born in the cave above Zoar on the worst night in "
              "Genesis: Moab ('from father,' the text's own sound-gloss) to Lot's firstborn daughter, Ben-Ammi "
              "('son of my kin,' father of the Ammonites) to the younger (19:30-38). The Bible remembers the "
              "cousinhood without flattery — and then hands the line its grace note: from Moab comes Ruth, "
              "great-grandmother of David (Ruth 4:17), named in the genealogy of Jesus (Matthew 1:5). Still on "
              "the map four centuries after Genesis closes: Daniel's last vision has Edom, Moab, and the chief "
              "of the sons of Ammon slipping the final king's hand (Daniel 11:41).",
         refs=[(19, 37), (19, 38), ("Daniel", 11, 41)], videos=[]),

    # ---- Genesis 20 ----
    dict(slug="gerar", name="Gerar", kind="place",
         desc="A town of the western Negev borderland, on the road between Canaan and Egypt — where Abraham "
              "'sojourns' (gur, 20:1; the name nearly rhymes with the verb) and replays the sister-ruse on king "
              "Abimelech. Isaac will repeat both the sojourn and the ruse here (ch. 26). Usually identified with "
              "Tel Haror (Tell Abu Hureira) in the Nahal Gerar valley.",
         refs=[(10, 19), (20, 1), (20, 2), (26, 1), (26, 6)], coords=(31.3819, 34.6069, 0.15), approx=True,
         modern="Tel Haror, Nahal Gerar valley, western Negev, Israel", videos=[]),
    dict(slug="philistines", name="the Philistines", kind="person", aliases=["Philistines", "Philistine"],
         desc="The 'sea peoples' of the Canaanite coast — Israel's great enemy through the era of the Judges and "
              "the early kings (Samson and Delilah, the ark captured, Goliath and David, the death of Saul on "
              "Gilboa). They give their name to the whole land: 'Palestine' is 'Philistia.' In Genesis they meet "
              "the patriarchs as the people of Gerar under king Abimelech, who envy Isaac's wealth and stop up "
              "his father's wells (ch. 26). ⚠ This is one of the book's famous ANACHRONISMS: the Philistines as "
              "history knows them — an Aegean people — did not settle the coast until about 1200 BC, centuries "
              "after Abraham and Isaac. Most read 'Philistines' here as an editorial UPDATING of the place-name "
              "for later readers (the same modernizing seen at 'Dan,' 14:14, and 'Ur of the Chaldeans'); a few "
              "posit an earlier Aegean presence. Either way it is the kind of seam the authorship-and-date "
              "debate turns on (see the Genesis introduction).",
         refs=[(26, 1), (26, 8), (26, 14), (26, 15)], videos=[]),
    dict(slug="abimelech", name="Abimelech (of Gerar)", kind="person", aliases=["Abimelech"],
         desc="King of Gerar — 'my-father-is-king,' possibly a dynastic title rather than a personal name (like "
              "'Pharaoh'; an Abimelech meets Isaac in ch. 26 too). The pagan king who argues righteousness with "
              "God at midnight ('will you kill a nation even though righteous?', 20:4 — Abraham's own courtroom "
              "word from 18:23), whose 'integrity of heart' God himself confirms, and who answers being wronged "
              "with gifts and an open invitation (20:14-15). He returns to cut a treaty with Abraham at Beersheba "
              "(21:22-34).",
         refs=[(20, 2), (20, 4), (20, 9), (20, 14), (20, 17), (21, 22), (21, 25), (21, 32), (26, 1), (26, 8), (26, 26)], videos=[]),

    # ---- Daniel 1 ----
    dict(slug="daniel-person", name="Daniel", kind="person", aliases=["Daniel"],
         desc="'El is my judge' — deported from Jerusalem as a youth in 605 BC, renamed Belteshazzar by the empire "
              "(a name the narrator quietly declines to use), trained three years in Babylon's cuneiform "
              "curriculum, and found 'ten hands better' than the court's own diviners (1:20). He serves through "
              "the entire exile — 'until the first year of King Cyrus' (1:21), 605 to 539 BC — under Babylonian "
              "and then Persian kings, interpreter of dreams in the book's first half, seer of visions in its "
              "second. Ezekiel, his contemporary, already uses the name proverbially for righteousness and wisdom "
              "(Ezekiel 14:14; 28:3).",
         refs=[("Daniel", 1, 6), ("Daniel", 1, 8), ("Daniel", 1, 17), ("Daniel", 1, 21),
               ("Daniel", 12, 4), ("Daniel", 12, 13)], videos=[]),
    dict(slug="nebuchadnezzar", name="Nebuchadnezzar II", kind="person", aliases=["Nebuchadnezzar", "Nebuchadrezzar"],
         desc="King of Babylon 605–562 BC — the empire's great builder (the Ishtar Gate, the ziggurat Etemenanki) "
              "and Jerusalem's destroyer: the 605 campaign (the year of Carchemish, fixed by the Babylonian "
              "Chronicle) took Daniel; 597 took king Jehoiachin; 586 burned the city and the temple. Daniel's "
              "court tales give him a dream he refuses to tell (ch. 2), a furnace (ch. 3), a humbling madness — "
              "and, uniquely among scripture's tyrants, a doxology (4:34-37). Douay, via the Greek, spells him "
              "Nabuchodonosor.",
         refs=[("Daniel", 1, 1), ("Daniel", 1, 18), ("Jeremiah", 21, 2), ("Jeremiah", 21, 7)], videos=[]),
    dict(slug="hananiah-mishael-azariah", name="Hananiah, Mishael, and Azariah", kind="person",
         aliases=["Hananiah", "Mishael", "Azariah", "Shadrach", "Meshach", "Abednego"],
         desc="Daniel's three companions from Judah — 'Yah has been gracious,' 'who is what El is?', 'Yah has "
              "helped' — renamed Shadrach, Meshach, and Abednego by the empire (1:7; each new name smuggles in a "
              "Babylonian god, Nebo's apparently garbled to 'Nego'). They share the vegetable test and the "
              "ten-hands verdict (1:19-20); their own hour, the furnace, comes in chapter 3.",
         refs=[("Daniel", 1, 6), ("Daniel", 1, 7), ("Daniel", 1, 11), ("Daniel", 1, 19)], videos=[]),

    # ---- Daniel 11 ----
    dict(slug="darius-the-mede", name="Darius the Mede", kind="person", aliases=["Darius the Mede", "Darius"],
         desc="The king 'who received the kingdom' at Babylon's fall in Daniel's telling (5:31; 11:1 stands 'in "
              "his first year') — and the book's famous historical puzzle: no king of this name appears in the "
              "Babylonian or Persian records between Belshazzar and Cyrus. The proposals: a throne-name of Cyrus "
              "himself ('Darius the Mede, that is, Cyrus the Persian' is even a possible reading of 6:28); "
              "Gubaru/Ugbaru, the general-governor who took Babylon the night it fell; or an error of the "
              "tradition. Reported, not adjudicated.",
         refs=[("Daniel", 11, 1)], videos=[]),
    dict(slug="antiochus-iv", name="Antiochus IV Epiphanes", kind="person",
         desc="Seleucid king 175–164 BC — never named in Daniel (the text calls him 'a contemptible man,' 11:21), "
              "but wearing his biography: the throne seized by intrigue, the high priest Onias III murdered, two "
              "Egyptian wars, the Roman circle in the sand at Eleusis (168 BC), and the desecration of Jerusalem's "
              "temple — the daily offering halted and 'the abomination that desolates' erected, 15 Kislev 167 BC "
              "(1 Maccabees 1:54 quotes Daniel's own phrase for it). He styled himself Epiphanes, 'God Manifest'; "
              "contemporaries punned Epimanes, 'the madman.' He died at Tabae in Persia, 164 BC — a death whose "
              "mismatch with Daniel 11:40-45 is the oldest crux in the book's interpretation (Porphyry vs Jerome; "
              "see the chapter's notes).",
         refs=[("Daniel", 11, 21), ("Daniel", 11, 31)], videos=[]),

    # ---- Matthew 5 ----
    dict(slug="mount-of-beatitudes", name="The Mount of Beatitudes", kind="place",
         desc="'He went up the mountain; and when he had sat down…' (Matthew 5:1) — the unnamed hillside of the "
              "Sermon on the Mount, somewhere above the Sea of Galilee's northwest shore near Capernaum, the "
              "ministry's home base. Tradition since the Byzantine pilgrims has settled on the slope now called "
              "the Mount of Beatitudes above Tabgha — a natural amphitheater where a seated voice genuinely "
              "carries. Luke's parallel sermon stands 'on a level place' (6:17); a plateau on a hillside "
              "satisfies both readers and both texts.",
         refs=[("Matthew", 5, 1)],
         coords=(32.8807, 35.5556, 0.06),
         modern="Mount of Beatitudes, above Tabgha, northwest shore of the Sea of Galilee, Israel",
         videos=[]),

    # ---- Matthew 6 ----
    dict(slug="solomon", name="Solomon", kind="person", aliases=["Solomon"],
         desc="David's son, Israel's third king — builder of the first temple, proverbially the wisest and "
              "richest man of his age: the gold shields, the ivory throne, the fleet bringing 'gold, and "
              "silver, ivory, and apes, and peacocks' (1 Kings 10). He enters this site not at his zenith but "
              "losing a beauty contest to a wildflower: 'not even Solomon, in all his glory, was clothed like "
              "one of these' (Matthew 6:29). Matthew's opening genealogy runs the royal line through him "
              "(1:6-7), and Jesus will invoke him once more: 'something greater than Solomon is here' (12:42).",
         refs=[("Proverbs", 1, 1), ("Matthew", 6, 29)], videos=[]),

    # ---- Exodus 1 ----
    dict(slug="exodus-pharaoh", name="Pharaoh (of the Exodus)", kind="person", aliases=["Pharaoh"],
         desc="The unnamed king of Exodus 1 — 'a new king over Egypt who did not know Joseph' (1:8) — who "
              "turns a rescued family into a slave force and orders the newborn boys drowned. Pharaoh is a "
              "title ('great house'), not a name, and the story pointedly withholds the man's name while "
              "keeping the midwives'. WHICH pharaoh depends on the date of the Exodus, and this translation "
              "follows the EARLY DATE (1446 BC, from 1 Kings 6:1's '480 years' before Solomon's temple), "
              "argued in our own time most carefully — and, Michael judges, least tendentiously — by JOEL "
              "KRAMER of Expedition Bible (Associates for Biblical Research). On that reading: the pharaoh of "
              "the OPPRESSION here is Thutmose III (reigned c. 1479–1425 BC), Egypt's great empire-builder, "
              "whose relentless Canaan campaigns created the demand for the store-cities Israel is forced to "
              "build; the pharaoh of the EXODUS itself, a generation later, is his son Amenhotep II. Kramer's "
              "film below makes the striking case that Amenhotep II did NOT drown (Scripture says the ARMY "
              "drowned, not pharaoh, Exodus 14:28; Psalm 136:15) — he reigned on, his Canaan campaigns "
              "abruptly ceasing after 1446, and was buried in tomb KV35, whose mummy survives: 'the tomb of "
              "the Exodus pharaoh you can visit.' The DREAM STELE of his successor Thutmose IV — which needs "
              "a god's promise to explain why he, not the firstborn, took the throne — fits a firstborn who "
              "died (Exodus 12:29). The store-city name 'Raamses' (1:11), the mainstay of the rival LATE date "
              "(Ramesses II, ~1250 BC, the academic majority), is best read as an updated place-name — the "
              "same editorial modernizing already seen at 'Dan' (Genesis 14:14) and 'Ur of the Chaldeans.'",
         refs=[("Exodus", 1, 8), ("Exodus", 1, 11), ("Exodus", 1, 22)],
         videos=[("Tomb of the Exodus Pharaoh: What Was Found & Why You Don't Know About It!",
                  "https://www.youtube.com/watch?v=mJP4pVjnWpk")]),
    dict(slug="shiphrah-puah", name="Shiphrah and Puah", kind="person", aliases=["Shiphrah", "Puah"],
         desc="The two Hebrew midwives of Exodus 1:15-21 — Shiphrah ('beauty') and Puah ('splendor,' or "
              "'one who cries out') — who commit the FIRST recorded act of civil disobedience in the Bible: "
              "ordered by the king of Egypt to kill the newborn boys on the birthing-stones, they 'feared "
              "God' (yare Elohim) and refused, letting the boys live. Their nimble answer to Pharaoh — the "
              "Hebrew women give birth before a midwife can arrive — the narrator does not stop to judge; "
              "'God dealt well with the midwives, and made them households' (families of their own). The story "
              "withholds the mighty pharaoh's name and preserves these two — the moral inversion the whole "
              "book runs on. (Whether they were Hebrew women or Egyptian midwives OF the Hebrews the grammar "
              "leaves open; the tradition made them Jochebed and Miriam, Moses' mother and sister.)",
         refs=[("Exodus", 1, 15), ("Exodus", 1, 17), ("Exodus", 1, 21)], videos=[]),
    dict(slug="pithom-raamses", name="Pithom and Raamses", kind="place", aliases=["Pithom", "Raamses"],
         desc="The two 'store-cities' (arei miskenot — supply depots / garrison-granaries) the enslaved "
              "Israelites build for Pharaoh (Exodus 1:11), in the eastern Nile Delta. RAAMSES is the city "
              "later known as Pi-Ramesses, the Delta capital built up by Ramesses II (13th c.) near ancient "
              "Avaris (Tell el-Dab'a / Qantir) — which is why the name anchors the LATE date of the Exodus. "
              "On the EARLY date (see the Exodus-pharaoh entry), 'Raamses' is an updated place-name for a "
              "site that existed earlier, like 'Dan' for Laish. PITHOM (Egyptian Per-Atum, 'house of Atum') "
              "is usually located at Tell el-Retabeh or Tell el-Maskhuta in the Wadi Tumilat. Both guard "
              "Egypt's vulnerable northeastern frontier — the road Israel will later walk OUT.",
         refs=[("Exodus", 1, 11)],
         coords=(30.8, 31.83, 0.4), approx=True,
         modern="Eastern Nile Delta: Raamses = Qantir/Tell el-Dab'a; Pithom = Tell el-Retabeh, Egypt"),
    dict(slug="joseph", name="Joseph", kind="person", aliases=["Joseph"],
         desc="Jacob's eleventh son, sold into Egypt by his brothers and risen to be its vizier — the man "
              "whose foresight in the famine saved Egypt and brought Jacob's household of seventy down to "
              "settle there (his story fills Genesis 37–50, not yet on this site). Exodus opens on the far "
              "side of his life: 'Joseph died, and all his brothers, and all that generation' (1:6), and then "
              "the fatal hinge — 'a new king arose who did not know Joseph' (1:8). The rescue is forgotten; "
              "the rescued become slaves. His bones, by his own oath, will be carried out of Egypt at the "
              "Exodus (Genesis 50:25; Exodus 13:19) — the one man of Genesis who makes the journey home.",
         refs=[(30, 24), ("Exodus", 1, 5), ("Exodus", 1, 6), ("Exodus", 1, 8)], videos=[]),

    # ---- Exodus 2 ----
    dict(slug="moses", name="Moses", kind="person", aliases=["Moses"],
         desc="Israel's deliverer, lawgiver, and prophet — born to a Levite couple (Amram and Jochebed) "
              "under Pharaoh's death-order, hidden three months, then floated on the Nile in a papyrus ARK "
              "(the same word, tevah, as Noah's; see the dictionary) and drawn out by Pharaoh's own daughter, "
              "who raises him in the Egyptian court. Grown, he kills an Egyptian overseer, flees to Midian, "
              "marries Zipporah, and is called back at the burning bush to bring Israel out (Exodus 3). The "
              "New Testament frames his life in three forties (Acts 7:23, 30, 36): forty years an Egyptian "
              "prince, forty a Midianite shepherd, forty leading Israel; he dies at 120 (Deuteronomy 34:7), "
              "the prophet 'whom Jehovah knew face to face.' "
              "<strong>His name is Egyptian.</strong> The story gives a Hebrew reason — Pharaoh's daughter "
              "names him Mosheh 'because I DREW HIM OUT (meshitihu) of the water' (2:10), from the Hebrew verb "
              "mashah, 'to draw out.' But the name itself is the ordinary Egyptian element MOSE / MES, 'born "
              "of, son, child' — the very piece in THUT-MOSE ('born of Thoth'), AH-MOSE, and RA-MESSES ('born "
              "of Ra') — the kind of theophoric court-name an Egyptian princess would actually give (likely "
              "with a god's name once attached and later dropped). Even the Hebrew wordplay betrays the seam: "
              "the form Mosheh is ACTIVE, 'the one who draws out' — not the passive mashuy, 'drawn out,' that "
              "the daughter's own explanation would require — a Hebrew pun laid over a genuinely Egyptian "
              "name. Far from an embarrassment, that Egyptian name is a fingerprint of authenticity: a later "
              "writer inventing a national hero would hardly hand him a foreign name advertising an Egyptian "
              "upbringing. Ancient Jewish writers already knew it was Egyptian (Philo; Josephus derives it "
              "from the Egyptian for water + saved). "
              "<strong>Who he likely was.</strong> On the EARLY DATE this translation follows (Exodus 1446 BC; "
              "see the Pharaoh-of-the-Exodus entry and Joel Kramer / Expedition Bible), Moses is born about "
              "1526 BC and raised in the 18th-dynasty court during the reign of Thutmose I–III — the pharaoh "
              "he later flees (2:15) being Thutmose III, whose death (2:23) clears his return to Amenhotep II. "
              "Some early-date readers go further and identify the princess who drew him out with Hatshepsut, "
              "the great female pharaoh of that court — a striking fit, though an identification the text does "
              "not make and this entry offers only as a possibility. What is not speculative is the shape: an "
              "Egyptian name, an Egyptian upbringing, and a Hebrew heart — the man at home nowhere (he names "
              "his own son 'a resident alien in a foreign land,' 2:22) whom God makes the way home.",
         refs=[("Exodus", 2, 2), ("Exodus", 2, 10), ("Exodus", 2, 11),
               ("Leviticus", 1, 1), ("Numbers", 1, 1)], videos=[]),
    dict(slug="aaron", name="Aaron", kind="person", aliases=["Aaron", "Aaron's sons"],
         desc="Moses's older brother (by three years, Exodus 7:7), the first HIGH PRIEST of Israel and head "
              "of the priestly line — the Levite family through whom all legitimate sacrifice would run. In "
              "Exodus he is Moses's mouthpiece before Pharaoh ('he shall be your spokesman,' Exodus 4:16), his "
              "arms held up over the battle with Amalek, and the maker of the golden calf — the one grave "
              "failure the text never hides. In Leviticus he comes into his office: 'Aaron's sons, the priests' "
              "are the ones who dash the blood and tend the altar-fire in the very first chapter (1:5, 7, 8, 11), "
              "and chapters 8–10 ordain him and his sons, then strike two of them (Nadab and Abihu) dead for "
              "'strange fire.' He dies on Mount Hor (Numbers 20:28); his priesthood passes to his son Eleazar "
              "and endures as the Aaronic (or Levitical) priesthood, the office the letter to the Hebrews "
              "measures against a greater priest 'after the order of Melchizedek.'",
         refs=[("Leviticus", 1, 5), ("Leviticus", 1, 7), ("Leviticus", 1, 11),
               ("Numbers", 1, 3), ("Numbers", 1, 17), ("Numbers", 1, 44)], videos=[]),
    dict(slug="nahshon", name="Nahshon", kind="person", aliases=["Nahshon"],
         desc="Son of Amminadab, CHIEFTAIN of the tribe of Judah at the wilderness census (Numbers 1:7; "
              "2:3; 7:12) — and one of the most quietly important names in the Bible's genealogies. His "
              "sister Elisheba married Aaron (Exodus 6:23), so he is the high priest's brother-in-law; and "
              "the line runs straight from him to the throne and beyond: Nahshon → Salmon → Boaz (who marries "
              "Ruth) → Obed → Jesse → King DAVID (Ruth 4:20–22), and on to the Messiah in both Gospel "
              "genealogies (Matthew 1:4; Luke 3:32). It is fitting that Judah's chieftain heads the muster and "
              "camps first, on the east, leading the march (Numbers 2:3, 9). Jewish tradition (Midrash, and "
              "the Talmud at Sotah 37a) honors Nahshon as the first Israelite to step into the Red Sea, before "
              "it parted — faith walking in before the water opened.",
         refs=[("Numbers", 1, 7)], videos=[]),
    dict(slug="judah", name="Judah", kind="person",
         aliases=["Judah", "the tribe of Judah"],
         desc="Jacob's fourth son by Leah, and the tribe descended from him — the ROYAL and messianic line. "
              "Born with the cry 'this time I will praise (odeh) Jehovah' (Genesis 29:35), Judah rises over his "
              "brothers: he saves Joseph's life, offers himself as surety for Benjamin, and receives Jacob's "
              "deathbed blessing that 'the scepter shall not depart from Judah' (Genesis 49:10). At the "
              "wilderness census his tribe is the largest of all (74,600 fighting men, Numbers 1:27) and takes "
              "the place of honor: it camps on the east and marches at the head of the army (Numbers 2:3, 9), "
              "led by the chieftain Nahshon. From Judah come David, the kings of Jerusalem, and — the New "
              "Testament announces — 'the Lion of the tribe of Judah' (Revelation 5:5); the very word 'Jew' is "
              "worn down from the name Judah.",
         refs=[(29, 35), ("Numbers", 1, 7), ("Numbers", 1, 26)], videos=[]),
    dict(slug="mount-sinai", name="Mount Sinai",
         kind="place", aliases=["Sinai", "wilderness of Sinai", "Mount Sinai", "Horeb"],
         desc="The mountain in the wilderness where Jehovah gave Israel the Law — also called HOREB. Here "
              "Moses met the burning bush (Exodus 3), here the nation heard the Ten Words amid thunder and "
              "gained the covenant (Exodus 19–24), here the tabernacle was built, and from the surrounding "
              "'wilderness of Sinai' the books of Leviticus and Numbers are spoken. Israel encamps at Sinai "
              "for about a year — from the third month after the Exodus (Exodus 19:1) until the cloud lifts on "
              "the twentieth day of the second month of the second year (Numbers 10:11). Its exact location is "
              "uncertain: the ancient and traditional site is Jebel Musa ('the Mountain of Moses') in the "
              "granite peaks of the southern Sinai peninsula, where Saint Catherine's Monastery has stood "
              "since the 6th century; other proposals place it elsewhere in the peninsula, in the Negev, or in "
              "northwest Arabia (a Jabal al-Lawz / Midian theory). This library follows the traditional "
              "identification while noting the debate.",
         coords=(28.539, 33.973, 3.0), approx=True,
         refs=[("Numbers", 1, 1), ("Numbers", 1, 19)], videos=[]),
    dict(slug="tabernacle", name="The Tabernacle",
         kind="place", aliases=["tent of meeting", "Tent of Meeting"],
         desc="The portable sanctuary Israel built at Sinai and carried through the wilderness — a curtained "
              "tent within a courtyard, God's dwelling in the midst of the camp. Hebrew has two names for it: "
              "the MISHKAN, 'dwelling-place' (from shakhan, 'to dwell'), and the OHEL MO'ED, the 'tent of "
              "MEETING' — mo'ed being the 'appointed time/place,' the same word hung on the lights of Genesis "
              "1:14 (see the dictionary). It is the appointed place of appointed meeting: 'there I will meet "
              "with you and speak with you' (Exodus 25:22). Exodus 25–40 gives its blueprint and building; it is "
              "finished and filled with the glory-cloud on the first day of the second year (Exodus 40:17, 34). "
              "Leviticus is then spoken entirely FROM it — 'Jehovah called to Moses and spoke to him from the "
              "tent of meeting' (1:1) — the offerings all brought 'to the door of the tent of meeting' (1:3). "
              "Its inmost room, the Holy of Holies, housed the ark and its atonement-cover (kapporet); the "
              "later Jerusalem Temple made its pattern permanent in stone.",
         refs=[("Leviticus", 1, 1), ("Leviticus", 1, 3), ("Leviticus", 1, 5)], videos=[]),
    dict(slug="midian", name="Midian", kind="place", aliases=["Midian"],
         desc="The land Moses flees to and shepherds in for forty years (Exodus 2:15) — home of the "
              "MIDIANITES, a people descended from Abraham through Keturah (Genesis 25:2), so distant kin to "
              "Israel. Their territory lay in northwest Arabia, east of the Gulf of Aqaba, spreading north "
              "into the Transjordan and the Sinai's edges — caravan-traders (it was Midianite/Ishmaelite "
              "traders who bought Joseph, Genesis 37:28). Here Moses marries into the household of the priest "
              "of Midian and, at Horeb/Sinai 'the mountain of God' at the desert's far side (Exodus 3:1), "
              "meets Jehovah in the burning bush. Later the relationship sours — Midian joins Moab to hire "
              "Balaam (Numbers 22–25) — but at the exodus it is Midian that shelters the deliverer and gives "
              "him a wife and a wise father-in-law.",
         refs=[(25, 2), (25, 4), ("Exodus", 2, 15), ("Exodus", 2, 16)],
         coords=(28.4, 35.3, 1.6), approx=True,
         modern="Northwest Arabia, east of the Gulf of Aqaba (Saudi Arabia), reaching into the Sinai/Transjordan"),
    dict(slug="jethro", name="Jethro (Reuel)", kind="person", aliases=["Reuel", "Jethro"],
         desc="The priest of Midian, Moses' father-in-law, who gives him his daughter Zipporah (Exodus "
              "2:16-21). He is named REUEL here ('friend of God,' 2:18) and JETHRO in the following chapters "
              "(3:1; 18) — the standing puzzle of two names. The oldest solutions still hold: Reuel is the "
              "personal name and Jethro (Yitro, from yeter, 'abundance, excellence') a title or honorific "
              "('his excellency'); or Reuel is the clan-grandfather and Jethro the working head of the house. "
              "(A third name, Hobab, appears too, Numbers 10:29 / Judges 4:11, sometimes read as Reuel's son "
              "and Moses' brother-in-law.) In Exodus 18 Jethro returns to Moses at Sinai, offers sacrifice to "
              "Jehovah — 'Now I know that Jehovah is greater than all gods' — and gives Moses the shrewd "
              "counsel to appoint judges and delegate, the Bible's first management lesson. A Midianite priest "
              "who worships Israel's God: one of scripture's quiet witnesses that the knowledge of the true "
              "God was not sealed inside Israel alone.",
         refs=[("Exodus", 2, 16), ("Exodus", 2, 18), ("Exodus", 2, 21), ("Exodus", 3, 1)], videos=[]),
    dict(slug="zipporah", name="Zipporah", kind="person", aliases=["Zipporah"],
         desc="'Bird' (tsippor, a small bird) — a daughter of the priest of Midian, given to Moses as his "
              "wife (Exodus 2:21), mother of his sons Gershom and Eliezer. She reappears in one of the "
              "strangest, starkest scenes in the Torah: on the road back to Egypt, when Jehovah 'sought to "
              "kill' Moses (over the uncircumcised son), it is Zipporah who acts — she takes a flint, "
              "circumcises the boy, touches Moses' feet with the foreskin and calls him 'a bridegroom of "
              "blood to me,' and the danger passes (Exodus 4:24-26). A Midianite woman performs the covenant "
              "sign that saves the covenant mediator's life. (Numbers 12 records Miriam and Aaron murmuring "
              "against Moses over his 'Cushite wife' — whether Zipporah or another is debated.)",
         refs=[("Exodus", 2, 21), ("Exodus", 2, 22)], videos=[]),
    dict(slug="horeb", name="Horeb (Mount Sinai)", kind="place", aliases=["Horeb"],
         desc="'The mountain of God' (Exodus 3:1), where the bush burns, where Moses is called, and where — "
              "one book later — Israel will camp for a year and receive the Law in fire and cloud. HOREB and "
              "SINAI are the same mountain under two names (Exodus tends to 'Sinai,' Deuteronomy to 'Horeb'); "
              "the exact peak is unknown. The traditional site since Byzantine times is JEBEL MUSA ('the "
              "mountain of Moses') in the south-central Sinai Peninsula, at whose foot St. Catherine's "
              "Monastery guards a thornbush said to be the descendant of the seneh. Other proposals have been "
              "argued — a northern Sinai peak, or JEBEL AL-LAWZ in northwest Arabia (favored by those who "
              "place Midian, where Moses was shepherding, across the Gulf of Aqaba, and read Galatians 4:25's "
              "'Sinai in Arabia' literally) — none decisive. What the text fixes is not the coordinates but "
              "the pattern: the God who meets Moses here in fire brings the whole nation back to the same "
              "fire (Exodus 19), and the sign given at the bush is the meeting itself — 'you will serve God "
              "on this mountain' (3:12).",
         refs=[("Exodus", 3, 1), ("Exodus", 3, 12)],
         coords=(28.5392, 33.9750, 0.5), approx=True,
         modern="Traditionally Jebel Musa, St. Catherine, south-central Sinai Peninsula, Egypt (disputed)",
         videos=[]),

    # ---- Genesis 23 ----
    dict(slug="machpelah", name="Machpelah", kind="place", aliases=["Machpelah"],
         desc="'The double' (from kaphal, 'to fold, to double') — the cave at the edge of Ephron the "
              "Hittite's field, facing Mamre at Hebron, that Abraham bought for 400 shekels of silver to "
              "bury Sarah (Genesis 23). It is the FIRST legally-held parcel of the Promised Land — the man "
              "promised the whole land owns, in his lifetime, one field with a grave in it. It becomes the "
              "patriarchal tomb: Abraham himself (25:9), Isaac and Rebekah, and Jacob and Leah (49:31; "
              "50:13) are all laid here — the one place in Canaan that indisputably belonged to the "
              "patriarchs, its purchase witnessed at the city gate and recorded tree by tree. The massive "
              "stone enclosure Herod the Great built over the cave still stands at Hebron (the Cave of the "
              "Patriarchs / al-Haram al-Ibrahimi) — among the oldest continuously-venerated sites on earth, "
              "and sacred to Jews, Christians, and Muslims alike.",
         refs=[(23, 9), (23, 17), (23, 19), (25, 9)],
         coords=(31.5247, 35.1108, 0.05),
         modern="The Cave of the Patriarchs (Tomb of the Patriarchs / al-Haram al-Ibrahimi), Hebron",
         videos=[]),

    # ---- Genesis 22 ----
    dict(slug="moriah", name="Moriah", kind="place", aliases=["Moriah"],
         desc="'The land of Moriah,' where Abraham was sent to bind Isaac (22:2) — and one of the most "
              "consequential place-names in scripture, because the word appears in only TWO verses in the "
              "whole Hebrew Bible. The other is 2 Chronicles 3:1: 'Solomon began to build the house of "
              "Jehovah in Jerusalem, on MOUNT MORIAH, where Jehovah had appeared to David his father, at the "
              "place David had prepared, on the threshing floor of Ornan the Jebusite.' So the Bible itself "
              "sets the altar of the Aqedah on the future Temple Mount. The chain runs: Abraham's altar "
              "(Genesis 22) → the threshing floor of Araunah/Ornan the Jebusite, bought by David for an "
              "altar after the plague (2 Samuel 24; 1 Chronicles 21) → Solomon's Temple, c. 966 BC (2 "
              "Chronicles 3:1) → the Second Temple → the platform standing today. Abraham's own name for the "
              "spot, Jehovah-Yireh ('on the mount of Jehovah it is seen to,' 22:14), reads across the "
              "centuries as a saying about this one hill. "
              "A note on the NAME of the city: at the Aqedah the place is not yet 'Jerusalem.' The nearby "
              "town is Salem, whose king Melchizedek Abraham had already met (14:18; Psalm 76:2 sets God's "
              "dwelling 'in Salem'); the Jebusites called their city Jebus (Judges 19:10); and the name "
              "Jerusalem itself (Urusalim) surfaces in the Amarna letters of about 1400 BC, after the "
              "patriarchs. Moriah was a bare height NORTH of the walled Jebusite city — which is why a "
              "threshing floor stood there, out in the wind above the town — and it was only drawn INTO "
              "Jerusalem when David and Solomon expanded the city northward to build the Temple. So the hill "
              "of Genesis 22 became the heart of Jerusalem before it wore that name. "
              "Honest caveats: the identification with the Temple Mount rests on the Chronicler (2 "
              "Chronicles 3:1) and Jewish tradition — a biblical-internal link, made explicit only "
              "centuries later; and the Samaritan tradition instead locates the binding at Mount Gerizim "
              "(their Pentateuch reads the name differently). The etymology of 'Moriah' is itself uncertain — "
              "the chapter plays it as 'seeing' (ra'ah), but 'place of teaching' (yarah) and 'myrrh' (mor) "
              "have all been proposed.",
         refs=[(22, 2), (22, 14)],
         coords=(31.7780, 35.2354, 0.06),
         modern="The Temple Mount / Haram al-Sharif, Old City of Jerusalem",
         videos=[("The Temple Mount — Where it IS. Where it ISN'T. What is it FOR?",
                  "https://www.youtube.com/watch?v=IrqRoLxa178")]),
    dict(slug="rebekah", name="Rebekah", kind="person", aliases=["Rebekah"],
         desc="Isaac's future wife — named, almost in passing, in the genealogical coda to the Aqedah: "
              "'Bethuel fathered Rebekah' (22:23), the last of the eight sons and one granddaughter Milcah "
              "bore to Abraham's brother Nahor, back in the old country. The chapter that nearly ended the "
              "line of promise closes by quietly naming the woman who will carry it on — two chapters before "
              "Isaac meets her. When the servant is sent to find her (ch. 24), she is the decisive one: 'I "
              "will go' (24:58); at the well she waters ten camels unasked. She bears the twins Esau and "
              "Jacob, receives the oracle that 'the elder shall serve the younger' (25:23), and engineers "
              "the blessing to Jacob (ch. 27) — the matriarch who reads the promise better than her husband.",
         refs=[(22, 23), (24, 15), (24, 58), (24, 67), (27, 5), (27, 42), (27, 46)], videos=[]),

    # ---- Genesis 24 ----
    dict(slug="laban", name="Laban", kind="person", aliases=["Laban"],
         desc="Rebekah's brother — and the narrator introduces his character in a single sly stroke: Laban 'ran "
              "out to the man, to the spring' (24:29) — but the very next verse tells us WHEN: 'when he saw the "
              "nose-ring, and the bracelets on his sister's hands' (24:30). The hospitality has an eye on the gold. "
              "He calls the stranger 'blessed of Jehovah' and clears the house, and with his father Bethuel gives "
              "Rebekah up graciously enough ('the thing is from Jehovah'). But the man glimpsed here is the same "
              "LABAN THE ARAMEAN who, a generation later, will take in the fleeing Jacob, swap Leah for Rachel on "
              "the wedding night, cheat his wages ten times over, and chase him down over stolen household idols "
              "(Genesis 29–31) — the grasping uncle whose greed the gold at the well already forecasts.",
         refs=[(24, 29), (24, 50), (27, 43), (28, 2), (28, 5), (29, 5), (29, 13), (29, 25), (30, 27)], videos=[]),
    dict(slug="leah", name="Leah", kind="person", aliases=["Leah"],
         desc="Laban's elder daughter, and the unloved wife — married to Jacob by her father's night-time trick "
              "in place of Rachel, the sister Jacob actually loved (29:23-25). The narrator marks her from the "
              "start with the ambiguous 'weak / tender eyes' (rakkot), set against Rachel's beauty; and God marks "
              "her with a tenderness of his own: 'Jehovah saw that Leah was HATED, and opened her womb' (29:31). "
              "She becomes the great mother of Israel — six of the twelve tribes are hers, and each son's name is "
              "a small cry of her longing to be loved (Reuben, Simeon, Levi, Judah…). The unloved wife bears the "
              "two most consequential sons of all: LEVI, father of the priesthood, and JUDAH, father of the kings "
              "and of the Messiah. She is buried beside Jacob at Machpelah (49:31) — not the wife he chose, but "
              "the wife in the ancestral tomb.",
         refs=[(29, 16), (29, 23), (29, 31), (30, 9)], videos=[]),
    dict(slug="rachel", name="Rachel", kind="person", aliases=["Rachel"],
         desc="Laban's younger daughter and the love of Jacob's life — a shepherdess he meets at the well and "
              "serves fourteen years to marry (29:9-30). 'Beautiful in form and lovely to look at,' and beloved, "
              "but for years barren while her unloved sister bears son after son; the ache turns to bitter rivalry "
              "('give me children, or I die,' 30:1). At last God 'remembers' her and she bears JOSEPH, and then "
              "dies giving birth to BENJAMIN on the road near Bethlehem, naming him with her last breath "
              "Ben-oni, 'son of my sorrow' (35:16-20). Her lonely wayside tomb becomes a landmark, and the "
              "prophet hears her still weeping there for her exiled children — 'Rachel weeping for her children, "
              "refusing to be comforted' (Jeremiah 31:15), the verse Matthew hears again over Bethlehem's "
              "murdered infants (Matthew 2:18).",
         refs=[(29, 6), (29, 18), (29, 30), (30, 1)], videos=[]),
    dict(slug="bethuel", name="Bethuel", kind="person", aliases=["Bethuel"],
         desc="Rebekah's father — son of Nahor (Abraham's brother) and Milcah (24:15, 24, 47), so Isaac's bride is "
              "the granddaughter of Abraham's own brother, kept inside the family the oath required. He is a "
              "curiously faint figure: at the decisive moment it is 'LABAN and Bethuel' who answer — the son named "
              "before the father (24:50) — and after that Bethuel vanishes from the scene while Laban and the "
              "mother do the negotiating. The order has fed old readings that Bethuel was aged, or that Laban had "
              "already taken the household in hand; the text simply lets the son speak first and moves on.",
         refs=[(24, 24), (24, 50)], videos=[]),
    dict(slug="aram-naharaim", name="Aram-naharaim (Paddan-aram)", kind="place", aliases=["Aram-naharaim", "Paddan-aram"],
         desc="'Aram of the Two Rivers' — upper Mesopotamia, the region around Haran where Abraham's kindred "
              "stayed when he went on to Canaan (24:10, 'the city of Nahor'). It is the ancestral homeland the "
              "family keeps returning to: Abraham came out of it by call, the servant goes back to it for Isaac's "
              "bride, and Jacob flees to it to find his own wives among Laban's daughters (28:2-7). Genesis's own "
              "name for its heartland is PADDAN-ARAM ('the field/plain of Aram'), the Haran district of the far "
              "upper Euphrates — where Jacob will spend twenty years; the 'two rivers' are the Euphrates and "
              "either the Tigris or the Habur.",
         refs=[(24, 10), (28, 2), (28, 5)],
         coords=(36.86, 39.03, 1.2), approx=True,
         modern="Upper Mesopotamia around Harran, southeastern Turkey / northern Syria"),

    # ---- Genesis 25 ----
    dict(slug="keturah", name="Keturah", kind="person", aliases=["Keturah"],
         desc="The wife Abraham takes after Sarah's death (25:1; called a 'concubine' at 1 Chronicles 1:32) — "
              "mother of six sons who become the peoples of the Arabian desert and the eastern trade routes: "
              "Zimran, Jokshan, Medan, MIDIAN, Ishbak, and Shuah, with grandsons Sheba and Dedan. Chief among them "
              "is Midian — so the Midianites who buy Joseph, and among whom Moses later shepherds and marries (see "
              "Midian), descend from Abraham himself. Abraham gives everything to Isaac and sends Keturah's sons "
              "'eastward, to the land of the east' with gifts (25:6): the promise is not divided, but the "
              "old man's line still fans out into a dozen nations, as he was told it would.",
         refs=[(25, 1), (25, 4)], videos=[]),
    dict(slug="esau", name="Esau (Edom)", kind="person", aliases=["Esau"],
         desc="Isaac and Rebekah's firstborn twin — born 'ruddy (admoni), all over like a hairy mantle,' so they "
              "called him ESAU; and because he traded his birthright for a bowl of RED (adom) stew, he earned the "
              "second name EDOM (25:25, 30). A man of the open field, a hunter, his father's favorite for the game "
              "he brought home — and the one who 'despised his birthright' (25:34), selling the eternal for a "
              "single meal, which is why the New Testament makes him the type of the 'profane' person (Hebrews "
              "12:16). Jacob will later cheat him of the blessing too (ch. 27), and Esau's murderous grief drives "
              "Jacob into exile; yet at their reunion Esau runs to embrace him and weeps (ch. 33), the wronged "
              "brother more gracious than the schemer. He is the father of EDOM, Israel's perennial neighbor and "
              "rival to the south.",
         refs=[(25, 25), (25, 30), (25, 34), (26, 34), (27, 34), (27, 41), (28, 6)], videos=[]),
    dict(slug="jacob", name="Jacob (Israel)", kind="person", aliases=["Jacob"],
         desc="The third patriarch, and the one the nation is named for — born gripping his twin's HEEL (aqev), so "
              "called YA'AQOV, 'heel-holder,' a name that becomes a byword for the supplanter who trips and "
              "overreaches (25:26; 27:36). He buys Esau's birthright for stew, steals Esau's blessing with his "
              "mother's help, and flees to Laban in the old country — where he is out-tricked in turn (Leah for "
              "Rachel) and fathers eleven sons and a daughter over twenty hard years. Wrestling a stranger at the "
              "Jabbok, he is renamed ISRAEL, 'he strives with God' (32:28); his twelve sons become the twelve "
              "tribes. A flawed, grasping, unforgettable man whom God chooses anyway — 'the God of Abraham, Isaac, "
              "and Jacob' — and whose story fills the rest of Genesis (chs. 25–50).",
         refs=[(25, 26), (25, 27), (25, 31), (27, 19), (27, 36), (28, 10), (28, 16), (29, 10), (29, 25), (30, 1)], videos=[]),
    dict(slug="edom", name="Edom (Seir)", kind="place", aliases=["Edom"],
         desc="The nation and land descended from ESAU — the rugged red-sandstone highlands south-east of the Dead "
              "Sea, also called SEIR ('hairy,' echoing Esau). The name Edom ('red') is minted in this chapter from "
              "the red stew (25:30) and matches the red Nubian sandstone of the region (whose later capital, Petra, "
              "is carved into it). Edom and Israel are the archetypal quarreling brothers of the Bible: kin, yet "
              "perennial enemies — Edom refuses Israel passage in the wilderness (Numbers 20), and the prophets "
              "return to it again and again (Obadiah is entirely an oracle against Edom; Jeremiah 49; Isaiah 34). "
              "Herod the Great was an Idumean — a Hellenized Edomite — so the brother-rivalry runs right up to the "
              "Gospels.",
         refs=[(25, 30)],
         coords=(30.32, 35.44, 0.9), approx=True,
         modern="The highlands of southern Jordan (Seir), south-east of the Dead Sea"),

    # ---- Genesis 21 ----
    dict(slug="beersheba", name="Beersheba", kind="place", aliases=["Beersheba"],
         desc="'Well of the seven / well of the oath' — the double-named well where Abraham and Abimelech "
              "swore over seven ewe-lambs (21:28-31; Hebrew 'to swear,' nishba, is literally 'to seven "
              "oneself,' so the two readings are one word). Abraham plants a tamarisk here and calls on El "
              "Olam, the Everlasting God (21:33); Isaac and Jacob will both anchor here after him, and 'from "
              "Dan to Beersheba' becomes the Bible's own phrase for the whole land, north to south. The "
              "excavated tell (Tel Be'er Sheva) preserves an Iron-Age planned town with a monumental well at "
              "its gate — a city built around exactly the asset this chapter litigates.",
         refs=[(21, 14), (21, 31), (21, 33), (26, 23), (26, 33)],
         coords=(31.2448, 34.8410, 0.08),
         modern="Tel Be'er Sheva, east of modern Beersheba, Israel",
         videos=[]),

    # ---- Jeremiah 20 ----
    # (gen21 ref-extensions handled inline on the existing hagar/isaac/abimelech entries below)
    dict(slug="jeremiah-person", name="Jeremiah", kind="person", aliases=["Jeremiah"],
         desc="A priest's son from Anathoth, drafted as a boy over his own objection ('before I formed you in "
              "the womb, I knew you… I am only a youth,' ch. 1) — and made to say, for some forty years under "
              "Judah's last kings, exactly what Jerusalem least wanted said: the city would fall, and Babylon "
              "was the instrument. The cost is on the record like no other prophet's: beaten and locked in the "
              "stocks (20:2), his scroll burned column by column in the king's brazier (ch. 36, redictated to "
              "Baruch, longer), dropped into a mud cistern (ch. 38), and at last dragged to Egypt by the "
              "refugees he warned. The book preserves his 'confessions' — private arguments with God (chs. "
              "11–20), of which chapter 20 ('You enticed me… fire shut up in my bones… cursed be the day I was "
              "born') is the last and rawest. Tradition, weeping over Jerusalem, gave him Lamentations too.",
         refs=[("Jeremiah", 20, 1), ("Jeremiah", 20, 3), ("Jeremiah", 20, 9)], videos=[]),
    dict(slug="pashhur", name="Pashhur son of Immer", kind="person", aliases=["Pashhur"],
         desc="Priest and paqid nagid — 'chief overseer in the house of Jehovah,' head of temple order — who "
              "answered the sermon over the Hinnom valley by striking Jeremiah and locking him overnight in "
              "the stocks (20:1-2): the first recorded violence against the prophet, administered by the "
              "temple's own police. He came back the next morning to a new name — Magor-Missaviv, "
              "Terror-All-Around — and a measured sentence: exile, death, and burial in Babylon, 'you, and all "
              "who love you, to whom you have prophesied falsehood' (20:6) — the chief of order was also a "
              "comfortable false prophet. (A different Pashhur — and a 'Gedaliah son of Pashhur' — appear among "
              "Jeremiah's enemies in 38:1; clay seal-impressions bearing that Gedaliah's name and his colleague "
              "'Jehucal son of Shelemiah' were excavated a few meters apart in the City of David, sealed in the "
              "ash of the destruction Jeremiah foretold.)",
         refs=[("Jeremiah", 20, 1), ("Jeremiah", 20, 3), ("Jeremiah", 20, 6)], videos=[]),
    dict(slug="babylon", name="Babylon", kind="place", aliases=["Babylon"],
         desc="Bab-ili, 'gate of the god' — the city on the Euphrates that gave the world Hammurabi's laws, "
              "and under Nebuchadnezzar II the Ishtar Gate, the ziggurat Etemenanki (standing behind the "
              "Bible's memory of Babel's tower — see Shinar), and the empire that ended Judah. In Jeremiah's "
              "preaching the doom long comes from an unnamed 'north'; at 20:4-6 the name is finally said out "
              "loud — Babylon, five times in three verses — and Daniel's first page records the fulfillment "
              "begun (605 BC). The city fell to Cyrus in 539 BC (the Nabonidus Chronicle and Cyrus Cylinder "
              "carry the receipt), and Revelation will pick the name up again as the world-city's cipher "
              "(chs. 17–18).",
         refs=[("Jeremiah", 20, 4), ("Daniel", 1, 1)],
         coords=(32.5364, 44.4209, 0.5),
         modern="Tell Babil, near Hillah, Babil Governorate, Iraq",
         videos=[("Search for the Tower of Babel", "https://www.youtube.com/watch?v=cYc_VgjJfw8"),
                 ("Exploring Babylon and the Prophecies Against Her", "https://www.youtube.com/watch?v=QtUNHjDmGOY")]),

    # ---- Jeremiah 21 ----
    dict(slug="zedekiah", name="Zedekiah", kind="person", aliases=["Zedekiah"],
         desc="Judah's last king — born Mattaniah, installed and renamed by Nebuchadnezzar himself after the "
              "597 deportation (2 Kings 24:17): a vassal wearing a throne-name his conqueror chose. Twenty-one "
              "when crowned, chronically unable to choose between his officials and his conscience — he sends "
              "delegations to Jeremiah (21:1; 37:3), consults him in secret (37:17; 38:14-16), lets the "
              "officials drop him in the cistern, then lets Ebed-melech pull him out. The rebellion the "
              "prophet begged him not to make brought the final siege (588–586). His end at Riblah is the "
              "book's darkest sentence: his sons killed before his eyes, then his eyes put out — the last "
              "thing he ever saw (39:6-7).",
         refs=[("Jeremiah", 21, 1), ("Jeremiah", 21, 7)], videos=[]),
    dict(slug="pashhur-malchiah", name="Pashhur son of Malchiah", kind="person", aliases=["Pashhur"],
         desc="NOT the Pashhur of the stocks (that was the son of Immer, ch. 20) — a second official of the "
              "same name, sent by Zedekiah during the final siege to ask Jeremiah for a miracle (21:1). The "
              "book's editors filed the two Pashhur scenes side by side, seventeen years apart — the scroll's "
              "own catchword filing system. This Pashhur has a future: he stands among the officials who have "
              "Jeremiah thrown into the cistern as a defeatist (38:1-6) — in the very verse where a 'Gedaliah "
              "son of Pashhur' also appears, whose clay seal-impression was excavated in the City of David's "
              "destruction ash.",
         refs=[("Jeremiah", 21, 1)], videos=[]),

    # ---- Jeremiah 22 ----
    dict(slug="josiah", name="Josiah", kind="person", aliases=["Josiah"],
         desc="The last good king of Judah (reigned c. 640–609 BC) — crowned at eight, who purged the idols and, "
              "when the lost scroll of the Law was found in the temple during his repairs (2 Kings 22), tore his "
              "robes and led the deepest reform in Judah's history. Jeremiah's ministry began in his thirteenth "
              "year (Jeremiah 1:2), and it is Josiah the prophet holds up in this chapter as the yardstick for his "
              "own sons: 'Your father — did he not eat and drink, AND do justice and righteousness? … He judged the "
              "cause of the poor and needy … Is that not to know me?' (22:15-16). His death was the hinge of the "
              "age: he rode out to stop Pharaoh Necho at Megiddo and was killed (609 BC), and within a generation "
              "everything he had built came down. He is the 'dead' of 22:10, mourned — while his sons are the ones "
              "to weep over.",
         refs=[("Jeremiah", 22, 15), ("Jeremiah", 22, 16)], videos=[]),
    dict(slug="shallum-jehoahaz", name="Shallum (Jehoahaz)", kind="person", aliases=["Shallum", "Jehoahaz"],
         desc="Josiah's son, the first of his heirs to fall — known by his personal name SHALLUM (22:11) and his "
              "throne-name JEHOAHAZ. The people made him king after Josiah died at Megiddo, but he reigned only "
              "three months: Pharaoh Necho, returning south, deposed him, fined the land, and carried him to Egypt "
              "in chains, setting his brother Jehoiakim on the throne instead (2 Kings 23:31-34). Jeremiah's word "
              "over him is the chapter's opening dirge — 'weep not for the dead, weep for the one who goes away, "
              "for he will return no more, nor see the land of his birth' (22:10-12). He died in Egypt, the first "
              "Davidic king to end his days a foreign prisoner, and the pattern for the two who would follow.",
         refs=[("Jeremiah", 22, 11)], videos=[]),
    dict(slug="jehoiakim", name="Jehoiakim", kind="person", aliases=["Jehoiakim"],
         desc="Josiah's son Eliakim, renamed JEHOIAKIM by Pharaoh Necho, who put him on the throne after deposing "
              "his brother Jehoahaz (2 Kings 23:34) — an Egyptian puppet who became a Babylonian vassal after "
              "Carchemish (605), then rebelled. Jeremiah's woe against him (22:13-19) is scorching: he built a "
              "cedar-and-vermilion palace with UNPAID labor, 'his eyes and heart on nothing but dishonest gain.' "
              "He is the king who, in one of the Bible's most vivid scenes, sat by his brazier and personally "
              "sliced Jeremiah's dictated scroll column by column into the fire (Jeremiah 36:23) — so his sentence "
              "is the anti-funeral: no mourner's 'Alas!', 'the burial of a donkey, dragged and flung beyond the "
              "gates.' (Kings and Chronicles are quieter about his actual death; the oracle stands as the verdict "
              "pronounced.) His eleven-year reign spent Judah's last chance.",
         refs=[("Jeremiah", 22, 18), ("Jeremiah", 22, 13)], videos=[]),
    dict(slug="jehoiachin", name="Jehoiachin (Coniah / Jeconiah)", kind="person", aliases=["Coniah", "Jehoiachin", "Jeconiah"],
         desc="Jehoiakim's son, three names for one doomed boy-king: JEHOIACHIN (his full name), JECONIAH, and the "
              "clipped, almost contemptuous CONIAH that Jeremiah uses here (22:24, 28). Eighteen years old, three "
              "months on the throne, when Nebuchadnezzar took Jerusalem in the first great deportation (597 BC) "
              "and carried him to Babylon with the treasures and the craftsmen and ten thousand captives — the "
              "exile Ezekiel and the young Daniel's world. Jeremiah's oracle strips him of authority in one image: "
              "even were he 'a signet on my right hand, yet from there I would tear you off,' and 'write this man "
              "childless.' Yet the curse is throne-deep, not blood-deep: he fathered seven sons in exile (1 "
              "Chronicles 3:17), was released from prison and given a seat at the Babylonian king's table thirty-"
              "seven years later (2 Kings 25:27-30) — a mercy corroborated by the excavated BABYLON RATION "
              "TABLETS, which list oil and grain for 'Ya'u-kinu, king of Judah' and his sons by name. His grandson "
              "Zerubbabel is handed the signet back (Haggai 2:23), and both Gospel genealogies of the Messiah pass "
              "through his line — the king 'written childless' as to David's old throne became an ancestor of the "
              "one who inherits a greater one.",
         refs=[("Jeremiah", 22, 24), ("Jeremiah", 22, 28)], videos=[]),

    # ---- Daniel 12 ----
    dict(slug="michael-archangel", name="Michael (the great prince)", kind="person", aliases=["Michael"],
         desc="'Who is like God?' — an angel named after a rhetorical question, mi-kha-El, whose answer is NO "
              "ONE. In Daniel's vision-frame he is 'one of the chief princes' who fights the unseen 'princes' of "
              "Persia and Greece (10:13, 21), and at the end 'the great prince who stands over the sons of your "
              "people' (12:1) — Israel's assigned guardian-advocate, standing up as the time of distress opens. "
              "One of only two angels the Bible names (Gabriel is the other). The New Testament gives him two "
              "more scenes: 'Michael the archangel' disputing over the body of Moses (Jude 9), and the war in "
              "heaven — 'Michael and his angels fought against the dragon' (Revelation 12:7).",
         refs=[("Daniel", 12, 1)], videos=[]),

    # ---- Revelation 1 ----
    dict(slug="john-of-patmos", name="John (of Revelation)", kind="person", aliases=["John"],
         desc="The seer of Revelation names himself only 'John — your brother, and companion in the affliction' "
              "(1:9). Tradition from the second century (Justin Martyr, Irenaeus) identifies him with the apostle, "
              "son of Zebedee, author of the Gospel; but the question is ancient — Dionysius of Alexandria "
              "(3rd century) already argued from style that the Gospel's smooth Greek and Revelation's wild, "
              "Hebrew-boned Greek cannot come from one hand, and proposed a second John, 'John of Patmos.' The "
              "book claims only the name; the church kept it either way. Reported, not settled.",
         refs=[("Revelation", 1, 1), ("Revelation", 1, 4), ("Revelation", 1, 9)], videos=[]),
    dict(slug="patmos", name="Patmos", kind="place",
         desc="A small rocky island of the Dodecanese, off the coast of Asia Minor — some 60 km from Miletus. "
              "Rome used such islands for banishment, and John 'came to be' here 'because of the word of God and "
              "the testimony of Jesus' (1:9) — exile for preaching, on the natural reading. Here, 'in the Spirit "
              "on the Lord's day,' he saw the vision; the island's Cave of the Apocalypse has been shown to "
              "pilgrims as the spot since Byzantine times.",
         refs=[("Revelation", 1, 9)],
         coords=(37.309, 26.547, 0.08),
         modern="Patmos, Dodecanese, Greece", videos=[]),
    dict(slug="seven-churches", name="The Seven Churches of Asia", kind="place",
         aliases=["seven churches", "seven congregations"],
         desc="Ephesus, Smyrna, Pergamum, Thyatira, Sardis, Philadelphia, Laodicea (1:11) — seven congregations "
              "of the Roman province of Asia (western Asia Minor), listed in exact courier's order: up the coast, "
              "then inland and south. Revelation is a circular letter, and the list is its postal route. (This "
              "entry keeps the traditional catalogue label 'Seven Churches'; the translation itself reads "
              "'congregation' for ekklēsia — see the dictionary entry for the word, and for King James's rule "
              "that forbade Tyndale's rendering.) The first four letters arrive in chapter 2 (each city now has "
              "its own entry); Sardis, Philadelphia and Laodicea receive theirs in chapter 3.",
         refs=[("Revelation", 1, 4), ("Revelation", 1, 11), ("Revelation", 1, 20)], videos=[]),
    dict(slug="ephesus", name="Ephesus", kind="place", aliases=["Ephesus"],
         desc="The great harbor metropolis of Roman Asia — temple of Artemis (one of the seven wonders), theater "
              "for 25,000, and by tradition the adopted home of John himself. Paul spent three years here (Acts "
              "19-20). First on the courier's route and first of the seven letters (Rev 2:1-7): fullest in praise "
              "— toil, endurance, vigilance against false apostles — and stung by the most famous complaint in "
              "the set: 'you have left your first love.' The ruins at Selçuk are among the grandest of the "
              "ancient Mediterranean.",
         refs=[("Revelation", 1, 11), ("Revelation", 2, 1)],
         coords=(37.9411, 27.3419, 0.08), modern="Efes, near Selçuk, Türkiye", videos=[]),
    dict(slug="smyrna", name="Smyrna", kind="place", aliases=["Smyrna"],
         desc="The beautiful harbor city whose ringed acropolis ancient writers praised as 'the crown of Smyrna' "
              "— apt, for the letter that promises 'the crown of life' (Rev 2:8-11): one of only two of the seven "
              "with no rebuke at all. Rich city, poor congregation, bounded suffering ('ten days'), and the charge kept "
              "to the letter two generations on, when its own bishop Polycarp was martyred in the stadium "
              "(c. AD 155), refusing to recant. Continuously inhabited ever since — modern İzmir.",
         refs=[("Revelation", 1, 11), ("Revelation", 2, 8)],
         coords=(38.4189, 27.1287, 0.1), modern="İzmir, Türkiye", videos=[]),
    dict(slug="pergamum", name="Pergamum", kind="place", aliases=["Pergamum"],
         desc="Old royal capital of Asia, terraced up its mountain — 'where Satan's throne is' (Rev 2:12-17). The "
              "candidates: the Great Altar of Zeus (excavated and carried to Berlin — it stands today in the "
              "Pergamon Museum), the province's first imperial-cult temple, or the serpent-shrine of Asclepius; "
              "perhaps the whole skyline at once. Here Antipas, the book's only named martyr, was killed; here "
              "'Balaam's teaching' — go along with the guild feasts — got its answer: hidden manna, and a white "
              "stone with a new name.",
         refs=[("Revelation", 1, 11), ("Revelation", 2, 12), ("Revelation", 2, 13)],
         coords=(39.1319, 27.1844, 0.1), modern="Bergama, Türkiye", videos=[]),
    dict(slug="thyatira", name="Thyatira", kind="place", aliases=["Thyatira"],
         desc="The smallest and least famous of the seven — an inland workshop town of trade guilds (its one "
              "other New Testament appearance is Lydia, 'a seller of purple from Thyatira,' Acts 16:14) — and it "
              "receives the LONGEST of the seven letters (Rev 2:18-29), from 'the Son of God,' the title's only "
              "occurrence in Revelation. Its crisis was economic: the guild feasts in the gods' honor were where "
              "business happened, and the prophetess the letter code-names Jezebel taught the congregation to go along.",
         refs=[("Revelation", 1, 11), ("Revelation", 2, 18), ("Revelation", 2, 24)],
         coords=(38.9190, 27.8417, 0.1), modern="Akhisar, Türkiye", videos=[]),

    # ---- the divine name ----
    dict(slug="jehovah", name="Jehovah (the divine name)", kind="person", aliases=["Jehovah"],
         desc="The personal name of God — the four Hebrew letters יהוה (YHWH, the Tetragrammaton), which this "
              "translation prints as <strong>Jehovah</strong> wherever the Hebrew has the name. It first appears at "
              "Genesis 2:4 (paired with Elohim, 'God') and occurs some 6,800 times in the Hebrew Bible. Ancient "
              "Jewish practice avoided pronouncing it, saying <em>Adonai</em> ('Lord') in its place, so the Greek "
              "and Latin Bibles and most English versions substitute the title — 'the LORD' in small capitals. "
              "'Jehovah' is the traditional English form (from about the thirteenth century; used throughout the "
              "American Standard Version and by the New World Translation) — a hybrid of the consonants YHWH with "
              "the vowels of <em>Adonai</em>; scholars reconstruct the original pronunciation as 'Yahweh.' The full "
              "discussion, and why this project chose 'Jehovah,' is on the "
              "<a href=\"ask-jehovah.html\">Ask Mr. Librarian page</a>. The Name's own self-explanation is given "
              "at the burning bush — 'ehyeh asher ehyeh,' and then 'YHWH … this is my name forever' (Exodus "
              "3:14-15); see that chapter.",
         refs=[(2, 4), ("Exodus", 3, 15)],
         videos=[("Searching for the earliest mention of the Israelite's God, \"Yahweh.\"",
                  "https://www.youtube.com/watch?v=pGEOZ5YI22M")]),
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
    # ---- Exodus 1 ----
    (("Exodus", 1, 7),  (1, 28), "the creation blessing — 'be fruitful and multiply and fill' — fulfilled at full volume on a slave people; sharats, 'swarm,' is the creation-word"),
    (("Exodus", 1, 13), (15, 13), "the affliction God foretold to Abraham at the covenant of the pieces: 'your seed will be sojourners… and they will afflict them'"),
    (("Exodus", 1, 17), (22, 12), "'the midwives feared God' — the same reverent fear the angel found in Abraham at the altar: 'now I know that you fear God'"),
    (("Exodus", 1, 17), ("Proverbs", 1, 7), "the fear of God — 'the beginning of knowledge' — as the midwives' wisdom: when king and God command opposite, disobey the king"),

    # ---- Exodus 2 ----
    (("Exodus", 2, 3),  (6, 14), "tevah, an 'ark' — the one other thing in scripture called a tevah: Noah's ark. Both are saved through the death-waters in a pitch-sealed ark; the deliverer floats the flood in miniature"),
    (("Exodus", 2, 2),  (1, 4),  "ki tov — 'she saw him, that he was GOOD' — the mother's word over her baby is God's word over the light on the first day, 'and God saw the light, that it was good'"),
    (("Exodus", 2, 22), (23, 4), "ger, a 'resident alien' — Moses names his son Gershom by Abraham's own confession at Machpelah, 'I am a resident alien among you': the patriarch's statelessness handed to the man who will end it"),
    (("Exodus", 2, 24), (17, 7), "God 'remembered his covenant' — not that he had forgotten, but that the everlasting covenant cut with Abraham (17:7) has now come due; zakhar here means to ACT on a promise"),

    # ---- Exodus 3 ----
    (("Exodus", 3, 2),  (16, 7),  "the ANGEL OF JEHOVAH — the same seam met at the Bible's first mal'akh YHWH, Hagar's well: the messenger who so carries the Sender that the account slides from 'the angel' to 'Jehovah' speaking as God himself"),
    (("Exodus", 3, 4),  (22, 11), "the doubled name and 'Here I am' — 'Moses, Moses!' answered with hineni, exactly as 'Abraham, Abraham!' was answered with the knife raised on Moriah"),
    (("Exodus", 3, 7),  ("Exodus", 2, 25), "'I have SEEN … HEARD … KNOW' — the four verbs that closed chapter 2 (God heard, remembered, saw, knew), now spoken in the first person out of the fire"),
    (("Exodus", 3, 12), ("Exodus", 3, 14), "ehyeh, 'I will be' — the presence promised to Moses, 'I WILL BE with you,' is the very word God gives two verses on as his Name, 'I WILL BE WHAT I WILL BE'"),
    (("Exodus", 3, 14), ("Revelation", 1, 8), "'I WILL BE / I AM' — the Greek Bible's 'ho ōn,' the One who is, is the title Revelation hands to Christ: 'him who is and who was and who is coming'"),
    (("Exodus", 3, 16), (21, 1),  "paqod paqadti, 'I have surely attended to you' — the paqad of 'Jehovah visited Sarah' with a son, and dying Joseph's password: 'God will surely visit you'"),
    (("Exodus", 3, 20), ("Jeremiah", 21, 2), "niflaotai, 'my wonders' — the Exodus wonders first promised here; Zedekiah's officials would one day beg Jeremiah to see them repeated, and learn the Wonder-worker had changed sides"),
    (("Exodus", 3, 22), (15, 14), "'you will strip Egypt bare' — the great possessions God foretold to Abram in the dark: 'afterward they will come out with great wealth'"),

    # ---- Genesis 23 ----
    ((23, 4),  (17, 8),  "achuzzah, a 'holding' — the everlasting HOLDING God promised Abraham (all Canaan), and here the one burial holding is all of it he owns in his lifetime"),
    ((23, 17), (13, 18), "Machpelah 'faced Mamre' — the oaks where Abraham first pitched his tent and built an altar now look onto the family tomb"),
    ((23, 6),  (12, 2),  "'a prince of God among us' — the Hittites see the great name God promised to make of Abraham"),
    ((23, 20), (12, 7),  "the land promised 'to your seed' — of which this single witnessed field, bought for a grave, is the first legal parcel"),

    # ---- Genesis 24 ----
    ((24, 58), (12, 1),  "'I will go' — elekh: Rebekah leaves her land and kindred for a land she has never seen, doing of her own will exactly what the call commanded Abraham, 'go, you yourself, from your land and your birthplace'"),
    ((24, 60), (22, 17), "'let your seed possess the gate of those who hate them' — her family's blessing on Rebekah quotes, almost word for word, the oath sworn to Abraham at the Aqedah"),
    ((24, 7),  (15, 18), "'to your seed I will give this land' — Abraham cites the oath of the covenant of the pieces as the guarantee the servant will not fail"),
    ((24, 62), (16, 14), "Isaac settles at Beer-lahai-roi — 'the well of the Living One who sees me,' where the angel had found the outcast Hagar: the heir dwells where the seeing-God met the cast-out"),
    ((24, 67), (23, 19), "'Isaac was comforted after his mother' — Sarah, buried at Machpelah one chapter before, and now her tent holds a bride: the grief of ch. 23 answered"),
    ((24, 12), (19, 19), "chesed — the loyal kindness the servant asks God to show and designs his sign to test, the same covenant-love Lot named when the angels dragged him free of Sodom"),

    # ---- Genesis 25 ----
    ((25, 9),  (23, 19), "Isaac AND Ishmael bury Abraham in the cave of Machpelah — the field he bought for Sarah's grave one generation before; the two sons, one sent away, stand together at their father's tomb"),
    ((25, 17), (17, 20), "Ishmael's twelve princes — the exact promise God made to Abraham for him: 'twelve chieftains he will father, and I will make him a great nation'"),
    ((25, 18), (16, 12), "'over against all his brothers he settled' — the angel's word to Hagar in the desert, 'he will dwell in the face of all his brothers,' now recorded as fact"),
    ((25, 23), (21, 12), "'the elder will serve the younger' — the promise runs through the chosen son, not the firstborn: 'in Isaac your seed will be called,' the reversal Isaac himself embodied, now handed to Jacob"),
    ((25, 26), (3, 15),  "Jacob is born gripping the HEEL (aqev) — the rare word of the first promise, 'you will strike his heel': the name Ya'aqov folds the whole struggle of the seed into a newborn's fist"),
    ((25, 11), (16, 14), "Isaac settles at Beer-lahai-roi — 'the well of the Living One who sees me,' Hagar's well: the son of the promise makes his home where the seeing-God met the cast-out"),

    # ---- Genesis 26 ----
    ((26, 1),  (12, 10), "a famine drives the patriarch south — as it drove Abram toward Egypt (12:10); but Isaac is told 'do not go down to Egypt,' kept in the land his father had to leave"),
    ((26, 4),  (22, 17), "'I will multiply your seed as the stars … and in your seed all the nations will bless themselves' — the Aqedah oath, word for word, now re-granted to the son"),
    ((26, 5),  (22, 18), "'because Abraham obeyed my voice' — the obedience of the binding of Isaac (22:18) is named as the very ground of the blessing now passing to Isaac"),
    ((26, 8),  (21, 9),  "Isaac was metsacheq ('Isaac-ing') with Rebekah — the same participle used of Ishmael 'laughing/mocking' (21:9): the name-verb tsachaq, here the affection that betrays a husband, not a sister"),
    ((26, 24), (15, 1),  "'Do not fear, for I am with you' — the 'fear not' first spoken to Abram in the night vision (15:1), now to his son at Beersheba"),
    ((26, 33), (21, 31), "Beersheba named for an OATH a second time — Isaac's pact with Abimelech re-founds the well his father named for the same sworn word (the sheva pun, oath and seven, both times)"),

    # ---- Genesis 27 ----
    ((27, 29), (12, 3),  "'cursed be those who curse you, and blessed be those who bless you' — the very words of the promise to Abram (12:3), now stolen into Jacob's blessing along with everything else"),
    ((27, 29), (25, 23), "'be lord over your brothers, and let your mother's sons bow down to you' — the oracle Rebekah heard in the womb, 'the elder will serve the younger,' now enacted in a father's blessing"),
    ((27, 36), (25, 26), "'is he not rightly named Jacob (Ya'aqov)? he has supplanted me' — the heel-grabber's name from birth (25:26) cashed out at last: to seize the heel is to trip and overreach"),
    ((27, 36), (25, 33), "'he took my birthright, and now my blessing' — the two thefts: the bekhorah bought for stew (25:33) and now the berakhah stolen by disguise"),
    ((27, 41), (4, 8),   "'I will kill my brother Jacob' — the oldest sin in the family, brother rising to murder brother, as Cain rose against Abel (4:8); but Rebekah's warning turns it aside"),
    ((27, 46), (26, 35), "the Hittite daughters-in-law 'a bitterness of spirit' (26:35) — Rebekah's real grief becomes the perfect pretext to send Jacob safely east for a wife"),

    # ---- Genesis 28 ----
    ((28, 12), ("John", 1, 51), "the stairway with the angels 'ascending and descending' — Jesus tells Nathanael he will see 'the angels of God ascending and descending on the SON OF MAN': he is himself the Bethel, the meeting-place of heaven and earth"),
    ((28, 13), (13, 15), "'the land on which you lie — to you I will give it, and to your seed' — the land-grant of Abraham (13:15) handed down to the grandson, spoken over him as he flees it"),
    ((28, 14), (12, 3),  "'in you and your seed all the families of the earth will be blessed' — the promise of 12:3, third generation now, given to a fugitive with a stone for a pillow"),
    ((28, 3),  (17, 1),  "EL SHADDAI blesses Jacob — Isaac hands on the covenant-name God gave Abraham at the circumcision, 'I am El Shaddai; walk before me' (17:1)"),
    ((28, 15), (26, 24), "'I am with you, and will keep you wherever you go' — the presence promised to Isaac at Beersheba (26:24) now to Jacob on the road, the covenant word passing father to son"),
    ((28, 22), (14, 20), "Jacob vows a TENTH of all God gives him — the first vowed tithe, as Abraham had given Melchizedek a tenth of everything (14:20)"),

    # ---- Genesis 29 ----
    ((29, 25), (27, 35), "'why have you DECEIVED me?' — rimmah, the very root of the mirmah ('deceit') Isaac named when Jacob stole the blessing (27:35): the deceiver, in the dark, is now the deceived"),
    ((29, 26), (27, 36), "'we do not give the younger before the firstborn' — Laban's rule is a quiet judgment on the man who took both the firstborn's birthright and blessing (27:36); the measure he gave is measured back"),
    ((29, 14), (2, 23),  "'you are my bone and my flesh' — Laban's welcome borrows the kinship-cry Adam first spoke over Eve, 'bone of my bones and flesh of my flesh' (2:23)"),
    ((29, 10), (24, 15), "Jacob meets Rachel at the well — the third of the Bible's well-betrothals: as Abraham's servant found Rebekah drawing water (24:15), so the son finds his own bride at a well in the old country"),
    ((29, 31), (25, 21), "Jehovah opens the barren womb — as he answered Isaac's prayer for barren Rebekah (25:21); the matriarchs' children come by God's gift, not nature's course"),

    # ---- Leviticus 1 (cross-book) ----
    (("Leviticus", 1, 1), ("Exodus", 3, 4), "vayiqra, 'and he called' — the very verb of the burning bush, where 'God CALLED to him from within the bush, Moses, Moses!' (Exodus 3:4); now the same voice calls from the tent it fills"),
    (("Leviticus", 1, 9), (8, 21), "reyach nichoach, 'a soothing aroma' — the exact phrase of Noah's altar after the flood, when 'Jehovah smelled the soothing aroma' and swore never again to curse the ground (8:21): the first burnt-offering becomes Israel's daily law"),
    (("Leviticus", 1, 3), (17, 1), "tamim, 'without blemish' — the unflawed victim demanded at the altar is the same word God asked of Abraham's walk: 'walk before me and be blameless' (17:1)"),
    (("Leviticus", 1, 4), (6, 14), "kipper, 'to make atonement' — the piel of kaphar, 'to cover'; its plain root coated Noah's ark with pitch (kopher, 6:14). The ark that covered Noah from the judging waters and the offering that covers the sinner share one root"),

    # ---- Numbers 1 (cross-book) ----
    (("Numbers", 1, 1), ("Leviticus", 1, 1), "the tent of meeting, still speaking — Leviticus was given from it in the first month of the second year (Leviticus 1:1); one month later the same voice turns from the law of worship to the muster of an army"),
    (("Numbers", 1, 2), (21, 1), "paqad, 'to muster' — the very verb by which 'Jehovah VISITED (paqad) Sarah' with a son (21:1): God's attention-turning, once given to a barren woman, now musters the nation her son fathered"),
    (("Numbers", 1, 46), (15, 5), "603,550 fighting men — the promise made countable: God had told Abram to 'count the stars, if you are able… so shall your seed be' (15:5), a seed as uncountable as heaven; now it is an army numbered to the fifty"),
    (("Numbers", 1, 7), (29, 35), "Nahshon, chieftain of Judah, heads the muster — Judah, Leah's son named 'this time I will PRAISE Jehovah' (29:35), now leads the host and camps first, on the east: the praise-tribe at the head of the army"),
    (("Numbers", 1, 20), (29, 32), "'the sons of Reuben, Israel's firstborn' counted first — Leah's firstborn, 'Jehovah has looked on my affliction' (29:32); he keeps the honor of being numbered first, though the leadership has already passed to Judah"),

    # ---- Genesis 30 ----
    ((30, 3),  (16, 2),  "'that I may be BUILT UP through her' — ibbaneh, the ben/banah pun; Rachel gives Bilhah to Jacob in the exact words and gesture with which Sarai gave Hagar to Abram (16:2): the barren matriarch building a house through a maidservant"),
    ((30, 22), (8, 1),   "'God REMEMBERED Rachel' — zakhar, the verb that turns a story: as 'God remembered Noah' and the flood began to recede (8:1), so God remembers Rachel and opens her womb"),
    ((30, 22), (29, 31), "God opens Rachel's womb — the mercy that had opened Leah's (29:31); both sisters' children come as God's gift, not by the mandrakes or the striving of this chapter"),
    ((30, 27), (12, 3),  "'Jehovah has blessed me FOR YOUR SAKE' — Laban, a pagan, blessed on Jacob's account: the Abrahamic promise that 'in you all the families of the earth will be blessed' (12:3) at work, as it later will be through Joseph in Egypt"),
    ((30, 43), (17, 2),  "'the man increased EXCEEDINGLY' — me'od me'od, the 'very, very' of the multiply-blessing spoken over Abraham (17:2), now filling Jacob's flocks and household in Laban's own land"),

    # ---- Proverbs 1 (cross-book) ----
    (("Proverbs", 1, 7), (1, 1),   "reshit, 'beginning' — the fear of Jehovah as the START of knowledge, the exact word that opens the Bible: bereshit, 'in the beginning'"),
    (("Proverbs", 1, 7), (22, 12), "'the fear of Jehovah' — the reverent awe the angel found in Abraham at the altar: 'now I know that you fear God'"),
    (("Proverbs", 1, 4), (3, 1),   "ormah, 'shrewdness' — the serpent's own craft (arum, 'subtil'), redeemed into the survival-sense Wisdom gives the simple"),
    (("Proverbs", 1, 10), ("Jeremiah", 20, 7), "patah, 'entice' — the seduction the sinners offer the son, the same verb Jeremiah threw at heaven: 'you enticed me, Jehovah'"),

    # ---- Genesis 22 ----
    ((22, 2),  (12, 1),  "lekh-lekha, 'go, you yourself' — the emphatic doubled command that appears exactly twice in the Torah, both to Abraham: leave your land (12:1), and go to Moriah (22:2)"),
    ((22, 2),  (14, 18), "the land of Moriah — the Temple Mount (2 Chr 3:1), the hill of Melchizedek's Salem (14:18) drawn into what would become Jerusalem"),
    ((22, 3),  (21, 14), "'rose early in the morning' — the dawn-habit of Hagar's sending (21:14), now on a far darker morning"),
    ((22, 13), (21, 19), "Abraham lifted his eyes and saw the ram — as God opened Hagar's eyes and she saw the well: the seeing-thread closing on rescue"),
    ((22, 14), (16, 13), "Jehovah-Yireh, 'Jehovah sees' — the mountain named for the seeing-God Hagar first named El Roi, 'the God who sees'"),
    ((22, 17), (15, 5),  "seed like the stars of the heavens — the count Abram was shown on a night long before, now sealed under oath, and joined by the sand"),
    ((22, 18), (12, 3),  "'in your seed all the nations blessed' — the 12:3 promise, its channel now named and the whole sworn by God himself"),
    ((22, 18), (21, 12), "'because you listened to my voice' — the phrase of the garden's fall (3:17), turned to obedience (21:12), now the ground of the world's blessing"),

    # ---- Genesis 21 ----
    ((21, 6),  (17, 17), "the laughter thread — Abraham laughed face-down at the promise; now Sarah sings it: 'Laughter God has made for me'"),
    ((21, 6),  (18, 12), "Sarah's hidden, fearful laugh inside the tent — paid here as an open one, and a name"),
    ((21, 9),  (17, 17), "Ishmael metsacheq — 'laughing,' the participle of Isaac's own name-verb: whatever he did, in Hebrew he did Isaac"),
    ((21, 12), (3, 17),  "'listen to her voice' — the exact phrase of the garden's indictment, inverted here into a command that carries the plan forward"),
    ((21, 17), (16, 11), "'God heard the boy' — shama Elohim: Ishmael's name (Yishma-El, God hears), promised at his announcement, paid as an event"),
    ((21, 19), (16, 13), "God opened her eyes and she saw a well — sight returned as rescue to the woman who named him El Roi, the One who sees"),
    ((21, 33), (14, 18), "El Olam joins the El-name series — El Elyon at Salem, El Roi at the well, El Shaddai at the covenant, now the Everlasting God at a tamarisk"),

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
    ((4, 26), (12, 8),  "'called on the name of Jehovah' — the formula, from Enosh to Abram's altar"),
    ((5, 29), (6, 6),   "nacham — Noah's 'comfort' returns as Jehovah's 'regret'"),
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
    # ---- Genesis 14 ----
    ((14, 13), (10, 21), "'Hebrew' (ivri) — the name Eber, flagged in the Table of Nations, paid off on Abram"),
    ((14, 12), (13, 12), "Lot in Sodom — the cost of the tent he pitched toward the city"),
    ((14, 10), (11, 3),  "the tar (chemar) of the Siddim pits — the same word as the bitumen of Babel"),
    ((14, 19), (4, 1),   "qoneh, 'Maker' — the root qanah that Eve punned on at Cain's birth"),
    # ---- Genesis 15 ----
    ((15, 1),  (14, 20), "shield (magen) — the root of 'delivered' (miggen) in Melchizedek's blessing"),
    ((15, 1),  (14, 23), "'your reward shall be very great' — answering Abram's refusal of Sodom's reward"),
    ((15, 7),  (11, 31), "'Ur of the Chaldeans' — the Chaldean anachronism from the road out of Ur"),
    ((15, 12), (2, 21),  "the deep sleep (tardemah) — the word for the sleep God laid on the human in the garden"),
    # ---- Genesis 16 ----
    ((16, 1),  (12, 16), "an Egyptian slave-girl — Pharaoh's gifts in the Egypt sojourn included 'female servants'"),
    ((16, 2),  (3, 17),  "'listened to the voice of' his wife — the garden verdict's exact idiom, over the surrogate plan"),
    ((16, 4),  (12, 3),  "qalal — 'the one who belittles you': the promise's warning-word, tripped by Hagar's contempt"),
    ((16, 5),  (6, 11),  "chamas — Sarai's 'the wrong done to me' is the flood's word for violence"),
    ((16, 6),  (15, 13), "anah, 'afflict' — prophesied of Israel in Egypt, dealt first by Israel's house to an Egyptian"),
    ((16, 10), (15, 5),  "beyond counting — the star-promise's counting verb, spoken to a slave-girl"),
    ((16, 14), (14, 7),  "Kadesh — the En-mishpat of the war of the kings fixes Beer-lahai-roi on the map"),
    # ---- Genesis 17 ----
    ((17, 1),  (6, 9),   "tamim + the walking verb — Noah 'blameless, walked WITH God'; Abram told to walk BEFORE him"),
    ((17, 5),  (12, 2),  "'I will make your name great' — now God remakes the name itself: Abram becomes Abraham"),
    ((17, 7),  (9, 16),  "brit olam, 'everlasting covenant' — the bow's phrase, now written in the flesh"),
    ((17, 11), (9, 12),  "'the sign of the covenant' — hung in the sky for Noah, carried in the body here"),
    ((17, 14), (15, 18), "karat — a covenant is 'cut'; the male who refuses the cutting is 'cut off'"),
    ((17, 19), (16, 11), "'you shall call his name…' — the annunciation formula, spoken over Ishmael, now over Isaac"),
    ((17, 20), (16, 11), "'I have heard you' (shema'tikha) — God answers with the very verb of Ishmael's name"),
    ((17, 23), (7, 13),  "'on that very same day' — Noah's boarding formula, stamped on Abraham's same-day obedience"),
    # ---- Genesis 18 ----
    ((18, 12), (17, 17), "the laugh — Abraham's face-down, then Sarah's behind the tent flap: Isaac, 'he laughs,' is named from both"),
    ((18, 14), (17, 21), "'at the appointed time' (mo'ed) — the one-year clock on Isaac, set and repeated"),
    ((18, 20), (4, 10),  "the outcry — Abel's blood 'crying out from the ground'; Sodom's victims cry the same way"),
    ((18, 21), (11, 5),  "'let me go down and see' — Babel's procedure: judgment only after inspection"),
    ((18, 25), (16, 5),  "shaphat — 'may Jehovah judge between me and you' becomes 'shall not the Judge of all the earth do justice?'"),
    ((18, 27), (3, 19),  "dust — 'for dust you are,' owned in the first person: 'I am dust and ashes'"),
    ((18, 28), (6, 11),  "shachat, 'ruin' — the flood's verb: Abraham asks whether God is about to do THAT again"),
    # ---- Genesis 19 ----
    ((19, 5),  (18, 19), "yada — 'I have known him' against 'that we may know them': one verb, covenant and violation"),
    ((19, 9),  (18, 25), "shaphat — the mob's sneer, 'he keeps playing the judge,' against the Judge of all the earth"),
    ((19, 14), (17, 17), "metsacheq — the laugh-root gone dark: to Lot's sons-in-law, doom sounds like a joke"),
    ((19, 25), (13, 10), "the kikkar — 'like the garden of Jehovah, before Jehovah destroyed Sodom': chapter 13's flash-forward lands"),
    ((19, 27), (18, 22), "'the place where he had stood before Jehovah' — Abraham returns to yesterday's courtroom"),
    ((19, 29), (8, 1),   "zakhar — 'God remembered Noah' / 'God remembered Abraham': the remembering that acts, at both rescues"),
    ((19, 3),  (18, 6),  "the hospitality mirror — Lot's midnight urgency repeats Abraham's noon: rise, bow, press, bake"),
    # ---- Daniel 1 ----
    (("Daniel", 1, 2), (11, 2), "Shinar — the tower's own land: the temple vessels carried to Babel's country"),
    (("Daniel", 1, 7), (17, 5), "renaming — the empire renames to erase; the God of Abraham renamed to bless"),
    (("Daniel", 1, 12), ("Revelation", 2, 10), "ten days of testing — Smyrna's bounded trial speaks Daniel's dialect"),
    (("Daniel", 1, 9), (19, 19), "chesed — covenant kindness, granted this time in a foreign court"),
    # ---- Daniel 11 ----
    (("Daniel", 11, 30), (10, 4), "Kittim — Javan's son in the Table of Nations, grown into Rome: the ships that turn a king"),
    (("Daniel", 11, 16), (17, 8), "the Beautiful Land — the everlasting possession of the covenant, a chessboard square between empires"),
    (("Daniel", 11, 41), (19, 37), "Edom, Moab, and Ammon — Lot's cave-born kin, still next door at history's end"),
    (("Daniel", 11, 26), ("Daniel", 1, 8), "pat-bag — the king's portion Daniel refused, breaking a king at his own table"),
    (("Daniel", 11, 8), ("Daniel", 1, 2), "gods and vessels carried captive — the trophy-theology of the exile's first verse, replayed between pagans"),
    # ---- Genesis 20 ----
    ((20, 2),  (12, 13), "the wife-sister ruse — Egypt's script replayed at Gerar, the Bible's most famous doublet"),
    ((20, 4),  (18, 25), "'will you kill a nation even though righteous?' — the pagan king files Abraham's own brief"),
    ((20, 5),  (17, 1),  "tom — the integrity asked of Abraham ('be blameless'), claimed and confirmed for Abimelech"),
    ((20, 7),  (2, 17),  "mot tamut — Eden's doubled death-sentence, served on a king"),
    ((20, 9),  (12, 18), "'What have you done to us?' — Pharaoh's question, asked again at Gerar"),
    ((20, 13), (19, 19), "chesed — Lot's word for rescue, spent by Abraham on the ruse arrangement"),
    ((20, 18), (16, 2),  "atsar — Sarai's 'kept me from bearing' shuts every womb in Abimelech's house"),
    # ---- John 2 ----
    (("John", 2, 11), ("Revelation", 1, 1), "sēmeion — 'the beginning of the signs' and 'he made it known in signs': one method, both ends of the shelf"),
    (("John", 2, 21), ("John", 1, 14), "the naos of his body — the Word who 'tabernacled among us,' now the temple itself"),
    (("John", 2, 1), ("John", 1, 29), "'on the third day' — the running week of days from chapter 1 ends in a wedding"),
    (("John", 2, 25), (6, 5), "what is in the human — the heart Jehovah read before the flood, read now by the Word"),
    # ---- Revelation 2 ----
    (("Revelation", 2, 7), (3, 24), "the tree of life — under guard at Eden's east gate, promised open in the paradise of God"),
    (("Revelation", 2, 17), (17, 5), "the new name — the God who renamed Abram writes a new name on a white stone"),
    (("Revelation", 2, 23), ("John", 2, 25), "the searcher of hearts — 'he knew what was in the human'; 'I am the one who searches kidneys and hearts'"),
    (("Revelation", 2, 8), ("Revelation", 1, 17), "'the first and the last, who was dead' — Smyrna addressed by the Patmos vision's own title"),
    # ---- Revelation 1 ----
    (("Revelation", 1, 2), ("John", 1, 1), "the word of God — John's logos, now borne witness to from Patmos"),
    (("Revelation", 1, 8), (17, 1), "pantokratōr, 'the Almighty' — the Greek Bible's guess for El Shaddai, native at last"),
    (("Revelation", 1, 8), (2, 4), "'the one who is, and who was, and who is coming' — the divine name unfolded into tenses"),
    (("Revelation", 1, 17), (15, 1), "'do not be afraid' — the word to Abram at the Bible's first vision, spoken again at its last"),
    # ---- Daniel 12 ----
    (("Daniel", 12, 1), ("Daniel", 11, 41), "the escape-verb paid — Edom, Moab, and Ammon escaped the king's hand by geography; your people escape by enrollment, 'everyone found written in the book'"),
    (("Daniel", 12, 2), (3, 19), "'the ground of dust' gives back its sleepers — Eden's sentence, 'dust you are, and to dust you shall return,' answered with waking"),
    (("Daniel", 12, 2), ("John", 1, 4), "chayyei olam, 'everlasting life' — the Hebrew Bible's only use of the phrase; John's Gospel opens with the word: 'in him was life'"),
    (("Daniel", 12, 3), (1, 6), "'the shining of the VAULT' — raqia, day two's hammered dome, the measure of the risen teachers' brightness"),
    (("Daniel", 12, 4), ("Revelation", 1, 3), "'seal the book until the time of the end' — and the counter-order at the canon's far end: Revelation opens UNsealed, 'for the time is near'"),
    (("Daniel", 12, 7), (14, 22), "the oath posture — Abram raised one hand to Jehovah; the man in linen raises both hands to the heavens"),
    (("Daniel", 12, 10), ("Daniel", 11, 35), "'purified, made white, refined' — the martyrs' three-verb metallurgy, promised its finish"),
    # ---- Matthew 5 ----
    (("Matthew", 5, 3), ("Daniel", 12, 12), "makarios is the Greek of ashrei — Daniel's beatitude on the one who waits, now the Sermon's opening word"),
    (("Matthew", 5, 5), (15, 7), "'they shall inherit the earth' — Psalm 37's promise in the grammar of the land-grant to Abram: 'to give you this land, to inherit it'"),
    (("Matthew", 5, 14), ("John", 1, 9), "'the light of the world' — the true light that gives light to everyone; the title handed on: YOU are the light of the world"),
    (("Matthew", 5, 15), ("Revelation", 1, 20), "the lamp set on the lampstand — Revelation's vision makes the congregations themselves the lampstands"),
    (("Matthew", 5, 18), (1, 1), "'until the heaven and the earth pass away' — Genesis 1:1's merism for everything, given an expiry clause"),
    (("Matthew", 5, 22), (4, 6), "the first murder began as anger in a face — 'Why are you angry, and why has your face fallen?'"),
    (("Matthew", 5, 45), (1, 17), "the sun hung 'to shine on the earth' — and it rises on evil and good alike; the Father's indiscriminate weather"),
    (("Matthew", 5, 48), (17, 1), "'walk before me, and be blameless' — tamim, El Shaddai's charge to Abram; the Sermon closes on the Greek counterpart: whole, as the heavenly Father is whole"),
    # ---- Matthew 6 ----
    (("Matthew", 6, 13), ("Matthew", 5, 37), "apo tou ponērou — 'from the evil one,' or 'from evil': the ambiguous genitive flagged at 5:37, home in the prayer's last petition"),
    (("Matthew", 6, 4), (16, 13), "El Roi, 'the God who sees' — Hagar's name for God in the desert; the Sermon's Father 'who sees in secret'"),
    (("Matthew", 6, 26), (1, 30), "the birds of the heaven, fed — 'every green plant for food': the Creator was feeding the creatures on the record's first page"),
    (("Matthew", 6, 11), (3, 19), "bread by the sweat of your face — Eden's sentence; the prayer asks bread back as a gift, one day at a time"),
    (("Matthew", 6, 33), ("Matthew", 5, 6), "seek first the kingdom and his righteousness — the fourth Beatitude's hunger, given its compass heading"),
    # ---- Matthew 7 ----
    (("Matthew", 7, 12), ("Matthew", 5, 17), "'the Law and the Prophets' — the Sermon's bookend: opened at 5:17 ('not to tear down, but to fulfill'), closed by the Golden Rule"),
    (("Matthew", 7, 16), (3, 18), "thorns and thistles — Eden's curse-crop, the same word-pair in the Greek Bible; no grapes grow on the curse's own vegetation"),
    (("Matthew", 7, 25), (7, 17), "rain and rising waters as the test of what stands — the flood's grammar, scaled to a single house"),
    (("Matthew", 7, 15), ("Revelation", 2, 2), "wolves in sheep's clothing — Ephesus, two generations on, praised for testing self-styled apostles and finding them false"),
    (("Matthew", 7, 9), ("Matthew", 6, 11), "the prayer's bread-petition, argued from fatherhood — what father hands his child a stone?"),
    (("Matthew", 7, 26), ("Matthew", 5, 22), "mōros — forbidden as an insult at 5:22, earned as a description at 7:26: the man who hears and does not do"),
    # ---- Jeremiah 20 ----
    (("Jeremiah", 20, 16), (19, 25), "haphakh — Sodom's overthrow-verb, wished on the bearer of birth-news; the chapter's bracket, opened by the 'twister' stocks that share the root"),
    (("Jeremiah", 20, 12), ("Revelation", 2, 23), "'who sees kidneys and heart' — Jeremiah's oath, quoted back across the canon by Thyatira's Christ: 'I am the one who searches kidneys and hearts'"),
    (("Jeremiah", 20, 1), ("Matthew", 5, 22), "'these things' = the sermon of ch. 19, preached over the valley of Ben-Hinnom — the valley Greek wears as Gehenna"),
    (("Jeremiah", 20, 4), ("Daniel", 1, 2), "'all Judah into the hand of the king of Babylon' — prophesied from the stocks; recorded as done on Daniel's first page"),
    (("Jeremiah", 20, 11), (15, 1), "'Jehovah is with me like a dread warrior' — the vision-word to Abram, 'I am a shield to you,' in a fighter's key"),
    # ---- Jeremiah 21 ----
    (("Jeremiah", 21, 8), ("Matthew", 7, 13), "the Two Ways — 'the way of life and the way of death'; the Sermon's two gates walk the same fork, both descending from Deuteronomy's choice"),
    (("Jeremiah", 21, 2), ("Jeremiah", 20, 4), "Babylon, named from the stocks (~605) — now at the walls (588): the book files its two Pashhur scenes side by side, seventeen years apart"),
    (("Jeremiah", 21, 12), (18, 19), "'to do righteousness and justice' — Abraham's brief; the house of David measured against it: render justice in the morning"),
    (("Jeremiah", 21, 13), (11, 5), "'Who shall come down against us?' — Babel's page already answered the fortified boast: 'Jehovah came down'"),
    (("Jeremiah", 21, 7), ("Daniel", 1, 1), "the same king, two spellings, two sieges — Daniel's opening is Nebuchadnezzar's first visit (605); this oracle is his last (588)"),
    # ---- Jeremiah 22 ----
    (("Jeremiah", 22, 5), (22, 16), "'By myself I have sworn' — bi nishbati, verbatim: the self-oath that once SEALED the blessing to Abraham on Moriah now seals the palace's ruin if it will not do justice"),
    (("Jeremiah", 22, 21), (22, 18), "'you have not obeyed my voice' — the exact reverse of the reason Abraham was blessed, 'because you obeyed my voice': the royal house is the anti-Abraham"),
    (("Jeremiah", 22, 16), ("Proverbs", 1, 7), "'is that not to know me?' — da'at: justice for the poor IS the knowledge of God, the very word the fear of Jehovah is 'the beginning of'"),
    (("Jeremiah", 22, 10), (12, 1), "moledet, 'the land of his birth' — Abram was called to LEAVE his homeland and gained a nation; the exiled king loses his by force and never sees it again"),
    (("Jeremiah", 22, 7), ("Jeremiah", 21, 14), "the choicest cedars felled and burned — the fire promised for the palace's cedar 'forest' (the House of the Forest of Lebanon) one chapter back"),
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
    # ("Tomb of the Exodus Pharaoh: What Was Found & Why You Don't Know About It!"
    #  — PLACED 2026-07-16 on the EXODUS-PHARAOH encyclopedia entry (Exodus 1),
    #  per Michael's call to lead with Joel Kramer's early-date identification.
    #  Full research captured in research/exodus_pharaoh_early_date.md for later chapters.)
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
    # ("Sodom burned—Zoar did NOT" — FULL PLACEMENT 2026-07-16 when Genesis 19 shipped:
    #  in-chapter vclip at 19:24, plus the sodom-gomorrah and zoar encyclopedia entries'
    #  embeds, their "preview" caveats removed.)
    # ("Capernaum Unearthed" — PLACED 2026-07-16 when John 2 shipped: Capernaum
    #  entered the text at John 2:12 and got its encyclopedia entry, video embedded.)
    ("Where Jesus Was Crucified: The archaeological evidence!",
     "https://www.youtube.com/watch?v=ufVXZBrbSsU",
     "The Gospels (the crucifixion narratives)",
     "The case for the crucifixion site; place at the Passion narrative in whichever Gospel is translated first."),
    # ("The Temple Mount--Where it IS. Where it ISN'T. What is it FOR?"
    #  — PLACED 2026-07-16 on the MORIAH encyclopedia entry (Genesis 22 = the
    #  future Temple Mount, 2 Chr 3:1). Still broadly relevant; re-use for
    #  1 Kings / Solomon's Temple and the Gospels' Temple scenes when those arrive.)
    ("Caesarea: The City that Changed the World!",
     "https://www.youtube.com/watch?v=SNnCtAR_8Q8",
     "Acts (Cornelius, Paul's imprisonment)",
     "Herod's port city; the setting for several Acts episodes."),
    # ("How we KNOW the dates for the Old Testament!" — PLACED 2026-07-16 on
    #  chronology.html, its natural home, when the Chronology shipped.)
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
    (7, 16, "“Then Jehovah shut him in” — the door closes itself, once the choosing is over."),
    (8, 22, "A promise that the seasons will keep turning, for as long as the earth lasts."),
    (9, 13, "The bow in the clouds — not a rainbow decoration, a hung weapon, put away."),
    (11, 4, "“Let us make a name for ourselves” — the ambition that becomes Babel."),
    (12, 1, "“Go — you yourself” — the call that starts everything that follows."),
    (12, 2, "The promise: a great nation, a great name, and a blessing to be."),
    (13, 9, "Abram's offer to Lot — take either half, so the family doesn't have to break."),
    (13, 16, "Offspring like the dust of the earth — the promise made physical."),
    (14, 19, "Melchizedek — the Bible's first priest — blesses Abram over bread and wine."),
    (15, 6, "Trust, counted as righteousness — the sentence Paul and James both built on."),
    (16, 13, "Hagar — the only person in the Bible to give God a name: the God who sees me."),
    (17, 1, "El Shaddai's one command to a 99-year-old: walk before me, and be whole."),
    (18, 14, "The question that hangs over the whole story: is anything too wondrous for Jehovah?"),
    (18, 25, "Abraham's audacity, filed as a question: shall not the Judge of all the earth do justice?"),
    (19, 29, "The hinge of the whole rescue, stated in four words: God remembered Abraham."),
    ("John", 1, 1, "John's first sentence opens before Genesis 1:1 does."),
    ("John", 1, 14, "The Word pitched his tent among us — the tabernacle, come back."),
    ("John", 1, 29, "Passover lamb and Isaiah's servant, gathered into one title by the Baptist."),
    ("John", 2, 10, "The steward's astonished compliment — the sign's whole theology in one line."),
    ("Revelation", 1, 8, "The Alpha and the Omega — the Name unfolded into every tense at once."),
    ("Revelation", 1, 17, "The vision-word to Abram, spoken again at the canon's last vision: do not be afraid."),
    ("Revelation", 2, 10, "Smyrna's charge — kept to the letter, two generations on, by its own bishop Polycarp."),
    ("Daniel", 1, 8, "The quiet verb the whole book stands on: Daniel set on his heart."),
    ("Daniel", 11, 32, "The chapter's hinge between empires and martyrs: the people who know their God stand firm."),
    ("Daniel", 12, 3, "The Hebrew Bible's clearest resurrection scene gives the teachers the sky: shining like the vault, like the stars, forever."),
    ("Matthew", 5, 44, "The Sermon's summit — love your enemies; the sun and the rain make the argument."),
    ("Matthew", 5, 9, "The seventh Happy-saying: the peacemakers, called sons of God."),
    ("Matthew", 6, 21, "The Sermon's compass needle: the heart follows the treasure."),
    ("Matthew", 6, 26, "The argument against anxiety is a bird — fed daily by the same Father, and worth less than you."),
    ("Matthew", 7, 12, "The Golden Rule — stated positive where the ancients stated it negative, and signed: this IS the Law and the Prophets."),
    ("Matthew", 7, 7, "Three present imperatives — Greek's continuous aspect: keep asking, keep seeking, keep knocking."),
    ("Jeremiah", 20, 9, "The fire shut up in the bones — the confession of a man who tried to resign and could not."),
    ("Jeremiah", 20, 11, "The chapter's power-verb closes its ledger: God prevailed, the prophet could not, the pursuers shall not."),
    ("Jeremiah", 21, 8, "The Two Ways at their sharpest — the way of life and the way of death, with life outside the walls."),
    (21, 6, "Genesis 21 — the laughter banked since Abraham's face-down laugh finally lands: 'Laughter God has made for me.'"),
    (21, 17, "God hears the boy 'there where he is' — Ishmael's name paid as an event in the wilderness."),
    (22, 8, "The Aqedah's center: 'God will see to the lamb for himself' — the seeing that will name the mountain."),
    (22, 14, "Abraham names the place Jehovah-Yireh — 'on the mount of Jehovah, it is seen to': the hill of the future Temple."),
    (23, 4, "Abraham's own word for himself in the land promised to his seed: 'a resident alien and a settler among you.'"),
    (23, 6, "The Hittites' verdict on the landless stranger in their midst: 'a prince of God you are among us.'"),
    ("Exodus", 1, 12, "The blessing outruns the whip: 'the more they afflicted them, the more they multiplied and spread.'"),
    ("Exodus", 1, 17, "The Bible's first civil disobedience — two women: 'the midwives feared God, and did not do as the king commanded.'"),
    ("Proverbs", 1, 7, "The motto the whole book is tuned to: the fear of Jehovah is the beginning — and the chief part — of knowledge."),
    ("Proverbs", 1, 33, "Wisdom's last, quiet promise: whoever listens will dwell secure — safety not from trouble, but from fear."),
    ("Exodus", 2, 10, "The rescue funded from Pharaoh's own house: the princess names him Moses — 'because I drew him out of the water.'"),
    ("Exodus", 2, 24, "Four verbs turn the whole book: 'God heard… God remembered his covenant… God saw… and God knew.'"),
    ("Jeremiah", 22, 16, "The prophets' definition of knowing God: 'He judged the cause of the poor and needy… Is that not to know me? declares Jehovah.'"),
    ("Jeremiah", 22, 29, "The threefold cry, unforgettable in the Hebrew — erets, erets, arets: 'Land! Land! Land! Hear the word of Jehovah!'"),
    ("Exodus", 3, 5, "The first patch of earth the Bible calls holy — made holy only by the Presence: 'the place on which you are standing is holy ground.'"),
    ("Exodus", 3, 14, "The sentence the whole Bible turns on — God's own name for himself: 'I WILL BE WHAT I WILL BE.'"),
    (24, 58, "The bride's one-word answer, and the whole faith of Abraham in it: 'Will you go with this man?' — 'I will go.'"),
    (24, 67, "The tenderest close in Genesis: Isaac brought her into his mother Sarah's tent, and took Rebekah, and she became his wife; and he loved her — and Isaac was comforted after his mother."),
    (25, 23, "The oracle to Rebekah, and the pattern that runs through Genesis: 'Two nations are in your womb… and the elder will serve the younger.'"),
    (25, 34, "Five flat verbs and a verdict — 'he ate and drank and rose and went his way; so Esau despised his birthright.'"),
    (26, 22, "The reward of a patient man who kept yielding the wells — 'now Jehovah has made room for us, and we will be fruitful in the land.'"),
    (26, 24, "God to Isaac at Beersheba, in the night: 'I am the God of Abraham your father. Do not fear, for I am with you.'"),
    (27, 22, "The words that should have unmasked the whole deception, and didn't: 'The voice is the voice of Jacob, but the hands are the hands of Esau.'"),
    (27, 38, "The most anguished cry in Genesis — the rejected firstborn: 'Have you but one blessing, my father? Bless me too, my father!' And Esau lifted up his voice and wept."),
    (28, 16, "Jacob wakes from the dream of the stairway, undone by grace he did not earn: 'Surely Jehovah is in this place, and I did not know it!'"),
    (28, 17, "The fugitive's awe at an ordinary place made holy: 'How awesome is this place! This is none other than the house of God, and this is the gate of heaven.'"),
    (29, 20, "Love that makes the years light: 'Jacob served seven years for Rachel, and they seemed to him but a few days, because of his love for her.'"),
    (29, 31, "God on the side of the unloved: 'And Jehovah saw that Leah was unloved, and he opened her womb.'"),
    ("Leviticus", 1, 2, "Worship as drawing near: 'When any of you brings an offering (qorban) to Jehovah…' — the word means 'that which is brought near,' not destroyed but approached."),
    ("Leviticus", 1, 9, "The refrain of the whole altar: 'a burnt-offering, an offering by fire, a soothing aroma to Jehovah' — the exact phrase of Noah's first altar (Genesis 8:21)."),
    ("Numbers", 1, 46, "The star-promise made countable: 'all those mustered were 603,550' — the seed once as uncountable as the stars (Genesis 15:5) is now an army you can number to the fifty."),
    ("Numbers", 1, 53, "The guardians in the ring: 'the Levites shall camp around the tabernacle… that there be no wrath upon the congregation' — the one tribe left off the war-roll is the wall that keeps a holy God's people safe."),
    (30, 2, "The limit of a husband and the givenness of life: 'Am I in God's place, who has withheld from you the fruit of the womb?' Children are God's to give."),
    (30, 22, "The turn of the whole chapter: 'And God remembered Rachel, and God listened to her and opened her womb' — after all the striving, the answer comes as gift."),
]

# ---------------------------------------------------------------------------
# Journeys — drawn as a route line at the top of the Atlas (an inline-SVG map,
# self-contained, projected from real lat/lon; no map library, no external
# tiles). Each stop is either a numbered PRIMARY stop (dot + legend row) or a
# `via` bend-point (a small unlabeled vertex that shapes the line so it follows
# the rivers instead of cutting across the desert). `slug` links a stop to its
# encyclopedia entry; `ref` = (chapter, verse) deep-links into the translation.
# Honest by design: the northern arc follows the Euphrates (a herding household
# "moves at the speed of water"), and the southern leg is the route reconstructed
# from Jacob's reverse journey (Gen 31-33) — said so in the panel's own caption.
# Genesis gives NO itinerary between Haran and Shechem; this is indicative.
# ---------------------------------------------------------------------------
ROUTES = [
    dict(
        slug="abraham-migration",
        title="Abram's Migration — Ur to Canaan",
        chapters="Genesis 11–12",
        blurb=(
            "The book gives no itinerary at all between Haran and Shechem — \"they set out for the land of "
            "Canaan, and they arrived.\" This is the route reconstructed from the geography and from Jacob's "
            "later journey run in reverse (Genesis 31–33), the line the biblical archaeologist Joel Kramer "
            "retraces on the ground in the Expedition Abraham film (catalogued at the Ur and Abram entries). "
            "The northern arc follows the Euphrates — with herds you travel at the speed of water, not straight "
            "across the desert — and the southern leg comes down through Gilead, crosses the Jordan at the ford "
            "by Adam, and climbs to Shechem. A schematic drawn from real coordinates: the numbered stops are "
            "located; the connecting line is indicative."
        ),
        stops=[
            dict(name="Ur of the Chaldeans", coord=(30.9626, 46.1035), slug="ur",
                 note="Setting out for Canaan", ref=(11, 31)),
            dict(name="Babylon", coord=(32.5422, 44.4208),
                 note="Passed on the way up the Euphrates (route geography, not a Genesis stop)"),
            dict(coord=(35.95, 39.02), via=True),   # Euphrates–Balikh confluence (near Raqqa): the river's NW bend
            dict(name="Haran", coord=(36.8636, 39.0328), slug="haran-city",
                 note="Terah settles and dies; Abram's call", ref=(11, 32)),
            dict(name="Damascus", coord=(33.5131, 36.2919), slug="damascus",
                 note="Down the Aramean corridor toward Canaan"),
            dict(name="Gilead", coord=(32.40, 35.78), via=True),   # the hills of Gilead
            dict(name="Peniel", coord=(32.19, 35.68), via=True),   # the Jabbok at Peniel
            dict(name="Adam", coord=(32.10, 35.55), via=True),     # the Jordan ford by Adam
            dict(name="Shechem", coord=(32.2137, 35.2853), slug="shechem",
                 note="Journey's end (first altar) — down through the hills of Gilead, across the Jabbok at "
                      "Peniel, over the Jordan at the ford by Adam, and up the Wadi Farah",
                 ref=(12, 6)),
        ],
        # A zoomed inset of the tight Canaan-entry cluster (Gilead / Peniel / Adam /
        # Shechem) — too close together to label on the full-sweep map, so they show
        # here with the Jordan drawn in. box = (lat_min, lat_max, lon_min, lon_max).
        inset=dict(
            title="Entering Canaan — the final leg",
            box=(31.92, 32.52, 35.16, 35.95),
            jordan_lon=35.53,
        ),
    ),
]

# ---------------------------------------------------------------------------
# Chronology — the "when" layer (2026-07-16, Michael's ask). Two honest clocks,
# kept deliberately separate, plus prose on the chronology page for what the
# archaeologists can and cannot date:
#   am   — the text's OWN internal clock: years from Adam (Anno Mundi), exactly
#          as the Masoretic numbers add up. Derivable from the translation itself
#          (the begetting-ages of Genesis 5 and 11 + the stated ages of Abram).
#          Uses the plain Terah-70 reading of 11:26 (the crux is explained on the
#          page: Acts 7:4's ordering implies Terah-130, which shifts Abram +60).
#   trad — the traditional BC dates as Ussher's Annals (1650) printed them, the
#          numbers the old English Bibles carried in their margins. A
#          reconstruction, labeled as such — NOT presented as fact. (For
#          everything before Terah, trad = 4004 minus AM; from Abram on the two
#          columns run 60 years apart because Ussher took the Terah-130 reading.)
# CHRON_CHAPTERS drives the little timeline strip at the top of each chapter
# page; CHRON_EVENTS drives the big chronology.html timeline. Grow BOTH by one
# entry per new chapter. A "coming" event renders greyed, unlinked.
# ---------------------------------------------------------------------------
CHRON_ERAS = [
    ("creation",   "Creation"),
    ("preflood",   "Before the Flood"),
    ("flood",      "The Flood"),
    ("postflood",  "After the Flood"),
    ("patriarchs", "The Patriarchs"),
    ("exodus",     "Egypt and the Exodus"),
    ("monarchy",   "The Kingdom"),
    ("exile",      "The Exile"),
    ("intertestament", "Between the Testaments"),
    ("gospels",    "The Gospels"),
    ("apostolic",  "The Apostolic Age"),
]

CHRON_CHAPTERS = {
    "gen1":  dict(era="creation",
                  when="The creation week — 'day one' through the seventh day.",
                  clock="The chapter keeps its own clock: seven days. Every date below hangs from them."),
    "gen2":  dict(era="creation",
                  when="The same week from inside the garden — the sixth and seventh days, close up.",
                  clock="AM 1 — year one of the text's own count."),
    "gen3":  dict(era="preflood",
                  when="Eden and the fall — undated, inside Adam's early years.",
                  clock="The text gives no number; Seth arrives 'when Adam had lived 130 years' (5:3), so this story sits somewhere inside those decades."),
    "gen4":  dict(era="preflood",
                  when="Cain and Abel, then Cain's line running generations deep.",
                  clock="Seth is born AM 130, after Abel's death (4:25) — the chapter's one fixed peg."),
    "gen5":  dict(era="preflood",
                  when="Ten generations on one page — Adam to Noah.",
                  clock="The chapter IS the clock: its ages add straight up. Seth AM 130 · Enoch taken AM 987 · Noah born AM 1056."),
    "gen6":  dict(era="preflood",
                  when="Noah at 500; the hundred-and-twenty-year countdown announced.",
                  clock="≈ AM 1536–1656 — the last century before the flood."),
    "gen7":  dict(era="flood",
                  when="The flood begins — Noah's 600th year, the 17th day of the 2nd month.",
                  clock="AM 1656 by the Masoretic count (the Greek Bible's longer ages put it at AM 2242 — see the chronology page)."),
    "gen8":  dict(era="flood",
                  when="The flood's own logbook — a year and ten days, dated to the day.",
                  clock="AM 1656–1657; Noah steps out in his 601st year."),
    "gen9":  dict(era="postflood",
                  when="The covenant of the bow; Noah's remaining 350 years.",
                  clock="AM 1657 onward; Noah dies AM 2006."),
    "gen10": dict(era="postflood",
                  when="The Table of Nations — the generations between the flood and Abram.",
                  clock="≈ AM 1657 into the 1900s; 'in the days of Peleg' (born AM 1757) 'the earth was divided.'"),
    "gen11": dict(era="postflood",
                  when="Babel — then the ten-generation bridge from Shem to Abram.",
                  clock="Shem's line runs AM 1658 (Arpachshad) to AM 1878 (Terah); Abram born AM 1948 — or 2008: the text allows both (see the chronology page)."),
    "gen12": dict(era="patriarchs",
                  when="The call — Abram leaves Haran at 75.",
                  clock="AM 2023 · c. 1921 BC in the traditional (Ussher) reckoning."),
    "gen13": dict(era="patriarchs",
                  when="Abram and Lot separate — early in the Canaan years.",
                  clock="Between AM 2023 and 2033 (the 'ten years' of 16:3) · c. 1918 BC traditional."),
    "gen14": dict(era="patriarchs",
                  when="The war of the kings — while Abram camps at Mamre.",
                  clock="Undated, within AM 2023–2033 · c. 1913 BC in the traditional reckoning."),
    "gen15": dict(era="patriarchs",
                  when="The covenant of the pieces — before Ishmael, while the heir is still Eliezer.",
                  clock="Within AM 2023–2033 · c. 1912 BC traditional — and the chapter itself looks 400 years ahead, to the Exodus."),
    "gen16": dict(era="patriarchs",
                  when="Hagar — Abram's tenth year in Canaan; Ishmael born when Abram is 86.",
                  clock="AM 2033–2034 · c. 1911–1910 BC traditional."),
    "gen17": dict(era="patriarchs",
                  when="Abram 99, Ishmael 13; Isaac promised 'at this appointed time next year.'",
                  clock="AM 2047 · c. 1897 BC traditional."),
    "gen18": dict(era="patriarchs",
                  when="Three visitors at Mamre; the argument over Sodom — the year before Isaac.",
                  clock="AM 2047 · c. 1897 BC traditional; Sodom's last day is tomorrow."),
    "gen19": dict(era="patriarchs",
                  when="Sodom's last night — the fire at sunrise, the flight to Zoar, and the cave.",
                  clock="AM 2047 · 1897 BC in Ussher's reckoning — the year before Isaac."),
    "gen21": dict(era="patriarchs",
                  when="Isaac is born and the laughter lands; Hagar's second desert; the well of the oath at Beersheba.",
                  clock="AM 2048 · c. 1896 BC traditional — the promise of 17:21 kept 'at the appointed time,' one year on; Abraham is 100, Sarah 90."),
    "exod1": dict(era="exodus",
                  when="A family becomes a nation; a new king enslaves them; and two midwives who feared God defy the order to kill the boys.",
                  clock="The bondage in Egypt, before the Exodus. On the EARLY date this translation follows (1 Kings 6:1 → Exodus 1446 BC; Joel Kramer / Expedition Bible), the oppressing pharaoh is Thutmose III (d. c. 1425 BC) and the store-cities are built for his empire; the pharaoh of the Exodus itself is Amenhotep II. The mainstream LATE date (~1250 BC, Ramesses II) rests on the store-city name Raamses — read here as an updated place-name."),
    "exod2": dict(era="exodus",
                  when="Moses is born and drawn from the Nile in an ark of papyrus; grown, he kills an Egyptian and flees to Midian; and God hears, remembers, sees, and knows.",
                  clock="On the EARLY date this translation follows (Exodus 1446 BC), Moses is born about 1526 BC, flees Thutmose III to Midian about forty years later (2:11-15), and shepherds there through the pharaoh's death (2:23, c. 1425 BC) until the burning-bush call returns him to Amenhotep II's Egypt. The whole chapter is the forty silent years before Exodus 3."),
    "exod3": dict(era="exodus",
                  when="The burning bush at Horeb — Moses called, holy ground, and the Name revealed: 'I will be what I will be,' Jehovah, 'my name forever.'",
                  clock="c. 1446 BC on the early date — Moses is about eighty (Exodus 7:7), the oppressing pharaoh (Thutmose III) has died, and the forty Midian years end at the mountain of God. The call launches the year of the Exodus itself; Amenhotep II now sits on Egypt's throne."),
    "lev1": dict(era="exodus",
                 when="At Sinai, from the newly-raised tent of meeting, Jehovah calls Moses and gives the law of the burnt-offering — the herd, the flock, and the poor person's bird, each an offering that ascends whole in smoke.",
                 clock="c. 1445 BC on the early date — the second year after the Exodus. The tabernacle is finished and filled with glory on the first day of the second year (Exodus 40:17, 34); Leviticus is spoken FROM it, in the roughly one month before Israel breaks camp (Numbers 10:11). The whole book is delivered at Mount Sinai, before the wilderness march resumes."),
    "num1": dict(era="exodus",
                 when="In the wilderness of Sinai the redeemed people are counted and arrayed as an army — twelve tribes, twelve chieftains, 603,550 fighting men; and Levi is set apart to carry and guard the tent at the camp's center.",
                 clock="c. 1445 BC — the first day of the SECOND month of the second year, one month after Leviticus and about three weeks before the cloud lifts and Israel marches (Numbers 10:11). Thirteen months out of Egypt, the nation is mustered for the conquest it will not, for lack of faith, actually attempt for another thirty-eight years."),
    "gen23": dict(era="patriarchs",
                  when="Sarah dies at Hebron; Abraham buys the cave of Machpelah — the first parcel of the Promised Land is a grave.",
                  clock="AM 2085 · c. 1859 BC traditional — Sarah dies at 127, thirty-seven years after Isaac's birth (Isaac is now 37). The purchase gives the patriarchs their one indisputable foothold in Canaan; the tomb at Hebron is venerated to this day."),
    "gen24": dict(era="patriarchs",
                  when="Abraham sends his servant back to the family in Aram-naharaim for Isaac's bride; the sign at the well, Rebekah's 'I will go,' and the tent of Sarah restored.",
                  clock="AM 2088 · c. 1856 BC traditional — Isaac is 40 when he takes Rebekah (25:20), three years after Sarah's death; Abraham, 'old and well on in years,' is about 140. The longest chapter in Genesis, and the hinge between the first generation of the promise and the second."),
    "gen25": dict(era="patriarchs",
                  when="Keturah's sons and the peoples of the east; Abraham dies at 175, buried by Isaac and Ishmael; and the twins Esau and Jacob are born and the birthright sold.",
                  clock="Not one date but a span, in the toldot (generations) style: the twins are born when Isaac is 60 (AM 2108 · c. 1836 BC), and Abraham dies at 175 fifteen years later (AM 2123 · c. 1821 BC) — so the grandfather lived to see the boys grow. The chapter closes the first generation of the promise and opens the third."),
    "gen26": dict(era="patriarchs",
                  when="The one chapter all about Isaac — famine and the sister-ruse at Gerar, the re-dug wells (Esek, Sitnah, Rehoboth), the covenant reaffirmed, and a pact with Abimelech at Beersheba.",
                  clock="Isaac's Gerar-and-Beersheba years, spanning parts of his middle life; the chapter closes with Esau marrying at 40 (26:34), so Isaac is about 100 by its end (AM 2148 · c. 1796 BC). Non-chronological in the patriarchal manner — a portrait of the quiet middle patriarch who re-walks and re-digs his father's ground rather than breaking new."),
    "gen27": dict(era="patriarchs",
                  when="The stolen blessing — Rebekah and Jacob deceive the blind, dying Isaac to steal Esau's blessing; Esau's murderous grief drives Jacob to flee toward Haran.",
                  clock="AM ≈ 2185 · c. 1760 BC on the traditional reckoning — Isaac is about 137 (he wrongly thinks he is dying, though he will live some forty years more, to 180), and Jacob about 77. The hinge of the whole Jacob cycle: from here he flees to Laban, and the rest of Genesis follows him east and home."),
    "gen28": dict(era="patriarchs",
                  when="Jacob flees toward Haran; at Bethel he dreams of the stairway between earth and heaven, the covenant is confirmed to the fugitive, and he vows his first vow.",
                  clock="AM ≈ 2185 · c. 1760 BC — the first night of the flight begun in ch. 27, Jacob about 77. His twenty years with Laban start here; the theophany at Bethel is his first personal meeting with the God of his fathers, alone on the road with a stone for a pillow."),
    "gen29": dict(era="patriarchs",
                  when="Jacob at the well of Haran, and Laban's morning trick — Leah for Rachel; two wives, fourteen years' service, and Leah's first four sons.",
                  clock="AM ≈ 2185–2199 · c. 1760–1746 BC — the first years of Jacob's twenty in Haran. He serves seven years for Rachel, is tricked into Leah, serves seven more; the twelve tribes begin to be born (Reuben, Simeon, Levi, Judah to Leah). The deceiver's own schooling in being deceived."),
    "gen30": dict(era="patriarchs",
                  when="The war of the wives — the maidservants' sons, the mandrake bargain, and eight more children (Dan through Joseph); then Jacob out-shrewds Laban with the speckled flocks and grows rich.",
                  clock="AM ≈ 2192–2205 · c. 1753–1740 BC — the middle and later years of Jacob's twenty in Haran. Most of the twelve tribes are born here (Dan, Naphtali, Gad, Asher, Issachar, Zebulun, and Joseph, plus Dinah); with Joseph's birth Jacob turns for home, and in his last six years builds the flocks that make him wealthy enough to leave."),
    "gen22": dict(era="patriarchs",
                  when="The Aqedah — the binding of Isaac on Moriah, the ram in the thicket, and the promise sealed by God's own oath.",
                  clock="Some years after Isaac's birth (his age is debated — the midrash makes him 37, Josephus 25); Moriah is the hill 2 Chronicles 3:1 will name as the Temple Mount, so this altar stands where Solomon's will."),
    "gen20": dict(era="patriarchs",
                  when="Gerar — the sister-ruse replayed; Abimelech's dream; the Bible's first 'prophet.'",
                  clock="AM 2047–2048 · c. 1897 BC traditional — between Sodom's fall and Isaac's birth, which is one verse away."),
    "prov1": dict(era="monarchy",
                  when="The prologue to Proverbs — the purpose of wisdom, a father's first warning, and Wisdom crying aloud in the streets.",
                  clock="Attributed to Solomon, son of David (reigned c. 970–931 BC) — the wisdom gathered at Israel's royal court, though the book collects sayings from several hands across the monarchy. Wisdom literature keeps no calendar of its own: this is timeless counsel filed under the king who made the court famous for it."),
    "jer20": dict(era="exile",
                  when="Pashhur puts Jeremiah in the stocks; the prophet renames him Terror-All-Around, names Babylon at last — and curses the day he was born.",
                  clock="c. 605–598 BC, Jehoiakim's Jerusalem — after Carchemish (Babylon is finally named as the exile's destination, five times in three verses), before the first deportation arrives to prove it."),
    "jer21": dict(era="exile",
                  when="Zedekiah's delegation asks for a miracle; the answer is the bleakest in the book — God fights on the siege's side, and life is outside the walls.",
                  clock="588–586 BC, the final siege — the book has jumped seventeen years past ch. 20 (its chapters are filed by theme and catchword, not by calendar). The city and its cedar 'forest' burn in the summer of 586."),
    "jer22": dict(era="exile",
                  when="The tariff of the last four kings — Shallum carried to Egypt, Jehoiakim's donkey-burial, Coniah the signet torn off; 'is that not to know me?' and 'write this man childless.'",
                  clock="Delivered across Jehoiakim's reign (c. 609–598 BC), with its Coniah oracle reaching the deportation of 597 — the chapter surveys Josiah's dead and his three heirs in turn: Jehoahaz already in Egypt, Jehoiakim reigning, and Jehoiachin's fall previewed. The kings run in the reverse of Abraham: called out of their homeland by force, not promise."),
    "dan1": dict(era="exile",
                 when="Nebuchadnezzar takes Jerusalem's first captives — Daniel and his three friends enter Babylon's court.",
                 clock="605 BC — the year of Carchemish, fixed by the Babylonian Chronicle: the first date on this site pinned by a document outside the Bible. Verse 21 spans the whole exile in one line, 'until the first year of King Cyrus' — 539 BC."),
    "dan11": dict(era="exile",
                  when="The angel's scroll of wars — from Persia through Alexander to the abomination that desolates.",
                  clock="The vision stands in Cyrus's first Persian years (ch. 10 dates it ~536 BC) and sweeps 370 years forward — to Antiochus IV's desecration, 15 Kislev 167 BC. Where its accuracy stops (v40) is the hinge of the whole dating debate."),
    "dan12": dict(era="exile",
                  when="The vision's last words — the sleepers in the dust wake, the book is sealed, and Daniel is promised his lot at the end of the days.",
                  clock="Still Cyrus's first Persian years (~536 BC), closing the single vision of chs. 10–12 — and counting past 167 BC's desolation to the 1,290 and 1,335 days that twenty-two centuries of readers have never quite decoded."),
    "mat5": dict(era="gospels",
                 when="The Sermon on the Mount opens — eight Happy-sayings, salt and light, and six rounds of 'You have heard… but I say.'",
                 clock="c. AD 28–30, early in the Galilean ministry, on a hillside above the lake's northwest shore (tradition: the Mount of Beatitudes, above Tabgha). The first of Matthew's five great discourses — and the first page of this site printed in red letters."),
    "mat6": dict(era="gospels",
                 when="The Sermon continues — alms, prayer, and fasting in secret; the Lord's Prayer; treasure, the undivided eye, Mammon; the birds and the lilies.",
                 clock="Same hillside, same discourse (c. AD 28–30) — the middle chapter of the Sermon's three. Its prayer became the most-recited text in human history; the Didache, within living memory of the apostles, already prescribes it three times a day."),
    "mat7": dict(era="gospels",
                 when="The Sermon's finale — judge not, ask-seek-knock, the Golden Rule, the narrow gate, wolves and fruit, 'I never knew you,' and the house on the rock.",
                 clock="Same hillside, same discourse (c. AD 28–30) — the Sermon's closing chapter. Its last line ('when Jesus finished these words') is the first of five such seams: the visible joints of Matthew's five-discourse architecture."),
    "john1": dict(era="gospels",
                  when="The Baptist at the Jordan; Jesus' first disciples — and a prologue that opens before day one.",
                  clock="c. AD 26–29 (Luke 3:1 pegs the Baptist to Tiberius's fifteenth year) — while verse 1 reaches back before creation itself."),
    "john2": dict(era="gospels",
                  when="The first sign at Cana; then the first Passover — the temple cleared.",
                  clock="c. AD 27–28: 'forty-six years this temple has been under building' (2:20) counts from Herod's start in 20/19 BC — one of the Gospels' few countable dates."),
    "rev1": dict(era="apostolic",
                 when="John exiled on Patmos; the vision 'on the Lord's day' — the canon's last book opens.",
                 clock="c. AD 95 by the traditional dating (Irenaeus places the vision late in Domitian's reign); a minority argues for the late 60s, under Nero."),
    "rev2": dict(era="apostolic",
                 when="The seven letters begin — Ephesus, Smyrna, Pergamum, Thyatira.",
                 clock="c. AD 95 — the congregations of the Asian postal road, a generation after Paul walked it."),
}

CHRON_EVENTS = [
    # -- Creation --
    dict(era="creation", am="1", trad="4004 BC", event="The creation week", ref=(1, 1)),
    # -- Before the Flood --
    dict(era="preflood", am="1–130", trad="—", event="Eden, the fall, Cain and Abel — undated, inside Adam's early years", ref=(3, 1)),
    dict(era="preflood", am="130", trad="3874 BC", event="Seth born, 'in place of Abel'", ref=(4, 25)),
    dict(era="preflood", am="987", trad="3017 BC", event="Enoch taken — 'and he was not there, for God took him'", ref=(5, 24)),
    dict(era="preflood", am="1056", trad="2948 BC", event="Noah born", ref=(5, 29)),
    dict(era="preflood", am="≈1536", trad="—", event="The 120-year countdown announced", ref=(6, 3)),
    # -- The Flood --
    dict(era="flood", am="1656", trad="2348 BC", event="The flood — Noah's 600th year",
         note="Methuselah's 969 years end in AM 1656 — the very year of the flood.", ref=(7, 11)),
    dict(era="flood", am="1657", trad="2347 BC", event="The ark emptied; the covenant of the bow", ref=(9, 13)),
    # -- After the Flood --
    dict(era="postflood", am="1658", trad="2346 BC", event="Arpachshad born, 'two years after the flood'", ref=(11, 10)),
    dict(era="postflood", am="1757", trad="2247 BC", event="Peleg born — 'in his days the earth was divided': Babel's window", ref=(10, 25)),
    dict(era="postflood", am="1948 <span class='ch-alt'>(or 2008)</span>", trad="1996 BC",
         event="Abram born — the Terah crux in one row",
         note="Terah fathered his first son at 70 (11:26); whether Abram was that son decides the number — Acts 7:4's ordering implies he wasn't (Terah-130). Ussher sided with 130.",
         ref=(11, 26)),
    dict(era="postflood", am="2006", trad="1998 BC", event="Noah dies — Abram is already alive on the plain count", ref=(9, 29)),
    dict(era="postflood", am="2083", trad="1921 BC", event="Terah dies in Haran at 205",
         note="On the plain count Terah lives on sixty years after Abram's departure; Acts 7:4 and the Samaritan text read it the other way.", ref=(11, 32)),
    # -- The Patriarchs --
    dict(era="patriarchs", am="2023", trad="1921 BC", event="The call: Abram leaves Haran at 75", ref=(12, 4)),
    dict(era="patriarchs", am="2023+", trad="c. 1920–1912 BC", event="Egypt; the parting from Lot; the war of the kings; the covenant of the pieces — undated, within the decade", ref=(12, 10)),
    dict(era="patriarchs", am="2033", trad="1911 BC", event="Hagar taken, 'after Abram had lived ten years in the land'", ref=(16, 3)),
    dict(era="patriarchs", am="2034", trad="1910 BC", event="Ishmael born; Abram 86", ref=(16, 16)),
    dict(era="patriarchs", am="2047", trad="1897 BC", event="The covenant of circumcision; Abraham and Sarah named; Isaac promised for next year", ref=(17, 24)),
    dict(era="patriarchs", am="2047", trad="1897 BC", event="Three visitors at Mamre; Abraham argues the Judge of all the earth down to ten", ref=(18, 1)),
    dict(era="patriarchs", am="2047", trad="1897 BC", event="Sodom and Gomorrah overthrown; Lot escapes to Zoar; Moab and Ammon born", ref=(19, 24)),
    dict(era="patriarchs", am="2047–2048", trad="c. 1897 BC", event="Abraham at Gerar — the sister-ruse replayed; Abimelech's dream; the first 'prophet'", ref=(20, 3)),
    dict(era="patriarchs", am="2048", trad="1896 BC", event="Isaac born, 'at the appointed time' — and the laughter lands; Hagar and Ishmael sent to the wilderness of Beersheba",
         note="The child promised for three chapters is born to a hundred-year-old Abraham and a ninety-year-old Sarah, and the name banked since 17:17 is paid: Yitschaq, 'he laughs' (21:6). At the weaning feast the household divides — Hagar's second desert scene closes on the same seeing that named her first (21:19).",
         ref=("Genesis", 21, 2)),
    dict(era="patriarchs", am="—", trad="c. 1870s BC?", event="The Aqedah — Abraham binds Isaac on Mount Moriah; the ram in the thicket; the promise sealed by God's own oath",
         note="The altar of Genesis 22 stands on the hill 2 Chronicles 3:1 names as MOUNT MORIAH — the future Temple Mount, where David will buy Araunah's threshing floor and Solomon will build the first Temple (c. 966 BC). Moriah, north of the Jebusite town of Salem/Jebus, is drawn into Jerusalem only when the city expands to build there — so the hill of the binding becomes the city's heart before it wears the name. The year is uncertain: Isaac's age is debated (the midrash makes him 37).",
         ref=("Genesis", 22, 2)),
    dict(era="patriarchs", am="2085", trad="1859 BC", event="Sarah dies at Hebron; Abraham buys the cave of Machpelah — the patriarchs' first foothold in the land",
         note="Sarah dies at 127 (the only woman whose lifespan the Torah records), and Abraham — a landless 'resident alien' in the land promised to his seed — buys a field and cave from Ephron the Hittite for 400 shekels, witnessed at the city gate (Genesis 23). It is the first parcel of Canaan the patriarchs indisputably own, and becomes their tomb (Abraham, Isaac, Rebekah, Jacob, Leah); Herod's enclosure over the cave still stands at Hebron.",
         ref=("Genesis", 23, 19)),
    dict(era="patriarchs", am="2088", trad="1856 BC", event="Isaac marries Rebekah — the servant's journey to the old country, the sign at the well, 'I will go'",
         note="Abraham, old, sends his senior servant back to the family in Aram-naharaim to find Isaac a wife — not from the Canaanites, and not by bringing Isaac back east (the promise runs forward, not home). At the well the servant asks for a sign of CHESED — the girl who waters ten thirsty camels unasked — and 'before he had finished speaking' Rebekah appears (Genesis 24, the longest chapter in the book). Asked 'Will you go?', she answers with the whole faith of Abraham in a single word — 'I will go' (elekh) — leaving her land and kindred for a land she has never seen, and her family blesses her in the very words of the Aqedah oath. Isaac is 40 (25:20); he brings her into his mother Sarah's tent, loves her, and is comforted after Sarah's death.",
         ref=("Genesis", 24, 67)),
    dict(era="patriarchs", am="2108", trad="1836 BC", event="Esau and Jacob born to Isaac and Rebekah; the elder to serve the younger, and the birthright sold for stew",
         note="After twenty barren years Isaac entreats Jehovah and Rebekah conceives twins who struggle in the womb; she inquires of Jehovah directly and hears the oracle that governs the rest of Genesis — 'two nations… and the elder will serve the younger' (25:23). Esau is born ruddy and hairy (Edom, Seir), Jacob gripping his heel (Ya'aqov, the heel-holder who will supplant). Isaac is 60. Grown, Esau trades his birthright for a bowl of red lentil stew and 'despised' it (25:34) — the New Testament's type of the profane man who sells the eternal for one meal (Hebrews 12:16).",
         ref=("Genesis", 25, 26)),
    dict(era="patriarchs", am="2123", trad="1821 BC", event="Abraham dies at 175, 'old and full of years,' and is gathered to his people — buried by Isaac and Ishmael at Machpelah",
         note="The first generation of the promise closes: Abraham dies at 175, 'gathered to his people' (the death-formula that reaches past the grave to the ancestors), and his two eldest sons — Isaac the heir and Ishmael the sent-away — stand together to bury him in the cave he had bought for Sarah (Genesis 25:7-10). He lived fifteen years past the twins' birth, long enough to see his grandsons grow. Keturah's six sons, meanwhile, fan out east as the peoples of Arabia — Midian among them, the line Moses will later marry into.",
         ref=("Genesis", 25, 8)),
    dict(era="patriarchs", am="—", trad="c. 1810–1796 BC", event="Isaac's Gerar years — the covenant reaffirmed, the re-dug wells, and a pact with Abimelech at Beersheba",
         note="The one chapter given wholly to Isaac (Genesis 26). A famine sends him to Gerar, but unlike his father he is told not to go down to Egypt; God re-grants him the whole Abrahamic oath — 'because Abraham obeyed my voice.' He replays the sister-ruse, grows rich enough that the Philistines envy him, and patiently re-digs his father's stopped wells, yielding the contested ones (Esek, Sitnah) until God gives him room (Rehoboth). At Beersheba he hears 'do not fear, for I am with you,' builds an altar, and cuts a treaty with Abimelech. The quiet middle patriarch inherits and preserves rather than breaking new ground; the chapter ends with Esau's Hittite wives — 'a bitterness of spirit' that will set the next chapter in motion.",
         ref=("Genesis", 26, 24)),
    dict(era="patriarchs", am="≈2185", trad="c. 1760 BC", event="The stolen blessing — Jacob deceives the blind Isaac and takes Esau's blessing; Esau's grief drives him to flee toward Haran",
         note="Isaac, old and blind and thinking himself near death, sends Esau to hunt game for the blessing; Rebekah dresses Jacob in his brother's clothes and goatskins and cooks the savory food, and Jacob lies his way to the blessing his mother heard promised at his birth (Genesis 27). The blessing spoken cannot be recalled — 'yes, and he will be blessed' — and Esau's great and bitter cry, 'bless me too, my father!', is one of the Bible's most anguished moments (Hebrews 12:17). Esau plots murder; Rebekah sends Jacob east to her brother Laban 'for a few days' — she will never see him again. It is the hinge of the whole Jacob cycle, and the beginning of the deceiver's own long schooling in being deceived.",
         ref=("Genesis", 27, 35)),
    dict(era="patriarchs", am="≈2185", trad="c. 1760 BC", event="Jacob's ladder at Bethel — the covenant confirmed to the fugitive on the road to Haran; his first vow",
         note="On the first night of his flight, alone with a stone for a pillow, Jacob dreams of a stairway between earth and heaven with angels ascending and descending, and hears the whole Abrahamic promise spoken over him — land, seed like the dust, all families of the earth blessed, 'and I am with you, and will keep you wherever you go' (Genesis 28). He wakes crying 'Surely Jehovah is in this place, and I did not know it,' sets his stone up as an anointed pillar, names the place Bethel ('house of God'), and vows his first vow — a tenth of all he is given. It is grace to a deceiver on the run, and the stairway Jesus will one day claim as himself (John 1:51).",
         ref=("Genesis", 28, 12)),
    dict(era="patriarchs", am="≈2185", trad="c. 1760 BC", event="Jacob serves Laban — deceived into marrying Leah, then Rachel; the tribes begin to be born",
         note="Jacob reaches Haran, meets Rachel at the well, and serves Laban seven years for her — 'and they seemed to him but a few days, for the love he had for her.' But on the wedding night Laban substitutes his elder daughter Leah, and in the morning 'behold, it was Leah!' (Genesis 29). 'Why have you deceived me?', Jacob demands — and Laban answers with the very principle Jacob had trampled: 'we do not give the younger before the firstborn.' The deceiver is deceived; he serves seven more years for Rachel too. God, seeing Leah unloved, gives her the first four sons — Reuben, Simeon, Levi, and Judah — so that the priestly and the royal (and messianic) lines both spring from the wife nobody chose.",
         ref=("Genesis", 29, 25)),
    dict(era="patriarchs", am="≈2192–2205", trad="c. 1753–1740 BC", event="The tribes born and Jacob grows rich — the war of the wives, and the speckled flocks that outwit Laban",
         note="Through the bitter fertility-contest of Rachel and Leah and their two maidservants, eight more of Jacob's children are born (Genesis 30): Dan and Naphtali to Bilhah, Gad and Asher to Zilpah, Issachar and Zebulun and the daughter Dinah to Leah, and at last — 'God remembered Rachel' — Joseph, to the wife who had waited longest. With Joseph born Jacob asks to go home, but Laban, who admits 'Jehovah has blessed me for your sake,' bargains him into staying for wages of the speckled and spotted flock. Jacob answers Laban's cheating with the peeled rods and shrewd selective breeding, and 'the man increased exceedingly' — so that within six years the near-empty-handed fugitive is rich in flocks, servants, and camels, and ready to return to Canaan.",
         ref=("Genesis", 30, 22)),
    # -- Egypt and the Exodus --
    dict(era="exodus", am="—", trad="c. 15th c. BC", event="Israel enslaved in Egypt — store-cities Pithom and Raamses built; Pharaoh's decree against the newborn sons",
         note="A new king 'who did not know Joseph' turns Jacob's multiplying household into a slave force (Exodus 1). On the EARLY date this translation follows (Exodus 1446 BC, from 1 Kings 6:1; Joel Kramer / Expedition Bible — see research), the oppressor is Thutmose III, Egypt's great empire-builder, and the pharaoh of the Exodus a generation later is Amenhotep II, whose Canaan campaigns cease after 1446 and whose successor's Dream Stele hints his firstborn had died. The store-city name 'Raamses' — the pillar of the rival late date (Ramesses II, ~1250 BC) — is taken as an updated place-name, like 'Dan' in Genesis 14:14.",
         ref=("Exodus", 1, 11)),
    dict(era="exodus", am="—", trad="c. 1526–1486 BC", event="Moses born and drawn from the Nile; grown, he flees to Midian — and God hears Israel's groaning and remembers his covenant",
         note="Born to a Levite couple under Pharaoh's death-decree, hidden three months, then floated on the Nile in an ark of papyrus (the word tevah, Noah's ark) and drawn out by Pharaoh's daughter to be raised in the Egyptian court (Exodus 2). His very name is Egyptian — mose, 'born of, son,' the element in Thut-mose and Ra-messes — under a Hebrew pun on mashah, 'to draw out.' At about forty he kills an Egyptian overseer and flees to Midian, marries Zipporah, and shepherds there until the oppressing pharaoh (Thutmose III on the early date) dies (2:23) — the forty silent years before the burning bush. The chapter ends on four verbs that turn the whole book: God heard, remembered his covenant, saw, and knew.",
         ref=("Exodus", 2, 10)),
    dict(era="exodus", am="—", trad="c. 1446 BC", event="The burning bush at Horeb — Moses called; the Name revealed: 'I will be what I will be,' Jehovah",
         note="At the mountain of God, an angel of Jehovah in a bush that burns unconsumed; 'take off your sandals, for the place is holy ground'; and the God of Abraham, Isaac, and Jacob names himself — ehyeh asher ehyeh, 'I will be what I will be,' and YHWH, 'this is my name forever, my memorial to all generations' (Exodus 3:14-15). The four verbs that closed chapter 2 (God heard, remembered, saw, knew) come back in the first person out of the fire. On the early date Moses is about eighty (7:7); the call opens the year of the Exodus, 1446 BC. This chapter is the ground of the whole translation's rendering of the Name as Jehovah.",
         ref=("Exodus", 3, 14)),
    dict(era="exodus", am="—", trad="c. 1445 BC", event="At Sinai, the law of the offerings given — Leviticus is spoken from the tent of meeting",
         note="In the second year after the Exodus, with the tabernacle finished and filled with the glory-cloud (Exodus 40:17, 34), Jehovah calls Moses from within it and gives the sacrificial law — beginning with the olah, the whole burnt-offering (Leviticus 1). Israel is still encamped at Mount Sinai; the whole book is delivered here in about a month, before the march north resumes (Numbers 10:11). The offering's refrain, 'a soothing aroma to Jehovah,' reaches back to Noah's first altar after the flood (Genesis 8:21), and the demand for a victim 'without blemish' (tamim) reaches back to the walk God asked of Abraham (Genesis 17:1).",
         ref=("Leviticus", 1, 3)),
    dict(era="exodus", am="—", trad="c. 1445 BC", event="The census at Sinai — Israel mustered as an army; 603,550 fighting men, the Levites set apart",
         note="On the first day of the second month of the second year — one month after Leviticus, thirteen months out of Egypt — Moses and Aaron take a census of the twelve tribes: every male from twenty years old and upward, all who could go to war, tribe by tribe, to a total of 603,550 fighting men (Numbers 1). Israel is arrayed as an army for the march to Canaan, one chieftain (nasi) per tribe, Judah's Nahshon at the head. The tribe of Levi alone is left off the war-roll, appointed instead to carry, pitch, and guard the tabernacle and to camp around it as a buffer 'that there be no wrath upon the congregation.' The star-promise to Abram (Genesis 15:5) has become a countable host; but this same generation, at Kadesh, will refuse the land and be sentenced to die in the wilderness — the muster is of an army that never fights the war it was numbered for.",
         ref=("Numbers", 1, 46)),
    # -- The Kingdom --
    dict(era="monarchy", am="—", trad="c. 970–931 BC", event="Solomon reigns in Jerusalem — the wisdom of the royal court; the proverbs gathered under his name",
         note="David's son, at his asking, is given 'a wise and understanding heart' (1 Kings 3); his court becomes the Bible's byword for wisdom, and Proverbs is filed under his name (Proverbs 1:1) — the wisdom books' home era. His forty-year reign is the high-water mark of the united kingdom, before it splits in two at his death.",
         ref=("Proverbs", 1, 1)),
    dict(era="monarchy", am="—", trad="c. 966 BC", event="Solomon builds the First Temple on Mount Moriah — the hill of the Aqedah becomes the house of Jehovah",
         note="2 Chronicles 3:1: Solomon built 'on Mount Moriah, on the threshing floor of Ornan the Jebusite' — the very hill where Abraham had bound Isaac (Genesis 22) and where David had raised an altar. The bare height north of the old Jebusite town is now the city's heart, and 'on the mount of Jehovah it is seen to' (Genesis 22:14) has its building. Destroyed by Nebuchadnezzar in 586 BC.",
         ref=("Genesis", 22, 14)),
    # -- The Exile --
    dict(era="exile", am="—", trad="605 BC", event="Nebuchadnezzar's first deportation: Daniel taken to Babylon; the temple vessels to Shinar",
         note="Daniel 1:1's 'third year of Jehoiakim' vs Jeremiah 25:1's 'fourth' — Babylonian accession-year counting vs Judean inclusive counting; both land on 605, the year of Carchemish, fixed by the Babylonian Chronicle tablets: the chronology's first externally documented date.",
         ref=("Daniel", 1, 1)),
    dict(era="exile", am="—", trad="c. 605–598 BC", event="Jeremiah in the stocks — Pashhur renamed Terror-All-Around; Babylon named as the exile's destination",
         note="The first recorded violence against Jeremiah: a night in the 'twister' at the upper Benjamin Gate, for the sermon preached over the valley of Ben-Hinnom. The oracle that followed is the first in the book to say 'Babylon' out loud — five times in three verses — and the confession after it ('You enticed me… a burning fire shut up in my bones… cursed be the day I was born') is the rawest prayer in the prophets.",
         ref=("Jeremiah", 20, 7)),
    dict(era="exile", am="—", trad="597 BC", event="The first great deportation — Jehoiachin (Coniah), eighteen and three months on the throne, carried to Babylon; the signet torn off",
         note="Nebuchadnezzar takes Jerusalem the first time (2 Kings 24:10-16) and deports the boy-king Jehoiachin with the treasures, the craftsmen, and ten thousand captives — Ezekiel and the exile community among them; Jeremiah's tariff of kings (ch. 22) ends on his sentence, 'though Coniah were a signet on my right hand, yet would I tear you off… write this man childless.' The Babylonian Chronicle dates the city's fall to 2 Adar (16 March 597), and the excavated palace RATION TABLETS list grain and oil for 'Ya'u-kinu, king of Judah' — the deposed king, alive in Babylon, named in the archive of his captor.",
         ref=("Jeremiah", 22, 24)),
    dict(era="exile", am="—", trad="588–586 BC", event="The final siege of Jerusalem — Zedekiah's delegation told: the city goes to the fire; life is outside the walls",
         note="Nebuchadrezzar's armies close on the city; the king's last-ditch embassy asks for an Exodus-style wonder and hears the Exodus formula aimed inward — 'I myself will fight against you with an outstretched hand and a strong arm' (Jeremiah 21:5). The city and temple burned in the summer of 586 (2 Kings 25:8-9); the Lachish ostraca — Judean military letters scratched during this very campaign, dug from the gate-room ash — carry the panic contemporaneously.",
         ref=("Jeremiah", 21, 5)),
    dict(era="exile", am="—", trad="539 BC", event="Babylon falls to Cyrus — 'and Daniel continued until the first year of King Cyrus'",
         note="The exile's terminus, posted at its start (Daniel 1:21); pinned outside the Bible by the Nabonidus Chronicle and the Cyrus Cylinder.",
         ref=("Daniel", 1, 21)),
    dict(era="exile", am="—", trad="c. 536 BC", event="Daniel's last vision, by the great river — the scroll of wars, the sleepers who wake, the sealed book",
         note="One scene spanning chapters 10–12, dated by 10:1 to 'the third year of Cyrus' — an old man shown the far end of history and dismissed with a personal promise: 'you shall rest, and you shall stand up to your lot at the end of the days' (12:13). The Hebrew Bible's clearest resurrection text (12:2) belongs to this vision.",
         ref=("Daniel", 12, 2)),
    # -- Between the Testaments --
    dict(era="intertestament", am="—", trad="167 BC", event="The abomination that desolates — Antiochus IV halts the daily offering; an altar to Zeus on the altar of burnt offering",
         note="1 Maccabees 1:54 dates it to 15 Kislev, 167 BC, quoting Daniel 11:31's own phrase. Whether Daniel foresees or records the day is the book's great dating question — both readings, at full strength, on the chapter page. The temple was rededicated three years later (Hanukkah, 164 BC).",
         ref=("Daniel", 11, 31)),
    # -- The Gospels --
    dict(era="gospels", am="—", trad="c. AD 26–29", event="The Baptist at the Jordan; the Word made flesh; the first disciples", ref=("John", 1, 29)),
    dict(era="gospels", am="—", trad="c. AD 27–28", event="The first sign at Cana; the temple cleared at the first Passover",
         note="'Forty-six years this temple has been under building' (John 2:20): Josephus dates Herod's rebuild from 20/19 BC — one of the Gospels' few countable dates, and a peg for the whole ministry.",
         ref=("John", 2, 20)),
    dict(era="gospels", am="—", trad="c. AD 28–30", event="The Sermon on the Mount — the Happy-sayings; 'you have heard… but I say'; 'love your enemies'",
         note="Matthew 5–7, the first of the Gospel's five great discourses, on a hillside above the Sea of Galilee's northwest shore (tradition: the Mount of Beatitudes, above Tabgha). Undatable to a year within the ministry — placed here mid-course, where Matthew places it: after the calling of the first disciples, before the sending of the Twelve.",
         ref=("Matthew", 5, 1)),
    # -- The Apostolic Age --
    dict(era="apostolic", am="—", trad="c. AD 95", event="John, exiled on Patmos, sees the vision — 'I am the Alpha and the Omega'",
         note="Irenaeus (c. AD 180) places the vision 'toward the end of Domitian's reign' (d. 96); a minority tradition dates it under Nero, before 70. Reported, not settled.",
         ref=("Revelation", 1, 9)),
]


# ---------------------------------------------------------------------------
# BOOK_INTROS — a reference "front page" for each book of the Bible, reached
# from the Table of Contents (build.py -> book-<slug>.html). Author, date,
# place, genre, structure, themes, key words/people, source text, and — in the
# project's neutrality habit — an honest "Where the debates are" box for the
# contested questions (authorship, date, unity). LEAD with the traditional /
# conservative view, note the critical alternative honestly and briefly; never
# cast a vote. A LIVING record: refine and add as more is found. Only books the
# translation has begun need an entry; the ToC shows the rest as still ahead.
# Fields are plain strings / lists of strings; key_words are dictionary slugs
# and key_people/key_places are encyclopedia slugs (build.py filters any that
# don't exist yet, so it's safe to list ahead).
# ---------------------------------------------------------------------------
BOOK_INTROS = {
    "Genesis": dict(
        hebrew_name="בְּרֵאשִׁית",
        hebrew_translit="Bereshit",
        hebrew_meaning="'In the beginning' — the Hebrew Bible names each book by its first word.",
        greek_name="Γένεσις (Genesis)",
        greek_meaning="'Origin, generation' — the Greek title, from the book's own recurring "
                      "'these are the generations (toldot) of…' formula.",
        tagline="The book of beginnings — of the world, of humanity, and of the covenant family "
                "through whom God begins to put it right.",
        genre="Narrative — primeval history (chs. 1–11) and patriarchal saga (chs. 12–50), framed "
              "by genealogies (the toldot headings), with a few poems and covenant scenes.",
        canon="The first book of the TORAH (the Law / Pentateuch, the five books of Moses), and the "
              "first book of the Christian Old Testament.",
        author="By ancient and traditional reckoning, Jewish and Christian alike, Genesis is the first "
               "of the five books of MOSES — the lawgiver of the Exodus (15th century BC on the early "
               "date this translation follows). The book itself is anonymous; it never names its author, "
               "and its recurring 'these are the generations (toldot) of…' headings read like older "
               "records stitched into one account, which a Mosaic author would have gathered and set "
               "down. Since the 18th–19th centuries a critical view has instead read the Pentateuch as a "
               "composite of several strands woven together over centuries. This translation leads with "
               "the traditional Mosaic authorship — see 'Where the debates are' below.",
        date="On the traditional view, essentially Mosaic: the mid-15th century BC (c. 1446–1406, the "
             "wilderness years), recording events that reach from creation back through the patriarchs. "
             "The stories of chapters 12–50 are set in the early second millennium BC (Abraham c. 2000 "
             "BC on the traditional chronology); the primeval history of chapters 1–11 stands before all "
             "datable history. (The critical view dates the book's final composition far later, "
             "c. 6th–5th century BC.)",
        place="Remembered as gathered and written by Moses in the wilderness — Sinai and the plains of "
              "Moab, between Egypt and the promised land. The events themselves range from Mesopotamia "
              "(Ur, Haran) through Canaan and down into Egypt.",
        audience="Israel newly redeemed from Egypt — a people on the edge of Canaan who need to know "
                 "whose world this is, where they came from, and what God swore to their fathers. Genesis "
                 "answers exactly those questions.",
        structure=[
            ("1–11", "Primeval history — creation, Eden and the fall, Cain and Abel, the flood, the "
                     "Table of Nations, and Babel: the whole human race in broad strokes."),
            ("12–25", "Abraham — the call and the threefold promise, Sodom, the birth and binding of "
                      "Isaac, and the deaths of Sarah and Abraham."),
            ("25–28", "Isaac and the twins — Esau and Jacob, the birthright and the stolen blessing."),
            ("28–36", "Jacob — Bethel, the years with Laban, and the wrestling at the Jabbok that makes "
                      "him Israel."),
            ("37–50", "Joseph — sold into Egypt, risen to power, the family reunited, and the promise "
                      "carried down into Egypt: 'you meant it for evil, God meant it for good.'"),
        ],
        themes=[
            "The blessing and the promise — 'be fruitful and multiply,' and the threefold oath to "
            "Abraham: land, seed, and blessing to all the nations.",
            "The reversal of the firstborn — again and again God chooses the younger: Isaac over "
            "Ishmael, Jacob over Esau, Ephraim over Manasseh.",
            "Covenant — God binding himself by oath, and the signs he gives (the bow in the cloud, "
            "circumcision).",
            "Sin and its spread (chs. 3–11) answered by grace and election (chs. 12–50).",
            "Providence — a God who works through famine, barrenness, and betrayal to keep his word.",
        ],
        key_words=["toldot", "bara", "tehom", "ruach", "tselem", "brit", "chesed", "tsachaq",
                   "hineni", "aqad", "ger", "bekhorah", "aqev", "yhvh"],
        key_people=["abram", "sarai", "hagar", "ishmael", "isaac", "rebekah", "esau", "jacob",
                    "noah", "melchizedek", "lot", "keturah", "eliezer"],
        source_text="Translated from the Hebrew MASORETIC TEXT — the digital Hebrew of Mechon-Mamre "
                    "(the Leningrad/Aleppo tradition), consonants with the Masoretes' vowel-points and "
                    "cantillation. The scroll's own paragraph breaks are kept and shown as it marks "
                    "them: petuchah {פ} (open) and setumah {ס} (closed). The seven-version shelf under "
                    "every chapter compares the NIV, KJV, Douay-Rheims, The Living Bible, the 1599 "
                    "Geneva, ASV, and NWT.",
        christ="For Christian readers Genesis plants the seeds the rest of the Bible grows: the 'seed of "
               "the woman' who will crush the serpent (3:15), the blessing to all nations through "
               "Abraham's seed (12:3), the near-sacrifice of the beloved son on Moriah (ch. 22), and "
               "the scepter that will not depart from Judah (49:10). This translation marks those echoes "
               "as they come; it does not force them.",
        debates="The two live questions are AUTHORSHIP and DATE, and they travel together. The "
                "traditional view — Jewish and Christian for over two millennia — is Mosaic authorship "
                "in the 15th–13th centuries BC. The dominant academic view since Wellhausen — the "
                "'Documentary Hypothesis' and its successors — reads the "
                "Pentateuch as a composite of sources (conventionally J, E, D, and P) edited into final "
                "shape around the Babylonian exile (6th–5th c. BC), pointing to the book's doublets, its "
                "two divine names (Jehovah / YHWH and Elohim), and apparent anachronisms — 'Dan' "
                "(14:14), 'Ur of the Chaldeans,' the Philistines, domesticated camels — as seams. "
                "Conservatives answer that a 15th-century Moses could gather and update older records, "
                "that the 'anachronisms' are editorial modernizations of place-names (this translation "
                "flags several — see the Genesis 14 and Exodus 1 notes), and that the ancient Near "
                "Eastern parallels cut both ways. This library's rule holds: the readings are laid out "
                "with their pedigrees, and it does not cast a vote — the same posture it takes on "
                "Daniel's date and the date of the Exodus.",
    ),
    "Leviticus": dict(
        hebrew_name="וַיִּקְרָא",
        hebrew_translit="Vayiqra",
        hebrew_meaning="'And he called' — the book's first word: Jehovah calling Moses from the tent. "
                       "In the scroll the last letter of that first word, the aleph, is written SMALL — a "
                       "scribal tradition as old as our earliest manuscripts (see the chapter-1 notes).",
        greek_name="Λευιτικόν (Leuitikon)",
        greek_meaning="'The Levitical (book)' — the Greek title, 'the book concerning the Levites,' the "
                      "priestly tribe whose worship it governs; the Vulgate's Leviticus gives us the English "
                      "name. The Jewish tradition also calls it Torat Kohanim, 'the priests' manual.'",
        tagline="The priests' manual and the book of holiness — how a sinful people may draw near to a holy "
                "God and live in his presence without being consumed.",
        genre="Law and priestly instruction (torah) — largely DIVINE SPEECH: God dictating to Moses from the "
              "tent of meeting, with a spine of narrative (the ordination of Aaron, the death of Nadab and "
              "Abihu) running through the middle.",
        canon="The third book of the TORAH (the Law / Pentateuch, the five books of Moses), at the very "
              "center of the five — and, fittingly, the book at the heart of Israel's worship.",
        author="By ancient and traditional reckoning, Jewish and Christian alike, Leviticus is the work of "
               "MOSES — more than any other book it presents itself as words Moses received directly: some "
               "fifty-six times 'Jehovah spoke to Moses, saying…' The events sit at Mount Sinai in the second "
               "year after the Exodus (15th century BC on the early date this translation follows). The "
               "critical tradition since Wellhausen assigns most of the book to a late 'Priestly' source (P), "
               "with the Holiness Code of chapters 17–26 as a distinct hand (H); this translation leads with "
               "the traditional Mosaic authorship — see 'Where the debates are' below.",
        date="On the traditional view, essentially Mosaic: given at Sinai c. 1445 BC, in the roughly one "
             "month between the raising of the tabernacle (Exodus 40, the first day of the second year) and "
             "Israel's departure from Sinai (Numbers 10:11). (The critical view dates the Priestly material's "
             "composition far later, around the Babylonian exile, 6th–5th century BC.)",
        place="Mount Sinai — the whole book is spoken there, at and from the newly-built tent of meeting, "
              "before the wilderness march resumes.",
        audience="Israel newly redeemed and newly given God's dwelling in their midst — a people who now face "
                 "the terrifying practical question the tabernacle raises: how does a holy God live in the "
                 "camp of a sinful people without destroying it? Leviticus is the answer.",
        structure=[
            ("1–7", "The offerings — burnt, grain, peace, sin, and guilt: the five sacrifices, from the "
                    "worshipper's side (chs. 1–5) and the priest's (chs. 6–7)."),
            ("8–10", "The priesthood — Aaron and his sons ordained and installed; then Nadab and Abihu offer "
                     "'strange fire' and are struck dead: holiness is not to be improvised."),
            ("11–15", "Clean and unclean — foods, childbirth, skin disease, and bodily discharges: the daily "
                      "boundaries between the holy and the common."),
            ("16", "The Day of Atonement (Yom Kippur) — the book's center: the two goats, one for Jehovah and "
                   "one 'for Azazel,' and the once-a-year entry into the Holy of Holies."),
            ("17–26", "The Holiness Code — 'You shall be holy, for I, Jehovah your God, am holy': sexual, "
                      "social, and sabbatical law, the festivals, the jubilee, and the covenant's blessings "
                      "and curses."),
            ("27", "Vows and tithes — an appendix on things dedicated to Jehovah and their redemption."),
        ],
        themes=[
            "HOLINESS — the book's heartbeat: 'You shall be holy, for I am holy' (11:44; 19:2; 20:26). To be "
            "holy (qadosh) is to be set apart, belonging to God.",
            "ATONEMENT and BLOOD — 'the life of the flesh is in the blood… it is the blood that makes "
            "atonement' (17:11); the sacrificial system is God's provided way to cover sin.",
            "DRAWING NEAR — every offering is a qorban, 'that which is brought near': worship as approach, not "
            "appeasement of a distant deity.",
            "The PRESENCE of God in the camp — the whole book exists because the glory now dwells in the tent; "
            "everything is arranged so that Israel can live next to holiness.",
            "CLEAN and UNCLEAN — a daily grammar of the holy and the common that teaches a people to "
            "distinguish, as God distinguished light from dark at creation.",
            "'Love your neighbor as yourself' (19:18) — the verse Jesus named, with Deuteronomy 6:5, as the "
            "hinge of the whole Law.",
        ],
        key_words=["qorban", "olah", "kaphar", "tamim", "nichoach", "samakh", "shechitah", "qadash", "moed"],
        key_people=["moses", "aaron", "tabernacle"],
        source_text="Translated from the Hebrew MASORETIC TEXT — the digital Hebrew of Mechon-Mamre "
                    "(the Leningrad/Aleppo tradition), consonants with the Masoretes' vowel-points and "
                    "cantillation, and its scribal peculiarities kept — including the famous SMALL ALEPH that "
                    "ends the book's first word (1:1). The scroll's own paragraph breaks are shown as it marks "
                    "them: petuchah {פ} (open) and setumah {ס} (closed). The seven-version shelf under every "
                    "chapter compares the NIV, KJV, Douay-Rheims, The Living Bible, the 1599 Geneva, ASV, "
                    "and NWT.",
        christ="No book is read more christologically by the New Testament. The letter to the Hebrews takes "
               "Leviticus as one long shadow: the sacrifices that must be repeated because they cannot finally "
               "take away sin (Hebrews 10:1–4), the high priest who enters the Holy of Holies once a year with "
               "blood not his own — all pointing to a single, final offering. The demand for a victim 'without "
               "blemish' (tamim, 1:3) becomes 'a lamb without blemish or spot' (1 Peter 1:19); the Day of "
               "Atonement's two goats — one killed, one bearing the sins away — are read as two sides of one "
               "cross; and the poor person's two birds (1:14) are the very offering Mary and Joseph bring for "
               "the infant Jesus (Luke 2:24). This translation marks those echoes as they come; it does not "
               "force them.",
        debates="The live questions are AUTHORSHIP and DATE, as with all the Torah, and they travel together. "
                "The traditional view — Jewish and Christian for over two millennia — is Mosaic authorship at "
                "Sinai in the 15th century BC; the book's relentless 'Jehovah spoke to Moses' frame makes it "
                "the Pentateuch's strongest claimant to direct Mosaic dictation. The dominant academic view "
                "since Wellhausen assigns Leviticus to the 'Priestly' source (P), edited into shape around the "
                "Babylonian exile (6th–5th c. BC), and further isolates chapters 17–26 as a separate "
                "'Holiness Code' (H) — pointing to differences of vocabulary and emphasis between them. "
                "Conservatives answer that ancient Near Eastern ritual texts of the second millennium BC are "
                "closely comparable, that the tabernacle-centered (not temple-centered) worship fits the "
                "wilderness setting the book claims, and that thematic variation is not the same as separate "
                "authorship. This library's rule holds: the readings are laid out with their pedigrees, and it "
                "does not cast a vote — the same posture it takes on Genesis's composition and the date of "
                "Daniel.",
    ),
    "Numbers": dict(
        hebrew_name="בְּמִדְבַּר",
        hebrew_translit="Bemidbar",
        hebrew_meaning="'In the wilderness' — from the fifth word of the opening verse, 'in the wilderness of "
                       "Sinai.' The Hebrew title names the true subject of the book: the forty wilderness years.",
        greek_name="Ἀριθμοί (Arithmoi)",
        greek_meaning="'Numbers' — the Greek and Latin (Numeri) title, taken from the two great censuses that "
                      "frame the book, of the first wilderness generation (ch. 1) and the second (ch. 26).",
        tagline="The book of the wilderness years — a redeemed people counted and set in order, who then "
                "refuse the land at its border and are left to die in the desert, while God keeps his promise "
                "for their children.",
        genre="Narrative and law interwoven — a march-journal braided with censuses, camp-arrangements, "
              "priestly and purity law, and vivid set-pieces of rebellion and mercy, with a few very ancient "
              "poems (the Song of the Ark, Balaam's oracles).",
        canon="The fourth book of the TORAH (the Law / Pentateuch, the five books of Moses), and the fourth "
              "book of the Christian Old Testament.",
        author="By ancient and traditional reckoning, Jewish and Christian alike, Numbers is the work of "
               "MOSES — the man at the center of nearly every scene, and the book records that 'Moses wrote "
               "down their starting-places, stage by stage' (33:2). The events run from Mount Sinai in the "
               "second year after the Exodus to the plains of Moab in the fortieth (15th century BC on the "
               "early date this translation follows). Since Wellhausen the critical tradition has read Numbers, "
               "like the rest of the Pentateuch, as a weave of sources — much of it assigned to a late "
               "'Priestly' hand around the Babylonian exile, around an older narrative core. This translation "
               "leads with the traditional Mosaic authorship — see 'Where the debates are' below.",
        date="On the traditional view, essentially Mosaic: composed across the wilderness period, "
             "c. 1445–1406 BC. Its events span from the first day of the second month of the second year after "
             "the Exodus (1:1) to the fortieth year on the plains of Moab, just before Moses's death. (The "
             "critical view dates the book's Priestly material's composition far later, around the 6th–5th "
             "century BC.)",
        place="The wilderness — the book moves from the wilderness of SINAI (chs. 1–10), through the desert "
              "wanderings by way of Kadesh, to the plains of MOAB across the Jordan from Jericho (chs. 22–36), "
              "where Israel encamps at the threshold of the promised land.",
        audience="The SECOND generation — the children of those who came out of Egypt, mustered anew on the "
                 "plains of Moab and about to enter the land their parents refused. Numbers is written to "
                 "orient and to warn them: here is how the presence of God is to be ordered in the camp, and "
                 "here is what unbelief cost the generation before you.",
        structure=[
            ("1–10", "At Sinai — the census and the camp arrayed around the tent, the Levites set apart, the "
                     "Passover and the silver trumpets; then the cloud lifts and Israel marches."),
            ("11–12", "The march and the first grumblings — the graves of craving, and Miriam and Aaron "
                      "speaking against Moses, 'the meekest man on the face of the earth.'"),
            ("13–14", "KADESH — the twelve spies, the majority's bad report, the people's refusal to enter, "
                      "and the sentence: forty years in the wilderness, and this whole generation to die there."),
            ("15–19", "Laws and rebellion — the revolt of Korah, the plague stayed by incense, and the "
                      "budding of Aaron's staff that settles the priesthood."),
            ("20–25", "The second generation moves — the deaths of Miriam and Aaron, Moses striking the rock, "
                      "the bronze serpent, victories in Transjordan, Balaam's oracles, and the sin at Peor."),
            ("26–36", "On the plains of Moab — the second census, Joshua appointed, the daughters of "
                      "Zelophehad, the festival calendar, the boundaries of the land, and the cities of refuge."),
        ],
        themes=[
            "The ORDER of the camp around the presence — God at the center, the tribes arrayed in their "
            "armies, the Levites a ring between: holiness given a shape you could walk through.",
            "UNBELIEF and its cost — Kadesh is the hinge of the book: the refusal of the land, the forty "
            "years, 'your corpses shall fall in this wilderness' (14:29).",
            "GRUMBLING against God, and his patience — a repeated cycle of complaint, judgment, Moses's "
            "intercession, and mercy.",
            "The FAITHFULNESS of God through the faithlessness of the people — a whole generation is lost, yet "
            "the promise passes to their children intact.",
            "PROVISION in the wilderness — the manna, the water from the rock, the guiding cloud and the "
            "silver trumpets.",
            "INTERCESSION — Moses standing again and again in the breach, pleading for the people who have "
            "just risen against him (14:13–19).",
        ],
        key_words=["paqad", "eda", "matteh", "tsava", "gulgolet", "nasi", "moed"],
        key_people=["moses", "aaron", "nahshon", "judah", "mount-sinai"],
        source_text="Translated from the Hebrew MASORETIC TEXT — the digital Hebrew of Mechon-Mamre "
                    "(the Leningrad/Aleppo tradition), consonants with the Masoretes' vowel-points and "
                    "cantillation, and its scribal peculiarities kept. The scroll's own paragraph breaks are "
                    "shown as it marks them: petuchah {פ} (open) and setumah {ס} (closed). Numbers carries one "
                    "of the most striking scribal marks in the whole Torah — the two INVERTED NUNS "
                    "(<span dir='rtl'>נ</span>) that bracket the little Song of the Ark at 10:35–36, an ancient "
                    "editorial sign whose meaning the tradition still debates (a passage 'out of place,' or set "
                    "apart as its own book). The seven-version shelf under every chapter compares the NIV, KJV, "
                    "Douay-Rheims, The Living Bible, the 1599 Geneva, ASV, and NWT.",
        christ="The New Testament reads the wilderness generation as a deliberate pattern: 'these things "
               "happened to them as examples, and were written down for our instruction' (1 Corinthians "
               "10:11). Paul calls the manna and the water 'spiritual food and drink,' and says of the "
               "rock that followed them, 'that rock was Christ' (1 Corinthians 10:4). Two images reach "
               "furthest: the BRONZE SERPENT lifted on a pole, that whoever looked to it might live (21:9), "
               "which Jesus takes for his own cross — 'as Moses lifted up the serpent in the wilderness, so "
               "must the Son of Man be lifted up' (John 3:14); and Balaam's oracle of 'a STAR that shall come "
               "out of Jacob' (24:17), long read as a promise of the Messiah. This translation marks those "
               "echoes as they come; it does not force them.",
        debates="The questions are AUTHORSHIP, DATE, and — uniquely sharp in this book — the NUMBERS "
                "themselves. On authorship and date the picture matches the rest of the Torah: the traditional "
                "view is Mosaic composition in the 15th–13th centuries BC; the dominant academic view since "
                "Wellhausen reads a late 'Priestly' edition (6th–5th c. BC) around older material. The "
                "distinctive debate is the size of the census: taken plainly, 603,550 fighting men imply a "
                "nation of perhaps two million crossing the desert — a miracle sustained by daily manna. "
                "Because the Hebrew word eleph means both 'thousand' and 'clan / military unit,' some scholars "
                "read the totals as a smaller host (so-many units of so-many men); others hold the plain "
                "figures. A third strand of debate concerns the wilderness itinerary and the location of "
                "Kadesh and of Mount Sinai itself. This library prints the numbers as the text gives them, "
                "flags the eleph ambiguity in the word rather than resolving it, and lays out the readings "
                "with their pedigrees without casting a vote — the same posture it takes on Genesis's "
                "composition and the date of Daniel.",
    ),
}
