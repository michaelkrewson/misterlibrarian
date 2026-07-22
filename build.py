#!/usr/bin/env python3
"""Build the MisterLibrarian Bible Project static site.

Single source of truth: mstr-trader's dashboard/mister_translation.html
(each chapter lives there as a <div class="chapter-panel" id="chapter-genN">
block). This script extracts every chapter panel and regenerates the public
site: one page per chapter with prev/next navigation, a Table of Contents
with live progress, the home page, and the Ask Mr. Librarian posts.

Usage:
    python3 build.py [--source /path/to/mister_translation.html]

After adding a new chapter to the source file, re-run this and push.
"""
import argparse
import hashlib
import html
import json
import math
import os
import re
from collections import defaultdict

from library_data import (DICTIONARY, ENCYCLOPEDIA, XREFS, VIDEO_CREDITS, VIDEO_QUEUE,
                           LINK_OVERRIDES, VERSE_OF_DAY, ROUTES, REGIONS,
                           CHRON_ERAS, CHRON_CHAPTERS, CHRON_EVENTS, BOOK_INTROS)

OUT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SOURCE = os.path.join(OUT, "source", "mister_translation.html")


def _asset_ver(name):
    """Short content hash of a static asset, for cache-busting its URL on every build
    (so a style.css edit can never be masked by a stale browser/CDN cache again)."""
    try:
        with open(os.path.join(OUT, name), "rb") as f:
            return hashlib.sha1(f.read()).hexdigest()[:10]
    except OSError:
        return "0"


CSS_VER = _asset_ver("style.css")
JS_VER = _asset_ver("player-clips.js")
AUDIO_JS_VER = _asset_ver("audio-reader.js")
NOTES_JS_VER = _asset_ver("reader-notes.js")

SITE_NAME = "The MisterLibrarian Bible Project"
TAGLINE = "Catalogued &amp; compared, one chapter at a time"
SITE_URL = "https://mistertranslation.com"
OG_IMAGE = f"{SITE_URL}/img/og-default.png"   # branded default link-preview image

# FormSubmit endpoint for the Ask-a-Question form. This is the activated form's
# random alias (delivers to the librarian's gmail without exposing the address in
# the page source). Verified working 2026-07-10 via a test submission.
FORM_ENDPOINT = "https://formsubmit.co/cea4e687d42ed1897e3ccd3753c4d75c"

# GoatCounter — free, open-source, cookie-less analytics (no consent banner needed;
# see https://www.goatcounter.com). Sign up, enable "Allow adding visitor counts on
# your website" in Settings > Integrations, and set this to your site code (the
# CODE in CODE.goatcounter.com). Leave as None and every tracking hook below is a
# silent no-op — the site behaves exactly as it does today.
GOATCOUNTER_CODE = "mistertranslation"

# Chapter registry: slug -> (book, chapter number, one-line teaser).
# Add a line here when a new chapter lands in the source file.
CHAPTERS = [
    ("gen1", "Genesis", 1, "The seven days — day one, the vault, and the image of God."),
    ("gen2", "Genesis", 2, "The sabbath, the divine name arrives, and “side,” not “rib.”"),
    ("gen3", "Genesis", 3, "The serpent, the fall, and the naked/crafty pun that spans the chapter break."),
    ("gen4", "Genesis", 4, "Cain and Abel, the first murder, and “am I my brother’s keeper?”"),
    ("gen5", "Genesis", 5, "Ten generations, one drumbeat — and the one man who never dies."),
    ("gen6", "Genesis", 6, "The sons of God, the Nephilim, Jehovah’s regret, and the ark."),
    ("gen7", "Genesis", 7, "The flood: creation run in reverse, and “Jehovah shut him in.”"),
    ("gen8", "Genesis", 8, "God remembers Noah — the raven, the dove, and the first altar."),
    ("gen9", "Genesis", 9, "Meat and blood, the first law, and the bow hung in the clouds."),
    ("gen10", "Genesis", 10, "The Table of Nations: the whole known world, drawn as one family tree."),
    ("gen11", "Genesis", 11, "Babel and babble — and the quiet road to Ur."),
    ("gen12", "Genesis", 12, "Lekh lekha: the call of Abram, and Egypt as the Exodus in miniature."),
    ("gen13", "Genesis", 13, "Abram and Lot part ways — the land too small for both, and the Hebrew word for “separate” that decides everything."),
    ("gen14", "Genesis", 14, "The war of the kings, Abram rescues Lot, and Melchizedek — bread, wine, the first tithe, and the first “Hebrew.”"),
    ("gen15", "Genesis", 15, "The covenant of the pieces — the stars, “counted to him as righteousness,” and the God who walks between the halves alone."),
    ("gen16", "Genesis", 16, "Hagar and Ishmael — the Bible's first angel, the runaway slave-girl, and the God who sees."),
    ("gen17", "Genesis", 17, "The covenant in the flesh — El Shaddai, Abram becomes Abraham, Sarai becomes Sarah, and a face-down laugh names Isaac."),
    ("gen18", "Genesis", 18, "Three visitors at Mamre, Sarah's laugh — and Abraham arguing the Judge of all the earth down to ten."),
    ("gen19", "Genesis", 19, "Sodom's last night — the two angels at the gate, sulfur and fire at sunrise, a pillar of salt, and the cave above Zoar."),
    ("gen20", "Genesis", 20, "The sister-ruse replayed at Gerar — Abimelech's dream, the Bible's first 'prophet,' and the pagan king with the integrity."),
    ("john1", "John", 1, "The Word made flesh — the Prologue and its “was God / a god,” the Lamb of God, and the first disciples."),
    ("john2", "John", 2, "Water into wine at Cana — the beginning of the signs — and the temple cleared at the first Passover: “destroy this temple.”"),
    ("2john1", "2 John", 1, "The shortest book in the Bible by verse count — one sheet of papyrus from \"the elder\" to \"a chosen lady,\" whom nobody has ever conclusively identified. Truth and love welded together in three verses, then the hard instruction: a travelling teacher who brings a different Christ gets no house and no welcome, because paying for a mission is joining it."),
    ("3john1", "3 John", 1, "The most private document in the Bible — a note from \"the elder\" to one man, Gaius, about a local quarrel. It commands the exact thing 2 John forbade (receive the travelling brothers) because the travellers are the opposite men; and it names Diotrephes, \"who loves to be first,\" a churchman who throws people out of the assembly for the crime of hospitality. It ends: greet the friends by name."),
    ("jude1", "Jude", 1, "The New Testament's fiercest short letter — twenty-five verses from a brother of Jesus who calls himself only 'a slave of Jesus Christ,' urging the church to 'contend for the faith once for all delivered.' A torrent of judgment-examples (the fallen angels, Sodom, Cain, Balaam, Korah), storm-and-sea images (waterless clouds, wandering stars), the archangel Michael disputing over the body of Moses, a prophecy quoted from ENOCH — a book that is not in the Bible — and, at the end, one of Scripture's greatest doxologies."),
    ("rev1", "Revelation", 1, "The unveiling begins — Patmos, the Lord's day, one like a son of man among the lampstands, and the Alpha and the Omega."),
    ("rev2", "Revelation", 2, "The letters begin — Ephesus's lost first love, Smyrna's crown, Satan's throne at Pergamum, and Jezebel of Thyatira."),
    ("dan1", "Daniel", 1, "Babylon takes its first captives — four renamed youths, a ten-day test of vegetables and water, and 'ten hands better' than the magicians."),
    ("dan2", "Daniel", 2, "Nebuchadnezzar's dream, and an impossible test — tell me the dream I will not tell you, or die. Daniel prays, the mystery is revealed, and he sings: God 'removes kings and sets up kings.' Then the dream itself: a great statue of gold, silver, bronze, and iron, its feet iron mixed with clay — and a stone cut without hands that shatters it all and grows into a mountain filling the earth. The four kingdoms, and the everlasting fifth; and the chapter where the book turns from Hebrew to ARAMAIC."),
    ("dan11", "Daniel", 11, "The angel's scroll of wars — Persia, Alexander, the kings of south and north, the abomination that desolates — and the seam where history becomes hope."),
    ("dan12", "Daniel", 12, "The sleepers in the ground of dust wake — everlasting life named for the first time, the sealed book, two numbers nobody has decoded, and a lot promised at the end of the days."),
    ("mat5", "Matthew", 5, "The Sermon on the Mount opens in red letters — eight Happy-sayings, salt and light, not one iota, and six rounds of 'You have heard… but I say': anger, lust, oaths, the other cheek, love for enemies."),
    ("mat6", "Matthew", 6, "The Sermon's middle chapter — alms, prayer, and fasting in secret; the Lord's Prayer and its famous missing doxology; treasure, the undivided eye, Mammon — and the birds and the lilies."),
    ("mat7", "Matthew", 7, "The Sermon's finale — the splinter and the beam, ask-seek-knock, the Golden Rule signed, the narrow gate, wolves and fruit, 'I never knew you' — and the house on the rock."),
    ("mark1", "Mark", 1, "The most breathless of the four Gospels starts already at a run — no birth, no genealogy, just a grown man at a river and the word 'immediately' eleven times over. The heavens are TORN open at the baptism (the same violent verb as the temple curtain at the end), a demon is the first to name Jesus correctly, and a leper is healed by a man 'moved with anger' who reaches across the line and touches him."),
    ("luke1", "Luke", 1, "The longest chapter in the Gospels and the songbook of the church — two annunciations set against each other (a priest struck dumb for doubting, a girl in Nazareth blessed for believing), the leap in Elizabeth's womb, and two of the great canticles: Mary's Magnificat ('he has brought down rulers from thrones and lifted up the lowly') and Zechariah's Benedictus ('the dawn from on high')."),
    ("jer1", "Jeremiah", 1, "The call of Jeremiah — the longest, most turbulent prophetic career in the Bible opens on a boy who says 'I am only a youth.' Known before the womb and made 'a prophet to the nations,' his mouth is touched and filled, and he is charged with the six verbs that are the program of the whole book: to uproot and to tear down, to destroy and to overthrow, to build and to plant. Two visions seal it — an almond branch (God WATCHING over his word) and a boiling pot tilting from the north (the disaster coming) — and a frightened boy is made an iron pillar."),
    ("jer20", "Jeremiah", 20, "Pashhur and the stocks — the prophet renames his jailer Terror-All-Around, names Babylon at last, confesses the fire shut up in his bones — and curses the day he was born."),
    ("jer21", "Jeremiah", 21, "The final siege — Zedekiah's delegation asks for a miracle and hears the bleakest answer in the book: the Exodus formula aimed inward, the way of life through the enemy camp, and fire for the cedar forest."),
    ("jer22", "Jeremiah", 22, "The tariff of the last kings — Shallum carried to Egypt, Jehoiakim's donkey-burial, and Coniah the signet torn off God's right hand; 'is that not to know me?' and 'write this man childless.'"),
    ("prov1", "Proverbs", 1, "The prologue to wisdom — the book's whole toolkit in seven verses, 'the fear of Jehovah is the beginning of knowledge,' a father's warning against the gang, and Lady Wisdom crying aloud in the streets."),
    ("gen21", "Genesis", 21, "Isaac is born and the laughter lands — then Hagar's second desert scene ('God heard the boy, there where he is'), seven ewe-lambs, the well of the oath, and the Everlasting God at a tamarisk."),
    ("gen22", "Genesis", 22, "The Aqedah — 'take your son, your only one, whom you love': the binding of Isaac on Moriah, the ram in the thicket, the mountain of seeing, and the promise sealed by oath."),
    ("gen23", "Genesis", 23, "Sarah dies at Hebron, and Abraham — a landless resident alien in the land promised to his seed — buys the cave of Machpelah for 400 shekels: the first foothold of the Promised Land is a grave."),
    ("gen24", "Genesis", 24, "The longest chapter in Genesis — Abraham's servant is sent to the old country for Isaac's bride; the sign at the well tests kindness, Rebekah answers 'I will go,' and the tent of Sarah is filled again."),
    ("gen25", "Genesis", 25, "Abraham dies at 175 and Isaac and Ishmael bury him together; the twins Esau and Jacob are born wrestling — 'the elder will serve the younger' — and Esau sells his birthright for a bowl of red stew."),
    ("gen26", "Genesis", 26, "The one chapter all about Isaac — a famine and the sister-ruse at Gerar, the covenant reaffirmed, the patient re-digging of his father's wells (Esek, Sitnah, Rehoboth), and a pact with Abimelech at Beersheba."),
    ("gen27", "Genesis", 27, "The stolen blessing — Rebekah disguises Jacob to deceive the blind, dying Isaac and steal Esau's blessing; Esau's great and bitter cry, 'Bless me too, my father!', and his murderous grief that drives Jacob to flee."),
    ("gen28", "Genesis", 28, "Jacob flees toward Haran and, with a stone for a pillow, dreams of a stairway between earth and heaven — 'Surely Jehovah is in this place, and I did not know it!' — names it Bethel, and vows his first vow."),
    ("gen29", "Genesis", 29, "Jacob meets Rachel at the well and serves seven years for her that 'seemed but a few days'; but in the morning — 'behold, it was Leah!' The deceiver is deceived, and Jehovah opens the unloved wife's womb."),
    ("gen30", "Genesis", 30, "The war of the wives: Rachel's 'Give me children, or else I die!', the maidservants' sons, and the mandrake bargain — eight more children born (Dan through Joseph). Then Jacob out-shrewds Laban with the peeled rods and the speckled flocks, and 'increased exceedingly.'"),
    ("gen31", "Genesis", 31, "Jacob flees Haran with his family and flocks; Rachel steals her father's household gods and hides them under the camel-saddle; Laban pursues and is warned off in a dream. Two schemers end their twenty years at a heap of stones — Galeed and Mizpah: 'May Jehovah watch between me and you.'"),
    ("gen32", "Genesis", 32, "Coming home to face the brother he cheated, Jacob is met by angels at Mahanaim, sends a lavish gift ahead to Esau, and prays his first prayer ('I am too small…'). Then, left alone by the Jabbok, he wrestles a man till dawn — and is crippled, blessed, and renamed ISRAEL: 'for you have striven with God and prevailed.'"),
    ("gen33", "Genesis", 33, "The dreaded reunion becomes an embrace: Esau runs to meet the brother who cheated him, falls on his neck, and weeps — 'to see your face is like seeing the face of God.' Jacob presses his 'blessing' back on him, then settles at Shechem, buys land, and builds an altar: El-Elohe-Israel."),
    ("gen34", "Genesis", 34, "The dark chapter at Shechem. Dinah, Jacob's daughter, is violated by the prince Shechem; her brothers answer 'with deceit,' demanding the whole town be circumcised — then Simeon and Levi fall on the helpless city on the third day, kill every male, and carry off its wealth, women, and children. Jacob rebukes them only for the danger they have made; they answer with a question no one answers: 'Should he treat our sister like a prostitute?'"),
    ("gen35", "Genesis", 35, "Jacob keeps his vow: back to Bethel, the foreign gods buried under the oak, and his name sealed a second time — Israel — under the promise of El Shaddai. Then the road takes its toll: Deborah's oak of weeping, Rachel dead in childbirth on the way to Bethlehem (Ben-oni, whom his father renames Benjamin), Reuben's sin against his father's bed, the twelve sons named at last, and old Isaac buried at Hebron by Esau and Jacob together."),
    ("gen36", "Genesis", 36, "The book pauses to catalogue Esau. His Canaanite wives and sons, his peaceful move to the red highlands of Seir 'away from his brother Jacob,' the clan-chiefs of Edom, the older Horite people they displaced, and eight kings who reigned in Edom 'before any king reigned over Israel' — and, hidden in the roll, the birth of Amalek, Israel's oldest enemy. The brother's line is honored and closed before the story turns wholly to Joseph."),
    ("gen37", "Genesis", 37, "The story comes home to Jacob's house — and to Joseph: the long ornamented tunic, the two dreams that make his brothers hate him, the errand to Shechem, the pit at Dothan, and twenty pieces of silver. The brothers dip the coat in a goat's blood and send it back with two words their father's own past taught him to dread — “recognize, please” — and Jacob, refusing all comfort, becomes the first person in the Bible to name Sheol."),
    ("gen38", "Genesis", 38, "The story stops dead and turns to Judah — who goes down from his brothers, marries a Canaanite, buries two sons, and withholds the third from their widow. Tamar takes her future by stratagem: veiled at the Opening of the Eyes, she secures his seal, cord and staff, and when he sentences her to be burned she sends them back with the two words he taught his own father to dread — “recognize, please.” His answer, “She is more righteous than I,” is the hinge of his life, and the twins born at the end carry the line to David."),
    ("gen39", "Genesis", 39, "Down in Egypt, in the house of the man who bought him — and the narrator, who never once named God while Joseph was being sold, now says four times that “Jehovah was with Joseph.” He runs Potiphar's whole estate; his master's wife, day after day, wants him; he refuses, and she keeps the garment he leaves in her hand. A second cloth is used to tell a second lie about him, and he goes to prison — where he is promptly put in charge of that too."),
    ("gen40", "Genesis", 40, "Pharaoh's cupbearer and baker land in Joseph's prison and dream on the same night — three branches and three baskets. The dreamer who has not mentioned a dream since the pit reads both, correctly, including the one nobody wanted: the same court phrase, “Pharaoh will lift up your head,” means pardon for one man and decapitation for the other, and on the king's birthday it lands on both at once. Joseph asks one favour in return — “remember me” — and the chapter's last words are “and he forgot him.”"),
    ("gen41", "Genesis", 41, "Two years after the cupbearer forgot him, Pharaoh dreams of seven fat cows swallowed by seven gaunt ones, and not one of Egypt's diviner-priests can read it. Joseph is run out of the pit, shaved, and set in front of a king — and his first word is “Not I.” He reads the dream, then hands over an unrequested seven-year grain policy, and walks out of the room governor of Egypt with the king's signet on his hand: thirty years old, thirteen years after his brothers sold him."),
    ("gen42", "Genesis", 42, "Ten brothers go down to Egypt for grain and bow to the governor, faces to the ground — the dream of the sheaves, fulfilled through the pit that was meant to stop it. He recognizes them instantly and makes himself unrecognizable, calls them spies, and jails them three days; and in the cell they say to each other, not knowing he understands every word, “we are guilty concerning our brother — we saw the distress of his soul when he pleaded with us.” He turns away and weeps, binds Simeon, and sends the rest home with their silver hidden in the sacks."),
    ("gen43", "Genesis", 43, "The grain runs out and Jacob has to let Benjamin go. Judah puts up himself — “I myself will be surety for him” — where Reuben had offered his own sons, and his father says yes. They go down with double silver and a gift of balm, gum and ladanum: the very cargo the caravan was carrying the day they sold Joseph into it. An Egyptian steward greets them with the word their family could not say — peace — and the governor seats them in exact birth order, stares at his mother's other son, and has to leave the room."),
    ("gen44", "Genesis", 44, "The silver cup is planted in Benjamin's sack and the brothers are overtaken on the road — chapter 37 rebuilt to specification: Rachel's favoured son condemned alone, and the other ten explicitly free to go home unharmed. Not one of them takes it. Then Judah steps forward and speaks for seventeen verses, the longest speech in Genesis, almost entirely in quotation of an old man's grief — and offers to stay a slave in the boy's place."),
    ("gen45", "Genesis", 45, "Joseph clears the room and the restraint he has held for two chapters fails in a single clause — the Egyptians hear him weeping through the palace wall. \"I am Joseph. Is my father still alive?\" His brothers cannot answer; they are terrified. Then the sentence twenty-two years in arriving: \"it was not you who sent me here, but God\" — said nine words after \"whom you sold.\" And in Canaan an old man's heart goes numb, until he sees the wagons."),
    ("gen46", "Genesis", 46, "Israel packs up everything and gets as far as Beersheba — the last town in Canaan — and stops to sacrifice, because every earlier descent into Egypt in this book went badly or was forbidden outright. God answers in the visions of the night with the permission he came for, and a promise in two halves: \"I myself will go down with you… and I myself will surely bring you up again.\" Then the seventy names, one by one, and an old man who has seen his son's face."),
    ("gen47", "Genesis", 47, "Five brothers say the line Joseph gave them and it works. Then a landless herdsman is stood in front of the king of Egypt and, twice, blesses him — and when asked his age answers that his years have been \"few and evil.\" Then the famine grinds on and Joseph buys Egypt for Pharaoh: its silver, then its livestock, then its land, and finally its people, who thank him for it. Genesis reports all of it without a word of praise or blame."),
    ("gen48", "Genesis", 48, "Jacob adopts Joseph's two Egyptian sons as his own — a legal act that turns them into tribes and hands Joseph the double portion Reuben forfeited. Then a blind father blesses two brothers of unequal birth order, and crosses his hands. Joseph takes hold of his father's wrist to correct him and is refused: \"I know, my son, I know.\" The Hebrew word for crossing the hands is the word for acting with insight."),
    ("gen49", "Genesis", 49, "Jacob calls all twelve to his bed to tell them what will happen \"in the latter days\" — the longest poem in Genesis, and not gentle. Reuben is stripped of his rank in two lines, Simeon and Levi have their anger cursed by name for Shechem, and Judah is handed the sceptre with the most disputed sentence in the book. Then a dying man stops mid-prophecy to pray, finishes with a property deed, and lies down."),
    ("gen50", "Genesis", 50, "The last chapter. Egypt gives a foreign shepherd a state funeral, and then \u2014 with the old man safely dead \u2014 ten frightened men invent a message from him and beg for their lives. What they get is the sentence the whole book has been walking toward: \"you devised evil against me; God devised it for good.\" It ends with an oath about a body, and an embalmed man in a box in the wrong country."),
    ("exod1", "Exodus", 1, "A family becomes a nation, a new king 'who did not know Joseph' enslaves them, and two midwives who feared God defy Pharaoh's order to kill the boys — the second book of the Bible opens."),
    ("exod2", "Exodus", 2, "Moses is born and floated on the Nile in an ark of papyrus, drawn out by Pharaoh's daughter; grown, he kills an Egyptian and flees to Midian, marries Zipporah — and God hears, remembers, sees, and knows."),
    ("exod3", "Exodus", 3, "The burning bush that is not consumed, holy ground, and the Name itself — 'I will be what I will be,' Jehovah, 'my name forever' — with the commission to Pharaoh and the promise of a land flowing with milk and honey."),
    ("exod4", "Exodus", 4, "Three signs to make Israel believe — a staff that turns to a serpent, a hand struck leprous and healed, water turned to blood — and Moses' last excuses: 'I am heavy of mouth.' God's anger, and Aaron given as his mouth; the return to Egypt where 'those who sought your life are dead'; the staggering word 'Israel is my firstborn son' with the tenth plague already threatened; and the strangest night in the Torah, the 'bridegroom of blood.'"),
    ("exod5", "Exodus", 5, "The first audience with Pharaoh, and it goes badly. 'Let my people go' is met with 'WHO is Jehovah, that I should obey his voice? I do not know Jehovah' — the question the whole book exists to answer. Pharaoh calls the request laziness and retaliates precisely: gather your own straw, deliver the same quota of bricks. The Israelite foremen are beaten, the people turn on Moses, and Moses turns on God: 'you have not delivered your people at all.'"),
    ("exod6", "Exodus", 6, "God answers Moses' accusation with his Name: 'I am Jehovah' — and the hardest verse in the book about that Name ('by my name Jehovah I did not make myself known' to the patriarchs, though Genesis has them using it). Then the SEVEN 'I will' promises of redemption, whose first four became the four cups of the Passover seder — spoken to a people so crushed by their labor they cannot hear them. And a Levite genealogy that stops at Moses and Aaron, because it is not a census but a set of credentials."),
    ("exod7", "Exodus", 7, "'See, I have made you God to Pharaoh, and Aaron your brother shall be your prophet' — the Bible's clearest definition of a prophet, in passing. Aaron's staff becomes not a snake but a TANNIN, the serpent-dragon of Pharaoh's own crown, and swallows the magicians'. Then the first plague: the Nile — worshipped as the god Hapi, and the river Hebrew boys were drowned in — turned to blood. ⚠ The Masoretic chapter runs to 29 verses; English Bibles print the last four as 8:1-4."),
    ("exod8", "Exodus", 8, "Plagues two through four. Offered the end of the frogs, Pharaoh answers 'TOMORROW' — one more night with them — and when relief comes he uses it to harden. Then the gnats, which Egypt's magicians cannot copy: 'This is the finger of God,' say the professionals, conceding what the king will not. And the swarms, the first plague to DISCRIMINATE — Goshen set apart — after which Pharaoh stops refusing and starts bargaining, every offer keeping a hostage. ⚠ Masoretic numbering: this chapter = English 8:5-32."),
    ("exod9", "Exodus", 9, "Plagues five, six, and seven. The pestilence on Egypt's herds — and Pharaoh SENDS to verify that not one animal of Israel's died, and hardens anyway. The boils that drive the magicians from the room for good. And the hail with fire in it, which arrives with something no plague had before: a day's warning and instructions for surviving it — so that for the first time some Egyptians BELIEVE, and run their households indoors. ⚠ At 9:12 the narrator says for the first time that JEHOVAH hardened Pharaoh's heart; through the five plagues before it, Pharaoh hardened his own."),
    ("exod10", "Exodus", 10, "Locusts and darkness — and the chapter where Pharaoh's own court breaks before he does: 'How long shall this man be a snare to us? Do you not yet know that Egypt is destroyed?' The plagues are also given a new reason here: not Pharaoh at all, but a story to be RECOUNTED to a son and a son's son. The bargaining ends when Moses refuses the last hostage: 'not a hoof shall be left behind' — and Pharaoh ends the interview with a death threat."),
    ("exod11", "Exodus", 11, "The tenth blow announced. This is the sentence handed down back at 4:22-23 — 'Israel is my firstborn son… I will kill your son, your firstborn' — now formally served: at midnight, every firstborn from the throne to the millstones. Israel is told to ASK the neighbors for silver and gold (the verb the KJV turned into 'borrow', which made the exodus look like a fraud for three centuries), a great OUTCRY is promised to Egypt in the very word Exodus used for Israel's own, and Moses walks out of the palace in burning anger."),
    ("exod12", "Exodus", 12, "The chapter that answers everything since chapter 1 — and answers it not with another plague but with a calendar, a lamb, unleavened bread, and blood on two doorposts and a lintel. The year itself is re-founded on the night of the rescue; the rite is built around a child's question before the rescue has even happened; the tenth blow falls at midnight and Pharaoh, who began with 'I do not know Jehovah', ends by asking for a blessing. Israel walks out with a MIXED MULTITUDE — and the chapter closes with one law for the native and the sojourner alike."),
    ("exod13", "Exodus", 13, "Because Israel's firstborn were spared, they are claimed: 'consecrate to me every firstborn — it is mine.' A donkey's firstling is bought back with a lamb or its neck is broken; a firstborn son is ALWAYS bought back, never sacrificed. The command to tell a son comes twice more here (four times in four chapters). Then the first thing God does with a free people is take them the LONG way — 'lest they change their minds when they see war' — while Moses carries Joseph's bones out on an oath four hundred years old, and a pillar of cloud and fire goes ahead."),
    ("exod14", "Exodus", 14, "The sea. Israel is told to turn BACK and camp with the water behind them — a militarily absurd position, and the text says outright it is bait: 'Pharaoh will say, they are wandering in confusion.' Six hundred chariots overtake them, Israel's first words as a free people are 'better to serve the Egyptians than to die in the wilderness', and a strong east wind blows all night. ⚠ Note what verse 28 says drowned — the ARMY — and what it never says."),
    ("2sam1", "2 Samuel", 1, "Saul is dead on Gilboa, and a man runs into Ziklag with the crown in his hand and a story that does not match the one 1 Samuel just told. David — who spent years as Saul's hunted rival — tears his clothes, fasts, executes the messenger for laying a hand on 'Jehovah's anointed', and then chants the Song of the Bow: 'How the mighty have fallen.' A lament that says nothing of the spear thrown at him, the years of pursuit, or the priests of Nob."),
    ("lev1", "Leviticus", 1, "The manual of worship opens: from the tent he has just filled, Jehovah CALLS Moses and gives the law of the burnt-offering — the herd, the flock, and the poor person's two birds, each ascending whole in smoke, 'a soothing aroma to Jehovah.'"),
    ("num1", "Numbers", 1, "'In the wilderness of Sinai' the redeemed people are counted and arrayed as an army for the march — twelve tribes, twelve chieftains, 603,550 fighting men; and one tribe, Levi, left off the war-roll to carry and guard the tent at the camp's center."),
    ("deut1", "Deuteronomy", 1, "Moses begins the longest speech of his life, on the far side of the Jordan, to a generation that was not there. \"Eleven days from Horeb\" — and then \"in the fortieth year\": the whole chapter is the explanation of that gap. Judges appointed, spies sent, a land refused, and the flat closing line that nothing happened for a very long time."),
    ("josh1", "Joshua", 1, "The book of the crossing opens on the worst possible news — \"Moses my servant is dead\" — and refuses to let it stop anything: rise, cross the Jordan. Three times Joshua is told to be strong and resolute, and the courage he most needs turns out to be for keeping the scroll, not the sword. Then rations, a marching order, an old promise called in, and the people handing the charge back: \"only be strong and resolute.\""),
    ("judg1", "Judges", 1, "The conquest, told from underneath. It opens well — Israel asks God, Judah goes up, cities fall — and then, tribe by tribe marching north up the map, the same phrase tolls seven times: DID NOT DRIVE OUT. A king mutilated as he mutilated others, a woman who negotiates for water, iron chariots offered as an excuse, and a redeemed people putting the Canaanites to forced labour instead of removing them."),
    ("ruth1", "Ruth", 1, "The quiet counter-story to the Judges: a famine empties the House of Bread, a family flees to Moab and loses its men, and a widow named Naomi turns home 'empty' — while a Moabite daughter-in-law refuses to leave her with the Bible's great oath of loyalty: 'your people my people, your God my God.' Names turn to omens, Naomi renames herself Mara ('bitter'), and the last line opens a barley field where redemption is about to begin."),
    ("1sam1", "1 Samuel", 1, "The book that gives Israel its kings opens on a barren woman. Hannah, provoked year after year by her rival, prays silently at Shiloh until the priest Eli takes her for a drunk; she vows her son to God, and when Samuel is born she carries the weaned boy back and gives him away — 'lent to Jehovah' for life. The FIRST 'Jehovah of hosts' in the Bible, a wordplay ('asked') that reaches toward Saul, and the seed of the song (ch 2) that Mary's Magnificat will be built on."),
    ("mal1", "Malachi", 1, "The last of the prophets opens his case, and the people answer back — the move that is the book’s signature: ‘I have loved you’ / ‘in WHAT have you loved us?’ Jacob loved and Esau hated, Edom’s highlands left in rubble, and then the charge that fills the chapter: a priesthood bringing blind, lame and stolen animals to the altar of a God they find, above all, BORING. Try that on the Persian governor, says Malachi — and then, astonishingly, in the last book of the Old Testament: ‘from the rising of the sun to its setting my name is great among the nations.’"),
    ("ezek1", "Ezekiel", 1, "A deported priest sits beside an irrigation canal in southern Iraq — five years into the exile, in the year he should have begun serving at an altar he will never see again — and the heavens open. A storm out of the north, four living creatures with four faces each, wheels within wheels whose rims are full of eyes, a vault of terrible ice over their heads, and above the vault a sapphire throne with something on it that looks like a human being. Ezekiel never once says he saw God: he says he saw the appearance of the likeness of the glory of Jehovah, and fell on his face. The vault is the same word as Genesis 1, and the light around the throne is the war-bow of Genesis 9."),
    ("job1", "Job", 1, "A blameless man in a country nobody can find loses everything in a single afternoon — and the reader, unlike Job, is shown exactly why. In a heavenly council the Accuser (the Hebrew says ‘THE satan’, with the article: an office, not a name) asks the question the whole book exists to answer — ‘is it for NOTHING that Job fears God?’ Is anyone good unpaid? Four messengers arrive, each while the last is still speaking, each ending on the same sentence. Then Job tears his robe, falls to the ground, and blesses — using the very verb the Hebrew has been using all chapter to mean CURSE."),
    ("1kgs1", "1 Kings", 1, "The book opens on a body that will not work: an old king buried under blankets who cannot get warm, and a court that has just run a test and published the result. Within a verse one son is proclaiming himself king with a chariot and fifty runners — the exact sentence used of Absalom — and his father, the narrator notes, had never once in his life asked him why he had done anything. Then a prophet briefs a queen on what to say, and she says it better than he wrote it, and reminds the dying king of an oath the reader has never heard of. Solomon is anointed at the city\u2019s own spring while the rival feast is held out of sight downstream — and the winner\u2019s first act as king is to spare his brother, on a condition."),
    ("2kgs1", "2 Kings", 1, "A book that begins in the middle of somebody else\u2019s obituary — Kings is one scroll in Hebrew, and the Greek split fell mid-reign. A king falls through a roof lattice and, injured, sends to Baal-zebub of Ekron to ask whether he will live; his messengers are intercepted by a Messenger, and the question they carry back is asked three times, word for word: is it because there is no God in Israel? Then three companies of fifty are sent up a hill to fetch a prophet, and two of them are burned off it — a passage the New Testament itself objects to when two disciples propose repeating it and are rebuked. The man in the hair coat and the leather belt will be described again, eight centuries later, standing in a river."),
    ("1chr1", "1 Chronicles", 1, "The most extreme compression in the Bible. It opens with one word and no verb — \u201cAdam\u201d — and gives nine names where Genesis 5 gave thirty-two verses of ages and deaths. Fifty-four verses take the whole human race from creation to the kings of Edom, and in all of it exactly ONE man is given a verb. Watch what the compiler keeps and what he drops: \u201cAbram \u2014 he is Abraham\u201d is four words for the call, the covenant, Sodom, Isaac and Moriah; the sons of Isaac are \u201cEsau and ISRAEL\u201d, and the name Jacob never appears at all. And at the end, in a list of Edomite kings copied from Genesis, you can watch a text being copied by hand and see exactly which letters a tired scribe confuses."),
    ("2chr1", "2 Chronicles", 1, "Solomon\u2019s reign begins on the sentence 1 Kings 2 ended with — and the two chapters of coup, deathbed list and executions that got him there are simply not told. Then Gibeon, where Chronicles supplies the explanation Kings never gives for a king sacrificing at a high place: the tent of meeting Moses made was standing there, with Bezalel\u2019s bronze altar in front of it. God appears that night and Solomon asks for \u201cwisdom and KNOWLEDGE\u201d — where 1 Kings has him ask for a listening heart to discern good and evil, the same night rendered twice. And four verses after the gift, the chapter records that he collected chariots and imported horses from Egypt: the two things Deuteronomy forbids a king by name, set down without a word of comment. \u26a0 Eighteen verses in Hebrew; English Bibles print the last as 2:1."),
    ("ezra1", "Ezra", 1, "The book opens on the sentence the Hebrew Bible ENDS on. Chronicles closes the Jewish canon mid-decree \u2014 \u201clet him go up\u201d \u2014 and Ezra quotes the same words and finishes them. A Persian emperor\u2019s rescript is introduced with the prophets\u2019 own formula, \u201cthus says Cyrus\u201d; the same verb that stirs an emperor stirs a few dozen householders; and those who stay hand silver and gold to those who go, which is what happened the last time Israel walked out of a foreign country. Then the temple vessels Nebuchadnezzar shelved in his god\u2019s treasury are counted back out by a Persian treasurer \u2014 and the inventory does not add up."),
    ("neh1", "Nehemiah", 1, "\u201cThe words of Nehemiah son of Hacaliah\u201d \u2014 no other book in the Hebrew Bible opens with a man\u2019s own name and then keeps going in the first person. He is in the Persian winter palace at Susa when men from Judah bring news that Jerusalem still lies open and disgraced, and he sits down and weeps and mourns for days, and then prays for four months. The prayer is made almost entirely of quotations from Deuteronomy \u2014 he is not composing, he is holding God to a document \u2014 and it ends by asking for mercy \u201cbefore this man\u201d, who happens to be the most powerful human being alive. Then the last five words of the chapter explain everything: now I was cupbearer to the king."),
    ("est1", "Esther", 1, "The only book in the Bible that never mentions God opens with a hundred and eighty days of a king showing people his money. Ahasuerus is XERXES, and the year is 483 BC \u2014 the same year Herodotus has him gathering his nobles to plan the invasion of Greece, a war this book never mentions and whose length is exactly the gap between chapters 1 and 2. Then, on the seventh day of the second banquet, drunk, he sends for his wife to be displayed alongside the furniture, and she refuses \u2014 and the Hebrew gives no reason whatever. What follows is a comedy at the expense of frightened officials: an empire\u2019s entire legal apparatus convened over a dinner-party snub, and a decree carried by the imperial post to a hundred and twenty-seven provinces announcing that men should be in charge at home."),
]
# Spanish home-page teasers, keyed by chapter slug. The Spanish index used to
# reuse CHAPTERS' ENGLISH teaser text, so es.html showed Spanish titles over
# English descriptions. Add a line here whenever a source/es/<slug>.html lands;
# build_es WARNS (and prints no description) if one is missing, rather than
# silently falling back to English again.
TEASERS_ES = {
    "gen1":  "Los siete días — el día uno, la bóveda, y la imagen de Dios.",
    "gen34": "El capítulo oscuro de Siquem: Dina es violada, y sus hermanos responden «con engaño».",
    "gen35": "Jacob cumple su voto en Betel y entierra los dioses extranjeros — y el camino se cobra a Débora, a Raquel y a Isaac.",
    "gen36": "El libro se detiene a catalogar a Esaú: sus mujeres, los jefes de Edom y, escondido en la lista, el nacimiento de Amalec.",
    "gen37": "La túnica, los dos sueños, el pozo en Dotán y veinte piezas de plata — y dos palabras que volverán: «reconoce, por favor».",
    "gen38": "Judá y Tamar: ella toma su sello, su cordón y su báculo, y se los devuelve con las dos palabras que él enseñó a su padre.",
    "gen39": "Abajo en Egipto, en casa de Potifar — y el narrador, que no nombró a Dios ni una vez mientras vendían a José, ahora lo dice cuatro veces.",
    "gen40": "El copero y el panadero sueñan la misma noche: «el faraón alzará tu cabeza» significa indulto para uno y horca para el otro.",
    "gen41": "El faraón sueña con siete vacas gordas y nadie sabe leerlo. José sale del pozo, dice «no yo», y acaba gobernando Egipto.",
    "mark1": "El Evangelio m\u00e1s veloz empieza ya corriendo: los cielos RASGADOS, un demonio que lo reconoce primero, y un leproso tocado.",
    "luke1": "El cap\u00edtulo m\u00e1s largo de los Evangelios: dos anunciaciones \u2014un sacerdote enmudecido por dudar, una joven bendecida por creer\u2014 y dos c\u00e1nticos, el Magn\u00edficat y el Benedictus.",
    "3john1": "El documento más privado de la Biblia: \u00abel anciano\u00bb a Gayo, y contra Di\u00f3trefes, \u00abque ama ser el primero\u00bb.",
    "jude1": "La carta breve más feroz del NT: un hermano de Jesús que se llama solo «esclavo», luchando por «la fe una vez dada» — y que cita a Enoc, un libro que no está en la Biblia.",
    "2john1": "El libro más corto de la Biblia: \u00abel anciano\u00bb a \u00abuna se\u00f1ora elegida\u00bb — verdad y amor, y una puerta que no se abre.",
    "judg1": "La conquista contada por debajo: empieza bien, y luego, tribu por tribu, la misma frase suena siete veces — no expuls\u00f3.",
    "ruth1": "La contrahistoria serena de los Jueces: hambre, huida a Moab, tres muertes — y una nuera moabita que no se aparta con el gran juramento: «tu pueblo mi pueblo, tu Dios mi Dios».",
    "1sam1": "El libro que da reyes a Israel abre sobre una mujer estéril: Ana ora en silencio en Silo, el sacerdote Elí la toma por ebria, y cuando nace Samuel lo entrega —«prestado a Jehová» de por vida. El primer «Jehová de los ejércitos» de la Biblia, y la semilla del cántico que será el Magníficat.",
    "josh1": "\u00abMois\u00e9s ha muerto\u00bb — y ahora, cruza el Jord\u00e1n. Tres veces: s\u00e9 fuerte y resuelto; y el valor es para el rollo, no la espada.",
    "deut1": "\u00abOnce d\u00edas desde Horeb\u00bb — y luego \u00aben el a\u00f1o cuarenta\u00bb. Mois\u00e9s empieza a explicar los cuarenta a\u00f1os.",
    "gen50": "El \u00faltimo cap\u00edtulo: \u00abustedes pensaron mal contra m\u00ed; Dios lo pens\u00f3 para bien\u00bb. Y un ata\u00fad en Egipto.",
    "gen49": "El poema del lecho de muerte: Rubén degradado, Simeón y Leví maldecidos, y a Judá el cetro. Y luego una escritura de propiedad.",
    "gen48": "Jacob adopta a los dos hijos egipcios de José, y luego cruza las manos a propósito: \u00abLo sé, hijo mío, lo sé\u00bb.",
    "gen47": "Jacob bendice al faraón y llama a sus a\u00f1os \u00abpocos y malos\u00bb. Y José compra Egipto entero para el faraón.",
    "gen46": "Israel se detiene en Beerseba y Dios le habla de noche: \u00abNo temas bajar a Egipto\u00bb. Y luego los setenta nombres.",
    "gen45": "José despide a todos y se quiebra: \u00abYo soy José. \u00bfVive a\u00fan mi padre?\u00bb Y luego: no fueron ustedes, sino Dios.",
    "gen44": "La copa de plata aparece en el saco de Benjamín y los otros diez quedan libres de marcharse. Ninguno lo hace. Y Judá habla.",
    "gen43": "Se acaba el grano y Jacob debe dejar ir a Benjamín. Judá se ofrece a sí mismo como fiador, y bajan con un regalo que ya hizo ese camino.",
    "gen42": "Diez hermanos se inclinan ante un gobernador al que no reconocen — y confiesan, sin saber que él entiende cada palabra: «somos culpables».",
    "jer1": "El llamado de Jeremías: un muchacho que dice «solo soy un joven», conocido antes del vientre, hecho «profeta a las naciones» — con los seis verbos (arrancar, derribar… edificar y plantar), la rama de almendro y la olla hirviente del norte.",
    "dan2": "El sueño de Nabucodonosor y una prueba imposible: la estatua de oro, plata, bronce y hierro con pies de barro, y la piedra cortada sin manos que la deshace y se hace montaña — los cuatro reinos y el quinto eterno; y el capítulo donde el libro pasa del hebreo al ARAMEO.",
    "exod4": "Tres señales para que Israel crea —vara que se hace serpiente, mano leprosa, agua vuelta sangre— y las últimas excusas de Moisés; Aarón como su boca, y la palabra asombrosa: «Israel es mi hijo primogénito», con la décima plaga ya anunciada.",
    "exod5": "La primera audiencia con el faraón sale mal: «¿Quién es Jehová para que yo oiga su voz?» — ladrillos sin paja, los capataces israelitas golpeados, el pueblo contra Moisés y Moisés contra Dios: «no has librado a tu pueblo».",
    "exod6": "Dios responde con su Nombre: «Yo soy Jehová» —y el versículo más difícil sobre ese Nombre— y las SIETE promesas «yo os», base de las cuatro copas de la Pascua, dichas a un pueblo demasiado aplastado para oírlas.",
    "exod7": "«Te he puesto como Dios para el faraón, y Aarón tu hermano será tu profeta»: la vara se hace TANÍN —el dragón del tocado del faraón— y traga las de los magos; luego la primera plaga, el Nilo (el dios Hapi) vuelto sangre.",
    "exod8": "Plagas dos a cuatro: ofrecido el fin de las ranas, el faraón responde «MAÑANA»; los piojos que los magos no pueden copiar («esto es el dedo de Dios»); y las nubes de insectos, la primera plaga que distingue —Gosén queda aparte—. ⚠ Numeración masorética: este capítulo = 8:5-32 en español.",
    "exod9": "Plagas cinco, seis y siete: la peste sobre el ganado de Egipto — y el faraón MANDA a verificar que no murió ni una res de Israel, y se endurece igual —; las llagas que sacan a los magos de la sala para siempre; y el granizo con fuego dentro, que llega con algo que ninguna plaga tuvo antes: un día de aviso e instrucciones para sobrevivirlo, de modo que por primera vez algunos egipcios CREEN. ⚠ En 9:12 el narrador dice por primera vez que JEHOVÁ endureció el corazón del faraón.",
    "exod10": "Langostas y tinieblas — y el capítulo en que la propia corte del faraón se quiebra antes que él: «¿Hasta cuándo será este hombre un lazo para nosotros? ¿Todavía no sabes que Egipto está destruido?». Aquí las plagas reciben además una razón nueva: no el faraón, sino un relato que se CONTARÁ al hijo y al hijo del hijo. Y el regateo termina cuando Moisés rechaza el último rehén: «no quedará ni una pezuña».",
    "exod11": "El décimo golpe, anunciado. Es la sentencia dictada allá en 4:22-23 —«Israel es mi hijo primogénito… mataré a tu hijo, tu primogénito»— ahora notificada formalmente: a medianoche, todo primogénito desde el trono hasta las piedras del molino. A Israel se le manda PEDIR plata y oro a los vecinos (el verbo que la KJV convirtió en «tomar prestado», lo que hizo parecer un fraude al éxodo durante tres siglos), se promete a Egipto un gran CLAMOR con la misma palabra que Éxodo usó para el de Israel, y Moisés sale del palacio ardiendo en ira.",
    "exod12": "El capítulo que responde a todo lo ocurrido desde el capítulo 1, y no con otra plaga sino con un calendario, un cordero, pan sin levadura y sangre en dos postes y un dintel. El año mismo se refunda en la noche del rescate; el rito se construye en torno a la pregunta de un niño antes incluso de que el rescate ocurra; el décimo golpe cae a medianoche y el faraón, que empezó con «no conozco a Jehová», termina pidiendo una bendición. Israel sale con una MULTITUD MIXTA, y el capítulo cierra con una sola ley para el nativo y para el extranjero.",
    "exod13": "Como los primogénitos de Israel fueron perdonados, quedan reclamados: «conságrame todo primogénito: mío es». El primer nacido de un asno se rescata con un cordero o se le quiebra el cuello; un hijo primogénito se rescata SIEMPRE, nunca se sacrifica. El mandato de contárselo a un hijo aparece aquí dos veces más (cuatro en cuatro capítulos). Y lo primero que Dios hace con un pueblo libre es llevarlo por el camino LARGO —«no sea que cambien de parecer al ver la guerra»—, mientras Moisés saca los huesos de José por un juramento de cuatrocientos años y una columna de nube y de fuego va delante.",
    "exod14": "El mar. A Israel se le manda VOLVER atrás y acampar con el agua a la espalda —una posición militarmente absurda, y el texto dice sin rodeos que es un cebo: «el faraón dirá: andan errantes»—. Seiscientos carros les dan alcance, las primeras palabras de Israel como pueblo libre son «mejor nos era servir a los egipcios que morir en el desierto», y un fuerte viento del este sopla toda la noche. ⚠ Nótese qué dice el versículo 28 que se ahogó —el EJÉRCITO— y qué no dice nunca.",
    "2sam1": "Saúl ha muerto en Gilboa, y un hombre entra corriendo en Siclag con la corona en la mano y un relato que no cuadra con el que 1 Samuel acaba de contar. David —que pasó años siendo el rival perseguido de Saúl— rasga sus vestiduras, ayuna, manda ejecutar al mensajero por poner la mano sobre «el ungido de Jehová», y entona el Canto del Arco: «¡Cómo han caído los valientes!». Un lamento que no dice nada de la lanza que le arrojaron, ni de los años de persecución, ni de los sacerdotes de Nob.",
    "mal1": "El último de los profetas abre su caso y el pueblo le replica — la seña del libro: «Los he amado» / «¿En QUÉ nos has amado?». Jacob amado y Esaú aborrecido, los montes de Edom en ruinas, y luego la acusación que llena el capítulo: sacerdotes que traen animales ciegos, cojos y robados al altar de un Dios que, sobre todo, les parece ABURRIDO. Llévalo a tu gobernador persa, dice Malaquías — y luego, en el último libro del Antiguo Testamento: «desde donde el sol nace hasta donde se pone, grande es mi nombre entre las naciones».",
    "ezek1": "Un sacerdote deportado se sienta junto a un canal de riego en el sur de Irak —a cinco años del destierro, en el año en que debía haber empezado a servir ante un altar que ya no verá— y los cielos se abren. Una tempestad del norte, cuatro seres vivientes de cuatro rostros cada uno, ruedas dentro de ruedas con los aros llenos de ojos, una bóveda de hielo temible sobre sus cabezas y, encima de la bóveda, un trono de zafiro con algo que parece un ser humano. Ezequiel no dice ni una vez que vio a Dios: dice que vio la apariencia de la semejanza de la gloria de Jehová, y cayó sobre su rostro. La bóveda es la misma palabra que en Génesis 1, y la luz en torno al trono es el arco de guerra de Génesis 9.",
    "job1": "Un hombre íntegro, en un país que nadie sabe situar, lo pierde todo en una sola tarde — y el lector, a diferencia de Job, ve exactamente por qué. En un consejo celestial el Acusador (el hebreo dice «EL satán», con artículo: un cargo, no un nombre) hace la pregunta para la que existe todo el libro: «¿acaso teme Job a Dios DE BALDE?». ¿Es alguien bueno sin cobrar? Llegan cuatro mensajeros, cada uno mientras el anterior aún habla, todos terminando en la misma frase. Entonces Job rasga su manto, cae a tierra y bendice — con el mismísimo verbo que el hebreo lleva todo el capítulo usando para decir MALDECIR.",
    "1kgs1": "El libro abre sobre un cuerpo que ya no funciona: un rey anciano sepultado en mantas que no logra entrar en calor, y una corte que acaba de hacer una prueba y publicar el resultado. En un versículo, un hijo se proclama rey con carro y cincuenta corredores —la frase exacta que se usó de Absalón—, y su padre, anota el narrador, jamás le había preguntado por qué hacía nada. Luego un profeta instruye a una reina sobre qué decir, y ella lo dice mejor de lo que él lo escribió, y le recuerda al rey moribundo un juramento del que el lector nunca ha oído hablar. Salomón es ungido en el manantial de la ciudad mientras el banquete rival se celebra sin testigos valle abajo — y el primer acto del vencedor como rey es perdonar a su hermano, con una condición.",
    "2kgs1": "Un libro que empieza a mitad de la esquela de otro: Reyes es un solo rollo en hebreo, y el corte griego cayó en mitad de un reinado. Un rey cae por la celosía del tejado y, herido, manda consultar a Baal-zebub de Ecrón si vivirá; a sus mensajeros los intercepta un Mensajero, y la pregunta que traen de vuelta se hace tres veces, palabra por palabra: ¿acaso no hay Dios en Israel? Luego suben tres compañías de cincuenta a buscar a un profeta, y dos arden en la ladera — un pasaje al que el propio Nuevo Testamento pone objeción cuando dos discípulos proponen repetirlo y son reprendidos. Al hombre del manto de pelo y el cinturón de cuero lo describirán otra vez, ocho siglos después, de pie en un río.",
    "1chr1": "La compresión más extrema de la Biblia. Abre con una palabra y sin verbo —«Adán»— y da nueve nombres donde Génesis 5 daba treinta y dos versículos de edades y muertes. Cincuenta y cuatro versículos llevan a la raza humana entera de la creación a los reyes de Edom, y en todo ello exactamente UN hombre recibe un verbo. Obsérvese qué conserva el compilador y qué suprime: «Abram — él es Abraham» son cuatro palabras para el llamado, el pacto, Sodoma, Isaac y Moriah; los hijos de Isaac son «Esaú e ISRAEL», y el nombre Jacob no aparece ni una vez. Y al final, en una lista de reyes edomitas copiada del Génesis, se puede ver un texto siendo copiado a mano y qué letras confunde un escriba cansado.",
    "2chr1": "El reinado de Salomón empieza en la frase con que terminó 1 Reyes 2 — y los dos capítulos de golpe de Estado, lista en el lecho de muerte y ejecuciones que lo llevaron allí sencillamente no se cuentan. Luego Gabaón, donde Crónicas aporta la explicación que Reyes nunca da para un rey que sacrifica en un lugar alto: allí estaba la tienda de reunión que hizo Moisés, con el altar de bronce de Bezaleel delante. Dios se aparece esa noche y Salomón pide «sabiduría y CONOCIMIENTO» — donde 1 Reyes le hace pedir un corazón que oiga para discernir entre lo bueno y lo malo: la misma noche contada dos veces. Y cuatro versículos después del don, el capítulo registra que juntó carros e importó caballos de Egipto: las dos cosas que el Deuteronomio prohíbe a un rey por su nombre, anotadas sin una palabra de comentario. ⚠ Dieciocho versículos en hebreo; las Biblias castellanas imprimen el último como 2:1.",
    "ezra1": "El libro abre con la frase en que TERMINA la Biblia hebrea. Crónicas cierra el canon judío a mitad del decreto —«que suba»— y Esdras cita las mismas palabras y las termina. El rescripto de un emperador persa se introduce con la fórmula propia de los profetas, «así dice Ciro»; el mismo verbo que despierta a un emperador despierta a unas docenas de cabezas de familia; y los que se quedan entregan plata y oro a los que se van, que es lo que ocurrió la última vez que Israel salió de un país extranjero. Luego los utensilios del templo que Nabucodonosor guardó en el tesoro de su dios son contados de vuelta por un tesorero persa — y el inventario no cuadra.",
    "neh1": "«Palabras de Nehemías hijo de Hacalías»: ningún otro libro de la Biblia hebrea abre con el nombre propio de un hombre y sigue después en primera persona. Está en el palacio de invierno persa, en Susa, cuando unos hombres de Judá traen la noticia de que Jerusalén sigue abierta y en oprobio; y se sienta y llora y hace duelo por días, y luego ora durante cuatro meses. La oración está hecha casi por entero de citas del Deuteronomio —no está componiendo, está exigiendo a Dios el cumplimiento de un documento— y termina pidiendo misericordia «delante de este hombre», que resulta ser el ser humano más poderoso vivo. Y entonces las últimas cinco palabras del capítulo lo explican todo: yo era copero del rey.",
    "est1": "El único libro de la Biblia que nunca menciona a Dios abre con ciento ochenta días de un rey enseñando su dinero. Asuero es JERJES, y el año es el 483 a.C. — el mismo en que Heródoto lo tiene reuniendo a sus nobles para planear la invasión de Grecia, una guerra que este libro no menciona jamás y cuya duración es exactamente el hueco entre los capítulos 1 y 2. Entonces, el séptimo día del segundo banquete, bebido, manda traer a su mujer para exhibirla junto con el mobiliario, y ella se niega — y el hebreo no da razón alguna. Lo que sigue es una comedia a costa de unos funcionarios asustados: todo el aparato jurídico de un imperio convocado por un desaire de sobremesa, y un decreto llevado por el correo imperial a ciento veintisiete provincias anunciando que los hombres manden en casa.",
}

NEXT_UP = "Genesis 24"         # (legacy; nav is now book-scoped in nav_strip)
TOTAL_BIBLE_CHAPTERS = 1189

BOOKS_OT = [("Genesis", 50), ("Exodus", 40), ("Leviticus", 27), ("Numbers", 36),
    ("Deuteronomy", 34), ("Joshua", 24), ("Judges", 21), ("Ruth", 4),
    ("1 Samuel", 31), ("2 Samuel", 24), ("1 Kings", 22), ("2 Kings", 25),
    ("1 Chronicles", 29), ("2 Chronicles", 36), ("Ezra", 10), ("Nehemiah", 13),
    ("Esther", 10), ("Job", 42), ("Psalms", 150), ("Proverbs", 31),
    ("Ecclesiastes", 12), ("Song of Solomon", 8), ("Isaiah", 66),
    ("Jeremiah", 52), ("Lamentations", 5), ("Ezekiel", 48), ("Daniel", 12),
    ("Hosea", 14), ("Joel", 3), ("Amos", 9), ("Obadiah", 1), ("Jonah", 4),
    ("Micah", 7), ("Nahum", 3), ("Habakkuk", 3), ("Zephaniah", 3),
    ("Haggai", 2), ("Zechariah", 14), ("Malachi", 4)]
BOOKS_NT = [("Matthew", 28), ("Mark", 16), ("Luke", 24), ("John", 21),
    ("Acts", 28), ("Romans", 16), ("1 Corinthians", 16), ("2 Corinthians", 13),
    ("Galatians", 6), ("Ephesians", 6), ("Philippians", 4), ("Colossians", 4),
    ("1 Thessalonians", 5), ("2 Thessalonians", 3), ("1 Timothy", 6),
    ("2 Timothy", 4), ("Titus", 3), ("Philemon", 1), ("Hebrews", 13),
    ("James", 5), ("1 Peter", 5), ("2 Peter", 3), ("1 John", 5), ("2 John", 1),
    ("3 John", 1), ("Jude", 1), ("Revelation", 22)]

# --- book-aware helpers (multi-book support) -------------------------------
# The site began Genesis-only; these let a second book (John, …) coexist without
# breaking the live genesis-N.html URLs. A library ref is (ch, v) for Genesis
# (back-compat) or (book, ch, v) for any book; `_ref` normalizes to (book, ch, v).
BOOK_TOTAL = {name: n for name, n in BOOKS_OT + BOOKS_NT}
_NT_BOOKS = {name for name, _ in BOOKS_NT}
_BOOK_ABBR = {"Genesis": "Gen", "Exodus": "Exod", "Leviticus": "Lev", "Numbers": "Num",
              "Deuteronomy": "Deut", "Jeremiah": "Jer", "Proverbs": "Prov", "Daniel": "Dan", "Matthew": "Matt", "Mark": "Mark",
              "Luke": "Luke", "John": "John", "Acts": "Acts", "Romans": "Rom",
              "Revelation": "Rev"}


def book_slug(book):
    """URL slug for a book: 'Genesis' -> 'genesis', '1 John' -> '1-john'."""
    return book.lower().replace(" ", "-")


def chapter_filename(book, ch):
    return f"{book_slug(book)}-{ch}.html"


def book_abbr(book):
    return _BOOK_ABBR.get(book, book)


def _is_nt(book):
    return book in _NT_BOOKS


def _ref(r):
    """Normalize a library ref: (ch, v) -> Genesis; (book, ch, v) -> that book."""
    return (r[0], r[1], r[2]) if len(r) == 3 else ("Genesis", r[0], r[1])


# Normalize library-data refs to (book, ch, v) once, at load, so every consumer
# below unpacks a uniform triple. Genesis entries keep their bare (ch, v) tuples
# in library_data.py and normalize here to book="Genesis".
for _e in ENCYCLOPEDIA:
    _e["refs"] = [_ref(r) for r in _e["refs"]]
XREFS_N = [(_ref(a), _ref(b), why) for (a, b, why) in XREFS]


FAVICON = ("data:image/svg+xml," + html.escape(
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 46 46'>"
    "<circle cx='23' cy='23' r='22.5' fill='#0b1929'/>"
    "<rect x='9' y='12' width='3.6' height='22' rx='1.8' fill='#3b2d5e' stroke='#e8c968' stroke-width='0.6'/>"
    "<rect x='33.4' y='12' width='3.6' height='22' rx='1.8' fill='#3b2d5e' stroke='#e8c968' stroke-width='0.6'/>"
    "<rect x='12.6' y='14.5' width='20.8' height='17' fill='#efe6cf'/>"
    "<path d='M28 30 l5 -5 1.4 1.4 -5 5 -2 0.6 z' fill='#e8c968'/></svg>", quote=True))

SCROLL_SVG = """<svg class="mtlib-icon" viewBox="0 0 46 46" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <circle cx="23" cy="23" r="22.5" fill="#0b1929"/>
  <circle cx="23" cy="23" r="22.5" fill="none" stroke="#e8c968" stroke-width="0.7" opacity="0.4"/>
  <rect x="9" y="12" width="3.6" height="22" rx="1.8" fill="#3b2d5e" stroke="#e8c968" stroke-width="0.6"/>
  <rect x="33.4" y="12" width="3.6" height="22" rx="1.8" fill="#3b2d5e" stroke="#e8c968" stroke-width="0.6"/>
  <rect x="12.6" y="14.5" width="20.8" height="17" fill="#efe6cf"/>
  <g stroke="#8a7ab0" stroke-width="1.1" stroke-linecap="round">
    <line x1="15.5" y1="19" x2="30.5" y2="19"/>
    <line x1="15.5" y1="23" x2="30.5" y2="23"/>
    <line x1="15.5" y1="27" x2="26.5" y2="27"/>
  </g>
  <path d="M28 30 l5 -5 1.4 1.4 -5 5 -2 0.6 z" fill="#e8c968"/>
</svg>"""


def header(active="", lang="en"):
    def cls(k):
        return ' class="on"' if k == active else ""
    if lang == "es":
        # Spanish locale header. The nav links ONLY to pages that exist in Spanish
        # (so a Spanish-only reader is never dumped into English); it grows as the
        # Spanish edition is built out. The 🌐 switch jumps to the English home.
        return f"""<header class="site-head">
  <div class="utilnav">
    <a class="util-ask" href="contact.es.html" title="Enviar una pregunta">✉️ Preguntar</a>
    <details class="langsel">
      <summary title="Idioma">\U0001F310 Español</summary>
      <div class="langlist">
        <a href="index.html">English</a>
        <a href="es.html" class="cur">Español</a>
      </div>
    </details>
  </div>
  <a class="brand" href="es.html">
    {SCROLL_SVG}
    <span class="brand-name">La Traducción <span class="lib">Mister</span></span>
  </a>
  <div class="rule"></div>
  <div class="tag">Una nueva traducción de la Biblia desde el hebreo y el griego</div>
  <nav class="topnav">
    <a href="es.html"{cls('home')}>Inicio</a>
  </nav>
</header>"""
    return f"""<header class="site-head">
  <div class="utilnav">
    <a class="util-ask" href="contact.html" title="Ask a question">✉️ Ask a Question</a>
    <details class="langsel">
      <summary title="Language">\U0001F310 English</summary>
      <div class="langlist">
        <a href="index.html" class="cur">English</a>
        <a href="es.html">Español</a>
      </div>
    </details>
  </div>
  <a class="brand" href="index.html">
    {SCROLL_SVG}
    <span class="brand-name">The Mister<span class="lib">Librarian</span> Bible Project</span>
  </a>
  <div class="rule"></div>
  <div class="tag">{TAGLINE}</div>
  <nav class="topnav">
    <a href="index.html"{cls('home')}>Home</a>
    <a href="toc.html"{cls('toc')}>Table of Contents</a>
    <a href="reading.html"{cls('reading')}>📗 My Reading</a>
    <a href="library.html"{cls('library')}>📚 Library</a>
    <a href="chronology.html"{cls('chronology')}>🕰 Chronology</a>
    <a href="ask.html"{cls('ask')}>Ask Mr. Librarian</a>
    <a href="about.html"{cls('about')}>About</a>
  </nav>
</header>"""


FOOTER = """<footer class="site-foot">
  <p>The MisterLibrarian Bible Project — a fresh translation of the Bible into modern English, made from
  the original Hebrew and Greek (the Masoretic Text and the critical Greek text) one chapter at a time,
  with translator's notes comparing every choice against seven landmark versions. Kept by Mr. Librarian;
  translated with Claude.</p>
  <p><a href="toc.html">Table of Contents</a> · <a href="reading.html">My Reading</a> · <a href="library.html">Library</a> · <a href="chronology.html">Chronology</a> · <a href="contact.html">Ask Mr. Librarian a question</a> · <a href="about.html">About the project</a></p>
</footer>"""

# Spanish-locale footer — links only to what exists in Spanish, so a Spanish-only
# reader is never dropped into English. Grows as the Spanish edition is built out.
ES_FOOTER = """<footer class="site-foot">
  <p>La Traducción Mister — una nueva traducción de la Biblia al español, hecha desde el hebreo y el griego
  originales (el Texto Masorético y el texto crítico griego), capítulo por capítulo, con notas del traductor
  que comparan cada decisión con la Reina-Valera y otras versiones. Cuidada por Mr. Librarian; traducida con
  Claude. Esta edición está creciendo capítulo por capítulo.</p>
  <p><a href="es.html">Inicio</a> · <a href="index.html">English edition</a></p>
</footer>"""


def _goatcounter_script():
    """Sitewide, cookie-less visit tracking (GoatCounter) injected into every page's <head>.
    No-op until GOATCOUNTER_CODE is set above."""
    if not GOATCOUNTER_CODE:
        return ""
    return (f'\n<script data-goatcounter="https://{GOATCOUNTER_CODE}.goatcounter.com/count" '
            f'async src="//gc.zgo.at/count.js"></script>')


def _stats_box():
    """Live 'Site Traffic' box for the About page — fetches GoatCounter's public,
    unauthenticated site-wide TOTAL counter JSON and renders it client-side (no iframe,
    no GoatCounter branding). NB: GoatCounter's counter endpoints return HTTP 404 for a
    thin/zero-data path even though the JSON body is still valid — so this deliberately
    parses the body regardless of status code, and only hides the box if the fetch itself
    fails outright (network error, ad-blocker, or not yet configured) or the body is
    unparseable. Learned the hard way: an earlier version checked response.ok first, which
    made the box silently vanish on every load."""
    if not GOATCOUNTER_CODE:
        return ""
    return f"""<div class="panel statsbox" id="statsbox">
  <div class="stats-label">\U0001F4CA Site Traffic</div>
  <div class="stats-num" id="statsNum">\u2014</div>
  <div class="stats-sub">site visits, all-time \u00b7 tracked anonymously via
  <a href="https://www.goatcounter.com" rel="noopener">GoatCounter</a> \u2014 no cookies, no personal
  data, nothing sold</div>
</div>
<script>
(function(){{
  fetch("https://{GOATCOUNTER_CODE}.goatcounter.com/counter/TOTAL.json")
    .then(function(r){{ return r.json(); }})
    .then(function(d){{
      var el = document.getElementById("statsNum");
      if (el && d && d.count) el.textContent = d.count;
      else {{ var b = document.getElementById("statsbox"); if (b) b.style.display = "none"; }}
    }})
    .catch(function(){{
      var b = document.getElementById("statsbox");
      if (b) b.style.display = "none";
    }});
}})();
</script>"""


def _og_tags(title, desc, url="", image=""):
    """Open Graph + Twitter-card meta so a shared link unfurls with a title,
    description and image. canonical + og:url are emitted ONLY when the page's
    own url is given — a wrong canonical (defaulting to the homepage) is worse
    for SEO than none, so pages that don't pass a url simply omit it."""
    img = image or OG_IMAGE
    d = desc or ("A fresh translation of the Bible from the Hebrew and Greek, "
                 "verse by verse.")
    t = html.escape(title, quote=True)
    de = html.escape(d, quote=True)
    tags = [
        f'<meta property="og:site_name" content="Mister Translation"/>',
        f'<meta property="og:type" content="{"article" if url else "website"}"/>',
        f'<meta property="og:title" content="{t}"/>',
        f'<meta property="og:description" content="{de}"/>',
        f'<meta property="og:image" content="{img}"/>',
        f'<meta name="twitter:card" content="summary_large_image"/>',
        f'<meta name="twitter:title" content="{t}"/>',
        f'<meta name="twitter:description" content="{de}"/>',
        f'<meta name="twitter:image" content="{img}"/>',
    ]
    if url:
        full = f"{SITE_URL}/{url}"
        tags.insert(0, f'<link rel="canonical" href="{full}"/>')
        tags.append(f'<meta property="og:url" content="{full}"/>')
    return "\n" + "\n".join(tags)


def page(title, body, active="", desc="", url="", image="", lang="en"):
    d = f'\n<meta name="description" content="{html.escape(desc, quote=True)}"/>' if desc else ""
    og = _og_tags(title, desc, url, image)
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>{d}{og}
<link rel="icon" href="{FAVICON}"/>
<link rel="stylesheet" href="style.css?v={CSS_VER}"/>{_goatcounter_script()}
</head>
<body>
<div class="wrap">
{header(active, lang)}
<script src="reading.js"></script>
<script src="player-clips.js?v={JS_VER}"></script>
<script src="audio-reader.js?v={AUDIO_JS_VER}"></script>
<script src="reader-notes.js?v={NOTES_JS_VER}" defer></script>
<script src="https://www.youtube.com/iframe_api"></script>
{body}
{ES_FOOTER if lang == "es" else FOOTER}
</div>
</body>
</html>
"""


# Chapter slugs in SOURCE-FILE order. New panels are appended, so this is publish
# order — which is what the homepage "Newest" surfaces need. CHAPTERS itself is kept
# in CANONICAL order (for book-scoped chapter nav), so its tail is the canonically-
# last chapter, NOT the most recently shipped one. Set by extract_source.
PUBLISH_ORDER = []


def extract_source(source_path):
    src = open(source_path, encoding="utf-8").read()
    global PUBLISH_ORDER
    PUBLISH_ORDER = re.findall(
        r'<div class="chapter-panel[^"]*" id="chapter-([a-z0-9]+)">', src)
    chapters = {}
    for slug, _, _, _ in CHAPTERS:
        m = re.search(
            r'<div class="chapter-panel[^"]*" id="chapter-%s">(.*?)</div><!-- /chapter-%s -->'
            % (slug, slug), src, re.S)
        if not m:
            raise SystemExit(f"chapter panel {slug} not found in source")
        chapters[slug] = m.group(1).strip()
    return chapters


def clean_chapter(content):
    # In-page chapter-switch links (showChapter) -> real chapter-page links; the nav strip covers movement.
    slug_to_file = {slug: chapter_filename(book, num) for slug, book, num, _ in CHAPTERS}
    content = re.sub(
        r'<a href="#" onclick="showChapter\(\'([a-z0-9]+)\'[^"]*"[^>]*>([^<]+)</a>',
        lambda m: f'<a href="{slug_to_file.get(m.group(1), "toc.html")}">{m.group(2)}</a>', content)
    return content


# ---------------------------------------------------------------- library ---

def verse_anchor(ch, v):
    """Anchor id used in the source markup: chapter 1 is bare vN, others vCH-N."""
    return f"v{v}" if ch == 1 else f"v{ch}-{v}"


def verse_url(book, ch, v):
    return f"{chapter_filename(book, ch)}#{verse_anchor(ch, v)}"


# Which chapters actually have a page built. Library entries (encyclopedia,
# dictionary, atlas) legitimately cite verses from chapters we have not
# translated yet — a place's refs list is about the PLACE, not about our
# publication schedule — so those citations must render as plain text rather
# than as links to a 404. Adding a chapter to CHAPTERS turns every pending
# citation of it into a live link automatically, with no data to go back and
# edit. The site-wide dead-link check is what caught this: Goshen cites
# Gen 46-47 and Exod 8-9, none of which exist yet.
PUBLISHED_CHAPTERS = {(book, num) for _slug, book, num, _teaser in CHAPTERS}


def chapter_published(book, ch):
    return (book, ch) in PUBLISHED_CHAPTERS


def ref_link(book, ch, v, label=None):
    """A verse citation: a link if that chapter is published, plain text if not."""
    label = label or f"{book_abbr(book)} {ch}:{v}"
    if not chapter_published(book, ch):
        return f'<span class="ref-unpub" title="not translated yet">{label}</span>'
    return f'<a href="{verse_url(book, ch, v)}">{label}</a>'


_YT_ID_RE = re.compile(r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})")

# YouTube video IDs whose owner has DISABLED embedding on third-party sites
# (an iframe just renders a dead "Video unavailable — Watch on YouTube" box).
# Verified via the oEmbed endpoint: an embeddable video returns HTTP 200, a
# non-embeddable one returns HTTP 401. For these we render a nice clickable
# thumbnail card that links out to YouTube instead of a broken embed. To add
# one: check `https://www.youtube.com/oembed?url=<watch-url>&format=json` — if
# it 401s, drop the 11-char id in here.
NOEMBED_IDS = {
    "8cqBePFD9S4",   # Expedition Bible — "BETHEL: Where Jacob Met God" (embedding disabled)
    "WzunDBINbS4",   # Expedition Bible — "MAMRE — Where God Appeared to Abraham!" (embedding disabled)
}


def youtube_embed(url, title):
    """A responsive, privacy-enhanced YouTube embed (falls back to a plain link
    if the id can't be parsed, or a clickable thumbnail card if the video has
    embedding disabled — see NOEMBED_IDS)."""
    m = _YT_ID_RE.search(url)
    if not m:
        return f'<p><a href="{html.escape(url, quote=True)}" rel="noopener">▶ {html.escape(title)}</a></p>'
    vid = m.group(1)
    if vid in NOEMBED_IDS:
        watch = f"https://www.youtube.com/watch?v={vid}"
        thumb = f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg"
        return f"""<div class="vembed">
  <a class="vlink-frame" href="{watch}" target="_blank" rel="noopener"
     title="{html.escape(title, quote=True)} — watch on YouTube"
     style="background-image:url('{thumb}')">
    <span class="vlink-play" aria-hidden="true">▶</span>
    <span class="vlink-badge">Watch on YouTube ↗</span>
  </a>
  <div class="vembed-title">{html.escape(title)} <span class="vlink-note">(plays on YouTube — this film has embedding turned off)</span></div>
</div>"""
    return f"""<div class="vembed">
  <div class="vembed-frame">
    <iframe src="https://www.youtube-nocookie.com/embed/{vid}"
      title="{html.escape(title, quote=True)}" loading="lazy"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
  </div>
  <div class="vembed-title">{html.escape(title)}</div>
</div>"""


def _atlas_zoom(span):
    """Rough OSM zoom level for a "view larger map" link, derived from the bbox span
    in degrees (a tight excavated-site span -> high zoom; a broad region -> low)."""
    z = round(9 - math.log2(max(span, 0.02)))
    return max(3, min(17, z))


def osm_embed(lat, lon, span, label, caption=None):
    """A key-less, officially-supported OpenStreetMap embed (no Google API/billing
    needed for a static site) centered on (lat, lon), with a bbox span_degrees wide.

    `caption` (already-escaped HTML) renders directly under the map frame, above the
    "view larger" link — the readable-English fix for OSM's Middle East labels, which
    are mostly Arabic-script only with no `name:en` fallback for anything but a
    handful of major cities."""
    half = span / 2.0
    bbox = f"{lon - half:.4f},{lat - half:.4f},{lon + half:.4f},{lat + half:.4f}"
    marker = f"{lat:.4f},{lon:.4f}"
    zoom = _atlas_zoom(span)
    view_url = f"https://www.openstreetmap.org/?mlat={lat:.4f}&mlon={lon:.4f}#map={zoom}/{lat:.4f}/{lon:.4f}"
    cap_html = f'<div class="atlas-caption">{caption}</div>' if caption else ""
    return f"""<div class="mapembed">
  <div class="mapembed-frame">
    <iframe src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik&marker={marker}"
      title="{html.escape(label, quote=True)}" loading="lazy"></iframe>
  </div>
  {cap_html}
  <div class="mapembed-link"><a href="{view_url}" rel="noopener">View larger map on OpenStreetMap →</a></div>
</div>"""


def _build_alias_index():
    """alias word/phrase -> [entry, ...] candidate encyclopedia entries."""
    index = defaultdict(list)
    for e in ENCYCLOPEDIA:
        for alias in e.get("aliases", [e["name"]]):
            index[alias].append(e)
    return index


_ALIAS_INDEX = _build_alias_index()
_ALIAS_PATTERN = re.compile(
    r'\b(' + '|'.join(re.escape(w) for w in
                       sorted(_ALIAS_INDEX, key=len, reverse=True)) + r')\b')
def _norm_override(o):
    # (ch, v, word, idx, slug) -> Genesis; (book, ch, v, word, idx, slug) -> that book.
    if len(o) == 6:
        b, ch, v, w, i, s = o
        return (b, ch, v, w, i), s
    ch, v, w, i, s = o
    return ("Genesis", ch, v, w, i), s


_OVERRIDE_MAP = dict(_norm_override(o) for o in LINK_OVERRIDES)
_SLUG_TO_ENTRY = {e["slug"]: e for e in ENCYCLOPEDIA}
_REGION_BY_SLUG = {r["slug"]: r for r in REGIONS}
_VERSE_ENG_BLOCK = re.compile(
    r'(id="(v(?:\d+-)?\d+)"[^>]*>.*?<div class="eng">)(.*?)(</div>)', re.S)


def inject_encyclopedia_links(content, book, ch):
    """Turn the first mention per chapter of each ENCYCLOPEDIA entry (by its
    `name` or any `aliases`) into a link to its encyclopedia.html entry.

    Only ENCYCLOPEDIA entries are linked, never DICTIONARY terms (those are
    Hebrew concept-words whose English rendering varies verse to verse, so a
    literal-string match on them would be unreliable). Resolution order for
    a matched word: (1) an explicit LINK_OVERRIDES pin for this exact
    (chapter, verse, word, occurrence-within-verse); (2) if only one entry
    claims that word at all, use it; (3) if several entries share the word
    (e.g. "Haran" the man and "Haran" the city), prefer whichever one's own
    `refs` list already includes this verse. Anything still unresolved is
    left as plain text rather than guessed at. Each entry links only once
    per chapter — later mentions in the same chapter stay plain, so the
    first sighting of "Eden" carries the link and the page isn't peppered
    with repeats of the same one.
    """
    linked_slugs = set()

    def verse_block(m):
        prefix, vid, eng_html, suffix = m.group(1), m.group(2), m.group(3), m.group(4)
        vnum = int(vid.rsplit("-", 1)[-1] if "-" in vid else vid[1:])
        seen_in_verse = defaultdict(int)

        def word_match(wm):
            word = wm.group(1)
            seen_in_verse[word] += 1
            occurrence = seen_in_verse[word]
            # Only entities that actually appear in THIS book are eligible, so a
            # Genesis entry can never link inside John (or vice versa).
            candidates = [c for c in _ALIAS_INDEX[word]
                          if any(rb == book for (rb, rc, rv) in c["refs"])]
            slug = _OVERRIDE_MAP.get((book, ch, vnum, word, occurrence))
            # An explicit human pin is an instruction, so it BEATS the
            # once-per-chapter cap below. Without this a territory named twenty
            # times in one chapter links only at its first, incidental mention
            # (Edom linked at 36:1, "that is, Edom") and the verse that actually
            # describes the land — 36:8, "Esau dwelt in the hill country of
            # Seir" — got no map link at all. The cap still governs everything
            # unpinned, so ordinary names are never peppered with repeats.
            pinned = slug is not None
            if slug is None:
                if len(candidates) == 1:
                    slug = candidates[0]["slug"]
                else:
                    ref_hits = [c["slug"] for c in candidates if (book, ch, vnum) in c["refs"]]
                    slug = ref_hits[0] if len(ref_hits) == 1 else None
            if slug is None or (slug in linked_slugs and not pinned):
                return word
            linked_slugs.add(slug)
            name = html.escape(_SLUG_TO_ENTRY[slug]["name"], quote=True)
            return (f'<a class="eterm" href="encyclopedia.html#{slug}" '
                    f'title="{name} — see the Encyclopedia">{word}</a>')

        return prefix + _ALIAS_PATTERN.sub(word_match, eng_html) + suffix

    return _VERSE_ENG_BLOCK.sub(verse_block, content)


def inject_xrefs(content, book, ch):
    """Append ⤷ cross-reference chips inside each verse block this (book, ch) owns.
    Same-book targets show a bare `12:2` chip (unchanged from the Genesis-only era);
    cross-book targets show a `Gen 1:1` / `John 1:1` chip so the link is unambiguous."""
    by_verse = defaultdict(list)   # verse in THIS chapter -> [((tbook, tch, tv), why), ...]
    for (ab, ac, av), (bb, bc, bv), why in XREFS_N:
        if ab == book and ac == ch:
            by_verse[av].append(((bb, bc, bv), why))
        if bb == book and bc == ch:
            by_verse[bv].append(((ab, ac, av), why))
    for v, links in sorted(by_verse.items()):
        anchor = verse_anchor(ch, v)
        marker = f'id="{anchor}"'
        i = content.find(marker)
        if i < 0:
            continue
        # the verse block closes with the first '</div></div>' after its id
        j = content.find("</div></div>", i)
        if j < 0:
            continue
        chips = ""
        for (tb, tc, tv), why in links:
            # A chip is nothing but a jump target, so an unpublished chapter gets
            # skipped outright rather than rendered as plain text (which is right
            # for an encyclopedia citation but useless here). XREFS may legitimately
            # point forward — the payoff of an echo often lands chapters ahead of
            # where it was planted — and the chip appears by itself once that
            # chapter ships. Nothing to remember, nothing to go back and edit.
            if not chapter_published(tb, tc):
                continue
            lbl = f"{tc}:{tv}" if tb == book else f"{book_abbr(tb)} {tc}:{tv}"
            chips += (f'<a class="xref" href="{verse_url(tb, tc, tv)}" '
                      f'title="{html.escape(why, quote=True)}">⤷ {lbl}</a>')
        if not chips:
            continue
        block = f'<div class="xrefs"><span class="xr-label">cross-refs</span>{chips}</div>'
        content = content[:j] + block + content[j:]
    return content


# A video clip is authored right AFTER the verse it belongs to
# (<div class="vclip"> immediately following the verse's closing </div>). Left
# there it renders BELOW that verse's divider line, so a reader mistakes it for
# the next verse's clip. This pulls each clip INSIDE the verse it follows — just
# before the verse-closing </div>, after any cross-ref chips — so it sits above
# the divider and clearly belongs to the verse above it. Runs for every chapter,
# so clips can keep being authored the simple way.
_CLIP_INTO_VERSE = re.compile(r'</div>\s*(<div class="vclip"[^>]*></div>)')


def move_clips_into_verses(content):
    return _CLIP_INTO_VERSE.sub(lambda m: m.group(1) + "</div>", content)


_FILMCLIP_RE = re.compile(r'<div class="filmclip"([^>]*)></div>')


def _clip_attr(attrs, name):
    m = re.search(r'%s="([^"]*)"' % re.escape(name), attrs)
    return m.group(1) if m else ""


def render_film_clips(content):
    """Turn a <div class="filmclip" data-video=ID data-title=.. data-source=..> marker
    (authored at the very bottom of a chapter panel, after the notes/info-block) into a
    labeled 'Companion film' block. These are DRAMATIZATIONS — feature films, not the
    on-site archaeology footage embedded on the encyclopedia's place entries — so they
    are kept visually and editorially distinct, and honestly labeled as such. Not touched
    by move_clips_into_verses (that only matches class="vclip")."""
    def repl(m):
        attrs = m.group(1)
        vid = _clip_attr(attrs, "data-video")
        title = _clip_attr(attrs, "data-title") or "Companion film"
        source = _clip_attr(attrs, "data-source")
        embed = youtube_embed(f"https://youtu.be/{vid}", title)
        src_html = f" — <em>{html.escape(source)}</em>" if source else ""
        return f"""<div class="filmshelf">
  <div class="filmshelf-head">\U0001F3AC Companion film · a dramatization</div>
  <p class="filmshelf-note">A dramatized retelling{src_html}, offered alongside the chapter as a companion.
  It is a <strong>film, not archaeology</strong> — an interpretation of the story, kept separate from the
  on-site footage on the site's place entries. (Embedded from a third-party upload; it may move or disappear.)</p>
  {embed}
</div>"""
    return _FILMCLIP_RE.sub(repl, content)


_STOPWORDS = set("""
a an and are as at be but by for from he her him his i in into is it its let me my not of on or our
so that the their them then there they this to was we were will with you your all any because if
when who whom whose what which shall may your yours out up down over under after before again very
came come go went said says do did done had has have how than too these those upon them one two
""".split())


def extract_verses_english(chapters):
    """Return [(book, ch, v, plain_english_text), ...] for every verse in every chapter."""
    rows = []
    for slug, book, num, _ in CHAPTERS:
        content = chapters[slug]
        for m in re.finditer(
                r'id="(v(?:\d+-)?\d+)".*?<div class="eng">(.*?)</div>', content, re.S):
            anchor, eng = m.group(1), m.group(2)
            vnum = int(anchor.rsplit("-", 1)[-1] if "-" in anchor else anchor[1:])
            text = re.sub(r"<[^>]+>", " ", eng)
            text = html.unescape(text)
            text = re.sub(r"\s*note\s*$", "", text.strip())
            text = re.sub(r"\s+", " ", text)
            rows.append((book, num, vnum, text))
    return rows


def build_concordance(chapters):
    rows = extract_verses_english(chapters)
    index = defaultdict(list)          # word -> [(book, ch, v), ...]
    for book, ch, v, text in rows:
        seen = set()
        for raw in re.findall(r"[A-Za-z][A-Za-z'’\-]*", text):
            w = raw.lower().strip("'’-")
            if len(w) < 3 or w in _STOPWORDS or w in seen:
                continue
            seen.add(w)
            index[w].append((book, ch, v))
    words = sorted(index.keys())
    total_refs = sum(len(vs) for vs in index.values())

    letters = sorted({w[0].upper() for w in words})
    jump = " ".join(f'<a href="#L{L}">{L}</a>' for L in letters)
    sections = []
    cur = None
    for w in words:
        L = w[0].upper()
        if L != cur:
            if cur is not None:
                sections.append("</div>")
            sections.append(f'<h2 id="L{L}">{L}</h2><div class="panel conc">')
            cur = L
        refs = index[w]
        links = " ".join(
            ref_link(b, c, v) for b, c, v in refs)
        sections.append(
            f'<div class="cw"><span class="cw-w">{html.escape(w)}</span>'
            f'<span class="cw-n">×{len(refs)}</span>'
            f'<span class="cw-refs">{links}</span></div>')
    if cur is not None:
        sections.append("</div>")

    body = f"""<h1 class="pagetitle">🔠 Concordance</h1>
<p class="lede">Every significant English word in the translation so far, with every verse it appears in —
<strong>{len(words)} words, {total_refs} occurrences, generated automatically from the translation text
itself</strong> each time a chapter is added (common function words are skipped). Because it indexes THIS
translation, it reflects this project's actual renderings: look up <em>vault</em>, not <em>firmament</em>.</p>
<p class="lede jump">Jump to: {jump}</p>
{''.join(sections)}"""
    out = page(f"Concordance — {SITE_NAME}", body, active="library",
               desc="Auto-generated concordance of the MisterLibrarian translation — every significant "
                    "word, every verse, rebuilt as each chapter is added.")
    open(os.path.join(OUT, "concordance.html"), "w", encoding="utf-8").write(out)
    return len(words), total_refs


def build_dictionary():
    entries = sorted(DICTIONARY, key=lambda e: e[1].lower())
    items = []
    for slug, term, orig, translit, gloss, ref in entries:
        book, ch, v = _ref(ref)
        script_cls = "dgreek" if _is_nt(book) else "dheb"   # Greek renders LTR, Hebrew RTL
        items.append(f"""<div class="dentry" id="{slug}">
  <div class="dhead"><span class="dterm">{html.escape(term)}</span>
    <span class="{script_cls}">{orig}</span> <span class="dtr">{html.escape(translit)}</span></div>
  <p>{gloss} <a class="dref" href="{verse_url(book, ch, v)}">→ first discussed at {book_abbr(book)} {ch}:{v}</a></p>
</div>""")
    body = f"""<h1 class="pagetitle">📖 Dictionary</h1>
<p class="lede">The original-language words this translation has met so far — Hebrew for the Tanakh, Greek for
the New Testament — <strong>{len(entries)} terms</strong>, each added the chapter its translator's note first
discussed it, with a link back to that discussion. This is a reader's glossary of the actual working
vocabulary, not an abridged lexicon.</p>
<div class="panel dict">
{''.join(items)}
</div>"""
    out = page(f"Dictionary — {SITE_NAME}", body, active="library",
               desc="A growing dictionary of the Hebrew terms behind the MisterLibrarian translation, "
                    "added chapter by chapter.")
    open(os.path.join(OUT, "dictionary.html"), "w", encoding="utf-8").write(out)
    return len(entries)


def build_encyclopedia():
    places = [e for e in ENCYCLOPEDIA if e["kind"] == "place"]
    people = [e for e in ENCYCLOPEDIA if e["kind"] in ("person", "people")]

    def render(entries):
        out = []
        for e in sorted(entries, key=lambda x: x["name"].lower()):
            refs = " ".join(ref_link(b, c, v) for b, c, v in e["refs"])
            if e.get("videos"):
                vids = "".join(youtube_embed(u, t) for t, u in e["videos"])
            else:
                vids = ('<div class="evids-empty">▶ No films on the shelf yet — archaeology and '
                        'geography videos get added here as Mr. Librarian finds good ones.</div>')
            # A mapped place gets a direct route to its map. Without this the
            # only way from an entry to the atlas was the chapter-level toggle,
            # so a reader who clicked "Seir" in the verse landed on prose with
            # no way to see where the territory actually was.
            maplink = ""
            if e.get("coords"):
                is_region = e["slug"] in _REGION_BY_SLUG
                label = "🗺️ See the territory boundary" if is_region else "🗺️ See it on the atlas"
                maplink = (f'<div class="emap"><a href="atlas.html#atlas-{e["slug"]}">{label} →</a></div>')
            out.append(f"""<div class="eentry" id="{e['slug']}">
  <div class="ehead">{html.escape(e['name'])}</div>
  <p>{e['desc']}</p>
  <div class="erefs"><span class="xr-label">in the text</span> {refs}</div>
  {maplink}
  {vids}
</div>""")
        return "".join(out)

    queue_rows = "".join(
        f"""<div class="qrow"><div class="qrow-t"><a href="{html.escape(u, quote=True)}" rel="noopener">▶ {html.escape(t)}</a></div>
  <div class="qrow-target">→ {html.escape(target)}</div>
  <div class="qrow-note">{html.escape(note)}</div></div>"""
        for t, u, target, note in VIDEO_QUEUE)
    queue_section = ""
    if VIDEO_QUEUE:
        queue_section = f"""<h2>🎬 Coming to the encyclopedia</h2>
<p class="lede">Videos already found and credited to Expedition Bible, waiting for the translation to
reach the book or chapter they belong to — logged here so nothing gets lost between now and then.</p>
<div class="panel qlist">{queue_rows}</div>"""

    body = f"""<h1 class="pagetitle">🏺 Encyclopedia</h1>
<p class="lede">The people and places the translation has reached — <strong>{len(places)} places,
{len(people)} people</strong> — each entry linked to every verse where it appears, with a growing film
shelf of archaeology and geography footage embedded directly on the entries they illuminate.</p>

<h2>Places</h2>
<div class="panel ency">{render(places)}</div>

<h2>People</h2>
<div class="panel ency">{render(people)}</div>

{queue_section}"""
    out = page(f"Encyclopedia — {SITE_NAME}", body, active="library",
               desc="People and places of the MisterLibrarian translation — every entry verse-linked, "
                    "with embedded archaeology videos credited to Expedition Bible.")
    open(os.path.join(OUT, "encyclopedia.html"), "w", encoding="utf-8").write(out)
    return len(places), len(people)


def _route_geo(stops, inner_w=780.0, pad=42.0):
    """Equirectangular projection of a journey's stops into SVG px, with a
    cos(lat) longitude correction so the shape isn't stretched. Returns the
    projector plus the canvas size and the lat/lon bounds."""
    lats = [s["coord"][0] for s in stops]
    lons = [s["coord"][1] for s in stops]
    lat_min, lat_max = min(lats), max(lats)
    lon_min, lon_max = min(lons), max(lons)
    kx = math.cos(math.radians((lat_min + lat_max) / 2.0))
    gw = ((lon_max - lon_min) * kx) or 1.0
    scale = inner_w / gw
    w = inner_w + 2 * pad
    h = (lat_max - lat_min) * scale + 2 * pad

    def proj(lat, lon):
        return (pad + (lon - lon_min) * kx * scale, pad + (lat_max - lat) * scale)

    return proj, w, h, (lat_min, lat_max, lon_min, lon_max)


# --- territory maps -------------------------------------------------------
# The Levant's fixed geography, in real lat/lon. These are the features that
# genuinely DON'T move (coastline, rift lakes, the Jordan, the Arabah), so they
# are what a reader orients by when an ancient border is only approximate.
_COAST = [(33.20, 35.22), (32.90, 35.07), (32.50, 34.90), (32.08, 34.76),
          (31.60, 34.55), (31.30, 34.35), (31.10, 34.25), (30.85, 34.00)]
_DEAD_SEA = [(31.77, 35.48), (31.75, 35.56), (31.55, 35.59), (31.35, 35.53),
             (31.20, 35.49), (31.05, 35.46), (31.02, 35.38), (31.20, 35.40),
             (31.45, 35.42), (31.65, 35.44)]
_GALILEE = [(32.88, 35.58), (32.86, 35.65), (32.75, 35.66), (32.70, 35.59),
            (32.78, 35.54), (32.85, 35.54)]
_JORDAN = [(32.70, 35.57), (32.45, 35.55), (32.20, 35.56), (31.95, 35.53), (31.80, 35.52)]
_ARABAH = [(31.02, 35.38), (30.60, 35.22), (30.10, 35.08), (29.70, 35.02), (29.53, 34.98)]
# The Gulf of Aqaba — the fixed feature the far south orients by. Without it a
# Midian map is a dashed blob in empty space; it also gives Edom's southern tip
# (Ezion-geber) something to sit on.
_AQABA = [(29.53, 34.98), (29.10, 34.75), (28.60, 34.55), (28.10, 34.42), (27.80, 34.32),
          (27.75, 34.52), (28.05, 34.62), (28.55, 34.78), (29.05, 34.98), (29.53, 35.08)]


# EGYPT. The basemap above is Levantine, which was fine until the first Egyptian
# territory (Goshen) rendered as a dashed polygon floating in empty space — a map
# of a river delta with no river and no sea on it. These are the fixed features
# the Delta orients by, and Exodus will lean on them too.
_EGYPT_COAST = [(31.20, 29.90), (31.42, 30.40), (31.45, 31.10), (31.52, 31.83),
                (31.32, 32.20), (31.27, 32.35), (31.15, 32.60), (31.10, 33.10),
                (30.95, 33.60), (30.85, 34.00)]
# The Nile up to the Delta apex just north of Cairo, then its two surviving
# branches (Rosetta west, Damietta east). The Pelusiac branch that mattered most
# in antiquity has silted up entirely and is left off — drawing a channel that no
# longer exists as though it were as certain as the other two would be a lie of
# exactly the kind these maps are supposed to avoid.
_NILE = [(29.30, 31.20), (29.70, 31.25), (30.05, 31.23), (30.35, 31.15)]
_NILE_ROSETTA = [(30.35, 31.15), (30.70, 30.95), (31.05, 30.65), (31.42, 30.40)]
_NILE_DAMIETTA = [(30.35, 31.15), (30.70, 31.35), (31.05, 31.60), (31.52, 31.83)]
_BITTER_LAKES = [(30.40, 32.33), (30.22, 32.44), (30.02, 32.48), (29.95, 32.40),
                 (30.15, 32.34), (30.32, 32.27)]


def _region_geo(pts, margin=0.55, inner_w=760.0, pad=40.0,
                min_aspect=1.15, max_aspect=2.40):
    """Same equirectangular + cos(lat) projection as the routes map, but framed
    on a territory's own boundary with a margin so neighbours stay visible.

    The frame is then clamped to a sane ASPECT RATIO. Most of these territories
    are long north-south strips squeezed between the rift and the desert (Edom
    is 1.4° of latitude by 0.9° of longitude), which projects to a ~840x1219
    tower that reads terribly on screen. Widening the short axis instead of
    cropping the long one keeps the whole territory visible AND pulls in more
    surrounding geography, which is exactly what a boundary map is for."""
    lats = [p[0] for p in pts]
    lons = [p[1] for p in pts]
    lat_min, lat_max = min(lats) - margin, max(lats) + margin
    lon_min, lon_max = min(lons) - margin, max(lons) + margin
    kx = math.cos(math.radians((lat_min + lat_max) / 2.0))

    lat_span, lon_span = lat_max - lat_min, lon_max - lon_min
    aspect = (lon_span * kx) / lat_span if lat_span else 1.0
    if aspect < min_aspect:                      # too tall -> widen longitude
        want = min_aspect * lat_span / kx
        grow = (want - lon_span) / 2.0
        lon_min, lon_max = lon_min - grow, lon_max + grow
    elif aspect > max_aspect:                    # too wide -> grow latitude
        want = (lon_span * kx) / max_aspect
        grow = (want - lat_span) / 2.0
        lat_min, lat_max = lat_min - grow, lat_max + grow
        kx = math.cos(math.radians((lat_min + lat_max) / 2.0))
    gw = ((lon_max - lon_min) * kx) or 1.0
    scale = inner_w / gw
    w = inner_w + 2 * pad
    h = (lat_max - lat_min) * scale + 2 * pad

    def proj(lat, lon):
        return (pad + (lon - lon_min) * kx * scale, pad + (lat_max - lat) * scale)

    return proj, w, h, (lat_min, lat_max, lon_min, lon_max), scale


def _path(proj, pts, close=False):
    d = "M " + " L ".join("%.1f,%.1f" % proj(a, b) for a, b in pts)
    return d + " Z" if close else d


def render_region_map(region, others=()):
    """A self-contained inline-SVG territory map: the region's boundary drawn as
    a bold DASHED outline over a soft fill (dashed on purpose — an ancient border
    is an approximation and should not look surveyed), on a basemap of the
    features that are actually fixed, with neighbouring territories outlined
    faintly for context."""
    bound = region["boundary"]
    proj, W, H, (lat_min, lat_max, lon_min, lon_max), scale = _region_geo(bound)

    def visible(pts):
        return any(lat_min <= a <= lat_max and lon_min <= b <= lon_max for a, b in pts)

    def inframe(lat, lon):
        """A feature's PATH may run off the edge (a coastline should), but its
        LABEL must not — an anchor outside the viewBox is simply invisible."""
        return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

    # Named SITES are the labels that matter most, so they are reserved first and
    # everything else gives way to them: basemap labels are dropped on collision,
    # and the big translucent region name is nudged clear. Without this the
    # watermark lands on top of a city ("EDOM" printed through "Sela / Petra").
    site_pts = [(proj(la, lo), lb) for la, lo, lb in region.get("sites", [])
                if inframe(la, lo)]
    # Reserve the label's actual BOX, not just its anchor — a long name like
    # "Al-Bad' (traditional Madyan)" reaches ~150px to the right of its dot, so
    # anchor-only testing reports "clear" while the text visibly crowds.
    reserved = [(x, x + 12.0 + len(lb) * 5.6, y) for (x, y), lb in site_pts]

    def clear(x, y, w=0.0, ry=13.0):
        lo, hi = x - w / 2.0, x + w / 2.0
        return all(hi < sx - 6 or lo > ex + 6 or abs(y - sy) > ry
                   for sx, ex, sy in reserved)

    parts = []
    # graticule
    for lon in range(int(math.ceil(lon_min)), int(math.floor(lon_max)) + 1):
        x, _ = proj(lat_max, lon)
        parts.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H:.1f}" class="rg-grid"/>')
        parts.append(f'<text x="{x:.1f}" y="{H-5:.1f}" class="rg-tick" text-anchor="middle">{lon}°E</text>')
    for lat in range(int(math.ceil(lat_min)), int(math.floor(lat_max)) + 1):
        _, y = proj(lat, lon_min)
        parts.append(f'<line x1="0" y1="{y:.1f}" x2="{W:.1f}" y2="{y:.1f}" class="rg-grid"/>')
        parts.append(f'<text x="5" y="{y-3:.1f}" class="rg-tick">{lat}°N</text>')

    # basemap: the things that don't move
    if visible(_EGYPT_COAST):
        parts.append(f'<path d="{_path(proj, _EGYPT_COAST)}" class="reg-coast"/>')
    if visible(_COAST):
        parts.append(f'<path d="{_path(proj, _COAST)}" class="reg-coast"/>')
        clat, clon = _COAST[len(_COAST) // 2]
        if inframe(clat, clon):
            cx, cy = proj(clat, clon)
            if clear(cx - 40, cy, w=64):
                parts.append(f'<text x="{cx-8:.1f}" y="{cy:.1f}" class="reg-sea" text-anchor="end">Great Sea</text>')
    for poly, label, anchor in ((_DEAD_SEA, "Salt Sea", (31.40, 35.48)),
                                (_AQABA, "Gulf of Aqaba", (28.55, 34.62)),
                                (_BITTER_LAKES, "Bitter Lakes", (30.18, 32.40)),
                                (_GALILEE, None, None)):
        if visible(poly):
            parts.append(f'<path d="{_path(proj, poly, close=True)}" class="reg-water"/>')
            if label and inframe(*anchor):
                lx, ly = proj(*anchor)
                if clear(lx, ly, w=len(label) * 5.6):
                    parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="reg-sea" text-anchor="middle">{label}</text>')
    for line, label in ((_JORDAN, "Jordan"), (_ARABAH, "the Arabah"),
                        (_NILE, "the Nile"), (_NILE_ROSETTA, None), (_NILE_DAMIETTA, None)):
        if visible(line):
            parts.append(f'<path d="{_path(proj, line)}" class="reg-river"/>')
            mlat, mlon = line[len(line) // 2]
            if label and inframe(mlat, mlon):
                mx, my = proj(mlat, mlon)
                if clear(mx + 30, my, w=len(label) * 5.6):
                    parts.append(f'<text x="{mx+6:.1f}" y="{my:.1f}" class="reg-rlab">{label}</text>')

    # neighbouring territories, faint, for context
    for o in others:
        if o["slug"] == region["slug"] or not visible(o["boundary"]):
            continue
        parts.append(f'<path d="{_path(proj, o["boundary"], close=True)}" class="reg-other"/>')
        olat = sum(p[0] for p in o["boundary"]) / len(o["boundary"])
        olon = sum(p[1] for p in o["boundary"]) / len(o["boundary"])
        if lat_min <= olat <= lat_max and lon_min <= olon <= lon_max:
            ox, oy = proj(olat, olon)
            parts.append(f'<text x="{ox:.1f}" y="{oy:.1f}" class="reg-olab" text-anchor="middle">'
                         f'{html.escape(o["name"].split(" (")[0])}</text>')

    # the territory itself
    parts.append(f'<path d="{_path(proj, bound, close=True)}" class="reg-fill"/>')
    parts.append(f'<path d="{_path(proj, bound, close=True)}" class="reg-edge"/>')

    # sites
    for (x, y), label in site_pts:
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" class="reg-dot"/>')
        parts.append(f'<text x="{x+6:.1f}" y="{y+3.5:.1f}" class="reg-site">{html.escape(label)}</text>')

    # region name across the middle — nudged off the nearest city label
    clat = sum(p[0] for p in bound) / len(bound)
    clon = sum(p[1] for p in bound) / len(bound)
    nx, ny = proj(clat, clon)
    for dy in (0, -34, 34, -68, 68, -102, 102):
        if clear(nx, ny + dy, w=len(region["name"].split(" (")[0]) * 13.0, ry=16.0) and 20 < ny + dy < H - 20:
            ny += dy
            break
    parts.append(f'<text x="{nx:.1f}" y="{ny:.1f}" class="reg-name" text-anchor="middle">'
                 f'{html.escape(region["name"].split(" (")[0].upper())}</text>')

    # scale bar (50 km) + compass
    km_deg = 111.0
    bar = (50.0 / km_deg) * scale
    bx, by = 54.0, H - 26.0
    parts.append(f'<line x1="{bx:.1f}" y1="{by:.1f}" x2="{bx+bar:.1f}" y2="{by:.1f}" class="reg-bar"/>')
    parts.append(f'<text x="{bx+bar/2:.1f}" y="{by-6:.1f}" class="rg-tick" text-anchor="middle">50 km</text>')
    parts.append(f'<g transform="translate({W-40:.1f},34)">'
                 f'<line x1="0" y1="10" x2="0" y2="-10" class="rg-comp"/>'
                 f'<polygon points="0,-14 4,-5 -4,-5" class="rg-compf"/>'
                 f'<text x="0" y="22" class="rg-cn" text-anchor="middle">N</text></g>')

    return f"""<div class="region-map">
  <svg viewBox="0 0 {W:.0f} {H:.0f}" role="img"
       aria-label="Approximate territory of {html.escape(region['name'], quote=True)}">{''.join(parts)}</svg>
  <div class="region-caveat"><strong>Approximate.</strong> {region['caveat']}</div>
</div>"""


def render_route_panel(route):
    """A self-contained inline-SVG map of a journey — no map library, no
    external tiles: real lat/lon projected, a dashed route line, numbered
    PRIMARY stops, small `via` bend-points that curve the line to the rivers,
    a faint degree graticule, river hints, a compass, and a numbered legend."""
    stops = route["stops"]
    proj, W, H, (lat_min, lat_max, lon_min, lon_max) = _route_geo(stops)

    grid = []
    for lon in range(int(math.ceil(lon_min)), int(math.floor(lon_max)) + 1):
        x, _ = proj(lat_max, lon)
        grid.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H:.1f}" class="rg-grid"/>')
        if lon % 2 == 0:
            grid.append(f'<text x="{x:.1f}" y="{H-5:.1f}" class="rg-tick" text-anchor="middle">{lon}°E</text>')
    for lat in range(int(math.ceil(lat_min)), int(math.floor(lat_max)) + 1):
        _, y = proj(lat, lon_min)
        grid.append(f'<line x1="0" y1="{y:.1f}" x2="{W:.1f}" y2="{y:.1f}" class="rg-grid"/>')
        grid.append(f'<text x="5" y="{y-3:.1f}" class="rg-tick">{lat}°N</text>')

    pts = [proj(s["coord"][0], s["coord"][1]) for s in stops]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    via, marks, legend = [], [], []
    n = 0
    for s, (x, y) in zip(stops, pts):
        if s.get("via"):
            via.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" class="rg-via"/>')
            continue
        n += 1
        marks.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" class="rg-halo"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9.5" class="rg-dot"/>'
            f'<text x="{x:.1f}" y="{y+3.6:.1f}" class="rg-num" text-anchor="middle">{n}</text>')
        name = html.escape(s["name"])
        if s.get("slug"):
            name = f'<a href="encyclopedia.html#{s["slug"]}">{name}</a>'
        ref = ""
        if s.get("ref"):
            c, v = s["ref"]
            ref = f' <a class="route-ref" href="{verse_url("Genesis", c, v)}">Gen {c}:{v}</a>'
        note = f' — {html.escape(s["note"])}' if s.get("note") else ""
        legend.append(f'<li><span class="route-num">{n}</span>'
                      f'<span><strong>{name}</strong>{note}{ref}</span></li>')

    ex, ey = proj(34.6, 42.2)
    jx, jy = proj(31.55, 35.55)
    rivers = (f'<text x="{ex:.1f}" y="{ey:.1f}" class="rg-river" text-anchor="middle">Euphrates</text>'
              f'<text x="{jx:.1f}" y="{jy:.1f}" class="rg-river" text-anchor="middle">Jordan</text>')

    compass = (f'<g transform="translate({W-24:.0f},26)">'
               f'<line x1="0" y1="9" x2="0" y2="-7" class="rg-comp"/>'
               f'<path d="M0,-11 L3.5,-4 L-3.5,-4 Z" class="rg-compf"/>'
               f'<text x="0" y="-13" class="rg-cn" text-anchor="middle">N</text></g>')

    svg = (f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" '
           f'aria-label="Route map: {html.escape(route["title"])}" xmlns="http://www.w3.org/2000/svg">'
           f'<title>{html.escape(route["title"])}</title>'
           f'{"".join(grid)}{rivers}'
           f'<path d="{d}" class="rg-under"/><path d="{d}" class="rg-line"/>'
           f'{"".join(via)}{"".join(marks)}{compass}</svg>')

    return (f'<section class="route-panel" id="route-{route["slug"]}">'
            f'<h2>🧭 {html.escape(route["title"])}</h2>'
            f'<div class="route-sub">{html.escape(route["chapters"])} · the journey at a glance</div>'
            f'<p class="route-blurb">{route["blurb"]}</p>'
            f'<div class="route-map">{svg}</div>'
            f'{render_route_inset(route)}'
            f'<ol class="route-legend">{"".join(legend)}</ol>'
            f'</section>')


def render_route_inset(route):
    """A zoomed inset for a journey's tightly-clustered leg (configured on the
    route as `inset`): the named stops inside the box, labeled, with the Jordan
    drawn in — the detail the full-sweep map can't show without the numbers
    colliding. box = (lat_min, lat_max, lon_min, lon_max)."""
    cfg = route.get("inset")
    if not cfg:
        return ""
    lat_min, lat_max, lon_min, lon_max = cfg["box"]
    inside = [s for s in route["stops"] if s.get("name")
              and lat_min <= s["coord"][0] <= lat_max and lon_min <= s["coord"][1] <= lon_max]
    if len(inside) < 2:
        return ""
    kx = math.cos(math.radians((lat_min + lat_max) / 2.0))
    pad, inner_w = 30.0, 430.0
    scale = inner_w / (((lon_max - lon_min) * kx) or 1.0)
    W = inner_w + 2 * pad
    H = (lat_max - lat_min) * scale + 2 * pad

    def proj(lat, lon):
        return (pad + (lon - lon_min) * kx * scale, pad + (lat_max - lat) * scale)

    jx, _ = proj(lat_max, cfg["jordan_lon"])
    steps = 10
    rv = " ".join(f"{jx + 6*math.sin(k/steps*math.pi*2.4):.1f},{H*k/steps:.1f}" for k in range(steps + 1))
    river = (f'<polyline points="{rv}" class="rg-jordan"/>'
             f'<text x="{jx+9:.1f}" y="{H-9:.1f}" class="rg-river">Jordan</text>')

    pts = [proj(s["coord"][0], s["coord"][1]) for s in inside]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    line = f'<path d="{d}" class="rg-under"/><path d="{d}" class="rg-line"/>'

    marks = []
    for s, (x, y) in zip(inside, pts):
        marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" class="rg-idot"/>')
        nm = html.escape(s["name"])
        if s["coord"][1] < cfg["jordan_lon"]:   # west of the Jordan -> label to the left
            marks.append(f'<text x="{x-9:.1f}" y="{y+3.6:.1f}" class="rg-ilbl" text-anchor="end">{nm}</text>')
        else:
            marks.append(f'<text x="{x+9:.1f}" y="{y+3.6:.1f}" class="rg-ilbl">{nm}</text>')

    entry = f'<text x="{pad:.0f}" y="17" class="rg-from">↑ the route enters from Damascus</text>'
    svg = (f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" '
           f'aria-label="Inset: {html.escape(cfg["title"])}" xmlns="http://www.w3.org/2000/svg">'
           f'<title>{html.escape(cfg["title"])}</title>'
           f'{river}{line}{"".join(marks)}{entry}</svg>')
    return (f'<div class="route-inset"><div class="route-inset-h">🔎 {html.escape(cfg["title"])} '
            f'<span>zoom</span></div>{svg}</div>')


def build_atlas():
    """One page, organized chapter-by-chapter (not place-by-place like the
    encyclopedia) so a chapter's Atlas toggle can jump straight to `atlas.html#genesis-N`.
    Reuses ENCYCLOPEDIA's existing (chapter, verse) refs — no new authoring needed to
    know which places belong to which chapter."""
    places = [e for e in ENCYCLOPEDIA if e["kind"] == "place"]
    n_mapped = sum(1 for e in places if e.get("coords"))

    by_chapter = defaultdict(dict)  # (book, chapter num) -> {slug: first_verse}
    for e in places:
        for b, c, v in e["refs"]:
            key = (b, c)
            if e["slug"] not in by_chapter[key] or v < by_chapter[key][e["slug"]]:
                by_chapter[key][e["slug"]] = v

    sections = []
    for slug, book, num, teaser in CHAPTERS:
        entries = sorted(by_chapter.get((book, num), {}).items(), key=lambda kv: kv[1])
        if entries:
            place_html = []
            for pslug, _first_v in entries:
                e = _SLUG_TO_ENTRY[pslug]
                refs = " ".join(ref_link(b, c, v) for b, c, v in e["refs"])
                if e.get("coords"):
                    lat, lon, span = e["coords"]
                    badge = ' <span class="atlas-approx">approximate</span>' if e.get("approx") else ""
                    caption = f'📍 <strong>{html.escape(e["name"])}</strong>'
                    if e.get("modern"):
                        caption += f' — modern-day {html.escape(e["modern"])}'
                    map_html = osm_embed(lat, lon, span, e["name"], caption=caption)
                    # A territory gets its BOUNDARY drawn above the pin map: a marker
                    # dropped in the middle of a country says nothing about its extent.
                    reg = _REGION_BY_SLUG.get(pslug)
                    if reg:
                        badge = ' <span class="atlas-territory">territory</span>' + badge
                        map_html = render_region_map(reg, others=REGIONS) + map_html
                else:
                    badge = ""
                    map_html = ('<div class="atlas-nomap">📍 No fixed point plotted — the location is genuinely '
                                "undetermined (see the note above), so this shows no guessed pin.</div>")
                place_html.append(f"""<div class="atlas-place" id="atlas-{e['slug']}">
  <div class="atlas-place-h"><a href="encyclopedia.html#{e['slug']}">{html.escape(e['name'])}</a>{badge}</div>
  <p>{e['desc']}</p>
  <div class="erefs"><span class="xr-label">in the text</span> {refs}</div>
  {map_html}
  <div class="atlas-overlay-empty">🗺️ No ancient-world overlay on the shelf yet for this site — a period map
  showing how the region actually looked in the biblical world gets added here as Mr. Librarian curates one,
  the same way the encyclopedia's film shelf grows.</div>
</div>""")
            body_html = "".join(place_html)
        else:
            body_html = '<div class="atlas-empty">No places are named in this chapter yet — nothing to map.</div>'
        sections.append(f"""<div class="atlas-chapter" id="{book_slug(book)}-{num}">
  <div class="atlas-chhead"><a href="{chapter_filename(book, num)}">{book} {num}</a>
    <span class="atlas-chteaser">{html.escape(teaser)}</span></div>
  {body_html}
</div>""")

    route_html = "".join(render_route_panel(r) for r in ROUTES)

    body = f"""<h1 class="pagetitle">🗺️ Atlas</h1>
<p class="lede">Every place the translation has named so far, mapped chapter by chapter —
<strong>{n_mapped} of {len(places)} places</strong> located on a live map (a handful are genuinely debated or
unidentified, and say so rather than guess a pin). Jump here straight from any chapter's toggle bar, or browse
chapter by chapter below. Where Expedition Bible's Joel Kramer stakes out a specific site — Eden and Havilah via
the Pishon, Sodom and Gomorrah at Tall el-Hammam — that identification is the one plotted, credited in the
place's own note. An <strong>ancient-world overlay</strong> — how each region actually looked in the biblical
world, not just today — is a shelf still being built; it starts empty and fills in as real sources are curated,
the same honest way the encyclopedia's film shelf grows.</p>

{route_html}
{''.join(sections)}"""
    out = page(f"Atlas — {SITE_NAME}", body, active="library",
               desc="A chapter-by-chapter atlas of the MisterLibrarian Bible Project — every named place mapped, "
                    "with an ancient-world overlay shelf still growing.")
    open(os.path.join(OUT, "atlas.html"), "w", encoding="utf-8").write(out)
    return n_mapped, len(places)


def build_library(stats):
    n_words, n_refs, n_dict, n_places, n_people, n_xrefs, n_mapped, n_atlas_places = stats
    body = f"""<h1 class="pagetitle">📚 The Library</h1>
<p class="lede">The reference room of the project — every shelf grows automatically or by hand as each
chapter is translated, so the library is always exactly as deep as the translation itself.</p>

<div class="cardgrid">
  <a class="card" href="concordance.html"><div class="card-t">🔠 Concordance</div>
  <div class="card-d">{n_words} words · {n_refs} occurrences — every significant English word in the
  translation, indexed to every verse. Generated automatically from the text at every build.</div></a>
  <a class="card" href="dictionary.html"><div class="card-t">📖 Dictionary</div>
  <div class="card-d">{n_dict} Hebrew terms — the working vocabulary behind the translation, each linked
  to the note that first discussed it.</div></a>
  <a class="card" href="encyclopedia.html"><div class="card-t">🏺 Encyclopedia</div>
  <div class="card-d">{n_places} places · {n_people} people — verse-linked entries, with a film shelf on
  every place for archaeology &amp; geography videos.</div></a>
  <a class="card" href="atlas.html"><div class="card-t">🗺️ Atlas</div>
  <div class="card-d">{n_mapped} of {n_atlas_places} places mapped so far, chapter by chapter — a live map
  for every located site, with an ancient-world overlay shelf still growing.</div></a>
</div>

<h2>Cross-references</h2>
<div class="panel prose">
  <p><strong>{n_xrefs} connections and counting.</strong> The translator's notes keep catching the text
  quoting itself — the naked/crafty pun across the Genesis 2/3 break, "desire and mastery" recurring from
  Eve to Cain, Babel's grasped-at name answered by Abram's given one. Each of those connections is now a
  live link: look for the <span class="xref" style="cursor:default">⤷ 11:4</span> chips under verses on
  the chapter pages — every link runs both directions, and hovering shows why the two verses are
  connected. New chains are added as each chapter lands.</p>
</div>

<h2>Where this library is heading</h2>
<div class="panel prose">
  <p><strong>🔴 Red letters — live.</strong> The recorded words of Jesus are set in red — a promise
  declared on this page "so the convention is ready the day Matthew begins," and kept the day Matthew
  began: the Sermon on the Mount (Matthew 5), with John 1–2 and the risen Christ's words in
  Revelation 1–2 retrofitted the same day. (The Hebrew Bible's direct divine speech stays in ordinary
  type, as in nearly all red-letter editions.)</p>
  <p><strong>▶ The film shelf.</strong> Every place entry in the encyclopedia has a slot for curated
  archaeology and geography videos — excavations, site walk-throughs, museum pieces. Mr. Librarian
  curates; the encyclopedia is where they live.</p>
  <p><strong>🗺️ Ancient-world overlays.</strong> The atlas's live maps show where these places sit today;
  a period-accurate overlay — cities, kingdoms, and borders as they stood in the biblical world — is the
  next layer, added site by site as real sources are found rather than guessed at.</p>
  <p><strong>⤷ Deeper cross-references.</strong> As the translation grows, the chains multiply — and
  once multiple books exist, they'll connect across books the way study Bibles do, but built only from
  connections this project's own notes have actually argued for.</p>
  <p><strong>🔠 A Hebrew concordance.</strong> The current concordance indexes the English; a
  Hebrew-side index (every occurrence of <em>nefesh</em>, every <em>toldot</em>) is the natural next
  shelf.</p>
</div>"""
    out = page(f"Library — {SITE_NAME}", body, active="library",
               desc="The reference room of the MisterLibrarian Bible Project: concordance, dictionary, "
                    "encyclopedia, and cross-references — all growing with the translation.")
    open(os.path.join(OUT, "library.html"), "w", encoding="utf-8").write(out)


def nav_strip(book, num, position):
    """Book-scoped prev/next: chain within the SAME book. At a book's first
    published chapter, an NT book links back to the New Testament intro; at its
    last published chapter, show the next chapter of that book as coming-soon."""
    same = sorted(n for (_s, b, n, _t) in CHAPTERS if b == book)
    i = same.index(num)
    prev_html = ""
    if i > 0:
        prev_html = f'<a href="{chapter_filename(book, same[i - 1])}">◄ {book} {same[i - 1]}</a>'
    elif _is_nt(book):
        prev_html = '<a href="new-testament.html">◄ New Testament</a>'
    else:
        prev_html = '<a href="old-testament.html">◄ Old Testament</a>'
    if i < len(same) - 1:
        next_html = f'<a href="{chapter_filename(book, same[i + 1])}">{book} {same[i + 1]} ►</a>'
    elif num < BOOK_TOTAL.get(book, num):
        next_html = f'<span class="dis">{book} {num + 1} (coming soon)</span>'
    else:
        next_html = ""
    mid = '<a href="toc.html">\U0001F4DC Table of Contents</a>'
    if book in BOOK_INTROS:
        mid = f'<a href="book-{book_slug(book)}.html">\U0001F4D6 {book}</a> · ' + mid
    return (f'<div class="chnav {position}"><div class="side left">{prev_html}</div>'
            f'<div class="mid">{mid}</div>'
            f'<div class="side right">{next_html}</div></div>')


def chrono_strip(slug):
    """The little where-you-are-in-time bar at the top of a chapter page: the six
    eras as chips (current one lit), the chapter's own when-line, and the honest
    clock note — linking to the full chronology page. Driven by CHRON_CHAPTERS;
    a chapter with no entry simply gets no strip."""
    info = CHRON_CHAPTERS.get(slug)
    if not info:
        return ""
    chips = "".join(
        f'<span class="cs-era{" cs-on" if key == info["era"] else ""}">{label}</span>'
        for key, label in CHRON_ERAS)
    clock = f'<div class="cs-clock">{info["clock"]}</div>' if info.get("clock") else ""
    return (f'<div class="chrono-strip">'
            f'<div class="cs-eras">{chips}</div>'
            f'<div class="cs-body"><span class="cs-icon">🕰</span>'
            f'<div class="cs-text"><div class="cs-when">{info["when"]}</div>{clock}</div>'
            f'<a class="cs-link" href="chronology.html#era-{info["era"]}">Full chronology →</a></div>'
            f'</div>')


VERSE_DIR = "v"   # per-verse share stubs live under /v/
_VERSE_STUB_RE = re.compile(
    r'id="(v(?:\d+-)?\d+)"[^>]*>.*?<div class="eng">(.*?)</div>', re.S)


def _plain(s):
    """HTML fragment -> clean single-line text (for an og:description)."""
    s = re.sub(r"<[^>]+>", "", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def _verse_stub_html(ref, desc, target, chfile, stub_url, og_image):
    """A tiny share-stub page: crawlers read this verse's own OG tags; humans are
    redirected instantly to the real chapter at the verse anchor. `noindex,follow`
    keeps these thin pages out of search while the canonical points at the chapter."""
    title = html.escape(f"{ref} · Mister Translation", quote=True)
    de = html.escape(desc, quote=True)
    tgt = html.escape(target, quote=True)   # e.g. /genesis-1.html#v3 (root-relative)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<meta name="robots" content="noindex,follow"/>
<link rel="canonical" href="{SITE_URL}/{chfile}"/>
<link rel="icon" href="{FAVICON}"/>
<meta name="description" content="{de}"/>
<meta property="og:site_name" content="Mister Translation"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{title}"/>
<meta property="og:description" content="{de}"/>
<meta property="og:url" content="{html.escape(stub_url, quote=True)}"/>
<meta property="og:image" content="{og_image}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{title}"/>
<meta name="twitter:description" content="{de}"/>
<meta name="twitter:image" content="{og_image}"/>
<meta http-equiv="refresh" content="0;url={tgt}"/>
<script>location.replace('{target}');</script>
<style>body{{background:#060b14;color:#94a3b8;font-family:-apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;text-align:center;padding:80px 20px}}a{{color:#e8c968}}</style>
</head>
<body>
<p>Opening <a href="{tgt}">{html.escape(ref)}</a> in the Mister Translation…</p>
</body>
</html>
"""


_CARD_FONT_PATHS = {
    "serif":   "/System/Library/Fonts/Supplemental/Georgia.ttf",
    "serif_b": "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
    "sans":    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "sans_b":  "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
}
_CARD_FONTS = {}


def _card_font(kind, size):
    from PIL import ImageFont
    key = (kind, size)
    if key not in _CARD_FONTS:
        _CARD_FONTS[key] = ImageFont.truetype(_CARD_FONT_PATHS[kind], size)
    return _CARD_FONTS[key]


def _card_wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if cur and draw.textlength(t, font=font) > maxw:
            lines.append(cur); cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def _render_verse_card(book, num, v, text, path):
    """Render a 1200x630 og:image verse card (dark gradient + gold frame, the
    verse centred, its reference, and the wordmark) as a quantized PNG (~30KB).
    Returns True, or False if Pillow / the fonts aren't available — the caller
    then falls back to the branded default og:image."""
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except Exception:
        return False
    if not all(os.path.exists(p) for p in _CARD_FONT_PATHS.values()):
        return False
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (13, 21, 32))
    d = ImageDraw.Draw(img)
    top, bot = (13, 21, 32), (6, 11, 20)               # vertical gradient
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=(int(top[0] + (bot[0] - top[0]) * t),
                                       int(top[1] + (bot[1] - top[1]) * t),
                                       int(top[2] + (bot[2] - top[2]) * t)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))     # soft gold glow near the top
    ImageDraw.Draw(glow).ellipse([W * 0.5 - 520, -380, W * 0.5 + 520, 300],
                                 fill=(232, 201, 104, 42))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=26, outline=(92, 84, 54), width=2)

    pad = 110; cw = W - 2 * pad; n = len(text)
    size = 58 if n <= 70 else 50 if n <= 140 else 44 if n <= 220 else 38 if n <= 320 else 32
    while size >= 26:                                   # shrink to fit the verse zone
        vf = _card_font("serif", size); lines = _card_wrap(d, text, vf, cw); lh = int(size * 1.42)
        if len(lines) * lh <= 372:
            break
        size -= 3
    vf = _card_font("serif", size); lines = _card_wrap(d, text, vf, cw); lh = int(size * 1.42)
    if len(lines) * lh > 372:                           # still too tall -> truncate
        keep = max(1, 372 // lh); lines = lines[:keep]
        if lines:
            lines[-1] = lines[-1].rstrip(".,;:") + " …"
    verseH = len(lines) * lh

    ref = f"{book} {num}:{v}".upper()
    rf = _card_font("sans_b", 30); refH = 38; divH = 4; gap1 = 30; gap2 = 26
    blockH = verseH + gap1 + divH + gap2 + refH
    top_zone, bot_zone = 92, H - 135
    y = top_zone + ((bot_zone - top_zone) - blockH) // 2
    for ln in lines:
        d.text((W / 2, y), ln, font=vf, fill=(242, 236, 218), anchor="ma"); y += lh
    y += gap1
    d.rectangle([W / 2 - 48, y, W / 2 + 48, y + divH], fill=(232, 201, 104)); y += divH + gap2
    track = 3                                           # letter-spaced reference
    tw = sum(d.textlength(c, font=rf) for c in ref) + track * (len(ref) - 1)
    cx = W / 2 - tw / 2
    for c in ref:
        d.text((cx, y), c, font=rf, fill=(232, 201, 104), anchor="la")
        cx += d.textlength(c, font=rf) + track

    wf = _card_font("serif_b", 34); p1, p2 = "Mister ", "Translation"
    w1 = d.textlength(p1, font=wf); w2 = d.textlength(p2, font=wf); sx = W / 2 - (w1 + w2) / 2
    d.text((sx, H - 100), p1, font=wf, fill=(247, 242, 226), anchor="la")
    d.text((sx + w1, H - 100), p2, font=wf, fill=(232, 201, 104), anchor="la")
    d.text((W / 2, H - 54), "mistertranslation.com",
           font=_card_font("sans", 21), fill=(133, 147, 166), anchor="ma")

    img.quantize(colors=128, dither=Image.FLOYDSTEINBERG).save(path, "PNG", optimize=True)
    return True


def _render_default_card(path):
    """Render the branded default og:image (img/og-default.png) — the same dark
    gradient + gold frame as the verse cards, with the wordmark, a divider, the
    two-line tagline, and the domain. Regenerated by the build so the asset stays
    in sync with the code (returns False if Pillow / the fonts aren't available)."""
    try:
        from PIL import Image, ImageDraw, ImageFilter
    except Exception:
        return False
    if not all(os.path.exists(p) for p in _CARD_FONT_PATHS.values()):
        return False
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (13, 21, 32))
    d = ImageDraw.Draw(img)
    top, bot = (13, 21, 32), (6, 11, 20)               # vertical gradient
    for y in range(H):
        t = y / (H - 1)
        d.line([(0, y), (W, y)], fill=(int(top[0] + (bot[0] - top[0]) * t),
                                       int(top[1] + (bot[1] - top[1]) * t),
                                       int(top[2] + (bot[2] - top[2]) * t)))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))     # soft gold glow near the top
    ImageDraw.Draw(glow).ellipse([W * 0.5 - 520, -380, W * 0.5 + 520, 300],
                                 fill=(232, 201, 104, 42))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([34, 34, W - 34, H - 34], radius=26, outline=(92, 84, 54), width=2)

    # wordmark: two-tone, centred, ~upper third
    wf = _card_font("serif_b", 74); p1, p2 = "Mister ", "Translation"
    w1 = d.textlength(p1, font=wf); w2 = d.textlength(p2, font=wf); sx = W / 2 - (w1 + w2) / 2
    d.text((sx, 205), p1, font=wf, fill=(247, 242, 226), anchor="lm")
    d.text((sx + w1, 205), p2, font=wf, fill=(232, 201, 104), anchor="lm")

    d.rectangle([W / 2 - 48, 278, W / 2 + 48, 282], fill=(232, 201, 104))   # divider

    sf = _card_font("sans", 30)                        # two-line tagline
    d.text((W / 2, 332), "A fresh translation of the Bible —",
           font=sf, fill=(200, 206, 214), anchor="mm")
    d.text((W / 2, 380), "from the Hebrew and Greek, verse by verse.",
           font=sf, fill=(200, 206, 214), anchor="mm")

    d.text((W / 2, 452), "mistertranslation.com",
           font=_card_font("sans", 21), fill=(133, 147, 166), anchor="mm")

    img.quantize(colors=128, dither=Image.FLOYDSTEINBERG).save(path, "PNG", optimize=True)
    return True


# --- verse-card staleness + size budget -------------------------------------------
# Cards are expensive to render, so they are reused across builds. But "reuse if the
# file exists" strands the old image when a later exactness pass rewords the verse.
# A tiny content-hash manifest (img/v/.cards.json) fixes that: a card is re-rendered
# only when the verse text (or CARD_TEMPLATE_VERSION) changed. A pre-manifest card is
# trusted and seeded, so this ships without re-rendering the ~1,200 existing cards.
CARD_TEMPLATE_VERSION = "1"   # bump to force-regenerate EVERY verse card after a card-design change
CARD_BUDGET_WARN_MB = 700     # GitHub Pages publishes ~1 GB max; warn before the cards get there
_CARD_MANIFEST = None
_CARD_MANIFEST_DIRTY = False


def _card_manifest_path():
    return os.path.join(OUT, "img", VERSE_DIR, ".cards.json")


def _card_manifest():
    global _CARD_MANIFEST
    if _CARD_MANIFEST is None:
        try:
            _CARD_MANIFEST = json.load(open(_card_manifest_path(), encoding="utf-8"))
        except (OSError, ValueError):
            _CARD_MANIFEST = {}
    return _CARD_MANIFEST


def _card_hash(text):
    return hashlib.sha1(f"{CARD_TEMPLATE_VERSION}\x00{text}".encode("utf-8")).hexdigest()[:16]


def _set_card_hash(key, h):
    global _CARD_MANIFEST_DIRTY
    _card_manifest()[key] = h
    _CARD_MANIFEST_DIRTY = True


def _ensure_verse_card(book, num, v, stem, text, card_rel):
    """(Re)render the verse's og:image card only when needed. A hash MISMATCH (verse
    text or CARD_TEMPLATE_VERSION changed) forces a re-render; an existing card with no
    manifest entry is trusted and seeded. Returns card_rel, or None if Pillow/fonts are
    unavailable (the caller then falls back to the branded default og:image)."""
    card_path = os.path.join(OUT, card_rel)
    key = f"{stem}-{v}"
    want = _card_hash(text)
    have = _card_manifest().get(key)
    if os.path.exists(card_path):
        if have == want:
            return card_rel
        if have is None:                 # pre-existing card from before the manifest — trust + seed
            _set_card_hash(key, want)
            return card_rel
    if _render_verse_card(book, num, v, text, card_path):
        _set_card_hash(key, want)
        return card_rel
    return None


def save_card_manifest():
    if _CARD_MANIFEST_DIRTY and _CARD_MANIFEST is not None:
        with open(_card_manifest_path(), "w", encoding="utf-8") as f:
            json.dump(_CARD_MANIFEST, f, ensure_ascii=False, sort_keys=True)


def report_card_budget():
    cdir = os.path.join(OUT, "img", VERSE_DIR)
    if not os.path.isdir(cdir):
        return
    pngs = [f for f in os.listdir(cdir) if f.endswith(".png")]
    mb = sum(os.path.getsize(os.path.join(cdir, f)) for f in pngs) / (1024 * 1024)
    over = mb >= CARD_BUDGET_WARN_MB
    msg = f"{'⚠  ' if over else '   '}verse cards: {len(pngs)} PNGs, {mb:.0f} MB"
    if over:
        msg += (" — approaching the ~1 GB GitHub Pages publish cap; plan smaller/JPEG "
                "cards, per-chapter cards, or a separate image host before broad coverage")
    print(msg)


def build_verse_stubs(book, num, content):
    """Emit one /v/<book>-<ch>-<v>.html share-stub per verse in this chapter, so a
    shared verse link unfurls with THAT verse's text (crawlers ignore #fragments)."""
    chfile = chapter_filename(book, num)   # e.g. genesis-1.html
    stem = chfile[:-5]                       # genesis-1  (matches reader-notes.js)
    vdir = os.path.join(OUT, VERSE_DIR)
    cdir = os.path.join(OUT, "img", VERSE_DIR)
    os.makedirs(vdir, exist_ok=True)
    os.makedirs(cdir, exist_ok=True)
    for m in _VERSE_STUB_RE.finditer(content):
        vid = m.group(1)
        v = vid.rsplit("-", 1)[-1] if "-" in vid else vid[1:]
        eng = re.sub(r'<a class="notelink".*?</a>', "", m.group(2), flags=re.S)
        text = _plain(eng)
        if not text:
            continue
        ref = f"{book} {num}:{v}"
        desc = text if len(text) <= 200 else text[:197].rsplit(" ", 1)[0] + "…"
        target = f"/{chfile}#{verse_anchor(num, v)}"
        stub_url = f"{SITE_URL}/{VERSE_DIR}/{stem}-{v}.html"
        # per-verse og:image card — reused across builds, but re-rendered when the verse
        # text changed (see _ensure_verse_card); falls back to the branded default if
        # Pillow/fonts are absent.
        card_rel = _ensure_verse_card(book, num, v, stem, text,
                                      f"img/{VERSE_DIR}/{stem}-{v}.png")
        og_image = f"{SITE_URL}/{card_rel}" if card_rel else OG_IMAGE
        out = _verse_stub_html(ref, desc, target, chfile, stub_url, og_image)
        open(os.path.join(vdir, f"{stem}-{v}.html"), "w", encoding="utf-8").write(out)


def build_chapter_pages(chapters):
    es_panels = _es_panels()   # chapters with a Spanish edition -> the reader's español toggle
    for slug, book, num, teaser in CHAPTERS:
        content = clean_chapter(chapters[slug])
        content = inject_encyclopedia_links(content, book, num)
        content = inject_xrefs(content, book, num)
        content = move_clips_into_verses(content)
        content = render_film_clips(content)
        content, has_es = inject_spanish(content, slug, es_panels)
        orig_lang = "Greek" if _is_nt(book) else "Hebrew"   # the Hide-original toggle label
        # A pre-generated narration MP3 (audio/<book>-N.mp3) is preferred when
        # present; otherwise the Listen button reads the page aloud in the
        # browser. gen_audio.py produces those files.
        mp3_rel = f"audio/{book_slug(book)}-{num}.mp3"
        audio_attr = f' data-audio="{mp3_rel}"' if os.path.exists(os.path.join(OUT, mp3_rel)) else ""
        es_file = chapter_filename(book, num)[:-5] + ".es.html"
        es_btn = ((f'<button class="tgl" id="esptgl" onclick="toggleEsp()">Mostrar español</button>'
                   f'<a class="tgl" href="{es_file}" title="Edición en español">\U0001F310 Español</a>')
                  if has_es else "")
        toggle = (f'<div class="togglebar">'
                  f'<button class="tgl tgl-read" id="readtgl">Mark as read</button>'
                  f'<div class="tgl-group">'
                  f'<button class="tgl tgl-audio" id="audiotgl"{audio_attr}>🔊 Listen</button>'
                  f'<button class="tgl" id="hebtgl" onclick="toggleHeb()">Hide {orig_lang}</button>'
                  f'{es_btn}'
                  f'<a class="tgl" href="atlas.html#{book_slug(book)}-{num}">🗺️ Atlas</a>'
                  f'</div>'
                  f'</div>')
        es_js = (("""
function toggleEsp(){
  var shown = document.body.classList.toggle("show-esp");
  document.getElementById("esptgl").textContent = shown ? "Ocultar espa\\u00f1ol" : "Mostrar espa\\u00f1ol";
  try{ localStorage.setItem("mtlib_showesp", shown ? "1" : "0"); }catch(e){}
}
(function(){ try{ if(localStorage.getItem("mtlib_showesp")==="1"){
  document.body.classList.add("show-esp");
  document.getElementById("esptgl").textContent = "Ocultar espa\\u00f1ol";
} }catch(e){} })();""") if has_es else "")
        body = f"""{nav_strip(book, num, 'top')}
{toggle}
{chrono_strip(slug)}
<article class="chapter">
{content}
</article>
{nav_strip(book, num, 'bottom')}
<script>
function toggleHeb(){{
  var hidden = document.body.classList.toggle("hide-heb");
  document.getElementById("hebtgl").textContent = hidden ? "Show {orig_lang}" : "Hide {orig_lang}";
  try{{ localStorage.setItem("mtlib_hideheb", hidden ? "1" : "0"); }}catch(e){{}}
}}
(function(){{ try{{
  if (localStorage.getItem("mtlib_hideheb") === "1"){{
    document.body.classList.add("hide-heb");
    document.getElementById("hebtgl").textContent = "Show {orig_lang}";
  }}
}}catch(e){{}} }})();
(function(){{
  var slug = "{slug}";
  var btn = document.getElementById("readtgl");
  function render(){{
    var isRead = !!mtlibGetRead()[slug];
    btn.textContent = isRead ? "\\u2713 Read" : "Mark as read";
    btn.classList.toggle("done", isRead);
  }}
  btn.addEventListener("click", function(){{
    mtlibSetRead(slug, !mtlibGetRead()[slug]);
    render();
  }});
  render();
}})();
{es_js}
</script>"""
        src = "the Greek (the critical Greek New Testament)" if _is_nt(book) else "the Hebrew (Masoretic Text)"
        desc = (f"{book} {num} translated fresh from {src}, with verse-by-verse "
                f"notes comparing NIV, KJV, Douay-Rheims, The Living Bible, the 1599 Geneva, ASV, and "
                f"NWT. {teaser}")
        out = page(f"{book} {num} — {SITE_NAME}", body, desc=desc,
                   url=chapter_filename(book, num))
        open(os.path.join(OUT, chapter_filename(book, num)), "w", encoding="utf-8").write(out)
        build_verse_stubs(book, num, content)


_BOOK_INTRO_CSS = """<style>
.bi-head{margin:0 0 4px}
.bi-names{color:var(--muted);font-size:14px;margin:0 0 18px}
.bi-heb{font-size:20px;font-family:'SBL Hebrew','Times New Roman',serif}
.bi-tr{font-style:italic}
.bi-facts{display:grid;gap:0}
.bi-row{display:grid;grid-template-columns:150px 1fr;gap:14px;padding:9px 0;border-top:1px solid var(--line,#2a2f3a)}
.bi-row:first-child{border-top:0}
.bi-k{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.04em;padding-top:2px}
.bi-v{line-height:1.55}
.bi-struct{display:grid;grid-template-columns:66px 1fr;gap:12px;padding:6px 0}
.bi-struct-r{font-weight:700;color:var(--accent,#c9a227)}
.bi-chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:4px}
.bi-chip{display:inline-block;padding:4px 11px;border-radius:20px;background:rgba(255,255,255,.05);
  border:1px solid var(--line,#2a2f3a);text-decoration:none;font-size:13px}
.bi-chip:hover{background:rgba(255,255,255,.10)}
.bi-debates{border-left:3px solid var(--accent,#c9a227)}
.bi-prog{display:flex;align-items:baseline;gap:10px;margin-bottom:8px}
.bi-prog b{font-size:22px}
@media(max-width:560px){.bi-row{grid-template-columns:1fr}.bi-k{padding-top:0}}
</style>"""


def build_book_intros():
    """A reference 'front page' for each book the translation has begun — Hebrew/
    Greek name, author, date, place, genre, structure, themes, key words and
    people (linked into the dictionary and encyclopedia), the source text, and —
    in the project's neutrality habit — an honest 'Where the debates are' box for
    authorship and date. Reached from the Table of Contents; the data lives in
    library_data.BOOK_INTROS. A LIVING page: grow the data as more is found."""
    dict_term = {e[0]: e[1] for e in DICTIONARY}
    ency_name = {e["slug"]: e["name"] for e in ENCYCLOPEDIA}

    def row(label, val):
        return (f'<div class="bi-row"><div class="bi-k">{label}</div>'
                f'<div class="bi-v">{val}</div></div>') if val else ""

    # Every book the translation has STARTED gets a page — not only the ones with
    # a hand-written BOOK_INTROS entry. A book page is first a navigator (chapter
    # buttons + each chapter's commentary); the reference material is a bonus that
    # appears when the data exists. Without this, seven started books (Exodus,
    # Jeremiah, Proverbs, Daniel, Matthew, John, Revelation) were dead chips on
    # the Table of Contents with nowhere to click through to.
    started = []
    for _s, b, _n, _t in CHAPTERS:
        if b not in started:
            started.append(b)

    for book in started:
        info = BOOK_INTROS.get(book, {})
        total = BOOK_TOTAL.get(book, 0)
        chs = sorted(((n, t) for (_s, b, n, t) in CHAPTERS if b == book))
        pub = [n for n, _t in chs]
        pct = round(len(pub) / total * 1000) / 10 if total else 0

        heb, heb_tr, heb_m = info.get("hebrew_name", ""), info.get("hebrew_translit", ""), info.get("hebrew_meaning", "")
        names = []
        if heb:
            names.append(f'<span class="bi-heb">{heb}</span> <span class="bi-tr">{heb_tr}</span>'
                         + (f' — {heb_m}' if heb_m else ''))
        gk, gk_m = info.get("greek_name", ""), info.get("greek_meaning", "")
        if gk:
            names.append(f'{gk}' + (f' — {gk_m}' if gk_m else ''))
        names_html = "<br>".join(names)

        facts = "".join([
            row("Where it sits", info.get("canon", "")),
            row("Genre", info.get("genre", "")),
            row("Author", info.get("author", "")),
            row("Date written", info.get("date", "")),
            row("Place", info.get("place", "")),
            row("Audience", info.get("audience", "")),
        ])
        struct = "".join(
            f'<div class="bi-struct"><span class="bi-struct-r">{r}</span><span>{l}</span></div>'
            for r, l in info.get("structure", []))
        themes = "".join(f"<li>{t}</li>" for t in info.get("themes", []))
        kw = "".join(
            f'<a class="bi-chip" href="dictionary.html#{s}"><em>{html.escape(dict_term[s])}</em></a>'
            for s in info.get("key_words", []) if s in dict_term)
        kp = "".join(
            f'<a class="bi-chip" href="encyclopedia.html#{s}">{html.escape(ency_name[s])}</a>'
            for s in info.get("key_people", []) if s in ency_name)

        # The chapter buttons: published chapters are live, the rest are placeholders
        # so you can see the shape of the whole book at a glance.
        pubset = set(pub)
        chips = "".join(
            (f'<a class="chch chch-done" href="{chapter_filename(book, i)}">{i}</a>'
             if i in pubset else f'<span class="chch">{i}</span>')
            for i in range(1, (total or (max(pub) if pub else 0)) + 1))

        # Each published chapter's commentary, on the book's own page. This is the
        # per-chapter blurb that used to live only as one long undifferentiated
        # list on the Table of Contents, mixed in with every other book.
        commentary = "".join(
            f'<a class="chrow" href="{chapter_filename(book, n)}">'
            f'<span class="chrow-n">{book} {n}</span>'
            f'<span class="chrow-t">{t}</span></a>'
            for n, t in chs)

        christ = info.get("christ", "")
        christ_panel = (f'<div class="panel prose"><h2 style="margin-top:2px">Looking forward</h2>'
                        f'<p>{christ}</p></div>') if christ else ""
        words_panel = ""
        if kw or kp:
            words_panel = '<div class="panel prose"><h2 style="margin-top:2px">Key words &amp; people</h2>'
            if kw:
                words_panel += ('<p class="muted" style="margin:0 0 4px">Words this book turns on — '
                                'each links to its dictionary entry:</p>'
                                f'<div class="bi-chips">{kw}</div>')
            if kp:
                words_panel += ('<p class="muted" style="margin:14px 0 4px">People &amp; places — '
                                'each links to the encyclopedia:</p>'
                                f'<div class="bi-chips">{kp}</div>')
            words_panel += '</div>'

        # A FINISHED book has nothing to report as progress: a 100% thermometer,
        # "the rest are still ahead," AND a "Complete — all N chapters translated"
        # banner all state the obvious once the grid is entirely gold, so a complete
        # book skips the status line and goes straight to the chapters.
        complete = bool(total) and len(pub) >= total
        if complete:
            progress_block = ""
            grid_hint = ""
        else:
            progress_block = (f'  <div class="bi-prog"><b>{len(pub)}</b> of {total} chapters translated '
                              f'<span class="progress-label">· {pct}%</span></div>\n'
                              f'  <div class="bar"><div class="bar-fill" style="width:{pct}%"></div></div>')
            grid_hint = ('  <p class="muted" style="margin:12px 0 8px">Gold chapters are published — '
                         'click one to read it. The rest are still ahead.</p>\n')

        # Every reference panel is conditional: a book with no BOOK_INTROS entry
        # still gets a full, useful page rather than a scatter of empty headings.
        names_block = f'<p class="bi-names">{names_html}</p>' if names_html else ""
        tagline_block = f'<p class="lede">{info["tagline"]}</p>' if info.get("tagline") else ""
        facts_block = f'<div class="panel">\n  <div class="bi-facts">{facts}</div>\n</div>' if facts else ""
        struct_block = f"<h2>How it's laid out</h2>\n<div class=\"panel\">{struct}</div>" if struct else ""
        themes_block = (f'<h2>What it\'s about</h2>\n<div class="panel prose">'
                        f'<ul style="margin:2px 0 0;padding-left:20px;line-height:1.6">{themes}</ul></div>'
                        ) if themes else ""
        source_block = (f'<div class="panel prose">\n  <h2 style="margin-top:2px">The source text</h2>'
                        f'\n  <p>{info["source_text"]}</p>\n</div>') if info.get("source_text") else ""
        debates_block = (f'<div class="panel prose bi-debates">\n'
                         f'  <h2 style="margin-top:2px">Where the debates are</h2>\n'
                         f'  <p>{info["debates"]}</p>\n</div>') if info.get("debates") else ""

        ref_blocks = "\n\n".join(b for b in [facts_block, struct_block, themes_block, words_panel,
                                              source_block, christ_panel, debates_block] if b)
        reference = "<h2>About the book</h2>\n" + (ref_blocks or
                    '<div class="panel prose"><p class="muted" style="margin:0">A full introduction to '
                    f'{book} — author, date, structure, themes and the honest questions of authorship — '
                    'is still to be written for this book.</p></div>')

        body = f"""{_BOOK_INTRO_CSS}
<p class="muted" style="margin:0 0 6px"><a href="toc.html">\U0001F4DC Table of Contents</a> ›
{book}</p>
<h1 class="pagetitle bi-head">\U0001F4D6 {book}</h1>
{names_block}
{tagline_block}

<h2>Chapters</h2>
<div class="panel">
{progress_block}
{grid_hint}  <div class="chgrid">{chips}</div>
</div>

<h2>Chapter by chapter</h2>
<div class="panel chlist">
{commentary}
</div>

{reference}
"""
        out = page(f"{book} — Introduction — {SITE_NAME}", body, active="toc",
                   desc=f"An introduction to the book of {book}: author, date, place, structure, themes, "
                        f"and the honest questions of authorship — the reference front page for "
                        f"{book} in the MisterLibrarian translation.",
                   url=f"book-{book_slug(book)}.html")
        open(os.path.join(OUT, f"book-{book_slug(book)}.html"), "w", encoding="utf-8").write(out)


def build_toc():
    done = len(CHAPTERS)
    pct = round(done / TOTAL_BIBLE_CHAPTERS * 1000) / 10

    pub = defaultdict(set)          # book -> {published chapter numbers}
    book_seen = []                  # books with published chapters, first-seen order
    for _s, book, num, _t in CHAPTERS:
        if book not in pub:
            book_seen.append(book)
        pub[book].add(num)

    def book_chip(name, n):
        # Any book the translation has started is a live link to its own page —
        # build_book_intros() now generates one for every started book, so a
        # started book is never a dead chip here.
        if name in pub:
            inner = f'{name} <b>{len(pub[name])}/{n}</b>'
            return f'<a class="book book-active" href="book-{book_slug(name)}.html">{inner}</a>'
        return f'<span class="book">{name} <i>{n}</i></span>'
    ot = "".join(book_chip(n, c) for n, c in BOOKS_OT)
    nt = "".join(book_chip(n, c) for n, c in BOOKS_NT)
    # The per-book chapter grids and the per-chapter commentary that used to be
    # duplicated here now live on each book's own page, where they belong. This
    # page is the navigator: progress, then all 66 books.
    body = f"""<h1 class="pagetitle">\U0001F4DC Table of Contents</h1>
<p class="lede">Every book of the Bible, and how far the translation has reached in each. A book in
gold has been started — open it for its chapters and the commentary on each one. Everything else is
still ahead.</p>

<h2>Progress</h2>
<div class="panel">
  <div class="progress-row">
    <div class="progress-num"><span>{done}</span> of {TOTAL_BIBLE_CHAPTERS} chapters</div>
    <div class="progress-label">{pct}% of the Bible</div>
  </div>
  <div class="bar"><div class="bar-fill" style="width:{pct}%"></div></div>
</div>

<h2>All 66 Books</h2>
<div class="panel">
  <div class="testament">Old Testament · 39 books</div>
  <p class="muted" style="margin:2px 0 12px"><a href="old-testament.html">📜 Introduction to the Old Testament — the Hebrew Scriptures →</a></p>
  <div class="bookgrid">{ot}</div>
  <div class="testament">New Testament · 27 books</div>
  <p class="muted" style="margin:2px 0 12px"><a href="new-testament.html">📜 Introduction to the New Testament — the Greek Scriptures →</a></p>
  <div class="bookgrid">{nt}</div>
</div>"""
    out = page(f"Table of Contents — {SITE_NAME}", body, active="toc",
               desc="Progress tracker for the MisterLibrarian Bible Project: every published chapter of "
                    "the fresh-from-the-Hebrew translation, and everything still ahead.")
    open(os.path.join(OUT, "toc.html"), "w", encoding="utf-8").write(out)


def votd_entries(chapters):
    """Verse-of-the-day candidates, with the actual quote pulled live from the
    translation text (never hand-typed) so it can never drift from the chapter
    page. A candidate referencing a not-yet-published verse is silently
    skipped, so this list is safe to grow ahead of the translation."""
    text_by_ref = {(b, c, v): t for b, c, v, t in extract_verses_english(chapters)}
    entries = []
    for e in VERSE_OF_DAY:
        book, ch, v, blurb = e if len(e) == 4 else ("Genesis", e[0], e[1], e[2])
        text = text_by_ref.get((book, ch, v))
        if not text:
            continue
        entries.append({"ref": f"{book} {ch}:{v}", "text": text, "blurb": blurb,
                         "href": verse_url(book, ch, v)})
    return entries


def build_reading():
    rows = "".join(
        f'<label class="rrow" data-slug="{slug}" data-href="{chapter_filename(book, num)}">'
        f'<input type="checkbox" class="rchk"/>'
        f'<span class="rrow-n">{book} {num}</span>'
        f'<span class="rrow-t">{teaser}</span></label>'
        for slug, book, num, teaser in CHAPTERS)
    body = f"""<h1 class="pagetitle">\U0001F4D7 My Reading</h1>
<p class="lede">Track your own progress through the translation as it's published. Checked chapters are
remembered <strong>only in this browser</strong> — a bit of localStorage, nothing ever sent anywhere, no
account needed. Come back after a new chapter lands and pick up right where you left off. (You can also
check a chapter off directly from its own page, next to the Hide Hebrew toggle.)</p>

<div class="panel" id="continueBox" style="display:none"></div>

<h2>Your progress</h2>
<div class="panel">
  <div class="progress-row">
    <div class="progress-num"><span id="rDone">0</span> of {len(CHAPTERS)} read</div>
    <div class="progress-label" id="rPct">0%</div>
  </div>
  <div class="bar"><div class="bar-fill" id="rBar" style="width:0%"></div></div>
</div>

<h2>Chapters</h2>
<div class="panel chlist rlist">
{rows}
</div>

<p class="muted" style="margin-top:14px;font-size:12px"><a href="#" id="resetLink">Reset my progress</a></p>

<script>
(function(){{
  var rows = document.querySelectorAll(".rrow");
  function render(){{
    var read = mtlibGetRead();
    var done = 0, firstUnread = null;
    rows.forEach(function(r){{
      var slug = r.dataset.slug;
      var chk = r.querySelector(".rchk");
      var isRead = !!read[slug];
      chk.checked = isRead;
      r.classList.toggle("rrow-done", isRead);
      if (isRead) done++;
      else if (!firstUnread) firstUnread = r;
    }});
    var total = rows.length;
    var pct = total ? Math.round(done / total * 100) : 0;
    document.getElementById("rDone").textContent = done;
    document.getElementById("rPct").textContent = pct + "%";
    document.getElementById("rBar").style.width = pct + "%";
    var cbox = document.getElementById("continueBox");
    if (firstUnread){{
      var label = firstUnread.querySelector(".rrow-n").textContent;
      cbox.style.display = "block";
      cbox.innerHTML = '<div class="muted" style="margin-bottom:8px">Continue where you left off</div>' +
        '<a class="btn" href="' + firstUnread.dataset.href + '">Read ' + label + ' \\u2192</a>';
    }} else if (total) {{
      cbox.style.display = "block";
      cbox.innerHTML = '<div class="muted">You\\u2019re caught up \\u2014 every published chapter is ' +
        'read. Come back when the next one lands.</div>';
    }}
  }}
  rows.forEach(function(r){{
    r.querySelector(".rchk").addEventListener("change", function(e){{
      mtlibSetRead(r.dataset.slug, e.target.checked);
      render();
    }});
  }});
  document.getElementById("resetLink").addEventListener("click", function(e){{
    e.preventDefault();
    if (confirm("Reset your reading progress on this device?")){{
      try{{ localStorage.removeItem("mtlib_read"); }}catch(err){{}}
      render();
    }}
  }});
  render();
}})();
</script>"""
    out = page(f"My Reading — {SITE_NAME}", body, active="reading",
               desc="Track your own progress through The MisterLibrarian Bible Project, chapter by "
                    "chapter — kept privately in your browser, no account needed.")
    open(os.path.join(OUT, "reading.html"), "w", encoding="utf-8").write(out)


def build_index(chapters):
    # "Newest" = most-recently-published = the LAST panel in the source file
    # (PUBLISH_ORDER), NOT CHAPTERS[-1]: CHAPTERS is in canonical order, so its tail is
    # the canonically-last chapter (currently Exodus), not the one shipped most recently.
    # Both the button and the card grid (newest-first) follow publish order so they agree.
    _by_slug = {slug: (slug, book, num, teaser) for slug, book, num, teaser in CHAPTERS}
    pub = [_by_slug[s] for s in PUBLISH_ORDER if s in _by_slug] or list(CHAPTERS)
    latest = pub[-1]
    cards = "".join(
        f'<a class="card" href="{chapter_filename(book, num)}"><div class="card-t">{book} {num}</div>'
        f'<div class="card-d">{teaser}</div></a>'
        for _, book, num, teaser in reversed(pub))
    votd_json = json.dumps(votd_entries(chapters), ensure_ascii=False).replace("</", "<\\/")
    ch_json = json.dumps(
        [{"slug": slug, "label": f"{book} {num}", "href": chapter_filename(book, num)}
         for slug, book, num, _ in CHAPTERS])
    body = f"""<section class="hero">
  <h1>A new translation of the Bible,<br/>made one chapter at a time.</h1>
  <div class="hero-grid">
  <div class="hero-copy">
  <p>Welcome. This project translates the Bible into modern English directly from the original Hebrew —
  the Masoretic Text, reproduced verse-by-verse alongside the new rendering so every choice can be checked
  against the source. Beneath each chapter sit <strong>translator's notes, verse by verse</strong>,
  explaining each decision and comparing it against seven landmark versions: the NIV, the KJV, the
  Douay-Rheims, The Living Bible, the 1599 Geneva Bible, the American Standard Version, and the New World
  Translation.</p>
  <p>No verse is smoothed over, no difficulty hidden: where the Hebrew puns, the translation puns or the
  notes confess it can't; where the text is uncertain or the manuscripts disagree, the notes say so plainly.
  The work advances one chapter per sitting — follow along from the beginning, or jump in at the newest
  chapter.</p>
  <div class="hero-cta">
    <a class="btn" href="genesis-1.html">Start at Genesis 1</a>
    <a class="btn btn-2" href="{chapter_filename(latest[1], latest[2])}">Newest: {latest[1]} {latest[2]}</a>
  </div>
  </div>
  <figure class="hero-fig">
    <img src="img/great-isaiah-scroll.jpg" width="1040" height="639" loading="lazy"
      alt="Two columns of the Great Isaiah Scroll from Qumran — dense hand-written Hebrew on warm parchment, with an ancient crack running between the sheets"/>
    <figcaption>
      <span class="ms-name">The Great Isaiah Scroll — Qumran, 2nd century BC</span>
      Two columns of the <em>Great Isaiah Scroll</em> (1QIsa<sup>a</sup>), from Cave 1 at Qumran — the oldest
      complete copy of any book of the Bible, and the treasure the Shrine of the Book in Jerusalem was built
      to house.
      <span class="ms-credit">Photograph: Ardon Bar Hama — via
      <a href="https://commons.wikimedia.org/wiki/File:Great_Isaiah_Scroll.jpg" rel="noopener">Wikimedia Commons</a> · public domain (detail)</span>
    </figcaption>
  </figure>
  </div>
</section>

<div class="panel votd" id="votd">
  <div class="votd-label">Verse of the Day · from this translation</div>
  <div class="votd-q" id="votdText">—</div>
  <div class="votd-ref" id="votdRef"></div>
  <div class="votd-blurb" id="votdBlurb"></div>
  <a class="votd-link" id="votdLink" href="#">Read it in context →</a>
</div>

<div class="panel" id="continueBox" style="display:none;margin-top:14px"></div>

<h2>Chapters — newest first</h2>
<div class="cardgrid">
{cards}
</div>

<h2>From the desk</h2>
<div class="cardgrid">
  <a class="card" href="old-testament.html"><div class="card-t">\U0001F4DC The Old Testament</div>
  <div class="card-d">The Hebrew Scriptures: what the Tanakh is and how it's arranged, the Masoretic text and its scribal marks, the older witnesses, and why the Name is rendered Jehovah.</div></a>
  <a class="card" href="new-testament.html"><div class="card-t">\U0001F4DC The New Testament</div>
  <div class="card-d">Crossing from Hebrew into Greek: the critical text, the manuscript apparatus behind the translation, and the method for the Greek Scriptures.</div></a>
  <a class="card" href="reading.html"><div class="card-t">\U0001F4D7 My Reading</div>
  <div class="card-d">Track your own progress through the translation, chapter by chapter — kept privately in your browser.</div></a>
  <a class="card" href="ask.html"><div class="card-t">\U0001F4D6 Ask Mr. Librarian</div>
  <div class="card-d">Reader questions answered — was the Word "God" or "a god" (John 1:1 and the deity of Christ), and why the Book of Enoch isn't included.</div></a>
  <a class="card" href="about.html"><div class="card-t">ℹ️ About the project</div>
  <div class="card-d">The method, the seven-version shelf, and what "essentially literal, modern register" means here.</div></a>
</div>

<script>
var MTLIB_VOTD = {votd_json};
var MTLIB_CHAPTERS = {ch_json};
(function(){{
  if (!MTLIB_VOTD.length) return;
  var now = new Date();
  var doy = Math.floor((now - new Date(now.getFullYear(), 0, 0)) / 86400000);
  var v = MTLIB_VOTD[doy % MTLIB_VOTD.length];
  document.getElementById("votdText").textContent = "\\u201c" + v.text + "\\u201d";
  document.getElementById("votdRef").textContent = "\\u2014 " + v.ref;
  document.getElementById("votdBlurb").textContent = v.blurb;
  document.getElementById("votdLink").href = v.href;
}})();
(function(){{
  var read = mtlibGetRead();
  var done = 0, firstUnread = null;
  MTLIB_CHAPTERS.forEach(function(c){{
    if (read[c.slug]) done++;
    else if (!firstUnread) firstUnread = c;
  }});
  var cbox = document.getElementById("continueBox");
  if (done === 0) return;
  cbox.style.display = "block";
  if (firstUnread){{
    cbox.innerHTML = '<div class="muted" style="margin-bottom:8px">Continue where you left off</div>' +
      '<a class="btn btn-2" href="' + firstUnread.href + '">Read ' + firstUnread.label + ' \\u2192</a>';
  }} else {{
    cbox.innerHTML = '<div class="muted">You\\u2019re caught up on every published chapter \\u2014 nice ' +
      'work. Come back when the next one lands, or revisit your <a href="reading.html">reading progress</a>.</div>';
  }}
}})();
</script>"""
    out = page(SITE_NAME, body, active="home",
               desc="A fresh translation of the Bible into modern English, made from the original Hebrew "
                    "one chapter at a time, with verse-by-verse notes comparing seven landmark versions.")
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(out)


def build_about():
    body = f"""<h1 class="pagetitle">About the project</h1>
<div class="panel prose">
  <p><strong>What this is.</strong> A fresh translation of the Bible into modern English, made one chapter
  at a time, directly from the <strong>Masoretic Text</strong> — the traditional Hebrew text of the Bible,
  as printed at <a href="https://mechon-mamre.org" rel="noopener">Mechon-Mamre</a>. The pointed Hebrew is
  reproduced verse-by-verse on every chapter page (a Hide&nbsp;Hebrew toggle is there for English-only
  reading), so every choice is checkable against the source.</p>
  <p><strong>The philosophy: essentially literal, in a natural modern register.</strong> Keep the Hebrew's
  word-plays, repetitions and structure wherever English can bear them; where it can't, say so in the notes
  rather than silently smoothing it over. Where the text is genuinely uncertain — a word that appears once
  in the whole Bible, a line the ancient manuscripts disagree on — the notes say that too, instead of
  pretending to a confidence the evidence doesn't support.</p>
  <p><strong>The seven-version shelf.</strong> Below every chapter, verse-by-verse translator's notes
  compare this translation's choices against seven landmark versions, chosen to span the full range of
  translation philosophy and history:</p>
  <div class="shelf">
    <div class="sv"><b>NIV</b> New International Version (2011) — committee, dynamic-leaning.</div>
    <div class="sv"><b>KJV</b> King James Version (1611) — the classic; built on Tyndale and Geneva.</div>
    <div class="sv"><b>DRB</b> Douay-Rheims (Challoner) — English of the Latin Vulgate; the historic Catholic text.</div>
    <div class="sv"><b>TLB</b> The Living Bible (1971) — Kenneth Taylor's one-man paraphrase.</div>
    <div class="sv"><b>GNV</b> Geneva Bible (1599) — the Reformation study Bible, before the KJV.</div>
    <div class="sv"><b>ASV</b> American Standard Version (1901) — famously literal.</div>
    <div class="sv"><b>NWT</b> New World Translation (1984) — the Watch Tower Society's translation.</div>
  </div>
  <p style="margin-top:14px"><strong>Honesty note.</strong> This translation is made by Claude (Anthropic's
  AI) working from the pointed Hebrew, guided and edited by Mr. Librarian. It is a study rendering, not the
  product of a translation committee — treat the notes as the argument for each choice, and check them
  against the shelf. Quotations from copyrighted versions are kept to brief phrases for comparison; the
  KJV, Geneva, Douay-Rheims, and ASV are public domain.</p>
  <p><strong>The name.</strong> A librarian's job is to catalogue, source, and compare — not to preach.
  That's the ethos here: every claim sourced, every alternative shown, disagreements between traditions
  presented rather than settled.</p>
  <p><strong>Privacy.</strong> The <a href="index.html">home page</a>'s Verse of the Day and the
  <a href="reading.html">My Reading</a> progress tracker both run entirely in your own browser (a bit of
  localStorage) — there's no login and no server-side record of what you've read; clear your browser
  data and it's gone, same as any other private note to yourself. The one thing that <em>is</em> measured
  is an anonymous, cookie-less visit count — no personal data, no cross-site tracking, nothing sold,
  no consent banner needed because none of that happens.{" That's it, live, right below." if GOATCOUNTER_CODE else ""}</p>
  {_stats_box()}
</div>"""
    out = page(f"About — {SITE_NAME}", body, active="about",
               desc="How the MisterLibrarian Bible Project works: translated from the Masoretic Hebrew, "
                    "essentially literal in a modern register, compared against seven landmark versions.")
    open(os.path.join(OUT, "about.html"), "w", encoding="utf-8").write(out)


def build_old_testament():
    """The heading page for the Old Testament / Hebrew Scriptures — the front door to
    the bulk of the project: what the Hebrew Bible is and how it is arranged, the
    Masoretic source text and its scribal apparatus, the witnesses the notes consult,
    an honest account of how we know the text is reliable, and the translation's
    signature decision — rendering the divine Name as Jehovah. A living page: edit this
    function as the method for the Hebrew Scriptures develops."""
    body = """<h1 class="pagetitle">The Old Testament</h1>
<div class="nt-intro">
<p class="lede nt-lede">This is where the project begins — in the <strong>Hebrew of the Tanakh</strong>, the
Scriptures Jesus and the apostles called simply "the Law and the Prophets." Most of this library's work lives
here: the five books of Moses, the histories, the poetry and wisdom, and the prophets. This page is the
reference desk for the Hebrew Scriptures — what the collection is and how it is arranged, the text we translate
from and the scribal marks we keep, the older witnesses the notes weigh, and the one decision that marks nearly
every page: rendering the divine Name as <strong>Jehovah</strong>, not "the LORD." It's a <strong>living
page</strong> — updated as the method takes shape.</p>

<figure class="ms-figure">
  <img src="img/great-isaiah-scroll.jpg" width="1040" height="639" loading="lazy"
    alt="Two columns of the Great Isaiah Scroll from Qumran — dense hand-written Hebrew on warm parchment, with an ancient crack running between the sheets"/>
  <figcaption>
    <span class="ms-name">The Great Isaiah Scroll — Qumran, 2nd century BC</span>
    Two columns of the <em>Great Isaiah Scroll</em> (1QIsa<sup>a</sup>), from Cave 1 at Qumran — the oldest
    complete copy of any book of the Bible, roughly a thousand years older than the medieval manuscripts behind
    the standard Hebrew text, and yet word-for-word almost the same.
    <span class="ms-credit">Photograph: Ardon Bar Hama — via
    <a href="https://commons.wikimedia.org/wiki/File:Great_Isaiah_Scroll.jpg" rel="noopener">Wikimedia Commons</a> · public domain (detail)</span>
  </figcaption>
</figure>

<div class="panel prose nt-panel1">
  <h2 style="margin-top:2px">What it is, and how it's arranged</h2>
  <p><strong>Two names for one library.</strong> Christians call it the <strong>Old Testament</strong>; the
  Jewish tradition calls it the <strong>Tanakh</strong> — an acronym for its three parts: <em>Torah</em> (the
  Law), <em>Nevi'im</em> (the Prophets), and <em>Ketuvim</em> (the Writings). It is the same collection of
  Scriptures, counted two ways: <strong>39 books</strong> in the common Christian reckoning, or
  <strong>24</strong> in the Jewish, which groups the material differently (the twelve Minor Prophets are one
  scroll, "The Twelve"; Samuel, Kings, and Chronicles are one book each). Written over roughly a thousand years,
  almost entirely in Hebrew, with a few passages in Aramaic (parts of Daniel and Ezra).</p>
  <p><strong>The order differs, too.</strong> The Jewish Tanakh runs Law → Prophets → Writings and ends on
  Chronicles, looking toward a return. The Christian Old Testament regroups the same books by kind — Law,
  History, Poetry and Wisdom, Prophets — and ends on Malachi, looking forward to a coming messenger. This
  translation follows the familiar Christian book-order for navigation, while noting the Hebrew arrangement
  where it matters (the placement of Daniel among the Writings, for instance).</p>
</div>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">The source text — the Masoretic Text</h2>
  <p>The Hebrew is translated from one remarkably stable traditional text: the <strong>Masoretic Text</strong>,
  the edition fixed and safeguarded by the <em>Masoretes</em>, generations of Jewish scribe-scholars working
  from roughly the 7th to the 10th centuries AD. Hebrew was first written with consonants only; the Masoretes
  added, above and below the ancient letters, a precise system of <strong>vowel points</strong> and
  <strong>cantillation marks</strong> (the <em>te'amim</em>, which double as musical and punctuation signs) —
  preserving not just the letters but exactly how the text was to be read and chanted. Their standardization was
  so thorough that medieval manuscripts a continent apart agree letter for letter.</p>
  <p>This project translates the digital Hebrew of <strong>Mechon-Mamre</strong> (the Leningrad/Aleppo
  tradition), and it deliberately keeps the scribes' own marks visible rather than smoothing them away:</p>
  <ul class="prose-list">
    <li>The scroll's paragraph breaks — <strong>petuchah</strong> <span class="hebph">{פ}</span> ("open") and
    <strong>setumah</strong> <span class="hebph">{ס}</span> ("closed") — are shown where the text marks them.</li>
    <li><strong>Ketiv / qere</strong> — the places where the tradition <em>writes</em> one thing (ketiv) and
    <em>reads</em> another (qere) are kept and noted, not silently harmonized.</li>
    <li>The famous <strong>oddities of the letters</strong> are preserved and explained — the shrunken
    <strong>small aleph</strong> that opens Leviticus (<a href="leviticus-1.html#v1">Vayiqra</a>, 1:1), the two
    <strong>inverted nuns</strong> that bracket the Song of the Ark in Numbers (10:35–36), the oversized and
    dotted letters elsewhere: ancient scribal signals the tradition has carried for two millennia.</li>
  </ul>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">The witnesses the notes consult</h2>
  <p>The Masoretic Text is the base, but it is not the only ancient copy. Where a reading is disputed the notes
  weigh the older and independent witnesses — always <strong>noted, never silently adopted</strong>
  (the Masoretic reading stands unless the note argues otherwise):</p>
  <div class="shelf">
    <div class="sv"><b>The Dead Sea Scrolls</b> (c. 250 BC – 68 AD) — the Qumran manuscripts, a thousand years
    older than the medieval Masoretic codices; the Great Isaiah Scroll above is the showpiece.</div>
    <div class="sv"><b>The Septuagint (LXX)</b> — the pre-Christian Greek translation of the Hebrew, quoted
    constantly in the New Testament; consulted through the printed <em>critical</em> editions (Göttingen,
    Rahlfs-Hanhart), since the great Greek codices (Vaticanus, Sinaiticus) are damaged in early Genesis.</div>
    <div class="sv"><b>The Samaritan Pentateuch</b> — the Torah as preserved by the Samaritan community in its
    own script, an independent line of transmission.</div>
    <div class="sv"><b>The Targums</b> — the ancient Aramaic translations-with-paraphrase (Onkelos, Jonathan),
    a window on how the text was understood in the synagogue.</div>
    <div class="sv"><b>The Peshitta</b> — the Syriac (Aramaic) translation, an early Eastern-church witness.</div>
    <div class="sv"><b>The Vulgate</b> — Jerome's Latin, made partly from the Hebrew of his day; it is exactly
    what the <strong>Douay-Rheims</strong> on our seven-version shelf renders into English.</div>
  </div>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">How do we know the Hebrew text is reliable?</h2>
  <p>The worry is natural: if the oldest complete medieval manuscripts of the Masoretic Text date from around
  the 10th–11th centuries AD, how do we know they preserve what was written a thousand years and more before?
  Two things answer it.</p>
  <ul class="prose-list">
    <li><strong>The Masoretes were fanatical copyists.</strong> They counted the letters of each book, marked
    its middle letter and middle word, and recorded the tally in the margins, so that a single dropped letter
    would betray itself. Their whole craft was built to transmit an already-fixed text without drift — and it
    worked: their manuscripts agree with one another to an astonishing degree.</li>
    <li><strong>The Dead Sea Scrolls let us check.</strong> When the Qumran scrolls surfaced in 1947, they
    handed us Hebrew Bible manuscripts a <em>thousand years older</em> than anything previously known. The
    verdict, most famously on the Great Isaiah Scroll: substantially the same text. The differences are mostly
    spelling and small variants; the book you read is the book they read.</li>
  </ul>
  <p>Honesty requires the other half, too. In a few books the ancient <strong>versions preserve a genuinely
  different edition</strong> — the Septuagint of Jeremiah, for instance, is about a seventh shorter than the
  Hebrew and arranged differently, and some Qumran copies match it; the Samaritan Torah has its own harmonizing
  expansions. This translation follows the Masoretic Text but <strong>flags such divergences where they matter</strong>,
  laying out the readings with their pedigrees rather than pretending the tradition is seamless.</p>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">The Name: why this translation says "Jehovah"</h2>
  <p>The defining decision of this Old Testament is what to do with the personal name of God. Some 6,800 times
  the Hebrew writes four consonants — <span class="hebph" dir="rtl">יהוה</span>, <strong>YHWH</strong>, the
  <em>Tetragrammaton</em> ("four letters"). Out of reverence, the Jewish reading tradition long ago stopped
  pronouncing it, saying <em>Adonai</em> ("my Lord") aloud instead; the Masoretes marked this by pointing the
  written YHWH with the vowels of Adonai — a standing "read it as Lord" instruction (a <em>qere perpetuum</em>).
  Following that tradition, <strong>most English Bibles print "the LORD"</strong> in small capitals wherever the
  name stands — a title in place of the Name.</p>
  <p>This translation does the opposite: it <strong>keeps the Name visible</strong>, rendering it
  <strong>Jehovah</strong> — the traditional English form (the ASV and the New World Translation use it too;
  Tyndale and the King James translators knew it). The form <em>Jehovah</em> itself comes from reading YHWH's
  consonants with Adonai's borrowed vowels; scholars reconstruct the original pronunciation as
  <em>Yahweh</em>. This library uses "Jehovah" as the established English name, not as a claim about exact
  pronunciation — and it never prints "the LORD" for the Name, not even inside a quotation, so the reader
  always sees where the personal name of God actually stands. That single choice shapes the whole translation,
  and it is the Hebrew Scriptures' counterpart to the neutrality problem the Greek Scriptures open on.</p>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">What carries through — the method</h2>
  <p>Everything that makes this a librarian's Bible and not a preacher's holds from the first verse of Genesis:
  an <strong>essentially literal</strong> rendering in natural modern English (<em>vault</em>, not "firmament";
  <em>side</em>, not "rib"); the <strong>seven-version shelf</strong> — NIV, KJV, Douay-Rheims, Living Bible,
  1599 Geneva, ASV, and NWT — compared under every chapter; the <strong>neutrality rule</strong>, laying out
  contested readings (the sons of God in Genesis 6, the date of the Exodus, the authorship of the Torah) with
  their pedigrees and casting no vote; the <strong>echo system</strong>, flagging a word or motif when it first
  appears and paying it off when it returns; and the <strong>honesty habits</strong> — hapax and uncertain
  words called uncertain, anachronisms and source-critical seams shown, not sanded. The Library grows a
  dictionary, an encyclopedia, an atlas, a chronology, and a concordance built from this translation's own
  English as the chapters arrive.</p>
</div>

<div class="panel">
  <p style="margin:0 0 6px"><strong>The Hebrew Scriptures begin at the beginning — Genesis 1.</strong></p>
  <p class="muted" style="margin:0 0 12px">"In the beginning God created the heavens and the earth." From the
  seven days and the garden through the flood, Babel, and the call of Abraham, the first book lays the ground
  the whole Bible builds on. Browse everything published so far in the Table of Contents.</p>
  <a class="btn" href="genesis-1.html">Read Genesis 1 →</a>
  <a class="btn" href="toc.html" style="margin-left:8px">Table of Contents →</a>
</div>"""
    out = page(f"The Old Testament — {SITE_NAME}", body, active="ot",
               desc="Introducing the Old Testament (the Hebrew Scriptures / Tanakh) in The MisterLibrarian "
                    "Bible Project: what the Hebrew Bible is and how it is arranged, the Masoretic source text "
                    "and its scribal apparatus, the witnesses the notes weigh (the Dead Sea Scrolls, the "
                    "Septuagint, the Samaritan Pentateuch, the Targums), how we know the text is reliable, and "
                    "why the translation renders the divine Name as Jehovah.")
    open(os.path.join(OUT, "old-testament.html"), "w", encoding="utf-8").write(out)


def build_new_testament():
    """The heading page for the New Testament / Greek Scriptures — an intro to the
    crossing from Hebrew into Greek, the full source-text apparatus the translation
    will consult, an honest account of how a body of thousands of manuscripts is
    actually weighed, and what carries over from the Hebrew chapters. A living page:
    edit this function as the method for the Greek Scriptures develops."""
    body = """<h1 class="pagetitle">The New Testament</h1>
<div class="nt-intro">
<p class="lede nt-lede">Here the project crosses a threshold — out of the Hebrew of the Tanakh and into the
<strong>Koine Greek of the New Testament</strong>, what a number of traditions call the
<em>Greek Scriptures</em>. The ethos doesn't change; the language, the manuscripts, and one or two famous
arguments do. This page is the reference desk for that crossing: the texts we translate from, how a body of
roughly 5,800 Greek manuscripts is actually weighed, and what carries over from the Hebrew chapters. It's a
<strong>living page</strong> — updated as the method for the Greek Scriptures takes shape.</p>

<figure class="ms-figure">
  <img src="img/p52-john-rylands.jpg" width="960" height="1280" loading="lazy"
    alt="Papyrus 52 (P52), the Rylands fragment — a scrap of the Gospel of John 18:31–33 in Greek, c. 125–150 CE"/>
  <figcaption>
    <span class="ms-name">P52 — the Rylands fragment</span>
    A scrap of <em>John 18:31–33</em> in Greek, c. 125–150 CE — the oldest surviving piece of any New
    Testament book, and part of the very Gospel this phase begins with.
    <span class="ms-credit">John Rylands Library, Manchester — via
    <a href="https://commons.wikimedia.org/wiki/File:Manchester,_John_Rylands_Library_Ms_Greek_P_457_(Papyrus_52)_recto_John_18,_31-33.jpg" rel="noopener">Wikimedia Commons</a> · public domain</span>
  </figcaption>
</figure>

<div class="panel prose nt-panel1">
  <h2 style="margin-top:2px">What changes, and what stays</h2>
  <p><strong>What changes.</strong> The source language is now Greek, not Hebrew. And the source <em>text</em>
  works differently: the Hebrew chapters translate one remarkably standardized traditional text (the Masoretic
  Text). The Greek New Testament has no single such text — instead there are thousands of manuscripts, the
  oldest on papyrus from within a century or so of the writing, and the base for translation is a
  <strong>critical text</strong> that weighs them against one another. One more thing changes: the
  <strong>words of Jesus will be set in red</strong>, the convention this library has promised since Genesis.</p>
  <p><strong>What stays.</strong> Everything that makes this a librarian's Bible and not a preacher's.
  Essentially literal, in a natural modern register. The same <strong>seven-version shelf</strong> under every
  chapter — the NIV, KJV, Douay-Rheims, Living Bible, 1599 Geneva, ASV, and NWT all carry the New Testament,
  so the comparison continues unbroken. The <strong>neutrality rule</strong>: where traditions divide, the
  notes give the readings with their pedigrees and <em>don't vote</em>. The <strong>echo system</strong> —
  and here it grows a new dimension, because the New Testament quotes the Old on nearly every page, so the
  cross-references will finally run between books. And the honesty habits: where a word is uncertain or the
  manuscripts disagree, the notes say so plainly instead of pretending to a confidence the evidence can't
  support.</p>
</div>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">The source texts</h2>
  <p>The base for translation is the <strong>critical Greek New Testament</strong> in the Nestle tradition —
  an <em>eclectic</em> text that doesn't reprint any one manuscript but reconstructs, variant by variant, the
  earliest recoverable reading, resting mainly on the oldest Alexandrian witnesses. Alongside it the notes
  consult the printed critical editions and the primary manuscripts behind them:</p>

  <h3>Printed critical editions</h3>
  <div class="shelf">
    <div class="sv"><b>Nestle</b> Novum Testamentum Graece, 18th ed. (1948) — the eclectic Greek text in the
    line that became the modern standard.</div>
    <div class="sv"><b>Bover</b> José María Bover's critical Greek New Testament — a Catholic scholar's
    independent edition.</div>
    <div class="sv"><b>Merk</b> Augustinus Merk's Novum Testamentum Graece et Latine — Greek with the Latin
    alongside.</div>
  </div>

  <h3>The great uncials — the 4th-century codices</h3>
  <div class="shelf">
    <div class="sv"><b>Vaticanus (B / 03)</b> mid-4th century (c. 325–350) — one of the two great uncial
    codices, and a chief pillar of the Alexandrian text.</div>
    <div class="sv"><b>Sinaiticus (א / 01)</b> mid-4th century (c. 330–360), found at St Catherine's
    Monastery on Sinai — a nearly complete New Testament.</div>
  </div>

  <h3>The early papyri — 2nd and 3rd centuries</h3>
  <p>Older still than the codices, and the reason we can say the Alexandrian text is early and not a late
  editorial invention:</p>
  <div class="shelf">
    <div class="sv"><b>P52</b> (the Rylands fragment) — a scrap of <em>John 18</em>, c. 125–150, the oldest
    known fragment of any New Testament book.</div>
    <div class="sv"><b>P66</b> (Bodmer II) — a substantial portion of <em>John</em>, c. 200.</div>
    <div class="sv"><b>P75</b> (Bodmer XIV–XV) — <em>Luke and John</em>, c. 175–225, textually almost
    identical to Vaticanus though ~150 years older, which is how we know that text isn't a late recension.</div>
    <div class="sv"><b>P46</b> (Chester Beatty II) — the <em>letters of Paul</em>, c. 200.</div>
  </div>

  <h3>The early versions</h3>
  <p>Independent early translations corroborate the Greek from the outside: the <strong>Latin</strong> — the
  Vulgate, which is exactly what the Douay-Rheims on our shelf renders into English — along with the
  <strong>Coptic</strong> (Egyptian) and <strong>Syriac</strong> traditions. When a Greek reading turns up
  already carried in a 3rd- or 4th-century version in another language, that is a second, independent vote for
  its antiquity.</p>
  <p class="muted" style="margin-top:10px">A practical note: you weigh the witnesses that actually preserve
  the book in front of you. The John papyri (P52, P66, P75) are gold for the Gospel of John and silent about
  Paul; P46 is the reverse. And though the two great codices carry the Greek Old Testament too, both are
  missing early Genesis — Vaticanus begins at Genesis 46:28 — which is why the Hebrew chapters lean on the
  printed critical Septuagint rather than on B and א directly.</p>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">Isn't weighing thousands of manuscripts impossible?</h2>
  <p>It sounds impossible — around 5,800 Greek manuscripts, plus thousands more in Latin, lectionaries, and
  quotations in the early writers, and somewhere near 400,000 points of variation among them. But you never
  weigh them flat, one vote each, and four things collapse the problem down to something a person can hold:</p>
  <ul class="prose-list">
    <li><strong>Manuscripts cluster into families, so you weigh <em>streams</em>, not copies.</strong> The
    overwhelming majority are late, medieval copies of copies, and they group into a few text-types —
    Alexandrian (the earliest, P75 and the great codices), Byzantine (the vast late majority), and Western. A
    thousand near-identical late copies count as roughly one witness with a thousand fingerprints.</li>
    <li><strong>Almost every variant is trivial.</strong> Spelling, a slip of the pen, a swapped word order
    (Greek is inflected, so order rarely changes the meaning). Of all those variants, the ones that are both
    <em>meaningful and viable</em> — a real reading, with real support, that changes the sense — are well
    under one percent; the ones that would actually alter an English translation are fewer still.</li>
    <li><strong>The weighing is principled, not brute force.</strong> Two questions decide each real variant:
    which reading best <em>explains how the others arose</em> (a scribe is likelier to smooth a hard reading
    than to roughen an easy one), and which has the <em>oldest and most widely spread</em> support. This is
    what the critical editions above have already carried out.</li>
    <li><strong>The genuinely combinatorial part is now done by computer.</strong> The modern critical editions
    use a method called the CBGM to model the family tree of variants across the whole tradition — precisely
    the part that would be impossible by hand.</li>
  </ul>
  <p>So the honest bottom line: you don't adjudicate 5,800 manuscripts — you read a critical apparatus that
  has already done the weighing, and it shows you the handful of variants that matter for each verse, with
  their pedigrees. The amount of text in real doubt is small, and the few large disputed passages are famous
  and openly flagged in every serious edition — the longer ending of Mark (16:9–20), the woman caught in
  adultery (John 7:53–8:11), the "Johannine Comma" (1 John 5:7–8). Nothing hidden; the notes will mark them
  when we reach them.</p>
</div>

<div class="panel prose">
  <h2 style="margin-top:2px">The first test: John 1:1</h2>
  <p>The New Testament opens, fittingly, on the project's hardest neutrality problem. The Gospel of John begins
  <span class="greek">Ἐν ἀρχῇ ἦν ὁ λόγος</span> — "In the beginning was the Word" — deliberately echoing the
  first words of Genesis, and then reaches its famous crux: <span class="greek">καὶ θεὸς ἦν ὁ λόγος</span>.
  Most versions render it "and the Word was God"; the New World Translation reads "and the Word was <em>a
  god</em>." That difference turns on a fine point of Greek grammar — a predicate noun with no article, standing
  before its verb — and it is exactly the kind of place this project exists to handle honestly. When John 1
  is posted, the note will lay out the grammar and the readings <strong>with their pedigrees, and won't cast a
  vote</strong>. That is the method the whole Old Testament has followed, carried across the threshold intact.</p>
</div>

<div class="panel">
  <p style="margin:0 0 6px"><strong>The Greek Scriptures begin with the Gospel of John.</strong></p>
  <p class="muted" style="margin:0 0 12px">Its first chapter — the Prologue, John the Baptist's testimony, and
  the calling of the first disciples — is now live, the first to arrive with the full apparatus above behind it:
  from the Prologue's "was God / a god" to the manuscript decision at John 1:18, where the earliest papyri decide
  the reading.</p>
  <a class="btn" href="john-1.html">Read John 1 →</a>
</div>"""
    out = page(f"The New Testament — {SITE_NAME}", body, active="nt",
               desc="Introducing the New Testament (the Greek Scriptures) in The MisterLibrarian Bible "
                    "Project: the critical Greek text and manuscript apparatus behind the translation "
                    "(Vaticanus, Sinaiticus, the early papyri P52/P66/P75/P46), how thousands of manuscripts "
                    "are weighed, and what carries over from the Hebrew.")
    open(os.path.join(OUT, "new-testament.html"), "w", encoding="utf-8").write(out)


def build_ask_enoch():
    body = """<div class="askbar"><a href="ask.html">← Ask Mr. Librarian</a></div>
<h1 class="pagetitle">Why isn't the Book of Enoch in this translation?</h1>

<div class="qbox">
  <div class="qlabel">A reader asked</div>
  <p>"Why did you not include the Book of Enoch in your translation of the Bible?"</p>
</div>

<div class="panel prose">
  <p>This project's source text has been the <strong>Masoretic Hebrew Bible</strong> — the Tanakh, pointed
  Hebrew and all — since the very first line of the very first chapter. The Book of Enoch was never part of
  that corpus to begin with. There's no Masoretic Hebrew text of Enoch to translate from; it doesn't survive
  complete in Hebrew at all. The only complete text is in Ge'ez (classical Ethiopic), with fragments of the
  original Aramaic and some Greek turning up among the Dead Sea Scrolls and elsewhere. So leaving it out
  wasn't a judgment call about whether it belongs — it was outside this project's stated method before the
  question of canon ever came up.</p>
  <p>The broader canon question is genuinely interesting, though. Enoch isn't in the Jewish canon, the
  Protestant 66-book list this project's Table of Contents is built around, or even the Catholic
  Deuterocanon (the extra books the Douay-Rheims tradition includes — Tobit, Judith, Maccabees, and so on —
  don't include it either). The one tradition where it actually <em>is</em> canonical scripture is the
  <strong>Ethiopian Orthodox Tewahedo Church</strong>, which is often the detail people miss — it's not that
  Enoch was universally rejected, it's that one major, ancient Christian tradition kept it and the others
  didn't.</p>
  <p>And it wasn't obscure or forgotten in the meantime. Multiple Aramaic copies of it turned up at Qumran
  among the Dead Sea Scrolls, so it was clearly in real circulation in Second Temple Judaism. And the New
  Testament itself references it — the epistle of <strong>Jude, verses 14–15</strong>, cites "Enoch, the
  seventh from Adam" prophesying judgment, language that traces straight back to Enoch's text. So whatever
  the reasons different communities eventually settled their canons the way they did (and scholars don't
  agree on one tidy explanation — theories range from its pseudepigraphal authorship claim, to discomfort
  with its angelology and cosmology, to it simply falling outside the criteria later rabbinic and church
  authorities used), it was clearly read and taken seriously by people in a position to know it well.</p>
  <p>Two places in this translation touch Enoch's world directly: the man himself — "Enoch walked with God,
  and then he was not there, for God took him" — appears in <a href="genesis-5.html#v5-21">Genesis
  5:21–24</a>, the two-verse mystery from which the later book grew; and the "sons of God" episode the Book
  of Enoch expands so dramatically opens <a href="genesis-6.html#v6-1">Genesis 6</a>.</p>
  <p>If this project ever extends to it, that's a real possibility — but it would be a different kind of
  undertaking than the Hebrew chapters posted so far, since it means working from Ge'ez and the
  Aramaic/Greek fragments instead of pointed Masoretic Hebrew, and being upfront that it sits outside the
  Tanakh and the Protestant canon this translation has otherwise followed.</p>
</div>

<div class="panel" style="margin-top:14px">
  <p class="muted" style="margin:0 0 12px">Have a question about the project, a translation choice, or
  what's coming next? Reader questions are exactly how this series grows — the next one could be yours.</p>
  <a class="btn" href="contact.html">✉️ Ask Mr. Librarian a question</a>
</div>"""
    out = page(f"Ask Mr. Librarian: the Book of Enoch — {SITE_NAME}", body, active="ask",
               desc="Why the Book of Enoch isn't part of this Bible translation: the Masoretic source "
                    "text, the canon question, the Ethiopian exception, and the Dead Sea Scrolls.")
    open(os.path.join(OUT, "ask-enoch.html"), "w", encoding="utf-8").write(out)


def build_ask_newton():
    """Ask Mr. Librarian: did Isaac Newton write about the Bible? Presents his three
    public-domain biblical works, their genuine fit with this site (Daniel/Revelation,
    the Johannine Comma on the NT apparatus page, the Chronology), and — under the
    project's neutrality rule — handles his private anti-Trinitarianism factually,
    distinguishing his sound textual findings from his partisan doctrinal motive. The
    works themselves are archived (source/newton/ + S3) by tools/archive_newton.py."""
    body = """<div class="askbar"><a href="ask.html">← Ask Mr. Librarian</a></div>
<h1 class="pagetitle">Did Isaac Newton write about the Bible?</h1>
<h2 style="margin-top:2px">The scientist's other library — and where it touches this one</h2>

<div class="qbox">
  <div class="qlabel">A reader asked</div>
  <p>"I've heard that Isaac Newton — the gravity and calculus Newton — wrote a huge amount about the Bible and
  prophecy. Is that true? And is any of it something you'd use in this translation?"</p>
</div>

<div class="panel prose">
  <p><strong>It is true, and it is stranger than most people know.</strong> The man who wrote the
  <em>Principia</em> left behind <em>more</em> words on theology, prophecy, and church history than on physics
  and mathematics combined — on the order of a million or two, most of it never published in his lifetime and
  only fully catalogued in the last century (the Yahuda and Portsmouth papers). Newton saw no wall between the
  two studies. He believed God had written two books — the book of nature and the book of Scripture — and that
  both were coded, lawful, and open to patient decoding by the same careful mind. He read Hebrew and Greek,
  collated manuscripts, drew up chronologies, and worked over Daniel and Revelation the way he worked over the
  orbits of the planets: as a system with hidden rules, to be recovered, not invented.</p>
  <p>Three of his biblical works were printed after his death and are long out of copyright. Remarkably, all
  three land on ground this project already stands on — so yes, they are worth knowing, and we keep our own
  copies so a dead link can never lose them (see <em>"Did we use any of it?"</em> below).</p>
</div>

<h2>1. His reading of Daniel and Revelation (1733)</h2>
<div class="panel prose">
  <p><strong>"Observations upon the Prophecies of Daniel, and the Apocalypse of St. John."</strong> This is
  Newton's big published book of biblical interpretation, and it takes on exactly the two apocalyptic books this
  translation has begun — <a href="daniel-1.html">Daniel</a> and <a href="revelation-1.html">Revelation</a>. He
  read them as a <em>historicist</em>: the beasts, horns, and seals are a symbolic map of real empires and
  church history, to be matched piece by piece against the record. He treated the imagery almost as a fixed
  vocabulary — a sun for a king, a beast for a kingdom — and decoded it with the same confidence he brought to
  a physical law.</p>
  <p><strong>What to make of it.</strong> Newton is dazzling here, and dated. His historicist scheme — reading
  the prophecies as a running commentary on the rise of Rome and the medieval church — is one honorable
  tradition among several (this library lays those traditions out, with their pedigrees, in the Daniel and
  Revelation notes, and casts no vote). And a famous footnote: in a <em>separate, unpublished</em> paper Newton
  once calculated that the world could not end before the year <strong>2060</strong> — reckoning from Daniel's
  1,260 "days" read as years. It is often misreported as a doomsday prediction; his own point was the opposite.
  He was rebuking the date-setters of his day: not "the end comes in 2060," but "stop announcing it sooner —
  the arithmetic won't even allow it." A scientist's caution, aimed at zealots.</p>
</div>

<h2>2. His textual criticism — and the Johannine Comma (1754)</h2>
<div class="panel prose">
  <p><strong>"An Historical Account of Two Notable Corruptions of Scripture,"</strong> written as a private
  letter to John Locke around 1690. This is Newton at his most rigorous, and it touches this site at its most
  sensitive seam. He argues, verse by verse and manuscript by manuscript, that <em>two</em> famous
  Trinitarian proof-texts were not original but crept into the Bible later: the <strong>Johannine Comma</strong>
  (1&nbsp;John&nbsp;5:7, "there are three that bear record in heaven, the Father, the Word, and the Holy
  Ghost") and the reading of <strong>1&nbsp;Timothy&nbsp;3:16</strong> ("<em>God</em> was manifest in the
  flesh" versus "<em>he who</em> was manifest").</p>
  <p><strong>Here is the striking part: on the textual facts, Newton was right,</strong> and modern scholarship
  — of every doctrinal stripe — agrees with him. The Johannine Comma is absent from every early Greek
  manuscript and every early translation; it surfaces first in late Latin copies and is now dropped or bracketed
  by essentially all critical editions. That is precisely why this site's <a href="new-testament.html">New
  Testament introduction</a> already names the Comma among the handful of famously disputed passages the notes
  will flag when we reach them. So Newton's <em>method</em> here — weigh the oldest and widest manuscript
  witnesses, ask which reading best explains how the others arose — is the very method the Greek-Scriptures page
  describes. When 1&nbsp;John&nbsp;5 is eventually translated, his letter will be the classic witness in the
  note.</p>
</div>

<h2>3. His biblical chronology (1728)</h2>
<div class="panel prose">
  <p><strong>"The Chronology of Ancient Kingdoms Amended."</strong> Newton spent decades trying to fix the dates
  of the ancient world — Egypt, Greece, Assyria, Israel — against the biblical record and the astronomy he could
  reconstruct, arguing the standard chronologies of his day had stretched history too long. It is, in effect,
  his own version of the project behind this site's <a href="chronology.html">Chronology</a> feature: the same
  impulse to place the story on a timeline. His specific conclusions have not survived the two centuries of
  archaeology since; but the instinct — build the timeline from the sources, show your working — is a kindred
  one.</p>
</div>

<h2>The one thing to hold at arm's length</h2>
<div class="panel prose bi-debates">
  <p>There is a reason to read Newton's biblical work with care, and it would be dishonest to hide it. Privately,
  Newton was an <strong>anti-Trinitarian</strong> — an "Arian," in the old term: he held that the Father alone is
  God in the fullest sense and that the Son is subordinate. He kept it secret (it would have cost him his
  Cambridge post and worse), but it shaped what he studied. His <em>Two Notable Corruptions</em> is not
  disinterested textual criticism that happened to land on two verses — it is aimed, deliberately, at the two
  verses most used to prove the Trinity.</p>
  <p>So the honest distinction is this. Newton's <em>textual finding</em> — that the Johannine Comma is a late
  insertion — stands on its own evidence and is accepted today by scholars who hold the Trinity as firmly as any
  (the doctrine never rested on that one disputed verse). But Newton's <em>larger conclusion</em> — that the
  deity of Christ itself is a corruption — is a doctrinal position, and a contested one, exactly the terrain of
  this library's hardest question: <a href="ask-jesus-god.html">was the Word "God," or "a god"?</a> On that
  question the site does what it always does — lays out the readings with their pedigrees and does not cast a
  vote. Newton belongs in that conversation as a famous, formidable <em>witness</em> for one side; he does not
  get to be the judge, and neither do we.</p>
</div>

<h2>Did we use any of it — and where are the books?</h2>
<div class="panel prose">
  <p><strong>Where Newton already touches this site:</strong> the <a href="new-testament.html">manuscript
  apparatus page</a> flags the Johannine Comma he demolished; <a href="daniel-1.html">Daniel</a> and
  <a href="revelation-1.html">Revelation</a> are the books of his <em>Observations</em>; and the
  <a href="chronology.html">Chronology</a> is the project he attempted first. As the relevant chapters arrive, a
  Newton observation will occasionally appear in a note — clearly labelled as a voice from history, never as the
  translation's own ruling.</p>
  <p><strong>And we keep the works themselves.</strong> All three are fully public domain (Newton died in 1727),
  and this library now archives its own durable copies so they can't be lost to a broken link — mirrored the way
  we mirror the Hebrew and Greek source texts. You can read them at their homes: the
  <a href="https://www.gutenberg.org/ebooks/16878" rel="noopener">Observations on Daniel &amp; the Apocalypse</a>
  and the <a href="https://www.gutenberg.org/ebooks/15784" rel="noopener">Chronology of Ancient Kingdoms</a> at
  Project Gutenberg, and the <a href="https://archive.org/details/83824690-an-historical-account-of-two-notable-corruptions-of-scripture" rel="noopener">Two
  Notable Corruptions of Scripture</a> at the Internet Archive.</p>
  <p class="muted" style="font-size:12px">The librarian's takeaway: the most famous scientist in history spent
  his hidden hours doing something very like what this project does — sourcing, collating, comparing, and
  refusing to take a text on trust. On his best days (the manuscripts) he was decades ahead of his time; on his
  boldest (the prophecy timetable, the chronology) he over-read the evidence; and on the deepest question he
  took a side this library will not. Worth knowing, worth keeping — and worth weighing for yourself.</p>
</div>"""
    out = page(f"Did Isaac Newton write about the Bible? — {SITE_NAME}", body, active="ask",
               desc="Isaac Newton wrote more on the Bible than on physics. His Observations on Daniel and "
                    "Revelation, his textual criticism of the Johannine Comma (1 John 5:7), and his biblical "
                    "chronology — how they fit The MisterLibrarian Bible Project, his private anti-Trinitarianism "
                    "handled honestly, and where to read the public-domain works.")
    open(os.path.join(OUT, "ask-newton.html"), "w", encoding="utf-8").write(out)


ES_BOOK = {"Genesis": "Génesis", "Exodus": "Éxodo", "Leviticus": "Levítico",
           "Numbers": "Números", "Deuteronomy": "Deuteronomio", "Joshua": "Josué",
           "Judges": "Jueces", "Ruth": "Rut", "1 Samuel": "1 Samuel", "1 Kings": "1 Reyes", "1 Chronicles": "1 Crónicas", "2 Chronicles": "2 Crónicas", "2 Kings": "2 Reyes",
           "2 Samuel": "2 Samuel", "Jeremiah": "Jeremías", "Proverbs": "Proverbios",
           "Daniel": "Daniel", "Ezra": "Esdras", "Esther": "Ester", "Nehemiah": "Nehemías", "Ezekiel": "Ezequiel", "Job": "Job", "Malachi": "Malaquías", "Matthew": "Mateo",
           "Mark": "Marcos", "Luke": "Lucas", "John": "Juan", "2 John": "2 Juan",
           "3 John": "3 Juan", "Jude": "Judas", "Revelation": "Apocalipsis"}


def _es_panels():
    """Read source/es/*.html -> {slug: inner_content}. The single source of Spanish
    truth: the Spanish page build AND the English-page 'Mostrar español' toggle both
    read from here, so the two can never drift."""
    es_dir = os.path.join(OUT, "source", "es")
    out = {}
    if not os.path.isdir(es_dir):
        return out
    for fn in sorted(os.listdir(es_dir)):
        if not fn.endswith(".html"):
            continue
        raw = open(os.path.join(es_dir, fn), encoding="utf-8").read()
        m = re.search(r'id="chapter-([a-z0-9]+)">(.*?)</div><!-- /chapter-\1 -->', raw, re.S)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def inject_spanish(content, slug, es_panels):
    """Thread the Spanish verse line into an ENGLISH chapter's verses (for the
    reader's 'Mostrar español' toggle). Pulls each verse's <div class="esp">…</div>
    from the Spanish source by verse id and drops it in right after the English
    <div class="eng">…</div>. No-op for chapters with no Spanish source yet."""
    esp = es_panels.get(slug)
    if not esp:
        return content, False
    # verse id -> spanish <div class="esp">…</div> (without the trailing notelink)
    es_by_v = {}
    for m in re.finditer(r'id="(v[\w-]+)".*?(<div class="esp">.*?</div>)', esp, re.S):
        line = re.sub(r'<a class="notelink".*?</a>', '', m.group(2), flags=re.S)
        es_by_v[m.group(1)] = line
    if not es_by_v:
        return content, False

    def add(m):
        vid = m.group("vid")
        esline = es_by_v.get(vid)
        if not esline:
            return m.group(0)
        return m.group(0) + "\n      " + esline
    # after each verse's English line, insert the Spanish line
    out = re.sub(
        r'id="(?P<vid>v[\w-]+)".*?<div class="eng">.*?</div>',
        add, content, flags=re.S)
    return out, True


def build_es():
    """The Spanish locale — a parallel edition built chapter by chapter from
    source/es/*.html. Each Spanish chapter renders to <slug>.es.html with Spanish
    chrome (Spanish nav, an 'Ocultar hebreo' toggle, and the 🌐 language switch back
    to English); es.html is the Spanish home. The English site is untouched. Grows as
    source/es/ files are added — the same 'chapter by chapter on both sides' cadence."""
    panels = _es_panels()
    if not panels:
        return
    en_by_slug = {slug: (book, num) for slug, book, num, _ in CHAPTERS}
    def es_teaser(slug):
        """Spanish description for a Spanish card. Never falls back to English —
        a missing teaser prints a warning and an empty description instead."""
        t = TEASERS_ES.get(slug)
        if not t:
            print(f"   \u26a0 no Spanish teaser for {slug} — add one to TEASERS_ES")
            return ""
        if len(t) > 160:                     # truncate the TEXT, then escape:
            t = t[:160].rsplit(" ", 1)[0] + "\u2026"   # escaping first can cut an
        return html.escape(t)                # HTML entity in half (&#x27; -> &#x2)
    built = []
    for slug, content in panels.items():
        bk = en_by_slug.get(slug)
        if not bk:
            continue
        book, num = bk
        es_title = f"{ES_BOOK.get(book, book)} {num}"
        en_file = chapter_filename(book, num)
        es_file = en_file[:-5] + ".es.html"          # genesis-1.html -> genesis-1.es.html
        toggle = (f'<div class="togglebar"><div class="tgl-group">'
                  f'<button class="tgl" id="hebtgl" onclick="toggleHeb()">Ocultar hebreo</button>'
                  f'<a class="tgl" href="{en_file}" title="Ver en inglés">\U0001F310 English</a>'
                  f'</div></div>')
        body = f"""{toggle}
<article class="chapter esp-page">
{content}
</article>
<p class="muted" style="text-align:center;margin:26px 0 0"><a href="{en_file}">Ver este capítulo en inglés (con la biblioteca y más notas) →</a></p>
<script>
function toggleHeb(){{
  var hidden = document.body.classList.toggle("hide-heb");
  document.getElementById("hebtgl").textContent = hidden ? "Mostrar hebreo" : "Ocultar hebreo";
  try{{ localStorage.setItem("mtlib_hideheb", hidden ? "1" : "0"); }}catch(e){{}}
}}
(function(){{ try{{ if(localStorage.getItem("mtlib_hideheb")==="1"){{
  document.body.classList.add("hide-heb");
  document.getElementById("hebtgl").textContent = "Mostrar hebreo";
}} }}catch(e){{}} }})();
</script>"""
        out = page(f"{es_title} — La Traducción Mister", body, lang="es",
                   url=es_file,
                   desc=f"{es_title}: una traducción nueva desde el hebreo, versículo por versículo, con notas del "
                        f"traductor y comparación con la Reina-Valera, la NVI y otras versiones. El Nombre: «Jehová».")
        open(os.path.join(OUT, es_file), "w", encoding="utf-8").write(out)
        built.append((slug, book, num, es_title))

    # Spanish home / índice
    built.sort(key=lambda x: (x[1], x[2]))
    cards = "\n".join(
        f'  <a class="card" href="{chapter_filename(b, n)[:-5]}.es.html"><div class="card-t">{t}</div>'
        f'<div class="card-d">{es_teaser(s)}</div></a>'
        for (s, b, n, t) in built)
    home = f"""<h1 class="pagetitle">La Traducción Mister</h1>
<p class="lede">Una nueva traducción de la Biblia <strong>desde el hebreo y el griego</strong>, capítulo por
capítulo y versículo por versículo, con notas del traductor y comparación con la Reina-Valera, la NVI, La Biblia
de las Américas y Dios Habla Hoy. El Nombre de Dios se traduce «<strong>Jehová</strong>», como en la
Reina-Valera.</p>

<div class="panel prose">
  <h2 style="margin-top:2px">Una edición que está naciendo</h2>
  <p>Esta es la edición en español, apenas comenzando y creciendo <strong>capítulo por capítulo</strong> junto a
  la <a href="index.html">edición en inglés</a>, que va más adelantada. Por ahora la biblioteca completa
  (enciclopedia, diccionario, atlas, cronología) y el aparato de notas más extenso viven en inglés; todo eso se
  irá traduciendo. Nada se traduce a la ligera: el texto viene del hebreo con el mismo cuidado que la edición
  inglesa — «bóveda», no «expansión»; «la humanidad», no «el hombre» — y las notas comparan con la Reina-Valera
  en vez de con las versiones inglesas.</p>
  <p>Si además lees inglés, en cada capítulo de la edición inglesa puedes <strong>activar u ocultar</strong> el
  hebreo, el inglés y el español a la vez, versículo por versículo.</p>
</div>

<h2>Capítulos disponibles</h2>
<div class="cardgrid">
{cards}
</div>"""
    out = page("La Traducción Mister — La Biblia en español", home, active="home", lang="es", url="es.html",
               desc="La Traducción Mister en español: la Biblia desde el hebreo, capítulo por capítulo, con notas "
                    "y comparación con la Reina-Valera. El Nombre de Dios se traduce «Jehová».")
    open(os.path.join(OUT, "es.html"), "w", encoding="utf-8").write(out)


def build_ask_index():
    body = """<h1 class="pagetitle">\U0001F4D6 Ask Mr. Librarian</h1>
<p class="lede">Reader questions about the translation — a word-choice, the text, the canon, a comparison
between versions — answered one at a time, in the librarian's way: sourced, compared, and left for you to
weigh rather than settled from the desk. Have one of your own? The <a href="contact.html">question box</a> is
exactly how this series grows.</p>
<div class="cardgrid">
  <a class="card" href="ask-jesus-god.html"><div class="card-t">Was the Word "God," or "a god"?</div>
  <div class="card-d">John 1:1 and the deity of Christ — the Greek of the missing article, "firstborn of all
  creation," the Angel of Jehovah, and the whole argument laid out on both sides.</div></a>
  <a class="card" href="ask-jehovah.html"><div class="card-t">Why does this translation say "Jehovah"?</div>
  <div class="card-d">The name of God — the four letters behind "the LORD," why almost every Bible hides it, and
  the choice between "the LORD," "Yahweh," and "Jehovah."</div></a>
  <a class="card" href="ask-enoch.html"><div class="card-t">Why isn't the Book of Enoch in this translation?</div>
  <div class="card-d">The Masoretic source text, the canon question, the Ethiopian exception, and the Dead Sea
  Scrolls.</div></a>
  <a class="card" href="ask-creation-days.html"><div class="card-t">How long were the days of creation?</div>
  <div class="card-d">The elastic Hebrew word <em>yom</em>, the sunless first days and the open seventh, and the
  ordinary-day, day-age, and literary-framework readings — with their pedigrees, no vote cast.</div></a>
  <a class="card" href="ask-newton.html"><div class="card-t">Did Isaac Newton write about the Bible?</div>
  <div class="card-d">The scientist wrote more on Scripture than on physics — his Daniel &amp; Revelation, his
  textual criticism of the Johannine Comma, his chronology, and his hidden anti-Trinitarianism, handled
  honestly.</div></a>
</div>"""
    out = page(f"Ask Mr. Librarian — {SITE_NAME}", body, active="ask",
               desc="Reader questions about The MisterLibrarian Bible Project, answered one at a time — sourced, "
                    "compared, and left for you to weigh.")
    open(os.path.join(OUT, "ask.html"), "w", encoding="utf-8").write(out)


def build_ask_jesus_god():
    """The exhaustive, balanced Ask Mr. Librarian post on John 1:1 and the deity of
    Christ. Presents BOTH the subordinationist/unitarian case and the full-deity case
    at full strength and declines to hand down a verdict — the project's 'catalogue,
    source, compare, don't preach' ethos. Edit this function to revise the post."""
    body = """<div class="askbar"><a href="ask.html">← Ask Mr. Librarian</a></div>
<h1 class="pagetitle">Was the Word "God," or "a god"?</h1>
<h2 style="margin-top:2px">John 1:1 and the deity of Christ</h2>

<div class="qbox">
  <div class="qlabel">A reader asked</div>
  <p>"John 1:1 is usually translated 'the Word was God,' but the New World Translation reads 'the Word was a
  god.' Which is right — and behind it, the bigger question: is Jesus God, a lesser divine being, or the
  highest of created beings? Can you lay out the whole argument, from the Greek and from the rest of the Bible,
  on both sides?"</p>
</div>

<div class="panel prose">
  <p><strong>A word before we begin.</strong> This is the single most-argued sentence in the Bible, and people
  who love the text, read the Greek, and mean every syllable of it have divided over it for seventeen centuries.
  A librarian's task here is not to hand down a verdict but to lay the evidence out fully and fairly — the
  grammar, the immediate context, and the witness of the rest of Scripture — and let you weigh it. So this post
  builds <em>both</em> cases at full strength and marks honestly where each one pays a price. (Our own
  translation had to choose a rendering for the verse itself; it takes the <em>qualitative</em> road — "and the
  Word was <a href="john-1.html#v1">divine</a>" — for reasons the John 1 note explains, but that is a rendering,
  not a ruling. The argument below is yours to finish.)</p>
</div>

<h2>The sentence that won't sit still</h2>
<div class="panel prose">
  <p>The Greek is <span class="greek">Ἐν ἀρχῇ ἦν ὁ λόγος, καὶ ὁ λόγος ἦν πρὸς τὸν θεόν, καὶ θεὸς ἦν ὁ λόγος</span>
  — three clauses. <strong>(1)</strong> "In the beginning was the Word": already existing when time began.
  <strong>(2)</strong> "and the Word was <em>with</em> God" (<em>pros ton theon</em>): face-to-face, in
  relationship — so the Word is not simply the same as the one he is "with." <strong>(3)</strong> "and the Word
  was <em>theos</em>." The whole fight is that third clause — and, standing behind it, whether the one it names
  is the eternal God, a distinct-but-lesser deity, or the first and highest thing God ever made.</p>
</div>

<h2>The grammar: the missing article</h2>
<div class="panel prose">
  <p><strong>Koine Greek has no word for "a."</strong> It has only the definite article ("the"). So every "a" or
  "an" in an English New Testament is <em>supplied</em> by the translator — it is never literally in the Greek.
  "There came <em>a</em> man" (John 1:6) has no "a" in Greek. That happens thousands of times, and it is the root
  of the whole dispute: in the clause "the Word was <em>theos</em>," <em>theos</em> ("God/god") has no article,
  and the translator must decide whether to leave it bare, add "the," or add "a."</p>
  <p><strong>The exact construction here</strong> — an article-less predicate noun standing <em>before</em> the
  verb — turns up all over the New Testament, and translators render it three different ways depending on the
  word and the context:</p>
  <ul class="prose-list">
    <li><strong>Indefinite ("a ___"):</strong> "this man is <em>a murderer</em>" (Acts 28:4 — the closest
    structural twin to John 1:1); "he was <em>a murderer</em> from the beginning" (John 8:44); "you are <em>a
    prophet</em>" (John 4:19). And, tellingly, the very same word: the Maltese "said he was <em>a god</em>" of
    Paul (Acts 28:6). So <em>theos</em> without the article <em>can</em> be "a god" — that part of the New World
    Translation's case is not baseless.</li>
    <li><strong>Qualitative (the <em>nature</em>, no "a," where "a" would be wrong):</strong> "God is
    <em>spirit</em>" (John 4:24 — same construction, and no one writes "God is a spirit"); "God is <em>love</em>"
    (1 John 4:8 — never "a love"); the Word became "<em>flesh</em>" (John 1:14).</li>
    <li><strong>Definite ("the ___"):</strong> a smaller set, where context makes the bare noun definite.</li>
  </ul>
  <p>So the construction <em>by itself</em> settles nothing — the same grammar yields "a murderer," "a god,"
  "God is spirit," and "God is love." What decides is the meaning of the noun and the context. The two studies
  everyone cites: <strong>Colwell (1933)</strong> observed that a <em>definite</em> predicate noun before the
  verb usually drops its article — but that only describes nouns already known to be definite; it cannot tell you
  whether a bare noun is definite, indefinite, or qualitative (reading it the other way round is a logical
  error). <strong>Harner (1973)</strong> studied this precise construction and concluded it is usually
  <em>qualitative</em> — and that John 1:1c is <em>neither</em> "the Word was God" <em>nor</em> "a god," but "the
  Word had the same nature as God." That qualitative reading is the mainstream of Greek scholarship.</p>
  <p><strong>The honest summary of the grammar:</strong> "a god" is grammatically <em>possible</em> (Acts 28:6
  proves it) but grammatically <em>disfavored</em> — the construction leans qualitative, toward <em>nature</em>,
  not toward "one of a class." And there is a semantic snag on top: "prophet," "murderer," "king" are classes you
  can be one <em>of</em>; but in the Bible's strict monotheism there is no class of "gods" to be one of ("besides
  me there is no god," Isaiah 44:6), which is what makes "a god" sit awkwardly where "a prophet" does not.</p>
</div>

<h2>The three readings, and one piece of plain logic</h2>
<div class="panel prose">
  <p>Three renderings, three theologies:</p>
  <ul class="prose-list">
    <li><strong>"the Word was God"</strong> (definite) — if read as "the Word <em>is</em> the person God," it
    collapses the Word into the Father. But the clause just said the Word was <em>with</em> God, and later Jesus
    <em>prays</em> to the Father — you cannot be <em>with</em> someone and <em>be</em> that same someone. So this
    reading, taken flatly, is ruled out by the verse itself. (It is the ancient error called <em>modalism</em>.)</li>
    <li><strong>"the Word was a god"</strong> (indefinite) — a distinct, <em>lesser</em> deity. Solves the
    with/be problem, but at the price the grammar disfavors and monotheism resists.</li>
    <li><strong>"the Word was divine / fully God"</strong> (qualitative) — the Word shares the one God's nature
    while remaining a distinct person from the Father. Answers the with/be logic (distinct persons, one nature)
    and matches the grammar's qualitative lean.</li>
  </ul>
  <p>Notice what the reader's own instinct — "you can't be with someone and be someone at the same time" —
  actually proves: it kills the flat, identifying reading, and leaves <em>either</em> the indefinite <em>or</em>
  the qualitative standing. Which of those two wins is decided not by the one verse but by what the rest of
  Scripture says the Word <em>is</em>. So — the two cases.</p>
</div>

<h2>The case that the Word is distinct, and subordinate</h2>
<div class="panel prose">
  <p>This is the reading Arius argued in the fourth century and the Jehovah's Witnesses hold today: the Son is
  genuinely <em>other</em> than the Father, ranked <em>under</em> him, and — in its stronger form — the first and
  highest of God's creatures rather than the uncreated God. Its evidence is real and considerable:</p>
  <p><strong>The distinction is written in.</strong> "The Word was <em>with</em> God." The Son is never the
  Father, and the Gospel never blurs them.</p>
  <p><strong>The Son defers to the Father, everywhere.</strong> "The Father is <em>greater</em> than I" (John
  14:28); "the Son can do nothing of his own accord" (5:19); "I came not to do my own will but the will of him
  who sent me" (6:38); "that they may know <em>you, the only true God</em>, and Jesus Christ whom you sent"
  (17:3); "I am ascending to <em>my God</em> and your God" (20:17); of the last day, "nor the Son, but only the
  Father" (Mark 13:32).</p>
  <p><strong>He prays.</strong> "Our Father who art in heaven" — spoken by a man on earth, to the Father in
  heaven. He cannot be praying to himself. Whoever the Word is, he is not the one he addresses.</p>
  <p><strong>"The firstborn of all creation" (Colossians 1:15),</strong> "the beginning of the creation of God"
  (Revelation 3:14), and Wisdom, whom "Jehovah created at the beginning of his work" (Proverbs 8:22, in the
  Greek Old Testament). On this reading the Son <em>had a beginning</em> — and the model is elegant: the Father,
  the unmade Architect, brings forth one first and supreme being, the Word, and then makes everything else
  <em>through</em> him, the master builder. "All things came to be through him" is satisfied without making the
  builder himself unmade.</p>
  <p><strong>The Angel of Jehovah.</strong> "I send an angel before you... obey his voice... <em>for my name is
  in him</em>" (Exodus 23:20–21). Throughout the Old Testament a figure called the Angel of Jehovah appears,
  speaks as God, bears the divine Name, and leads Israel out of Egypt (Exodus 14:19). Read this way, the "God" who
  <em>appears and speaks</em> in the Old Testament is the Word — Yahweh's spokesman and agent — while the supreme,
  invisible God is the Father ("no one has ever seen God," John 1:18; "his voice you have never heard, his form
  you have never seen," 5:37). And the pre-human Word, on this reading, is <em>Michael the archangel</em> — the
  Lord descends "with the voice of an archangel" (1 Thessalonians 4:16); Michael leads the armies of heaven
  (Revelation 12:7; Daniel 12:1).</p>
  <p><strong>And monotheism itself.</strong> There is one God, the Father; to call the Word "God" flatly seems to
  make two. Better, then, "a god," "a mighty one," "divine" — a real but subordinate glory, under the one God.</p>
  <p>It is a coherent, textually-anchored system, sincerely held. It is not a straw man, and it was very nearly
  the church's settled view.</p>
</div>

<h2>The case that the Word is fully God — one nature, distinct person</h2>
<div class="panel prose">
  <p>This reading agrees with every "distinct" and "submits" verse above — and says they describe the Son's
  <em>person</em> and his <em>mission</em>, not a lesser <em>nature</em>. Its evidence is a second stack the
  created-Son reading has to account for:</p>
  <p><strong>He made everything that was made (John 1:3; Colossians 1:16).</strong> "Not one thing came to be that
  has come to be" apart from him. If he made <em>all</em> created things, he is not among them — he is on the
  Creator's side of the line. (Tellingly, the New World Translation has to insert "<strong>[other]</strong>" four
  times in Colossians 1 — "all <em>[other]</em> things" — to keep the Son a creature; that bracketed word is not
  in the Greek, and it is doing all the work.)</p>
  <p><strong>"Firstborn" means rank, not birth-order.</strong> God calls David — Jesse's <em>youngest</em> son —
  "my <em>firstborn</em>, the highest of the kings of the earth" (Psalm 89:27), and glosses it for us: highest.
  Israel and Ephraim are each God's "firstborn" though neither was first. And Paul explains <em>why</em> he calls
  the Son firstborn — "<strong>for</strong> in him all things were created... and he is <em>before</em> all
  things" (Colossians 1:16–17): the title is grounded in his being Creator and sustainer, not the first creature.
  Greek even had a word for "first-created" (<em>prōtoktistos</em>); Paul pointedly did not use it.</p>
  <p><strong>God says he created alone.</strong> "I am Jehovah, who made all things, who stretched out the heavens
  <em>alone</em>, who spread out the earth <em>by myself</em>" (Isaiah 44:24). A general-contractor creature doing
  the building makes that false — unless the "through whom" belongs to the one Creator's own act.</p>
  <p><strong>Hebrews 1 all but forbids reading the Son as an angel.</strong> "To which of the <em>angels</em> did
  God ever say, 'You are my Son'?" (1:5) — none. "Let all God's angels <em>worship him</em>" (1:6). "Of the Son he
  says, 'Your throne, <em>O God</em>, is forever'" (1:8). And to the Son: "<em>You, Lord, laid the foundation of
  the earth</em>" (1:10 — a psalm to the eternal, unchanging YHWH, put in the Father's mouth <em>to</em> the Son).</p>
  <p><strong>The worship line.</strong> Created angels <em>refuse</em> worship: "You must not do that! I am a
  fellow servant... <em>worship God!</em>" (Revelation 22:8–9). The Son <em>receives</em> it, and angels are
  commanded to give it (Hebrews 1:6; and Thomas: "<em>my Lord and my God!</em>," John 20:28). Worship is the one
  thing that cannot be delegated — which is why it divides the Son from every creature.</p>
  <p><strong>YHWH's own signature, on Jesus.</strong> "I am <em>the first and the last</em>," says the one "who
  died, and is alive forevermore" (Revelation 1:17–18); "I am the Alpha and the Omega, the first and the last"
  (22:13, where verse 16 says "I, Jesus"). And "the first and the last" is the title YHWH claims <em>exclusively</em>
  — "besides me there is no god" (Isaiah 44:6). You cannot be "the first" and have had a beginning. So the same
  book that some read as "the beginning of creation" (Rev 3:14) also calls Jesus the one before whom nothing was.</p>
  <p><strong>He simply "was."</strong> John 1:1 says the Word "<em>was</em>" (continuous), never "came to be" —
  the very verb used for created things through the rest of the Prologue. "Before Abraham was, <em>I am</em>"
  (8:58). "The glory I had with you <em>before the world existed</em>" (17:5). "In him the whole <em>fullness of
  deity</em> dwells bodily" (Colossians 2:9); "in the <em>form of God</em>" (Philippians 2:6); "<em>Mighty
  God</em>" (Isaiah 9:6).</p>
  <p><strong>And the submission is real — but it is the submission of the <em>incarnate</em> Son.</strong> He
  "<em>emptied himself</em>, taking the form of a servant" (Philippians 2:6–7). "Greater" in "the Father is greater
  than I" is <em>meizōn</em> — greater in <em>position</em> — not <em>kreittōn</em>, better in <em>nature</em>. A
  son who obeys his father is no less human; and "Son" and "begotten" are same-nature words (a father begets a son
  of his own kind), which is why the old line was "<strong>begotten, not made</strong>": the Son is not fashioned
  like a tool but is of the Father's own being.</p>
</div>

<h2>The Angel of Jehovah, and Michael the archangel</h2>
<div class="panel prose">
  <p>This deserves its own weighing, because half of it is strong on any reading. That the Old Testament's
  <em>visible, speaking</em> God is the pre-incarnate Word — Yahweh's face and voice for the invisible Father —
  is an <em>ancient</em> Christian reading (Justin, Irenaeus, Tertullian), and it has real support: "no one has
  ever seen God" (John 1:18); the rock in the wilderness "<em>was Christ</em>" (1 Corinthians 10:4); and the
  earliest manuscripts of Jude 5 read that "<em>Jesus</em>, who saved a people out of the land of Egypt," later
  judged them. So the reader's instinct that the Word acted, appeared, and led in the Old Testament is not only
  plausible — it is old and well-grounded.</p>
  <p>What that instinct <em>produces</em>, though, cuts toward deity: if the "God" at the burning bush is the
  Word, then the one who said "<strong>I AM WHO I AM</strong>" (Exodus 3:14) is the Word — and when Jesus says
  "before Abraham was, <em>I am</em>" (John 8:58), he is claiming to be that very "I AM." Identifying the
  Old Testament God-figure with the Word makes him <em>greater</em>, not smaller.</p>
  <p>Is that Word a <em>created</em> archangel? "Angel" (<em>malʾakh</em>, <em>angelos</em>) means
  <strong>messenger — one sent</strong>; it names a job, not a nature. So the Word can be "the Messenger of Jehovah"
  while being divine. And three things resist the identification of the Son with the creature Michael:
  the Angel of Jehovah <em>receives worship</em>, speaks as God ("I am the God of Bethel," Genesis 31:13), and
  bears the Name — where created angels refuse worship; <strong>Hebrews 1</strong> spends a chapter proving the
  Son is <em>above</em> the angels, worshiped <em>by</em> them, and the Creator; <strong>Colossians 1:16</strong>
  says the Son created the angelic ranks ("thrones, dominions, rulers, authorities") — so he made Michael; and
  <strong>Jude 9</strong> has "the archangel Michael" not daring to rebuke Satan on his own authority — "<em>the
  Lord rebuke you</em>" — while Jesus commands Satan and demons directly ("Be gone, Satan!"). Michael appeals to a
  higher authority; Jesus <em>is</em> the one appealed to. (And "with the voice of an archangel," 1 Thessalonians
  4:16, no more makes Jesus the archangel than "with a trumpet blast" makes a general the trumpeter.)</p>
</div>

<h2>Where the oldest manuscripts weigh in</h2>
<div class="panel prose">
  <p>Two nearby verses are decided by the same manuscript evidence set out in the
  <a href="new-testament.html">New Testament introduction</a>. At <strong>John 1:18</strong> the earliest
  witnesses — the papyri <strong>P66</strong> and <strong>P75</strong>, with Sinaiticus and Vaticanus — read
  "the only <em>God</em>," while the later majority (and the King James tradition) read "the only <em>Son</em>."
  At <strong>John 1:34</strong> the earliest text reads "the <em>Chosen One</em> of God," the majority "the
  <em>Son</em> of God." The oldest copies, in other words, lean toward the higher Christology at 1:18 — but the
  manuscripts alone do not end the argument, and honest editions print both.</p>
</div>

<h2>The three ways the church has read it</h2>
<div class="panel prose">
  <p>It helps to name the landscape, without endorsing a corner:</p>
  <p><strong>Trinitarian</strong> (the Nicene mainstream): one God in three distinct persons — Father, Son,
  Spirit — the Son "begotten, not made," of one nature with the Father. Reads 1:1 qualitatively or definitely.</p>
  <p><strong>Unitarian / Arian / Jehovah's Witnesses:</strong> the Father alone is Almighty God; the Son is a
  distinct, subordinate being — in the Witnesses' form, the first creation and the pre-human Michael, "a god" in
  a real but lesser sense. Reads 1:1 "a god."</p>
  <p><strong>Modalist</strong> (Sabellian): Father, Son, and Spirit are one person in three modes. Reads 1:1 as
  a flat identity — and is the one option the verse's own "with God," plus the Lord's Prayer, most clearly rule
  out.</p>
</div>

<h2>Why sincere readers land differently</h2>
<div class="panel prose">
  <p>Because each reading pays a real price somewhere, and honest people weigh the prices differently.</p>
  <p><strong>The full-deity reading</strong> must take "firstborn" as rank rather than birth, lean hard on "the
  first and the last" being said of Jesus, and confess that three persons in one being is beyond tidy
  comprehension.</p>
  <p><strong>The created-Son reading</strong> must insert "[other]" into Colossians, read "firstborn" against
  Psalm 89's own definition, set aside Isaiah 44:24's "alone," and explain how a creature can be worshiped and
  wear YHWH's exclusive title.</p>
  <p><strong>The modalist reading</strong> must explain away the plain "with God" and a Son who prays to a Father
  not himself.</p>
  <p>Where you land depends on which verses you treat as the fixed points and which you treat as the ones needing
  explaining — and that is a genuinely weighty judgment, not a mark of bad faith on any side.</p>
</div>

<h2>Where this translation stands — and doesn't</h2>
<div class="panel prose">
  <p>A translation cannot print three renderings in one line; it has to choose, and then let the note carry the
  rest. This project renders 1:1 <strong>"and the Word was <a href="john-1.html#v1">divine</a>"</strong> — the
  qualitative road — because it is the reading the grammar most supports, it keeps the distinction the verse
  itself insists on ("<em>with</em> God"), and it avoids both the flat "was God" (which an English reader can hear
  as "the Word is the Father") and "a god" (which the grammar least supports and monotheism resists). That is a
  <em>translation choice</em>, argued in the open — not a verdict on the deep question of whether the Son is God
  of very God, a lesser divine being, or the first of creatures. On <em>that</em>, the librarian sets the two
  cases side by side, as above, and hands the scales to you.</p>
  <p class="muted" style="margin-top:6px">Read the verse in place, with its note: <a href="john-1.html#v1">John
  1:1</a>. The manuscripts behind 1:18 and 1:34: the <a href="new-testament.html">New Testament introduction</a>.
  More questions become posts here — <a href="contact.html">send yours to the librarian's desk</a>.</p>
</div>

<div class="panel" style="margin-top:14px">
  <p class="muted" style="margin:0 0 12px">More from <a href="ask.html">Ask Mr. Librarian</a>:
  <a href="ask-enoch.html">Why isn't the Book of Enoch in this translation?</a></p>
  <a class="btn" href="contact.html">✉️ Ask Mr. Librarian a question</a>
</div>"""
    out = page(f"Ask Mr. Librarian: was the Word God, or a god? — {SITE_NAME}", body, active="ask",
               desc="John 1:1 and the deity of Christ: the Greek grammar of the missing article (Colwell, "
                    "Harner), the three readings, 'firstborn of all creation,' the Angel of Jehovah and Michael "
                    "the archangel, the earliest manuscripts, and the whole case on both sides — laid out, not "
                    "settled.")
    open(os.path.join(OUT, "ask-jesus-god.html"), "w", encoding="utf-8").write(out)


def build_ask_jehovah():
    """Ask Mr. Librarian post explaining the divine-name choice: the Tetragrammaton,
    why nearly every Bible hides it behind 'the LORD,' Yahweh vs. Jehovah, and why this
    project restores the traditional English form 'Jehovah.'"""
    body = """<div class="askbar"><a href="ask.html">← Ask Mr. Librarian</a></div>
<h1 class="pagetitle">Why does this translation say &ldquo;Jehovah&rdquo;?</h1>
<h2 style="margin-top:2px">The name of God &mdash; the LORD, Yahweh, or Jehovah</h2>

<div class="qbox">
  <div class="qlabel">A reader asked</div>
  <p>&ldquo;Most Bibles say &lsquo;the L<span style="font-variant:small-caps">ord</span>.&rsquo; Why does this one
  print &lsquo;Jehovah&rsquo;? And isn&rsquo;t the Hebrew name really &lsquo;Yahweh&rsquo;?&rdquo;</p>
</div>

<div class="panel prose">
  <p><strong>The short answer.</strong> Behind the English word &ldquo;L<span
  style="font-variant:small-caps">ord</span>&rdquo; in most Bibles stands an actual name &mdash; the personal name
  of God, four Hebrew letters, <span class="dheb">יהוה</span> (YHWH), that the text uses some
  6,800 times. This translation prints it as <strong>Jehovah</strong> rather than hiding it behind the title
  &ldquo;the L<span style="font-variant:small-caps">ord</span>.&rdquo; Here is the whole story &mdash; the name, why
  it got covered over, and why &ldquo;Jehovah&rdquo; and not &ldquo;Yahweh.&rdquo;</p>
</div>

<h2>The name, and the four letters</h2>
<div class="panel prose">
  <p>God&rsquo;s personal name in the Hebrew Bible is written with four consonants &mdash; <span
  class="dheb">יהוה</span>, Y&#8209;H&#8209;W&#8209;H &mdash; which is why it is called the
  <strong>Tetragrammaton</strong> (&ldquo;four letters&rdquo;). It first appears in this translation at
  <a href="genesis-2.html">Genesis 2:4</a>, paired with <em>Elohim</em> (&ldquo;God&rdquo;) as <em>YHWH
  Elohim</em>, and from there it runs through the whole Hebrew Bible about <strong>6,800 times</strong> &mdash; far
  more often than any title. It is not a generic word for &ldquo;god&rdquo; (that is <em>Elohim</em>); it is a name,
  the way &ldquo;Abram&rdquo; is a name.</p>
</div>

<h2>Why almost every Bible hides it</h2>
<div class="panel prose">
  <p>Sometime in the centuries before Christ, Jewish reverence for the name hardened into a practice of
  <strong>not pronouncing it aloud</strong>. When a reader reached YHWH in the text, he said <em>Adonai</em>
  (&ldquo;my Lord&rdquo;) instead. That spoken substitution became the written one nearly everywhere:</p>
  <ul>
    <li>the Greek Old Testament (the <strong>Septuagint</strong>) put <em>Kyrios</em>, &ldquo;Lord&rdquo;;</li>
    <li>the Latin <strong>Vulgate</strong> put <em>Dominus</em>, &ldquo;Lord&rdquo;;</li>
    <li>and the <strong>King James Version</strong> set the English pattern still followed almost everywhere: print
    the name as &ldquo;the L<span style="font-variant:small-caps">ord</span>&rdquo; in small capitals &mdash; so a
    reader can tell the divine name from the ordinary word &ldquo;Lord&rdquo; (<em>Adonai</em>).</li>
  </ul>
  <p>So &ldquo;the L<span style="font-variant:small-caps">ord</span>&rdquo; in your Bible is not a translation of
  the name &mdash; it is a <em>substitute</em> for it, a title standing where the text actually put a name.
  Reverent, and nearly universal &mdash; but it does hide the name.</p>
</div>

<h2>Yahweh, or Jehovah?</h2>
<div class="panel prose">
  <p>Here is the twist: because the name went unspoken for so long, <strong>its original pronunciation was
  lost</strong>. Hebrew was written with consonants only; the vowel marks were added centuries later by scribes
  called the Masoretes &mdash; and when they came to YHWH, they did not write the name&rsquo;s own vowels (which
  they were not saying), they wrote the vowels of <em>Adonai</em>, as a reminder to say &ldquo;Adonai.&rdquo; So the
  written form carries one word&rsquo;s consonants and another word&rsquo;s vowels.</p>
  <p><strong>&ldquo;Yahweh&rdquo;</strong> is the modern scholarly <em>reconstruction</em> of the original &mdash;
  pieced together from early Greek writers who did spell it out (Clement of Alexandria wrote <em>Iabe</em>) and from
  the way the name appears inside other names (<em>Yeho</em>&#8209;shua, Isai&#8209;<em>ah</em>). It is very likely
  close to right.</p>
  <p><strong>&ldquo;Jehovah&rdquo;</strong> is what you get if you read those hybrid letters literally &mdash;
  YHWH&rsquo;s consonants <em>with</em> Adonai&rsquo;s vowels &mdash; a reading that took shape in the Middle Ages
  and became standard in English from around the sixteenth century. Strictly, it is a form that was never spoken in
  ancient Israel. But it has been the English name of God for some <strong>four to five hundred years</strong>: it
  stands in the KJV itself (Exodus 6:3; Psalm 83:18; Isaiah 12:2; 26:4), runs through the whole
  <span class="tag t-asv">ASV</span> of 1901, fills the hymnbook (&ldquo;Guide Me, O Thou Great Jehovah&rdquo;), and
  is the <span class="tag t-nwt">NWT</span>&rsquo;s single most defining choice.</p>
</div>

<h2>Why this translation chose &ldquo;Jehovah&rdquo;</h2>
<div class="panel prose">
  <p>Three honest options, then: keep <strong>&ldquo;the L<span
  style="font-variant:small-caps">ord</span>&rdquo;</strong> (traditional, but it hides the name); restore
  <strong>&ldquo;Yahweh&rdquo;</strong> (the scholar&rsquo;s best reconstruction); or restore
  <strong>&ldquo;Jehovah&rdquo;</strong> (the long&#8209;accepted English form of the name). This translation takes
  the third road &mdash; <strong>Jehovah</strong> &mdash; because it does the main thing worth doing, <em>puts the
  name back where the text has a name</em>, and does it in the form that has been at home in English for four
  centuries and that readers already recognize. It is not the scholar&rsquo;s reconstruction, and the notes do not
  pretend otherwise; it is the traditional English name, chosen on purpose &mdash; the same instinct that keeps
  &ldquo;Jesus&rdquo; and &ldquo;Isaiah&rdquo; rather than re&#8209;spelling every familiar name from scratch.</p>
  <p>A small, consistent code follows from it, and you will see all of it in the text:</p>
  <ul>
    <li><strong>Jehovah</strong> = the name YHWH (where other Bibles print &ldquo;the L<span
    style="font-variant:small-caps">ord</span>&rdquo;).</li>
    <li><strong>Lord Jehovah</strong> = <em>Adonai YHWH</em>, the title &ldquo;Lord&rdquo; joined to the name (as at
    <a href="genesis-15.html">Genesis 15:2</a>; older Bibles print &ldquo;Lord G<span
    style="font-variant:small-caps">od</span>&rdquo;).</li>
    <li><strong>Lord</strong> (ordinary type) = <em>Adonai</em>, the title on its own; <strong>God</strong> =
    <em>Elohim</em>.</li>
  </ul>
</div>

<h2>And the New Testament?</h2>
<div class="panel prose">
  <p>The same instinct raises a fair question about Jesus &mdash; whose name in his own tongue was
  <strong>Yeshua</strong> (&ldquo;Yahweh saves&rdquo;). This project keeps <strong>&ldquo;Jesus,&rdquo;</strong> the
  form the New Testament&rsquo;s own Greek authors wrote (<em>Iēsous</em>) and the form English has used for
  centuries &mdash; restoring the divine <em>name</em> in the Old Testament, while leaving the familiar personal
  names where readers already know them. So: the <em>name of God</em> is restored; the names of people are left as
  they stand.</p>
</div>

<div class="panel" style="margin-top:14px">
  <p class="muted" style="margin:0 0 12px">See it first at <a href="genesis-2.html">Genesis 2:4</a>, or in the
  <a href="dictionary.html">Dictionary</a> and <a href="encyclopedia.html">Encyclopedia</a>. More from
  <a href="ask.html">Ask Mr. Librarian</a>: <a href="ask-jesus-god.html">Was the Word God, or a god?</a> &middot;
  <a href="ask-enoch.html">Why isn&rsquo;t the Book of Enoch here?</a></p>
  <a class="btn" href="contact.html">✉️ Ask Mr. Librarian a question</a>
</div>"""
    out = page(f"Ask Mr. Librarian: why “Jehovah”? — {SITE_NAME}", body, active="ask",
               desc="The divine name in this translation: the Tetragrammaton (YHWH), why nearly every Bible hides "
                    "it behind 'the LORD,' the difference between 'Yahweh' and 'Jehovah,' and why this project "
                    "restores the traditional English form 'Jehovah.'")
    open(os.path.join(OUT, "ask-jehovah.html"), "w", encoding="utf-8").write(out)


def build_ask_creation_days():
    """Ask Mr. Librarian post on the length of the creation 'days' — the word yom,
    the internal signals of Genesis 1, the ordinary-day / day-age / framework
    readings with their pedigrees, and the honest 'isn't this just bending the Bible
    to fit science?' question. Companion to the Genesis 1 v5 note and the yom
    dictionary entry. Neutrality habit: lay out the views, don't cast a vote."""
    body = """<div class="askbar"><a href="ask.html">← Ask Mr. Librarian</a></div>
<h1 class="pagetitle">How long were the days of creation?</h1>
<h2 style="margin-top:2px">The word <em>yom</em>, the age of the earth, and the &ldquo;day-age&rdquo; reading</h2>

<div class="qbox">
  <div class="qlabel">A reader asked</div>
  <p>&ldquo;Does Genesis really mean six 24-hour days? Or can a &lsquo;day&rsquo; of creation stand for a long
  age &mdash; millions of years &mdash; so the Bible and the age of the earth aren&rsquo;t at war?&rdquo;</p>
</div>

<div class="panel prose">
  <p><strong>The short answer.</strong> The Hebrew word for &ldquo;day&rdquo; here is
  <a href="dictionary.html#yom"><em>yom</em></a>, and it is one of the most elastic words in the Bible: it can
  mean the daylight hours, an ordinary 24-hour day, <em>or</em> an indefinite stretch of time &mdash; an age.
  That range is real, and it is the reason serious readers have held very different views of the six
  &ldquo;days&rdquo; for two thousand years. A &ldquo;day&rdquo; that stands for a long age is a legitimate,
  ancient reading &mdash; not a modern dodge &mdash; and this translation lays out the options rather than
  insisting on one. Here is the whole picture.</p>
</div>

<h2>The word does the heavy lifting</h2>
<div class="panel prose">
  <p>Right in <a href="genesis-1.html#v5">Genesis 1:5</a>, <em>yom</em> is used two ways in a single sentence:
  &ldquo;God named the light <strong>day</strong> (<em>yom</em>), and the darkness he named night&rdquo; &mdash;
  there <em>yom</em> is the <em>daylight</em>, half of a 24-hour period &mdash; and then &ldquo;there was
  evening, and there was morning, <strong>day</strong> (<em>yom</em>) one,&rdquo; where it is the whole unit.
  Elsewhere the same word stretches much further:</p>
  <ul>
    <li>&ldquo;in the <strong>day</strong> that Jehovah made earth and heaven&rdquo;
    (<a href="genesis-2.html#v2-4">Genesis 2:4</a>) &mdash; here one <em>yom</em> gathers up the <em>entire</em>
    creation week; it plainly means &ldquo;when,&rdquo; not a single sunrise-to-sunset;</li>
    <li>&ldquo;the <strong>day</strong> of Jehovah&rdquo; &mdash; a whole era of judgment, not an afternoon;</li>
    <li>&ldquo;a thousand years in your sight are but as a <strong>day</strong>&rdquo; (Psalm 90:4, quoted at
    2 Peter 3:8) &mdash; the Bible&rsquo;s own reminder that God&rsquo;s days are not measured by our clocks.</li>
  </ul>
  <p>So the question &ldquo;how long is a day of creation?&rdquo; cannot be settled just by pointing at the word
  &ldquo;day.&rdquo; The word itself leaves the door open.</p>
</div>

<h2>What Genesis 1 itself hints</h2>
<div class="panel prose">
  <p>Two features of the chapter have made even careful, conservative readers wonder whether these are ordinary
  days:</p>
  <ul>
    <li><strong>The sun is not made until the fourth day</strong> (<a href="genesis-1.html#v14">1:14&ndash;19</a>).
    But an ordinary &ldquo;evening and morning&rdquo; day is defined by the sun. So the first three
    &ldquo;days&rdquo; pass with no sun to clock them &mdash; which suggests the word may be doing something
    other than marking solar days.</li>
    <li><strong>The seventh day has no &ldquo;evening and morning.&rdquo;</strong> Every other day is sealed
    with that refrain; the seventh is left open. The New Testament still speaks of God&rsquo;s
    <strong>rest</strong> as something a believer can enter <em>now</em> (Hebrews 4:3&ndash;11) &mdash; an
    open-ended &ldquo;day&rdquo; that has not yet closed.</li>
  </ul>
</div>

<h2>The readings, and their pedigrees</h2>
<div class="panel prose">
  <p>Three views have been held by serious readers, and a fourth older one. This library sets them out with
  their credentials and <strong>does not cast a vote</strong>.</p>

  <h3>1. Ordinary days &mdash; six literal 24-hour days</h3>
  <p>The plain force of &ldquo;evening and morning&rdquo; attached to a number, and the ground the Fourth
  Commandment gives for the seven-day week: &ldquo;in <em>six days</em> Jehovah made the heavens and the earth
  &hellip; and rested the seventh&rdquo; (Exodus 20:11). This is the reading of the Reformers and of modern
  <strong>young-earth creationism</strong>, which on the genealogies&rsquo; arithmetic places creation about
  six thousand years ago.</p>

  <h3>2. Long ages &mdash; the &ldquo;day-age&rdquo; reading</h3>
  <p>Each <em>yom</em> is a vast epoch, so the six &ldquo;days&rdquo; can span the millions and billions of
  years the earth and cosmos actually show. This is emphatically <em>not</em> a modern invention to escape
  geology: <strong>Augustine</strong> argued in the early fifth century (in <em>The Literal Meaning of
  Genesis</em>) that the creation &ldquo;days&rdquo; were <em>not</em> ordinary days at all, and
  <strong>Origen</strong> and the Jewish philosopher <strong>Philo</strong> read them non-literally centuries
  before that &mdash; more than a thousand years before anyone measured a rock. The day-age reading lets the
  Genesis account and the age of the universe (about <strong>13.8 billion years</strong>, with the earth about
  4.5 billion) stand together without forcing either to bend.</p>

  <h3>3. The literary framework</h3>
  <p>The &ldquo;days&rdquo; are a <em>topical</em>, not a stopwatch, arrangement. Days one to three form the
  <strong>realms</strong> &mdash; light, then sky and sea, then land &mdash; and days four to six fill those
  realms with their <strong>rulers</strong>: the luminaries, then birds and fish, then land animals and
  humankind. On this reading the chapter is a deliberately patterned poem of order, and &ldquo;how many
  hours?&rdquo; is simply the wrong question to put to it.</p>

  <h3>4. The gap reading (older)</h3>
  <p>An unstated stretch of time &mdash; long enough for whatever geology shows &mdash; falls <em>between</em>
  verses 1 and 2, before the six days begin. Widely held a century ago, less so now, but still on the shelf.</p>
</div>

<h2>&ldquo;But isn&rsquo;t this just bending the Bible to fit science?&rdquo;</h2>
<div class="panel prose">
  <p>It is the fair question, and the honest answer is <strong>no &mdash; at least not necessarily</strong>. The
  non-literal reading of the &ldquo;days&rdquo; is older than modern science by more than a millennium; Augustine
  reached it with no geology in hand at all, simply from wrestling with the text (the sunless first days, the
  open seventh, the elastic word). So a reader can hold the day-age or framework view on <em>literary and
  linguistic</em> grounds and never mention a fossil.</p>
  <p>Two honesty notes cut both ways. First, the <strong>age of the earth is a separate question</strong> from
  the length of the &ldquo;days&rdquo;: it is answered, independently and consistently, by radiometric dating,
  the cosmos&rsquo;s expansion, and the light-travel time of distant stars &mdash; and a 24-hour-day reader can
  still hold an old earth (the gap or framework views allow it). Second, forcing a tight <em>concordance</em>
  &mdash; matching each &ldquo;day&rdquo; to a geological era &mdash; can strain the text as much as ignoring
  the science does. This library&rsquo;s habit is to refuse both kinds of forcing.</p>
</div>

<h2>Where this translation stands</h2>
<div class="panel prose">
  <p>It renders <em>yom</em> plainly <strong>&ldquo;day&rdquo;</strong> &mdash; the true word, carrying its own
  full range &mdash; and presses no length onto it. It does not tell you the earth is six thousand years old, and
  it does not tell you the &ldquo;days&rdquo; are geological ages. It tells you what the word can mean, what the
  chapter hints, and who has read it which way &mdash; and leaves the weighing to you.</p>
  <p>One thing to know about this site&rsquo;s dates: the traditional years on the
  <a href="chronology.html">chronology</a> (Ussher&rsquo;s <strong>4004 BC</strong>, &ldquo;AM 1&rdquo;) are given
  as <em>the text&rsquo;s own genealogical reckoning</em> &mdash; the number the &ldquo;begat&rdquo; lists add up
  to &mdash; not as a scientific claim about the age of the planet. The long-age reading is fully on the table.
  The verse-by-verse discussion lives in the note at <a href="genesis-1.html#n5">Genesis 1:5</a>.</p>
</div>

<div class="askbar askbar-foot"><a href="ask.html">← More from Ask Mr. Librarian</a></div>"""
    out = page(f"How long were the days of creation? — {SITE_NAME}", body, active="ask",
               desc="How long were the days of creation? The Hebrew word yom, the age of the earth, and the "
                    "ordinary-day, day-age, and literary-framework readings — laid out with their pedigrees "
                    "and left for you to weigh.",
               url="ask-creation-days.html")
    open(os.path.join(OUT, "ask-creation-days.html"), "w", encoding="utf-8").write(out)


def build_contact():
    body = f"""<h1 class="pagetitle">✉️ Ask Mr. Librarian a question</h1>
<p class="lede">A question about the project, a translation choice you'd argue with, a chapter request,
or something you've always wondered about the text — send it in. Good questions become
<a href="ask-enoch.html">Ask Mr. Librarian</a> posts (anonymously unless you say otherwise), and reader
questions are exactly how that series grows.</p>

<div class="panel">
  <form action="{FORM_ENDPOINT}" method="POST" class="askform">
    <input type="hidden" name="_subject" value="Ask Mr. Librarian — a question from the site"/>
    <input type="hidden" name="_template" value="table"/>
    <input type="hidden" name="_next" value="{SITE_URL}/thanks.html"/>
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"/>
    <label>Your name <span class="opt">(optional)</span>
      <input type="text" name="name" placeholder="However you'd like to be credited — or leave blank"/>
    </label>
    <label>Your email <span class="opt">(optional — only needed if you'd like a reply)</span>
      <input type="email" name="email" placeholder="you@example.com"/>
    </label>
    <label>Your question <span class="req">(required)</span>
      <textarea name="question" required rows="7"
        placeholder="Ask anything — a verse, a word choice, a comparison between versions, what's coming next…"></textarea>
    </label>
    <button class="btn" type="submit">Send to the librarian's desk</button>
    <p class="formnote">Sending shows a quick captcha (keeps the robots out of the library), then brings
    you back here. Nothing is posted publicly — questions go straight to Mr. Librarian's desk.</p>
  </form>
</div>"""
    out = page(f"Ask a question — {SITE_NAME}", body, active="contact",
               desc="Send Mr. Librarian a question about the translation, a verse, or the project — "
                    "good questions become Ask Mr. Librarian posts.")
    open(os.path.join(OUT, "contact.html"), "w", encoding="utf-8").write(out)


def build_thanks():
    body = """<h1 class="pagetitle">📬 It's on the librarian's desk</h1>
<div class="panel prose">
  <p><strong>Your question is in.</strong> Thank you — reader questions are the lifeblood of the
  <a href="ask-enoch.html">Ask Mr. Librarian</a> series, and every one gets read. If yours becomes a post,
  it will appear anonymously unless you asked otherwise; if you left an email, you may get a reply
  directly.</p>
  <p>Meanwhile, the shelves are open: the <a href="toc.html">Table of Contents</a> has every chapter
  published so far.</p>
</div>"""
    out = page(f"Question received — {SITE_NAME}", body,
               desc="Your question is on Mr. Librarian's desk.")
    open(os.path.join(OUT, "thanks.html"), "w", encoding="utf-8").write(out)


def build_contact_es():
    """Spanish twin of the contact form, so a Spanish-only reader's 'Preguntar'
    (the top-right utility link) never lands on an English page. Same form endpoint,
    Spanish labels, and its own Spanish thank-you page."""
    body = f"""<h1 class="pagetitle">✉️ Hazle una pregunta a Mr. Librarian</h1>
<p class="lede">Una pregunta sobre el proyecto, una decisión de traducción que te gustaría discutir,
la solicitud de un capítulo, o algo que siempre te has preguntado sobre el texto — envíala. Las buenas
preguntas se convierten en publicaciones del blog de preguntas y respuestas (de forma anónima, salvo que
indiques lo contrario), y las preguntas de los lectores son justamente lo que hace crecer esa serie.</p>

<div class="panel">
  <form action="{FORM_ENDPOINT}" method="POST" class="askform">
    <input type="hidden" name="_subject" value="Mr. Librarian — una pregunta desde el sitio"/>
    <input type="hidden" name="_template" value="table"/>
    <input type="hidden" name="_next" value="{SITE_URL}/thanks.es.html"/>
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off"/>
    <label>Tu nombre <span class="opt">(opcional)</span>
      <input type="text" name="name" placeholder="Como quieras que te mencionemos — o déjalo en blanco"/>
    </label>
    <label>Tu correo <span class="opt">(opcional — solo si quieres una respuesta)</span>
      <input type="email" name="email" placeholder="tu@ejemplo.com"/>
    </label>
    <label>Tu pregunta <span class="req">(obligatorio)</span>
      <textarea name="question" required rows="7"
        placeholder="Pregunta lo que quieras — un versículo, una elección de palabra, una comparación entre versiones, lo que viene…"></textarea>
    </label>
    <button class="btn" type="submit">Enviar al escritorio del bibliotecario</button>
    <p class="formnote">Al enviar aparece un captcha rápido (para dejar a los robots fuera de la biblioteca)
    y luego vuelves aquí. Nada se publica en público — las preguntas van directo al escritorio de Mr. Librarian.</p>
  </form>
</div>"""
    out = page("Haz una pregunta — La Traducción Mister", body, lang="es", url="contact.es.html",
               desc="Envíale a Mr. Librarian una pregunta sobre la traducción, un versículo o el proyecto.")
    open(os.path.join(OUT, "contact.es.html"), "w", encoding="utf-8").write(out)


def build_thanks_es():
    body = """<h1 class="pagetitle">📬 Ya está en el escritorio del bibliotecario</h1>
<div class="panel prose">
  <p><strong>Tu pregunta llegó.</strong> Gracias — las preguntas de los lectores son el alma de esta
  serie, y todas se leen. Si la tuya se convierte en una publicación, aparecerá de forma anónima salvo
  que hayas pedido lo contrario; si dejaste un correo, quizá recibas una respuesta directa.</p>
  <p>Mientras tanto, los estantes están abiertos: la edición en español está creciendo capítulo por
  capítulo en la <a href="es.html">página principal</a>.</p>
</div>"""
    out = page("Pregunta recibida — La Traducción Mister", body, lang="es",
               desc="Tu pregunta está en el escritorio de Mr. Librarian.")
    open(os.path.join(OUT, "thanks.es.html"), "w", encoding="utf-8").write(out)


def _chron_video_credit():
    """The Expedition Bible credit line for the chronology page's field-guide film."""
    for c in VIDEO_CREDITS:
        if c.get("channel") == "Expedition Bible":
            return (f'From <a href="{c["url"]}" rel="noopener"><strong>{c["channel"]}</strong></a> '
                    f'({c["person"]}), the project\'s trusted archaeology shelf: how Old Testament dates '
                    f'are actually established — the outside anchors, and how far back they reach.')
    return "How Old Testament dates are actually established — the outside anchors, and how far back they reach."


def build_chronology():
    """The Chronology — 'where you are in time.' A living page: the two clocks
    (the text's own Anno Mundi count + the traditional Ussher BC dates), an
    era-by-era timeline built from CHRON_EVENTS (grows one entry per chapter),
    and the honest apparatus — the Terah crux, the MT/LXX/Samaritan divergence,
    and what archaeology can and cannot date. Edit CHRON_* in library_data.py
    to grow it; edit this function to reshape the prose."""
    from collections import OrderedDict
    by_era = OrderedDict((k, []) for k, _ in CHRON_ERAS)
    for ev in CHRON_EVENTS:
        by_era.setdefault(ev["era"], []).append(ev)

    sections = []
    for key, label in CHRON_ERAS:
        evs = by_era.get(key) or []
        if not evs:
            continue
        rows = []
        for ev in evs:
            am = ev.get("am") or "—"
            trad = ev.get("trad") or "—"
            if ev.get("coming"):
                where = f'<span class="ch-coming">{html.escape(ev["coming"])}</span>'
                cls = ' class="ch-dim"'
            else:
                book, ch, v = _ref(ev["ref"])
                where = f'<a href="{verse_url(book, ch, v)}">{book_abbr(book)} {ch}:{v}</a>'
                cls = ""
            note = f'<div class="ch-note">{ev["note"]}</div>' if ev.get("note") else ""
            rows.append(f'<tr{cls}><td class="ch-am">{am}</td><td class="ch-trad">{trad}</td>'
                        f'<td class="ch-ev">{ev["event"]}{note}</td><td class="ch-ref">{where}</td></tr>')
        sections.append(f"""<section class="chron-era" id="era-{key}">
<h2>{label}</h2>
<div class="chron-scroll"><table class="chron-table">
<thead><tr><th>Years from Adam<span class="ch-sub">the text's own count</span></th>
<th>Traditional BC<span class="ch-sub">Ussher, 1650</span></th>
<th>Event</th><th>Chapter</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>
</section>""")

    video = youtube_embed("https://www.youtube.com/watch?v=3DJtVlLRMGw",
                          "How we KNOW the dates for the Old Testament! — Expedition Bible (Joel Kramer)")

    body = f"""<h1 class="pagetitle">The Chronology</h1>
<div class="prose chron-intro">
<p class="lede">Where are you in time? Every chapter page now carries a small timeline strip that answers for
that chapter; this page is the whole ledger. It runs on <strong>two clocks, kept honestly apart</strong> —
and a third voice, the archaeologists', explained below.</p>

<div class="chron-clocks">
  <div class="chron-clock">
    <h3>① The text's own count</h3>
    <p>Genesis keeps its own calendar: the begetting-ages of chapters 5 and 11 and the stated ages of the
    patriarchs add up, year by year, from Adam. The first column — <strong>"years from Adam"</strong> (the
    traditional <em>Anno Mundi</em>) — is nothing more than that arithmetic, done on the Masoretic numbers this
    translation is made from. The flood lands in year 1656; Abram leaves Haran in 2023; the covenant of
    circumcision falls in 2047. No outside assumption is added — it is the Bible timing itself.</p>
  </div>
  <div class="chron-clock">
    <h3>② The traditional BC dates</h3>
    <p>The second column gives the dates <strong>Archbishop James Ussher</strong> published in his
    <em>Annals</em> (1650) — creation in 4004 BC, the flood in 2348, Abram's call in 1921 — the numbers the
    margins of old English Bibles carried for centuries. They are a <em>reconstruction built on clock ①</em>
    plus a chain of assumptions about the later periods, and they are offered here as the classic tradition,
    not as fact. (For everything before Terah, Ussher's date is simply 4004 minus the first column; from Abram
    on the two columns run sixty years apart — the Terah crux, below, explains why.)</p>
  </div>
  <div class="chron-clock">
    <h3>③ What the archaeologists can date</h3>
    <p>Absolute, checkable dates enter the Bible's world from <strong>outside sources</strong> — Assyrian
    eponym lists pinned to a solar eclipse (763 BC), Babylonian chronicles, synchronisms with named kings.
    Those anchors reach the era of Israel's monarchy (the battle of Qarqar, 853 BC; the fall of Jerusalem,
    586 BC) and will enter this page when the story does. <strong>The patriarchal age has no such anchor</strong>:
    if Abraham's journeys are history, they sit in the Middle Bronze Age (roughly 2000–1550 BC) — broadly where
    both clocks above put them — but no inscription names him, and this page won't pretend one does.</p>
  </div>
</div>
</div>

{''.join(sections)}

<div class="prose chron-honest">
<h2>The honest apparatus</h2>
<p><strong>The Terah crux (a sixty-year fork).</strong> "Terah lived 70 years, and fathered Abram, Nahor and
Haran" (11:26) — but was Abram the <em>firstborn</em>, or just first-listed? On the plain reading Abram is born
when Terah is 70 (AM 1948) — which has Terah living on in Haran sixty years <em>after</em> Abram's departure.
Stephen's speech in Acts 7:4 says Abram left <em>after his father died</em>, which works only if Abram was born
when Terah was 130 (AM 2008) — and the Samaritan Pentateuch shortens Terah's life to 145 so the plain reading
works instead. Ussher sided with Acts; the first column here keeps the plain arithmetic and flags the fork.</p>
<p><strong>Three Bibles, three totals.</strong> The begetting-ages themselves differ between the ancient
witnesses: the <strong>Masoretic</strong> numbers (used here) put the flood at AM 1656; the
<strong>Septuagint</strong>, whose pre-flood fathers mostly beget a century later, puts it at AM 2242; the
<strong>Samaritan Pentateuch</strong> at AM 1307. Someone in antiquity adjusted the arithmetic — which way, and
why, is argued to this day. The differences are noted, not resolved, exactly as this translation treats every
variant.</p>
<p><strong>Round numbers.</strong> The spans themselves love pattern — 400 years foretold (15:13), 120 years
counted down (6:3), Abram called at 75, a covenant at 99. Ancient chronology often works in schematic, symbolic
figures, and adding them like an accountant may be more precision than the text ever intended. The ledger above
is offered in that spirit: the text's own arithmetic, not an affidavit.</p>
</div>

<div class="prose chron-video">
<h2>How dating actually works — a field guide</h2>
<p>{_chron_video_credit()}</p>
{video}
</div>

<div class="prose chron-roadmap">
<h2>Where this page is going</h2>
<p>The timeline grows one chapter at a time, like everything on this site. Ahead: Isaac, Jacob and Joseph
complete the patriarchal ledger; the Exodus opens the era where the 400 years of Genesis 15:13 come due; and
with the kings of Israel and Judah the <em>third</em> clock finally engages — synchronisms with Assyria and
Babylon that let whole reigns be pinned to checkable dates. When the Gospels arrive in force, the same treatment
applies to Herod, Pilate, and "the fifteenth year of Tiberius."</p>
</div>"""

    out = page(f"The Chronology — {SITE_NAME}", body, active="chronology",
               desc="Where you are in time: the Bible's own year-count from Adam, the traditional "
                    "Ussher BC dates, and what archaeology can and cannot date — one honest timeline, "
                    "growing chapter by chapter.")
    open(os.path.join(OUT, "chronology.html"), "w", encoding="utf-8").write(out)


def check_shelf_density(chapters):
    """The site's promise is 'catalogued & COMPARED' — every chapter's notes weigh
    this translation against the seven-version shelf. This guard makes the promise
    enforceable: a chapter whose notes carry fewer than MIN shelf comparisons
    (<span class="tag t-…"> markers) FAILS the build, the same way a broken anchor
    would. Added 2026-07-16 after an audit found comparison density had decayed
    from 160 tags (Gen 1) to zero (Gen 19 as first shipped). Ledger/genealogy
    chapters that legitimately carry few notes are exempted BY NAME — adding a
    slug there is a conscious editorial decision, not a default."""
    MIN = 3
    EXEMPT = {"gen8", "gen10", "gen11"}   # flood logbook + the two genealogy tables (grandfathered)
    bad = []
    for slug, body in chapters.items():
        n = len(re.findall(r'class="tag t-', body))
        if n < MIN and slug not in EXEMPT:
            bad.append(f"  {slug}: {n} shelf comparison(s) — need ≥{MIN}")
    if bad:
        raise SystemExit("SHELF-DENSITY CHECK FAILED — 'catalogued & compared' means compared:\n"
                         + "\n".join(bad)
                         + "\n(compare against the shelf with tag t-kjv/t-niv/… spans, or consciously exempt the slug)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    args = ap.parse_args()
    chapters = extract_source(args.source)
    check_shelf_density(chapters)
    _render_default_card(os.path.join(OUT, "img", "og-default.png"))
    build_chapter_pages(chapters)
    build_toc()
    build_reading()
    build_index(chapters)
    build_about()
    build_old_testament()
    build_new_testament()
    build_book_intros()
    build_chronology()
    build_ask_enoch()
    build_ask_index()
    build_ask_jesus_god()
    build_ask_jehovah()
    build_ask_creation_days()
    build_ask_newton()
    build_es()
    build_contact()
    build_thanks()
    build_contact_es()
    build_thanks_es()
    n_words, n_refs = build_concordance(chapters)
    n_dict = build_dictionary()
    n_places, n_people = build_encyclopedia()
    n_mapped, n_atlas_places = build_atlas()
    build_library((n_words, n_refs, n_dict, n_places, n_people, len(XREFS), n_mapped, n_atlas_places))
    save_card_manifest()
    report_card_budget()
    print(f"built {len(CHAPTERS)} chapters + core pages + library "
          f"(concordance {n_words}w/{n_refs}refs, dict {n_dict}, ency {n_places}p/{n_people}pp, "
          f"atlas {n_mapped}/{n_atlas_places} mapped, xrefs {len(XREFS)}) from {args.source}")


if __name__ == "__main__":
    main()
