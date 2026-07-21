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
                   the project's trusted field-archaeology channel (see VIDEO_CREDITS
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
     "To afflict, oppress, humble — and, in the intensive innah, to FORCE, degrade, violate. Prophesied of Israel in Egypt (15:13), dealt by Sarai to an Egyptian (16:6), accepted in the angel's hard 'submit yourself' (16:9), heard by God in Hagar's 'affliction' (16:11) — the Exodus verb, running backward. Its darkest Genesis use is 34:2, of Shechem and Dinah — 'he took her and lay with her and innah her,' the law's own word for rape (Deuteronomy 22:29; what Amnon does to Tamar, 2 Samuel 13:14). The KJV/ASV soften it to 'humbled'; this translation renders it 'violated.'", (15, 13)),
    # ---- Genesis 34 (Hebrew) ----
    ("nevalah", "nevalah", "נְבָלָה", "nevalah",
     "An OUTRAGE — not ordinary wrong but the fixed, heavy term for a disgraceful act that tears the fabric of a people. Shechem's violation of Dinah is 'a nevalah in Israel, a thing that should not be done' (34:7); the same word names the gang-rape that ignites Israel's civil war (Judges 19-20) and Amnon's assault on Tamar ('no such nevalah is done in Israel,' 2 Samuel 13:12), and Achan's sacrilege (Joshua 7:15). It is kin to naval, the 'fool' who says in his heart there is no God (Psalm 14:1) — moral collapse, not mere foolishness. KJV and ASV flatten it to 'folly'; NIV 'disgraceful thing.' The tag 'in Israel' is pointed: the nation, freshly named two chapters back, meets its first atrocity from within its own tents.", (34, 7)),
    ("mohar", "mohar", "מֹהַר", "mohar",
     "The BRIDE-PRICE — the sum a groom's household paid to the bride's family for the marriage (distinct from the mattan, an added 'gift'). Shechem, desperate, tells Dinah's brothers to 'pile on me a very great mohar and gift, and I will give it' (34:12) — he will buy his way past the crime. The law fixes a mohar for a seduced unbetrothed girl (Exodus 22:16-17). KJV 'dowry,' which properly runs the other way (bride's family to groom); mohar is the price paid FOR the bride, not by her.", (34, 12)),
    # ---- Genesis 35 (Hebrew) ----
    ("nekhar", "nekhar", "נֵכָר", "nekhar",
     "FOREIGN, strange, other — the 'foreign gods' (elohei nekhar) Jacob orders his household to bury before they go up to Bethel (35:2, 4), among them surely the teraphim Rachel had stolen from Laban (31:19). To 'put away the elohei nekhar' becomes the refrain of every later turning-back to God — Joshua at Shechem (Joshua 24:23), Samuel (1 Samuel 7:3), the great reforms of the kings. The word also names the ben-nekhar, the 'foreigner/outsider' the law both shelters and, at the Passover, fences off (Exodus 12:43). KJV 'strange gods'; ASV and NWT 'foreign gods.'", (35, 2)),
    ("el-bethel", "El-Bethel", "אֵל בֵּית-אֵל", "El Beit-El",
     "'God of Bethel' — the name Jacob gives the ALTAR he raises on his return (35:7): not the place but its God, the God who met him here as a fugitive now claimed as his own. It makes good the vow of his first night here — 'this stone shall be God's house' (28:22) — and follows the patriarchs' pattern of naming God from an encounter (El Roi, El Elyon, El-Elohe-Israel). The compound stacks El, the ancient name of God, onto Beit-El, 'house of God,' so the altar-name reads 'the God of the house of God.'", (35, 7)),
    # ---- Genesis 36 (Hebrew) ----
    ("toledot", "toledot", "תּוֹלְדוֹת", "toledot",
     "GENERATIONS, descendants, 'the account of' — from yalad, 'to bear.' It is the load-bearing beam of Genesis: 'these are the toledot of…' divides the whole book into about ten panels — the heavens and earth (2:4), Adam (5:1), Noah (6:9), the nations (10:1), Shem and Terah (11:10, 27), Ishmael (25:12), Isaac (25:19), ESAU (36:1, and again 36:9), and Jacob (37:2). Each toledot hands the story from one generation to the next and, tellingly, clears the SIDE line before following the chosen one — Ishmael before Isaac, Esau before Jacob — so the long catalogue of Edom here is the book settling Esau's account with honor before it turns wholly to Joseph. KJV 'generations'; NWT 'history / origins.'", (36, 1)),
    ("alluf", "alluf", "אַלּוּף", "alluf",
     "A CLAN-CHIEF — the head of a 'thousand' (eleph), the leadership title of Edom, repeated like a drumbeat through this chapter (aluf Teman, aluf Omar…). The KJV famously renders it 'DUKE' (from the Latin dux, by way of the Vulgate) — a medieval European coronet comically out of place in Bronze-Age Seir; the ASV and NIV read 'chief,' the NWT 'sheik,' and this translation 'chief.' The word sketches Edom's early shape — not one throne but a federation of clan-heads — and even the king-list that follows (36:31-39) is non-dynastic, each king from a different town.", (36, 15)),
    ("yemim", "yemim", "יֵּמִם", "yemim",
     "A one-off word (a hapax legomenon) that has defeated every translator: 'this is the Anah who found the yemim in the wilderness as he pastured the donkeys' (36:24). The KJV guessed 'MULES' (from the donkey context); the NIV and most moderns read 'hot springs' (from an Aramaic cognate yamma, followed by the Vulgate's aquae calidae); the Samaritan and Syriac have 'water.' No one is sure — a clean example of how a single rare word, appearing once in the whole Bible, can leave the versions honestly guessing. This translation renders 'hot springs,' with the uncertainty flagged.", (36, 24)),
    ("ketonet-passim", "ketonet passim", "כְּתֹנֶת פַּסִּים", "ketonet passim",
     "The most famous garment in the Bible, and nobody is certain what it was (37:3). A ketonet is a plain tunic — the same word for the garments God makes in 3:21. Passim is the puzzle. The Septuagint guessed poikilos, 'many-hued'; the Vulgate followed with tunica polymita, 'many-threaded'; the KJV inherited 'a coat of many colours' and the Douay, translating the Latin, 'a coat of divers colours.' But elsewhere Hebrew pas means the flat of the hand or foot (it is the word for the PALM of the hand that writes on Belshazzar's wall, Daniel 5:5) — which yields a tunic reaching to the extremities: long-sleeved, ankle-length, the robe of someone who plainly does no work. The ASV keeps 'many colours' but concedes 'a long garment with sleeves' in the margin; the NWT reads 'a long striped garment'; the NIV 'an ornate robe,' noting the meaning is uncertain. The one hard clue: the phrase occurs in only one other story — it is what Tamar, David's daughter, wears, 'for so were the virgin daughters of the king robed,' and tears after Amnon rapes her (2 Samuel 13:18-19). Both are garments of royal rank; both end torn in a story about a violated sibling. This translation renders 'a long ornamented tunic,' with the doubt flagged rather than painted over.", (37, 3)),
    ("dibbah", "dibbah", "דִּבָּה", "dibbah",
     "A BAD REPORT, whispering, defamation — not neutral news but the word for a campaign of talk. Joseph brings his father 'their bad report' (37:2), and the text pointedly declines to say whether it was true. The word's two other famous appearances are both fatal: the ten spies bring back 'an evil report of the land' that costs a generation the promise (Numbers 13:32), and Jeremiah hears 'the whispering of many' from the men circling to kill him (Jeremiah 20:10). KJV 'evil report'; NWT 'bad report about them.'", (37, 2)),
    ("nakar", "nakar", "נָכַר", "haker / hikkir",
     "To RECOGNIZE, identify, acknowledge — the verb on which two of Genesis's cruelest scenes turn, and the same imperative both times. At Isaac's bedside the blind father 'did NOT recognize him, because his hands were hairy' (27:23), and Jacob takes a blessing that is not his. Ten chapters later Jacob's sons send him a bloodied tunic with the words haker-na — 'RECOGNIZE, PLEASE' — and he does (37:32-33), and believes a lie. Then, one chapter after that, Tamar sends Judah his own seal and staff with the identical phrase, haker-na (38:25) — the brother who engineered the sale receiving his own two words back. The verb is how this family lies to its fathers and how it is finally caught.", (37, 32)),
    ("sheol", "Sheol", "שְׁאוֹל", "she'ol",
     "The Hebrew realm of the dead — down, dark, silent — appearing here for the FIRST time in the Bible, in Jacob's 'I will go down to my son, mourning, to Sheol' (37:35). Crucially, everyone goes there: righteous and wicked alike, with no second word set against it. It is not a place of punishment, and the Hebrew Bible offers no rival destination. The KJV renders it 'the grave' here, but 'hell' in thirty-one other places and 'the pit' in three — so an English reader cannot tell that Jacob, Job, David and Isaiah are discussing one thing, and would reasonably conclude the patriarch expects the grave while the wicked go elsewhere. That is a doctrine assembled out of an inconsistent gloss. The Douay, following the Vulgate's infernum, prints 'into hell' right here — a patriarch expecting to join his beloved son there. The ASV and NWT both simply transliterate, 'Sheol,' declining to settle by translation what the Hebrew leaves open; this translation follows them on the merits — the same principle as 'vault' for raqia and 'side' for tsela.", (37, 35)),
    ("saq", "saq", "שַׂק", "saq",
     "SACKCLOTH — coarse, dark goat-hair cloth, worn against the skin as the dress of mourning and repentance. It enters the Bible in this verse, on Jacob, as a father's response to a lie about his son (37:34), and stays: the king of Nineveh trades his robe for it (Jonah 3:6), and Revelation's two witnesses prophesy in it (Revelation 11:3). The English word 'sackcloth' is literal — the same rough stuff sacks were made of.", (37, 34)),
    ("nachash", "nachash", "נָחַשׁ", "nachesh yenachesh",
     "To PRACTISE DIVINATION — to read omens. Joseph's steward says of the silver cup that his master 'indeed divines by it' (44:5), and Joseph repeats the claim to the brothers' faces (44:15). The practice is real and Egyptian: LECANOMANCY, reading the shapes made by oil dropped into water in a bowl, is attested across the ancient Near East. ⚠️ It is also flatly prohibited by the Torah later (Leviticus 19:26; Deuteronomy 18:10), which leaves an honest question the text never answers: is Joseph describing what he does, or maintaining an Egyptian persona that includes a magician's reputation? This is the man who told Pharaoh 'not I — God will answer' (41:16), so the second is at least as likely. Genesis reports the claim and declines to comment; the versions all keep it plain (KJV 'whereby indeed he divineth').", (44, 5)),
    ("cherem", "cherem", "חֵרֶם", "vayacharimu",
     "The BAN — a thing DEVOTED to God by being placed utterly beyond human use, which in war meant destroyed rather than plundered. From CHARAM, to shut off, seal away, consecrate irreversibly (the same root gives Arabic HARAM, 'forbidden/sacred'). It is the hardest concept in the conquest narratives: certain enemy cities are put under the CHEREM, their goods and often their people not taken as spoil but wiped out as an offering God alone owns. Judges 1:17 has Judah and Simeon 'put Zephath to the ban' and rename it HORMAH — 'Destruction,' the same root — freezing the act into the map. \u26a0\ufe0f This translation neither softens the word nor explains it away: it renders it as what it is and leaves the moral weight of it in the note, the same posture it takes on the numbers of the exodus and the flood.", ("Judges", 1, 17)),
    ("mas", "mas", "מַס", "la-mas",
     "FORCED LABOUR, corvée — conscripted, unpaid work owed to a ruler or state; a levy paid in bodies rather than money. \u26a0\ufe0f The word carries a bitter history in the Bible. It is what EGYPT imposed on Israel — 'they set taskmasters over them… to afflict them with their burdens' (Exodus 1:11 uses the cognate) — the very thing the exodus was a rescue FROM. So when Judges 1 says that, once Israel 'grew strong,' the tribes put the surviving Canaanites to MAS rather than driving them out (1:28, 30, 33, 35), the irony is deliberate and heavy: a people redeemed from forced labour imposing it, and doing so as a COMPROMISE with the command they were failing to keep. Solomon will later levy the same MAS on the remaining Canaanites (1 Kings 9:21) — and, disastrously, on Israel itself, which splits the kingdom. KJV 'tribute'; ESV/NIV 'forced labor.'", ("Judges", 1, 28)),
    ("hagah", "hagah", "הָגָה", "ve-hagita",
     "To MURMUR, mutter, growl — a concrete sound-word, not the abstraction 'meditate' most versions reach for. It is the low noise a lion makes over its prey (Isaiah 31:4), the moan of a dove, the muttering of a person turning something over. Applied to a scroll it means reading ALOUD UNDER THE BREATH, the ancient way of studying by voicing a text continually rather than scanning it in silence. Joshua 1:8 charges Joshua to HAGAH over the book of the instruction 'day and night,' and Psalm 1:2 uses the exact same verb of the blessed man — the two great 'day and night in the torah' texts, one opening the Prophets, one opening the Writings. KJV 'thou shalt meditate therein'; NWT 'you must read it in an undertone,' which keeps the voice.", ("Joshua", 1, 8)),
    ("sakal", "sakal", "שָׂכַל", "taskil",
     "To ACT WITH INSIGHT, and so to SUCCEED — the two senses are one in Hebrew, because to this literature success is the fruit of understanding, not luck or force. It is the root behind MASKIL ('a contemplative,' a title on several Psalms) and the verb that gave Jacob's crossed hands their meaning ('he crossed his hands SIKKEL — knowingly,' Genesis 48:14). Joshua 1:7-8 promises Joshua he will TASKIL 'wherever you go' — bracketed with TATZLIACH, 'prosper' — and pointedly attaches both to keeping the scroll rather than winning the war. The Bible's own definition of a successful general is a bookish one: prosperity follows from doing what is written. KJV 'then thou shalt have good success.'", ("Joshua", 1, 7)),
    ("nuach", "nuach", "נוּחַ", "meniach",
     "To REST, settle, come to a stop — the verb behind NOACH (Noah, 'rest') and the noun MENUCHAH, a resting-place. It is one of the book of Joshua's key promises: the point of crossing the Jordan is not conquest for its own sake but REST, somewhere to stop after forty years of not stopping (1:13, 15; 21:44; 22:4). \u26a0\ufe0f Hebrews 4 later reads this rest as UNFINISHED — 'if Joshua had given them rest, God would not have spoken of another day' — turning the land-rest into a figure for a rest still ahead, and leaning on the fact that 'Joshua' and 'Jesus' are the same name in Greek (IESOUS). The word that promises a place to stop becomes the word for something not yet reached.", ("Joshua", 1, 13)),
    ("euangelion", "euangelion", "εὐαγγέλιον", "euangelion",
     "GOOD NEWS — the word that gives us 'gospel' (Old English GOD-SPELL, 'good story'). In the wider Greek world it was an IMPERIAL announcement: the good news of a Caesar's birth, victory or accession, proclaimed across the empire — a famous inscription calls the birthday of Augustus 'the beginning (ARCHE) of the good news (EUANGELION) for the world.' Mark takes that political vocabulary and hangs it on a Galilean carpenter: his very first line, 'the beginning (ARCHE) of the good news of Jesus Christ' (1:1), reads almost as a deliberate answer to the emperor-cult. \u26a0\ufe0f Mark may have coined the use of EUANGELION as the title of a written LIFE of Jesus; the four accounts came to be called 'Gospels' after his opening word. In Jesus' own mouth it is not a book but an announcement: 'the kingdom of God has drawn near' (1:15).", ("Mark", 1, 1)),
    ("euthys", "euthys", "εὐθύς", "euthys",
     "IMMEDIATELY, at once — Mark's signature word and the engine of his Gospel. It appears about forty times in these sixteen short chapters (eleven in chapter 1 alone), far more than in all the rest of the New Testament combined, driving the narrative at a breathless run: Jesus calls, and 'IMMEDIATELY they left the nets'; he speaks, and 'IMMEDIATELY' the leprosy is gone. \u26a0\ufe0f It is not filler. The relentless EUTHYS is Mark's theology in an adverb — a kingdom breaking in with no pause for deliberation, a Jesus always in motion, a story that never sits down. Most translations vary it ('at once,' 'quickly,' 'straightway') for English elegance; keeping it consistent lets the drumbeat land. Same word EUTHEIAS in 1:3, 'make his paths STRAIGHT' — the root sense is 'straight,' and time-wise, 'straightaway.' KJV 'straightway,' its old catch-all for the word.", ("Mark", 1, 10)),
    ("basileia", "basileia", "βασιλεία", "he basileia tou theou",
     "KINGDOM, reign, royal rule — from BASILEUS, king. HE BASILEIA TOU THEOU, 'the kingdom of God,' is the heart of everything Jesus preaches, and his very first announcement: 'the time has been fulfilled, and the kingdom of God HAS DRAWN NEAR' (Mark 1:15). \u26a0\ufe0f It is less a place than an ACTIVITY — God's active reign breaking into the world — which is why 'kingdom' can mislead (there is no territory, no throne yet). The verb ENGIKEN, 'has drawn near,' is deliberately poised between 'is close at hand' and 'has arrived,' and the whole Gospel lives in that tension: the reign is here in Jesus' acts of authority and healing, and not yet in its fullness. Matthew, writing for Jewish readers wary of the divine name, mostly says 'kingdom of HEAVEN' for the same thing.", ("Mark", 1, 15)),
    ("propempo", "propempo", "προπέμπω", "propempsas",
     "To SEND ON THE WAY — a semi-technical word in the early church for equipping a traveller for the next leg of a journey: food, money, letters of introduction, sometimes an escort. It is the material engine of the whole early Christian mission. 3 John 6 tells Gaius he 'will do well to send them on their way (PROPEMPSAS) worthily of God,' and verse 8 turns the act into a theology: to support such travellers is to become 'FELLOW WORKERS with the truth.' The one who never leaves home but funds the one who does is a partner in the mission, not a spectator to it. Paul uses the same verb repeatedly of being outfitted by a church for onward travel (Romans 15:24; 1 Corinthians 16:6, 11; Titus 3:13).", ("3 John", 1, 6)),
    ("xenos", "xenos", "ξένος", "xenous",
     "A STRANGER, and also a GUEST — the same word for the unknown outsider and for the visitor you take in, because in the ancient world the two were meant to be the same act. It is the root of PHILOXENIA, 'love of strangers,' which is simply the Greek word for HOSPITALITY: a whole virtue named for treating the unknown traveller well. 3 John 5 praises Gaius for what he does for the brothers 'and these, XENOUS' — strangers he had never met and who could not repay him. The New Testament presses the point hard: 'do not neglect PHILOXENIA, for by it some have entertained angels unawares' (Hebrews 13:2). \u26a0\ufe0f The negative twin of the virtue stands one letter away in the pair: 2 John tells a church to refuse a XENOS who carries a false Christ. Same act, opposite travellers — the message decides, not the stranger's strangeness.", ("3 John", 1, 5)),
    ("agape", "agape", "ἀγάπη", "agape",
     "LOVE — the noun this literature is built on. Greek had several words for love and AGAPE was the least loaded of them: not EROS (desire), not PHILIA (the warm bond of friends and kin), but a comparatively colourless word that the Septuagint and then the New Testament filled up with content. \u26a0\ufe0f It is often said that AGAPE means specifically divine or selfless love while PHILEO means mere affection; that is an overstatement — John uses the two almost interchangeably (compare 21:15-17, where the verbs alternate with no evident shift). What is true is that this literature DEFINES the word rather than assuming it: 2 John 6 says flatly, 'this is love: that we walk according to his commandments' — love as a road walked, not a feeling described.", ("2 John", 1, 6)),
    ("aletheia", "aletheia", "ἀλήθεια", "aletheia",
     "TRUTH — and in John's writing far more than accuracy. The word saturates 2 John: five times in the first three verses (loved IN truth, all who KNOW the truth, the truth that REMAINS in us, grace and peace 'in truth and love'). It behaves less like a set of correct statements than like a place you can stand in and walk in — one can 'walk in truth' (v. 4) the way one walks in a road. \u26a0\ufe0f The letter's whole argument depends on truth and love being welded rather than balanced: the refusal of hospitality in vv. 10-11 is offered as an APPLICATION of love, not an exception to it. Greek ALETHEIA is built on a negation — 'un-concealment' — though by the first century that etymology is long buried in ordinary usage.", ("2 John", 1, 1)),
    ("meno", "meno", "μένω", "meno",
     "To REMAIN, abide, stay put — John's favourite verb and the hinge of 2 John. The letter sets it directly against PROAGO, to 'run ahead': 'everyone who RUNS AHEAD and does not REMAIN in the teaching of the Christ does not have God' (v. 9). \u26a0\ufe0f The irony is almost certainly deliberate — the opponents evidently presented themselves as ADVANCED, and the letter takes their own vocabulary and turns it: to get out in front of the teaching is not to arrive somewhere better but to leave. The same verb carries the Gospel's 'remain in me' (John 15) and the truth that 'REMAINS in us and will be with us forever' (v. 2). In a letter about who may be received, the verb for staying is the one that decides it.", ("2 John", 1, 9)),
    ("entole", "entole", "ἐντολή", "entole",
     "A COMMANDMENT — a specific charge or instruction, not a body of law (that would be NOMOS). John uses it for the one thing commanded: love one another. 2 John 5 makes the paradox explicit — 'not as though writing you a NEW commandment, but the one we have had FROM THE BEGINNING' — which sits deliberately beside Jesus calling that same command NEW (John 13:34). Both hold in their own frame: new in the manner of the commanding, old in that it was there from the start. \u26a0\ufe0f The letter is written to people being offered novelty, which is why it presses the old.", ("2 John", 1, 5)),
    ("devarim", "devarim", "דְּבָרִים", "elleh ha-devarim",
     "WORDS — and the Hebrew name of the fifth book of the Torah, taken as always from its own opening line: ELLEH HA-DEVARIM, 'these are the words that Moses spoke' (Deuteronomy 1:1). It could not be better named. Moses does almost nothing in this book but talk: it is three long sermons and a song, delivered in the last weeks of his life to a generation that did not see Egypt. \u26a0\ufe0f The ENGLISH title comes from a different route — the Greek DEUTERONOMION, 'second law,' from the Septuagint's rendering of a phrase at 17:18 that in Hebrew means 'a COPY of this instruction.' The Greek title has stuck for two thousand years and is not quite what the Hebrew says: this is not a second law but the first one preached. DAVAR itself covers word, thing, matter, affair — in Hebrew a word is an object with weight.", ("Deuteronomy", 1, 1)),
    ("torah", "torah", "תּוֹרָה", "ha-torah ha-zot",
     "INSTRUCTION, teaching, direction — from YARAH, to throw or shoot, and so to point the way (the same root behind MOREH, a teacher). Rendering it 'law' is the Greek Bible's choice (NOMOS) and it narrows the word: TORAH is what a parent teaches a child (Proverbs 1:8 calls a mother's teaching her torah) as much as what a court enforces. Deuteronomy 1:5 says Moses 'undertook to make this TORAH plain' — BE'ER, a concrete verb for digging out or engraving something so it can be read at a run (Habakkuk 2:2). So the book's own account of itself is not 'Moses restated the legislation' but: he set about making the teaching unmistakable. KJV 'began Moses to declare this law'; ESV 'undertook to explain this law.'", ("Deuteronomy", 1, 5)),
    ("chashav", "chashav", "חָשַׁב", "chashavtem / chashavah",
     "To DEVISE, plan, reckon, intend — the verb of deliberate purpose (it is also the word for accounting: to reckon something to someone's account, as at 15:6, 'he reckoned it to him as righteousness'). Genesis 50:20 uses it TWICE, of two different agents, over one event: 'you CHASHAV evil against me; God CHASHAV it for good.' \u26a0\ufe0f Notice what the sentence does not say. It does not say the evil was secretly good; the object of the first verb is RA'AH, evil, flatly. It does not deny they did it — three verses earlier their own message calls it 'the transgression of your brothers and their sin.' And it does not say God made them do it. Two agents, one event, opposite intentions, both intentions real. It is the fully developed form of what Joseph said in the heat of the reveal at 45:8 ('it was not you who sent me here, but God'), now restated with the guilt left in. KJV 'ye thought evil against me; but God meant it unto good.'", (50, 20)),
    ("aron", "aron", "אָרוֹן", "ba-aron",
     "A CHEST, box, or coffer — and the last noun in the book of Genesis. 'They embalmed him, and he was put BA-ARON BE-MITZRAYIM' (50:26): in a coffin, in Egypt. \u26a0\ufe0f It is the same ordinary word that will later name the ARK OF THE COVENANT, the chest carried through the wilderness and into the land — so the container that ends Genesis and the container at the centre of Israel's worship are called the same thing. A book that opens 'in the beginning God created the heavens and the earth' closes on an embalmed man in a box, and the final Hebrew word is the name of the wrong country. Nothing promised has arrived: the land is a grave-plot, the nation is seventy people in a border province. The ending is not a resolution, and is not meant to be one.", (50, 26)),
    ("acharit-hayamim", "acharit ha-yamim", "אַחֲרִית הַיָּמִים", "be-acharit ha-yamim",
     "THE LATTER DAYS — literally 'the AFTER of the days': the far end of things, what lies at the horizon of what is coming. Its first occurrence is Jacob summoning his sons (49:1) to hear what will happen to them BE-ACHARIT HA-YAMIM. \u26a0\ufe0f The phrase does NOT by itself mean 'the end of the world.' In the prophets it can mean anything from 'later on' to a genuinely final horizon, and later readers — Jewish and Christian — took it as a technical term for the eschaton and read Genesis 49 accordingly. Here it introduces a poem about tribal territories, forced labour and roadside ambushes, so the reach of the phrase is exactly what is in dispute. KJV 'in the last days'; ESV 'in days to come.' This translation renders it plainly and leaves the distance open.", (49, 1)),
    ("shiloh", "shiloh", "שִׁילֹה", "ad ki yavo shiloh",
     "The most disputed word in Genesis. 'The sceptre shall not depart from Judah… AD KI YAVO SHILOH' (49:10). Four serious readings: (1) a NAME — 'until Shiloh comes,' which is what the Masoretic vowels give and the least self-explanatory, since the referent is undefined; (2) a PLACE — 'until he comes to Shiloh,' the town in Ephraim where the tabernacle stood; (3) reading the consonants as SHELLO, 'until that which is his comes' / 'until he comes to whom it belongs' — the understanding behind the Septuagint and Syriac, and apparently alluded to at Ezekiel 21:27, 'until he comes whose right it is'; (4) SHAI LO, 'until tribute comes to him.' \u26a0\ufe0f The verse has been read messianically in BOTH traditions for a very long time — the Jewish Targums render it 'until Messiah comes,' and Christian readers apply it to Jesus — but that reading rests on options (1) or (3), not on anything the consonants settle by themselves. Modern versions genuinely disagree: KJV/NWT 'until Shiloh come'; ASV with a margin note; ESV 'until tribute comes to him.' This project gives the readings with their pedigrees and does not vote.", (49, 10)),
    ("goel", "go'el", "גֹּאֵל", "ha-go'el",
     "REDEEMER — one who BUYS BACK. GA'AL is not a religious abstraction but a family obligation in Israelite law: the go'el is the nearest kinsman with both the standing and the duty to recover what a relative has lost — to buy back sold land, to ransom a relative sold into servitude, to marry a childless widow, to avenge a killing (Leviticus 25:25-55; Numbers 35). Its FIRST occurrence in the Bible is here, in a blessing over two boys: 'the angel who has REDEEMED me from all evil' (48:16). Jacob places it in apposition with 'the God who has shepherded me' — whether identifying the angel WITH God or distinguishing him from God is grammatically open, and readers have gone both ways for two thousand years. The word goes on to carry Boaz in Ruth, the jubilee laws, and a great deal of Isaiah. KJV 'the Angel which redeemed me from all evil.'", (48, 16)),
    ("sikkel", "sikkel", "שִׂכֵּל", "sikkel et yadav",
     "He CROSSED his hands — KNOWINGLY. The word every translation renders 'crossed' is the piel of SAKAL, whose entire family of meanings is about insight, prudence and acting with understanding; it is not the ordinary Hebrew word for crossing anything. At the exact moment Jacob's arms go over each other to put his right hand on the younger boy's head, the narrator chooses a verb meaning TO DO A THING ADVISEDLY (48:14) — so the crossing and the knowing are one act in one word, and you are told the answer before Joseph objects. The KJV caught it and has never been bettered: 'guiding his hands wittingly'; ASV the same. Modern versions (ESV 'crossing his hands,' NIV 'crossing his arms') are accurate about the gesture and lose the deliberateness entirely. Three verses later Jacob says it in plain words: 'I know, my son, I know.'", (48, 14)),
    ("megurim", "megurim", "מְגוּרִים", "megurai",
     "SOJOURNINGS — the time spent living somewhere as a resident alien, from GUR, 'to reside as a stranger.' A GER is a foreigner lawfully present but landless: protected, tolerated, and holding no title to the ground under him. Pharaoh asks Jacob how many are the days of his LIFE; Jacob answers about the days of his MEGURIM (47:9), and then extends the word to his fathers as well. Standing in the richest country on earth, having just been handed its best province, he describes three generations as people who never owned anywhere — which is the patriarchal story in a single word, said to a man who owns everything he can see. The one piece of ground they do own is a grave (23:9). KJV 'the days of the years of my pilgrimage.'", (47, 9)),
    ("chomesh", "chomesh", "חֹמֶשׁ", "la-chomesh",
     "A FIFTH — twenty percent. It appears twice in the Joseph story and the second time is the first one made permanent: Joseph tells Pharaoh to take a fifth of the harvest through the seven good years (41:34), and then, when the famine has stripped the country of its silver, its livestock and finally its land, he fixes a fifth to Pharaoh as a STATUTE 'to this day' (47:26). The people are buying back their own stored surplus and paying for it with everything they own. A crown owning the land and taking a fixed share of every harvest, with a tax-exempt temple estate beside it, is a recognisable description of later Egyptian agriculture — the narrator is explaining to his readers why the country they know is arranged as it is.", (47, 24)),
    ("anokhi", "anokhi", "אָנֹכִי", "anokhi",
     "I, MYSELF — the long, emphatic form of the pronoun (beside the ordinary ANI). Hebrew normally carries the subject inside the verb, so writing the pronoun out at all is emphasis, and using the long form doubles it. Genesis 46:4 uses it TWICE in one verse, at the border, to a frightened old man: 'ANOKHI will go down with you to Egypt, and ANOKHI will surely bring you up again.' The promise is not that the family will be spared the descent but that God is going into it with them and coming back out. The same word opens the Ten Commandments ('ANOKHI is Jehovah your God,' Exodus 20:2). KJV catches it with 'I will go down with thee… and I will also surely bring thee up again.'", (46, 4)),
    ("mikneh", "mikneh", "מִקְנֶה", "anshei mikneh",
     "LIVESTOCK, and by extension the wealth held in it — from QANAH, 'to acquire': cattle as the thing you buy WITH, the standing capital of a herding people. The phrase ANSHEI MIKNEH, 'men of livestock,' is the one Joseph coaches his brothers to say to Pharaoh (46:34) instead of the blunter RO'EI TSON, 'shepherds of flocks,' which he uses himself when briefing them (46:32) — owners rather than hired hands, the same trade with a better title on it. It is a small, precise piece of court management, and Genesis lets you watch him do it.", (46, 32)),
    ("michyah", "michyah", "מִחְיָה", "le-michyah",
     "PRESERVATION OF LIFE, sustenance — from CHAYAH, to live: literally 'a means of staying alive.' It is the first of the three salvation words Joseph piles up when he finally explains himself: 'God sent me before you LE-MICHYAH — to preserve life' (45:5). The same root closes the chapter, when the wagons are seen and 'the SPIRIT OF JACOB REVIVED' (vatechi ruach, 45:27) — the man who insisted he would go down to Sheol mourning comes back to life in a clause. KJV 'to preserve life'; ASV the same.", (45, 5)),
    ("sheerit", "she'erit", "שְׁאֵרִית", "she'erit",
     "A REMNANT — what is LEFT OVER, from a root meaning to remain. Joseph uses it of a family of seventy people: 'God sent me before you to set for you a SHE'ERIT in the land' (45:7). The scale is domestic and the vocabulary is national — this is the word the prophets will spend centuries using for the surviving fragment of Israel after catastrophe (Isaiah 10:20-22; Jeremiah 23:3; Micah 2:12). Genesis plants it here, in a private room, describing a rescue nobody outside that room knows happened. KJV 'to preserve you a posterity in the earth'; ASV and ESV keep 'remnant.'", (45, 7)),
    ("peletah", "peletah", "פְּלֵיטָה", "li-fletah gedolah",
     "ESCAPE, DELIVERANCE — and by extension those who escape, the survivors; from PALAT, to slip away to safety. Joseph's third salvation word in three verses: 'to keep you alive LI-FLETAH GEDOLAH — for a great deliverance' (45:7). This translation keeps MICHYAH, SHE'ERIT and PELETAH as three distinct words rather than merging them into a single 'to save your lives,' because Joseph is deliberately stacking them: life preserved, a remnant set in place, an escape on a large scale. KJV 'to save your lives by a great deliverance'; the ESV flattens toward sense with 'to keep alive for you many survivors.'", (45, 7)),
    ("ragaz", "ragaz", "רָגַז", "al tirgezu",
     "To TREMBLE, be stirred up, be agitated — and, by an easy extension, to QUARREL. Joseph's last words to his brothers as they leave for Canaan: 'AL TIRGEZU BA-DEREKH — do not be agitated on the way' (45:24). The range is the whole interest. Read one way it is reassurance: don't be afraid, nothing will happen to you. Read the other it is a warning he has good reason to give — don't spend the entire journey arguing about whose idea the pit was; the old Jewish reading, and the one behind KJV's 'see that ye fall not out by the way.' NIV and ESV both choose 'quarrel'; NWT 'do not get upset.' This translation keeps AGITATED, which is where the Hebrew sits, and leaves the reader holding both.", (45, 24)),
    ("avon", "avon", "עָוֺן", "avon",
     "GUILT, iniquity — from a root meaning to bend or twist; the heaviest of the Hebrew words for wrongdoing, naming not a single act but the crookedness a person carries, and the liability that comes with it. It is the word in Judah's extraordinary answer when the cup is found in Benjamin's bag: 'God has found out the AVON of your servants' (44:16). They are innocent of the theft and Judah knows it — he is confessing something else entirely, twenty-two years old, to the one man in the room who knows exactly what he means. KJV 'God hath found out the iniquity of thy servants.'", (44, 16)),
    ("arav", "arav", "עָרַב", "e'ervennu",
     "To STAND SURETY, go guarantor — a commercial word: to pledge yourself against another's debt, so that if the thing is lost, YOU pay. It is what makes Judah's offer the hinge of the Joseph story. Reuben had said 'you may put my two sons to death if I do not bring him back' (42:37) — a man offering his own children as collateral, which is monstrous and costs him nothing he has to feel; Jacob refused flatly. Judah says 'I MYSELF will be surety for him — from my hand you shall require him' (43:9), putting up himself, and his father says yes. He then makes it good in ch. 44, offering to stay a slave in Benjamin's place — the moment Joseph stops being able to hold himself in. KJV 'I will be surety for him; of my hand shalt thou require him.'", (43, 9)),
    ("rachamim", "rachamim", "רַחֲמִים", "rachamim",
     "COMPASSION, mercy — and the word is built on RECHEM, the WOMB. Hebrew's ordinary term for mercy is mother-love: the physical ache of a parent for a child. Genesis 43 uses it twice, and the pairing is the chapter's quietest miracle. Jacob prays 'may El Shaddai give you COMPASSION before the man' (43:14), asking God to put womb-feeling into a hard Egyptian official; sixteen verses later that official sees his little brother and 'his COMPASSION grew warm toward his brother' (nikhmeru rachamav, 43:30 — the verb means to grow hot, to be kindled) and he has to leave the room to weep. The prayer is answered in a body Jacob does not know is his son's. KJV renders 43:30 'his bowels did yearn upon his brother' — genuinely faithful to the physicality, and simply aged into comedy.", (43, 14)),
    ("shalom", "shalom", "שָׁלוֹם", "shalom",
     "PEACE — but far wider than the absence of conflict: wholeness, soundness, welfare, everything being as it should be. You ask after a person's shalom the way English asks 'how are you?'. It runs through the Joseph story as a thread of withholding and return. The brothers 'could not speak to him in SHALOM' (37:4); their father then sent him on the errand that got him sold — 'go, see whether your brothers are at SHALOM' (37:14). The word then disappears for six chapters, until Joseph promises Pharaoh 'God will answer for Pharaoh's SHALOM' (41:16) — and returns in force in ch. 43, where an Egyptian steward greets the terrified brothers with 'SHALOM to you, do not be afraid' (43:23) and Joseph asks three times after their father's shalom (43:27-28). The men who could not say the word are asked it, in Egypt, by the brother they sold.", (37, 4)),
    ("toevah", "to'evah", "תּוֹעֵבָה", "to'evah",
     "An ABOMINATION — something detestable, ritually or socially intolerable to a particular group. Genesis uses it of EGYPTIAN sensibilities, not Israelite ones: 'the Egyptians cannot eat bread with the Hebrews, for that is an abomination to Egypt' (43:32), and later that shepherds are an abomination to them (46:34). The narrator reports the custom flatly, without mockery — and it quietly settles a clause left open at 39:6, where Potiphar 'knew nothing of what he had except the bread he ate.' It also leaves Joseph seated at neither table: not with the Egyptians, not with the Hebrews, eating alone between two peoples.", (43, 32)),
    ("chanan", "chanan", "חָנַן", "yechonkha",
     "To BE GRACIOUS, show favour freely — the root behind chen ('favour') and behind the names Hannah, Hanan, and (through Hebrew Yochanan) JOHN, 'Jehovah has been gracious.' Joseph uses it as a blessing over the little brother he has not seen in twenty-two years and cannot yet claim: 'God be gracious to you, my son' (43:29). It is the last thing he manages to say before his compassion overwhelms him and he leaves the room.", (43, 29)),
    ("melits", "melits", "מֵלִיץ", "melits",
     "An INTERPRETER, go-between, spokesman — from lits, to mediate. It appears in Genesis exactly once, in the quietest and most devastating line of chapter 42: the brothers speak freely in Hebrew in front of the Egyptian governor, confessing to each other that they are guilty of what they did to their brother, 'and they did not know that Joseph was listening, FOR THE INTERPRETER WAS BETWEEN THEM' (42:23). The translator is the disguise. It also tells you what Joseph has been doing for the whole scene: speaking Egyptian, through a third party, to his own family. Elsewhere the word can mean an envoy (2 Chronicles 32:31) or an advocate who speaks for a man before God (Job 33:23).", (42, 23)),
    ("ashem", "ashem", "אָשֵׁם", "ashemim",
     "GUILTY — culpable, liable, bearing the fault; the root behind asham, the guilt-offering of Leviticus. Not the language of regret but of an unpaid debt. It carries the brothers' confession in a foreign cell twenty-two years after the fact: 'truly we are GUILTY concerning our brother — that we saw the distress of his soul when he pleaded with us, and we did not listen' (42:21). Note what that sentence reveals: Genesis never told us, back at the pit (37:24), that Joseph begged. The narrator withheld it for five chapters so the reader would hear it for the first time in the mouths of the men who ignored it. KJV 'we are verily guilty concerning our brother.'", (42, 21)),
    ("chartummim", "chartummim", "חַרְטֻמִּים", "chartummim",
     "The Egyptian LECTOR-PRIESTS — not 'magicians' in the conjuring sense but the literate temple specialists who kept the ritual books and, among much else, interpreted dreams. Pharaoh summons them and they cannot read his dream (41:8, 24). This was a real profession with real manuals: the Dream Book of Papyrus Chester Beatty III lists dreams in columns beside standard readings. The narrator is not sneering at Egyptian learning; he is making a narrower claim — that this dream is not in the reference books. The word is itself probably an Egyptian loanword, and it travels: the SAME term turns up in another empire's court, where Babylon's experts likewise fail in front of a Hebrew captive (Daniel 1:20; 2:2), and again against Moses (Exodus 7:11). KJV 'magicians'; NWT 'magic-practicing priests' — clumsier English, closer to the institution.", (41, 8)),
    ("abrekh", "abrekh", "אַבְרֵךְ", "abrekh",
     "The herald's cry before Joseph's chariot (41:43) — and nobody knows what it means. Three serious proposals: a Hebrew derivation from barakh, 'to kneel,' giving the KJV's and ASV's committed 'BOW THE KNEE'; an Egyptian derivation (ib-r-k, roughly 'attention!', or a court title) giving the NIV's 'MAKE WAY!'; and the Akkadian abarakku, a high household steward. The NWT simply transliterates, and so does this translation — a shout in a foreign court that two thousand years of scholarship has not decoded should look like what it is. One of the small honest pleasures of the Hebrew Bible: a word can survive perfectly intact and completely opaque.", (41, 43)),
    ("nasa-rosh", "nasa rosh", "נָשָׂא רֹאשׁ", "yissa rosh",
     "To LIFT UP THE HEAD — a court idiom for singling a man out of the crowd: to review him, reckon him, take notice of him, raise him up. It is also the hinge on which Genesis 40 turns. Joseph tells the cupbearer 'Pharaoh will LIFT UP YOUR HEAD and restore you' (40:13) — pardon and promotion. He tells the baker 'Pharaoh will LIFT UP YOUR HEAD — from off you — and hang you on a tree' (40:19): the same phrase, two words added, and it means decapitation. Then verse 20 uses it once, governing both men at once — Pharaoh 'lifted up the head' of the cupbearer AND the head of the baker at his birthday feast, one back to his cup and one off his shoulders. KJV and ASV keep it literal in all three places and so preserve the wordplay; versions that smooth it to 'summoned' or 'sent for' destroy the architecture of the chapter. Elsewhere the same idiom means taking a census (Exodus 30:12, 'when you lift up the head of the sons of Israel').", (40, 13)),
    ("pitron", "pitron", "פִּתְרוֹן", "pitron",
     "An INTERPRETATION — specifically of a dream, and the word is almost confined to the Joseph story (with its Aramaic cousin pesher in Daniel and at Qumran). Egypt had a professional dream-reading industry, with reference manuals: the Dream Book of Papyrus Chester Beatty III lists dreams in columns beside standard readings. So when the two imprisoned officials complain that 'there is no one to INTERPRET' (40:8), they mean no specialist — they are in jail, cut off from the professionals. Joseph's answer sidesteps the whole trade: 'Do not INTERPRETATIONS belong to God?' He does not claim the gift; he assigns it upward, then asks to hear the dream. He says it again in front of Pharaoh — 'it is not in me' (41:16).", (40, 8)),
    ("bor", "bor", "בּוֹר", "bor",
     "A PIT or cistern — a bottle-shaped cut in the rock for collecting rainwater, smooth-sided and impossible to climb out of, which is why an empty one makes such an efficient prison. It is the hole Joseph's brothers threw him into at Dothan ('and the pit was empty; there was no water in it,' 37:24) — and it is the word Joseph himself uses of his Egyptian jail: 'here too I have done nothing that they should put me in the PIT' (40:15). ⚠️ The KJV, ASV and NIV all read 'dungeon' in 40:15 while reading 'pit' in 37:24, so an English reader cannot hear that Joseph is describing his cell with the same word he would use for that hole in the ground. This translation renders both 'pit.' Jeremiah is later lowered into one with mud at the bottom (Jeremiah 38:6).", (40, 15)),
    ("zakhar", "zakhar", "זָכַר", "zakhar",
     "To REMEMBER — and in Hebrew never merely 'to recall.' It means to act on behalf of, to take up someone's cause, and in Genesis it is the covenant verb: 'God REMEMBERED Noah' and the waters went down (8:1); 'God REMEMBERED Abraham' and Lot was pulled out of the overthrow (19:29); 'God REMEMBERED Rachel' and Joseph was born (30:22). Every time God remembers someone in this book, a rescue follows. Which is what makes Genesis 40 land: Joseph asks a man to remember him (40:14), and the chapter's last verse is 'the chief of the cupbearers did not REMEMBER Joseph — and he forgot him' (40:23). The verb is put in human hands with a favour attached, and it fails. Two years later the same man's first words are 'I REMEMBER my faults today' (41:9).", (40, 23)),
    ("mashqeh", "mashqeh", "מַשְׁקֶה", "mashqeh",
     "A CUPBEARER — literally 'one who gives drink.' The KJV's 'butler' has shrunk over four centuries into a comic figure in a tailcoat; the office was enormous. A king's cupbearer tasted what the king swallowed, so he was chosen for loyalty above almost anyone at court and stood nearer the royal ear than most ministers. Nehemiah holds the post under the king of Persia and uses a single unhappy expression to get imperial policy changed (Nehemiah 1-2). The man in Genesis 40 is 'chief of the cupbearers,' a saris of Pharaoh's court — and the one person positioned to say Joseph's name to a king.", (40, 1)),
    ("tsalach", "tsalach", "צָלַח", "matsliach",
     "To SUCCEED, prosper, be made to go well. Genesis 39 uses it as the drumbeat of Joseph's slavery — 'Jehovah was with Joseph, and he became a man who PROSPERED' (39:2), 'Jehovah made everything he did PROSPER in his hand' (39:3), and again in the jail at 39:23. The discomfort is deliberate and belongs to the Hebrew, not the English: the man being described is somebody's property in v. 2 and a prisoner by v. 20. Whatever the word promises, it plainly is not that things are pleasant or that he gets what he wants. KJV 'a prosperous man'; NWT 'a successful man.'", (39, 2)),
    ("yabam", "yabbem", "יַבֵּם", "yabbem",
     "To DO THE DUTY OF A BROTHER-IN-LAW — one Hebrew verb, built from yabam, 'a husband's brother.' When a man died childless his brother was to marry the widow, and their first son counted as the dead man's, so his name was not blotted out and the widow was not left destitute (38:8). Genesis shows the custom already operating two centuries before Deuteronomy 25:5-10 writes it into law — including the shaming ceremony for a brother who refuses. Everything in Genesis 38 turns on that refusal: Onan takes the marriage and withholds the duty, and Judah then withholds Shelah. The institution drives the whole book of Ruth, where Boaz performs the nearer kinsman's declined obligation. KJV 'perform the duty of an husband's brother unto her'; NWT 'perform brother-in-law marriage with her.'", (38, 8)),
    ("zonah", "zonah", "זוֹנָה", "zonah",
     "A PROSTITUTE — the plain, ordinary word (from zanah, to be unfaithful, to whore), used both literally and, all through the prophets, as the standing metaphor for Israel's unfaithfulness. It is what the narrator says Judah took Tamar to be (38:15) — and pointedly NOT the word his friend Hirah uses in public two verses later; see qedeshah. KJV 'harlot' for both, which loses the difference entirely.", (38, 15)),
    ("qedeshah", "qedeshah", "קְדֵשָׁה", "qedeshah",
     "A CONSECRATED WOMAN — from qadosh, 'holy,' the same root as sanctuary and saint. Traditionally understood as a cult or shrine prostitute attached to a temple, though the evidence outside the Bible is thinner and more disputed than confident commentaries admit, and some scholars doubt the institution existed in the form usually described. What is beyond dispute is the social register in Genesis 38: the narrator calls the veiled woman a zonah, a common prostitute (38:15), but when Hirah has to ask the locals for directions on his friend's behalf he says qedeshah (38:21) — the dignified term. The shelf splits four ways: KJV flattens both to 'harlot'; NIV 'shrine prostitute' and NWT 'temple prostitute' commit to the cultic reading; ASV keeps a distinction and flags the Hebrew in the margin. This translation renders 'consecrated woman' — near what the word says, without settling an institution the evidence won't settle.", (38, 21)),
    ("tsadaq", "tsadaq", "צָדַק", "tsadqah",
     "To BE IN THE RIGHT, be righteous — the root of tsedaqah, 'righteousness,' the noun 'counted' to Abram when he believed (15:6). Its most startling appearance is Judah's confession: tsadqah mimmenni, 'she is more righteous than I' (38:26) — the comparative form, spoken in public by a patriarch about the Canaanite widow who tricked him, and the first honest sentence he speaks in the Bible. The same root gives Noah his description ('a righteous man,' 6:9) and Abraham his argument at Sodom ('will you sweep away the righteous with the wicked?', 18:23).", (38, 26)),
    ("perets", "perets", "פֶּרֶץ", "perets",
     "A BREACH — a gap burst through a wall; from parats, to break out. The midwife's cry at the birth of Judah's twin is a pun on the name she is giving him: 'How you have BROKEN OUT (paratsta) — a breach (perets) upon you!' (38:29). It sounds like dismay and is kept as a name. Perez matters far past this chapter: Ruth closes by tracing 'the generations of Perez' ten names down to DAVID (Ruth 4:18-22), and Matthew opens the New Testament with the same line, naming 'Perez and Zerah by Tamar' (Matthew 1:3). KJV spells him Pharez, Douay (through the Greek) Phares.", (38, 29)),
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
     "The BLESSING — from barak, 'to bless' (and 'to kneel'), the thing the whole chapter is fought over. In Genesis a father's deathbed blessing is not a fond wish but a PERFORMATIVE, near-irrevocable word: once spoken it takes effect and cannot be recalled — 'I have blessed him; yes, and he will be blessed' (27:33). It carries the covenant itself (dew and fatness, dominion, and Abraham's own 'cursed be those who curse you,' 12:3). Jacob steals Esau's berakhah as he had bought his bekhorah (birthright); Esau's cry 'have you but one blessing?' (27:38) is the anguish of a word that cannot be unsaid. Hebrews 12:17 makes him the man who 'found no place for repentance, though he sought it with tears.' Twenty years later Jacob tries to give one back: pressing his gift on Esau at their reunion, he calls it not a 'present' but 'my berakhah, my BLESSING, that is brought to you' (33:11) — a deliberate, quiet restitution of the very thing he stole.", (27, 4)),
    ("matamim", "mat'ammim", "מַטְעַמִּים", "mat'ammim",
     "SAVORY FOOD — 'tasty things,' a delicacy (from ta'am, 'taste'): the dish of game Isaac craves and the disguise Rebekah cooks from two kids to fool him (27:4, 9, 31). KJV 'savoury meat'; NWT 'a tasty dish.' A small, human detail — the old blind man's love of a favorite meal — turned into the very instrument of the deception; the taste that was meant to confirm his son is the taste that helps steal the blessing.", (27, 4)),
    ("mirmah", "mirmah", "מִרְמָה", "mirmah",
     "DECEIT, treachery — 'your brother came with mirmah and took your blessing' (27:35; KJV 'subtilty,' NWT 'deception'). It becomes a thread running through Jacob's whole life, the deceiver repeatedly deceived: he cheats Esau with mirmah here, and Laban will cheat HIM ('why have you deceived me?', Leah for Rachel, 29:25); his sons answer Shechem 'with mirmah' and turn it into the slaughter of a whole city over their sister (34:13); and those same sons will one day deceive Jacob himself with Joseph's blood-dipped coat (37:31-33). The man named 'supplanter' (Ya'aqov) traffics in mirmah until God wrestles a new name out of him — Israel; the true Israelite, John's Gospel will later say, is the one 'in whom is no mirmah / deceit' (John 1:47).", (27, 35)),
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
    # ---- Genesis 31 (Hebrew) ----
    ("ganav", "ganav", "גָּנַב", "ganav",
     "To STEAL — the verb that rings through Jacob's flight like an alarm. Rachel ganav-steals her father's teraphim (31:19); Jacob ganav-steals 'the HEART' of Laban (31:20) — ganav lev, the Hebrew idiom for hoodwinking, deceiving someone (Absalom later 'steals the heart' of Israel, 2 Samuel 15:6); and Laban throws the word back three times ('you stole my heart… you stole from me… why did you steal my gods?', 31:26-30). The supplanter's whole household turns out to be a household of thieves. It is the plainest word behind the eighth commandment, 'you shall not steal' (Exodus 20:15).", (31, 20)),
    ("teraphim", "teraphim", "תְּרָפִים", "teraphim",
     "Household GODS — small domestic idols or figurines (KJV 'images'), used for luck and divination and, in the customs of that world, apparently bound up with family inheritance rights. Rachel steals her father's teraphim as she leaves (31:19), and why she wanted them the text leaves open: to press the inheritance Laban denied her (v. 14), for their supposed protection, or — the rabbis' kinder guess — to wean her father off idolatry. She hides them in the camel's saddle and sits on them, and 'the gods of Laban' end up sat upon (31:34). The word recurs across the Bible as a mark of forbidden worship — in Micah's shrine (Judges 17-18), in Michal's bed-decoy for David (1 Samuel 19:13), and among the idolatries Josiah purges (2 Kings 23:24).", (31, 19)),
    ("pachad-yitzchak", "Pachad Yitzchak", "פַּחַד יִצְחָק", "pachad Yitzchak",
     "'The FEAR of Isaac' — a rare divine title, found only in this chapter (31:42, 53): the God of Isaac named by the awe he inspires, 'the Awe-inspiring One whom Isaac reveres,' set beside 'the God of Abraham.' Pachad is dread, trembling reverence; some render it 'the Kinsman/Refuge of Isaac,' but the plain sense is the fear-of-God as a name for God himself. It is how Jacob distinguishes the true God of his fathers from 'the God of Nahor' that Laban swears by in the same breath (31:53) — the family's religion visibly dividing.", (31, 42)),
    # ---- Genesis 32 (Hebrew) ----
    ("qatonti", "qatonti", "קָטֹנְתִּי", "qatonti",
     "'I am too SMALL' — literally 'I have become small' (from qaton, 'to be little'), Jacob's word at the head of his prayer: 'I am too small for all the kindness (chesed) and all the faithfulness you have shown your servant' (32:11; KJV 'I am not worthy'). It is the great reversal of his life spoken in one word: the man who spent every year grasping to be GREAT — who has just become 'two camps' of wealth — confesses himself little before God, remembering that he once crossed the Jordan with nothing but a walking-stick. Humility named exactly, not by self-hatred but by measuring oneself against undeserved grace.", (32, 11)),
    ("israel", "Yisrael", "יִשְׂרָאֵל", "Yisrael",
     "'He STRIVES with God' (or 'God strives / God rules') — the new name wrestled out of Jacob at the Jabbok: 'no longer Jacob, but Israel, for you have striven (sarita, from sarah, 'to strive, struggle, persist') with God and with men, and have prevailed' (32:29). It answers 'Jacob' ('heel-grabber, supplanter'): the man who always grasped by cunning now prevails by HOLDING ON — refusing, though crippled, to let go without a blessing. The name is re-confirmed at Bethel (35:10) and becomes the name of the whole nation, the 'children of Israel' — a people named not for a triumph but for a night-long, limping struggle with God that would not quit.", (32, 29)),
    ("gid-hanasheh", "gid ha-nasheh", "גִּיד הַנָּשֶׁה", "gid ha-nasheh",
     "'The SINEW of the nasheh' — the thigh-tendon (traditionally the sciatic nerve) that the wrestling angel touched, leaving Jacob limping (32:26, 33). Because of that night, 'the children of Israel do not eat the sinew of the thigh, to this day' — an observance kept in kosher law ever since (the nerve and its branches are removed from an animal's hindquarters, or the hindquarters not eaten at all). It is the one dietary custom Genesis itself explains, a scar of memory worked into the daily table: every meal recalls the night their father was crippled and crowned at once.", (32, 33)),
    # ---- Genesis 33 (Hebrew) ----
    ("kesitah", "kesitah", "קְשִׂיטָה", "kesitah",
     "An archaic unit of MONEY or weight — Jacob buys the field at Shechem 'for a hundred kesitah' (33:19; KJV 'pieces of money'). Its exact value is unknown; the word survives in only three places in the whole Bible (here, Joshua 24:32, and Job 42:11), a sign of its great age — later Hebrew had long since replaced it with the shekel. The Septuagint and rabbis guessed it was worth a lamb (some ancient coins were stamped with a lamb), so it may have meant 'a lamb's-worth' of silver. This translation keeps the old word untranslated rather than smoothing it into 'coins,' which would be an anachronism — coinage proper came a thousand years later.", (33, 19)),
    ("el-elohe-israel", "El-Elohe-Israel", "אֵל אֱלֹהֵי יִשְׂרָאֵל", "El Elohe Yisrael",
     "'El, the God of Israel' — the name Jacob gives the altar he builds at Shechem (33:20), the fifth of the great EL-landmark names of Genesis (after El Elyon at Salem, 14:18; El Roi at Hagar's well, 16:13; El Shaddai at the covenant, 17:1; and El Olam at Beersheba, 21:33). It is the first time Jacob claims the God of his fathers under his OWN new name — Israel — folding the name the angel just gave him (32:29) into a confession of faith: the vow he made fleeing the land, 'then Jehovah shall be my God' (28:21), made good at an altar on the ground he has just bought.", (33, 20)),
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
    ("parthenos", "parthenos", "παρθένος", "parthenos",
     "VIRGIN — a young woman who has not known a man. In Luke 1:27 Mary is twice called PARTHENOS; in 1:34 she says plainly, 'since I do not know a man.' The Greek Old Testament used this same word to render Isaiah 7:14 ('a PARTHENOS shall conceive'), the verse Matthew 1:23 applies to this birth — where the Hebrew ALMAH means a young woman of marriageable age without BETULAH's technical focus on virginity. Luke's Greek settles what Isaiah's Hebrew left open.", ("Luke", 1, 27)),
    ("doule", "doule", "δούλη", "doule",
     "BONDSLAVE (female) — the strongest word for a slave, not merely a servant. Mary answers Gabriel, 'Behold, the DOULE of the Lord' (1:38), and sings that God looked on 'the low estate of his DOULE' (1:48). It is a word of total belonging, and she chooses it for herself: her assent, 'may it happen to me according to your word,' is a slave's yes to a master — and the pivot of the chapter, set against the priest Zechariah who could only be struck dumb.", ("Luke", 1, 38)),
    ("tapeinosis", "tapeinosis", "ταπείνωσις", "tapeinosis",
     "LOW ESTATE, lowliness, humiliation — a lowly CONDITION, not humility as a virtue. In the Magnificat God 'looked on the TAPEINOSIS of his bondslave' (1:48), the very word Hannah's Greek song uses (1 Samuel 1:11). Luke's point is that God NOTICES the low place and then reverses it; the song spells the reversal out — rulers pulled down, the lowly lifted, the hungry filled, the rich sent empty away.", ("Luke", 1, 48)),
    ("anatole", "anatole", "ἀνατολή", "anatole",
     "RISING / DAWN — and, in the Greek Old Testament, the messianic BRANCH. Zechariah's song says 'the ANATOLE from on high will visit us' (1:78). The word means the rising of the sun (light dawning on those in darkness, Isaiah 9:2) AND the 'Branch/shoot' promised to spring from David (Jeremiah 23:5; Zechariah 3:8; 6:12, where the Greek Bible uses this very word). Zechariah's ears would catch both at once: a sunrise and a sprouting Branch. ⚠️ No single English word holds both, so the versions split — 'dayspring' (KJV), 'sunrise' (ESV), 'daybreak' (NWT).", ("Luke", 1, 78)),
    ("dabaq", "davaq", "דָּבַק", "davaq",
     "TO CLING, cleave, stick fast — the verb of Genesis 2:24, where a man 'clings' to his wife and the two become one flesh. In Ruth 1:14 it is used of RUTH clinging to Naomi where Orpah kisses and leaves: Ruth's loyalty to her mother-in-law is written in marriage language, a woman cleaving as a spouse cleaves. The same root is used of Israel commanded to 'cling' to Jehovah (Deuteronomy 10:20).", ("Ruth", 1, 14)),
    ("menuchah", "menuchah", "מְנוּחָה", "menuchah",
     "REST — a settled security, a place to come to rest. Naomi prays Jehovah give her daughters-in-law MENUCHAH and spells out what she means, 'in the house of her husband' (Ruth 1:9): the safety of a home and marriage. It is the one thing the widowed, landless Naomi cannot provide, and the very thing the whole book circles back to give Ruth through Boaz (3:1, 'shall I not seek REST for you?'). The same root gives the Psalm's 'still waters,' literally 'waters of rest' (Psalm 23:2).", ("Ruth", 1, 9)),
    ("mara", "mara", "מָרָא", "mara",
     "BITTER — the name Naomi gives herself on her return: 'Do not call me Naomi [sweet]; call me MARA, for the Almighty has dealt very bitterly (hemar) with me' (Ruth 1:20). The pun turns her own name inside out. The same root marks the 'bitter' waters of Marah in the wilderness (Exodus 15:23) and the 'bitter herbs' of the Passover (Exodus 12:8). ⚠️ Naomi is wrong that she is empty — Ruth stands beside her — but the book lets her name her grief honestly before it answers it.", ("Ruth", 1, 20)),
    ("despotes", "despotes", "δεσπότης", "despotes",
     "MASTER, sovereign owner — the master of a household SLAVE (our 'despot'), a stronger, more possessive word than the ordinary 'lord' (kyrios). Jude calls himself a 'slave (doulos) of Jesus Christ' (1:1), then charges the intruders with denying 'our only DESPOTES and Lord, Jesus Christ' (1:4): runaway slaves disowning the one who owns them. The same title is given to the Sovereign Lord in Simeon's song (Luke 2:29) and the martyrs' cry (Revelation 6:10).", ("Jude", 1, 4)),
    ("aselgeia", "aselgeia", "ἀσέλγεια", "aselgeia",
     "LICENTIOUSNESS, unrestrained indecency — sensuality with no shame or brake, flaunted rather than hidden. Jude's charge is exact: the false teachers 'turn the grace of our God into ASELGEIA' (1:4), making forgiveness a licence and grace an excuse for the very thing it saves from. It heads Paul's works-of-the-flesh (Galatians 5:19) and names the old life's abandon (1 Peter 4:3).", ("Jude", 1, 4)),
    ("hapax", "hapax", "ἅπαξ", "hapax",
     "ONCE, once for all — a single decisive time, not to be repeated. It is the hinge of Jude's appeal: contend for 'the faith HAPAX delivered to the holy ones' (1:3) — handed over ONCE, complete, not to be revised, added to, or traded. The same word carries the weight of Hebrews' 'once for all' sacrifice of Christ (Hebrews 9:26-28; 10:10): what is done hapax cannot be undone.", ("Jude", 1, 3)),
    ("spilas", "spilas", "σπιλάς", "spilas",
     "A HIDDEN REEF (plural spilades) — a rock just under the surface that tears the hull out of a ship that never saw it. Jude's image for the intruders 'in your love-feasts' (1:12): they sit at the common table and wreck the church from below, unseen. ⚠️ A near-identical word, spilos ('spot, blemish'), stands behind the parallel in 2 Peter 2:13, and some render Jude's word 'blemishes' — but the seafaring 'reef' suits his storm of sea-images (waves, wandering stars) and is kept here.", ("Jude", 1, 12)),
    ("yatsar", "yatsar", "יָצַר", "yatsar",
     "TO FORM, shape, fashion — the potter's verb. It is the word for God forming the man from the dust of the ground (Genesis 2:7), and it opens Jeremiah's call: 'before I FORMED you in the belly I knew you' (1:5). Jeremiah later turns it into a whole sign-act at the potter's house, where the clay marred in the potter's hand is reshaped (ch 18) — the nation as clay under a hand that can make and unmake. The related noun yetser is the 'inclination' formed in the human heart.", ("Jeremiah", 1, 5)),
    ("shaqed", "shaqed / shoqed", "שָׁקֵד / שֹׁקֵד", "shaqed / shoqed",
     "ALMOND — and, one letter's sound away, WATCHING. Jeremiah sees 'a branch of an almond tree' (SHAQED), and God answers, 'you have seen well, for I am WATCHING (SHOQED) over my word to do it' (1:11-12). The almond is the first tree to wake and blossom in the Judean spring — the 'wakeful' or 'watcher' tree — so the pun makes the vision mean God is AWAKE over his word, watching to perform it. ⚠️ The wordplay cannot fully cross into English; the KJV reads the root as speed ('I will hasten my word'), most modern versions as watchfulness.", ("Jeremiah", 1, 11)),
    ("naar", "na'ar", "נַעַר", "na'ar",
     "A YOUTH, boy, young man — also a servant or attendant. Jeremiah objects to his call with it: 'I do not know how to speak, for I am only a NA'AR' (1:6), the reluctant-prophet's plea of inadequacy (compare Moses, Gideon, Isaiah). God does not dispute the youth; he answers 'do not say I am a youth' and sends him anyway. The same word covers a wide span of age and status — the infant Moses in the ark, the lad Isaac on Moriah, a king's servant.", ("Jeremiah", 1, 6)),
    ("chatat", "chatat", "חָתַת", "chatat",
     "TO BE SHATTERED, dismayed, broken with terror. In Jeremiah's charge it is a warning built on a pun: 'do not be SHATTERED (chatat) before them, lest I SHATTER (achittekha) you before them' (1:17) — fear the people and God himself will break you; the only safety is obedience. The same root sounds through the prophets for the panic of armies and the collapse of courage; its opposite is the steadiness of the one who trusts.", ("Jeremiah", 1, 17)),
    ("raz", "raz", "רָז", "raz",
     "MYSTERY, secret — an Aramaic word borrowed from Persian, the theme-word of Daniel 2, where it sounds eight times: Nebuchadnezzar's dream is a RAZ that only 'a God in heaven who reveals mysteries' can disclose (2:28). It names not a puzzle to be solved by cleverness but a hidden thing that must be REVEALED from above. ⚠️ The word travels: the Greek Bible and then the New Testament render it MYSTERION — Paul's 'mystery' of the gospel, once hidden and now made known (Romans 16:25; Ephesians 3:3-6), is Daniel's RAZ.", ("Daniel", 2, 18)),
    ("pesher", "pishra / pesher", "פִּשְׁרָא", "pishra / pesher",
     "INTERPRETATION — the Aramaic word for the meaning of a dream, sign, or oracle, paired all through Daniel with RAZ (mystery): the king demands both the dream and its PISHRA (2:6). It is the same root as the Hebrew PESHER that names the Dead Sea Scrolls' running commentaries ('the PESHER of this is…'), a whole Jewish way of reading in which a text's true meaning is a disclosed secret. In Daniel the interpretation is never the interpreter's ingenuity; it is given by God.", ("Daniel", 2, 4)),
    ("malku", "malku", "מַלְכוּ", "malku",
     "KINGDOM, kingship, reign — the Aramaic word that governs Daniel 2 and 7. It is kept the same across the four earthly MALKU (Babylon and the three that follow) and the everlasting fifth that 'the God of heaven shall set up… which shall never be destroyed' (2:44). The book's whole argument is a contest of kingdoms: the towering, brittle empires of the statue against the stone-become-mountain, the 'kingdom of God' that grinds them to chaff and fills the earth.", ("Daniel", 2, 44)),
    ("shaal", "sha'al", "שָׁאַל", "sha'al",
     "TO ASK, request — and, in a special sense, to LEND or give on loan. The verb generates the whole naming of 1 Samuel: Hannah 'ASKED' Samuel of Jehovah (1:20), and then 'LENT' him back — 'he is SHA'UL (lent/asked) to Jehovah' (1:28). ⚠️ The narrator's folk-etymology links the name SAMUEL to sha'al, though the name more likely means 'name of God' or 'God has heard'; and the wordplay reaches past Samuel to SAUL (Sha'ul, 'the asked-for one'), the king a people will 'ask' for (ch 8). One root quietly names the prophet, the gift, and the whole book's theme.", ("1 Samuel", 1, 20)),
    ("tzevaot", "tzeva'ot", "צְבָאוֹת", "tzeva'ot",
     "HOSTS, armies — the plural in the divine title YHWH TZEVA'OT, 'Jehovah of hosts' (or 'of armies'), which makes its FIRST appearance in the Bible at 1 Samuel 1:3, on the lips of Elkanah's family at Shiloh. The 'hosts' are the armies of heaven and earth, the whole marshaled power of creation, of which Jehovah is commander. The title then rings through the prophets and the Psalms as the name of the God who fights for his people — and it enters, fittingly, at a sanctuary, in an act of worship.", ("1 Samuel", 1, 3)),
    ("neder", "neder", "נֶדֶר", "neder",
     "A VOW — a binding promise made to God, often conditional ('if you will… then I will'). Hannah 'vowed a vow' (nadrah neder, 1:11): if Jehovah gives her a son she will give him back for life. The Law treats a vow with the utmost seriousness — 'when you make a vow to God, do not delay to fulfill it' (Deuteronomy 23:21; Ecclesiastes 5:4) — and Hannah keeps hers to the letter, carrying the weaned child to Shiloh and leaving him there.", ("1 Samuel", 1, 11)),
    ("nazir", "nazir", "נָזִיר", "nazir",
     "A NAZIRITE — one 'separated,' set apart to God by a vow, marked by abstaining from wine, avoiding corpse-defilement, and above all letting the hair grow uncut: 'no razor shall touch his head' (the sign Hannah pledges for Samuel, 1:11, and the mark of Samson, Judges 13). The full law is in Numbers 6. Usually a temporary vow, it is here a LIFELONG dedication from before birth — Samuel, like Samson, is given to God for the whole of his life.", ("1 Samuel", 1, 11)),
    ("ot", "ot / otot", "אוֹת / אֹתוֹת", "ot / otot",
     "A SIGN — a mark, token, or wonder that points beyond itself to authenticate a word or a promise. God gives Moses three OTOT to make Israel believe (Exodus 4:8-9): the staff-serpent, the leprous hand, the water-to-blood. The word runs from the rainbow, the 'sign' of the covenant with Noah (Genesis 9:12), and the sabbath, the 'sign' between God and Israel, to the plagues and the great 'signs and wonders' of the Exodus. A sign is not the point; it is a finger pointing at the one who gives it.", ("Exodus", 4, 8)),
    ("chazak", "chazaq", "חָזַק", "chazaq",
     "TO BE STRONG, to STRENGTHEN — and, of a heart, to HARDEN, make firm and unyielding. It opens the Exodus's hardest theological thread: 'I will HARDEN (chazaq) his heart, and he will not let the people go' (4:21). Across the plagues the book says both that JEHOVAH hardened Pharaoh's heart and that PHARAOH hardened his own (and uses two other verbs, kavad 'made heavy' and qashah 'made stubborn', alongside this one). Scripture holds the divine and the human hardening together without resolving them; the translation keeps the strong verb rather than softening it.", ("Exodus", 4, 21)),
    ("bekhor", "bekhor", "בְּכוֹר", "bekhor",
     "FIRSTBORN — the eldest son, who by right held the birthright, a double inheritance, and the family headship. Genesis is full of the firstborn displaced (Ishmael, Esau, Reuben); Exodus makes the firstborn a matter of life and death. God claims Israel itself as his BEKHOR — 'Israel is my firstborn son' (4:22), a claim of covenant sonship — and the conflict with Pharaoh becomes a contest over sons, climaxing when 'every firstborn in Egypt' is struck and Israel's firstborn are spared by blood (ch 12), after which every firstborn of Israel belongs to Jehovah.", ("Exodus", 4, 22)),
    ("chatan", "chatan damim", "חֲתַן דָּמִים", "chatan damim",
     "'BRIDEGROOM (or son-in-law) OF BLOOD' — the cryptic phrase Zipporah speaks at the terrifying night-lodging scene, cutting off her son's foreskin with a flint and touching it to 'his feet': 'surely you are a CHATAN DAMIM to me' (4:25-26). ⚠️ One of the most obscure expressions in the Hebrew Bible: chatan is 'bridegroom / son-in-law' (from the root for marriage-by-blood-tie), damim is 'blood' (plural, often of bloodshed); who is addressed, and what the phrase means, are genuinely uncertain. The likeliest sense ties it to the covenant blood of circumcision (Genesis 17) that averts the death Moses' household faced.", ("Exodus", 4, 25)),
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
              "Mounts Ebal and Gerizim. Site of the first land-promise and Abram's first altar (12:7). Jacob returns "
              "generations later, camps 'in peace' before the city and buys a field from the sons of Hamor (33:18-19) — "
              "but it is also where his daughter Dinah is violated by the town's prince (who bears the city's own name, "
              "Shechem son of Hamor), and where Simeon and Levi answer with the massacre of the whole city (ch. 34). It "
              "keeps echoing: Joseph's bones are buried in that same field (Joshua 24:32), Joshua gathers Israel here for "
              "the covenant renewal and sets up the great witness-stone (Joshua 24), and it becomes the first capital of "
              "the northern kingdom (1 Kings 12).",
         refs=[(12, 6), (12, 7), (33, 18), (34, 2)],
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
         refs=[(12, 8), (28, 19), (35, 7)],
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
              "later be his home (24:62; 25:11). He dies at 180, 'old and full of days,' at Hebron, and is buried in "
              "the cave of Machpelah by his two sons — Esau and Jacob together (35:27-29).",
         refs=[(17, 19), (17, 21), (21, 3), (21, 5), (21, 10), (22, 2), (22, 9), (25, 11), (25, 19), (25, 21), (26, 1), (26, 12), (26, 24), (27, 1), (27, 22), (28, 1), (35, 27), (35, 29)], videos=[]),

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
              "argued in our own time most carefully — and, in this project's judgement, least tendentiously — by JOEL "
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
         refs=[(30, 24), (33, 2), (37, 2), (37, 3), (37, 23), (37, 28),
               ("Exodus", 1, 5), ("Exodus", 1, 6), ("Exodus", 1, 8)], videos=[]),

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
         refs=[(29, 35), (37, 26), (37, 27), ("Numbers", 1, 7), ("Numbers", 1, 26)], videos=[]),
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
         refs=[(24, 29), (24, 50), (27, 43), (28, 2), (28, 5), (29, 5), (29, 13), (29, 25), (30, 27), (31, 2)], videos=[]),
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
         refs=[(29, 16), (29, 23), (29, 31), (30, 9), (31, 4), (33, 2)], videos=[]),
    dict(slug="dinah", name="Dinah", kind="person", aliases=["Dinah"],
         desc="Jacob and Leah's daughter — the one daughter the family record names, and the still center of Genesis 34's "
              "storm. She 'goes out to see the daughters of the land' and is seized and violated by Shechem, the prince of "
              "the town (34:2); her full brothers Simeon and Levi answer by putting the whole city to the sword. Through the "
              "entire chapter Dinah never speaks and is never asked — the men negotiate, deceive, and kill over her in "
              "silence, and the narrator lets that silence indict them. Her name (from din, 'judgment') hangs over a chapter "
              "that withholds its verdict until Jacob's deathbed curse of her avengers (49:5-7). She is listed among those "
              "who go down to Egypt (46:15), then passes from the story.",
         refs=[(34, 1), (34, 2), (34, 3), (34, 25)], videos=[]),
    dict(slug="hamor", name="Hamor", kind="person", aliases=["Hamor"],
         desc="The Hivite ruler of Shechem and father of the prince Shechem — the name means 'donkey.' He comes to Jacob "
              "as a smooth negotiator, proposing that the two peoples intermarry, trade, and 'become one people' (34:8-10), "
              "and sells the bargain to his own townsmen not by appeal to justice but to greed: 'their livestock and "
              "property — will they not be ours?' (34:23). He and his son are the first to fall to Simeon and Levi's swords "
              "(34:26). Long after, Jacob's purchase of a field 'from the sons of Hamor' (33:19) becomes Joseph's grave "
              "(Joshua 24:32) — the one patch of Shechem that stays Israel's by right, not by the sword.",
         refs=[(34, 2), (34, 6), (34, 20), (34, 26)], videos=[]),
    dict(slug="simeon", name="Simeon", kind="person", aliases=["Simeon"],
         desc="Jacob and Leah's second son — his name (Shim'on, from shama, 'to hear') is Leah's cry that 'Jehovah heard "
              "that I was hated' (29:33). With his brother Levi he takes the sword at Shechem, avenging their sister Dinah by "
              "slaughtering the town (34:25-31). The violence marks him for life: on his deathbed Jacob does not bless the two "
              "brothers but curses their anger — 'weapons of violence are their swords… I will scatter them in Israel' "
              "(49:5-7). The tribe of Simeon is given no separate territory but is swallowed into Judah's (Joshua 19:1), the "
              "curse working itself out. It is Simeon whom Joseph will later bind and hold hostage in Egypt (42:24).",
         refs=[(29, 33), (34, 25), (34, 30)], videos=[]),
    dict(slug="levi", name="Levi", kind="person", aliases=["Levi"],
         desc="Jacob and Leah's third son — named for her hope that now, with three sons, her husband will be 'joined' "
              "(lavah) to her (29:34). With Simeon he leads the massacre at Shechem (34:25) and shares the same deathbed "
              "curse for it: 'cursed be their anger… I will scatter them in Israel' (49:7). Yet the scattering turns to "
              "grace: Levi's descendants become the priestly tribe, given no land of their own but Jehovah himself as their "
              "portion — dispersed through all Israel's towns precisely as its teachers and priests, the curse of scattering "
              "remade into a vocation. Moses, Aaron, and Miriam are Levites; so is the whole priesthood. The avenger's line "
              "becomes the tribe that stands at the altar.",
         refs=[(29, 34), (34, 25)], videos=[]),
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
         refs=[(29, 6), (29, 18), (29, 30), (30, 1), (31, 4), (33, 2), (35, 16)], videos=[]),
    dict(slug="benjamin", name="Benjamin", kind="person", aliases=["Benjamin", "Ben-oni"],
         desc="Jacob's twelfth and last son, the second of Rachel's — born on the road near Bethlehem as she died in "
              "labor (35:16-18). Her dying name for him was BEN-ONI, 'son of my sorrow'; his father overrode it to "
              "BENJAMIN, 'son of the right hand' (the hand of strength and favor, or 'son of the south') — the only "
              "child in Genesis whose name a parent changes, a father refusing to let his beloved wife's last son "
              "carry her grief for life. The full brother of JOSEPH, he becomes the pledge and pivot of the Joseph "
              "story — the son Jacob cannot bear to send to Egypt, the cup hidden in his sack, the test that breaks "
              "the brothers open (chs. 42-45). His tribe gives Israel its first king, Saul, and the apostle Paul "
              "('of the tribe of Benjamin,' Philippians 3:5); Jacob's deathbed calls him 'a ravenous wolf' (49:27).",
         refs=[(35, 18), (35, 24)], videos=[]),
    dict(slug="bethlehem", name="Bethlehem", kind="place", aliases=["Bethlehem", "Ephrath", "Ephrathah"],
         desc="'House of Bread' (Beit-Lechem) — first named in the Bible here, under its older name Ephrath, when "
              "Rachel dies in childbirth 'on the way to Ephrath, that is Bethlehem' and Jacob marks her grave with a "
              "pillar (35:19-20). A small town six miles south of Jerusalem, it becomes the town of Ruth and Boaz "
              "(Ruth 1-4) and the home and city of DAVID (1 Samuel 16), from which Micah foretells the ruler 'whose "
              "origins are from of old' will come (Micah 5:2) — the prophecy Matthew and Luke set over the birth of "
              "Jesus (Matthew 2; Luke 2). So the wayside where the mother of Israel lies buried, weeping, becomes the "
              "road to the Messiah's cradle.",
         refs=[(35, 19)], videos=[]),
    dict(slug="deborah", name="Deborah", kind="person", aliases=["Deborah", "Allon-bacuth"],
         desc="Rebekah's nurse — a servant who appears twice, both times in silence and both times honored past her "
              "station. She is the unnamed nurse sent along when the young Rebekah leaves home for Isaac (24:59), and "
              "she surfaces once more, now in the aged Jacob's camp, only to die and be buried under an oak below "
              "Bethel that is named for the mourning: ALLON-BACUTH, 'the oak of weeping' (35:8). Rebekah herself gets "
              "no death-scene in Genesis; her old nurse gets a named tree and a page of tears — the Bible pausing "
              "over a life the world would have walked past. (A different Deborah, the prophet-judge, sings Israel's "
              "victory generations later, Judges 4-5.)",
         refs=[(35, 8)], videos=[]),
    dict(slug="reuben", name="Reuben", kind="person", aliases=["Reuben"],
         desc="Jacob and Leah's firstborn — his name (Re'uven) is Leah's cry, 'God has SEEN (ra'ah) my affliction… "
              "now my husband will love me' (29:32). The eldest, forever almost saving the day and falling short: he "
              "brings his mother the mandrakes that reopen the wife-war (30:14), and later he alone tries to spare "
              "Joseph, talking the brothers out of murder so he can rescue him — and returns to an empty pit "
              "(37:21-29). But here he commits the sin that undoes him, lying with Bilhah his father's concubine, a "
              "grab at his father's authority (35:22). For it he loses the birthright: Jacob's deathbed verdict is "
              "'unstable as water, you shall not have the excellency, because you went up to your father's bed' "
              "(49:3-4) — and the double portion passes to Joseph, the leadership to Judah.",
         refs=[(29, 32), (35, 22), (37, 21), (37, 29)], videos=[]),
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
    dict(slug="gilead", name="Gilead", kind="place", aliases=["Gilead", "Galeed", "mountain of Gilead", "hill country of Gilead"],
         desc="The hill country EAST of the Jordan, the highlands where Laban overtook the fleeing Jacob and "
              "the two made their treaty (31:21-54). Genesis derives the name here from the treaty-heap: Jacob "
              "calls it GALEED (gal-ed, 'heap of witness'), and Laban names the same heap in Aramaic, "
              "Jegar-sahadutha — the earliest Aramaic in the Bible — and the name Gilead sticks to the whole "
              "region. It becomes one of Israel's most storied territories: the balm of Gilead, the home of "
              "Jephthah and of the prophet Elijah the Tishbite, the pasture-land of Reuben and Gad, and, at "
              "this treaty-line, the boundary between Jacob's people and the Aramean world he is leaving behind.",
         refs=[(31, 21), (31, 23), (31, 25)],
         coords=(32.31, 35.73, 1.0), approx=True,
         modern="The highlands of northwest Jordan, east of the Jordan River (the Ajlun/Jerash region)"),
    dict(slug="jabbok", name="The Jabbok", kind="place", aliases=["Jabbok", "ford of the Jabbok", "Peniel", "Penuel", "Mahanaim"],
         desc="A deep river-gorge east of the Jordan, a tributary running down to it through Gilead — and the "
              "scene of the most famous night of Jacob's life. Its Hebrew name, YABBOQ, chimes with both "
              "Ya'aqov ('Jacob') and the verb of that night, vayye'aveq, 'and he WRESTLED' (32:23-25): at the "
              "ford of the Jabbok, Jacob wrestles a man until dawn and is renamed Israel. Two other names cluster "
              "at the crossing: just before it he had met the angels and called the place MAHANAIM ('two camps,' "
              "32:2-3), and after the wrestling he named the very spot PENIEL / Penuel, 'the Face of God,' "
              "'for I have seen God face to face, and my life was delivered' (32:31). The river later marks a "
              "boundary of the Ammonites and of the Amorite kingdom of Sihon.",
         refs=[(32, 23), (32, 25), (32, 31)],
         coords=(32.13, 35.68, 1.0), approx=True,
         modern="The Zarqa River, north-central Jordan, flowing west into the Jordan"),
    dict(slug="succoth", name="Succoth", kind="place", aliases=["Succoth"],
         desc="'BOOTHS' — Jacob's first stop after crossing back into the land, west of the Jabbok in the Jordan "
              "valley. Genesis gives the name its own explanation: he 'built himself a house and made booths "
              "(sukkot) for his livestock, therefore the place is named Succoth' (33:17). The word is the same "
              "that names Israel's autumn festival of Sukkot, the Feast of BOOTHS, when the people live a week in "
              "temporary shelters remembering the wilderness. Succoth reappears as a station of the Exodus "
              "(Exodus 12:37) and, in the plain of the Jordan, as a town in the days of Gideon (Judges 8) and "
              "of Solomon's bronze-casting (1 Kings 7:46).",
         refs=[(33, 17)],
         coords=(32.20, 35.61, 0.8), approx=True,
         modern="The Jordan valley east of the river, near the mouth of the Jabbok (northern Jordan)"),

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
         refs=[(25, 25), (25, 30), (25, 34), (26, 34), (27, 34), (27, 41), (28, 6), (32, 4), (33, 4), (36, 1)], videos=[]),
    dict(slug="jacob", name="Jacob (Israel)", kind="person", aliases=["Jacob"],
         desc="The third patriarch, and the one the nation is named for — born gripping his twin's HEEL (aqev), so "
              "called YA'AQOV, 'heel-holder,' a name that becomes a byword for the supplanter who trips and "
              "overreaches (25:26; 27:36). He buys Esau's birthright for stew, steals Esau's blessing with his "
              "mother's help, and flees to Laban in the old country — where he is out-tricked in turn (Leah for "
              "Rachel) and fathers eleven sons and a daughter over twenty hard years. Wrestling a stranger at the "
              "Jabbok, he is renamed ISRAEL, 'he strives with God' (32:28); his twelve sons become the twelve "
              "tribes. A flawed, grasping, unforgettable man whom God chooses anyway — 'the God of Abraham, Isaac, "
              "and Jacob' — and whose story fills the rest of Genesis (chs. 25–50).",
         refs=[(25, 26), (25, 27), (25, 31), (27, 19), (27, 36), (28, 10), (28, 16), (29, 10), (29, 25), (30, 1), (31, 3), (32, 29), (33, 3)], videos=[]),
    dict(slug="edom", name="Edom (Seir)", kind="place", aliases=["Edom", "Seir"],
         desc="The nation and land descended from ESAU — the rugged red-sandstone highlands south-east of the Dead "
              "Sea, also called SEIR ('hairy,' echoing Esau). The name Edom ('red') is minted from the red stew "
              "(25:30) and matches the red Nubian sandstone of the region (whose later capital, Petra, is carved "
              "into it). Its whole family tree — Esau's wives and sons, the clan-chiefs (alufim), the older Horite "
              "people they displaced, and eight kings who reigned 'before any king reigned over Israel' — fills "
              "Genesis 36. Edom and Israel are the archetypal quarreling brothers of the Bible: kin, yet perennial "
              "enemies — Edom refuses Israel passage in the wilderness (Numbers 20), and the prophets return to it "
              "again and again (Obadiah is entirely an oracle against Edom; Jeremiah 49; Isaiah 34). Herod the Great "
              "was an Idumean — a Hellenized Edomite — so the brother-rivalry runs right up to the Gospels.",
         refs=[(25, 30), (36, 1), (36, 8)],
         coords=(30.32, 35.44, 0.9), approx=True,
         modern="The highlands of southern Jordan (Seir), south-east of the Dead Sea"),
    dict(slug="amalek", name="Amalek", kind="people", aliases=["Amalek", "Amalekites", "Agagite"],
         desc="Israel's oldest and bitterest enemy — and, this chapter reveals, a grandson of ESAU: 'Timna was "
              "concubine to Eliphaz, Esau's son, and she bore Amalek' (36:12). The Amalekites ambush Israel's faint "
              "and straggling just out of Egypt (Exodus 17:8-16), and for it earn a unique sentence — 'Jehovah will "
              "have war with Amalek from generation to generation' — and the charge to 'blot out the memory of "
              "Amalek from under heaven' (Deuteronomy 25:17-19). Saul loses his kingdom for sparing their king Agag "
              "(1 Samuel 15); and Haman 'the Agagite,' who plots to annihilate every Jew in the Persian empire "
              "(Esther 3), is read as the last flowering of that line. So the roll of honor for Esau also, in a "
              "single verse, plants the enemy that will shadow Israel for a thousand years.",
         refs=[(36, 12), (36, 16)], videos=[]),
    dict(slug="horites", name="Horites", kind="people", aliases=["Horites", "Horite", "Hori"],
         desc="The original inhabitants of Seir, before Edom — 'the sons of Seir the Horite, the inhabitants of the "
              "land' (36:20), catalogued here alongside Esau's line. The name is usually tied to chor, 'cave,' so "
              "the traditional gloss is 'cave-dwellers' (some scholars instead connect them with the Hurrians of the "
              "wider ancient Near East). Genesis does not pretend Edom rose from empty land: Deuteronomy says plainly "
              "that 'the Horites lived in Seir formerly, but the sons of Esau dispossessed them… and dwelt in their "
              "place' (Deuteronomy 2:12) — the same honesty the Bible will later turn on the peoples Israel itself "
              "displaces. One Horite clan, Anah, is remembered for a desert find, the yemim (hot springs?) — a rare "
              "word no one can quite translate (36:24).",
         refs=[(36, 20), (36, 21)], videos=[]),

    # ---- Genesis 41 ----
    # ⚠️ ALIAS PARTITION: three entries now claim "Pharaoh" (Genesis 12, Joseph,
    # the Exodus). Their refs must partition per-verse or the resolver links the
    # wrong king — which it was doing: "Pharaoh" all through the Joseph story
    # resolved to the Genesis-12 entry, a man about two centuries earlier. The
    # refs below cover the FIRST occurrence in each Joseph chapter, which is what
    # the once-per-chapter link cap actually reaches.
    dict(slug="pharaoh-joseph", name="Pharaoh (of Joseph's time)", kind="person", aliases=["Pharaoh"],
         desc="The king who dreams of seven cows and seven ears, cannot get a reading from his own experts, and "
              "then hands a thirty-year-old Hebrew prisoner the government of Egypt (Genesis 41). He is never "
              "named — Genesis calls every Egyptian king simply 'Pharaoh,' which is itself the Egyptian phrase "
              "<em>per-aa</em>, 'the Great House,' the palace standing in for its occupant. ⚠️ NOT the Pharaoh "
              "of Genesis 12 (who took Sarai) nor the Pharaoh of the Exodus (who 'did not know Joseph'); the "
              "Bible's Egypt spans centuries under one recycled title. He is never named, so no identification "
              "is certain — but the chronology this translation follows elsewhere narrows it sharply. Taking the "
              "Exodus at 1446 BC (1 Kings 6:1) and Israel's 430 years in Egypt (Exodus 12:40) puts Jacob's "
              "arrival at 1876 BC; Joseph is thirty at his elevation (41:46) and thirty-nine when his father "
              "comes down, so he takes office around 1885 BC. That lands squarely in the <strong>12th Dynasty "
              "of the Middle Kingdom</strong>, in the reign of <strong>Senusret II</strong> and running on into "
              "Senusret III — a strong, centralized Egypt, which fits a chapter about a national grain "
              "bureaucracy. ⚠️ It also RULES OUT the popular HYKSOS theory, which places Joseph under the "
              "Semitic-speaking rulers of Lower Egypt on the appealing reasoning that a foreign dynasty would "
              "more readily elevate a Semite: the Hyksos period (c. 1650-1550 BC) is roughly 235 years too late "
              "for this reckoning. That view belongs to a different Exodus chronology, and the two should not be "
              "mixed. Corroborating material deserves grading rather than listing: the Semitic settlement "
              "excavated at AVARIS (Tell el-Dab'a) in the eastern Delta — Goshen's region — dating from the "
              "late 12th Dynasty is real archaeology and genuinely suggestive of Asiatics settled in Egypt at "
              "about the right time; the BAHR YUSSEF ('Joseph's Canal'), the channel feeding the Faiyum that "
              "Amenemhat III's hydraulic works expanded, is often cited but is far weaker — the name is "
              "medieval Arabic tradition, not an ancient inscription; and attempts to identify Joseph with a "
              "particular named vizier are speculation. What the chapter does get demonstrably right is the "
              "SETTING: the "
              "shaving before a royal audience (Egyptians were clean-shaven where Semites were bearded), the "
              "signet ring, the fine linen, the gold collar of honour, the second chariot, and a state grain "
              "administration — all attested Egyptian court practice. Genesis knows the country it is "
              "describing, whatever century it is describing.",
         refs=[(37, 36), (39, 1), (40, 2), (41, 1), (41, 38), (41, 41), (42, 15), (44, 18), (45, 2)], videos=[]),
    dict(slug="asenath", name="Asenath", kind="person", aliases=["Asenath"],
         desc="The Egyptian wife Pharaoh gives Joseph — 'daughter of Potiphera priest of ON' (41:45) — and so "
              "the mother of Manasseh and Ephraim, which means two of Israel's twelve tribes descend from an "
              "Egyptian priest's daughter. Genesis reports it without a flicker of anxiety, though later "
              "readers were less relaxed: a Hellenistic romance, <em>Joseph and Aseneth</em>, was written "
              "largely to supply her with a conversion. Her name is genuinely Egyptian, plausibly "
              "<em>ns-Nt</em>, 'she belongs to (the goddess) Neith.' ⚠️ Her father's name, POTIPHERA, is a "
              "fuller spelling of the same Egyptian name as POTIPHAR ('he whom Ra has given'); they are "
              "presented as different men — one the chief of the executioners, the other a priest of On — and "
              "the identical-sounding names are a coincidence of a very common formula, though some ancient "
              "traditions could not resist merging them.",
         refs=[(41, 45), (41, 50)], videos=[]),
    dict(slug="on-heliopolis", name="On (Heliopolis)", kind="place", aliases=["On"],
         desc="The ancient centre of the Egyptian sun-cult, where Joseph's father-in-law served as priest "
              "(41:45) — Egyptian <em>Iunu</em>, Greek HELIOPOLIS, 'sun city,' at the apex of the Delta inside "
              "modern Cairo. It was one of the oldest and most prestigious temple establishments in Egypt, the "
              "home of the Ennead and of Ra's own priesthood; a priest of On was an aristocrat of the "
              "religious establishment, which is the measure of the marriage Pharaoh arranges. Almost nothing "
              "of it survives above ground but a single standing obelisk of Senusret I (c. 1950 BC), which "
              "Joseph would have seen. Jeremiah names it Beth-shemesh, 'house of the sun' (43:13).",
         coord=(30.1290, 31.3070), refs=[(41, 45), (41, 50)], videos=[]),
    dict(slug="manasseh-ephraim", name="Manasseh and Ephraim", kind="person",
         aliases=["Manasseh", "Ephraim"],
         desc="Joseph's two sons by Asenath, born in Egypt before the famine, and both named for what exile "
              "had done to him. MANASSEH (Menashsheh) puns on <em>nashani</em> — 'God has made me FORGET all "
              "my toil and all my father's house' (41:51), a startling thing to say aloud about the family "
              "that is about to walk back into his life. EPHRAIM puns on <em>hiphrani</em> — 'God has made me "
              "FRUITFUL in the land of my affliction' (41:52); he calls Egypt, where he governs, the land of "
              "his affliction. Jacob later adopts both as his own and crosses his hands to put the younger "
              "first (48:5, 14) — one more overturned birthright — and their names become two of Israel's "
              "tribes; 'Ephraim' eventually stands for the whole northern kingdom in the prophets.",
         refs=[(41, 51), (41, 52)], videos=[]),

    # ---- Genesis 39 ----
    # UNNAMED in the text, so no aliases — encyclopedia-only, the antiochus-iv pattern.
    dict(slug="potiphars-wife", name="Potiphar's wife", kind="person",
         desc="The woman who propositions Joseph, is refused, and has him jailed on a false charge (Genesis "
              "39:7-20). The Hebrew never names her — she is 'his master's wife' throughout, which is part of "
              "the chapter's design: she has all the power and no identity, while the slave has a name. Later "
              "tradition supplied one anyway, calling her ZULEIKHA; the name is medieval, comes to prominence "
              "in Persian and Islamic retellings (where the story is elaborated at length in Sura 12 of the "
              "Qur'an and in Jami's poem <em>Yusuf and Zulaikha</em>), and has no basis in Genesis. Her "
              "accusation is a small masterpiece of construction: she gathers the household staff BEFORE her "
              "husband, opens with the ethnic word ('a HEBREW man… to laugh at US'), and by the time she "
              "reaches Potiphar it has become 'the Hebrew slave whom YOU brought to us' — the blame quietly "
              "relocated onto the man she is complaining to. Note too the one preposition she edits: the "
              "narrator says Joseph left the garment IN HER HAND, because she was gripping it; in her two "
              "retellings it becomes 'beside me,' and her hand vanishes from the story. ⚠️ A closely similar "
              "tale survives in Egyptian — the <em>Tale of Two Brothers</em> (Papyrus d'Orbiney, c. 1200 BC) — "
              "and in Greek myth as Phaedra and Hippolytus; whether that means borrowing, a shared stock of "
              "story-shapes, or simply a recurring fact of life for powerless men in powerful houses is argued "
              "and not settled.",
         refs=[(39, 7), (39, 12), (39, 14), (39, 19)], videos=[]),

    # ---- Genesis 38 ----
    dict(slug="tamar", name="Tamar", kind="person", aliases=["Tamar"],
         desc="Judah's daughter-in-law — widowed twice by his sons Er and Onan, then left in limbo when Judah "
              "withheld his third son Shelah, the levirate duty that was her only route to a future. She takes "
              "it by stratagem: veiled at the roadside on the Timnah road, she is taken by Judah for a "
              "prostitute, and secures as his pledge the seal, cord and staff that are his identity. Three "
              "months later, sentenced by him to be burned, she returns them with two words — 'RECOGNIZE, "
              "PLEASE' — the exact phrase Judah had used to make his own father identify Joseph's bloodied "
              "tunic. Judah's answer is the hinge of his life: 'She is more righteous than I' (38:26). "
              "Genesis never calls her righteous in its own voice; it has the patriarch do it, in public, and "
              "leaves the sentence standing. Her twins are Perez and Zerah — and the line of Perez runs to "
              "David (Ruth 4:18-22) and into the opening paragraph of the New Testament, where Matthew names "
              "her: 'Perez and Zerah by Tamar' (Matthew 1:3), one of only four women in that genealogy. "
              "⚠️ Not the same Tamar as David's daughter (2 Samuel 13), though the two stories share a word — "
              "the ketonet passim, the ornamented tunic.",
         refs=[(38, 6), (38, 14), (38, 25), (38, 26)], videos=[]),
    dict(slug="onan", name="Onan", kind="person", aliases=["Onan"],
         desc="Judah's second son, who married his brother Er's widow Tamar under the levirate custom and then "
              "refused its purpose — 'he knew that the offspring would not be his,' and so withheld it 'so as "
              "not to give offspring to his brother' (38:9). The chapter states the charge plainly and it is a "
              "property calculation: Er's death had made Onan heir, and a son credited to Er would displace "
              "him, so he took the marriage and cheated the dead man's name. ⚠️ The English word 'onanism' is a "
              "much later coinage that reads a different offence back into the verse; older Jewish and "
              "Christian commentators argued that reading at length, but it is theirs, not the text's — "
              "Genesis says what Onan withheld, and from whom.",
         refs=[(38, 4), (38, 8), (38, 9)], videos=[]),
    # ⚠️ NO "Zerah" alias: Genesis 36 has an Edomite Zerah (36:13, 17, 33) and a
    # bare alias here wrongly linked HIM to Judah's son. Zerah goes unlinked; the
    # entry covers him and is reachable from Perez.
    dict(slug="perez", name="Perez", kind="person", aliases=["Perez"],
         desc="The elder of Judah and Tamar's twins, named for the midwife's startled pun — 'how you have "
              "BROKEN OUT, a breach (perets) upon you!' — after his brother Zerah's hand appeared first, was "
              "marked with a scarlet thread, and withdrew (38:27-30). One more firstborn in this book who "
              "isn't. The name outlives the joke: Ruth ends by tracing 'the generations of Perez' ten "
              "names down to DAVID (Ruth 4:18-22), and Matthew opens the New Testament with the same line "
              "(Matthew 1:3). So the royal and messianic descent runs not through the son Judah protected nor "
              "the marriage he arranged, but through the widow he wronged. KJV spells him Pharez; Douay, "
              "through the Greek, Phares.",
         refs=[(38, 29), (38, 30)], videos=[]),
    dict(slug="adullam", name="Adullam", kind="place", aliases=["Adullam", "Adullamite"],
         desc="The town in the Judean lowlands (the Shephelah) where Judah 'went down' and took up with Hirah, "
              "his friend and go-between in the affair with Tamar (38:1, 12, 20). Identified with Tell "
              "esh-Sheikh Madhkur, in the hill country between the coastal plain and Hebron. Its cave will "
              "later shelter DAVID — a descendant of the twins conceived in this chapter — when he flees Saul "
              "and four hundred desperate men gather to him there (1 Samuel 22:1-2).",
         coord=(31.6497, 34.9569), refs=[(38, 1), (38, 12)], videos=[]),
    dict(slug="timnah", name="Timnah", kind="place", aliases=["Timnah"],
         desc="The town Judah went up to for his sheepshearing — a festival occasion — and on whose road Tamar "
              "took her seat (38:12-14). Usually identified with Tel Batash in the Sorek valley, excavated and "
              "occupied through the Bronze and Iron Ages. A Timnah is also where Samson finds his Philistine "
              "wife and kills a lion (Judges 14), though whether it is the same town is disputed.",
         coord=(31.7842, 34.9161), approx=True, refs=[(38, 12), (38, 13), (38, 14)], videos=[]),
    dict(slug="enaim", name="Enaim", kind="place", aliases=["Enaim"],
         desc="The place on the Timnah road where Tamar sat veiled — and the site of one of the Bible's driest "
              "jokes. The Hebrew petach einayim is 'the entrance of Enaim,' a real town; but einayim is also "
              "the ordinary word for EYES, so the phrase reads simultaneously as 'the Opening of the Eyes.' "
              "She takes her seat at Eyes-Open, and the very next verse is 'he did not know that she was his "
              "daughter-in-law' (38:14-16). The KJV misses both, reading 'in an open place'; ASV and NIV "
              "recover the town. Its exact location is unknown — somewhere between Adullam and Timnah.",
         refs=[(38, 14), (38, 21)], videos=[]),

    # ---- Genesis 37 ----
    dict(slug="goshen", name="Goshen", kind="place", aliases=["Goshen", "land of Goshen"],
         coords=(30.75, 31.90, 1.05), approx=True,
         modern="Eastern Nile Delta, Egypt — the Wadi Tumilat and the country around Tell el-Dab'a (Avaris)",
         desc="The district of the eastern NILE DELTA that Joseph gives his family to live in (45:10), and the "
              "address of Israel for the next four hundred years. Its qualifications are practical and the text "
              "says so: good pasture for flocks and herds, and 'near to me' — close enough to the seat of "
              "government to be provisioned through five more years of famine. It is also, crucially, at the "
              "EDGE. Goshen sits in the Delta's eastern reach, toward Canaan and slightly outside Egypt proper, "
              "which is why a family of shepherds can settle there and stay a distinct people rather than being "
              "absorbed — and Genesis 46:34 makes the separation explicit and mutual: 'every shepherd is an "
              "abomination to Egypt.' ⚠️ The exact boundaries are not recoverable. The name is not Egyptian and "
              "appears in no Egyptian text; the identification with the Wadi Tumilat and the region around "
              "Tell el-Dab'a (ancient Avaris, a Semitic settlement in exactly this area in the Middle Bronze "
              "Age) is a reasonable inference from the biblical geography plus the archaeology, not a "
              "documented match. What the text is clear about is the shape of the story: the same ground that "
              "receives them as honoured guests of the vizier holds them as slaves in Exodus 1, and it is from "
              "here that they leave.",
         refs=[(45, 10), (46, 28), (47, 6), (47, 27), ("Exodus", 8, 22), ("Exodus", 9, 26)]),
    dict(slug="dothan", name="Dothan", kind="place", aliases=["Dothan"],
         desc="The grazing town where Joseph finally found his brothers — and was stripped, thrown into a dry "
              "cistern, and sold (37:17-28). It is a real and well-identified site: TELL DOTHAN, about thirteen "
              "miles north of Shechem, excavated by Joseph Free in the 1950s and 60s and found to have been "
              "occupied continuously through the Bronze and Iron Ages, so a Bronze-Age family pasturing flocks "
              "there fits the archaeology. Its position matters to the plot: Dothan sits on the caravan route "
              "running from Gilead across the plain toward the coast road and Egypt — which is precisely why a "
              "spice caravan bound for Egypt happens past the pit (37:25). The town returns once more, and in "
              "the opposite key: it is at Dothan that Elisha's terrified servant wakes to find the hills around "
              "them full of horses and chariots of fire (2 Kings 6:13-17). Same town; the other kind of morning.",
         coord=(32.4106, 35.2264), refs=[(37, 17)], videos=[]),
    dict(slug="potiphar", name="Potiphar", kind="person", aliases=["Potiphar"],
         desc="The Egyptian who buys Joseph at the end of Genesis 37 — 'a court official of Pharaoh, chief of "
              "the executioners' (37:36). Both halves of his title repay attention. SARIS is the court-official "
              "word: it can mean a literal eunuch and often does, but is used broadly of high functionaries, "
              "which is why the versions divide (KJV 'an officer,' NWT 'a court official') — and why Potiphar's "
              "having a wife is not the contradiction it looks. SAR HA-TABBACHIM is literally 'chief of the "
              "SLAUGHTERERS,' from tabbach, a butcher; the usual rendering 'captain of the guard' rests on the "
              "reasonable ground that a royal bodyguard's business includes executions — and the Aramaic "
              "equivalent is unambiguous when the same office turns up in Babylon, where Arioch, 'chief of the "
              "executioners,' comes to kill the wise men (Daniel 2:14). His name is genuinely Egyptian: "
              "Pa-di-pa-Ra, 'he whom Ra has given.' In his house Joseph will rise to steward, be accused by "
              "Potiphar's wife, and be jailed (Genesis 39) — the second pit of his life.",
         refs=[(37, 36)], videos=[]),

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
    dict(slug="ruth", name="Ruth", kind="person", aliases=["Ruth"],
         desc="A woman of MOAB, widow of Mahlon, who binds herself to her Israelite mother-in-law NAOMI with the "
              "great oath 'your people my people, your God my God' (1:16) and returns with her to Bethlehem. The "
              "book named for her tells how this foreign convert gleans in the field of Boaz, claims the levirate "
              "redemption, and marries him — becoming the great-grandmother of DAVID (4:17) and, in Matthew's "
              "genealogy, an ancestress of Jesus (Matthew 1:5). ⚠️ That a MOABITE is the heroine cuts pointedly "
              "against Deuteronomy 23:3's ban on Moabites in the assembly of Jehovah: Ruth's covenant belonging is "
              "won by chesed and faith, not by blood. Her name's meaning is uncertain — often linked to re'ut, "
              "'friendship, companionship,' or to a root for 'refreshment.'",
         refs=[("Ruth", 1, 4), ("Ruth", 1, 16)], videos=[]),
    dict(slug="naomi", name="Naomi (Mara)", kind="person", aliases=["Naomi"],
         desc="Wife of ELIMELECH of Bethlehem, who loses husband and both sons in Moab and returns emptied to her "
              "home town, telling the women to call her not Naomi ('my sweetness') but Mara ('bitter'), 'for the "
              "Almighty has dealt very bitterly with me' (1:20). Her honest, unflinching naming of God as the author "
              "of her grief runs through the book, and her scheme to seek 'rest' for her daughter-in-law RUTH (3:1) "
              "drives its resolution. By the end the women of Bethlehem tell her a redeemer is born and 'a son has "
              "been born to Naomi' (4:17) — the emptiness reversed, and the line of David begun.",
         refs=[("Ruth", 1, 2), ("Ruth", 1, 20)], videos=[]),
    dict(slug="moab", name="Moab", kind="place", aliases=["Moabites", "Moabite", "Moab"],
         desc="The nation and high plateau east of the Dead Sea, descended from MOAB, son of LOT by his elder "
              "daughter (Genesis 19:37). Israel's perennial neighbour and frequent enemy: Moab hired Balaam to curse "
              "Israel (Numbers 22-24), and Deuteronomy 23:3 bars Moabites from 'the assembly of Jehovah, even to the "
              "tenth generation.' Yet it is to the fields of Moab that Elimelech's family flees the famine, and out "
              "of Moab comes RUTH, whose loyalty out-does Israel's own. The book quietly holds the ban and the "
              "Moabite heroine in the same hand.",
         refs=[("Ruth", 1, 1), (19, 37)], videos=[]),
    dict(slug="elimelech", name="Elimelech", kind="person", aliases=["Elimelech"],
         desc="'My God is King' — a man of Bethlehem, husband of NAOMI, who takes his family to sojourn in MOAB "
              "during a famine and dies there (Ruth 1:2-3), leaving the name and land that Boaz will later 'redeem' "
              "by marrying Ruth (4:9-10). His heavy, hopeful name stands over a story of exile and death — and then "
              "over a kingship, David's, restored through his line.",
         refs=[("Ruth", 1, 2)], videos=[]),
    dict(slug="orpah", name="Orpah", kind="person", aliases=["Orpah"],
         desc="The other Moabite daughter-in-law of NAOMI, widow of Chilion. Urged by Naomi to return home, Orpah "
              "kisses her mother-in-law and goes back 'to her people and to her gods' (1:15) — set beside RUTH, who "
              "clings and stays. ⚠️ The narrator does not blame her: hers is the reasonable choice, and the book "
              "uses it to measure the extravagance of Ruth's. Her name is traditionally linked to oref, 'the back of "
              "the neck' — the one who turns her back — though the etymology is uncertain.",
         refs=[("Ruth", 1, 4), ("Ruth", 1, 14)], videos=[]),
    dict(slug="jude", name="Jude (Judas, brother of James)", kind="person", aliases=["Jude"],
         desc="The author of the letter that bears his name — 'a slave of Jesus Christ and brother of JAMES' (1:1). "
              "Naming James the Just, leader of the Jerusalem church and a brother of Jesus, identifies this Jude as "
              "another of the Lord's brothers (listed in Mark 6:3 as 'James and Joses and Judas and Simon'). He "
              "writes not by family claim but as a servant, calling the church to 'contend for the faith once for "
              "all delivered.' ⚠️ Not to be confused with Judas Iscariot, or with the apostle Judas 'not Iscariot' "
              "(John 14:22); the brother-of-James signature marks him out.",
         refs=[("Jude", 1, 1)], videos=[]),
    dict(slug="balaam", name="Balaam", kind="person", aliases=["Balaam"],
         desc="The gentile seer of Numbers 22-24, hired by Balak of Moab to curse Israel and made to bless them "
              "instead — but who then taught Balak to seduce Israel into idolatry and immorality for a fee (Numbers "
              "31:16). In the New Testament he becomes the type of the teacher who sells his gift for money: Jude "
              "condemns those who 'for pay abandoned themselves to the error of Balaam' (1:11), and 2 Peter 2:15 and "
              "Revelation 2:14 use him the same way. Greed dressed up as prophecy.",
         refs=[("Jude", 1, 11)], videos=[]),
    dict(slug="korah", name="Korah", kind="person", aliases=["Korah"],
         desc="A Levite who led a revolt against the authority of Moses and Aaron in the wilderness, claiming the "
              "whole congregation was holy and needed no mediators; the earth opened and swallowed him and his "
              "company (Numbers 16). Jude makes him the type of rebellion against God-given leadership: the false "
              "teachers 'perished in the rebellion (antilogia) of Korah' (1:11) — the third of his three named "
              "ruins, after Cain's murder and Balaam's greed.",
         refs=[("Jude", 1, 11)], videos=[]),
    dict(slug="sodom", name="Sodom (and Gomorrah)", kind="place", aliases=["Sodom", "Gomorrah"],
         desc="The chief of the cities of the plain by the Dead Sea, a byword for wickedness, destroyed by fire and "
              "sulphur from Jehovah in the days of Abraham and Lot (Genesis 18-19). LOT escapes; his wife looks back "
              "and becomes a pillar of salt; and Moab and Ammon are born of the aftermath (Genesis 19:37-38). Ever "
              "after, Sodom is Scripture's shorthand for judgment — the prophets invoke it, Jesus warns that towns "
              "rejecting him will fare worse than it (Matthew 10:15), and Jude sets it among his examples, "
              "'undergoing the punishment of eternal fire' (1:7).",
         refs=[(19, 24), ("Jude", 1, 7)], videos=[]),
    dict(slug="jeremiah", name="Jeremiah", kind="person", aliases=["Jeremiah"],
         desc="'Jehovah exalts' (or 'loosens,' or 'establishes' — the root is uncertain). A priest of ANATHOTH in "
              "Benjamin, called in 627 BC (1:2) to a forty-year ministry that ran through the last five kings of "
              "Judah to the destruction of Jerusalem in 586 BC and beyond. Known before the womb and made 'a prophet "
              "to the nations' (1:5), he was charged 'to uproot and to tear down… to build and to plant' (1:10) — a "
              "career mostly of warning a doomed nation to submit to Babylon, and mostly rejected for it: beaten, put "
              "in the stocks, thrown down a cistern, and finally carried off to Egypt. The 'weeping prophet,' whose "
              "anguished 'confessions' lay his inner life bare, and who was given the promise of a NEW COVENANT "
              "written on the heart (31:31-34). His scribe BARUCH wrote his words down (ch 36).",
         refs=[("Jeremiah", 1, 1), ("Jeremiah", 1, 5)], videos=[]),
    dict(slug="anathoth", name="Anathoth", kind="place", aliases=["Anathoth"],
         desc="A Levitical (priestly) town in the territory of Benjamin, about three miles (5 km) northeast of "
              "Jerusalem — JEREMIAH's home village (1:1). It was very likely the place to which Solomon banished the "
              "priest Abiathar, sparing his life 'because you carried the ark' (1 Kings 2:26), which would make "
              "Jeremiah a son of that sidelined priestly line. Its men later plot against Jeremiah's life (11:21), "
              "and yet it is a field at Anathoth that Jeremiah buys, under siege, as a sign that 'houses and fields "
              "shall again be bought in this land' (ch 32). Identified with the modern village of Anata / nearby "
              "Ras el-Kharrubeh.",
         coords=(31.83, 35.28, 0.06), refs=[("Jeremiah", 1, 1)], videos=[]),
    dict(slug="daniel", name="Daniel (Belteshazzar)", kind="person", aliases=["Daniel"],
         desc="'God is my judge' — a Judean of noble birth taken to Babylon in the first deportation (605 BC) and "
              "given the Babylonian name BELTESHAZZAR (1:7). Trained for the royal court, he refuses the king's food, "
              "is found ten times wiser than the magicians, and rises to rule the province of Babylon after revealing "
              "and interpreting Nebuchadnezzar's dream (ch 2) — the first of a series in which he reads what no wise "
              "man can: the writing on Belshazzar's wall, and his own visions of the four beasts, the seventy weeks, "
              "and the resurrection. Delivered from the lions' den under Darius, he serves into the Persian period. "
              "The book bears his name and, from chapter 7, speaks in his own voice ('I, Daniel'). His three friends "
              "are SHADRACH, MESHACH, and ABEDNEGO.",
         refs=[("Daniel", 1, 6), ("Daniel", 2, 19)], videos=[]),
    dict(slug="shadrach-meshach-abednego", name="Shadrach, Meshach, and Abednego", kind="person",
         aliases=["Shadrach", "Meshach", "Abednego"],
         desc="The three companions of DANIEL — Judean youths whose Hebrew names, HANANIAH ('Jehovah is gracious'), "
              "MISHAEL ('who is what God is'), and AZARIAH ('Jehovah has helped'), each carried the name of the true "
              "God, and who were renamed in Babylon Shadrach, Meshach, and Abednego, names bound to Babylonian gods "
              "(1:6-7). Set over the province of Babylon at Daniel's request (2:49), they are the heroes of chapter 3: "
              "refusing to bow to Nebuchadnezzar's golden image, they are thrown into the fiery furnace and walk "
              "unburned with a fourth figure 'like a son of the gods' — 'our God is able to deliver us; but if not, "
              "we will not serve your gods' (3:17-18).",
         refs=[("Daniel", 2, 49)], videos=[]),
    dict(slug="samuel", name="Samuel", kind="person", aliases=["Samuel"],
         desc="'God has heard' (or 'name of God') — the child asked of Jehovah by his barren mother HANNAH and given "
              "back to serve at Shiloh (ch 1). He becomes the LAST of the judges and the first of the great "
              "prophets, the hinge-figure of Israel's history: he leads a repentant Israel against the Philistines, "
              "and then, when the people demand a king 'like all the nations,' he warns them, anoints SAUL, and later "
              "anoints DAVID in Saul's place. A lifelong Nazirite, called by God as a boy ('speak, for your servant "
              "hears,' ch 3), he is the prophet under whose word the whole monarchy begins. He dies at 1 Samuel 25, "
              "before the book that bears his name is done.",
         refs=[("1 Samuel", 1, 20), ("1 Samuel", 1, 27)], videos=[]),
    dict(slug="hannah", name="Hannah", kind="person", aliases=["Hannah"],
         desc="'Grace, favor' — the barren, beloved wife of ELKANAH, provoked year after year by her rival Peninnah, "
              "who prays silently at Shiloh until the priest Eli takes her for a drunk, vows her son to God if he is "
              "given, and, when SAMUEL is born, carries him back to the sanctuary and leaves him there (ch 1). She "
              "joins the line of Israel's once-barren mothers (Sarah, Rebekah, Rachel), and her song of the God who "
              "'raises the poor from the dust' and 'brings low and lifts up' (2:1-10) becomes, centuries later, the "
              "model for Mary's Magnificat (Luke 1:46-55).",
         refs=[("1 Samuel", 1, 2), ("1 Samuel", 1, 20)], videos=[]),
    dict(slug="eli", name="Eli", kind="person", aliases=["Eli"],
         desc="The priest and judge at SHILOH in Samuel's boyhood. He blesses the praying Hannah (after first "
              "mistaking her for a drunk) and raises the child Samuel at the sanctuary — but he fails to restrain his "
              "own wicked sons, HOPHNI and PHINEHAS, who defile the priesthood, and a man of God pronounces the end "
              "of his house (ch 2). Old and blind, he dies falling from his seat when word comes that the ark of God "
              "has been captured and his sons killed (ch 4) — the collapse of the old order that Samuel's rise "
              "replaces.",
         refs=[("1 Samuel", 1, 9), ("1 Samuel", 1, 17)], videos=[]),
    dict(slug="shiloh", name="Shiloh (the sanctuary)", kind="place", aliases=[],
         desc="A town in the hill country of EPHRAIM, north of Bethel, that was Israel's central sanctuary through "
              "the whole period of the Judges: here the tabernacle and the ark of the covenant stood (Joshua 18:1), "
              "and here Israel came up to worship 'Jehovah of hosts' (1 Samuel 1:3). It is the setting of Hannah's "
              "vow and the boyhood of Samuel — and it falls when the ark is captured in battle (ch 4), a loss the "
              "prophet Jeremiah invokes as a warning to a later generation trusting in the Jerusalem temple: 'go to "
              "my place that was in Shiloh… and see what I did to it' (Jeremiah 7:12). ⚠️ Not to be confused with the "
              "disputed word 'Shiloh' of Genesis 49:10, a different Hebrew term.",
         coords=(32.06, 35.29, 0.05), refs=[("1 Samuel", 1, 3), ("1 Samuel", 1, 9)], videos=[]),
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
    # A pin also OVERRIDES the once-per-chapter link cap (see build.py), which is
    # how a territory gets a map link at the verse that actually describes it
    # rather than at its first incidental mention.
    (36, 8, "Seir", 1, "edom"),             # "Esau dwelt in the hill country of Seir" — the territory verse
    (36, 8, "Edom", 1, "edom"),             # "— Esau is Edom"
]

XREFS = [
    # ---- Mark 1 ----
    ((("Mark", 1, 2)), (("Mark", 1, 3)), "'in Isaiah the prophet' — but v2 is Malachi 3:1 spliced with Exodus 23:20; only v3 is Isaiah 40:3"),
    ((("Mark", 1, 6)), (("Mark", 1, 7)), "camel's hair and a leather belt — John dressed as Elijah (2 Kings 1:8), the returning forerunner"),
    ((("Mark", 1, 10)), (("Mark", 1, 12)), "the heavens TORN open (schizō) — paid off only at 15:38, the temple curtain torn top to bottom"),
    ((("Mark", 1, 14)), (("Mark", 1, 15)), "'handed over' (paradothēnai), first of John, finally of Jesus — the forerunner's fate prefigures his"),
    ((("Mark", 1, 24)), (("Mark", 1, 25)), "the first to name Jesus correctly is a demon, and is muzzled — the Messianic secret opens here"),
    ((("Mark", 1, 41)), (("Mark", 1, 42)), "'moved with anger' (the harder reading) — and yet he touches the leper, the thing no one else would do"),

    # ---- Judges 1 ----
    ((("Judges", 1, 1)), (("Joshua", 1, 1)), "'after the death of Joshua' — the book opens exactly as Joshua did over Moses; the pattern is the point"),
    ((("Judges", 1, 2)), (49, 8), "Judah sent up first — Jacob's blessing, 'your brothers shall praise you,' made good at the head of the fighting"),
    ((("Judges", 1, 7)), (("Judges", 1, 6)), "Adoni-bezek's thumbs and toes: 'as I have done, so God has repaid me' — the victim names the justice"),
    ((("Judges", 1, 21)), (("Joshua", 1, 1)), "the Jebusites still in Jerusalem 'to this day' — the conquest of Joshua on the record as unfinished, before David"),
    ((("Judges", 1, 28)), (("Exodus", 1, 11)), "mas, 'forced labour' — the tribes impose on the Canaanites the very thing Egypt imposed on Israel"),

    # ---- Joshua 1 ----
    ((("Joshua", 1, 4)), (("Deuteronomy", 1, 7)), "the same ideal borders promised to Moses — wilderness to Lebanon to the Euphrates — repeated as the land is finally entered"),
    ((("Joshua", 1, 5)), (("Deuteronomy", 1, 8)), "'as I was with Moses, I will be with you' — the succession sealed by the same presence"),
    ((("Joshua", 1, 7)), (48, 14), "taskil, 'act wisely' — the insight-root that gave the crossed hands their meaning, now the promise to Joshua"),
    ((("Joshua", 1, 18)), (("Joshua", 1, 6)), "'only be strong and resolute' — the charge God laid on Joshua handed back to him by the people"),

    # ---- 3 John ----
    ((("3 John", 1, 5)), (("2 John", 1, 10)), "the exact positive of 2 John's refusal — receive the travellers, because these carry the Name, not a false Christ"),
    ((("3 John", 1, 8)), (("2 John", 1, 11)), "'fellow workers with the truth' — funding the right teacher makes you a partner in the mission, as funding the wrong one made you a partner in his work"),
    ((("3 John", 1, 11)), ("John", 15, 15), "'the friends' — the circle names itself by Jesus' own word, 'I have called you friends'"),
    ((("3 John", 1, 14)), (("2 John", 1, 12)), "'mouth to mouth' — the same close as the companion letter, a letter admitting a letter is not enough"),

    # ---- 2 John ----
    ((("2 John", 1, 5)), ("John", 13, 34), "'not a new commandment, but from the beginning' — set beside Jesus calling the love-command NEW"),
    ((("2 John", 1, 5)), ("John", 1, 1), "'from the beginning' — the same instinct as the Gospel to reach back to arche, here for a commandment"),
    ((("2 John", 1, 7)), ("John", 1, 14), "'Jesus Christ coming in flesh' — the confession the Gospel stated as 'the Word became flesh'"),
    ((("2 John", 1, 12)), (("Numbers", 12, 8)), "'mouth to mouth' — the phrase used of God speaking with Moses, kept literal here rather than 'face to face'"),

    # ---- Deuteronomy 1 ----
    ((("Deuteronomy", 1, 2)), (("Deuteronomy", 1, 3)), "'eleven days from Horeb' set beside 'in the fortieth year' — the whole chapter is the explanation of that gap"),
    ((("Deuteronomy", 1, 8)), (50, 24), "the oath to Abraham, Isaac and Jacob — the same three names Joseph quoted from his deathbed, now at the border they pointed to"),
    ((("Deuteronomy", 1, 9)), (("Deuteronomy", 1, 31)), "nasa, 'carry': what was too heavy for Moses to lift is what God does 'as a man carries his son'"),
    ((("Deuteronomy", 1, 27)), (("Exodus", 1, 11)), "'because Jehovah hated us he brought us out of Egypt' — the rescue reread as a trap"),
    ((("Deuteronomy", 1, 39)), (2, 17), "'children who do not know good from evil' — the tree's pairing, used of an age too young to be guilty"),

    # ---- Genesis 50 ----
    ((50, 5),  (47, 29), "the oath under the thigh, discharged — with an Egyptian state cortege as escort"),
    ((50, 8),  ("Exodus", 1, 8), "'only their little ones… they left in the land of Goshen' — hostages in all but name, and the first chill of Exodus 1"),
    ((50, 13), (23, 16), "Machpelah, bought from Ephron — used for the fourth and last time in the book"),
    ((50, 17), (37, 24), "'the transgression of your brothers and their sin' — the pit, named at last, in a message their father probably never sent"),
    ((50, 18), (37, 7),  "the dream of brothers bowing, completed — and the dreamer refuses to enjoy it"),
    ((50, 19), (30, 2),  "'am I in the place of God?' — Jacob threw the same phrase at Rachel in anger; Joseph uses it to decline a power he actually holds"),
    ((50, 20), (45, 8),  "'it was not you who sent me here, but God' restated more carefully, with the guilt left in"),
    ((50, 20), (45, 5),  "'to keep a numerous people alive' — the michyah root a third time, each time survival somebody paid for"),
    ((50, 24), ("Exodus", 3, 16), "'God will surely visit you' — quoted back at the burning bush, four hundred years later"),
    ((50, 25), (47, 30), "Joseph asks for what his father asked for, and stakes his body on a promise he will not see kept"),

    # ---- Genesis 49 ----
    ((49, 4),  (35, 22), "'you went up to your father's bed' — the one flat verse where 'Israel heard,' answered roughly forty years later"),
    ((49, 7),  (34, 25), "'cursed be their anger' — Shechem condemned at last on moral grounds, not the prudential ones he used at the time"),
    ((49, 8),  (29, 35), "Leah named him from yadah, 'to praise' — the poem hands the name back as a prophecy"),
    ((49, 8),  (37, 7),  "'your father's sons shall bow down to you' — Joseph's dream, awarded here to Judah"),
    ((49, 10), (44, 33), "the sceptre goes to the brother who offered to be a slave in Benjamin's place"),
    ((49, 22), (37, 24), "'the masters of arrows harassed him' — spoken to the ten men who put him in the pit, apparently without knowing it"),
    ((49, 25), (17, 1),  "Shaddai set beside 'blessings of shadayim, breasts' — the wordplay behind the name's uncertain meaning"),
    ((49, 29), (23, 16), "the cave at Machpelah recited as a deed: bought, from Ephron, the only ground the family owns in the land"),
    ((49, 31), (35, 19), "'and there I buried Leah' — the man who buried Rachel on a roadside asks to be laid beside the wife he did not choose"),
    ((49, 33), (49, 1),  "asaf, 'gather': he calls his sons to gather, gathers his feet into the bed, and is gathered to his people"),

    # ---- Genesis 48 ----
    ((48, 3),  (35, 11), "El Shaddai at Luz — Jacob quotes the Bethel promise back before he uses it to adopt"),
    ((48, 5),  (35, 22), "'like Reuben and Simeon' — the double portion Reuben forfeited, reassigned to Joseph through his two sons"),
    ((48, 7),  (35, 19), "Rachel's grave on the road to Ephrath, remembered sixty years later in the middle of a legal document"),
    ((48, 8),  (27, 18), "'Who are these?' — the last blind father in this book blessing two brothers was Isaac, and Jacob was the one lying to him"),
    ((48, 14), (25, 23), "the younger over the elder, a fourth time — and the only time it happens in the open, with nobody deceived"),
    ((48, 16), (32, 30), "'the angel who has redeemed me from all evil' — the first ga'al in the Bible, from a man who wrestled one at the Jabbok"),
    ((48, 19), (37, 9),  "'I know, my son, I know' — a father overruling Joseph on precedence, to the face of the dreamer of precedence"),
    ((48, 21), (46, 4),  "'God will bring you back' — plural: the Beersheba promise handed on as Jacob's last word to Joseph"),
    ((48, 22), (33, 19), "the ground at Shechem Jacob is recorded as BUYING, not taking 'with my sword and with my bow'"),
    ((48, 22), (34, 25), "the only violence at Shechem in this book is Simeon and Levi's — which Jacob condemned, and curses one chapter later"),

    # ---- Genesis 47 ----
    ((47, 3),  (46, 34), "the coached script delivered word for word — 'shepherds, both we and our fathers' — and it works: Goshen is granted"),
    ((47, 9),  (23, 9),  "'the days of my sojournings' — three generations who owned one piece of ground in Canaan, and it was a grave"),
    ((47, 14), (41, 34), "the silver of two countries buys back the grain his own administration took as the fifth in the good years"),
    ((47, 22), (41, 45), "the priests alone keep their land — and Joseph's wife is the daughter of a priest of On. Genesis records both and connects neither"),
    ((47, 25), (45, 5),  "'you have kept us alive' — the root of Joseph's own michyah, 'to preserve life,' now said by people selling themselves into servitude"),
    ((47, 27), (1, 28),  "'fruitful and multiplied greatly' — the creation blessing, landing on Israel in the same chapter Egypt loses everything"),
    ((47, 27), ("Exodus", 1, 7), "word for word the opening of Exodus 1:7, where the same verbs make a new king afraid"),
    ((47, 29), (24, 2),  "'put your hand under my thigh' — the oath Abraham required of his servant; both times it is about the future of the line"),
    ((47, 30), (46, 4),  "'carry me out of Egypt' — the practical form of 'I will surely bring you up again'"),
    ((47, 31), (37, 10), "'Israel bowed' — the object of the verb is left out; the dream Jacob once rebuked was 'shall I and your mother come to bow down to you?'"),

    # ---- Genesis 46 ----
    ((46, 1),  (26, 24), "Beersheba: where Isaac had his own night visit and built an altar — which is why Jacob sacrifices here to 'the God of his father Isaac'"),
    ((46, 2),  (22, 11), "'Jacob, Jacob' — the doubled name and the one-word answer, hineni, as at the binding: 'Abraham, Abraham'"),
    ((46, 2),  (37, 13), "hineni, 'here I am' — Joseph's word when his father sent him to find his brothers; the errand that ended in the pit"),
    ((46, 3),  (26, 2),  "the prohibition reversed at the same border: God told ISAAC 'do not go down to Egypt'; Jacob is told 'do not FEAR to go down'"),
    ((46, 4),  (50, 13), "'I will surely bring you up again' — discharged personally when Jacob's body is carried back to Machpelah, and nationally at the exodus"),
    ((46, 5),  (45, 27), "the wagons that convinced him, now carrying him"),
    ((46, 12), (38, 7),  "'and Er and Onan died in the land of Canaan' — chapter 38 acknowledged in a subordinate clause of the family record"),
    ((46, 15), (34, 1),  "Dinah counted among Leah's children, so chapter 34 is not quietly dropped"),
    ((46, 30), (37, 35), "'let me die this time' — against all the times he said he would go down to Sheol mourning"),
    ((46, 30), (45, 28), "'let me go and see him before I die' — answered"),
    ((46, 34), ("Exodus", 1, 8), "the separation strategy that keeps them a people, and eventually marks them: 'there arose a new king who did not know Joseph'"),

    # ---- Genesis 45 ----
    ((45, 1),  (43, 31), "'could no longer hold himself in' — the same verb (hit'appeq) he used to get through the meal in ch. 43, now negated: the restraint finally fails"),
    ((45, 4),  (37, 28), "'whom you sold into Egypt' — the act named plainly, to their faces, twenty-two years later"),
    ((45, 4),  (40, 15), "contrast: telling the cupbearer, he said only 'I was stolen away' — a sentence with the criminals left out of it"),
    ((45, 8),  (50, 20), "'it was not you who sent me here, but God' — the first half of the verdict that closes the book: 'you meant evil against me, but God meant it for good'"),
    ((45, 12), (42, 23), "'it is my mouth speaking to you' — the interpreter of 42:23, who existed because Joseph was pretending not to understand Hebrew, is gone"),
    ((45, 22), (37, 3),  "five changes of garments to Rachel's other son, in front of the same ten men — the coat, again"),
    ((45, 24), (37, 26), "'do not be agitated on the way' — with, on the old reading, a specific quarrel in mind: whose idea the pit was"),
    ((45, 26), (37, 32), "'he did not believe them' — the last thing these men brought their father was a bloodied coat and an invitation to draw his own conclusion"),
    ((45, 27), (37, 35), "'the spirit of Jacob revived' — the man who said he would go down to Sheol mourning his son"),
    ((45, 28), (46, 3),  "'let me go and see him before I die' — and God will meet him at Beersheba to promise the journey is safe"),

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

    # ---- Genesis 31 ----
    ((31, 3),  (28, 15), "'Return… and I will be with you' — the Bethel promise called in: the God who swore 'I am WITH YOU and will keep you wherever you go' (28:15) now says the keeping is done and sends Jacob home"),
    ((31, 13), (28, 20), "'I am the God of Bethel, where you… vowed a vow to me' — God holds Jacob to the vow he made as a frightened fugitive at Bethel (28:20-22); the escape-clause bargain is now due"),
    ((31, 42), (29, 32), "'God has seen my AFFLICTION' — oni, the very word Leah spoke over Reuben's birth, 'Jehovah has looked on my affliction' (29:32): the God who sees the unloved wife sees the cheated servant"),
    ((31, 20), (27, 35), "Jacob 'stole the heart' of Laban (deceived him) — the ganav to match the mirmah with which 'your brother came… and took your blessing' (27:35): the deceiver's craft, now turned on his deceiver"),
    ((31, 53), (11, 29), "'the God of Abraham and the God of NAHOR' — Laban swears by the god of the family branch that stayed in the east; Nahor, Abraham's brother (11:29), is Laban's own ancestor, and their religions have visibly parted"),

    # ---- Genesis 32 ----
    ((32, 2),  (28, 12), "'the angels of God met him' — twenty years after the stairway at Bethel, where angels of God ascended and descended (28:12); the messengers of God bracket Jacob's whole exile, at the border going out and coming home"),
    ((32, 12), (27, 41), "'deliver me from the hand of Esau' — the brother whose murder-grudge over the stolen blessing ('I will kill my brother Jacob', 27:41) drove the flight, now coming with four hundred men"),
    ((32, 13), (22, 17), "'your seed as the sand of the sea' — Jacob holds God to the oath of the binding of Isaac, 'I will multiply your seed as the stars… and as the sand on the seashore' (22:17): you cannot let me be killed, if your own word is to stand"),
    ((32, 29), (30, 8),  "'you have PREVAILED' — vatukhal, the very word Rachel cried at Naphtali's birth, 'I have prevailed' (30:8); but where she prevailed over her sister by scheming, Jacob prevails over God by refusing to let go"),
    ((32, 31), (16, 13), "Peniel, 'I have seen God face to face' — the seeing-God that Hagar first named at her well, El Roi, 'the God who sees… have I even here seen him who sees me?' (16:13)"),

    # ---- Genesis 33 ----
    ((33, 10), (32, 31), "'I have seen your face as one sees the face of God' — Jacob rereads the Peniel night (32:31, 'I have seen God face to face') in his brother's forgiving face: he has survived both faces, God's and Esau's, and lived"),
    ((33, 11), (27, 36), "'take my BLESSING (birkhati)' — Jacob calls the gift a 'blessing,' quietly handing one back to the brother whose blessing he stole: 'he has taken my blessing!' (27:36). The one thing he took, he tries to restore"),
    ((33, 4),  (27, 41), "Esau ran, embraced, and wept — the brother who once said 'I will kill my brother Jacob' (27:41); the murder-vow undone in an embrace so complete that Jesus paints the prodigal's father in its very words (Luke 15:20)"),
    ((33, 3),  (27, 29), "Jacob bowed to the ground seven times — the man whom the stolen blessing had made lord, 'let your brothers bow down to you' (27:29), now on his face before the brother he cheated"),
    ((33, 19), (12, 7),  "Jacob buys land and builds an altar at Shechem — at the very tree of Moreh where Abraham built his FIRST altar in Canaan (12:6-7); the grandson claims the same ground with the second parcel a patriarch has ever owned in the land"),

    # ---- Genesis 44 ----
    ((44, 2),  (37, 24), "the trap is chapter 37 rebuilt to specification — Rachel's favoured son condemned alone, the other ten explicitly freed to go home unharmed. Once, offered exactly that, they took it and sat down to eat bread. This time every one of them turns the donkeys around"),
    ((44, 13), (37, 34), "'and they tore their garments' — the gesture Jacob made over the bloodied coat and Reuben made at the empty pit, now made by all ten, for the brother they are refusing to abandon"),
    ((44, 32), (43, 9),  "arav — 'your servant became SURETY for the boy.' The guarantor's pledge of 43:9 called in: a surety pays when the thing is lost, and the thing is lost"),
    ((44, 33), (37, 26), "'let your servant remain INSTEAD OF the boy as a slave' — the man who said 'what profit is there if we kill our brother? come, let us SELL him' now offers to take the fate he once sold his brother into"),
    ((44, 28), (37, 33), "tarof toraf, 'surely he is torn to pieces' — Jacob's cry over the bloodied tunic, quoted by one of the men who staged that scene, to the man it was staged about"),
    ((44, 29), (37, 35), "the grey head brought down to Sheol — the third and fourth uses in Genesis, all the same man's grief (37:35, 42:38, and twice here in Judah's mouth). KJV reads 'grave' in all four and hides that it is one unbroken lament"),
    ((44, 17), (18, 25), "chalilah, 'far be it' — the protest Abraham made to God over Sodom ('far be it from you to kill the righteous with the wicked'), now used by the brothers and then by Joseph, who uses it to REFUSE a collective sentence and force the choice"),

    # ---- Genesis 43 ----
    ((43, 9),  (42, 37), "Judah puts up HIMSELF ('I myself will be surety for him') where Reuben had offered his own two sons as collateral. Jacob refused Reuben flatly and says yes to this — the measure of the difference, and the payoff of the man built in ch. 38"),
    ((43, 11), (37, 25), "gum, balm and ladanum — word for word the cargo the Ishmaelite caravan was carrying down to Egypt on the day the brothers sold Joseph into it. Jacob now loads the same three commodities as a GIFT and sends them down the same road, to the son he thinks is dead"),
    ((43, 23), (37, 4),  "shalom — 'PEACE to you, do not be afraid.' The word the brothers 'could not speak' to Joseph, and the errand their father sent him on (37:14), spoken over them in Egypt by a servant of the man they sold"),
    ((43, 30), (43, 14), "rachamim — Jacob prays that God will give them COMPASSION before the man; sixteen verses later that man's compassion 'grew warm' and he leaves the room to weep. The prayer is answered in a body Jacob does not know is his son's"),
    ((43, 32), (39, 6),  "the Egyptian table rule — 'the Egyptians cannot eat bread with the Hebrews' settles the clause left open at 39:6, where Potiphar knew nothing of his household 'except the bread he ate'"),
    ((43, 26), (37, 7),  "they bow again, twice in three verses — what was an insufferable dream has become the ordinary daily posture of ten adult men doing business"),
    ((43, 14), (17, 1),  "El Shaddai — Jacob prays by the covenant name last heard when God renamed Abram, the God who gives children to people who have none"),

    # ---- Genesis 42 ----
    ((42, 6),  (37, 7),  "'and they bowed down to him, faces to the ground' — the dream of the sheaves, fulfilled twenty-two years later in a single clause, and fulfilled THROUGH the pit that was meant to prevent it"),
    ((42, 7),  (27, 23), "nakar's fourth turn: Joseph 'recognized them AND MADE HIMSELF UNRECOGNIZABLE' (vayyakkirem / vayyitnakker, same root, opposite directions). Isaac failed to recognize the son in front of him; Jacob recognized a coat that lied; Judah recognized his own seal; Joseph knows the faces perfectly and chooses not to be known"),
    ((42, 21), (37, 24), "'we saw the distress of his soul when he PLEADED with us' — Genesis never reported this. At the pit the brothers stripped him, threw him in, and sat down to eat bread; the narrator said nothing about the boy in the hole. The pleading is withheld for five chapters so the reader hears it for the first time in the mouths of the men who ignored it"),
    ((42, 9),  (37, 5),  "'and Joseph remembered the dreams' — zakhar, the book's rescue-verb, fires at the exact moment he decides to accuse them. Whether what follows is vengeance or a controlled test is deliberately withheld until ch. 45"),
    ((42, 13), (37, 30), "'and the one is not' — einennu, the euphemism the brothers hide behind, and the same word Reuben cried at the empty pit ('the boy is not'). They say it to the man they are talking about"),
    ((42, 38), (37, 35), "'you would bring down my grey head in sorrow to Sheol' — word for word what Jacob said the day the bloodied coat came home. Twenty-two years, and the sentence has not changed; KJV reads 'grave' in both places and hides that it is the same lament"),
    ((42, 24), (34, 25), "Simeon is the one bound — the text never says why. He is the second-oldest (so taking him spares Reuben, who tried to save Joseph), and he is one of the two who emptied Shechem of every male"),

    # ---- Genesis 41 ----
    ((41, 9),  (40, 23), "zakhar — 'I bring my faults to REMEMBRANCE today.' Two years after the chapter that ended 'he did not remember Joseph, and he forgot him,' the same verb finally fires, prompted not by conscience but by a king in a bad mood and a room with no answers"),
    ((41, 14), (37, 24), "bor, 'the pit' — the third and last time the word is used of Joseph, and the only time he comes UP out of one. Thrown into a pit at Dothan, he called his cell a pit (40:15), and now they run him out of the pit to stand before a king"),
    ((41, 32), (37, 5),  "'the dream was DOUBLED… because the thing is established from God' — Joseph explains to a foreign king the exact rule that governs his own life. His two dreams, sheaves and stars, were the doubled pair his brothers hated him for; by this rule they were never boasting but a settled decree, and the brothers will bow"),
    ((41, 16), (40, 8),  "'Not I' — biladai. He said it to two prisoners ('do not interpretations belong to God?'); he says it again to the most powerful man on earth, at the one moment when overstating the gift would have paid"),
    ((41, 16), (37, 4),  "shalom — Joseph promises Pharaoh an answer for his PEACE, the very word his brothers could not speak to him and the errand his father sent him on (37:14)"),
    ((41, 8),  ("Daniel", 1, 20), "the chartummim fail — and the same word, the same failure, recurs in Babylon's court, where the king's experts are outmatched by a Hebrew captive (Daniel 1:20; 2:2). Genesis 41 is the template Daniel is written on"),
    ((41, 42), (38, 18), "the signet — the last man in this book to hand one over was Judah, surrendering his identity to a stranger at a roadside; here a king gives his away to make a slave into himself"),
    ((41, 43), (37, 7),  "Egypt bows before Joseph's chariot while a herald shouts — the sheaves of his own dream 'came around and bowed down to my sheaf'"),

    # ---- Genesis 40 ----
    ((40, 15), (37, 24), "bor, 'the pit' — Joseph describes his Egyptian cell with the identical word used of the dry cistern his brothers threw him into at Dothan. The KJV, ASV and NIV all switch to 'dungeon' here and hide it; this translation reads 'pit' in both"),
    ((40, 14), (39, 21), "chesed — two verses from the end of the previous chapter God 'extended kindness' to Joseph in this same jail; now Joseph asks a man for the same thing, and the chapter's last verse is the answer"),
    ((40, 23), (8, 1),   "zakhar, to remember — the covenant verb. 'God REMEMBERED Noah' and the waters went down; 'God remembered Abraham' (19:29); 'God remembered Rachel' (30:22). Every divine remembering in Genesis is followed by a rescue. Here it is handed to a man, and he forgets"),
    ((40, 5),  (37, 5),  "dreams return — absent since his brothers threw him in a pit for having them. The dreamer has become the interpreter, and this time the dreams are somebody else's"),
    ((40, 15), (14, 13), "'the land of the Hebrews' — Canaan named by the outsider-word, ivri, last heard of Abram; Joseph uses it of home while standing in Egypt"),
    ((40, 3),  (39, 1),  "'the house of the chief of the executioners' — Joseph is still inside Potiphar's establishment, and it is Potiphar who appoints him to attend the two prisoners: the same verb used when he first put Joseph over his house (39:4)"),

    # ---- Genesis 39 ----
    ((39, 6),  (29, 17), "yefeh to'ar vifeh mar'eh — 'beautiful in form and lovely to look at,' word for word the Hebrew used of RACHEL, and of no one else in the Bible. Joseph has his mother's face, and the narrator mentions it one verse before his master's wife looks at him"),
    ((39, 12), (37, 23), "the second garment. His brothers stripped his ornamented tunic and used it to tell his father a lie; a second garment is taken off him, kept back deliberately, and used to tell his master another. Twice stripped, twice the cloth speaks against him, and both times he says nothing"),
    ((39, 5),  (12, 3),  "'in you all the families of the earth will be blessed' — the promise operating in miniature and out of sight: an Egyptian slave-owner's whole estate is blessed 'for Joseph's sake,' and he never learns why"),
    ((39, 14), (14, 13), "ivri, 'Hebrew' — the outsider-word, first used of Abram and now spat by an Egyptian woman rallying the household staff: 'he has brought US in a HEBREW man'"),
    ((39, 14), (21, 9),  "letsacheq, 'to laugh at' — the laughter-root that named ISAAC, turned cruel once already when Sarah saw Ishmael metsacheq and demanded he be cast out, and now weaponised against Rachel's son by a stranger"),
    ((39, 9),  (20, 6),  "'sin against God' — Joseph names the wrong as God's before it is Potiphar's; at Gerar it was God who said 'I kept you from sinning against me,' to a pagan king in a dream about another man's wife"),
    ((39, 21), (19, 19), "chesed, covenant kindness — 'extended' to Joseph in a cell, the same faithful loyalty Lot invoked when he was pulled out of Sodom"),

    # ---- Genesis 38 ----
    ((38, 25), (37, 32), "haker-na, 'recognize, please' — Judah and his brothers sent their father a bloodied tunic with these two words; Tamar sends Judah his own seal and staff with the same two. He is answered in his own sentence, and the props rhyme: a garment and a goat used to make a father believe a lie, a seal and a staff used to make a son admit a truth"),
    ((38, 16), (27, 23), "'he did not know that she was his daughter-in-law' — the third turn of nakar in three generations: Isaac did NOT recognize the son in front of him, Jacob DID recognize a coat that was lying to him, and Judah recognizes only what carries his own signature"),
    ((38, 17), (37, 31), "a kid of the goats — the family's instrument of deception offered as a fee. His brothers slaughtered a goat to soak Joseph's tunic; his father wore goatskins to rob a blind man (27:16); Judah walks into a deception on the very animal he has used to run one"),
    ((38, 12), (37, 35), "nacham — Jacob 'REFUSED to be comforted' for the son Judah sold; eleven verses later Judah buries a wife, 'was comforted,' and goes up to a sheepshearing. The narrator sets the same verb on both men and says nothing"),
    ((38, 14), (24, 65), "the veil — Rebekah covered herself when she first saw Isaac; Leah's wedding-night substitution (29:25) only works because a bride's face is hidden. This house knows exactly what a veil is for"),
    ((38, 26), (15, 6), "tsedaqah, 'righteousness' — the word counted to Abram when he believed is now spoken by a patriarch, in public, about the Canaanite widow who tricked him: 'she is more righteous than I'"),
    ((38, 9),  (6, 11), "shichet, to RUIN — the flood's own verb (the earth was ruined, so God resolved to ruin it) used of what Onan does on the ground; this translation keeps the root audible in both places"),
    ((38, 29), (25, 26), "twins struggling over who comes out first — Jacob was born gripping Esau's heel, having lost that race; here even the midwife's scarlet marker cannot make the birth-order hold"),
    ((38, 18), ("Jeremiah", 22, 24), "the chotam, a signet — Judah hands his over to a stranger as a pledge and nearly loses it for good; Jeremiah's Coniah IS the signet, torn off God's right hand and thrown away"),

    # ---- Genesis 37 ----
    ((37, 13), (22, 1),  "hineni, 'Here I am' — the answer of total availability, spoken at the book's two darkest hinges: Abraham at the Aqedah, and now a beloved son sent by his father toward a death the reader can already see. At Moriah a voice from heaven stopped the knife; in Genesis 37 God is not named once"),
    ((37, 1),  (23, 4),  "'the land of his father's sojournings' — megurim, from ger: Jacob SETTLES in a land of not-settling, the same ache as Abraham's confession at Machpelah, 'I am a resident alien among you' — while Esau, one verse earlier, owns Seir outright"),
    ((37, 2),  (36, 1),  "'these are the toledot of Jacob' — the last of the book's ten 'generations' headings, and the one that breaks the pattern: no genealogy follows it, only a boy and a grudge. Genesis stops listing and becomes a story"),
    ((37, 8),  (3, 16),  "mashal, 'rule' — the brothers' sneer ('will you really RULE over us?') is the verb spoken over the woman in the garden and over Cain's crouching sin (4:7): from the beginning, the Bible's word for who is on top of whom"),
    ((37, 31), (27, 16), "the goat and the garment, turned back on him — Jacob deceived his blind father wearing his brother's clothes and the skins of goat kids; his sons deceive him with his son's tunic and the blood of a goat. Genesis Rabbah: 'with a kid he deceived, and with a kid he was deceived'"),
    ((37, 32), (27, 23), "haker-na, 'recognize, please' — the verb that FAILED at Isaac's bedside ('he did not recognize him') now succeeds on a bloodied tunic: the father who could not identify a son who was present identifies a son who is not"),
    ((37, 26), ("Jeremiah", 22, 17), "betsa — not neutral profit but the prophets' word for unjust gain. Judah sells the murder as a bad deal ('what GAIN is it?'); Jeremiah aims the same noun at a king of Judah's own line whose 'eyes and heart are on nothing but your unjust gain'"),
    ((37, 2),  ("Jeremiah", 20, 10), "dibbah, a 'bad report' — the whispering-campaign word. Joseph carries it to his father; Jeremiah hears it circling him from the men plotting his death"),
    ((37, 35), (5, 29),  "nacham, 'comfort' — the hope Lamech named into his son Noah, 'this one will bring us comfort,' now refused: 'he refused to be comforted.' Jeremiah will hear Rachel, Joseph's own mother, refuse it too (31:15 → Matthew 2:18)"),
    ((37, 26), (4, 10),  "'and cover his blood' — the first murder in this book left blood that was NOT covered, crying out from the ground. Judah's plan is precisely to make the ground keep quiet"),
    ((37, 36), ("Daniel", 1, 3), "a Hebrew youth taken young into a world empire and handed to the chief official of a foreign king — Potiphar, 'chief of the executioners,' has an exact Babylonian counterpart in Arioch (Daniel 2:14). Both boys will read dreams no one else can read and rise to stand second in the kingdom"),
    ((37, 12), (34, 25), "the brothers pasture the flock at SHECHEM — the town Simeon and Levi emptied of every male three chapters ago, after which Jacob said 'you have made me a stench to the inhabitants of the land.' The text names the place and says nothing else"),

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
    (("Ruth", 1, 1), ("Judges", 1, 1), "'in the days when the judges judged' — Ruth is set inside the era of Judges, and reads as its quiet counter-story of chesed"),
    (("Ruth", 1, 14), (2, 24), "'clung to her' — dabaq, the Genesis 2:24 marriage verb, turned to a daughter-in-law's loyalty"),
    (("Ruth", 1, 6), (21, 1), "paqad, 'Jehovah had visited his people' — the visitation verb of Sarah's son, now emptying the famine from the House of Bread"),
    (("Ruth", 1, 20), (17, 1), "Shaddai, 'the Almighty' — the old patriarchal name of God from the covenant with Abram, reached for in Naomi's grief"),
    (("Jude", 1, 11), (4, 8), "'the way of Cain' — the first murder (Genesis 4), Jude's first archetype of rebellion"),
    (("Jude", 1, 7), (19, 24), "Sodom and Gomorrah 'undergoing the punishment of eternal fire' — the fire and sulphur of Genesis 19"),
    (("Jude", 1, 14), (5, 24), "'Enoch, the seventh from Adam' — the man who 'walked with God, and was not' (Genesis 5:24), here the named source of a prophecy"),
    (("Jeremiah", 1, 5), (2, 7), "'before I formed you' — yatsar, the potter's verb that shaped the man from the dust (Genesis 2:7)"),
    (("Jeremiah", 1, 16), ("Jeremiah", 22, 9), "'forsaking me… other gods' — the very indictment the tariff of the last kings turns on (Jer 22:9)"),
    (("Jeremiah", 1, 17), ("Jeremiah", 20, 11), "'do not be shattered' / 'Jehovah is with me' — the fortress promise Jeremiah clings to in his darkest confession (Jer 20:11)"),
    (("Daniel", 2, 44), ("Daniel", 12, 3), "the everlasting kingdom that 'shall stand forever' — the hope that ends in the wise shining 'like the stars forever' (Dan 12:3)"),
    (("Daniel", 2, 28), ("Daniel", 12, 4), "'what will be in the latter days' — the horizon Daniel is told to seal up 'until the time of the end' (Dan 12:4)"),
    (("Daniel", 2, 21), ("Daniel", 11, 2), "'he removes kings and sets up kings' — the sovereignty played out in detail through the kings of Persia and Greece (Dan 11)"),
    (("1 Samuel", 1, 10), ("Ruth", 1, 20), "'bitter in soul' — the same bitterness Naomi named over herself, calling herself Mara (Ruth 1:20)"),
    (("1 Samuel", 1, 19), (30, 22), "'Jehovah remembered her' — zakar, the covenant verb that opened Rachel's womb (Genesis 30:22)"),
    (("1 Samuel", 1, 11), ("Luke", 1, 48), "'look on the affliction of your servant' — the note Mary's Magnificat, built on Hannah's song, will strike: 'he looked on the low estate of his bondslave' (Luke 1:48)"),
    (("Exodus", 4, 10), ("Jeremiah", 1, 6), "'not a man of words… heavy of mouth' — the reluctant prophet's plea, sounded again by Jeremiah, 'I am only a youth' (Jer 1:6)"),
    (("Exodus", 4, 12), ("Exodus", 3, 14), "'I will be with your mouth' — ehyeh, the same verb as the Name revealed at the bush, 'I will be what I will be' (Ex 3:14)"),
    (("Exodus", 4, 31), (50, 24), "paqad — Jehovah 'visited' Israel and saw their affliction, the very verb Joseph swore by over his coffin at the end of Genesis (50:24)"),
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
    ("Mark", 1, 11, "“You are my beloved Son; in you I am well pleased.” King and servant welded in one sentence — Psalm 2 and Isaiah 42."),
    ("Mark", 1, 15, "“The time has been fulfilled, and the kingdom of God has drawn near.” Jesus' first recorded words, and a manifesto."),
    ("Mark", 1, 41, "“Moved with anger, he stretched out his hand and touched him.” Angry AT the disease; the touch is for the man."),
    ("Judges", 1, 7, "“As I have done, so God has repaid me.” A mutilated king pronounces the sentence on his own cruelty."),
    ("Judges", 1, 19, "“Jehovah was with Judah… but he could not, because they had chariots of iron.” The excuse the book is documenting."),
    ("Judges", 1, 28, "“When Israel grew strong, they put the Canaanite to forced labour” — a people redeemed from slavery imposing it."),
    ("Joshua", 1, 8, "“You shall murmur over it day and night.” Not silent study — reading aloud under the breath, continually."),
    ("Joshua", 1, 9, "“Be strong and resolute… for Jehovah your God is with you wherever you go.” The reason is never his competence."),
    ("3 John", 1, 4, "“I have no greater joy than this: to hear that my children are walking in the truth.”"),
    ("3 John", 1, 8, "“Fellow workers with the truth.” The one who funds the mission is a partner in it, not a spectator."),
    ("3 John", 1, 15, "“Greet the friends by name.” The smallest, most human instruction in the New Testament's letters."),
    ("2 John", 1, 3, "“Grace, mercy, peace WILL be with us.” Every other letter makes this a wish; here it is a statement of fact."),
    ("2 John", 1, 6, "“This is love: that we walk according to his commandments.” Love defined as a road walked, not a feeling described."),
    ("2 John", 1, 12, "“I hope to come and speak mouth to mouth.” A letter's own admission that a letter is not enough."),
    ("Deuteronomy", 1, 2, "“Eleven days from Horeb.” The next verse says “in the fortieth year.” Nothing else needs to be said."),
    ("Deuteronomy", 1, 17, "“You shall not shrink before any man, for the judgement is God's.” A judge is handling something that is not his."),
    ("Deuteronomy", 1, 31, "“As a man carries his son.” Said directly against the accusation that God brought them out because he hated them."),
    (50, 17, "“And Joseph wept when they spoke to him.” Seventeen years on, his brothers still think he might kill them. That is what he weeps at."),
    (50, 20, "“You devised evil against me; God devised it for good.” One verb, two agents, both intentions real — and the guilt left in."),
    (50, 26, "“And he was put in a coffin in Egypt.” The last words of Genesis. Nothing promised has arrived yet."),
    (49, 10, "“The sceptre shall not depart from Judah.” The most disputed line in Genesis — four readings, and the note takes no vote."),
    (49, 18, "“For your salvation I have waited, Jehovah.” A dying man stops mid-prophecy, halfway down the list of his sons, and prays."),
    (49, 31, "“And there I buried Leah.” Genesis never told us she died. He asks to be laid beside her."),
    (48, 14, "“He crossed his hands knowingly.” The Hebrew verb for crossing is the verb for acting with insight — the gesture and the intent are one word."),
    (48, 16, "“The angel who has redeemed me from all evil.” The first time the Bible uses its word for a redeemer, and it is a grandfather blessing two boys."),
    (48, 19, "“I know, my son, I know.” The man who once deceived a blind father, now blind, refusing to be corrected."),
    (47, 9, "“Few and evil have been the days of the years of my life.” He is 130, and he calls it few."),
    (47, 25, "“You have kept us alive!” — said gratefully, by people who have just sold themselves into servitude."),
    (47, 27, "“And they were fruitful and multiplied greatly.” The creation blessing, in the same chapter Egypt loses everything."),
    (46, 3, "“Do not fear to go down to Egypt.” The permission the family needed — God had forbidden Isaac the same journey."),
    (46, 4, "“I myself will go down with you… and I myself will surely bring you up again.” The exile and the return promised in one breath."),
    (46, 30, "“Let me die this time, after my seeing your face.” Not a wish to die — a statement that the thing that made death unbearable is gone."),
    (45, 3, "“I am Joseph. Is my father still alive?” — and his brothers could not answer him."),
    (45, 8, "“It was not you who sent me here, but God” — said nine words after “whom you sold.” Both are true."),
    (45, 24, "“Do not be agitated on the way.” The last thing he says to them, and it may mean: don't spend the trip arguing about whose fault it was."),
    (45, 28, "“Enough! Joseph my son is still alive.” An old man stops asking questions and starts packing."),
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
    (31, 3, "The call home: 'Return to the land of your fathers and to your kindred, and I will be with you' — the Bethel promise coming due, twenty years on."),
    (31, 49, "The Mizpah stone — less a blessing than a fence: 'May Jehovah watch between me and you, when we are hidden from each other' — two rivals asking God to police a truce neither will keep on trust."),
    (32, 27, "The clinging that becomes a blessing: 'I will not let you go unless you bless me' — the man who once stole a blessing now demands one, wounded, holding on in the dark."),
    (32, 29, "The name that is a verdict: 'Your name shall no longer be Jacob, but Israel; for you have striven with God and with men, and have prevailed.'"),
    (33, 4, "Grace outran fear: 'And Esau ran to meet him, and embraced him, and fell on his neck and kissed him; and they wept' — the brother who had sworn to kill him."),
    (33, 10, "Forgiveness with the face of God in it: 'I have seen your face as one sees the face of God, and you have received me favorably.'"),
    (34, 7, "The text names the crime a crime: 'he had done an outrage in Israel, a thing that should not be done' — the newborn nation's first reckoning with an atrocity from within."),
    (35, 3, "Jacob names his God by what God has done: 'an altar to the God who answered me in the day of my distress, and was with me on the way that I went.'"),
    (35, 18, "Grief turned to blessing over a grave: the dying mother names him Ben-oni, 'son of my sorrow' — the father renames him Benjamin, 'son of the right hand.'"),
    (36, 7, "The old rivalry ends in room made, not blood: too much to hold them both, Esau gathers everything and leaves Canaan to his brother, taking Seir for himself."),
    (37, 13, "“Here I am.” The same two syllables Abraham gave at the Aqedah — now from a boy being sent, unarmed, to brothers who cannot speak to him in peace."),
    (37, 24, "“And the pit was empty — there was no water in it.” The Bible's most famous redundant sentence: not a drowning, a stone jar. Then they sat down to eat."),
    (38, 26, "“She is more righteous than I.” The first honest sentence Judah ever speaks — and the hinge of his whole life."),
    (38, 25, "“Recognize, please.” The two words Judah used to break his father, handed back to him with his own seal attached."),
    (39, 2, "“And Jehovah was with Joseph.” Said four times in one chapter — and never once in the chapter where he was sold."),
    (39, 9, "“How then could I do this great evil, and sin against God?” The wrong he names is against someone who is not in the room."),
    (40, 8, "“Do not interpretations belong to God?” Said by a prisoner to two courtiers who miss their professionals."),
    (40, 23, "“And he forgot him.” The whole chapter turns on a verb that, every other time Genesis uses it, is followed by a rescue."),
    (41, 16, "“Not I — God will answer.” The one moment when overstating his gift would have paid, and he refuses the credit first."),
    (41, 32, "Why a dream comes twice: “the thing is established from God, and God is hurrying to do it.”"),
    (42, 21, "“Truly we are guilty concerning our brother.” Twenty-two years later — and the first time we learn he pleaded."),
    (42, 23, "“They did not know that Joseph was listening, for the interpreter was between them.”"),
    (43, 9, "“I myself will be surety for him.” Judah puts up himself where Reuben had offered his own sons."),
    (43, 30, "“His compassion grew warm toward his brother” — rachamim, the word built on the womb."),
    (44, 33, "“Let your servant remain instead of the boy.” The man who once sold a brother offers to take his place."),
    (44, 34, "“How can I go up to my father, and the boy not with me?” The end of the longest speech in Genesis."),
    ("Luke", 1, 37, "“No word will be impossible with God.” The sentence spoken to Sarah at Mamre, carried now to a girl in Nazareth."),
    ("Luke", 1, 38, "“Behold, the bondslave of the Lord; may it happen to me according to your word.” Where a priest was struck dumb, a girl says yes."),
    ("Luke", 1, 46, "“My soul magnifies the Lord.” The Magnificat — a teenage girl sings the great reversal, built on Hannah's song."),
    ("Luke", 1, 52, "“He has brought down rulers from thrones and lifted up the lowly.” The most dangerous poem in the Gospels."),
    ("Luke", 1, 78, "“The dawn from on high will visit us” — ANATOLE: both the rising sun and the promised Branch of David."),
    ("Ruth", 1, 16, "“Your people are my people, and your God my God.” A Moabite widow's covenant, sworn by the name of Jehovah."),
    ("Ruth", 1, 17, "“May Jehovah do so to me, and more also, if anything but death parts me from you.” Ruth seals her oath."),
    ("Ruth", 1, 20, "“Call me Mara, for the Almighty has dealt very bitterly with me.” Naomi turns her own sweet name inside out."),
    ("Ruth", 1, 21, "“I went out full, and Jehovah has brought me back empty” — said while Ruth, the whole book's redemption, stands beside her."),
    ("Ruth", 1, 22, "“They came to Bethlehem at the beginning of the barley harvest.” The famine over; the field of Boaz one verse away."),
    ("Jude", 1, 3, "“Contend for the faith once for all delivered to the holy ones.” Jude's whole letter in a line — hapax, handed over once, complete."),
    ("Jude", 1, 21, "“Keep yourselves in the love of God, waiting for the mercy of our Lord Jesus Christ.” The fierce letter's tender center."),
    ("Jude", 1, 24, "“To him who is able to keep you from stumbling, and to make you stand before his glory blameless, with great joy.”"),
    ("Jude", 1, 25, "“To the only God our Savior… be glory, majesty, dominion, and authority, before all time and now and forever.” The great doxology."),
    ("Jeremiah", 1, 5, "“Before I formed you in the belly I knew you… a prophet to the nations I appointed you.” The call that reached back before the womb."),
    ("Jeremiah", 1, 8, "“Do not be afraid before them, for I am with you to deliver you.” The promise that bookends Jeremiah's whole call."),
    ("Jeremiah", 1, 10, "“To uproot and to tear down, to destroy and to overthrow, to build and to plant.” The mission of the whole book in six verbs."),
    ("Jeremiah", 1, 12, "“You have seen well, for I am watching over my word, to do it.” The almond (shaqed) and the Watcher (shoqed)."),
    ("Daniel", 2, 21, "“He changes the times and the seasons; he removes kings and sets up kings.” Daniel's thesis: God, not the empires, turns history."),
    ("Daniel", 2, 22, "“He reveals the deep and the hidden things; he knows what is in the darkness, and the light dwells with him.”"),
    ("Daniel", 2, 28, "“There is a God in heaven who reveals mysteries.” Against gods 'whose dwelling is not with flesh' — one who speaks to a man."),
    ("Daniel", 2, 44, "“The God of heaven shall set up a kingdom that shall never be destroyed… and it shall stand forever.” The stone that became a mountain."),
    ("1 Samuel", 1, 11, "“If you will look on the affliction of your servant and remember me… I will give him to Jehovah all the days of his life.” Hannah's vow."),
    ("1 Samuel", 1, 15, "“I have poured out my soul before Jehovah.” Hannah, praying silently, mistaken for a drunk by the priest."),
    ("1 Samuel", 1, 20, "“She called his name Samuel: because I have asked him of Jehovah.”"),
    ("1 Samuel", 1, 27, "“For this child I prayed, and Jehovah has granted me my petition that I asked of him.”"),
    ("Exodus", 4, 11, "“Who made man's mouth?… Is it not I, Jehovah?” God's answer to Moses' 'I am slow of speech.'"),
    ("Exodus", 4, 12, "“Now go; I will be with your mouth and teach you what you shall speak.”"),
    ("Exodus", 4, 22, "“Israel is my firstborn son… let my son go, that he may serve me.” The tenth plague announced at the outset."),
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
# ---------------------------------------------------------------------------
# REGIONS — territories drawn with a visible BOUNDARY, not a pin.
#
# A pin is the wrong shape for a country. "Esau dwelt in the hill country of
# Seir" is a statement about a TERRITORY, and a marker dropped in the middle of
# it tells the reader nothing about where it began or ended. Each region here
# carries a boundary polygon in real (lat, lon), drawn by build.render_region_map
# as a self-contained inline SVG over a shared Levant basemap (coast, Dead Sea,
# Sea of Galilee, Jordan, Arabah) — no map library, no external tiles, same
# approach as ROUTES.
#
# ⚠️ HONESTY RULE, and it is not decoration: ancient borders were fluid, mostly
# undefined in the modern sense, and shifted over centuries. These outlines are
# reconstructions from the biblical boundary lists (Numbers 34 for Canaan),
# Egyptian and Assyrian records, and the hard geography — the rift valley, the
# wadis, the desert fringe — which is the part that genuinely does not move.
# Every region states its own `caveat`, every outline is drawn DASHED to signal
# approximation, and no region may be added here without a defensible basis.
# Where a location is genuinely unknown (Eden, Havilah), it gets NO polygon —
# the same discipline as the atlas's "no guessed pin."
#
#   boundary : [(lat, lon), ...] closed implicitly; the dashed outline
#   sites    : [(lat, lon, "Label"), ...] fixed points inside/near it
#   caveat   : the honest sentence printed under the map
REGIONS = [
    dict(slug="edom", name="Edom (Seir)", ref=(36, 8),
         blurb="The red-sandstone highlands east of the Arabah — Esau's country, and the one the book "
               "has just spent forty-three verses cataloguing.",
         boundary=[(30.95, 35.40), (31.00, 35.70), (30.85, 35.88), (30.50, 35.92),
                   (30.15, 35.85), (29.85, 35.65), (29.60, 35.35), (29.55, 35.05),
                   (29.85, 35.12), (30.30, 35.25), (30.65, 35.32)],
         sites=[(30.7375, 35.6069, "Bozrah"), (30.3285, 35.4444, "Sela / Petra"),
                (29.55, 35.00, "Ezion-geber"), (30.65, 35.60, "Teman")],
         caveat="Edom's core is the highland block east of the Arabah, bounded north by the Wadi al-Hasa "
                "(the biblical Zered) and running south to the Gulf of Aqaba — the rift and the wadi are "
                "real and fixed, the eastern edge simply fades into desert with no line to draw. Later "
                "Edomites spread west of the Arabah into the Negev, the region Greeks and Romans called "
                "Idumea; that expansion is not shown here."),

    dict(slug="canaan", name="Canaan", ref=(12, 5),
         blurb="The land promised to Abraham and walked by all three patriarchs — the strip between the "
               "Mediterranean and the Jordan rift.",
         boundary=[(33.20, 35.20), (33.25, 35.65), (32.80, 35.62), (32.40, 35.56),
                   (31.90, 35.53), (31.50, 35.47), (31.05, 35.40), (30.75, 35.10),
                   (30.65, 34.55), (31.10, 34.28), (31.55, 34.52), (32.10, 34.78),
                   (32.55, 34.92), (33.05, 35.10)],
         sites=[(31.7683, 35.2137, "Jerusalem / Salem"), (32.2137, 35.2853, "Shechem"),
                (31.5326, 35.0998, "Hebron"), (31.8700, 35.4440, "Jericho"),
                (31.2518, 34.7913, "Beersheba"), (31.9309, 35.2203, "Bethel")],
         caveat="Drawn from the boundary list of Numbers 34 — the Mediterranean on the west, the Jordan "
                "and the Dead Sea on the east, the Wadi of Egypt and the wilderness of Zin on the south — "
                "which is the Bible's own definition of the land, not a political border that ever "
                "existed on the ground. The northern limit ('Lebo-hamath') is the least certain edge and "
                "is drawn conservatively."),

    dict(slug="gilead", name="Gilead", ref=(31, 21),
         blurb="The wooded Transjordan highlands where Jacob and Laban made their heap of witness — good "
               "grazing country, cut in half by the Jabbok gorge.",
         boundary=[(32.72, 35.60), (32.75, 36.05), (32.40, 36.15), (32.00, 36.00),
                   (31.80, 35.75), (31.80, 35.55), (32.10, 35.57), (32.45, 35.57)],
         sites=[(32.13, 35.68, "the Jabbok"), (32.20, 35.61, "Succoth"),
                (32.5578, 35.9906, "Ramoth-gilead"), (32.3100, 35.7300, "Mizpah / Galeed")],
         caveat="Gilead is a geographic name rather than a fixed state — the highlands east of the Jordan "
                "between the Yarmuk and the north end of the Dead Sea, split by the Jabbok into a northern "
                "and southern half. Its western edge (the Jordan) is exact; its eastern edge dissolves "
                "into the desert."),

    dict(slug="goshen", name="Goshen", ref=(45, 10),
         blurb="The corner of the eastern Nile Delta Joseph gives his family — good pasture, close to the "
               "government, and just far enough out of Egypt proper to stay a separate people.",
         boundary=[(30.30, 31.55), (30.35, 32.35), (30.60, 32.45), (30.95, 32.30),
                   (31.15, 32.00), (31.20, 31.60), (31.00, 31.30), (30.65, 31.25)],
         sites=[(30.79, 31.82, "Tell el-Dab'a (Avaris)"),
                (30.55, 32.05, "Wadi Tumilat"),
                (30.57, 31.51, "Bubastis")],
         caveat="Drawn approximately, and it has to be. GOSHEN is not an Egyptian word and appears in no "
                "Egyptian text \u2014 there is no ancient map, boundary stone or administrative list to copy "
                "from. What can be reconstructed is a general area rather than a border: the Bible places it "
                "in the eastern Delta, on the road to Canaan (46:28-29), with pasture good enough for large "
                "flocks and near enough to the seat of government to be provisioned through a famine. The "
                "Wadi Tumilat \u2014 the fertile east-west corridor running from the Delta toward the "
                "Bitter Lakes \u2014 fits all three, and Tell el-Dab'a at its north-west end was a genuine "
                "Semitic settlement in exactly this region in the Middle Bronze Age. The outline shown is "
                "that reasoning, not a documented frontier.",
         ),
    dict(slug="midian", name="Midian", ref=(25, 2),
         blurb="The desert country of Abraham's sons by Keturah — caravan people east of the Gulf of Aqaba, "
               "and the land Moses will flee to and marry into.",
         boundary=[(29.30, 34.95), (29.35, 35.60), (29.10, 36.30), (28.60, 36.85),
                   (28.00, 36.95), (27.45, 36.40), (27.30, 35.80), (27.70, 35.35),
                   (28.30, 35.05), (28.80, 34.90)],
         sites=[(28.4767, 35.0219, "Al-Bad' (Madyan)"),
                (28.80, 36.07, "Qurayyah"), (29.55, 35.00, "Ezion-geber")],
         caveat="This is the loosest outline on the site, and it is drawn that way on purpose. Midian was a "
                "PEOPLE before it was ever a place — tent-dwelling herders and caravan traders whose range "
                "moved with their flocks and their routes, never a state with a frontier. What is shown is "
                "the traditional heartland in north-west Arabia (the Hejaz), east of the Gulf of Aqaba: the "
                "coast is real, and there are two genuine anchors inland — Al-Bad', identified with Madyan "
                "since antiquity (Ptolemy and Josephus both put a 'Madiana' on this coast), and Qurayyah, the "
                "oasis whose distinctive painted pottery archaeologists actually call Midianite Ware. "
                "Everything east of those is a guess at where desert stops being anyone's. And the Bible "
                "itself will not keep Midianites inside it: they raid deep into Canaan in Judges 6-8, camp "
                "beside Moab in Numbers 22, and Moses pastures his father-in-law's flock as far as Horeb. "
                "Read the shape as 'where Midian was at home,' not as a border."),

    dict(slug="negev", name="The Negev", ref=(12, 9),
         blurb="The dry south — the country Abraham keeps drifting into, and the half-desert Israel will "
               "later have to cross to enter the land from below.",
         boundary=[(31.35, 34.35), (31.30, 35.05), (31.00, 35.25), (30.65, 34.95),
                   (30.50, 34.60), (30.70, 34.30), (31.05, 34.28)],
         sites=[(31.2518, 34.7913, "Beersheba"), (30.68, 34.50, "Kadesh-barnea"),
                (31.40, 34.63, "Gerar")],
         caveat="The Negev is defined by rainfall, not by a treaty — it is the arid belt south of the "
                "Judean hills, roughly from the Beersheba basin down to the wilderness of Zin. The Hebrew "
                "word simply means 'the dry country' (and, by extension, 'the south'), so its boundary is "
                "a gradient, drawn here at the conventional limits."),
]

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
    "gen31": dict(era="patriarchs",
                  when="Jacob flees Haran with his family and flocks; Rachel steals the household gods; Laban pursues and is warned off in a dream, and the two schemers part at the treaty-heap of Galeed and Mizpah.",
                  clock="AM ≈ 2205 · c. 1740 BC — the very end of Jacob's twenty years with Laban (he is about 97). Warned by God to go home, he flees across the Euphrates toward Gilead; Laban overtakes him after a seven-day chase, they trade accusations and make a boundary-covenant, and Laban goes home for good. Jacob is now poised to re-enter Canaan and face the brother he cheated."),
    "gen32": dict(era="patriarchs",
                  when="Coming home, Jacob is met by angels at Mahanaim, sends a lavish gift ahead to the brother he fears, prays his first prayer, and wrestles a man at the Jabbok until dawn — crippled, blessed, and renamed Israel.",
                  clock="AM ≈ 2205 · c. 1739 BC — days after leaving Laban, on the threshold of Canaan, Jacob about 97. Terrified that Esau is coming with four hundred men, he divides his camp, prays, and sends waves of livestock as a gift; then, alone by night at the ford of the Jabbok, he is renamed Israel by the wrestler and limps away at sunrise to meet his brother. The turning point of his life and the moment the nation gets its name."),
    "gen33": dict(era="patriarchs",
                  when="The dreaded reunion becomes an embrace — Esau runs, weeps, and forgives; Jacob presses his 'blessing' back on him, then crosses into Canaan, settles at Shechem, buys land, and builds an altar, El-Elohe-Israel.",
                  clock="AM ≈ 2205 · c. 1739 BC — the morning after the Jabbok. Esau meets Jacob in peace and returns to Seir; Jacob crosses into Canaan for the first time in twenty years, camps at Succoth and then Shechem, buys a field, and raises an altar in his new name. The exile is over — but the family will not stay long at peace: the dark chapter at Shechem (ch. 34) waits, and the road to Bethel and Rachel's grave (ch. 35) lies just ahead."),
    "gen34": dict(era="patriarchs",
                  when="The dark chapter at Shechem — Dinah violated by the prince, the brothers' answer 'with deceit,' and the massacre of the whole town by Simeon and Levi, that Jacob rebukes only for the danger it brings on him.",
                  clock="AM ≈ 2206 · c. 1739 BC — soon after Jacob settles near Shechem. The prince Shechem violates Dinah; her brothers trick the men of the town into circumcision, and on the third day Simeon and Levi put them all to the sword and plunder the city, carrying off its women and children. The atrocity forces the family off the land and drives the flight to Bethel in the next chapter — and it is not forgiven: Jacob curses the two brothers' swords on his deathbed (49:5-7)."),
    "gen35": dict(era="patriarchs",
                  when="Jacob keeps his Bethel vow — the foreign gods buried, his name sealed Israel a second time under El Shaddai — then the road takes Deborah, Rachel (bearing Benjamin at Bethlehem), and at last old Isaac, buried by Esau and Jacob together.",
                  clock="AM ≈ 2207 · c. 1739 BC — God calls Jacob back to Bethel to keep the vow he made fleeing; he purges the camp of its foreign gods, builds the altar, and is confirmed as Israel, heir of El Shaddai's covenant. On the road south Rachel dies bearing Benjamin and is buried by Ephrath — Bethlehem; Reuben sins against his father's bed; the twelve sons are all named. Isaac's death at Hebron (age 180, buried by both his sons) is recorded here to close his generation, though by the numbers he outlives Joseph's sale by years."),
    "gen36": dict(era="patriarchs",
                  when="The book pauses to catalogue Esau — his Canaanite wives, his move to Seir, the clans and chiefs of Edom, the Horites they displaced, and eight kings who reigned in Edom before Israel had any king.",
                  clock="An undated genealogical interlude. Esau settles the red highlands of Seir 'away from his brother Jacob' — a peaceful separation, like Abraham and Lot's — and his line becomes the nation of Edom, with clan-chiefs and a non-dynastic line of kings. Amalek, Israel's perennial enemy, is born in it (36:12). The chapter clears the brother's account with honor before Genesis turns, in ch. 37, wholly to Joseph."),
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
    "luke1": dict(era="gospels",
                  when="Two annunciations and two songs — Gabriel to Zechariah in the temple and to Mary in Nazareth, the Visitation, the birth of John, the Magnificat and the Benedictus.",
                  clock="c. 6–5 BC, 'in the days of Herod the king' (Herod the Great died in 4 BC) — the six months before the birth of Jesus. Luke's preface (1:1–4) is the one place a Gospel opens with a dated, first-person dedication."),
    "jude1": dict(era="apostolic",
                  when="A single-chapter warning against false teachers who 'crept in unnoticed' — with the letter's two famous citations of works outside the canon (the Assumption of Moses, and 1 Enoch).",
                  clock="Hard to date; commonly placed c. AD 65-80. Its close kinship with 2 Peter 2, and its appeal to 'remember the words of the apostles' as an established past, put it a generation into the church."),
    "jer1": dict(era="exile",
                 when="The call of Jeremiah — known before the womb, made 'a prophet to the nations,' shown the almond branch and the boiling pot from the north.",
                 clock="627 BC, 'the thirteenth year of Josiah' (v2) — the start of a forty-year ministry that runs, per the superscription, to the fall of Jerusalem in 586 BC."),
    "dan2": dict(era="exile",
                 when="Nebuchadnezzar's dream of the four-metal statue and the stone cut without hands — the four kingdoms and the everlasting fifth; Daniel reveals both the dream and its meaning.",
                 clock="'The second year of Nebuchadnezzar' (v1), c. 603 BC — early in the Babylonian exile. The Aramaic section of the book (2:4b-7:28) begins here."),
    "1sam1": dict(era="monarchy",
                  when="The birth of Samuel — Hannah's barrenness, her vow at Shiloh, and the child asked of Jehovah and given back; the book that will give Israel its kings opens on an answered prayer.",
                  clock="Late in the period of the Judges, c. 1105 BC — a generation before Israel demands a king. 1 Samuel is the hinge from the judges to the monarchy."),
    "exod4": dict(era="exodus",
                  when="Moses given the three signs, appointed Aaron as his mouth, and sent back to Egypt — 'Israel is my firstborn son,' the tenth plague already spoken, and the strange night of the 'bridegroom of blood.'",
                  clock="c. 1446 BC on the early-date chronology this project foregrounds — the pharaoh of the oppression (Thutmose III) has died; Moses returns to Amenhotep II, the pharaoh of the Exodus."),
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
    dict(era="patriarchs", am="≈2205", trad="c. 1740 BC", event="Jacob flees Haran — Rachel steals the household gods; the treaty-heap at Galeed and Mizpah",
         note="Warned by God to return, and with Laban's goodwill soured, Jacob gathers his wives, eleven sons, and vast flocks and slips away across the Euphrates toward Gilead — while Rachel, unknown to him, steals her father's teraphim (household gods). Laban pursues for seven days, is warned in a dream to 'speak neither good nor bad,' and overtakes Jacob in the hills of Gilead; he ransacks the tents for his gods (Rachel hides them under the camel-saddle and sits on them) and finds nothing. After Jacob's long, bitter account of twenty years' faithful service, the two make a boundary-covenant and heap up stones — Laban names it in Aramaic (Jegar-sahadutha), Jacob in Hebrew (Galeed), the first Aramaic in the Bible — and set the Mizpah watchpost between them: 'May Jehovah watch between me and you.' In the morning Laban kisses his grandchildren and goes home for good; Jacob turns toward Canaan and the brother he wronged.",
         ref=("Genesis", 31, 49)),
    dict(era="patriarchs", am="≈2205", trad="c. 1739 BC", event="The wrestling at the Jabbok — Jacob crippled, blessed, and renamed Israel",
         note="On the threshold of Canaan, and terrified that Esau is marching to meet him with four hundred men, Jacob meets the angels of God at Mahanaim ('two camps'), sends a lavish gift of livestock ahead in waves to appease his brother, and prays the first recorded prayer of his life — 'I am too small (qatonti) for all the kindness you have shown your servant.' Then, having sent everyone across the ford of the Jabbok, 'Jacob was left alone, and a man wrestled with him until dawn' (Genesis 32). Crippled at the hip but refusing to let go without a blessing, he is given a new name: 'no longer Jacob, but Israel — for you have striven with God and with men, and have prevailed.' He names the place Peniel, 'the Face of God,' and limps away at sunrise to meet Esau. It is the turning point of the Jacob story and the moment the nation of Israel receives its name; the sinew of the thigh is not eaten to this day in memory of it.",
         ref=("Genesis", 32, 29)),
    dict(era="patriarchs", am="≈2205", trad="c. 1739 BC", event="Jacob and Esau reconciled; Jacob settles at Shechem and builds an altar",
         note="The reunion Jacob had dreaded turns out to be an embrace: Esau — who had once sworn to kill him — runs to meet him, falls on his neck, and weeps (Genesis 33). Jacob bows seven times, presses his lavish gift on his brother as a 'blessing' returned, and says, 'to see your face is like seeing the face of God.' They part in peace — Esau home to Seir, Jacob keeping a careful distance — and Jacob crosses into Canaan at last, camping at Succoth and then before the city of Shechem, where he buys a field for a hundred kesitah (the second parcel of the Promised Land any patriarch has owned, after Machpelah) and raises an altar, El-Elohe-Israel, 'El, the God of Israel' — claiming the God of his fathers under his own new name. The twenty-year exile is over.",
         ref=("Genesis", 33, 4)),
    dict(era="patriarchs", am="≈2206", trad="c. 1739 BC", event="The massacre at Shechem — Dinah violated; Simeon and Levi deceive the town and destroy it; the family is driven toward Bethel",
         note="The homecoming turns dark. Dinah, Jacob's daughter by Leah, is seized and violated by Shechem, the Hivite prince of the town where the family has settled (Genesis 34). His father Hamor proposes a merger of the two peoples, and Shechem offers any bride-price; but the sons of Jacob answer 'with deceit' (b'mirmah — the family's own besetting word), demanding that every male of the town be circumcised. On the third day, while the men lie in pain, Simeon and Levi — Dinah's full brothers — take their swords, kill every male, and carry off the city's wealth, women, and children. Jacob rebukes the two only for the danger they have made ('you have made me a stench to the land'); they answer with a question the narrator leaves unanswered — 'Should he treat our sister like a prostitute?' The atrocity ends the family's peace at Shechem and sets up the flight to Bethel, and it is never forgiven: on his deathbed Jacob curses the brothers' anger and foretells that Simeon and Levi will be 'scattered in Israel' (49:5-7).",
         ref=("Genesis", 34, 25)),
    dict(era="patriarchs", am="≈2207", trad="c. 1739 BC", event="Jacob returns to Bethel — the foreign gods buried, his name sealed Israel a second time; Rachel dies bearing Benjamin on the road to Bethlehem",
         note="Called back by God to the place of his fleeing vow, Jacob purges his camp of its foreign gods and earrings, buries them under the oak at Shechem, and goes up to Bethel to build the altar he had promised twenty years before (Genesis 35). There God appears again, blesses him, and confirms the name Israel and the covenant of El Shaddai — a nation, a company of nations, and kings to come. On the road south Rachel dies in hard labor bearing her second son; with her last breath she names him Ben-oni, 'son of my sorrow,' but Jacob renames him Benjamin, and buries her by the way to Ephrath — that is, Bethlehem — under a pillar that stands 'to this day.' The twelve sons are now all named — just before the family begins to tear itself apart over Joseph.",
         ref=("Genesis", 35, 19)),
    dict(era="patriarchs", am="≈2288", trad="c. 1716 BC", event="Isaac dies at Hebron, 180 years old — buried by Esau and Jacob together (recorded in Genesis 35, though he outlives Joseph's sale)",
         note="Isaac, 'old and full of days,' dies at 180 and is buried in the cave of Machpelah by his two sons — the twins who fought in the womb and over the birthright standing together at the grave, as Isaac and Ishmael had once buried Abraham (25:9). Genesis places his obituary in ch. 35 to close his generation before turning wholly to Joseph, but by the chronology he actually dies about a dozen years AFTER Joseph is sold into Egypt (ch. 37) — the same out-of-order mercy the book showed with Abraham, clearing the old man from the stage in peace before the years of grief begin.",
         ref=("Genesis", 35, 29)),
    dict(era="patriarchs", am="—", trad="—", event="Esau's line becomes Edom in Seir — the clans, chiefs, and kings of the brother-nation (a genealogical interlude)",
         note="Genesis pauses to catalogue Esau (ch. 36): his Canaanite wives and sons, his move to the red highlands of Seir 'away from his brother Jacob' (a peaceful separation, echoing Abraham and Lot's, 13:6), the clan-chiefs of Edom, the older Horite people they displaced (Deuteronomy 2:12), and eight kings who 'reigned in Edom before any king reigned over Israel' — a notably non-dynastic line, each king from a different city. Amalek, Israel's future arch-enemy, is quietly born in the roll (36:12). Undated by design: a genealogical bridge that settles Esau's account with honor before the book turns wholly to Joseph.",
         ref=("Genesis", 36, 1)),
    dict(era="patriarchs", am="≈2276", trad="c. 1728 BC", event="Joseph sold into Egypt at seventeen — the coat stripped, the pit at Dothan, twenty pieces of silver",
         note="Joseph's age is given exactly ('seventeen years old,' 37:2), and Genesis later dates him precisely enough to anchor the rest: he stands before Pharaoh at thirty (41:46), and Jacob comes down to Egypt in the second year of the famine, when Joseph is thirty-nine (45:6, 47:9) — so the sale sits about twenty-two years before the family's descent. The brothers grazed the flock at Shechem, the town Simeon and Levi had destroyed (ch. 34), and sold him to a caravan on the Gilead-to-Egypt spice road; the price, twenty shekels, is exactly the valuation Leviticus 27:5 later fixes for a male his age. Note that by this chronology Isaac is still alive — his obituary was placed early, in ch. 35, to clear his generation before the story turned to Joseph.",
         ref=("Genesis", 37, 28)),
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
    "Deuteronomy": dict(
        hebrew_name="דְּבָרִים",
        hebrew_translit="Devarim",
        hebrew_meaning="'Words' — from the opening line, 'these are the WORDS that Moses spoke.' The Hebrew "
                       "title names the book by the thing it actually is: speech. Moses does almost nothing "
                       "in Deuteronomy but talk.",
        greek_name="Δευτερονόμιον (Deuteronomion)",
        greek_meaning="'Second law' — the Greek and Latin (Deuteronomium) title, and a slightly misleading "
                      "one. It comes from the Septuagint's rendering of a phrase at 17:18 that in Hebrew "
                      "means 'a COPY of this instruction,' written out for the king. The name has stuck for "
                      "two thousand years; the book is not a second law but the first one preached.",
        tagline="The last words of Moses — three sermons and a song, delivered on the plains of Moab to a "
                "generation that did not see Egypt, by a man who will not cross the river with them.",
        genre="Preached law. Formally it is a series of ADDRESSES rather than narrative or statute: a covenant "
              "document in the shape of an ancient treaty, with historical prologue, stipulations, blessings "
              "and curses, witnesses and a written deposit — and, in the middle of it, some of the most "
              "affectionate prose in the Hebrew Bible.",
        canon="The fifth and final book of the TORAH (the Law / Pentateuch, the five books of Moses), and the "
              "fifth book of the Christian Old Testament. It is the hinge of the canon: the last book before "
              "Israel enters the land, and the one the rest of the Bible quotes most. Jesus answers all three "
              "temptations from it.",
        author="By ancient and traditional reckoning, Jewish and Christian alike, the addresses are the words "
               "of MOSES — the book presents them as such throughout, in the first person, and says he wrote "
               "them down (31:9, 24). The account of his own death in chapter 34 is traditionally credited to "
               "JOSHUA or to a later hand; the Talmud already discusses the question. Critical scholarship "
               "since the nineteenth century has widely identified Deuteronomy (or a core of it) with the "
               "'book of the law' found in the temple under Josiah in 622 BC (2 Kings 22), and dated its "
               "composition to that period or somewhat earlier. See 'Where the debates are.'",
        date="On the traditional view, c. 1406 BC — the eleventh month of the fortieth year after the exodus "
             "(1:3), in the last weeks of Moses' life, immediately before the crossing. On the Josianic view, "
             "seventh century BC, with older material behind it.",
        place="The plains of MOAB, east of the Jordan, opposite Jericho — the staging ground for the crossing. "
              "Israel never moves in this book. The whole of Deuteronomy takes place standing still, at a "
              "border.",
        audience="The SECOND generation — the children of those who came out of Egypt. Moses says so bluntly: "
                 "'not with our fathers did Jehovah make this covenant, but with us, we, these here today, all "
                 "of us alive' (5:3). It is a book about how to hand faith to people who were not there.",
        structure=[
            ("1–4", "First address: what happened, and what to make of it — the wilderness retold to a "
                    "generation that did not live it, ending in a plea to remember Horeb."),
            ("5–11", "Second address, part one: the Ten Words repeated, the SHEMA ('Hear, O Israel'), and the "
                     "great command to love God with all the heart, soul and strength — with the warning that "
                     "prosperity, not hardship, is the likelier danger."),
            ("12–26", "Second address, part two: the statutes — worship at one place, kings, prophets, courts, "
                      "war, land, debt, gleaning, wages, weights. The law given a human face."),
            ("27–28", "Blessings and curses on Ebal and Gerizim — the covenant sanctions, with the curses at "
                      "four times the length of the blessings."),
            ("29–30", "Third address: covenant renewal, and the offer of 'life and good, death and evil' — "
                      "'therefore choose life.'"),
            ("31–34", "The handover: Joshua commissioned, the Song of Moses, the blessing of the tribes, and "
                      "the death of Moses on Nebo, buried by God in a grave no one knows."),
        ],
        themes=[
            "REMEMBER — the book's central verb. A generation that did not see the exodus is told to hold it "
            "as its own story; 'remember' and 'do not forget' run through it like a drumbeat.",
            "LOVE as a command and a motive. Deuteronomy is where Israel is told to love God with everything "
            "(6:5) — and, remarkably, where God's own choice of Israel is explained by nothing but love "
            "(7:7-8): not their size, not their merit.",
            "The danger of SUCCESS. The warnings are not mainly about suffering but about comfort: when you "
            "have eaten and are full, and built good houses, 'beware lest you forget' (8:11-14).",
            "The STRANGER, the orphan and the widow — protected again and again, with the same reason each "
            "time: you were slaves in Egypt. Ethics grounded in memory rather than in principle.",
            "ONE place, one God — the centralisation of worship, and the SHEMA's insistence that Jehovah is "
            "one.",
            "CHOICE. The book ends by setting life and death in front of the people and telling them to "
            "choose. It assumes they can.",
        ],
        key_words=["devarim", "torah", "chesed", "ahav", "zakhar", "ger", "mishpat"],
        key_people=["moses", "horeb", "mount-sinai", "egypt", "edom"],
        source_text="Translated from the Hebrew MASORETIC TEXT — the digital Hebrew of Mechon-Mamre (the "
                    "Leningrad/Aleppo tradition), consonants with the Masoretes' vowel-points and cantillation, "
                    "and its scribal peculiarities kept. The scroll's own paragraph breaks are shown as it "
                    "marks them: petuchah {פ} (open) and setumah {ס} (closed). Deuteronomy is also one of the "
                    "best-attested books at Qumran — a large number of copies were found in the Dead Sea "
                    "Scrolls, along with the oldest known texts of the Shema in the tefillin and mezuzah "
                    "fragments. The seven-version shelf under every chapter compares the NIV, KJV, "
                    "Douay-Rheims, The Living Bible, the 1599 Geneva, ASV, and NWT.",
        christ="Deuteronomy is the book Jesus quotes most in the crisis moments. All three answers in the "
               "wilderness temptation come from it — 'man does not live by bread alone' (8:3), 'you shall not "
               "put Jehovah your God to the test' (6:16), 'him only shall you serve' (6:13). Asked for the "
               "greatest commandment, he answers with the SHEMA and its love-command (6:4-5). And Moses' "
               "promise of 'a prophet like me from among your brothers, him you shall hear' (18:15) is applied "
               "to Jesus in Acts 3:22 and 7:37. This translation marks those echoes as they come; it does not "
               "force them.",
        debates="The central question is DATE, and it is sharper here than for any other book of the Torah. "
                "The book presents itself as the addresses of Moses in the fortieth year, and traditional "
                "Jewish and Christian reading takes it that way. Since W. M. L. de Wette in 1805, however, a "
                "large body of scholarship has linked Deuteronomy to the scroll discovered in the temple in "
                "622 BC (2 Kings 22-23), whose reading triggered Josiah's reform — a reform that looks "
                "strikingly like this book's programme, above all the abolition of local shrines in favour of "
                "one sanctuary. On that view Deuteronomy is a seventh-century composition (or an older core "
                "given seventh-century form), presented in Moses' voice. Arguments run both ways and deserve "
                "to be heard as arguments: the book's treaty FORM closely matches SECOND-MILLENNIUM Hittite "
                "vassal treaties rather than the first-millennium Assyrian ones, which cuts toward an early "
                "date; its language and concerns match late-monarchic Judah, which cuts toward a late one. "
                "Smaller questions attach to the account of Moses' own death (34), to the phrase 'across the "
                "Jordan' spoken as if from the west, and to notes like 'to this day.' This library lays the "
                "readings out with their pedigrees and does not cast a vote — the same posture it takes on "
                "Genesis's composition and the date of Daniel.",
    ),
    "2 John": dict(
        greek_name="Ἰωάννου Βʹ (Iōannou B)",
        greek_meaning="'Of John, 2' — the traditional Greek title. The letter itself carries no author's name at "
                      "all: it opens simply HO PRESBYTEROS, 'the elder.'",
        tagline="One sheet of papyrus, thirteen verses, from a man who signs himself only 'the elder' to a "
                "woman nobody has ever conclusively identified — on truth, love, and who may be let in the "
                "door.",
        genre="A letter, and formally a very ordinary one: sender, recipient, greeting, body, travel plans, "
              "closing greetings. It follows the standard Greco-Roman letter shape almost exactly, which is "
              "part of why its length is what it is — this is about as much as fits on a single sheet.",
        canon="One of the CATHOLIC or 'general' epistles, and one of the four short letters (2 Peter, 2 John, "
              "3 John, Jude) that the early church was slowest to settle. Eusebius in the fourth century still "
              "lists 2 and 3 John among the ANTILEGOMENA — the 'spoken-against' books, widely used but "
              "disputed — while placing 1 John among the undisputed. They were received into the canon "
              "nonetheless, and their brevity and lack of doctrinal novelty are probably why the argument was "
              "quiet.",
        author="The letter says only 'the elder' (HO PRESBYTEROS). The style, vocabulary and thought-world are "
               "so close to 1 John and the Gospel of John — truth, love, remaining, light, the commandment "
               "'from the beginning' — that common authorship with those is granted by nearly everyone. WHO "
               "that is, is the open question: John the apostle, son of Zebedee; or a distinct figure "
               "traditionally called 'JOHN THE ELDER,' whom Papias (c. AD 130) appears to distinguish from the "
               "apostle in a much-argued sentence preserved by Eusebius. See 'Where the debates are.'",
        date="Traditionally late in the first century, c. AD 85–95, from the same period and setting as 1 John. "
             "There is nothing datable inside the letter itself; the date is inferred from its relationship to "
             "1 John and from the situation it describes.",
        place="By strong early tradition, EPHESUS in Asia Minor, where John is said to have spent his last "
              "years — writing to a household or congregation somewhere in the same region, close enough to "
              "visit (v. 12).",
        audience="'A chosen lady and her children.' ⚠️ Whether that means an individual woman with a family, a "
                 "CONGREGATION addressed as a woman (with 'her children' as its members and 'your chosen "
                 "sister' in v. 13 as a sister church), or a woman actually named Kyria or Eklektē, has been "
                 "argued since the earliest commentators and is not settled. The pronouns shift between "
                 "singular and plural through the letter, which fits either reading.",
        structure=[
            ("1–3", "Greeting — the elder to the chosen lady, with truth used five times before the letter "
                    "properly begins, and a greeting that is a statement rather than a wish."),
            ("4–6", "Joy and the old commandment — some of her children are walking in truth; love and the "
                    "commandments defined in terms of each other."),
            ("7–9", "The warning — many deceivers, the confession of 'Jesus Christ coming in flesh,' the "
                    "antichrist, and the contrast between running ahead and remaining."),
            ("10–11", "The instruction — a teacher who does not bring this teaching gets no house and no "
                      "welcome, because to greet him is to share in his work."),
            ("12–13", "Closing — paper and ink are not enough; he hopes to come and speak mouth to mouth."),
        ],
        themes=[
            "TRUTH and LOVE as one thing. The letter refuses to let them separate: love is defined as walking "
            "in the commandments, and the refusal of hospitality in vv. 10-11 is an application of love, not "
            "an exception to it.",
            "REMAINING (menō) against running ahead. The opponents evidently presented themselves as advanced; "
            "the letter takes the word and turns it — to go out in front of the teaching is not progress but "
            "departure.",
            "The confession of Jesus Christ IN FLESH — the same test as 1 John 4:2, and the dividing line the "
            "letter draws.",
            "HOSPITALITY as endorsement. In a world where a congregation met in a house and a travelling "
            "teacher lived on what he was given, receiving someone was funding him. The letter is about a "
            "door and a purse, not about ordinary courtesy.",
            "The insufficiency of writing. It ends by saying so out loud: paper and ink will not do, and the "
            "writer wants to be in the room.",
        ],
        key_words=["agape", "aletheia", "meno", "entole"],
        key_people=["jesus"],
        source_text="Translated from the Greek of the SBL GREEK NEW TESTAMENT (SBLGNT), the critical text "
                    "edited by Michael W. Holmes — a modern eclectic text weighing the earliest manuscripts. "
                    "⚠️ 2 John is short enough that its textual questions are individually visible: verse 8 "
                    "divides over whether it is what WE worked for or what YOU worked for (and who does the "
                    "losing), and verse 12 over whether the joy made full is OURS or YOURS — a one-letter "
                    "difference (hēmōn / humōn) that sounded nearly identical in later Greek and is confused "
                    "throughout the New Testament. This translation prints the SBL reading and flags the "
                    "alternative in the note rather than quietly choosing the warmer one. The seven-version "
                    "shelf under the chapter compares the NIV, KJV, Douay-Rheims, The Living Bible, the 1599 "
                    "Geneva, ASV, and NWT.",
        christ="The letter's test is Christological and blunt: 'Jesus Christ coming in flesh.' ⚠️ It is aimed "
               "at teaching that denied a real incarnation — the tendency later called docetic, that the Son "
               "only appeared to be human — and the answer is not an argument but a confession. Verse 9 is "
               "the positive form: to remain in the teaching of the Christ is to have both the Father and the "
               "Son, and to leave it is to have neither. The letter assumes the Father and Son are held or "
               "lost together.",
        debates="Three, and none is settled. WHO WROTE IT: 'the elder' is either John the apostle writing "
                "modestly of himself, or a separate 'John the elder' known in Asia Minor — the question turns "
                "largely on one ambiguous sentence of Papias preserved by Eusebius, and honest readers have "
                "divided over it since the third century. WHO SHE IS: an individual woman, a personified "
                "congregation, or a woman named Kyria/Eklektē. And WHAT VV. 10-11 REQUIRE: the setting is "
                "clearly travelling teachers and the hospitality that sponsored them, but the letter has "
                "repeatedly been used to justify shunning family and refusing ordinary courtesy — uses its "
                "own context does not support. This library lays the readings out with their pedigrees and "
                "does not cast a vote.",
    ),
    "3 John": dict(
        greek_name="Ἰωάννου Γʹ (Iōannou G)",
        greek_meaning="'Of John, 3' — the traditional Greek title. Like its companion, the letter names no "
                      "author: it opens HO PRESBYTEROS, 'the elder.'",
        tagline="A private note from 'the elder' to one man named Gaius — praising a host, warning against a "
                "churchman who loves to be first, and vouching for a traveller — in the fewest Greek words of "
                "any book in the Bible.",
        genre="A personal letter, and the most private document in scripture: not addressed to a congregation "
              "at all but to a single named individual about a specific local situation. It follows the "
              "ordinary Greco-Roman letter form — sender, recipient, health-wish, body, closing — almost to "
              "the letter.",
        canon="One of the CATHOLIC or 'general' epistles, and — with 2 John — among the books the early church "
              "was slowest to settle. Eusebius lists both 2 and 3 John among the ANTILEGOMENA, the "
              "'spoken-against' writings: used but disputed, largely because they are short, personal, and "
              "quote little that could be checked. They were received nonetheless.",
        author="'The elder,' as in 2 John, and with the same unresolved question: John the apostle, or the "
               "distinct 'John the elder' of Papias. The two letters are so alike in length, form, vocabulary "
               "and situation that they are almost universally taken as a matched pair by one hand; whoever "
               "wrote one wrote the other.",
        date="Traditionally late first century, c. AD 85–95, from the same hand and moment as 2 John and near "
             "1 John. Nothing inside the letter dates it; the date is inferred from the pair.",
        place="By early tradition EPHESUS, writing to Gaius somewhere in the same region of Asia Minor — close "
              "enough that the elder expects to visit soon (v. 14) and deal with Diotrephes in person.",
        audience="GAIUS — 'the beloved,' a private Christian and evidently a householder who hosts and "
                 "provisions travelling missionaries. One of the commonest names in the Roman world; he cannot "
                 "be securely identified with any other Gaius in the New Testament. The letter is written to "
                 "him alone.",
        structure=[
            ("1–4", "Greeting and joy — the elder to Gaius, an ancient health-wish, and gladness that Gaius "
                    "'walks in truth.'"),
            ("5–8", "Praise for hospitality — Gaius has received travelling brothers, even strangers; to send "
                    "them on their way is to become a fellow worker with the truth."),
            ("9–10", "Diotrephes — 'who loves to be first,' who rejects the elder's authority, refuses the "
                     "brothers, and expels those who receive them."),
            ("11–12", "The lesson and a recommendation — 'imitate the good, not the bad,' and Demetrius, "
                      "vouched for by all and by the truth itself."),
            ("13–15", "Closing — ink and reed are not enough; peace, the friends, and 'greet the friends by "
                      "name.'"),
        ],
        themes=[
            "HOSPITALITY as partnership in the mission — the exact positive of 2 John's warning. Receiving and "
            "provisioning true travelling teachers makes the host a 'fellow worker with the truth.'",
            "TRUTH walked, not merely held — the same test as 2 John and 1 John: Gaius is praised because he "
            "'walks in truth,' Demetrius because the truth itself testifies to his life.",
            "The danger of AMBITION inside the church. Where 2 John fears false teaching from outside, 3 John "
            "fears a man who 'loves to be first' inside — arguably the harder danger, because it wears the "
            "right clothes and cites no heresy.",
            "AUTHORITY exercised with restraint. The elder, defied, does not curse, depose, or even write the "
            "church again — he intends to come and speak face to face.",
            "The church funding its OWN mission — the travellers 'took nothing from the outsiders,' so the "
            "message could never be mistaken for a paid enterprise.",
        ],
        key_words=["propempo", "xenos", "aletheia", "ekklesia"],
        key_people=["jesus"],
        source_text="Translated from the Greek of the SBL GREEK NEW TESTAMENT (SBLGNT), the critical text "
                    "edited by Michael W. Holmes. 3 John is textually calm compared with its neighbour — it "
                    "has few significant variants and no doctrine-bearing ones; its interest is that it is, in "
                    "actual Greek words, very nearly the shortest book in the Bible (2 John has fewer verses, "
                    "3 John slightly fewer words). Both are about the size of a single papyrus sheet, which is "
                    "very likely why each ends by saying the writer would rather come in person than keep "
                    "writing. The seven-version shelf under the chapter compares the NIV, KJV, Douay-Rheims, "
                    "The Living Bible, the 1599 Geneva, ASV, and NWT.",
        christ="3 John says almost nothing directly about Christ — no confession, no title, no argument. What "
               "it shows instead is Christ's ethic in miniature: the travellers go out 'for the sake of THE "
               "NAME' (v. 7), which stands alone, unelaborated, the way a household says 'the' name; and the "
               "circle calls itself simply 'THE FRIENDS' (v. 15), the word Jesus used of his disciples — 'I "
               "have called you friends' (John 15:15). The letter is what the gospel looks like as ordinary "
               "conduct: a door held open, a traveller vouched for, and a whole congregation greeted one name "
               "at a time.",
        debates="The same author question as 2 John — apostle or elder — and it is one question for both "
                "letters, since they are a pair. Two smaller ones are peculiar to 3 John: WHO GAIUS IS (the "
                "name is too common to place, and attempts to identify him with Paul's companions are "
                "guesses), and WHAT DIOTREPHES' offence actually was — a doctrinal split dressed as a "
                "personality clash, an early tension between travelling and settled authority, or simply the "
                "ordinary sin of a man who wanted the head of the table. The letter blames only the ambition. "
                "This library lays the readings out with their pedigrees and does not cast a vote.",
    ),
    "Judges": dict(
        hebrew_name="שׁוֹפְטִים",
        hebrew_translit="Shofetim",
        hebrew_meaning="'Judges' — but the Hebrew SHOFET is wider than a courtroom judge. A shofet DELIVERS as "
                       "much as he decides: the 'judges' of this book are chiefly military rescuers raised up "
                       "to save Israel from oppressors, and only secondarily settlers of disputes. 'Chieftain' "
                       "or 'deliverer' catches the sense as well as 'judge.'",
        greek_name="Κριταί (Kritai)",
        greek_meaning="'Judges' — the Greek and Latin (Iudices) title, a direct translation of the Hebrew, "
                      "carrying the same courtroom narrowing that the Hebrew word itself does not intend.",
        tagline="What happened after the conquest: a downward spiral of a people who forgot, a God who kept "
                "rescuing them anyway, and a refrain that ends the book — 'in those days there was no king in "
                "Israel; everyone did what was right in his own eyes.'",
        genre="Narrative history, but shaped as a THEOLOGY OF THE CYCLE: a repeating pattern (Israel does "
              "evil → is oppressed → cries out → God raises a deliverer → the land has rest → the deliverer "
              "dies → Israel does evil again) that spirals downward rather than round, so each turn is worse "
              "than the last. It contains some of the Bible's most vivid — and most disturbing — storytelling.",
        canon="The second book of the FORMER PROPHETS in the Hebrew Bible (Joshua, Judges, Samuel, Kings), "
              "the great history that runs from entering the land to losing it. In the Christian Old Testament "
              "it is the seventh book, grouped with the 'historical books.' It bridges Joshua's conquest and "
              "the rise of the monarchy under Samuel.",
        author="Anonymous. Ancient Jewish tradition (the Talmud) credits SAMUEL, and the book's repeated "
               "refrain, 'in those days there was no king in Israel,' is written from a standpoint that "
               "already has one — so a monarchy-era hand, plausibly early, is the traditional and natural "
               "reading. Critical scholarship sees it as part of a larger 'Deuteronomistic History' (Joshua "
               "through Kings) shaped in the seventh-sixth centuries BC around older hero-stories. See 'Where "
               "the debates are.'",
        date="The EVENTS fall in the roughly two centuries between the conquest and the monarchy — on the "
             "traditional chronology c. 1380–1050 BC, a period of tribal, decentralised Israel with no "
             "central government. The COMPOSITION is later: monarchy-era on any view, whether early (near "
             "Samuel) or, on the Deuteronomistic view, considerably later.",
        place="The land of Canaan itself, tribe by tribe — the hill country, the valleys, the coastal plain "
              "held by the Philistines, and the Transjordan. The book is intensely geographical: its "
              "disasters and rescues are local, tied to particular tribes and particular towns.",
        audience="Later Israel — a people who DID have a king, reading the story of what life was like when "
                 "there was none. The book is, among other things, an argument about leadership: what happens "
                 "to a covenant people with no centre to hold them.",
        structure=[
            ("1:1–3:6", "The double introduction — the incomplete conquest (ch. 1) and its theological "
                        "diagnosis (ch. 2): a generation arose 'who did not know Jehovah,' and the cycle "
                        "begins."),
            ("3:7–16:31", "The judges themselves — Othniel, Ehud and the fat king, Deborah and Barak and Jael "
                          "with her tent-peg, Gideon and his fleece, the tragedy of Jephthah's vow, and the "
                          "long ruin of Samson. Each cycle darker than the last."),
            ("17–21", "The double epilogue — Micah's idol and the migration of Dan, and the horror at Gibeah "
                      "and the near-destruction of Benjamin: two stories with no judge at all, showing how far "
                      "the rot has gone. The refrain closes it: 'everyone did what was right in his own eyes.'"),
        ],
        themes=[
            "The CYCLE — sin, servitude, supplication, salvation, and back to sin — spiralling DOWN. The land "
            "gets less rest and the deliverers get more flawed as the book goes on.",
            "God's exhausting FAITHFULNESS. He keeps rescuing a people who keep forgetting him, raising "
            "deliverer after deliverer for a nation that does not deserve one — grace stretched to the point "
            "of grief.",
            "The FLAWED deliverer. These are not saints: a left-handed assassin, a reluctant thresher, a man "
            "who sacrifices his own daughter to a rash vow, a womanising strongman undone by his own "
            "appetites. God works through deeply compromised people, and the book never pretends otherwise.",
            "The danger of the UNFINISHED task — Judges 1's 'did not drive out' becomes the root of everything "
            "that follows: the peoples left in the land become the snare that pulls Israel into their gods.",
            "The question of a KING. The refrain 'no king in Israel; everyone did what was right in his own "
            "eyes' frames the anarchy as a leadership vacuum — setting up the books of Samuel and the demand "
            "for a monarchy.",
            "Some of the Bible's most prominent WOMEN — Deborah the prophet-judge, Jael the killer of Sisera, "
            "Achsah who negotiates for water, Jephthah's unnamed daughter, Samson's Delilah, and the horrific "
            "fate of the Levite's concubine — for good and for terrible ill.",
        ],
        key_words=["cherem", "mas", "chesed", "goral"],
        key_people=["judah", "moses", "jerusalem"],
        source_text="Translated from the Hebrew MASORETIC TEXT — the digital Hebrew of Mechon-Mamre (the "
                    "Leningrad/Aleppo tradition), consonants with the Masoretes' vowel-points and cantillation, "
                    "and its scribal peculiarities kept. The scroll's own paragraph breaks are shown as it "
                    "marks them: petuchah {פ} (open) and setumah {ס} (closed). Judges also contains one of the "
                    "oldest passages in the Hebrew Bible — the SONG OF DEBORAH (ch. 5), archaic poetry many "
                    "scholars date close to the events it celebrates, and a place where the Masoretic text is "
                    "famously difficult. The seven-version shelf under every chapter compares the NIV, KJV, "
                    "Douay-Rheims, The Living Bible, the 1599 Geneva, ASV, and NWT.",
        christ="Judges is the Bible's long argument that flawed human deliverers are not enough. Every judge "
               "rescues, and every rescue fails to last, because the deliverer dies and the people relapse — "
               "and the book ends crying out, in effect, for a king who will not. The New Testament reads the "
               "whole pattern as pointing past itself: Hebrews 11 lists Gideon, Barak, Samson and Jephthah "
               "among the heroes of faith, flaws and all, 'of whom the world was not worthy' — people who "
               "'were commended through their faith, yet did not receive what was promised,' because the "
               "something better was still ahead.",
        debates="AUTHORSHIP AND DATE, as with the other Former Prophets: the traditional ascription to Samuel "
                "(monarchy-era, early) versus the critical view of a Deuteronomistic History edited in the "
                "seventh-sixth centuries around older sources — the recurring refrain about 'no king' clearly "
                "post-dates the events either way. CHRONOLOGY: the judgeships and their round numbers (many "
                "periods of 40 or 80 years) add up to more time than the span between conquest and monarchy "
                "allows, so most read the judges as partly OVERLAPPING regional figures rather than a single "
                "national succession. And the HARD ETHICS — the ban, Jephthah's vow, the atrocity at Gibeah — "
                "which the book reports with striking refusal to tidy up; it shows the horror without "
                "endorsing it, and readers have always argued over how much is description and how much is "
                "verdict. This library lays the readings out with their pedigrees and does not cast a vote.",
    ),
    "Mark": dict(
        greek_name="Κατὰ Μᾶρκον (Kata Markon)",
        greek_meaning="'According to Mark' — the traditional title. The book itself names no author; the "
                      "ascription to Mark is early and external. Its own opening word, EUANGELION ('good "
                      "news'), is very likely where the whole genre got the name 'Gospel.'",
        tagline="The shortest, fastest, and probably earliest of the four Gospels — a breathless, urgent "
                "account of Jesus in action, with almost no teaching and one relentless adverb: "
                "'immediately.'",
        genre="A GOSPEL — a new literary form Mark may effectively have invented: not a biography in the "
              "ancient sense, not a chronicle, but a theological narrative of the life, death and "
              "resurrection of Jesus, written to proclaim rather than merely to record. Mark's is the most "
              "action-driven of the four: heavy on miracle and movement, light on discourse.",
        canon="The second Gospel in the traditional order (after Matthew), but on the majority scholarly view "
              "the FIRST to be written — the earliest of the four, and a principal source drawn on by both "
              "Matthew and Luke. One of the four canonical Gospels that open the New Testament.",
        author="By strong and early tradition, JOHN MARK — the companion of Peter and, earlier, of Paul and "
               "Barnabas (Acts 12:12, 25; 13:13; 1 Peter 5:13). Papias, writing around AD 130 and quoting an "
               "even older source ('the Elder'), says Mark was Peter's INTERPRETER and 'wrote down accurately "
               "all that he remembered' of Peter's preaching, 'though not in order.' This makes the Gospel, "
               "on the traditional view, essentially the memoirs of PETER as set down by his assistant — "
               "which fits its vivid, eyewitness-flavoured detail and its unflattering portrait of Peter "
               "himself.",
        date="Most place it around AD 65–70 — near or just after the deaths of Peter and Paul in Rome and "
             "around the Jewish war that ended in the destruction of the Temple in AD 70. A few argue for a "
             "date in the 50s. Either way it is early: within a generation of the events, and the earliest "
             "written Gospel.",
        place="By tradition ROME, written for a Gentile, largely Roman audience. The internal signs fit: Mark "
              "explains Jewish customs his readers would not know (7:3-4), translates Aramaic phrases into "
              "Greek, and uses a striking number of Latin loanwords (legion, denarius, centurion). It reads "
              "like a Gospel made for people far from Galilee.",
        audience="GENTILE believers, probably under pressure — a church that needed the story of a Messiah who "
                 "suffered, told to people who might soon suffer themselves. Mark's Jesus is constantly "
                 "misunderstood, and the disciples constantly fail, which speaks to a community learning that "
                 "following the crucified one is hard.",
        structure=[
            ("1:1–13", "The beginning — no birth, straight to John the baptiser, the baptism, and the "
                       "temptation, all in thirteen verses."),
            ("1:14–8:26", "The ministry in Galilee — a whirlwind of healings, exorcisms, parables and growing "
                          "crowds, and a mounting question: who is this? (with the disciples steadily failing "
                          "to answer it)."),
            ("8:27–10:52", "The turn — Peter confesses 'you are the Christ,' and from that moment Jesus sets "
                           "his face toward Jerusalem, predicting his death three times and redefining "
                           "greatness as service. The hinge of the book."),
            ("11:1–16:8", "Jerusalem — the entry, the temple, the last supper, Gethsemane, the trial, the "
                          "cross, and the empty tomb. The Gospel that has run at a sprint slows to tell the "
                          "passion in detail."),
        ],
        themes=[
            "URGENCY — the relentless 'immediately' (euthys), a kingdom breaking in with no pause, a Jesus "
            "always on the move. The pace is itself a message.",
            "The SUFFERING Messiah — Mark refuses a triumphant Christ. Nearly half the book is the road to the "
            "cross, and its climax is not a resurrection appearance but a centurion at a corpse saying 'truly "
            "this was the Son of God.'",
            "The MESSIANIC SECRET — Jesus repeatedly silences those who would announce him (demons, the "
            "healed, even the disciples). His identity is real but hidden, and only fully sayable at the "
            "cross.",
            "The FAILING disciples — nowhere are the twelve less flattering. They misunderstand, they sleep, "
            "they flee, Peter denies him — a hard mirror for a struggling church, and a strange choice for a "
            "book supposedly based on Peter's own preaching.",
            "AUTHORITY (exousia) — over disease, demons, the Sabbath, sin, the sea. Mark shows rather than "
            "argues: what Jesus DOES makes the claim his words leave unspoken.",
            "SERVICE (diakoneō) — from the angels in the wilderness and Simon's mother-in-law to the book's "
            "great definition, 'the Son of Man came not to be served but to serve, and to give his life as a "
            "ransom for many' (10:45).",
        ],
        key_words=["euangelion", "euthys", "basileia", "exousia"],
        key_people=["jesus", "john-the-baptist", "simon-peter", "capernaum"],
        source_text="Translated from the Greek of the SBL GREEK NEW TESTAMENT (SBLGNT), the critical text "
                    "edited by Michael W. Holmes — a modern eclectic text weighing the earliest manuscripts. "
                    "\u26a0\ufe0f Mark carries two of the most consequential textual questions in the New "
                    "Testament. Its OPENING (1:1) divides over whether 'Son of God' stood in the first "
                    "sentence, and 1:41 over whether Jesus was 'moved with COMPASSION' or 'moved with ANGER' "
                    "at the leper — a one-word difference this translation resolves toward the harder reading, "
                    "explained in the note. And its ENDING is the single largest textual problem in the "
                    "Gospels: the oldest manuscripts stop abruptly at 16:8, with the women fleeing the empty "
                    "tomb 'for they were afraid,' and the familiar 'longer ending' (16:9-20) is a later "
                    "addition — flagged there when the translation reaches it. This library prints the "
                    "critical text and lays the variants out with their pedigrees. The seven-version shelf "
                    "under every chapter compares the NIV, KJV, Douay-Rheims, The Living Bible, the 1599 "
                    "Geneva, ASV, and NWT.",
        christ="Mark IS a book about who Jesus is, and it withholds the answer on purpose. The demons know it "
               "from the first page; the reader is told it in verse 1; but the human characters cannot see it "
               "until the end — and the confession the whole Gospel drives toward comes not from a disciple "
               "but from a Roman executioner looking at a dead man: 'truly this man was the Son of God' "
               "(15:39). Mark's Christ is the crucified one, and his central claim is that you do not "
               "understand the glory until you have seen the cross.",
        debates="AUTHORSHIP is relatively secure by ancient standards — the Papias tradition linking Mark to "
                "Peter is early and specific — though critical scholars treat 'Mark' as shorthand for the "
                "community that produced it. The live questions are the ENDING (almost universally, 16:9-20 is "
                "judged a later addition, since the earliest and best manuscripts end at 16:8; whether Mark "
                "MEANT to end so abruptly, or whether the original ending was lost, is genuinely debated), "
                "the two great VARIANTS at 1:1 and 1:41, and MARKAN PRIORITY — the majority view that Mark was "
                "written first and used by Matthew and Luke, against the older tradition that Matthew came "
                "first. This library prints the critical text and lays the readings out with their pedigrees "
                "without casting a vote.",
    ),
    "Luke": dict(
        greek_name="Κατὰ Λουκᾶν (Kata Loukan)",
        greek_meaning="'According to Luke.' The book names no author; the ascription to LUKE — a physician and companion of Paul — is early and undisputed. It is the first of two volumes: the Gospel and the Acts of the Apostles, both addressed to the same Theophilus, together the longest single contribution to the New Testament by any one hand.",
        tagline="The longest and most literary of the Gospels — a physician's orderly account, and the Gospel of the outsider: women, the poor, the Samaritan, the tax-collector; a Saviour whose coming is sung by a teenage girl and announced first to shepherds.",
        genre="A GOSPEL, and volume one of a two-part history (Luke–Acts) — the most consciously literary of the four. It opens with a classical Greek preface, dates events by emperors and governors, carries the largest vocabulary in the New Testament, and preserves a wealth of material found in no other Gospel (the Good Samaritan, the Prodigal Son, the Rich Man and Lazarus, the road to Emmaus).",
        canon="The THIRD Gospel and the LONGEST book in the New Testament; paired with Acts as a single two-volume work that together makes up about a quarter of the NT — more text than Paul. One of the three Synoptics.",
        author="By early and near-unanimous tradition, LUKE, 'the beloved physician' (Colossians 4:14) — a Gentile companion of Paul, present in the first-person 'we' sections of Acts (16, 20, 27–28) and named in Philemon 24 and 2 Timothy 4:11. On the majority view the only GENTILE author in the Bible; the medical vocabulary and the close interest in Paul's journeys fit the tradition.",
        date="Commonly placed around AD 80–85, though some argue the 60s–70s. It turns partly on Luke's use of Mark (which he clearly draws on) and on where Acts breaks off — with Paul still alive under house arrest in Rome (c. AD 62), which some read as an early terminus for the whole two-volume work.",
        place="Uncertain — proposals include Rome, Achaia, and Antioch. Written for a Greco-Roman readership: Luke smooths Semitic detail, explains Palestine to outsiders, and frames the story inside the wider empire.",
        audience="GENTILE Christians and inquirers — 'most excellent Theophilus' and everyone like him. Luke universalises the good news: he traces Jesus' genealogy back not merely to Abraham but to ADAM, 'son of God' (3:38), and ends Acts with the gospel reaching Rome, the heart of the world.",
        structure=[
            ["1:1–4", "The preface — a formal dedication to Theophilus; the one place a Gospel opens like a Greek history."],
            ["1:5–2:52", "The infancy narrative — two annunciations, the Visitation, the births of John and Jesus, the shepherds, Simeon and Anna, the boy in the temple. Luke's alone, and full of songs."],
            ["3:1–4:13", "John the baptiser, the baptism, the genealogy back to Adam, the temptation."],
            ["4:14–9:50", "The Galilean ministry — healings, parables, the calling and sending of the twelve."],
            ["9:51–19:27", "The long journey to Jerusalem — the heart of Luke, holding most of his unique parables (the Good Samaritan, the Prodigal Son, the Rich Man and Lazarus)."],
            ["19:28–24:53", "Jerusalem — the entry, the temple, the Last Supper, the cross, the empty tomb, and the road to Emmaus."],
        ],
        themes=[
            "The OUTSIDER welcomed — women, the poor, tax-collectors, Samaritans, sinners. Luke's Jesus eats with the wrong people and tells stories in which they are the heroes.",
            "The GREAT REVERSAL — sounded first in Mary's song (the lowly lifted, the rich sent empty away) and paid out in the Beatitudes-and-woes, in Lazarus at the gate, in the last made first.",
            "The HOLY SPIRIT and PRAYER — the Spirit fills Elizabeth, Mary, Zechariah, and Simeon before a single miracle is done; Jesus prays at every hinge and teaches his followers to.",
            "JOY and SONG — Luke 1–2 is the songbook of the church (Magnificat, Benedictus, Gloria, Nunc Dimittis); the Gospel begins and ends with people praising God 'with great joy.'",
            "SALVATION for ALL — the genealogy to Adam, the Samaritan neighbour, the promise that 'all flesh will see the salvation of God' (3:6).",
        ],
        key_words=["charis", "parthenos", "makarios", "euangelion"],
        key_people=["jesus", "john-the-baptist", "nazareth"],
        source_text="Translated from the Greek of the SBL GREEK NEW TESTAMENT (SBLGNT), edited by Michael W. Holmes. Luke's Greek is the most refined in the Gospels — a classical, balanced periodic preface (1:1–4), then a deliberate shift into Septuagint-flavoured Greek for the infancy story, so the reader hears the Old Testament resume. Its sharpest textual questions cluster later (the sweat 'like blood' in Gethsemane, 22:43–44; some words from the cross), noted where they fall; chapter 1 is textually calm.",
        christ="Luke's Jesus is the Saviour of the whole world, and above all of those the world discards. He is announced not to kings but to shepherds; his mother is a nobody from Nazareth who sings a revolution; his genealogy runs past Abraham all the way to Adam, making him the second head of the entire human race, not one nation's Messiah only. He is 'Son of the Most High' and 'a Saviour, who is Christ the Lord' — and the one who says his whole mission is 'to seek and to save the lost' (19:10).",
        debates="AUTHORSHIP by Luke the physician is early and rarely contested even critically, helped by the first-person 'we' passages of Acts. The live questions are DATE (the 80s versus a pre-63 date tied to the abrupt ending of Acts), SOURCES (Luke names 'many' predecessors in 1:1; the majority view has him using Mark and a sayings source alongside material unique to him), and a handful of famous later VARIANTS. The two-volume unity of Luke–Acts, addressed to the same Theophilus, is broadly agreed.",
    ),
    "Ruth": dict(
        hebrew_name="רוּת",
        hebrew_translit="Rut",
        hebrew_meaning="'Ruth' — the book's Moabite heroine gives it her name, its meaning uncertain (often linked to re'ut, 'friendship, companionship'). One of the Five Megillot (Festival Scrolls) of the Hebrew Bible, read aloud at Shavuot, the harvest feast — fitting for a story that turns on a barley field.",
        greek_name="Ῥούθ (Rhouth)",
        greek_meaning="The Septuagint moves Ruth out of the Writings and sets it right after Judges, as a historical bridge to the days of David — the placement the Christian Old Testament inherited.",
        tagline="A short, luminous story of loyal love (chesed) in the dark age of the Judges — a famine, a Moabite widow's oath, and a redemption that runs down to David.",
        genre="A HEBREW SHORT STORY / novella — a self-contained narrative of exceptional craft, built on the theme-word chesed and the machinery of gleaning-rights and levirate redemption. Set 'in the days when the judges judged,' it is the deliberate counter-story to the book of Judges: where that book is national, violent, and downward, Ruth is domestic, gentle, and redemptive.",
        canon="In the Hebrew Bible, one of the Five Megillot among the Writings (Ketuvim), read at Shavuot (the barley-and-wheat harvest festival). In the Christian Old Testament, following the Septuagint, it is placed after Judges and before 1 Samuel — the bridge from the chaos of the Judges to the rise of David.",
        author="Anonymous. Jewish tradition (Talmud, Bava Batra 14b) credits SAMUEL, but the book names no author, and its closing genealogy to David — plus its need to explain a custom that was 'formerly' done in Israel (4:7) — implies a writer looking back from David's time or later.",
        date="Debated. The Davidic genealogy sets a floor at David's reign (c. 1000 BC); the classical, un-Aramaised Hebrew and the explanation of an obsolete custom (4:7) point to a later hand looking back. Two main proposals: an early-monarchic date, or a post-exilic one (5th c. BC) — on which reading the book stands pointedly AGAINST the expulsion of foreign wives under Ezra and Nehemiah. The setting ('the days of the judges') is fixed; the composition is the open question.",
        place="The land of Judah — Bethlehem and the fields of Moab across the Dead Sea. A story of the Judahite countryside: barley fields, a threshing floor, the town gate.",
        audience="Israel — and, on the post-exilic reading, an Israel arguing with itself over who belongs. The book's answer is a Moabite woman whose chesed makes her more truly a daughter of the covenant than many born inside it.",
        structure=[
            ["1", "Emptying — famine drives Elimelech's family to Moab; the men die; Naomi returns bereft with Ruth, who binds herself to her with the great oath."],
            ["2", "Gleaning — Ruth 'happens' upon the field of Boaz, a kinsman; his kindness to a foreign widow; Naomi's first hope, 'he is one of our redeemers.'"],
            ["3", "The threshing floor — Naomi's plan; Ruth's midnight appeal to Boaz to 'spread your wing over your servant'; his pledge to redeem."],
            ["4", "Redemption — Boaz secures the right at the gate, marries Ruth, a son is born; the women bless Naomi; the genealogy runs to David."],
        ],
        themes=[
            "CHESED — loyal, covenant love, the book's spine: Ruth's to Naomi, Boaz's to Ruth, and God's beneath both. The word recurs at 1:8, 2:20, 3:10.",
            "REDEMPTION (ga'al) — the kinsman-redeemer who buys back land and raises up a dead man's name; Boaz as the go'el, the role the whole plot turns on.",
            "THE OUTSIDER BROUGHT IN — a Moabite, barred by law, made an ancestress of the king; belonging by faith and loyalty, not blood.",
            "PROVIDENCE IN THE ORDINARY — no miracles, no visions; God works through a chance-met field, a harvest, a levirate law, a gate full of witnesses. 'She happened to come to the field of Boaz' (2:3) is the book's whole theology of quiet providence.",
            "EMPTY TO FULL — Naomi's arc from 'I went out full and came home empty' (1:21) to a child laid in her lap (4:16).",
        ],
        key_words=["chesed", "goel", "menuchah", "dabaq"],
        key_people=["ruth", "naomi", "moab", "bethlehem"],
        source_text="Translated from the pointed Hebrew Masoretic Text (as printed by Mechon-Mamre). Ruth's Hebrew is classical and clean — some of the finest narrative prose in the Bible — with a scatter of archaic or dialect forms and a few ketiv/qere (written-versus-read) notes that translators weigh but that rarely change the sense. The book is textually calm; its difficulties are literary and legal — the workings of gleaning-rights and levirate redemption — handled in the notes where they fall.",
        christ="The book ends on a genealogy, and that is its Christian point: the line runs Boaz → Obed → Jesse → DAVID (4:17-22), and through David, in Matthew's opening chapter, to Jesus — where RUTH the Moabite is named among the women in his ancestry (Matthew 1:5). Boaz the kinsman-redeemer (go'el) who buys back the destitute and covers them has long been read as a figure of a greater Redeemer; and the gathering of a Gentile outsider into the covenant people foreshadows the gospel's reach beyond Israel. A harvest story that ends in a cradle — and the cradle leads to a king.",
        debates="The main questions are DATE (early-monarchic vs post-exilic — which decides whether the book is a straightforward tale or a pointed argument against the foreign-wife expulsions of Ezra-Nehemiah) and AUTHORSHIP (the Samuel tradition vs an anonymous later hand). The legal machinery is also discussed — how gleaning-rights, the go'el's duty, and levirate marriage interlock, and why the nearer redeemer of chapter 4 backs out. On the book's meaning there is little dispute: it is about chesed, and about a foreigner made kin.",
    ),
    "Jude": dict(
        greek_name="Ἰούδα (Iouda)",
        greek_meaning="'Of Jude' — Ioudas, the same name as Judah and Judas. The author names himself 'brother of James,' which marks him as a brother of Jesus who calls himself only the Lord's slave.",
        tagline="The New Testament's fiercest short letter — a one-chapter call to 'contend for the faith,' famous for quoting two books that are not in the Bible.",
        genre="A general (catholic) EPISTLE — a circular letter of warning and exhortation, not addressed to one named church. Twenty-five verses of sustained polemic against false teachers, built on a chain of Old-Testament and Jewish judgment-examples, and closed by one of Scripture's greatest doxologies.",
        canon="One of the seven 'catholic' (general) epistles near the end of the New Testament, just before Revelation. Among the shortest books in the Bible, and — with 2 and 3 John and 2 Peter — one whose place in the canon was debated in the early centuries, partly because of its use of non-canonical sources.",
        author="JUDE — Ioudas, 'a slave of Jesus Christ and brother of James' (v1). Naming James the Just (leader of the Jerusalem church and a brother of Jesus) identifies the author as another brother of the Lord (Mark 6:3), writing not by family claim but as a servant. A minority take him for a different, otherwise-unknown Jude.",
        date="Debated; commonly c. AD 65-80. The appeal to 'remember the words of the apostles' as an established past (v17) and the letter's close relationship with 2 Peter 2 suggest a date a generation into the church. Nothing in it is precisely datable.",
        place="Unknown. The thoroughly Jewish character of its examples (the Exodus, the fallen angels, Enoch, Moses, Korah) and its ease with extra-biblical Jewish tradition point to a Jewish-Christian author writing to Jewish-Christian congregations, somewhere in the eastern Mediterranean world.",
        audience="Christian congregations under threat from within — 'certain men have crept in unnoticed' (v4). Not a single church but believers generally, warned against teachers who turned grace into licence and denied the Lord who bought them.",
        structure=[
            ["1-4", "Greeting, and the occasion — a letter meant to be warm, turned urgent: 'contend for the faith once for all delivered.'"],
            ["5-16", "The indictment — a chain of judgment-examples (the wilderness generation, the fallen angels, Sodom; Cain, Balaam, Korah; Enoch's prophecy) and vivid portraits of the intruders."],
            ["17-23", "The exhortation — remember the apostles' warning; build yourselves up, pray, keep, wait; and rescue the wavering, 'snatching them out of the fire.'"],
            ["24-25", "The doxology — to the God able to keep you from stumbling and present you blameless, glory forever."],
        ],
        themes=[
            "CONTENDING FOR THE FAITH — the faith 'once for all (hapax) delivered,' complete and not to be traded; the whole letter is a call to guard it.",
            "JUDGMENT ON THE UNGODLY — a relentless chain of examples that rescue is no guarantee: a redeemed people, angels, famous men, all fell.",
            "GRACE TURNED TO LICENCE — the specific heresy: making forgiveness an excuse for the sin it forgives (aselgeia), and denying the Master (despotes) who owns them.",
            "MERCY WITHIN THE WARNING — the fierce letter's other face: 'keep yourselves in the love of God,' 'have mercy,' 'snatch them from the fire.'",
            "THE USE OF JEWISH TRADITION — Jude reaches openly for material outside the canon (the Assumption of Moses, 1 Enoch) to make his case — the clearest such case in the Bible.",
        ],
        key_words=["hapax", "despotes", "aselgeia", "agape"],
        key_people=["enoch", "michael-archangel", "balaam", "sodom"],
        source_text="Translated from the Greek of the SBL Greek New Testament (SBLGNT), edited by Michael W. Holmes. Jude's Greek is vigorous and vivid — a torrent of triads and sea-and-storm images — and carries two significant textual questions handled in the notes: the reading 'JESUS' (rather than 'the Lord') saving the people out of Egypt (v5), adopted here on the strength of the earliest witnesses; and the tangled 'have mercy… snatch from the fire… mercy with fear' of vv22-23, where the manuscripts cannot all be reconciled.",
        christ="For all its fierceness the letter is framed by Christ: its readers are 'kept for Jesus Christ' (v1) and told to 'wait for the mercy of our Lord Jesus Christ' (v21), and it ends 'to the only God our Savior, through Jesus Christ our Lord' (v25). The heresy Jude fights is precisely a denial of 'our only Master and Lord, Jesus Christ' (v4) — and if the disputed reading of v5 stands, Jude sees Christ himself as the one who led Israel out of Egypt. The Lord who saves is the Lord who judges, and the same hands that keep you from stumbling will present you blameless before his glory.",
        debates="Two clusters. First, the NON-CANONICAL SOURCES — Jude's use of the Assumption of Moses (v9) and his direct quotation of 1 Enoch as prophecy (vv14-15), which unsettled some early churches and still raises the question of what 'quoting' a book implies about its authority (the note takes no vote). Second, the RELATIONSHIP TO 2 PETER — Jude and 2 Peter 2 share so much material (the fallen angels, Sodom, Balaam, the waterless clouds) that one almost certainly drew on the other or a common source; which came first is a standing literary question. Authorship (the Lord's brother vs an unknown Jude) and date follow from these.",
    ),
    "Jeremiah": dict(
        hebrew_name="יִרְמְיָהוּ",
        hebrew_translit="Yirmeyahu",
        hebrew_meaning="'Jeremiah' — likely 'Jehovah exalts,' or 'Jehovah loosens/casts,' or 'Jehovah establishes' (the root is genuinely uncertain). The book is named for its prophet, whose forty-year ministry spanned the last kings of Judah and the destruction of Jerusalem.",
        greek_name="Ἰερεμίας (Ieremias)",
        greek_meaning="In the Septuagint, Jeremiah is significantly SHORTER (by about one-eighth) and arranges the oracles-against-the-nations in a different place — one of the most important cases in the Old Testament of two genuinely different editions of one book (a Hebrew Dead Sea Scroll fragment matches the shorter Greek order).",
        tagline="The longest book in the Bible by word count — the forty-year cry of the 'weeping prophet' who watched Judah fall, who tore down and planted, and who was given the promise of a new covenant written on the heart.",
        genre="PROPHECY — poetry and prose intertwined: oracles of judgment and hope, symbolic sign-acts, a running biography of the prophet's own sufferings (the 'confessions'), and historical narrative of Jerusalem's last days. By word count, the largest book in the Bible.",
        canon="One of the Major Prophets (with Isaiah and Ezekiel), placed after Isaiah; in the Hebrew canon, among the Latter Prophets. The book of Lamentations, traditionally ascribed to Jeremiah, follows it in the Christian order.",
        author="JEREMIAH son of Hilkiah, a priest of Anathoth, called in 627 BC (1:2). The book credits its writing to Jeremiah dictating to his scribe BARUCH son of Neriah (ch 36 — where the king burns the first scroll and it is rewritten larger). The complex final shape — poetry, prose sermons, and third-person narrative — points to Baruch and later hands gathering and arranging the material.",
        date="The ministry runs c. 627-586 BC and after (Jeremiah is carried to Egypt following the fall). The book reached its two differing editions — the shorter Greek and the longer Hebrew — over the decades that followed, likely in the exile.",
        place="Judah — Anathoth, Jerusalem, and finally Egypt, where fleeing survivors carry Jeremiah off after the assassination of Gedaliah (chs 42-44). He prophesied through the reigns of Josiah, Jehoahaz, Jehoiakim, Jehoiachin, and Zedekiah.",
        audience="Judah in its last generation — kings, priests, false prophets, and people — warned to submit to Babylon as God's instrument and to turn back, and refusing; and then the exiles, given a letter (ch 29) to settle, build, and pray for the city of their captivity, and wait out seventy years.",
        structure=[
            ["1", "The call — Jeremiah known before the womb, the almond branch and the boiling pot, the charge to uproot and to plant."],
            ["2-25", "Oracles against Judah and Jerusalem — the great indictment (the broken cisterns, the temple sermon, the potter's house, the sign-acts), interlaced with the prophet's own anguished 'confessions.'"],
            ["26-45", "Narratives of conflict and the fall — Jeremiah against the kings and false prophets; the burned scroll; the letter to the exiles; the siege, the cistern, the destruction, and the flight to Egypt."],
            ["30-33", "The Book of Consolation (set within the above) — restoration, and the NEW COVENANT written on the heart (31:31-34)."],
            ["46-51", "Oracles against the nations — Egypt, Philistia, Moab, Ammon, Edom, Damascus, Kedar, Elam, and Babylon."],
            ["52", "A historical appendix — the fall of Jerusalem retold (paralleling 2 Kings 25)."],
        ],
        themes=[
            "THE COVENANT BETRAYED — Judah has 'forsaken the fountain of living waters and hewn out broken cisterns' (2:13); idolatry is adultery, and the judgment is the marriage's grief, not God's caprice.",
            "SUBMIT TO BABYLON — Jeremiah's scandalous, treasonous-sounding message: Babylon is God's instrument, resistance is rebellion against God, and the exile must be accepted and outlasted (the seventy years).",
            "TEAR DOWN AND PLANT — the six verbs of 1:10; a ministry mostly of demolition that nonetheless ends in building, because judgment is never God's last word.",
            "THE NEW COVENANT — the book's summit (31:31-34): a covenant written not on stone but on the heart, sins remembered no more — the passage the New Testament takes as fulfilled in Christ (Hebrews 8).",
            "THE COST OF THE WORD — the 'confessions' (e.g. 20:7-18), where the prophet accuses God of deceiving him, curses the day of his birth, and yet cannot stop speaking because the word is 'a fire shut up in my bones.' No prophet's inner life is so exposed.",
        ],
        key_words=["yatsar", "navi", "qadash", "shaqed"],
        key_people=["jeremiah", "josiah", "zedekiah", "babylon"],
        source_text="Translated from the pointed Hebrew Masoretic Text (as printed by Mechon-Mamre). ⚠️ Jeremiah is the Old Testament's great case of a book that survives in TWO editions: the Hebrew (Masoretic) text is roughly one-eighth longer than the Greek Septuagint, and the two place the oracles-against-the-nations differently — and a Hebrew fragment from Qumran matches the shorter Greek. This translation follows the Masoretic Hebrew and notes the major differences where they fall. The book is otherwise rich in wordplay — the almond/watcher pun of 1:11-12 is the first of many.",
        christ="Jeremiah's summit is the NEW COVENANT (31:31-34): 'I will put my law within them, and write it on their hearts… and I will remember their sin no more.' The New Testament takes this as the covenant sealed in Christ's blood (Luke 22:20; 1 Corinthians 11:25) and quotes it in full as fulfilled (Hebrews 8:8-12; 10:16-17). The weeping prophet — rejected by his own, made to suffer for the word, promising a covenant of the heart — has long been read as a figure of the one who wept over the same city (Luke 19:41) and inaugurated the covenant Jeremiah foresaw.",
        debates="The two EDITIONS (shorter Greek vs longer Hebrew, and the differing place of the nations-oracles) — most scholars now see the Greek as translating an earlier, shorter Hebrew edition, and the Masoretic text as a later expanded one. The book's COMPOSITION — how its poetry, prose sermons, and biography (the last likely from Baruch) came together — is much studied, as is the authenticity and dating of individual oracles, especially the prose sermons whose style resembles Deuteronomy. The prophet himself, by contrast, is one of the most vividly and personally known figures in the Old Testament.",
    ),
    "Daniel": dict(
        hebrew_name="דָּנִיֵּאל",
        hebrew_translit="Daniyyel",
        hebrew_meaning="'God is my judge' (or 'God has judged'). The book is named for its hero, a young Judean exile in the Babylonian and Persian courts — and it is unique in the Old Testament for being written in TWO languages, Hebrew (1:1-2:4a; 8-12) and Aramaic (2:4b-7:28).",
        greek_name="Δανιήλ (Daniel)",
        greek_meaning="The Greek versions of Daniel carry THREE sections not in the Hebrew-Aramaic text — the Prayer of Azariah and the Song of the Three Young Men (within ch 3), Susanna, and Bel and the Dragon — which Catholic and Orthodox Bibles include and Protestants place among the Apocrypha. There were also two quite different Greek translations (the Old Greek and Theodotion), an unusual textual situation.",
        tagline="A young exile in a pagan court, and the God who 'removes kings and sets up kings' — court tales of faith under empire (chs 1-6) and visions of the world-kingdoms giving way to the kingdom of God (chs 7-12).",
        genre="Two genres in one book. Chapters 1-6 are COURT TALES — narratives of Daniel and his friends keeping faith under Babylonian and Persian kings (the dream-statue, the fiery furnace, the writing on the wall, the lions' den). Chapters 7-12 are APOCALYPTIC — symbolic visions of beasts, horns, and the end, the Old Testament's fullest example of the genre that flowers in Revelation.",
        canon="In the Christian Old Testament, grouped with the Major Prophets (after Ezekiel). In the HEBREW canon, notably, Daniel stands not among the Prophets but among the WRITINGS (Ketuvim) — a placement much discussed, often tied to the book's date and its apocalyptic rather than classically-prophetic character.",
        author="Traditionally DANIEL himself, a Judean of noble birth taken to Babylon in the first deportation (605 BC) and serving into the Persian period. The book mixes third-person narrative (chs 1-6) with first-person visions (chs 7-12, 'I, Daniel'). Critical scholarship widely holds that the book reached its final form in the 2nd century BC (see the debates).",
        date="The great crux of the book. The TRADITIONAL date is the 6th century BC (the events' own setting, 605-536 BC), making chapters 7-12 genuine long-range prophecy. The CRITICAL consensus dates the final book to c. 165 BC, during the persecution of the Jews under Antiochus IV Epiphanes — reading the 'prophecies,' especially the detailed history of chapter 11, as a review of past events down to the author's own day (a recognized ancient genre). The question turns on the precision of chapter 11, the book's Persian and Greek loanwords, its place in the Hebrew canon, and one's view of predictive prophecy. Laid out with pedigrees; no vote.",
        place="Babylon and the Persian court — the exile and its aftermath, from Nebuchadnezzar through Belshazzar to Darius the Mede and Cyrus of Persia.",
        audience="The people of God under a hostile empire — whether sixth-century exiles in Babylon or second-century Jews under Antiochus, the message is the same: the pagan powers are real and terrible, but their days are numbered, God is sovereign over every throne, and faithfulness under pressure will be vindicated.",
        structure=[
            ["1", "The court education — Daniel and his three friends refuse the king's food and are found ten times wiser."],
            ["2", "Nebuchadnezzar's dream of the four-metal statue and the stone — the four kingdoms and the everlasting fifth."],
            ["3", "The golden image and the fiery furnace — Shadrach, Meshach, and Abednego, and a fourth 'like a son of the gods.'"],
            ["4", "Nebuchadnezzar's madness and restoration — the king who learns 'heaven rules.'"],
            ["5", "Belshazzar's feast and the writing on the wall — 'weighed and found wanting'; Babylon falls that night."],
            ["6", "Daniel in the lions' den under Darius."],
            ["7", "The vision of the four beasts and the 'one like a son of man,' given dominion forever."],
            ["8-12", "Further visions — the ram and goat, the seventy weeks, the kings of the north and south (ch 11), and the resurrection and the end (ch 12)."],
        ],
        themes=[
            "GOD IS SOVEREIGN OVER EMPIRES — 'he removes kings and sets up kings' (2:21); the lesson every proud king must learn, that 'the Most High rules the kingdom of men and gives it to whom he will' (4:17).",
            "FAITHFULNESS UNDER PRESSURE — the food, the image, the prayer, the lions: God's people keep faith without power, and are vindicated (though ch 11's martyrs show that vindication is not always rescue).",
            "THE KINGDOM OF GOD — the stone that becomes a mountain (ch 2), the everlasting dominion given to 'one like a son of man' (ch 7): the world-empires give way to a kingdom that never ends.",
            "REVELATION OF MYSTERIES — God 'reveals the deep and hidden things' (2:22); the RAZ (mystery) made known, the sealed book, the interpreting angel — the apocalyptic conviction that the shape of history is known to God and can be disclosed.",
            "RESURRECTION AND JUDGMENT — Daniel 12:2 is the Old Testament's clearest word of a resurrection to 'everlasting life' or 'everlasting contempt,' the horizon the whole book leans toward.",
        ],
        key_words=["raz", "malku", "acharit-hayamim", "pesher"],
        key_people=["daniel", "nebuchadnezzar", "babylon", "shadrach-meshach-abednego"],
        source_text="Translated from the pointed Masoretic text (as printed by Mechon-Mamre). ⚠️ Daniel is the Old Testament's BILINGUAL book: it opens in Hebrew (1:1-2:4a), switches to ARAMAIC — the international language of the empires — for 2:4b-7:28, then returns to Hebrew for chapters 8-12. The Aramaic chapters are the ones about the Gentile world-powers, and the seam falls mid-sentence at 2:4. The Greek tradition adds material not in the Hebrew-Aramaic (the Song of the Three, Susanna, Bel and the Dragon) and survives in two divergent translations; this translation follows the Masoretic Hebrew-Aramaic and notes the major issues where they fall.",
        christ="Two images from Daniel became central to how the New Testament speaks of Christ. The STONE 'cut out without hands' that breaks the empires and grows to fill the earth (ch 2) is heard behind Jesus' 'stone the builders rejected' and the kingdom of God that starts small and grows (Matthew 21:42-44; 13:31-33). And the 'ONE LIKE A SON OF MAN' who comes with the clouds and is given everlasting dominion (7:13-14) is the title Jesus most often takes for himself — 'the Son of Man' — and quotes at his own trial (Mark 14:62). Daniel 9's 'seventy weeks' and 12's resurrection also run deep in New Testament expectation.",
        debates="The DATE is the master-question (6th-century prophecy vs 2nd-century review-as-prophecy — see above), and nearly everything else attaches to it: the identity of the four kingdoms (Rome vs Greece as the fourth), of 'Darius the Mede' (unattested in other sources), the meaning of the 'seventy weeks' (9:24-27), and the referent of the 'abomination that makes desolate' (Antiochus IV, a future antichrist, or both). The book's Persian and Greek loanwords, its place in the Writings, and the extraordinary precision of chapter 11 down to about 165 BC are the main data. Laid out with pedigrees; the library prints the text and does not cast a vote.",
    ),
    "1 Samuel": dict(
        hebrew_name="שְׁמוּאֵל א",
        hebrew_translit="Shemuel Alef",
        hebrew_meaning="'1 Samuel.' In the Hebrew Bible, Samuel is a SINGLE book (named for the prophet Samuel — 'God has heard,' or 'name of God'); the split into 1 and 2 Samuel comes from the Greek Septuagint, which divided it (and Kings) for length. It is the book of the great turn from the judges to the monarchy.",
        greek_name="Βασιλειῶν Αʹ (Basileion A) — '1 Kingdoms'",
        greek_meaning="The Septuagint groups Samuel and Kings as four 'books of the Kingdoms' (Basileion A-D), so that 1 Samuel is '1 Kingdoms' and 2 Samuel '2 Kingdoms' — a title that names the books by their subject, the rise and history of Israel's kings.",
        tagline="The hinge from the judges to the kings — Samuel the last judge and first great prophet, Saul the first king and his fall, and the rise of David; and it opens on a barren woman's answered prayer.",
        genre="HISTORICAL NARRATIVE — part of the 'Former Prophets' (Joshua, Judges, Samuel, Kings) in the Hebrew canon, and of what scholars call the Deuteronomistic History. Superb narrative art: the intertwined stories of Samuel, Saul, and David, told with a psychological depth and moral ambiguity rarely matched in ancient literature.",
        canon="In the Hebrew Bible, one book ('Samuel') among the Former Prophets; in the Christian Old Testament, 1 and 2 Samuel, following Ruth and preceding 1-2 Kings — the second stretch of the four-book sweep (Samuel-Kings) from the last judge to the fall of Jerusalem.",
        author="Anonymous. Jewish tradition (Talmud, Bava Batra 14b) credits Samuel with the early chapters and the prophets Nathan and Gad with the rest (cf 1 Chronicles 29:29) — though Samuel himself dies at 1 Samuel 25. Critical scholarship sees the book as woven from older sources (an 'Ark Narrative,' a 'History of David's Rise,' the 'Court History' of 2 Samuel) into the larger Deuteronomistic History, reaching its final form in or after the exile.",
        date="The events span roughly 1100-1010 BC (from Samuel's birth to Saul's death on Gilboa). The book's sources are old; its final composition is debated, commonly placed within the monarchy and edited into the Deuteronomistic History by the exile (6th century BC).",
        place="The central hill country of Israel — Ramah, Shiloh, Gibeah, and the Philistine borderlands — in the generation when Israel, pressed by the Philistines and led by a corrupt priesthood and a last great judge, demanded a king 'like all the nations.'",
        audience="Israel under, or remembering, the monarchy — a people wrestling with the institution of kingship itself: was asking for a king a rejection of God's own rule, or the means through which God would raise up David and, through him, the promise of an everlasting throne? The book holds both truths in tension and never quite resolves them.",
        structure=[
            ["1-7", "Samuel — his birth to Hannah, his call at Shiloh, the loss and return of the ark, and his judgeship over a repentant Israel."],
            ["8-15", "Saul — Israel demands a king; Samuel warns them and anoints Saul; Saul's early victories, his disobedience, and his rejection by God."],
            ["16-31", "David's rise and Saul's fall — David anointed in secret, Goliath, David at court, Saul's jealousy and pursuit, David the fugitive, and Saul's death on Mount Gilboa."],
        ],
        themes=[
            "KINGSHIP, and its ambiguity — Israel asks for a king 'like the nations,' which Samuel calls a rejection of God's own kingship (8:7); yet God grants it and works through it. The book neither simply endorses nor simply condemns the monarchy.",
            "GOD LIFTS THE LOWLY — sounded first in Hannah's song (2:1-10): 'he raises the poor from the dust… Jehovah kills and makes alive.' The barren bear children, the shepherd-boy becomes king, the mighty are brought down — the theme Mary's Magnificat takes up (Luke 1).",
            "OBEDIENCE OVER SACRIFICE — Saul is rejected not for weakness but for disobedience dressed up as worship; 'to obey is better than sacrifice' (15:22) is the book's verdict on him.",
            "THE ANOINTED ONE (MASHIACH) — Saul, then David, is 'Jehovah's anointed'; David, 'a man after God's own heart,' becomes the pattern of the king to come, and 'Jehovah looks on the heart, not the outward appearance' (16:7).",
            "THE WORD OF THE PROPHET — from Samuel's night-call ('speak, for your servant hears') onward, the prophet's word directs and judges the king; the throne stands under the word.",
        ],
        key_words=["shaal", "tzevaot", "neder", "nazir"],
        key_people=["samuel", "hannah", "eli", "shiloh"],
        source_text="Translated from the pointed Hebrew Masoretic Text (as printed by Mechon-Mamre). ⚠️ Samuel is famous among Old Testament books for the DIFFICULTY of its Hebrew text: the Masoretic text has suffered more than most from scribal slips, and the Greek Septuagint and the Dead Sea Scrolls (especially the Samuel scrolls from Qumran cave 4) frequently differ, at times preserving a better reading. This translation follows the Masoretic Hebrew and notes the major variants where they fall (already at 1:24, 'three bulls' vs 'a three-year-old bull').",
        christ="The book's gravity all leans toward DAVID — 'Jehovah's anointed' (mashiach, 'messiah'), the shepherd-king chosen not for his height but for his heart, whose throne God will promise to establish forever (2 Samuel 7). The New Testament traces Jesus to David's line and calls him 'Son of David'; the anointing, the shepherd, the rejected-then-exalted king are all patterns the Gospels take up. And the book opens with a note the Gospels echo directly: Hannah's song of the God who lifts the lowly and casts down the proud (2:1-10) is the model on which Mary sings her Magnificat (Luke 1:46-55).",
        debates="The main questions are SOURCES and COMPOSITION (how the Ark Narrative, the History of David's Rise, and the Court History were combined, and the book's place in the Deuteronomistic History), and the two attitudes to KINGSHIP the book seems to hold at once (the 'pro-' and 'anti-monarchic' strands of chapters 8-12). The TEXT itself is a standing problem — where the Masoretic Hebrew, the Septuagint, and the Qumran scrolls diverge, which preserves the original. And particular cruxes (the two accounts of how Saul became king, the two of David entering Saul's service, Goliath's height in the Hebrew vs the Greek) are much discussed.",
    ),
}
