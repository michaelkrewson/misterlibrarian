#!/usr/bin/env python3
"""Build the MisterLibrarian Bible Project static site.

Single source of truth: mstr-trader's dashboard/mister_translation.html
(each chapter lives there as a <div class="chapter-panel" id="chapter-genN">
block). This script extracts every chapter panel and regenerates the public
site: one page per chapter with prev/next navigation, a Table of Contents
with live progress, the home page, and the Dear Mr. Librarian posts.

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
                           CHRON_ERAS, CHRON_CHAPTERS, CHRON_EVENTS, BOOK_INTROS,
                           DICTIONARY_ES, ENCYCLOPEDIA_ES, CHAPTER_ART)

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
SHARE_JS_VER = _asset_ver("share.js")

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
    ("1john1", "1 John", 1, "The warmest and most searching of the letters — and barely a letter at all: no greeting, no name, no address, just a voice that has SEEN and TOUCHED what it preaches. ⚠ It opens like the Gospel of John (\"that which was from the beginning… the word of life\") and then, against secessionists who denied Christ came in the flesh, puts hands on it: \"that which we have heard… seen with our eyes… and our hands HANDLED.\" The eyewitnesses share what they saw so the readers may have FELLOWSHIP (koinōnia) — with them, and so with the Father and the Son. Then the letter's first great declaration: ⚠ \"God is LIGHT, and in him is no darkness at all\" — the first of the Johannine \"God is\" sayings, met by \"God is love\" at the summit (4:8). To walk in the light is to live truthfully, and \"the blood of Jesus his Son cleanses us from all sin\" — a present, continual cleansing, not sinlessness. The chapter closes by quoting and demolishing three slogans of the perfectionist opponents (\"we have no sin\"; \"we have not sinned\") and answering them with one honest admission: \"if we CONFESS our sins, he is faithful and just to forgive.\""),
    ("2john1", "2 John", 1, "The shortest book in the Bible by verse count — one sheet of papyrus from \"the elder\" to \"a chosen lady,\" whom nobody has ever conclusively identified. Truth and love welded together in three verses, then the hard instruction: a travelling teacher who brings a different Christ gets no house and no welcome, because paying for a mission is joining it."),
    ("3john1", "3 John", 1, "The most private document in the Bible — a note from \"the elder\" to one man, Gaius, about a local quarrel. It commands the exact thing 2 John forbade (receive the travelling brothers) because the travellers are the opposite men; and it names Diotrephes, \"who loves to be first,\" a churchman who throws people out of the assembly for the crime of hospitality. It ends: greet the friends by name."),
    ("jude1", "Jude", 1, "The New Testament's fiercest short letter — twenty-five verses from a brother of Jesus who calls himself only 'a slave of Jesus Christ,' urging the church to 'contend for the faith once for all delivered.' A torrent of judgment-examples (the fallen angels, Sodom, Cain, Balaam, Korah), storm-and-sea images (waterless clouds, wandering stars), the archangel Michael disputing over the body of Moses, a prophecy quoted from ENOCH — a book that is not in the Bible — and, at the end, one of Scripture's greatest doxologies."),
    ("rev1", "Revelation", 1, "The unveiling begins — Patmos, the Lord's day, one like a son of man among the lampstands, and the Alpha and the Omega."),
    ("rev2", "Revelation", 2, "The letters begin — Ephesus's lost first love, Smyrna's crown, Satan's throne at Pergamum, and Jezebel of Thyatira."),
    ("rev8", "Revelation", 8, "The Lamb opens the seventh seal, and instead of a seventh horror there is silence in heaven for about half an hour -- one of the least explained moments in the whole book, and the library reports several old guesses rather than settling on one. Seven angels are given seven trumpets; before any sounds, another angel offers incense with the prayers of the saints at the golden altar, likely the same prayers already heard, the martyrs' own 'how long' from chapter 6 -- and then fills the same censer with fire and throws it to earth. The first four trumpets sound: hail and fire mixed with blood burns a third of the earth, rewriting Egypt's seventh plague; a burning mountain turns a third of the sea to blood; a falling star named Wormwood, the Hebrew Bible's own old image for the bitterness of judgment, poisons a third of the waters; a third of the sun, moon, and stars go dark. Where the fourth seal's horseman reached a fourth of the earth, each trumpet now reaches a third -- the same partial-not-total pattern, intensified. The chapter closes on a single eagle -- &#9888; 'angel' in KJV and RV60, following the Textus Receptus; 'eagle' in every other version compared here, following the earlier manuscripts -- crying three woes for what the last three trumpets are still to bring."),
    ("rev7", "Revelation", 7, "Chapter 6 ended on a question -- who is able to stand? -- and this chapter delays the answer further still. Four angels hold back the four winds; the earth, sea, and every tree wait untouched while a fifth angel seals 'the servants of our God' on their foreheads first. A hundred and forty-four thousand are sealed, tribe by tribe, twelve thousand each -- and &#9888; Dan is missing from the list, the sole tribe of Jacob's twelve sons never named here, for reasons the text itself never states. Then a second crowd appears, one no one could count, from every nation and tribe and people and tongue, in white robes with palm branches, crying that salvation belongs to God and the Lamb. An elder explains: these are the ones coming out of the great tribulation, who washed their robes white in the blood of the Lamb -- a paradox the Greek does not soften. They will hunger and thirst no more, sheltered by the one who will 'spread his tabernacle' over them, in language three English versions translate three different ways. The chapter's closing promise, that God will wipe away every tear from their eyes, is not this book's only time -- the same words return, exactly, when the whole vision closes at chapter 21."),
    ("rev6", "Revelation", 6, "The Lamb begins opening the seven seals, one by one. Four horsemen ride out in turn, each summoned by a living creature's single word, 'Come': a white horse whose rider carries a bow and a crown, conquering; a fiery red horse that takes peace from the earth; a black horse whose rider carries scales, pricing a day's food at a day's wage while sparing the oil and the wine; and a pale horse named Death, with Hades following, given power to kill a fourth of the earth. &#9888; Who the first rider is, the text never says, and the library reports two live readings rather than choosing one -- conquest itself, or Christ going out to conquer. The fifth seal opens on the souls of the slain under the altar, crying the Psalter's own old question, 'how long,' and told to rest a little longer until a fixed number still to come is complete. The sixth seal shakes the sky itself -- sun black, moon to blood, stars falling, the heavens rolled up like a scroll, quoting Joel and Isaiah directly -- until every rank of humanity, kings to slaves, is begging the mountains to fall on them and hide them, the exact plea Jesus told Jerusalem's weeping women they would one day make. The chapter's last line is a question nothing in it answers: who is able to stand?"),
    ("rev5", "Revelation", 5, "The scroll from chapter 4's closing note is now in the hand of the one on the throne, sealed with seven seals, and a mighty angel asks who is worthy to open it. No one in heaven or on earth or under the earth can &mdash; not until an elder tells John to stop weeping: &lsquo;the Lion of the tribe of Judah, the Root of David, has conquered.&rsquo; John turns to look at the Lion, and what he sees is a Lamb, standing as though slain. The word is <em>arnion</em>, a diminutive John's Gospel never uses of Christ, and this book will repeat it twenty-eight more times, all the way to its final chapters. The Lamb takes the scroll, and the whole scene erupts into song &mdash; first the twenty-four elders and four living creatures, then countless angels, then &lsquo;every creature in heaven and on earth and under the earth and in the sea,&rsquo; declaring the Lamb worthy for a different reason than chapter 4 gave God: not for creating, but for being slain and buying a people &lsquo;from every tribe and tongue and people and nation.&rsquo; &#9888; Verses 9-10 carry a real textual crux: KJV, following the Textus Receptus, reads first person throughout (&lsquo;hast redeemed <em>us</em>&hellip; <em>we</em> shall reign&rsquo;); the earlier manuscripts behind ASV, NIV and ESV read third person (&lsquo;persons&hellip; they will reign&rsquo;) &mdash; the reading this translation follows."),
    ("rev4", "Revelation", 4, "The seven letters are complete, and the book's next movement opens exactly where chapter 3's own closing note said it would: a door standing open in heaven. John is caught up and sees a throne — never physically described, only compared to the flash of gemstones and a rainbow's color, the same restraint the whole Bible keeps around the divine form. Twenty-four elders in white, seven flames burning that are 'the seven spirits of God' (named here for the third time), a sea of glass, and four living creatures covered in eyes. ⚠ KJV alone calls them 'beasts' — everyone else, in both languages, reads 'living creatures,' the plain sense of the Greek. They are not John's invention: the four faces (lion, ox, man, eagle) come from Ezekiel's throne-vision, where each creature carried all four at once; the six wings and the endless cry come from Isaiah's seraphim, crying the same three words this chapter now repeats — 'Holy, holy, holy.' The elders respond by casting their own crowns before the throne and declaring God worthy for one reason: he created all things. It is the first of two worship-hymns this book will sing to two different thrones that turn out to be one — chapter 5's Lamb will be found worthy for an entirely different reason, not for making, but for being slain."),
    ("rev3", "Revelation", 3, "The letters conclude — Sardis, Philadelphia, Laodicea. &#9888; Sardis gets no praise at all: &ldquo;you have a name that you live, and you are dead,&rdquo; a city famously stormed twice by night because its guards stopped watching the one climbable approach. Philadelphia, alone with Smyrna, gets no complaint: &ldquo;an open door, which no one is able to shut&rdquo; &mdash; the phrase that became Christian shorthand for opportunity &mdash; and a promise of being made a pillar, spoken to a city still rebuilding from an earthquake. Then Laodicea, wealthy, self-satisfied, &ldquo;neither cold nor hot&rdquo; &mdash; a city whose own aqueduct water arrived lukewarm from Hierapolis's hot springs and Colossae's cold ones, and whose three great boasts (banking, black wool, eye-salve) are answered one by one: gold refined by fire, white garments, salve that actually heals. And the most reproduced verse in the chapter, &ldquo;I stand at the door and knock&rdquo; (v20), addressed not to an outsider but to the church itself, on the far side of its hardest rebuke."),
    ("rev21", "Revelation", 21, "A new heaven and a new earth, no more sea, and every tear wiped away \u2014 and \u26a0 the word for \u201cnew\u201d is a decision the whole book keeps: KAINOS nine times, NEOS never, in a New Testament where NEOS turns up twenty-seven times elsewhere. New in kind, not new in time. \u26a0 The tent of God is with humanity, and the verb is the one from John 1:14 \u2014 it occurs in two books only. The city is a CUBE, 12,000 stadia every way, and the only other cube in the Bible is the Holy of Holies. There is no sanctuary in it. The gates never shut, because there is no night. \u26a0 And the list at verse 8 opens with THE COWARDLY \u2014 the same word Jesus used in his last sentence to his friends."),
    ("rev22", "Revelation", 22, "The last chapter of the Bible \u2014 the river, the tree of life on both banks, and leaves for the healing of the nations. \u26a0 Two variants here are worth more than most whole books of textual notes. Verse 14 is \u201cthose who WASH THEIR ROBES\u201d in every critical text and in the Byzantine majority text, and \u201cthose who DO HIS COMMANDMENTS\u201d only in the Textus Receptus behind the King James. And verse 19 reads TREE of life in every Greek witness \u2014 the KJV\u2019s \u201cbook of life\u201d comes from Erasmus in 1516 back-translating from the Latin Vulgate, because the last leaf of his only manuscript was missing. So the sentence forbidding anyone to add to the book contains, in the most influential English Bible ever printed, a word that was added to it. Plus Daniel told to seal his book and John told not to, and a final benediction the manuscripts never quite agreed on."),
    ("dan1", "Daniel", 1, "Babylon takes its first captives — four renamed youths, a ten-day test of vegetables and water, and 'ten hands better' than the magicians."),
    ("dan2", "Daniel", 2, "Nebuchadnezzar's dream, and an impossible test — tell me the dream I will not tell you, or die. Daniel prays, the mystery is revealed, and he sings: God 'removes kings and sets up kings.' Then the dream itself: a great statue of gold, silver, bronze, and iron, its feet iron mixed with clay — and a stone cut without hands that shatters it all and grows into a mountain filling the earth. The four kingdoms, and the everlasting fifth; and the chapter where the book turns from Hebrew to ARAMAIC."),
    ("dan3", "Daniel", 3, "Nebuchadnezzar builds an image entirely of gold — his own unstated answer to the dream one chapter before — and demands the whole province bow at the sound of the orchestra. Three men refuse: 'our God is able to deliver us; but if not, we will not serve your gods.' The furnace heated seven times hotter kills the men who threw them in and leaves a fourth figure walking free inside the fire, 'like a son of the gods.' The king who tried to execute them ends the chapter blessing their God by name."),
    ("dan11", "Daniel", 11, "The angel's scroll of wars — Persia, Alexander, the kings of south and north, the abomination that desolates — and the seam where history becomes hope."),
    ("dan12", "Daniel", 12, "The sleepers in the ground of dust wake — everlasting life named for the first time, the sealed book, two numbers nobody has decoded, and a lot promised at the end of the days."),
    ("mat1", "Matthew", 1, "The New Testament opens on a genealogy — 'the book of the genesis of Jesus Christ, son of David, son of Abraham' — the word that opens the Bible (Genesis) chosen to open the Gospel. Forty-two generations in three panels of fourteen, from Abraham to David, David to the exile, the exile to the Christ — and ⚠ four women break into the list of fathers, three of them Gentile and every one touched by scandal: Tamar, Rahab, Ruth, and 'the wife of Uriah'. The count is a designed thing (fourteen is the number of DAVID's name in Hebrew), not a registry: it drops three kings, runs the royal line through the cursed Jechoniah, and breaks its 'fathered… fathered' drumbeat at the last link, where Jesus is not fathered by Joseph but 'BORN of' Mary. ⚠ Then the birth itself: Mary found with child 'of the Holy Spirit'; Joseph, a righteous man, resolving to divorce her quietly until an angel stops him in a dream; the name JESUS unfolded as 'YHWH saves' ('he will save his people from their sins'); and Isaiah's virgin-sign landed as EMMANUEL, 'God with us' — the name that brackets the whole Gospel, which will close on 'I am with you always'."),
    ("mat2", "Matthew", 2, "The nativity's dark half. Magi from the east — astrologer-priests of Persia, not kings, and Matthew never counts them — arrive in Jerusalem asking for a king who was BORN one, which is the one thing Herod, voted his title by the Roman Senate, was not; and the city that should have rejoiced is 'shaken' along with him. ⚠ The chief priests answer correctly out of Micah and then nobody walks the six miles to look, while the men with a star and no Scripture cross half the east and fall down in a HOUSE (there is no stable here and no shepherds — those are Luke's, and the two accounts never overlap). Then the chapter turns: Herod's 'secretly' is the same word as Joseph's 'quietly' one chapter earlier, and the time he ascertains 'exactly' becomes the width of the killing. ⚠ Four dreams, four withdrawals, and four quotations — Bethlehem, Egypt, Ramah, Nazareth — three of them famously difficult: 'out of Egypt I called my son' is a verse about ISRAEL, the angel's 'those who were seeking the child's life are dead' is Moses' own marching orders quoted without a footnote, and 'he shall be called a Nazarene' is a prophecy that exists in no book. Rachel, buried at Bethlehem, weeps over its children and will not be comforted — the same two words Jacob used at the pit."),
    ("mat3", "Matthew", 3, "The wilderness and the water — the next two steps of the exodus pattern chapter 2 set going. A man in camel's hair and a leather belt appears in the Judean desert with one sentence, 'Repent, for the kingdom of the heavens has drawn near' — which is, word for word, the sentence Jesus himself begins with at 4:17. ⚠ The costume is a quotation: 2 Kings 1:8 dresses Elijah in exactly those clothes, and Malachi had promised Elijah before the day of the Lord. The Isaiah verse John is identified with carries the most famous punctuation argument in the Bible — the Hebrew's parallel puts the wilderness with the ROAD ('in the wilderness prepare the way'), the Greek puts it with the VOICE — and Matthew quietly reads 'his paths' where Isaiah and the Greek both read 'our God'. ⚠ Then the Pharisees and Sadducees arrive together, which almost never happens, and are called a brood of vipers and told that God can raise children for Abraham out of the stones at their feet — a pun that works only in Hebrew (banim / avanim). And at the close, the difficulty every reader feels, which only Matthew records: John tries to stop him. 'I have need to be baptized by YOU, and you come to me?' Jesus' first recorded words in this Gospel are the answer — 'allow it now, for thus it is fitting for us to fulfil all righteousness' — and then a voice out of the heavens says a sentence assembled from three Scriptures at once: the royal son of Psalm 2, the beloved (only) son of Genesis 22, and the servant of Isaiah 42, whose very next line is 'I have put my spirit upon him.'"),
    ("mat4", "Matthew", 4, "The wilderness again — but forty days of it, and Matthew alone writes 'forty days AND FORTY NIGHTS', which is Moses' phrase on the mountain, where 'bread he did not eat'. Three temptations, each answered out of DEUTERONOMY, the book of the wilderness generation; and the tempter opens on the last thing God said, 'IF you are the Son of God'. ⚠ He also quotes Scripture — and drops a clause. Psalm 91 promises the angels will guard you 'in all your ways'; the devil goes straight from the first line to the third and leaves those four words out, which are precisely the ones that would have answered him. ⚠ Then the word this library has tracked since the magi: the devil asks to be BOWED TO (proskyneō — the magi's verb, and Herod's lie), and Jesus answers with the one verse in the Law that names its object. Afterwards, a fourth 'withdrawal' — the nativity's verb — takes him north to Capernaum, and Isaiah's 'Galilee of the NATIONS' is quoted over a mixed borderland (Hebrew 8:23–9:1, where the people are WALKING in darkness and Matthew has them SITTING). The ministry then opens with the Baptist's own sentence, word for word, immediately after the Baptist is arrested for saying it — and four fishermen leave two boats, the Greek quietly distinguishing the hand-net of the poorer pair from the family firm with a hull, a father, and hired men."),
    ("mat5", "Matthew", 5, "The Sermon on the Mount opens in red letters — eight Happy-sayings, salt and light, not one iota, and six rounds of 'You have heard… but I say': anger, lust, oaths, the other cheek, love for enemies."),
    ("mat6", "Matthew", 6, "The Sermon's middle chapter — alms, prayer, and fasting in secret; the Lord's Prayer and its famous missing doxology; treasure, the undivided eye, Mammon — and the birds and the lilies."),
    ("mat7", "Matthew", 7, "The Sermon's finale — the splinter and the beam, ask-seek-knock, the Golden Rule signed, the narrow gate, wolves and fruit, 'I never knew you' — and the house on the rock."),
    ("mat8", "Matthew", 8, "He comes DOWN from the mountain of the Sermon, and the healing half of the summary at 4:23 begins — chapters 5-7 were the teaching, chapters 8-9 are this. A leper bows (proskyneō, the magi's verb, a fourth time) and doubts not the power but the WILL: 'if you are willing' — 'I am willing'; and then Jesus TOUCHES him, which under the Law transmits uncleanness to the toucher, and Matthew reports none travelling that way. ⚠ Then a Roman officer uses the Baptist's exact words, 'I am not worthy' (3:11, of the sandals; here, of his own roof), and argues from a chain of command rather than from merit — the one inference Jesus is said to marvel at — which draws the hardest sentence yet: many will recline with the patriarchs from east and west, and 'the sons of the kingdom' be put outside. ⚠ Peter has a mother-in-law, which means Peter has a wife; and Isaiah 53:4 is quoted over an evening of house calls, following the HEBREW ('our diseases… our pains') where the Greek Old Testament turns the first noun into 'sins'. The first 'Son of Man' in the Gospel belongs to a man with nowhere to sleep. ⚠ Matthew calls the storm an EARTHQUAKE (seismos — Mark and Luke both say 'squall'), the same word he uses at the crucifixion and the empty tomb; Jesus REBUKES the sea with the verb used on demons, and nobody in the boat concludes anything — they ask. And where Mark has one demoniac, Matthew has TWO; the chapter that opened with crowds following ends with a whole town asking him to leave."),
    ("mat9", "Matthew", 9, "The healing half keeps going — a paralytic forgiven before he is healed ('which is easier to say?'), a tax collector named Matthew called from his own booth and dinner with 'sinners', the bridegroom question and new wine in old skins, a ruler's daughter and a woman healed by a touch of the fringe, two blind men crying 'Son of David', a mute man freed and the first charge that the power comes from the ruler of demons — and at the end, word for word, the summary sentence of 4:23 returns to close the frame around the Sermon and the healings, ending on a prayer answered by name next chapter: 'the harvest is plentiful, but the laborers are few.'"),
    ("mat10", "Matthew", 10, "The Mission Discourse — the Twelve named (six pairs, a Zealot and a tax collector among them, Judas placed last with the one clause no one else gets) and sent out with authority but no money, no bag, no staff: 'freely you received, freely give.' Sheep among wolves, floggings and kings, families turned into enemies (quoting Micah almost word for word), the first mention of the cross anywhere in this Gospel — before Jesus has said one word about his own — and 'whoever loses his life for my sake will find it.' Ends on the smallest reward named: a cup of cold water, not lost."),
    ("mat11", "Matthew", 11, "John, now imprisoned, sends to ask the question his own ministry never quite let him ask aloud: 'Are you the one who is to come, or should we look for another?' Jesus answers out of Isaiah's own vocabulary, then turns to the crowds — not a reed, not soft clothing, but a prophet and more than a prophet — quotes a second messenger-prophecy over him, and calls him Elijah, 'if you are willing to receive it.' ⚠ One of the New Testament's most argued single verses sits at the center: 'the kingdom of the heavens suffers violence' — readings given, none forced. Children refusing to dance to either tune in the marketplace; a real textual crux over whether wisdom is vindicated by her deeds or her children; woes on Chorazin, Bethsaida and Capernaum measured against Tyre, Sidon and Sodom, with a king of Babylon's own boast turned on a fishing town; a prayer that hides these things from the wise and reveals them to infants; and the Gospel's gentlest words, unparalleled anywhere else — 'Come to me, all who labor and are heavy-laden' — closing on a yoke that is kind."),
    ("mat12", "Matthew", 12, "Grain plucked on the sabbath answered with Hosea 6:6 a second time, exactly as promised — and 'something greater than the temple is here.' A withered hand healed, and for the first time the Pharisees' word is 'destroy,' not merely 'accuse.' Isaiah's Servant Song quoted at length — the longest Old Testament citation in this Gospel — a servant who 'will not quarrel nor cry out.' ⚠ The Beelzeboul charge, planted at 9:34 and named at 10:25, finally gets its full scene: a divided kingdom cannot stand, and 'the kingdom of God has come upon you.' ⚠ The blasphemy of the Spirit — the one sin not forgiven, 'in this age or the age to come' — given with readings, not a verdict. John's own 'brood of vipers' comes back on Jesus' lips against the same opponents; a tree known by its fruit; every idle word weighed. The sign of Jonah demanded and given — three days and three nights, and Nineveh and the queen of the south rising to condemn 'this generation.' And it closes on a redefinition of family itself: 'whoever does the will of my Father… is my brother and sister and mother.'"),
    ("mat13", "Matthew", 13, "The Parables discourse — seven of them in one sitting, opening with the Sower and its four soils, and a hard answer to 'why parables?': Isaiah's ancient hardening prophecy, quoted with its command softened to a description, presented with readings rather than a verdict. ⚠ The Weeds sown among the wheat by an enemy at night — darnel, a poison look-alike no one can safely pull early — left to grow until a harvest with its own reapers. The Mustard Seed's imperial tree-imagery borrowed for the smallest possible seed; the Leaven hidden in 'three measures' of flour, the identical rare word already met at Sarah's tent (Genesis 18:6). A fulfillment formula that names no prophet, quoting a psalm of Asaph against a minority reading that supplies 'Isaiah.' The Weeds explained — sons of the kingdom, sons of the evil one, a field that is the whole world — then Hidden Treasure and the Pearl, one found by accident and one by a lifetime's search, both ending the same way. The Net, and a scribe 'trained for the kingdom' who may well be Matthew's own self-portrait. And it closes at Nazareth, rejected in his own hometown, where — a promise from last chapter paid in full — his brothers are finally named: James, Joseph, Simon, and Judas."),
    ("mat14", "Matthew", 14, "A birthday banquet turns into an execution — Herod's rash oath, a daughter coached by her mother, and John the Baptist's head on a platter, in a flashback Matthew steps back to tell before catching up to 'now.' ⚠ Grief drives Jesus into his seventh withdrawal in this Gospel, and instead of solitude he finds a crowd he has compassion on — five loaves and two fish, a blessing, and twelve baskets left over from five thousand fed, the vocabulary itself (a small Jewish hand-basket, not the larger one a Gentile crowd will get next chapter) quietly marking who is being fed. Then a boat fighting the wind till the fourth watch of the night, Jesus walking on the sea, and the disciples' cry of 'a ghost!' answered with 'Take heart, it is I' — the same courage-word already given a paralyzed man and a bleeding woman, now spoken by the one doing something the Old Testament reserves for God alone. ⚠ Peter asks to come, gets one word back — 'Come' — and is out of the boat before he starts to sink: 'Lord, save me,' the same verb as Jesus' own name, and 'you of little faith, why did you doubt?', a rebuke that pairs with a verb so rare it sounds only one more time in the whole New Testament. No storm-rebuke this time, only presence — and a bow in the boat finally paired, after six earlier bows across this Gospel, with the words it was always waiting for: 'truly you are the Son of God.' It closes on a whole region reaching for the fringe of his garment."),
    ("mark1", "Mark", 1, "The most breathless of the four Gospels starts already at a run — no birth, no genealogy, just a grown man at a river and the word 'immediately' eleven times over. The heavens are TORN open at the baptism (the same violent verb as the temple curtain at the end), a demon is the first to name Jesus correctly, and a leper is healed by a man 'moved with anger' who reaches across the line and touches him."),
    ("mark2", "Mark", 2, "Five collisions in one chapter, and the first hint that this is going to end badly. ⚠ Four men take a roof apart &mdash; Mark uses two verbs for it, un-roofing and DIGGING, which is exactly how a Galilean mud-and-brushwood roof comes off, where Luke retelling it has them go down through TILES. The man is lowered on a <em>krabattos</em>, a straw pallet, a low word both Matthew and Luke replace with a proper bed; this translation keeps the mat. Then a sentence that breaks in half mid-clause and is left broken. ⚠ A tax collector is called from his booth and Mark names him LEVI son of Alphaeus, where the Gospel of Matthew names him Matthew &mdash; with the second half of the puzzle stated: Mark&rsquo;s own list of the Twelve has no Levi in it. A bridegroom who will be TAKEN AWAY, three words long, the first shadow in the book. And then ⚠ &ldquo;in the time of Abiathar the high priest&rdquo; &mdash; where 1 Samuel says the priest was AHIMELECH and Abiathar is his son, laid out rather than patched, with the evidence against it (Matthew and Luke both drop the phrase) and the real defence for it (Mark uses the same construction at 12:26 to mean &ldquo;in the passage about&hellip;&rdquo;). The chapter ends on the sentence no other Gospel kept: the sabbath came into being for the human being, and not the other way round."),
    ("mark4", "Mark", 4, "The boat kept ready at 3:9 finally gets used: Jesus teaches an entire shoreline crowd from the water, starting with a sower whose seed lands on four kinds of ground it cannot be told apart from until the harvest is in. Then the disciples ask why he speaks in parables, and get the hardest sentence in the chapter &mdash; parables are given so THAT outsiders may see and not perceive, hear and not understand, &lsquo;lest they should turn and be forgiven.&rsquo; &#9888; Matthew's version of the same moment quotes Isaiah as fulfilled prophecy, framed with BECAUSE; Mark's Jesus states it as his own purpose, with no citation at all &mdash; a real difference between the two Gospels, not a translator's choice. A lamp and a measure follow, both sayings that surface in entirely different settings in Matthew's Sermon on the Mount. Then a parable found only in Mark: a farmer scatters seed and the earth bears fruit AUTOMATICALLY, he does not know how &mdash; and a mustard seed, proverbially the smallest a Galilean farmer would plant, becomes the largest garden plant there is. The chapter ends on a lake: a squall fills the boat, Jesus sleeps through it, and when woken he REBUKES the wind and orders the sea, &lsquo;Be muzzled&rsquo; &mdash; the identical command, the identical verb, he already gave an unclean spirit at 1:25. The disciples' own fear and unbelief close the chapter, still asking the question it never answers: who is this?"),
    ("mark3", "Mark", 3, "The plot to kill him is formed six verses in, by a coalition that should not exist. ⚠ Jesus looks round at them WITH ANGER &mdash; and unlike the disputed anger at 1:41 this one is textually secure, which is the best corroboration chapter 1&rsquo;s harder reading could get. Matthew deletes the look and the emotion; Luke keeps the looking-round, drops the feeling, and four words later hands the fury to the OPPONENTS instead. Then the Twelve are MADE &mdash; the plain verb, unsoftened &mdash; and among them two men get a nickname nobody ever uses again. ⚠ And then the two verses neither Matthew nor Luke has in any form: his own family come to SEIZE him, saying he is out of his mind. Mark wraps the Beelzebul charge inside that scene &mdash; the first clear instance of the sandwich he builds this whole Gospel out of &mdash; so that the family&rsquo;s verdict and the scribes&rsquo; verdict are read through each other. ⚠ The unforgivable saying turns on one disputed noun: an eternal SIN, a condition that does not stop, against the later text&rsquo;s eternal JUDGEMENT, which is where &ldquo;damnation&rdquo; comes from. And the chapter ends with his mother outside a circle and the word given to whoever is sitting inside it."),
    ("luke1", "Luke", 1, "The longest chapter in the Gospels and the songbook of the church — two annunciations set against each other (a priest struck dumb for doubting, a girl in Nazareth blessed for believing), the leap in Elizabeth's womb, and two of the great canticles: Mary's Magnificat ('he has brought down rulers from thrones and lifted up the lowly') and Zechariah's Benedictus ('the dawn from on high')."),
    ("luke2", "Luke", 2, "\u26a0 There is no inn in this chapter, and Luke has a word for inn \u2014 he uses it eight chapters later, in the good Samaritan. The word here is KATALYMA, a guest room, which is what Luke calls the upper room of the Last Supper. There is no innkeeper either; he arrives with the mediaeval mystery plays. \u26a0 One final sigma decides what the angels sang: EUDOKIAS gives peace to the people God has favoured, EUDOKIA gives the King James \u201cgood will toward men\u201d, and the word is used nine times in the New Testament with God as its owner every other time. Simeon\u2019s song is the vocabulary of a slave being manumitted, his sword is the two-handed one Revelation uses six times, and Anna belongs to a tribe that had been gone seven hundred years. Plus the hardest date in the New Testament: Quirinius governed Syria in AD 6 and Herod died in 4 BC."),
    ("jer1", "Jeremiah", 1, "The call of Jeremiah — the longest, most turbulent prophetic career in the Bible opens on a boy who says 'I am only a youth.' Known before the womb and made 'a prophet to the nations,' his mouth is touched and filled, and he is charged with the six verbs that are the program of the whole book: to uproot and to tear down, to destroy and to overthrow, to build and to plant. Two visions seal it — an almond branch (God WATCHING over his word) and a boiling pot tilting from the north (the disaster coming) — and a frightened boy is made an iron pillar."),
    ("jer2", "Jeremiah", 2, "The book's actual opening argument, following directly after the call: Jehovah remembers the loyal love of Israel's bridal-and-wilderness years before a single charge is named &mdash; then asks a question the chapter never lets anyone answer, &lsquo;what fault did your fathers find in me?&rsquo; The central image is a plumbing failure played for a kind of dark comedy: abandoning a self-renewing fountain of living water to dig cracked cisterns by hand. &#9888; A real ketiv/qere lands on the chapter's most loaded line &mdash; the Hebrew text WRITES &lsquo;I will not serve&rsquo; right after &lsquo;I broke your yoke,&rsquo; but tradition READS an unrelated verb, &lsquo;I will not transgress&rsquo;; this translation follows the ketiv and the majority of the shelf. The same yoke-breaking language recurs, verbatim, at the already-shipped Jeremiah 30:8 &mdash; one liberation already accomplished here, a second one still promised there. Camel, wild donkey, thief, and a father made of wood: five images in a row, each catching the same unfaithfulness from a different, increasingly undignified angle."),
    ("jer18", "Jeremiah", 18, "The potter's house — sent down to a workshop on the city's edge, Jeremiah watches a vessel go wrong under the hand and be thrown again, and hears the most CONDITIONAL sentence in the prophets: “if that nation turns back from its evil… then I relent.” The clay's answer is one flat word — “Hopeless” — refusing an offer that was still open. Then the potter's own verb turns on them (“I am FORMING evil against you”), the fourth “device” in the chapter is aimed at the prophet himself, and it closes in an imprecatory prayer this library will not soften. ⚠ Two genuine cruxes are left standing with their pedigrees and no vote: verse 14's “rock of the field” and verse 17's “back and not the face.”"),
    ("jer19", "Jeremiah", 19, "The potter's flask comes back FIRED — bought and smashed beyond mending at the Potsherd Gate over the valley of Ben-Hinnom, Baal named outright at last, the days coming when the place is called the valley of slaughter, and the sentence carried out of the valley and into the temple court itself."),
    ("jer20", "Jeremiah", 20, "Pashhur and the stocks — the prophet renames his jailer Terror-All-Around, names Babylon at last, confesses the fire shut up in his bones — and curses the day he was born."),
    ("jer21", "Jeremiah", 21, "The final siege — Zedekiah's delegation asks for a miracle and hears the bleakest answer in the book: the Exodus formula aimed inward, the way of life through the enemy camp, and fire for the cedar forest."),
    ("jer22", "Jeremiah", 22, "The tariff of the last kings — Shallum carried to Egypt, Jehoiakim's donkey-burial, and Coniah the signet torn off God's right hand; 'is that not to know me?' and 'write this man childless.'"),
    ("jer23", "Jeremiah", 23, "Woe to the shepherds — and then the promise against them: a righteous BRANCH raised up for David, whose name corrects the reigning king's own ('Jehovah is our Righteousness'). Then the chapter turns on Jeremiah's own profession and does not stop for twenty-eight verses: prophets who fill their hearers with vapor, who preach peace to people who despise God, who steal each other's oracles and keep the rubber stamp — 'declares Jehovah' — after dropping the name. The test is one question, 'who has stood in the COUNCIL of Jehovah?', and one falsifiable result: had they been in it, they would have turned the people back. Straw against grain, a word like fire and like a hammer that shatters rock, a God you cannot hide from — and a chapter-long pun on the word BURDEN that ends by confiscating it. ⚠ Two genuine cruxes are left standing with their pedigrees and no vote: verse 33's 'what burden!' versus the ancient versions' 'YOU are the burden,' and verse 39's forget-or-lift."),
    ("jer29", "Jeremiah", 29, "Jeremiah's letter to the exiles in Babylon: build houses, plant gardens, seek the shalom of the city that deported you \u2014 and the most-quoted verse on the internet, read in the plural and in its seventy-year context."),
    ("jer31", "Jeremiah", 31, "The Book of Consolation's center: Jehovah builds virgin Israel again, Rachel weeps at Ramah for children who will return, Ephraim is asked whether he is a precious son \u2014 and Jehovah promises a NEW COVENANT, law written on the heart, sin remembered no more. The single longest Old Testament quotation anywhere in the New Testament (Hebrews 8) starts here."),
    ("prov1", "Proverbs", 1, "The prologue to wisdom — the book's whole toolkit in seven verses, 'the fear of Jehovah is the beginning of knowledge,' a father's warning against the gang, and Lady Wisdom crying aloud in the streets."),
    ("prov31", "Proverbs", 31, "\u26a0 Chayil is a FORCE word \u2014 what an army is called, what valour is, what wealth and capability are \u2014 and eshet chayil (v10) is a WOMAN OF VALOUR, not a character reference. The shelf splits five ways on that one word: KJV 'virtuous', ASV 'worthy', NWT 'capable', TNM 'competente' \u2014 and only RV 1909 keeps the force, with 'Mujer fuerte'. The register is not an accident: her husband lacks no SHALAL, plunder (v11), she girds her loins (v17), and she gives PREY to her household (v15). \u26a0 The word even turns around inside the chapter \u2014 v3, in the separate oracle a queen mother teaches King Lemuel, warns him not to give his CHAYIL to women. Read as a list of activities, vv13-24 describe a business: importing like a merchant fleet, buying and developing land out of her own profits, checking her margin, and selling wholesale to a Canaanite shipper. She laughs at the last day (v25). And the shape matters: vv10-31 are a COMPLETE acrostic, alef to tav with no irregularity at all, which reads far more naturally as praise built to be memorable than as a list of requirements \u2014 and only the NWT and TNM tell the reader it is there."),
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
    ("exod15", "Exodus", 15, "The Song of the Sea — one of the oldest pieces of poetry in the Bible, and the first place the short divine name YAH appears anywhere in it ('my strength and song is Yah'), a line Isaiah 12:2 and Psalm 118:14 later quote back word for word. Eighteen verses of pure victory poem: Jehovah is called a MAN OF WAR outright, the sea piles up at the blast of his nostrils, and 'who is like you among the gods' becomes Mi Chamocha, a line still recited daily in Jewish morning prayer three thousand years later. Then Miriam — the first person in the Bible called a prophetess — answers with a two-line refrain some scholars think is actually the older, original song, before the narrative resumes on foot: three dry days, bitter water at Marah sweetened by a tree, and 'I am Jehovah your healer,' the first time God claims the title as his own name."),
    ("exod16", "Exodus", 16, "Six weeks out of Egypt, the people grumble for the pots of meat they left behind — a Hebrew verb that falls nine times in eleven verses, the densest repetition in the book so far. The answer is quail, and a flake on the ground so strange that everyone asks the same question, MAN HU, 'what is it?' — and that very question becomes the substance's name three verses before the naming actually happens. It cannot be hoarded (what's left rots by morning) and it cannot be measured unfairly (whoever gathers much has nothing left over, whoever gathers little has no lack) — except on the sixth day, when a double portion survives the night clean, because the seventh day is a SABBATH, spoken here as a noun for the first time in the Bible, four chapters before the Ten Commandments legislate it. A jar of it is set aside before the Testimony, kept for forty years so it could never be eaten."),
    ("exod19", "Exodus", 19, "Israel reaches Sinai, and everything in this chapter happens before a single commandment is given. Jehovah's offer runs on what has already happened — 'you have seen what I did to the Egyptians, and how I bore you on eagles' wings' — and a proposal, not yet a law: keep the covenant, and become his ‘treasured possession’ among all peoples, a ‘kingdom of priests and a holy nation.’ The people accept before they know the terms. Then three days of preparation — wash your garments, do not go near a woman, boundaries set around the mountain with a death penalty for touching it, carried out from a distance so that no one who executes the sentence has to cross the same line. ⚠ And then the mountain itself answers: thunder, lightning, a thick cloud, a trumpet blast that grows louder with no human trumpeter, smoke like a furnace, the whole mountain shaking. Moses climbs it and comes back down three separate times in this one chapter, each trip circling back to the same warning — keep the people back, sanctify the priests, let no one break through to look. The danger named is not disobedience. It is curiosity."),
    ("exod18", "Exodus", 18, "Jethro brings Moses' wife and two sons back to him — Gershom, named at birth ('a sojourner there'), and a brother named for the first time in the whole Bible, decades after the fact: Eliezer, 'my father's God was my help.' Jethro hears the whole story and reaches his own verdict: 'now I know that Jehovah is greater than all gods' — a comparative claim from a Midianite priest, made by argument rather than decree. ⚠ He then takes the offering himself and presides over a sacrificial meal Aaron and Israel's elders simply attend — before Aaron has any priesthood to speak of. The next day he watches Moses judge the whole nation alone, morning to evening, and says the thing nobody else had: 'the thing that you are doing is not good... you will surely wear yourself out.' The fix is the Bible's first management lesson — able men who fear God, love truth, and hate a bribe, set as rulers of thousands, hundreds, fifties, and tens, so that only the hard cases ever reach Moses at all. ⚠ And a puzzle in the calendar: this chapter's own language already has Moses making known 'the statutes of God and his laws' — before Sinai, one chapter away, ever gives them."),
    ("exod17", "Exodus", 17, "No water at Rephidim, and the people who were just fed manna reach for the same grumbling verb they used the chapter before. Moses strikes the rock at Horeb with the staff that once turned the Nile to blood, and names the place MASSAH and MERIBAH — testing and strife, one event named twice over in two different roots. Then Amalek attacks, and a man with no introduction at all is handed an army: Joshua's first appearance anywhere in the Bible, while Moses' raised hands — held up by Aaron and Hur when they grow too heavy to lift alone — decide a battle no tactics are ever described for. It ends on the hardest line in the chapter: a word that occurs exactly once in the whole Hebrew Bible, translated here 'a hand upon the throne of Yah,' which the shelf itself cannot agree how to resolve."),
    ("exod20", "Exodus", 20, "The Ten Commandments \u2014 and the chapter that shows why TEN is a decision rather than a reading. The Hebrew runs 22 verses where English Bibles print 26, four commandments sit inside a single verse (separated not by verse numbers but by the scribes' paragraph marks), and the same unaltered text is counted three different ways by the Jewish, Catholic-Lutheran, and Reformed traditions \u2014 which is why 'the second commandment' means different things to different readers. \u26a0 The sixth is lo tirtzach, and RATZACH is the verb Numbers 35 uses of the manslayer who flees to a city of refuge, not harag, the ordinary word for killing: every version on this shelf but one says 'kill'. The third is not a rule about swearing but about LIFTING UP the Name emptily. And it ends with the people standing far off while Moses walks into the thick darkness where God was."),
    ("exod21", "Exodus", 21, "The Ten Commandments were apodictic law \u2014 bare, unconditional. This chapter opens the Mishpatim, the case law that works them out: 'if\u2026 then,' the same genre as the Code of Hammurabi, centuries older. A Hebrew servant serves six years and goes free \u2014 a hard ceiling this law nowhere sets for a foreign-born slave. \u26a0 The chapter's most famous line, 'eye for eye, tooth for tooth,' sits inside one specific case, and its job there is to set a LIMIT on vengeance, not license it \u2014 two verses later, injuring a servant's eye costs the master not his own eye but the servant's freedom. And a goring ox that kills a second time after a documented warning costs its owner his own life unless a ransom is paid \u2014 almost word for word the same case found in the Code of Hammurabi, centuries before this text's own conventional date."),
    ("exod22", "Exodus", 22, "This chapter has no verse 1 \u2014 Hebrew and English Bibles split it differently, and what English readers call Exodus 22:1 is already on these pages as the last verse of chapter 21. \u26a0 What follows is the most exposed stretch of the Mishpatim yet: a bailment system with a genuinely coherent risk-allocation logic (borrowed vs. deposited vs. hired), the seduction/bride-price law, three capital sentences fired in a row with zero explanation \u2014 including the verse whose King James wording, 'suffer not a witch to live,' fueled centuries of witch trials \u2014 and the one law in the whole chapter enforced by God personally rather than through any court: mistreat a widow or orphan, and 'I will surely hear their cry.'"),
    ("exod23", "Exodus", 23, "The Mishpatim close on courtroom ethics that cut both ways \u2014 don't twist justice against the poor, but don't favor the poor either \u2014 then command something the rest of the chapter never explains: help your ENEMY'S ox or fallen donkey, before the word 'neighbor' has even appeared. \u26a0 The chapter's calendar clause is six words in Hebrew and became an entire branch of Jewish law: 'you shall not boil a young goat in its mother's milk' \u2014 repeated twice more elsewhere and read by rabbinic tradition as the root of kosher meat-and-dairy separation. And an angel is sent ahead with a warning stranger than any messenger needs: he will not pardon your transgression, 'for my name is in him' \u2014 followed by a conquest deliberately paced too slow to finish quickly, so the land won't fall empty before Israel can hold it."),
    ("2sam1", "2 Samuel", 1, "Saul is dead on Gilboa, and a man runs into Ziklag with the crown in his hand and a story that does not match the one 1 Samuel just told. David — who spent years as Saul's hunted rival — tears his clothes, fasts, executes the messenger for laying a hand on 'Jehovah's anointed', and then chants the Song of the Bow: 'How the mighty have fallen.' A lament that says nothing of the spear thrown at him, the years of pursuit, or the priests of Nob."),
    ("lev1", "Leviticus", 1, "The manual of worship opens: from the tent he has just filled, Jehovah CALLS Moses and gives the law of the burnt-offering — the herd, the flock, and the poor person's two birds, each ascending whole in smoke, 'a soothing aroma to Jehovah.'"),
    ("lev19", "Leviticus", 19, "The heart of the Holiness Code: “You shall be holy, for I, Jehovah your God, am holy” — unpacked into thirty-five verses of field edges left for the poor, honest wages, no partiality in court, no standing idly by a neighbor's blood, and the single most-quoted line in the Torah, “you shall love your neighbor as yourself,” repeated word for word sixteen verses later for the stranger. Mixed seeds, mixed cloth, the corners of a beard, tattoos, honest scales — the ordinary and the cosmic held in one list, closed fifteen times by the same three words: I am Jehovah."),
    ("num1", "Numbers", 1, "'In the wilderness of Sinai' the redeemed people are counted and arrayed as an army for the march — twelve tribes, twelve chieftains, 603,550 fighting men; and one tribe, Levi, left off the war-roll to carry and guard the tent at the camp's center."),
    ("deut1", "Deuteronomy", 1, "Moses begins the longest speech of his life, on the far side of the Jordan, to a generation that was not there. \"Eleven days from Horeb\" — and then \"in the fortieth year\": the whole chapter is the explanation of that gap. Judges appointed, spies sent, a land refused, and the flat closing line that nothing happened for a very long time."),
    ("josh1", "Joshua", 1, "The book of the crossing opens on the worst possible news — \"Moses my servant is dead\" — and refuses to let it stop anything: rise, cross the Jordan. Three times Joshua is told to be strong and resolute, and the courage he most needs turns out to be for keeping the scroll, not the sword. Then rations, a marching order, an old promise called in, and the people handing the charge back: \"only be strong and resolute.\""),
    ("josh6", "Joshua", 6, "Jericho, shut up tight against Israel, falls to a war plan with no battle in it: march around the walled city once a day for six days behind the ark and seven trumpets of rams' horns, say nothing, and on the seventh day march around seven times and shout. The walls fall flat, the city and everything in it is devoted to destruction, and one household is spared by name — Rahab, the prostitute who hid the spies, whose scarlet cord is still in the window. Joshua closes the chapter with a curse on whoever rebuilds Jericho — a curse the book of Kings will report, by name, coming true."),
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
    ("joel1", "Joel", 1, "Four waves of locusts strip Judah down to the wood — and Joel uses FOUR different Hebrew words for them, whose distinctions nobody has ever established: four species, four growth stages, or four names piled up for weight. But the loss is not measured in bushels. It is measured by what has stopped at the temple: with no flour and no wine, the daily grain and drink offering cannot be made, so the country’s standing conversation with God has gone silent — which is why the PRIESTS, not the farmers, are told to sleep in sackcloth. Then the day of Jehovah arrives in a pun no translation can carry (shod from SHADDAI), and a verse with three words that occur nowhere else in the Bible. It ends with the cattle, and with a verb borrowed from Psalm 42: even the beasts of the field PANT for you, because the streams have dried up."),
    ("hos1", "Hosea", 1, "God tells a prophet to marry a promiscuous woman, and then to name their three children after the sentence on his country: JEZREEL, after a massacre; LO-RUCHAMAH, Not-Pitied — and Hebrew builds its word for mercy on the word for a WOMB, so naming a newborn girl Not-Mother-Loved is worse in Hebrew than in English; and LO-AMMI, Not-My-People. The last of them takes the covenant formula apart, and then goes further than any English Bible shows: the Hebrew of verse 9 has no word for ‘God’ in it. What it says is ‘I will not be EHYEH to you’ — the name God gave himself at the burning bush, withdrawn. Note also who dates this book: four kings of JUDAH, for a prophet who preached only to the north. And note that it has nine verses, not eleven."),
    ("lam1", "Lamentations", 1, "Twenty-two verses, because the Hebrew alphabet has twenty-two letters and each verse begins with the next one — the most tightly controlled writing in the Bible, about the least controllable thing that happens to people. Jerusalem has burned, and the city is a widow sitting alone: the roads to Zion mourn because nobody is walking on them, priests and elders die in the streets while out looking for food, and five separate times the poem says the same thing — SHE HAS NO COMFORTER. Not that there is no rescue; that there is nobody sitting with her. Halfway through, the city interrupts the description of herself and takes the poem over, and she concedes the verdict was just. Babylon burned this city, and Babylon is not named once in five chapters — every clause has God as its subject, which is exactly why the complaints can be addressed to him."),
    ("lam2", "Lamentations", 2, "The fiercest chapter in the book, and the one that says outright what chapter 1 only implied: 'The Lord has become like an enemy.' He bends his bow against his own city, tears down his own temple like a demolition contractor stretching a measuring line, and erases the very festival calendar that made worship possible. The image the whole chapter turns on is a shout of victory raised INSIDE the house of Jehovah, as on the day of an appointed feast — the vocabulary of celebration used for the enemy's own triumph. Children ask their mothers 'Where is grain and wine?' and faint in the streets; by the end, God is asked outright whether women have really been reduced to eating their own children. And for the first time in this book, two letters of the acrostic switch places — pe printed before ayin — a small, unexplained irregularity in a poem otherwise built entirely on order."),
    ("isa1", "Isaiah", 1, "Isaiah opens not with a sermon but with a LAWSUIT: heaven and earth are summoned as witnesses — the same two the covenant calls in Deuteronomy — and the charge is read. An ox knows who feeds it; Israel does not. Then the hardest passage in the prophets: God says he is sick of the sacrifices HE COMMANDED — ‘who asked this of your hand?’ — because the hands lifted in prayer are full of blood, and the courts will not hear an orphan. Verse 8 can be dated: Jerusalem left ‘like a booth in a vineyard,’ which is 701 BC, and Sennacherib’s own prism says he shut Hezekiah up there ‘like a bird in a cage.’ And then the most quoted verse in the book — though your sins are like scarlet — which in Hebrew may not be a promise at all, but a prosecutor’s question. The dye, incidentally, was a worm, and it was famous for not washing out."),
    ("isa40", "Isaiah", 40, "The seam of the book — chapter 40 is where the horizon shifts to an exile already accomplished, and comfort becomes the word of the next twenty-seven chapters. “Comfort, comfort my people” opens onto a voice crying in the wilderness (all four Gospels quote it for John the Baptist), “all flesh is grass” (1 Peter 1:24), a shepherd gathering lambs in his arm, and a cosmic argument — who has measured the waters in his hand, who has instructed the Spirit of Jehovah (Paul quotes it twice) — that ends on the chapter's most beloved line: those who wait for Jehovah shall renew their strength, they shall mount up with wings like eagles."),
    ("isa53", "Isaiah", 53, "The suffering servant \u2014 the most argued-over passage in the Hebrew Bible, and the argument is textual, not merely theological. \u26a0 Whether the servant is ISRAEL (Isaiah 49:3 says so by name) or an INDIVIDUAL (53:8 sets him against 'my people') is left standing with both cases set out in full and no vote taken. Two plurals nearly every Bible singularises: lamo at v8 is normally 'to THEM', and be-motav at v9 is 'his DEATHS' \u2014 which the KJV of 1611 flagged in its own margin while three modern versions print the singular silently. \u26a0 And at v11 the Great Isaiah Scroll from Qumran, a thousand years older than our oldest Masoretic manuscripts, reads 'he will see LIGHT' where the Masoretic text has no object at all \u2014 agreeing there with the Septuagint against the later Hebrew. One verb, paga (to MEET), frames the poem: our iniquity is made to meet him at v6, and he intercedes at v12."),
    ("sos1", "Song of Solomon", 1, "The title is a Hebrew superlative — a noun governing its own plural, like ‘holy of holies’ — so it means THE BEST SONG THERE IS; and ‘which is Solomon’s’ is a single prefixed letter that can equally mean by him, for him, about him, or in his manner. Then, with no narrator and no introduction, a woman begins mid-desire: ‘Let him kiss me with the kisses of his mouth.’ She will speak most of this book, open it and close it. She says she is black AND lovely — the Hebrew has the ordinary conjunction, and Jerome’s ‘but’ has shaped the verse ever since — and explains it herself: sunburn, from being made to keep her brothers’ vineyards. He calls her a mare among Pharaoh’s chariots, which is not about size: Egyptian chariots were drawn by stallions, and one mare pulls the formation apart. It ends with two lovers lying on grass under cedars, calling it their house."),
    ("qoh1", "Ecclesiastes", 1, "The Bible’s most sceptical book opens with a word almost every English version has translated as a verdict when the Hebrew gives an image: HEVEL, vapor — a breath, mist you can see and cannot hold. “Vanity,” “meaningless,” “futile” all decide something the Hebrew leaves open. Then a poem in which the sun PANTS its way back to its starting line, the wind circles and returns, the rivers run to a sea that never fills, and the generations pass while the earth stays put — four systems in perpetual motion, none of them arriving. “There is nothing new under the sun.” The speaker calls himself Qohelet, which is not a name but an office — ‘the Congregator’ — and says “I WAS king,” a past tense that does not fit Solomon and started a rabbinic legend about a deposed king wandering as a beggar. He ends the chapter with a bill: in much wisdom is much vexation, and whoever adds knowledge adds pain."),
    ("qoh3", "Ecclesiastes", 3, "A time to be born and a time to die \u2014 fourteen paired opposites, two per verse, with the word ET heading twenty-eight clauses, and no verdicts anywhere in the list: killing sits in it as flatly as healing. Then the poem turns out to be a setup. \u26a0 At v11 the consonants of ha-OLAM give ETERNITY (ASV, TNM), THE WORLD (KJV, RV \u2014 olam drifts that way in late Hebrew, and this is late Hebrew), or, repointed, HIDDENNESS \u2014 which no version prints and which alone makes the verse agree with its own second half. \u26a0 And at v21 the Masoretic text points two participles with the DEFINITE ARTICLE (the dagesh in the yod is the tell), so the verse says 'the one going up' and 'the one going down'; repointed it asks 'does it go up? does it go down?' The KJV is the version that followed the vowels \u2014 ASV, NWT and TNM all supply 'whether' \u2014 which is the reverse of this library's usual finding. Along the way: yitron, an accounting word, asks what the worker accumulates (v9) and answers at v19 that the advantage of man over the beast is NOTHING; one RUACH in all of them; and God shows people that they ARE beasts (v18), with no comparison particle in the Hebrew."),
    ("amos1", "Amos", 1, "A sheep-breeder from a Judean village walks into the northern kingdom at the height of its wealth and opens by condemning everybody else — Damascus, Gaza, Tyre, Edom, Ammon — five nations sentenced in a formula that will run EIGHT times, and whose eighth is aimed at the people nodding along. Every charge is an atrocity against human beings and not one is idolatry: threshing a region with iron sledges, selling whole populations on to Edom, forgetting a covenant of brothers, hunting your own twin and “ruining his own compassion” — a word built on the Hebrew for WOMB — and, the only crime given a motive, ripping open the pregnant women of Gilead in order to enlarge a border. ⚠ And the book fixes its own date twice: by two kings, and by a natural disaster — “two years before THE earthquake,” with the definite article, because the readers could count from it, and because archaeologists keep finding the layer."),
    ("obad1", "Obadiah", 1, "The SHORTEST book in the Old Testament — twenty-one verses, one chapter — and every word of it is aimed at one target: EDOM, the nation descended from Esau, condemned for standing by (and gloating, and looting) while Babylon sacked Jerusalem. Its first nine verses run almost word for word with Jeremiah 49, the largest sustained parallel between two prophetic books. The charge is a single word — “the VIOLENCE done to your BROTHER Jacob” — because Edom's crime is not that it attacked but that it WATCHED, and by watching joined in, told in eight commands each pinned to “the day” Jerusalem fell, with the word “day” beating ten times in four verses. Then the hinge of the whole book: “as you have done, it will be done to you.” It ends handing the contested map back to its owner — “and the kingdom will belong to Jehovah” — and along the way passes through SEPHARAD, an unknown place whose misidentification became the name of Spanish Jewry."),
    ("jonah1", "Jonah", 1, "The odd one out of the Twelve: not a book of oracles but a STORY, and the only prophetic book whose prophet DISOBEYS. Told to go east and cry against Nineveh — the great enemy capital, the future destroyer of Israel — Jonah runs west to the ends of the sea, boarding a ship at Joppa “away from before Jehovah.” God hurls a storm; the pagan sailors pray, cast lots, and beg Jonah's God for mercy while Jonah sleeps in the hold, and when they finally throw him overboard (rowing hard first, to try to save him — they are more merciful than the prophet), they end up fearing Jehovah and offering sacrifice. The chapter is charted by one word — DOWN: down to Joppa, down into the ship, down into the hold — and built on one irony: “I fear Jehovah, who made the sea and the dry land,” says the man fleeing across the sea. ⚠ And the famous fish is NOT here — it is Hebrew 2:1, which English Bibles renumber 1:17; this site follows the Masoretic count, and it is a “great fish,” not a whale."),
    ("micah1", "Micah", 1, "Isaiah's country cousin — a Shephelah farmer's prophet who preached the same eighth-century word from the bottom of society that Isaiah preached from the top. The chapter opens as a courtroom (heaven and earth summoned as witnesses), then a great theophany: God comes DOWN and the mountains MELT under him like wax before fire. And the crime turns out to be the two capital cities themselves — “What is the revolt of Jacob? Is it not SAMARIA? And what are the high places of Judah? Are they not JERUSALEM?” Then the most untranslatable passage in the prophets: Micah mourns his own home region town by town, turning each village's NAME into a pun on its FATE as the Assyrian invasion rolls through — Dust-town rolling in dust, Fair-town stripped bare, the Going-out that cannot go out, and his own Moresheth handed over like a bride. ⚠ Micah is the only writing prophet the Hebrew Bible quotes BY NAME (Jeremiah 26:18), and his book gives the New Testament Bethlehem (5:2) and “do justice, love mercy, walk humbly” (6:8)."),
    ("nahum1", "Nahum", 1, "The dark twin of Jonah: the same city, Nineveh, a century and a half later — and this time no mercy. Where Jonah's Nineveh repented and was spared, Nahum's has gone back to being the ancient world's most efficient killing-machine, and God announces its end. The book opens not with the city but with a wrath-HYMN built as an alphabetic acrostic that breaks off halfway — an ordered alphabet of judgment left unfinished — and it quotes the famous Exodus-34 formula tilted toward JUSTICE: “slow to anger and great in power, and he will by no means leave the guilty unpunished.” Yet in the exact middle sits the one verse of mercy (“Jehovah is good, a stronghold in the day of distress”) that makes the whole book of doom deserve its name — Nahum means COMFORT, because the fall of the destroyer is the good news for everyone it crushed. ⚠ And the famous “feet of him who brings good news” verse is NOT here — it is Hebrew 2:1 (English renumbers it 1:15); this site follows the Masoretic count."),
    ("habakkuk1", "Habakkuk", 1, "The prophet who ARGUES back. Alone among the Twelve, Habakkuk's book is not a message from God to the people but a DIALOGUE with God — a two-round dispute over the oldest hard question there is. First complaint: how long, Jehovah, will you tolerate the violence rotting Judah, the paralyzed law, the perverted courts? God's answer is the shock the whole book turns on — “I am raising up the CHALDEANS,” the Babylonian war-machine (horses swifter than leopards, who “laugh at every fortress” and whose “own strength is their god”) — the cure worse than the disease. Which triggers the harder, second complaint, the theodicy problem stated as cleanly as it ever has been: “you are of purer eyes than to look on evil… why then do you look on the treacherous, and stay silent while the wicked swallows one more righteous than himself?” The chapter ends with the question hanging in the air and the prophet climbing his watchtower to wait — and the answer, in chapter 2, will be the New Testament's most quoted line: “the righteous will live by his faith.” ⚠ A running commentary on this very book was among the first Dead Sea Scrolls found in 1947."),
    ("zephaniah1", "Zephaniah", 1, "The darkest “day of Jehovah” in the Twelve — and it opens with the most terrifying sentence in the prophets: “I will utterly sweep away everything from the face of the ground,” Genesis 1 run in REVERSE (humankind, beasts, birds and fish swept off the ground they were given on the sixth day). Then the lens narrows to one city: God cuts off Baal's remnant, the idol-priests, the rooftop star-worshippers, and — his real target — the hedgers who bow “swearing by Jehovah AND swearing by Milcom.” He prepares a sacrifice where Judah is the meat and the invaders are the guests, searches Jerusalem with lamps for the smug who say “Jehovah will do no good and do no harm,” and rises to the Day of Wrath whose Latin Vulgate (“dies irae, dies illa”) became the West's most famous funeral hymn. ⚠ Yet the prophet's own name means “Jehovah has HIDDEN,” and the book turns (2:3) on “perhaps you will be hidden” and ends with God “exulting over you with singing.” A prophet of royal blood: his heading traces him four generations back to King Hezekiah — the longest pedigree in the prophets."),
    ("psalms1", "Psalms", 1, "The front door of the Bible’s hymnbook. The 150 psalms are Israel’s prayers and songs for every weather of the soul — but the book does not open with a prayer. It opens with a WISDOM POEM, Psalm 1, that stands at the gate and tells you how to read everything behind it: there are two ways, the way of the righteous and the way of the wicked, and the whole of a life turns on which one you walk. The happy man — and the Psalter’s very first word is “Happy” (ashrei), the same word that opens the Beatitudes — does not drift down the staircase of the wicked (walk, then stand, then sit) but delights in the law of Jehovah and murmurs it day and night; and so he is a tree planted by water, fruitful and green, while the wicked are chaff the wind simply blows away. “Jehovah knows the way of the righteous, but the way of the wicked will perish.” A quiet poem that is the doorway to the songbook Jesus sang."),
    ("psalms23", "Psalms", 23, "The most-read chapter in the Psalter, and one of the most-read in the Bible — six verses in which almost every famous line turns out to be carrying something the English has quietly dropped. &#9888; &ldquo;Shepherd&rdquo; is a ROYAL title across the ancient Near East, not a pastoral one, so the opening line is a claim about who rules — the same metaphor Jeremiah 23 runs from the opposite end, cursing the shepherds who failed. &ldquo;I shall not want&rdquo; meant &ldquo;I shall not LACK&rdquo; in 1611 and now means nearly the opposite. &#9888; &ldquo;He restoreth my soul&rdquo; has no soul in it: nefesh is the throat, the breath, the whole living self, and yeshovev is shuv — he brings my LIFE back. The &ldquo;paths&rdquo; of righteousness are ma'gelei, wheel-RUTS, a road already worn. &#9888; At verse 4 the poem stops talking ABOUT God and starts talking TO him — third person to second, at the exact centre, in the dark — and never turns back; the valley is a gei, a narrow ravine; and tsalmavet is the crux, the Masoretic &ldquo;death-shadow&rdquo; against the lexicons&rsquo; re-pointed &ldquo;deep darkness,&rdquo; 18 occurrences, ten of them in Job. Then the shepherd simply walks off the page: verses 5&ndash;6 are a HOST and a house, the oil is dashen (a host greasing a guest&rsquo;s head) and pointedly NOT mashach, the anointing verb behind Messiah. &#9888; And the last verse holds two things every familiar version loses — goodness and chesed do not &ldquo;follow&rdquo; but PURSUE (radaph, the hunting verb used of Egypt and of Saul), and le'orekh yamim is &ldquo;for length of days,&rdquo; a long life, not &ldquo;forever.&rdquo; The closing consonants can be read three ways; the Masoretes pointed them shuv, &ldquo;I shall RETURN&rdquo; — which frames the psalm&rsquo;s second half with the same root as verse 3, a frame that vanishes in every translation printing &ldquo;dwell.&rdquo;"),
    ("psalms27", "Psalms", 27, "A psalm of two halves that read like two different moods until the last line ties them together. Verses 1&ndash;6 are pure confidence &mdash; &ldquo;Jehovah is my light and my salvation, whom shall I fear?&rdquo; &mdash; an army encamped, war rising, and none of it enough to shake the one thing David asks for: to sit in Jehovah's house and be gone over the way a priest examines an offering. Then, with no warning, verse 7 turns to urgent, unresolved pleading &mdash; &ldquo;hide not thy face,&rdquo; a father and mother who have let go, false witnesses closing in &mdash; and the psalm's most famous line breaks off mid-sentence, the &ldquo;then&rdquo; clause simply never supplied. &#9888; Verse 6's &ldquo;sacrifices with a shout&rdquo; uses the identical Hebrew word, teru'ah, for the noise that brought Jericho's wall down two chapters earlier on this shelf &mdash; the same shout, turned from a weapon into worship."),
    ("psalms51", "Psalms", 51, "\u26a0 The verb at v12 is BARA \u2014 the verb of Genesis 1:1, which across the whole Hebrew Bible takes ONLY God as its subject. No human ever baras anything, and it is not the ordinary word for making or shaping. So 'create in me a clean heart' does not ask to be improved: it asks for the act of the first sentence of the Bible, performed on a heart. \u26a0 Note the numbering: in the Hebrew the superscription IS the text, so every verse here runs two ahead \u2014 the famous line is Psalm 51:10 in English and v12 on this page. \u26a0 And the psalm contradicts itself in the open: 'you do not want sacrifice' (v18), then three lines later 'then bulls will go up on your altar' (v21). Zevach appears four times, on both sides of the reversal, and the plainest reading is that the last two verses are a later hand that could not leave v18 as the last word. Three words for wrong that are not synonyms (rebellion, guilt, missing the mark), each with its own verb: wipe out, wash, cleanse. Hyssop, the sprig that daubs blood on the Passover doorposts, asked for by a psalm that will shortly say sacrifice is not wanted. And 'against you, you only, have I sinned' \u2014 said, if the superscription is right, by a man who had a soldier killed."),
    ("psalms91", "Psalms", 91, "2025&rsquo;s most-searched chapter, and the Bible&rsquo;s most unconditional-sounding promise of protection &mdash; which is exactly why the devil quotes it. &#9888; It has NO superscription: no author, no tune, no occasion (the Septuagint later handed it to David, the Talmud to Moses; the Hebrew names nobody). It opens by stacking FOUR names for God in two verses &mdash; Elyon, Shaddai, YHVH, &lsquo;my God&rsquo; &mdash; moving from the highest title to the most personal possessive in a breath, and the verbs are about lodging till morning, not residing. &#9888; Verse 4 makes God&rsquo;s FAITHFULNESS the armour (&lsquo;a shield and a socherah is his emet&rsquo; &mdash; and socherah occurs nowhere else in the Hebrew Bible). Verses 5&ndash;6 set four terrors on a clock, night&ndash;day&ndash;dark&ndash;noon &mdash; and the fourth, qetev, is where the NOONDAY DEMON entered Christianity: a scourge in Hebrew, <em>daimonion mes&#275;mbrinon</em> in the Septuagint, <em>daemonium meridianum</em> in the Vulgate, and the patron demon of monastic acedia by the fourth century. &#9888; Verse 9&rsquo;s grammar breaks mid-sentence and three versions repair it three different ways &mdash; the NWT even marks its added word with brackets. &#9888; Verses 11&ndash;12 are the two the tempter cites at Matthew 4:6, and standing on the Hebrew side you can see exactly what he left out: the Hebrew has three clauses, the quotation has two, and the missing one is &lsquo;to guard you in all your ways&rsquo; &mdash; protection on the road, which is not a warrant for jumping off a roof. Verse 13 puts four beasts underfoot including <em>tannin</em>, the great sea-beast of Genesis 1:21 &mdash; and its <em>peten</em> became the Vulgate&rsquo;s BASILISK, a second monster this psalm handed to Europe by translation. Then at verse 14 the voice changes to God&rsquo;s own first person with no warning at all, and the psalm closes on <em>orekh yamim</em>, the same phrase that ends Psalm 23 &mdash; here with the verb (&lsquo;I will SATISFY him&rsquo;) that settles it as a long life rather than eternity."),
    ("psalms121", "Psalms", 121, "The first of fifteen Songs of Ascents (120&ndash;134), the only run of consecutive psalms in the Psalter sharing one title &mdash; sung, tradition says, either by pilgrims climbing to Jerusalem for the great feasts, or one by one on the fifteen steps of the Temple itself. Eight verses turn on a single word: SHAMAR, &lsquo;to keep,&rsquo; falls six times in six lines, the densest concentration of one root in a psalm this short. &ldquo;I will lift up my eyes to the mountains &mdash; from where will my help come?&rdquo; opens on a real question the Hebrew leaves open (KJV alone on this shelf reads it as a statement instead); v2 answers it, and the rest of the psalm spends itself insisting that the answer never sleeps &mdash; not dozing, not sleeping, not once, day or night, sun or moon &mdash; closing on the same promise God once made a frightened man alone at Bethel: I will keep you wherever you go."),
    ("psalms139", "Psalms", 139, "\u26a0 Chaqar, to search out, occurs exactly TWICE and brackets the psalm: 'you have searched me' (v1) and 'search me' (v23) \u2014 and what sits between them is vv19-22, the part nobody quotes, where the speaker asks God to kill people and says he hates them with a COMPLETE hatred. Read as a bracket, the closing request is not a pious add-on to a comfortable poem about being known: it is the speaker submitting what he has just said to examination. \u26a0 The hardest verse is decided by a scribal note: at v16 the Hebrew carries a KETIV/QERE \u2014 written 'and NOT', read 'and FOR HIM' \u2014 one letter, and the clause turns over; and the shelf mostly follows the written form, not the read one. \u26a0 Golmi in the same verse occurs ONCE in the Hebrew Bible: an unformed mass, the root behind the GOLEM of later legend, which RV, NWT and TNM all now render 'embryo'. And the most-quoted line rests on a supplied word \u2014 v14 is two Hebrew words, and RV 1909 reads the wonder as belonging to GOD'S WORKS rather than to the speaker, on which reading the verse never says 'I am wonderfully made' at all. Kidneys as the seat of conscience (v13), a womb SCREENED like a sukkah, a person EMBROIDERED in the depths of the earth, and a closing 'way of pain' that the KJV admits only in its margin."),
    ("jhn3", "John", 3, "Nicodemus comes by night &mdash; and the whole conversation runs on a pun no language can keep. &#9888; <em>An&#333;then</em> means BOTH &ldquo;from above&rdquo; and &ldquo;again&rdquo;: Jesus says a man must be born <em>an&#333;then</em>, Nicodemus hears the second sense and asks the famous absurd question about re-entering a womb. Counted in the archive the word occurs 13 times in the New Testament, five of them John&rsquo;s &mdash; and every other Johannine use is SPATIAL, while Galatians 4:9 proves the temporal sense is real, so the misunderstanding is a genuine possibility of the Greek and not a straw man. &#9888; And John settles it himself at v31, glossing <em>an&#333;then</em> with &ldquo;out of heaven&rdquo; in the same verse. Five verses after the first pun comes a second: <em>pneuma</em> is wind AND Spirit, and v8 builds a sentence on the fact. &#9888; Then the most quoted sentence in the world, carrying two things English has lost &mdash; <em>hout&#333;s</em> is MANNER, not quantity (&ldquo;this is HOW God loved the world,&rdquo; not &ldquo;so much&rdquo;; the archaic Spanish RV 1909 gets it right where nearly everyone else does not), and <em>monogen&#275;s</em> is &ldquo;the only Son,&rdquo; not &ldquo;only-begotten,&rdquo; which came through the Latin. &#9888; And a decision this library had to make in public: Greek manuscripts have no quotation marks, many editors read vv16&ndash;21 as the evangelist rather than Jesus, and because this translation prints red letters it cannot decline to choose &mdash; so <strong>the red ends at verse 15 and John 3:16 is not in red here</strong>, with the note giving both readings and stating that nothing theological turns on it. Three textual variants argued from the direction a copyist would move; the bronze serpent lifted in the wilderness; the judgment as a light switched on rather than a sentence handed down; two men baptizing at once and the Gospel correcting itself about it; and the best man at somebody else&rsquo;s wedding, whose job has a built-in ending."),
    ("jhn6", "John", 6, "Five loaves and two small fish feed five thousand, twelve baskets are left over, and the crowd tries to make him king by force &mdash; so he withdraws alone up a mountain. That night the disciples row into a storm and see him walking on the water: &ldquo;It is I; do not be afraid&rdquo; &mdash; the same two words, <em>egō eimi</em>, this Gospel elsewhere lets stand absolutely as a claim of divine self-naming. The crowd catches up demanding a bigger sign than the one they just ate, and gets instead the first of this Gospel's seven &ldquo;I am&rdquo; sayings built with a stated predicate: &ldquo;I AM THE BREAD OF LIFE.&rdquo; ⚠ Then the language turns physical and does not turn back: the ordinary verb for eating gives way, six times running, to a cruder Greek word properly meaning to GNAW &mdash; tracking exactly how much of the audience the teaching costs him. &ldquo;This is a hard saying; who can listen to it?&rdquo; some of his own disciples say, and for the first time in this Gospel, they turn back and no longer walk with him. Peter's answer to &ldquo;do you also want to go away?&rdquo; is not an easier reading of the teaching but a confession that there is nowhere else worth going &mdash; &ldquo;Lord, to whom shall we go? You have the words of eternal life&rdquo; &mdash; a v69 title for Jesus (&ldquo;the Holy One of God&rdquo; against the Byzantine &ldquo;Christ, the Son of the living God&rdquo;) the shelf itself can't agree on. It closes on Judas, named for the first time by his father's name, already a devil, still one of the Twelve."),
    ("jhn5", "John", 5, "A man who has been lying by a pool for thirty-eight years, and a question that sounds almost cruel &mdash; &ldquo;Do you want to become well?&rdquo; He is healed, told to carry his mat, and it is the SABBATH: the first real hostility in this Gospel starts here, not over the healing but over the mat. &#9888; Verse 4 &mdash; the angel stirring the water &mdash; is missing on these pages; the earliest Greek manuscripts do not have it, so the numbering simply skips it, v3 to v5. Then, for calling God his own Father, Jesus is accused of &ldquo;making himself EQUAL WITH GOD&rdquo; (isos, the plain word, not softened by any version checked) &mdash; and the long speech that follows (vv19&ndash;47), the longest single speech Jesus has given in this Gospel so far, answers that charge rather than backing away from it: the Son can do nothing of himself, which turns out to be the larger claim, not the smaller one. &#9888; &ldquo;An hour is coming, and now is&rdquo; (v25) is the exact formula John 4:23 planted, now applied to the dead hearing the Son&rsquo;s voice and living &mdash; and three verses later the SAME formula drops its second half (v28), marking a hoped-for hour still only future. Four witnesses are called &mdash; John the Baptist, the works, the Father, the Scriptures &mdash; and v39&rsquo;s &ldquo;you search the Scriptures&rdquo; is genuinely ambiguous in Greek between a command and a statement, KJV reading one way and nearly everyone else the other."),
    ("jhn4", "John", 4, "The longest conversation Jesus has with anybody in any Gospel &mdash; and it opens with him asking HER for a favour. &#9888; Read it against <em>John 3</em>, because the two are built as a pair: a named male insider, a ruler, who comes BY NIGHT; and an unnamed foreign woman met at NOON. He misunderstands <em>an&#333;then</em>; she misunderstands &ldquo;living water&rdquo; &mdash; which in ordinary Greek simply means RUNNING water, so she is hearing it correctly in its everyday sense, exactly as he did. &#9888; And here John marks the misunderstanding with the vocabulary itself: the narrator and Jesus say <em>p&#275;g&#275;</em>, a SPRING, while the woman says <em>phrear</em>, a dug SHAFT &mdash; two words for the same hole in the ground, sorted by who is speaking, and the KJV&rsquo;s uniform &ldquo;well&rdquo; erases all of it (the NWT and the archaic Spanish RV 1909 both keep it; the modern TNM loses it). Then the five husbands, where the text never calls her sinful and Jesus never rebukes her; the demolished Samaritan temple on Gerizim behind &ldquo;this mountain&rdquo;; and <em>pneuma ho theos</em> at v24 &mdash; the identical anarthrous construction as John 1:1, so &ldquo;God is spirit&rdquo; follows from the ruling already made in the prologue. &#9888; The first <em>eg&#333; eimi</em> in the book is said to a Samaritan woman alone at noon; the disciples arrive and are astonished not that she is a Samaritan but that she is A WOMAN, and John quotes the two questions nobody asked. She leaves her water jar, phrases her announcement in the form that expects the answer NO, and the town comes anyway &mdash; then tells her they have moved past her testimony, and calls him <em>Saviour of the world</em>, which was a title of Caesar."),
    ("jhn14", "John", 14, "\u201cIn my Father\u2019s house are many mansions\u201d \u2014 except that is not what the Greek says, and the proof is twenty-one verses further down the same chapter. MONE occurs twice in the entire New Testament, both times here, and at verse 23 nobody translates it \u201cmansion.\u201d \u26a0 Three places where the manuscripts genuinely divide: verse 7 is a rebuke in one text and a promise in another; verse 14 either does or does not contain the word \u201cme,\u201d which would make it the only place in John where prayer is addressed to Jesus; and one small word decides whether verse 2 is a question. Plus the widest split on the whole shelf \u2014 Comforter, Helper, Advocate, Counselor, Paraclete \u2014 and why 1 John 2:1 settles it. Thomas asks the honest question, Philip asks the reasonable one, and the chapter ends by saying \u201cget up, let us go from here\u201d and then carrying on for three more chapters."),
    ("jhn15", "John", 15, "The vine, the branches, and \u201cabide in me\u201d \u2014 MENO eleven times in five verses, the word the previous chapter kept planting and never once commanded. \u26a0 Verses 2 and 3 run a three-word pun no English version fully keeps: airei, kathairei, katharoi \u2014 takes away, prunes clean, you are clean \u2014 and verse 3 is the punchline, answering \u201cyou are clean, but not all of you\u201d two chapters earlier, now that Judas has left the room. The one tending the vine is called by the word the other Gospels give to the tenants who kill the son. Slaves are promoted to friends on the grounds of having been told things. \u201cThey hated me for nothing\u201d uses the New Testament\u2019s ordinary word for a free gift. And verse 26 is the sentence the Eastern and Western churches split over in 1054 \u2014 one line that honestly supports both sides."),
    ("zechariah1", "Zechariah", 1, "The prophet who opened the age of apocalyptic. Haggai’s exact contemporary in the rubble of 520 BC, Zechariah answers the same discouragement not with a builder’s plain command but with EIGHT NIGHT VISIONS. Chapter 1 gives the first: a horseman on a red horse standing among the myrtle trees in a shadowed ravine, a divine patrol that has ranged the earth and reports — ominously — that “all the earth is at rest” while Zion still mourns; and “the angel who talked with me” (the interpreting angel all later apocalypse is built on) cries “How long?” God answers with a jealousy FOR Jerusalem, a measuring line stretched over her for rebuilding, and comfort renewed — the whole framed by the oldest word in the prophets, “Return to me, and I will return to you.” ⚠ Zechariah is a priest as well as a prophet, and his pedigree (“son of Berechiah”) carries the tangled Matthew 23:35 crux. ⚠ Masoretic chapter 1 has seventeen verses; the four-horns vision that English prints as 1:18–21 is Hebrew 2:1–4. With this chapter, every one of the Twelve now has a first chapter on the site."),
    ("haggai1", "Haggai", 1, "The book that got the job DONE. Eighteen years after the exiles came home from Babylon, the temple’s foundation lay untouched and the people told themselves “the time has not come.” In four oracles dated to the very DAY — the most precisely-timed book in the Old Testament — the prophet Haggai shames them out of roofing their own paneled houses while God’s house lies a ruin, names the strange leaking futility of ‘me first, God later’ (you earn wages “into a bag full of holes”), and turns a pun on three consonants into the whole point: because you left my house charev, ‘a ruin,’ he called a chorev, a drought, on your fields. Then the rarest thing in all the prophets happens — the people OBEY, and break ground twenty-three days later. What moves them is not a threat but four words from ‘the messenger of Jehovah’: “I am with you.” ⚠ Addressed to the prince Zerubbabel (a Davidic heir, the future signet ring) and the priest Joshua, and dated by a PERSIAN emperor — because there is no longer a king in Jerusalem."),
    ("est1", "Esther", 1, "The only book in the Bible that never mentions God opens with a hundred and eighty days of a king showing people his money. Ahasuerus is XERXES, and the year is 483 BC \u2014 the same year Herodotus has him gathering his nobles to plan the invasion of Greece, a war this book never mentions and whose length is exactly the gap between chapters 1 and 2. Then, on the seventh day of the second banquet, drunk, he sends for his wife to be displayed alongside the furniture, and she refuses \u2014 and the Hebrew gives no reason whatever. What follows is a comedy at the expense of frightened officials: an empire\u2019s entire legal apparatus convened over a dinner-party snub, and a decree carried by the imperial post to a hundred and twenty-seven provinces announcing that men should be in charge at home."),
    ("acts1", "Acts", 1, "The only sequel in the Bible. Luke takes up his pen a second time, addresses the same Theophilus, and opens by calling his whole Gospel merely “the first account… of all that Jesus BEGAN to do and to teach” — which leaves the obvious question of who is doing the continuing. Forty days of appearances end on a hill outside Jerusalem with the disciples asking the question they have been asking all along — “Lord, is it at this time that you are restoring the kingdom to Israel?” — and getting an answer that refuses the calendar without refusing the hope, and then hands them a map: Jerusalem, Judea and Samaria, and the end of the earth. That map turns out to be the table of contents of the twenty-seven chapters that follow. Then a cloud, and two men in white asking why they are still standing there looking up. The rest of the chapter is the church doing the only thing it can do before Pentecost: it walks back a sabbath day’s journey, climbs the stairs, and waits — a fisherman, a tax-collector who had worked for Rome and a zealot from the party that killed such men, together with the women, the brothers who had not believed, and Mary, in the last mention Scripture gives her. Then Peter stands up among “a crowd of names, about a hundred and twenty” to fill the empty twelfth chair, and the church casts lots for the last time in the Bible. ⚠ It also carries the New Testament’s most awkward parenthesis: Luke’s account of how Judas died, which does not agree with Matthew’s — printed here with both readings and no vote."),
    ("acts3", "Acts", 3, "A man lame from birth, healed at the temple's Beautiful Gate — the first miracle in Acts worked by someone other than Jesus, and Peter's own first move is to deny credit for it. 'Silver and gold I do not have,' and a command, 'in the name of Jesus Christ the Nazarene, rise up and walk' &mdash; a phrase that genuinely divides the manuscripts, not just the translations: the oldest single witness reads bare 'walk,' while the Byzantine text and the modern critical standard both add 'rise up and.' ⚠ Peter's sermon in Solomon's Portico names Jesus with a Greek word, <em>pais</em>, that the whole shelf splits on translating &mdash; KJV 'Son,' everyone else 'servant,' the same fork in RV60 versus NVI. It closes on 'the times of RESTORATION of all things' &mdash; a single rare noun, apokatastasis, that Origen would later stretch into a doctrine of universal salvation the wider church never adopted. And a promise handed to a Jewish crowd in a Jewish courtyard, 'to you first,' the sequencing Paul will spend Romans repeating."),
    ("acts2", "Acts", 2, "Pentecost, and the day the promise chapter 1 refused to date gets paid. ⚠ Luke is careful twice and every version blurs it once: there is no wind and no fire, there is a SOUND LIKE a violent wind and tongues AS OF fire &mdash; and <em>glōssa</em> means the organ, the shape a flame makes, and a language, all three live in one paragraph. The miracle is put in the hearers&rsquo; ears as much as the speakers&rsquo; mouths. ⚠ The list of nations has JUDEA in it, textually secure in every printed edition and geographically inexplicable; the old conjectures are set out and none adopted. Then Peter&rsquo;s sermon, and two places where the argument is visibly built on the Greek Bible: Joel&rsquo;s undated &ldquo;afterward&rdquo; is quoted as &ldquo;IN THE LAST DAYS,&rdquo; and the whole David argument turns on <em>diaphthora</em>, DECAY &mdash; where the Hebrew <em>shachat</em> is &ldquo;the pit,&rdquo; and the case from a rotted body does not arise. ⚠ Also &ldquo;loosing the BIRTH PANGS of death,&rdquo; which you cannot do, because Hebrew <em>chevel</em> is both a cord and a pang and the Greek took the second. And at v38 the baptism is &ldquo;on the name of Jesus Christ&rdquo; &mdash; the Acts pattern Matthew 28&rsquo;s note named and left unresolved, now on these pages."),
    ("rom1", "Romans", 1, "The opening of the most consequential letter ever written. Paul is in Corinth, about fifty-six years old, with the eastern Mediterranean behind him and Spain in front of him — and he needs the backing of congregations in the capital that he has never met and did not found. So he writes them a letter of introduction, and it turns into the most sustained argument in the New Testament. The first seven verses are one enormous Greek sentence in which he calls himself a SLAVE before he calls himself an apostle; then a careful, rather charming approach to strangers, in which he offers to give them a spiritual gift and then catches himself and says he wants one back. And then, in two sentences, the thesis that reorganised Europe: “I am not ashamed of the gospel; for it is God’s power for salvation to everyone who believes, to the Jew first and also to the Greek. For in it God’s righteousness is revealed, from faith to faith” — quoting Habakkuk, the answer the prophet climbed his watchtower to wait for, and the line Augustine, Luther and Wesley each dated their turning to. The rest of the chapter is the indictment: humanity knew God, would not honour him, and traded his glory down through the creature-list of Genesis 1 in reverse — man, birds, beasts, things that crawl — after which God, three times, simply “gave them over.” ⚠ It contains the most argued-over paragraph in the Bible, printed here with the vocabulary laid out and the readings given their pedigrees, and no vote cast. ⚠ And it is a trap: the vice list is bait, and the next sentence after the chapter break springs it — “therefore you are without a defense, whoever you are who judges.”"),
    ("rom2", "Romans", 2, "The trap chapter 1 set springs on the first word: “therefore you are without a defense, whoever you are who judges — for in that in which you judge another, you condemn yourself.” God shows NO PARTIALITY, rendering to each according to works, “to the Jew first and also to the Greek” — the letter's own thesis phrase, now cutting toward judgment instead of toward the gospel's advance. ⚠ Then the sentence that would outlive the argument around it: Gentiles who never received the law can still do by nature what the law requires, “a law to themselves,” its work “written on their hearts” — the New Testament's closest approach to a doctrine of conscience and natural law, quoted for centuries by readers who never opened the rest of the letter. Four rhetorical blows land on the confident teacher who cannot teach himself — steal, adultery, idols, temple robbery — and “the name of God is blasphemed among the Gentiles because of you, just as it is written.” It closes on the hardest sentence Paul's own closing note to chapter 1 named in advance: the real Jew is one inwardly, and circumcision is of the heart, “by spirit, not by letter.”"),
    ("rom8", "Romans", 8, "The chapter is built on the preposition WITH. Nine syn- compounds run from v16 to v29 \u2014 the Spirit witnesses WITH our spirit, we are heirs TOGETHER, we suffer WITH and are glorified TOGETHER, the creation groans TOGETHER and travails TOGETHER, the Spirit takes hold TOGETHER WITH us, all things work TOGETHER, and we are formed WITH the image of the Son. \u26a0 Verse 28 is the EIGHTH OF THE NINE, so the most-quoted promise in the chapter is one beat in a pattern rather than a standalone guarantee: the claim is not that events are secretly convenient but that nothing here happens alone. Two cruxes, neither voted on \u2014 the clause the KJV and RV carry at v1 and the earliest witnesses lack (it appears to have migrated up from v4, and it turns freedom from condemnation into a condition), and whether GOD is the subject at v28, where NWT and TNM take the longer reading and KJV, ASV and RV take the shorter. Plus proorizo, the most disputed word in the chapter: it names a marked-out DESTINATION and leaves the Calvinist-Arminian question to inference in both directions. And Abba \u2014 Aramaic left untranslated, then translated, exactly as at Galatians 4:6 and Mark 14:36."),
    ("1cor1", "1 Corinthians", 1, "The most practical book in the New Testament opens with the first recorded church split — and it is not about doctrine. It is about which preacher people liked best. Word has reached Paul in Ephesus, by way of a woman named Chloe and her household, that the congregation he founded in Corinth has broken into parties chanting slogans: “I am of Paul,” “I of Apollos,” “I of Cephas,” “I of Christ.” His reply does not adjudicate between them. It goes underneath them, to the thing all four parties are actually competing for — status, cleverness, a name to drop — and takes the ground away: “Has Christ been parcelled out? Paul was not crucified for you, was he?” Then the argument that has never stopped being difficult: God&rsquo;s chosen instrument is an executed provincial, which to Greeks is an idiocy and to Jews an obscenity, and God appears to have picked it precisely because it is unimpressive. “Look at your calling, brothers — not many wise, not many powerful, not many well-born.” ⚠ Along the way the apostle loses track of who he has baptised and says so in writing; a co-signer appears who may be the man beaten for Paul&rsquo;s sake in Acts 18; and the whole chapter ends where it was always going: “Let the one who boasts, boast in the Lord.”"),
    ("1cor13", "1 Corinthians", 13, "The love chapter \u2014 read at weddings, written to a congregation fighting about whose spiritual gift outranked whose. Verses 4-7 are FIFTEEN finite verbs and not one adjective: \u26a0 'love is patient, love is kind' is makrothyme\u012b, chr\u0113steuetai \u2014 'love waits long, love acts kindly' \u2014 and the KJV and ASV kept the verbs where the modern versions flattened them into adjectives, turning love from something that DOES into something that IS. One verb, katarge\u014d, runs four times through the chapter and most versions hide it under four different English words. A bronze mirror, not a glass, and a RIDDLE rather than a darkness. And 'greater', not 'greatest'. \u26a0 Verse 3 turns on a single consonant \u2014 'that I may be BURNED' against 'that I may BOAST' \u2014 and the shelf divides with the manuscripts; no vote is taken here."),
    ("2cor1", "2 Corinthians", 1, "The most personal letter Paul wrote opens like a man exhaling. A year after the argumentative First Corinthians, the relationship had nearly broken — a visit that went badly, rival missionaries who had turned the congregation against him, a severe “letter of tears” — and then, at the last moment, reconciliation. So he does not begin with the usual “I thank my God” but with a Jewish blessing: “Blessed be the God and Father of our Lord Jesus Christ, the Father of compassions and God of all comfort.” The word COMFORT then tolls ten times in five verses, an untranslatable drum-beat, because that is the argument: the God who comforts us in affliction does it so that we can comfort others with the comfort we received. He nearly died “in Asia” — an ordeal he pointedly refuses to describe — and it taught him to trust “God, who raises the dead.” Then the wound the whole warm opening was circling: his enemies had used a changed travel plan to call him a double-talker whose “yes” means nothing, and Paul turns even that into one of his great sentences — every promise of God is “Yes” in Christ, and the church&rsquo;s “Amen” is the echo of it. ⚠ The Spirit is a “down payment” (arrabōn — the same word, still, as a modern Greek engagement ring), and the chapter ends with the apostle defending his authority and then disclaiming it in the same breath: “not that we lord it over your faith, but we are fellow workers for your joy.”"),
    ("gal1", "Galatians", 1, "The angriest letter in the New Testament, and you can hear it in what is MISSING. Every other letter Paul wrote opens with a paragraph of thanks for its readers — even the exasperating Corinthians got one. This one says “grace to you and peace,” and then, where the thanks should stand, drops straight into “I am astonished that you are so quickly deserting…” A first-century reader would feel the cold the instant the courtesy did not come. Rival missionaries had followed Paul into his congregations in Galatia teaching that Gentile converts must be circumcised and keep the law of Moses to belong fully to God — and, evidently, that Paul&rsquo;s own authority was second-hand, borrowed from the apostles in Jerusalem. So the letter opens by denying that twice in its first six words (“an apostle — not FROM men nor THROUGH a man”), pronounces a curse on anyone preaching a different gospel — including himself, including “an angel from heaven,” and says it twice — and then spends the rest of the chapter proving its independence with a travelogue: after the revelation he did not go to Jerusalem, he went to Arabia; three years later he visited Cephas for a fortnight and met no other apostle but James the Lord&rsquo;s brother; the Judean congregations had never even seen his face. ⚠ And the chapter that begins in fury ends in something else entirely — the churches he had once tried to destroy repeating a rumour about him, “the one who once persecuted us is now announcing the faith he once tried to destroy,” and glorifying God because of it."),
    ("eph2", "Ephesians", 2, "Chapter 1 ended in doxology; chapter 2 opens with a diagnosis nobody softens. “You were DEAD” — not sick, not struggling, dead in trespasses and sins, following “the ruler of the authority of the air” — and then, four verses in, the hinge of the whole letter: “BUT GOD.” Two words the Greek grammar itself was straining toward, since the opening sentence never finds its own main verb until God supplies one. By grace you have been saved — the phrase interrupts its own sentence twice, muttered almost, as if Paul cannot get three clauses into the argument without saying it again. Then the letter turns to the Gentile readers directly: once called “the uncircumcision” by the so-called “circumcision,” without hope and without God in the world — but now brought near by blood. ⚠ “The dividing wall of the fence” is very likely not an abstraction: the Jerusalem temple's actual inner courts were fenced by a stone barrier, the soreg, posted with warning inscriptions threatening death to any Gentile who crossed it — two of those exact stones have been excavated and sit today in museums in Istanbul and Jerusalem. Paul nearly died over an accusation of breaking that precise rule (Acts 21:28). He tells this church that Christ has broken the wall down and made ONE NEW MAN where there were two — and closes on a building metaphor that will not hold still: “are being built together,” present tense, into a temple that is not finished yet."),
    ("eph1", "Ephesians", 1, "The calmest and most cosmic thing Paul wrote — and it may not be addressed where the title says. ⚠ The words “in Ephesus” are MISSING from the earliest manuscripts, leaving a blank where an address should stand; Marcion knew this letter as the one to Laodicea; and although Paul spent three years in Ephesus, longer than anywhere else, the letter contains not one personal greeting and twice says he has only HEARD of his readers&rsquo; faith. It reads exactly like a circular carried round a group of congregations with the destination left open. What follows the address is extraordinary: verses 3 to 14 are ONE SENTENCE in Greek — about two hundred words without a full stop, the longest in the New Testament — a man who set out to say “blessed be God” and could not find a place to stop. It runs from before the founding of the world to the gathering up of all things in heaven and earth under one head, and it is not an argument but a doxology that got away from him. Then he prays — not that anything be added, but that “the eyes of your heart” might be opened to see what is already theirs. And when he reaches for a measure of God&rsquo;s power he does not use a metaphor: he uses an event. How great is it? It is the power that raised Jesus from the dead and seated him above every rule and authority and power and lordship — which, in a city famous for magic and amulets and the great temple of Artemis, was the most practical sentence in the letter."),
    ("php1", "Philippians", 1, "A thank-you note for money, written in chains, by a man awaiting a verdict that could go either way — and it is the warmest thing Paul wrote. He does not even call himself an apostle: just “Paul and Timothy, slaves of Christ Jesus,” level with his young colleague, because nothing in this letter needs defending. The Philippians were the one congregation that never gave him trouble; they had been sending him money since the first day, and “your partnership in the gospel” is very nearly a commercial receipt. The word to watch is JOY — it sounds four times in this chapter and sixteen in four short chapters, from a prison cell. Then two of the most disarming paragraphs in the New Testament. First: there are people in Rome preaching Christ specifically to spite him, out of “envy and rivalry,” hoping to make his imprisonment worse — and his response is “what of it? &hellip; whether in pretense or in truth, Christ is being announced, and in this I rejoice.” Bad motives he shrugs at; a different gospel he had cursed twice over in Galatians. Second: asked to choose between execution and release, he cannot. “To me, to live is Christ and to die is gain” — ten Greek words with no verb in them — and then, honestly, “which I will choose, I do not know.” ⚠ He decides to expect release on the grounds that other people still need him. And he tells a proud Roman colony to “live out your CITIZENSHIP worthily of the gospel,” a word every version flattens to conduct."),
    ("php4", "Philippians", 4, "\u26a0 Writing to a Roman colony, Paul reaches outside his own vocabulary, and it can be counted: prosphiles ('lovely') and euphemos ('well spoken of') each occur ONCE in the whole New Testament, both in v8; arete \u2014 VIRTUE, the master-word of Greek ethics \u2014 occurs four times, three of them in Peter, and v8 is PAUL'S ONLY USE of it anywhere; autarkes (v11) is the central technical term of STOICISM; and memyemai (v12), 'I have been initiated', is the verb of the MYSTERY CULTS and a New Testament hapax. Four borrowed words in five verses \u2014 and he breaks the biggest one, saying he has LEARNED self-sufficiency and then locating his sufficiency in someone else. \u26a0 And the most-quoted verse in the letter is missing a word: at v13 the Byzantine text adds Christo, so the earliest text reads 'for all things I have strength in THE ONE WHO EMPOWERS ME'. The shelf splits on exactly the line it split on at Romans 8:1. What the verse says is smaller and stranger than the version on the merchandise \u2014 panta ischyo is 'I am strong for all things', a claim about capacity to ENDURE, sitting in a paragraph about being hungry. Then the chapter turns into a set of books: an account of giving and receiving, fruit to your account, and apecho, the word written on receipts \u2014 paid in full \u2014 with the money called a fragrant aroma and an acceptable sacrifice in the same breath. Euodia and Syntyche are both women, both named, their quarrel addressed from prison."),
    ("col1", "Colossians", 1, "The least important town any New Testament letter is addressed to receives one of the highest statements about Christ ever written. Colossae was a small, declining wool town in the Lycus valley, overshadowed by its richer neighbours; Paul had never been there — the congregation was founded by a local man, Epaphras — and an earthquake would flatten the valley about the time the letter was carried. Its people were being offered access to God through ranks of angels, food rules, festivals, ascetic discipline and special knowledge for insiders. Paul&rsquo;s answer is not an argument but a HYMN, almost certainly one the churches were already singing before he wrote it down: “He is the image of the invisible God, firstborn of all creation… all things were created through him and for him… and in him all things hold together.” ⚠ Two of its words have carried enormous weight: “firstborn” (prōtotokos), which the fourth century went to war over — does it place Christ inside creation, or over it? — and “fullness” (plērōma), which was probably the opponents&rsquo; own term for the graded ranks of beings between God and the world, and which Paul says settled entirely in one man. Both are laid out with their pedigrees and no vote cast. ⚠ And the height of the hymn is deliberately anchored: the cosmic paragraph — thrones and lordships, all things visible and invisible — comes to rest on an execution, “having made peace through the blood of his cross.” The chapter&rsquo;s centre is four Greek words: “Christ in you, the hope of glory.”"),
    ("1th1", "1 Thessalonians", 1, "Very probably the oldest Christian writing that survives — older than any Gospel, written about AD 50, perhaps twenty years after the crucifixion. Paul had been in Thessalonica only a few weeks: he argued in the synagogue on three sabbaths, a mob was raised in the marketplace, the house of his host Jason was stormed, and the missionaries were smuggled out of the city by night, leaving behind a congregation of brand-new converts to deal with the consequences. He had not managed to get back. This letter is what he wrote when Timothy finally returned with the news that they were still standing. ⚠ Almost everything about it is early: the greeting is the shortest he ever wrote — four words, &ldquo;grace to you and peace,&rdquo; and it stops, where every other letter extends it; there is no apostolic title, not even &ldquo;slave,&rdquo; just three names; and the conventions of Christian letter-writing have plainly not hardened yet. In verse 3 the triad of faith, love and hope appears for the first time in literature, in passing, as though the readers already knew it — and the words attached to it are working words: the LABOUR of love is exhausting toil, and &ldquo;endurance&rdquo; is literally a remaining-under. ⚠ The chapter closes with two verses widely thought to be older than the letter carrying them, a portable summary of what Gentile converts were taught — turn, serve, wait — ending in the earliest datable sentence in which Christians say what they are waiting for: &ldquo;to wait for his Son from the heavens.&rdquo; There is no timetable in it at all."),
    ("2th1", "2 Thessalonians", 1, "The most disputed of Paul&rsquo;s letters outside the Pastorals opens by looking back over its shoulder at the first one. The senders are the same three names, and the greeting fills in exactly the half that 1 Thessalonians broke off &mdash; &ldquo;grace to you and peace, FROM God the Father and the Lord Jesus Christ&rdquo; &mdash; the first of a string of verbal debts to the earlier letter that make some scholars think a later hand wrote it with the first open in front of him. ⚠ Then the chapter turns to the strongest page of RETRIBUTION anywhere in Paul: to a congregation being actively persecuted, he promises that God will &ldquo;repay affliction to those afflicting you&rdquo; at the unveiling of the Lord Jesus from heaven &ldquo;in flaming fire&rdquo; &mdash; a scene quarried whole out of Isaiah. The comfort is careful and easily missed: the vengeance is God&rsquo;s and not theirs, the account settled at the end and not by the sufferers&rsquo; own hands. ⚠ And the sentence that has divided readers for centuries sits at verse 9 &mdash; &ldquo;eternal destruction, away from the face of the Lord&rdquo; &mdash; whose single Greek preposition can mean shut OUT from his presence or ruin coming FROM it, and under which lies the old question of whether &ldquo;eternal destruction&rdquo; is unending or final. The library keeps the ambiguity and does not vote. The prayer that ends the chapter reaches back one more time, quoting the first letter&rsquo;s &ldquo;work of faith&rdquo; and &ldquo;with power&rdquo; almost word for word."),
    ("1ti1", "1 Timothy", 1, "The first of the three Pastoral letters — and the first book in the library whose Pauline authorship the majority of scholars doubt, on grounds of vocabulary, church-order and a career that will not fit Acts. ⚠ The debate is laid out on both sides; no vote is cast. What the chapter itself does is set Timothy against a slippery Ephesian error — teachers of &ldquo;a different doctrine&rdquo; lost in &ldquo;myths and endless genealogies&rdquo; — and answer them not with rival knowledge but with an aim: &ldquo;the GOAL of the charge is love, out of a pure heart.&rdquo; Then the law &ldquo;used lawfully,&rdquo; and a vice-list built on the Ten Commandments that includes <em>arsenokoitai</em>, a rare word minted from Leviticus and rendered seven different ways by the seven shelf versions — the library sets out the philology and the spread and does not adjudicate the modern question. ⚠ At the centre is the first of the Pastorals&rsquo; &ldquo;faithful sayings&rdquo;: &ldquo;Christ Jesus came into the world to save sinners — of whom I am foremost,&rdquo; present tense, the chief of sinners kept as a standing title and offered as the proof of God&rsquo;s patience. It breaks into a doxology — &ldquo;to the King of the ages, immortal, invisible, the only God&rdquo; — where the King James, following the later text, prints &ldquo;the only WISE God.&rdquo; It ends with two men &ldquo;handed over to Satan&rdquo; — a discipline meant to reform, not a curse."),
    ("2ti1", "2 Timothy", 1, "On the traditional reading the LAST thing Paul wrote — from a second imprisonment, cold and mostly abandoned, with execution in view — and the most personal of the three Pastorals, which is why even some who doubt he wrote the letters think this one keeps his own notes. Where 1 Timothy called Timothy his &ldquo;true&rdquo; child, this opens to the &ldquo;BELOVED&rdquo; child and toward &ldquo;the promise of life,&rdquo; a fitting keynote under a death sentence. ⚠ It traces a faith down three named generations — the grandmother Lois, the mother Eunice, then Timothy — the one place the New Testament follows belief through a family, and down the female line of a mixed marriage. Its heart is a charge not to be ASHAMED: &ldquo;God did not give us a spirit of cowardice, but of power and love and self-control&rdquo;; and a banker&rsquo;s confidence, &ldquo;I know whom I have believed&hellip; he is able to guard my DEPOSIT until that day&rdquo; — the entrusted gospel, to be held and handed on intact. It ends in a bleak, tender contrast: a whole province &ldquo;turned away from me,&rdquo; and one man, Onesiphorus, who &ldquo;was not ashamed of my chain&rdquo; and searched Rome until he found the prisoner."),
    ("tit1", "Titus", 1, "The shortest of the three Pastoral letters, and a working commission: Titus is left on CRETE to &ldquo;set right what was left undone&rdquo; and appoint elders town by town. The greeting is the most theological in the Pastorals — a whole sentence of doctrine before it reaches the addressee — and it rests the hope of eternal life on a striking title, &ldquo;the God who does not LIE,&rdquo; who promised it &ldquo;before times eternal.&rdquo; ⚠ Chapter 1 gives one of the clearest windows in the New Testament onto the earliest church order: it says appoint &ldquo;elders&rdquo; (v5) and then, describing the same man, calls him the &ldquo;overseer&rdquo; (v7) — two words for one office, the bishop-over-elders still centuries off. The qualifications are almost all matters of character; the one skill asked is to hold the sound teaching and rebuke those who contradict it. ⚠ Then the confrontation, with its famous flourish: Paul quotes a Cretan poet — &ldquo;Cretans are always liars, evil beasts, lazy gluttons&rdquo; — calls him &ldquo;a prophet of their own,&rdquo; and adds &ldquo;this testimony is true&rdquo; (the line is Epimenides, and carries the ancient liar&rsquo;s-paradox knot). It closes on the letter&rsquo;s whole theology of conduct: &ldquo;they profess to know God, but by their works they deny him.&rdquo;"),
    ("phm1", "Philemon", 1, "The shortest of Paul&rsquo;s letters and the only truly private one — a single page of pure tact, written to one man about one man. Onesimus, a slave, has run from his master Philemon (a well-off believer of Colossae), reached Paul in prison, and been converted; now Paul sends him home carrying this. ⚠ The strategy is in the first word: not &ldquo;apostle&rdquo; but &ldquo;PRISONER of Christ Jesus&rdquo; — Paul has every right to command and spends the whole letter refusing to, appealing &ldquo;for love&rsquo;s sake&rdquo; instead, because a free choice is worth what an order is not. He puns on the slave&rsquo;s name (Onesimus, &ldquo;useful&rdquo;): &ldquo;once USELESS to you, now USEFUL.&rdquo; He offers to pay any debt in his own hand — &ldquo;charge it to my account; I, Paul, will repay&rdquo; — and reminds Philemon that he owes Paul &ldquo;your very self.&rdquo; ⚠ And at the centre is the sentence that has weighed most in the long argument over slavery: receive him &ldquo;no longer as a slave but more than a slave, a BELOVED BROTHER.&rdquo; Paul never quite commands manumission — readers have debated the silence for two thousand years — but the word &ldquo;brother&rdquo; quietly dissolves the word &ldquo;slave&rdquo; without ever attacking it head-on. The library sets the sentence down and lets it do its slow work."),
    ("heb1", "Hebrews", 1, "An anonymous masterpiece opens with the most polished sentence in the New Testament — no greeting, no author&rsquo;s name, just a period of Greek so finished that its writer&rsquo;s identity became one of the great puzzles (Origen&rsquo;s shrug: &ldquo;God only knows&rdquo;). The thesis is stated at once: God&rsquo;s old speech was FRAGMENTARY — &ldquo;in many parts and many ways,&rdquo; a piece to each prophet — and his new speech is single and final, &ldquo;in a Son&rdquo; through whom he also &ldquo;made the ages.&rdquo; ⚠ Verse 3 reaches for the strongest words available — the Son is the RADIANCE of God&rsquo;s glory and the &ldquo;exact imprint of his substance&rdquo; (<em>charakt&#275;r</em>, the die that stamps a coin; <em>hypostasis</em>, the word the fourth century went to war over) — and then, the whole sentence having run from before creation to the cross, it rests on a SEAT: he &ldquo;sat down at the right hand of the Majesty,&rdquo; the priest who sits because the work is finished. ⚠ Then a chain of seven Old Testament quotations proving the Son higher than the angels, who are told to worship him (v6), who are mere &ldquo;winds and flame&rdquo; (v7) — while the Son is addressed as &ldquo;God&rdquo; (v8) and as the &ldquo;Lord&rdquo; who &ldquo;laid the foundation of the earth&rdquo; (v10, a psalm to Yahweh handed straight to the Son). The angels end the chapter demoted to errand-runners for the people the Son came to save."),
    ("heb11", "Hebrews", 11, "\u26a0 The chapter has a countable skeleton: PISTEI, 'by faith', opens exactly EIGHTEEN verses, and the gaps matter as much as the hits \u2014 the run breaks twice, and both times the chapter stops listing and starts arguing. A second thread brackets it: martyreo, to bear witness, five times, the last at v39 \u2014 and it is the root of MARTYR, in a chapter that ends with people sawn in two. \u26a0 Verse 1 turns on hypostasis, literally a STANDING-UNDER: substance (KJV, RV), assurance (ASV, TNM), NWT's hybrid 'assured expectation', or \u2014 in the commercial papyri \u2014 a TITLE-DEED, the document proving you own what you cannot see. It occurs five times in the NT, and one of the others is Hebrews 1:3, the word the fourth-century councils made the technical term for PERSON. \u26a0 And whose faith is v11? The base text reads the dative, 'together with Sarah', making ABRAHAM the subject; every version reads the nominative, making SARAH the subject. What decides it is a phrase about anatomy. Two words occur nowhere else in the NT \u2014 etympanisthesan (v35), stretched over a DRUM, where only RV keeps the picture with 'estirados'; and epristhesan (v37), SAWN IN TWO, the traditional death of Isaiah. \u26a0 And the most famous chapter about faith in the Bible ends on a negative: they did not receive the promise, and cannot be COMPLETED apart from us."),
    ("jas1", "James", 1, "The most Jewish and most practical book in the New Testament — wisdom literature in a Christian key, very possibly by JAMES the brother of Jesus, who calls himself only &ldquo;a slave&rdquo; and never mentions the family tie. It opens on trials: &ldquo;count it all joy&hellip; when you fall into TRIALS,&rdquo; because testing makes endurance and endurance makes a whole person. ⚠ The chapter turns on one Greek word, <em>peirasmos</em> — a &ldquo;trial&rdquo; that comes from outside (v2) and a &ldquo;temptation&rdquo; that works from inside (v13) — and James uses the pivot to block the oldest excuse: God tests no one; each is dragged off by &ldquo;his own desire,&rdquo; which conceives and bears sin, and sin brings forth death. Against that he sets a God who does not change — &ldquo;the Father of the lights, with whom there is no shadow of turning&rdquo; — who instead gives us birth by the word of truth. It is thick with echoes of the Sermon on the Mount (ask and it will be given; the good Father&rsquo;s gifts; the hearer who <em>does</em>), coins the word &ldquo;double-souled,&rdquo; and ends on the definition that has outlived a thousand sermons: ⚠ &ldquo;Pure and undefiled RELIGION&hellip; is this: to look in on orphans and widows in their affliction, and to keep oneself unspotted from the world.&rdquo;"),
    ("1pe1", "1 Peter", 1, "The New Testament&rsquo;s great letter of hope in suffering — written to scattered EXILES across five provinces of Asia Minor, by (on the traditional reading) the fisherman Peter. It names its readers by their whole condition, <em>parepid&#275;moi</em>, resident aliens living in a world that is not home, and answers their hardship with a birth: ⚠ &ldquo;he gave us NEW BIRTH into a living hope through the resurrection,&rdquo; into &ldquo;an inheritance imperishable and undefiled and unfading, kept in the heavens.&rdquo; Present trials are &ldquo;a little while&rdquo; and an assayer&rsquo;s fire: the tested faith is worth more than gold, which perishes though gold itself is proved by flame. ⚠ The chapter holds some of the NT&rsquo;s most memorable lines — loving a Christ &ldquo;whom, not having seen, you love&hellip; with joy inexpressible&rdquo;; the prophets who &ldquo;searched their own oracles&rdquo; for &ldquo;the sufferings of Christ and the glories after&rdquo;; &ldquo;gird up the loins of your mind&rdquo;; &ldquo;be holy, for I am holy&rdquo;; and the ransom paid &ldquo;not with silver or gold but with the precious blood of Christ, a lamb without blemish.&rdquo; It closes on the word that outlasts the grass: &ldquo;all flesh is grass&hellip; but the word of the Lord remains forever.&rdquo;"),
    ("2pe1", "2 Peter", 1, "The MOST DISPUTED book in the New Testament canon &mdash; the early church itself hesitated over it, and it was the last writing to win a secure place. It presents itself, deliberately, as Peter&rsquo;s LAST TESTAMENT, written knowing &ldquo;the putting off of my tent is soon.&rdquo; It opens by calling Jesus God outright &mdash; &ldquo;our God and Saviour Jesus Christ&rdquo; (the Granville-Sharp grammar named in the notes) &mdash; and tells latecomers their faith is of &ldquo;EQUAL STANDING&rdquo; (<em>isotimos</em>) with the apostles&rsquo; own. ⚠ Then the boldest phrase of its kind in the NT: through the promises believers &ldquo;become PARTAKERS of the DIVINE NATURE&rdquo; (<em>theias koin&#333;noi physe&#333;s</em>) &mdash; the seed of the Eastern doctrine of <em>theosis</em>, hedged by the verse as escaping corruption, not absorption into God. There follows a ladder of virtues, a <em>sorites</em> that Christianises the Stoic list: faith &rarr; excellence (<em>aret&#275;</em>, the crown-word of Greek ethics) &rarr; knowledge &rarr; self-control &rarr; endurance &rarr; godliness &rarr; brotherly affection &rarr; LOVE. ⚠ Against teachers who call Christ&rsquo;s coming a fable, the writer stakes all on having SEEN: &ldquo;we were EYEWITNESSES of his majesty&rdquo; on the holy mountain, when the Father&rsquo;s voice named him &ldquo;my Son, my beloved.&rdquo; And it ends on the NT&rsquo;s clearest word on inspiration &mdash; the prophetic word as &ldquo;a lamp shining in a murky place, until&hellip; the MORNING STAR rises,&rdquo; and prophecy borne not &ldquo;by the will of man, but men, CARRIED ALONG by the Holy Spirit, spoke from God.&rdquo;"),
    ("mat15", "Matthew", 15, "A hard question about hand-washing turns into a lesson on what actually defiles &mdash; quoting Isaiah&rsquo;s &ldquo;this people honors me with their lips&rdquo; and naming the Pharisees &ldquo;blind guides of the blind.&rdquo; ⚠ Then a Canaanite woman crosses into the one Gentile territory the Gospels record Jesus personally entering, and out-argues him: &ldquo;even the little dogs eat the crumbs that fall from their masters&rsquo; table&rdquo; &mdash; the Gospel&rsquo;s own superlative, &ldquo;great is your faith,&rdquo; given to the outsider it has gone furthest to mark as one. A crowd by the sea glorifies &ldquo;the God of Israel&rdquo;; then bread and fish multiplied a second time for four thousand more, seven baskets left over this time, not twelve &mdash; the vocabulary itself still tracking who is being fed."),
    ("mat16", "Matthew", 16, "The Pharisees and Sadducees ask together for a sign, as promised three chapters ago, and are refused with the same answer already given once. ⚠ Then Jesus asks who people say he is, and Peter answers, &ldquo;You are the Christ, the Son of the living God&rdquo; &mdash; met with a wordplay on Peter&rsquo;s own name, a promise to build &ldquo;my congregation&rdquo; (not, this translation insists, &ldquo;my church&rdquo;), and keys to bind and loose on earth. Then, in the same breath, the first plain prediction of the cross &mdash; and Peter, praised one moment, rebuked as &ldquo;Satan&rdquo; the next for trying to talk Jesus out of it. It closes on the cost of following at all: deny yourself, take up your cross, and a promise that some standing here will not taste death before they see the Son of Man coming in his kingdom."),
    ("mat17", "Matthew", 17, "Six days later, three of them go up a high mountain and he is TRANSFIGURED &mdash; his face like the sun, Moses and Elijah beside him, Peter offering to build tents, and out of a bright cloud the voice from the baptism saying the same sentence with one new imperative attached: &ldquo;listen to him.&rdquo; Coming down, a gag order with an expiry date, and the scribes&rsquo; Elijah question answered flat: he already came, and they did what they liked with him. Then straight into a mess at the bottom of the hill &mdash; a moonstruck boy the disciples could not heal, a rebuke for &ldquo;little faith,&rdquo; and a mustard seed against a mountain. The second passion prediction, this time with no argument from Peter. And, found only in Matthew, the temple tax: kings tax strangers rather than their own sons, so the sons are free &mdash; a freedom asserted and immediately waived, settled by a four-drachma coin in a fish&rsquo;s mouth that the chapter never says was caught. ⚠ There is no verse 21 here: the words the KJV prints are absent from the earliest manuscripts, and the gap is left showing rather than renumbered."),
    ("mat18", "Matthew", 18, "The FOURTH DISCOURSE &mdash; on life inside the congregation, and it opens on the wrong question: the disciples ask who is GREATEST. Jesus answers with their own comparative, sets a child in the middle of them, and says the way in is to TURN and become like one. Then the millstone a donkey turns, the hand and foot and eye already cut off once in the Sermon, and Gehenna. The ninety-nine left ON THE MOUNTAINS to look for the one that strayed. A three-step procedure for a brother who wrongs you, built to stop at the earliest stage and ending &mdash; if it must &mdash; at the <em>ekkl&#275;sia</em>, a word Jesus says only twice in any Gospel and which here has to be small enough to hear a private quarrel; then binding and loosing, given at 16:19 to Peter in the singular and here to everyone in the plural. And the discourse closes where it opened: two or three gathered, and Christ &ldquo;in the middle of them&rdquo; &mdash; the child&rsquo;s exact place, in the same three Greek words. Peter asks how often to forgive; the answer quotes Lamech&rsquo;s revenge-song and runs it backwards. Then ten thousand talents against a hundred denarii, two identical pleas for patience, and an ending nobody quotes. ⚠ There is no verse 11 here: the words the KJV prints are absent from the earliest manuscripts, and the gap is left showing."),
    ("mat19", "Matthew", 19, "Out of Galilee at last &mdash; the fourth of the five discourse-seams closes chapter 18, and from here the book only travels toward Jerusalem. Pharisees ask whether a man may divorce his wife FOR ANY CAUSE, which is not a neutral question but the slogan of one side of a live rabbinic dispute; Jesus answers by going behind Moses to Genesis, and distinguishes what Moses COMMANDED from what he PERMITTED, &ldquo;for your hardness of heart.&rdquo; The disciples conclude it is not worth marrying. Then children are brought &mdash; and the disciples rebuke them, one chapter after being told that the kingdom belongs to such as these; Matthew does not comment, and does not need to. ⚠ Then the rich young man, where Matthew&rsquo;s earliest text is NOT the familiar one: not &ldquo;Good teacher / why do you call me good&rdquo; (which is how Mark and Luke read, and how later copyists made Matthew read) but &ldquo;what GOOD THING shall I do / why do you ask me about the good?&rdquo; &mdash; the adjective moved off the man and onto the deed. He goes away grieving, the only person in the book invited to follow who does not. A camel, a needle, and two popular rescues that do not survive contact with the evidence. Then Peter&rsquo;s accounting question, twelve thrones promised in Judas&rsquo;s hearing, and a warning aimed straight at the man who asked: many first will be last."),
    ("mat20", "Matthew", 20, "The vineyard parable is a BRACKET: 19:30 said &ldquo;many first will be last,&rdquo; sixteen verses argue it, and v16 says it again. Workers hired at dawn, at nine, at noon, at three and at five &mdash; and the last group are idle for a reason nobody mentions in the retellings: &ldquo;<em>because no one hired us</em>.&rdquo; All are paid a denarius, and the complaint is precise: not that anyone was underpaid, but &ldquo;you have made them EQUAL to us.&rdquo; The grievance is the equality, and the answer is a Semitic idiom about a stingy eye. Then the THIRD passion prediction, the fullest &mdash; the first to name the Gentiles, and the first to say the word CRUCIFIED, which had to wait for the Romans to enter the sentence. Then, immediately, a mother asking for the two best seats; a cup her sons agree to drink without knowing what it is; and two verbs of pettiness answered by two words on a ladder going DOWN &mdash; servant, then slave &mdash; ending in the one place in Matthew where Jesus states the purpose of his death as a transaction: a ransom in exchange for many. It closes at Jericho with two blind men shouting a royal title over the crowd&rsquo;s objection, and following him up the road when they can see. ⚠ The KJV&rsquo;s extra line at v16 (&ldquo;many are called, but few chosen&rdquo;) is absent from the earliest manuscripts here and original at 22:14."),
    ("mat21", "Matthew", 21, "Jerusalem, at last. ⚠ Matthew is the only evangelist with TWO animals &mdash; a donkey and a colt &mdash; because he reads Zechariah&rsquo;s Hebrew parallelism as naming two beasts rather than saying one thing twice; the whole visual tradition, Giotto included, quietly paints one. HOSANNA is not praise but a cry for help, <em>hoshi&rsquo;a-na</em>, &ldquo;save, please&rdquo; &mdash; and the crowd is singing Psalm 118, whose middle verses Jesus will quote back against the authorities before the chapter ends. The whole city is SHAKEN, in the earthquake-word Matthew keeps for hinges. Then the temple: tables overturned, and a charge spliced from Isaiah and Jeremiah &mdash; not a den of shoplifters but a CAVE OF BANDITS, the same word as the two men crucified beside him. A fig tree with leaves and no fruit, placed immediately after a temple with activity and no fruit. The authority question, answered with a question they cannot afford to answer, and Matthew tells us why: &ldquo;we are afraid of the crowd.&rdquo; ⚠ Then the two sons, where three manuscript arrangements give two different answers and the Spanish shelf&rsquo;s two witnesses land on opposite sides. And the tenants of the vineyard, opening with Isaiah&rsquo;s Song of the Vineyard and closing on a rejected stone &mdash; with the sentence about &ldquo;a nation producing its fruits&rdquo; whose supersessionist reading this library names rather than skirts."),
    ("mat22", "Matthew", 22, "Four groups interrogate him in the temple and he answers the last question himself, after which &ldquo;no one dared ask him anything more.&rdquo; A wedding feast the invited will not attend, replaced by whoever is at the crossroads &mdash; &ldquo;both bad and good&rdquo; &mdash; and a guest with no garment who is <em>muzzled</em>, the same vivid verb Jesus will use on the Sadducees twelve verses later. ⚠ And the line &ldquo;many are called, but few are chosen&rdquo; finally sits in its own house: chapter 20&rsquo;s note said it belonged here and was imported there, and at 22:14 the manuscripts raise no dispute at all. Then the coin: Pharisees allied with HERODIANS, a trap that works whichever way he answers, and a question about whose IMAGE it carries &mdash; <em>eikōn</em>, the Genesis 1:27 word &mdash; answered with GIVE BACK, not give. The Sadducees&rsquo; seven brothers, met with an argument that rests on a present-tense &ldquo;I AM&rdquo; that the Greek supplies and the Hebrew of Exodus 3:6 does not write. Two commandments the whole Law HANGS from, like a coat on a peg. And Psalm 110&rsquo;s two lords, a puzzle sharper in Greek than in Hebrew, which he leaves open."),
    ("mat23", "Matthew", 23, "Nobody interrupts. Thirty-eight verses of uninterrupted speech, the longest sustained attack in the Gospel &mdash; and it opens by CONCEDING their authority: they sit on Moses&rsquo; seat, so &ldquo;do everything they tell you,&rdquo; a sentence the library sets out without smoothing. Widened phylacteries and lengthened fringes &mdash; and the fringe is the one Jesus wears himself, touched for healing at 9:20. Three titles refused, including the one later Christian practice has most conspicuously kept. ⚠ Then SEVEN woes &mdash; seven in the critical text, because the KJV&rsquo;s eighth (the widows&rsquo;-houses verse 14) is absent from the earliest manuscripts and cannot even agree with itself about where to stand. An oath system taken apart until no oath fails to reach God; mint and dill tithed while judgement, mercy and faithfulness are let go; a gnat strained out and a camel gulped down; and whitewashed tombs &mdash; where the lime was a WARNING, not decoration, because touching a grave made you unclean. ⚠ Then a name that does not fit: Zechariah son of Barachiah, whose parentage belongs to the prophet and whose murder belongs to another man. And then, without warning, the register breaks: &ldquo;Jerusalem, Jerusalem&hellip; how often I wanted to gather your children, the way a hen gathers her chicks &mdash; and you were not willing.&rdquo;"),
    ("mat24", "Matthew", 24, "The fifth and last discourse begins. He walks out of the temple three verses after calling it desolate, a disciple points at the stonework, and the answer is that not one stone will be left. ⚠ Then the question the whole chapter inherits: the disciples ask about the temple&rsquo;s fall, his PRESENCE (<em>parousia</em>, a word Matthew uses four times and all four here) and the completion of the age &mdash; and in Greek the last two share one article, which may mean they take all of it for one event. Wars and famines are only BIRTH PANGS, the pain that means a process is under way. Daniel named outright for the abomination, with the Gospel&rsquo;s one aside to the reader. Flight instructions too local and short-range to be about the end of the world. Lightning nobody needs to be told about, and vultures over a body. ⚠ Then the two hardest sentences in Matthew: &ldquo;this generation will not pass away&hellip;&rdquo; (four readings set out, with what each costs, including the one that concedes the terms were not met), and &ldquo;about that day and hour nobody knows &mdash; not the angels, NOR THE SON&rdquo; &mdash; three words present in the earliest manuscripts, absent from the Byzantine, and printed here, because no scribe has a motive to add them. Noah&rsquo;s generation is invoked for obliviousness, not wickedness; and one is taken and one left, where the popular reading and the flood two verses earlier point opposite ways. It ends in a single imperative: stay awake."),
    ("mat25", "Matthew", 25, "The same discourse, still running, and the last teaching in the Gospel. ⚠ Ten girls with lamps &mdash; not &ldquo;virgins,&rdquo; because nothing in the story turns on chastity and the difference between the two fives is OIL &mdash; and note that when the bridegroom takes his time, ALL TEN fall asleep. The parable does not fault the sleeping; what separates them is a decision taken before the waiting began, and the sensible five refuse to share because some things cannot be lent at the last minute. Then the talents, where the smallest share is twenty years&rsquo; wages, the two who invested get word-for-word identical praise, and ⚠ the third slave calls his master HARD &mdash; and the master does not deny it, he argues from the slave&rsquo;s own premise. Then the sheep and the goats, which stops being a parable and becomes a verdict: six ordinary items, nothing religious among them, and both groups asking the same question &mdash; &ldquo;WHEN did we see you?&rdquo; Neither knew. ⚠ It ends on two contested words, <em>kolasis</em> (rooted in pruning, not retribution) and <em>ai&#333;nios</em> (duration, or the quality of the age to come), applied to both destinies in one sentence &mdash; the textual ground of a three-way argument the library describes and does not enter. After five discourses the final criterion is not doctrine, vigilance or productivity. It is whether anyone got fed."),
    ("mat26", "Matthew", 26, "The discourses are over; from here Matthew narrates. ⚠ A jar of ointment broken over his head and an objection about the poor &mdash; where the verse quoted to defer giving is, in Deuteronomy, the premise of a command to give. Thirty pieces of silver, weighed out with Zechariah&rsquo;s own weighing-verb. A supper where bread and a cup get new names, and where the earliest text does NOT read &ldquo;new&rdquo; covenant and does read &ldquo;for many.&rdquo; Gethsemane, the oil press, where the cup he offered two ambitious brothers becomes the one he asks to be spared, and where the &ldquo;stay awake&rdquo; of the last two chapters is failed three times. A kiss, a sword put away, and a sentence to Judas with no main verb. Then two hearings in one house: inside, under oath, he describes the throne of chapter 25 from the dock; outside in the same courtyard, under oath, Peter denies him three times &mdash; plainly, then swearing, then calling down curses &mdash; and is given away by his accent."),
    ("mat27", "Matthew", 27, "The chapter Matthew tells with the fewest adjectives and the most Psalms. ⚠ Judas is filled with REGRET, not repentance &mdash; the softer word &mdash; and the priests brush him off with the very phrase Pilate will later use on them. Then a quotation Matthew assigns to JEREMIAH whose words are Zechariah&rsquo;s, laid out here rather than patched: the Hebrew of Zechariah reads &lsquo;potter&rsquo; where most Bibles print &lsquo;treasury,&rsquo; and Matthew&rsquo;s priests refuse the treasury and buy the potter&rsquo;s field. ⚠ The prisoner is printed as JESUS Barabbas &mdash; the reading Origen found in his manuscripts and objected to &mdash; so Pilate offers a choice between two men called Jesus, one of them &lsquo;son of the father.&rsquo; A basin of water that transfers nothing, and then ⚠ verse 25, printed plainly and with its history named, because no verse in this Gospel has been used to do more harm. A stranger from Cyrene conscripted with the Sermon&rsquo;s own requisition-verb. Wine with gall, not vinegar. A cry in Hebrew and Aramaic at once, which is why they mishear it as Elijah. And a torn curtain, a shaking, three lines about opened tombs that no other Gospel has and nobody can explain, a centurion whose Greek has no article in it, and a sealed stone."),
    ("mat28", "Matthew", 28, "The last chapter of the Gospel, and the first book of the New Testament this project has finished. ⚠ A great SHAKING at the tomb and the guards shaken with the same verb; a messenger who rolls the stone away and then SITS on it, which no other Gospel has; and &ldquo;he WAS RAISED&rdquo; in the passive, with the agent left unstated, as this Gospel prefers. Silver changes hands a second time, and the story the soldiers are paid to tell would convict them of sleeping on watch &mdash; Matthew leaves the hole visible and does not point at it. Then a mountain, and ⚠ the word chapter 14 promised: the eleven knelt &ldquo;but some of them DOUBTED&rdquo; &mdash; <em>distazō</em>, used twice in the whole New Testament, of Peter sinking and of these men, and this time with no rebuke at all before all authority is handed over. The hard border of 10:5-6 is thrown open to ALL THE NATIONS with no reconciliation offered; the baptismal formula is printed with the state of the evidence set out precisely rather than summarized; and the book closes on the same three words it opened with &mdash; &ldquo;I am with you&rdquo; answering Emmanuel, &ldquo;God with us.&rdquo; No ascension, no closing Amen in the earliest text: it stops with him still speaking."),
    ("mark5", "Mark", 5, "A man possessed by &lsquo;Legion&rsquo; &mdash; a Roman military word borrowed to describe a crowd inside one man &mdash; is freed among the tombs, and a herd of about two thousand pigs runs downhill into the lake carrying the spirits Jesus lets them enter without recorded comment. &#9888; The region's own name is disputed in the manuscripts, &lsquo;Gadarenes&rsquo; against &lsquo;Gerasenes,&rsquo; a real textual crux this translation reports rather than resolves. The town, more afraid of the healed man than the possessed one, asks Jesus to leave &mdash; the only request in the chapter he does not argue with &mdash; and for the first time in this Gospel he tells someone to go home and PROCLAIM rather than stay silent, sending the first missionary of the Decapolis into the story with no fisherman's background at all. Then two miracles interleave: a synagogue ruler named Jairus falls at the feet of the very class of official already plotting against Jesus, for a &lsquo;little daughter&rsquo; at the point of death; on the way, a woman twelve years sick &mdash; the same number as the age of the girl he is racing toward &mdash; touches his garment from behind and is healed by a POWER the text describes almost physically, leaving him and felt leaving. &ldquo;Daughter,&rdquo; he calls her, the only time in this Gospel he uses the word for a grown woman. Then Peter, James and John appear together for the first time as a set, taken in alone to a room already laughing at the claim that the child only sleeps &mdash; and &ldquo;Talitha koum,&rdquo; spoken in the Aramaic Jesus actually used, kept untranslated and then translated immediately, the same pattern already used for &lsquo;Boanerges.&rsquo; The silence command returns at once, the opposite instruction to the one just given a chapter before, with no stated rule for why."),
    ("jer24", "Jeremiah", 24, "Two baskets of figs, set before the temple after the first deportation to Babylon in 597 BC &mdash; one basket very good, like early-ripe figs, and one so bad the figs cannot be eaten. Jehovah's own interpretation reverses every instinct: the good figs are the exiles already gone, stripped and marched to Babylon, and the bad figs are Zedekiah, his princes, and everyone still standing in Jerusalem or scattered to Egypt. To the good figs, Jehovah promises to &lsquo;build them and not tear down, plant them and not uproot&rsquo; &mdash; two of the same six verbs handed to the prophet at his own commissioning (1:10), only now spoken as a mercy instead of a mandate &mdash; and &lsquo;a heart to know me,&rsquo; the same covenant formula this book expands to the whole house of Israel three chapters later at the New Covenant oracle. &#9888; V5's &lsquo;so I will regard&rsquo; and v7's &lsquo;to know me&rsquo; translate two different Hebrew roots four verses apart, one of formal recognition and one of relationship &mdash; kept distinct rather than flattened into one English word. To the bad figs: the identical sword-famine-pestilence sentence already delivered to Zedekiah by name three chapters earlier, and a five-way shelf split on the single word for what they become to &lsquo;all the kingdoms of the earth&rsquo; &mdash; removed, tossed to and fro, or an object of horror, depending which version is open."),
    ("jer25", "Jeremiah", 25, "A date precise enough to do arithmetic from &mdash; the fourth year of Jehoiakim, which was also the first year of Nebuchadrezzar, 605 BC, the year Babylon became the region's undisputed power. Jeremiah audits his own career first: twenty-three years of the identical, unheeded message. Then Jehovah names Nebuchadrezzar &lsquo;my servant&rsquo; without softening it, and pronounces the single most load-bearing number in the rest of the book &mdash; seventy years of service to Babylon, a prophecy this book's own later chapters (already on these pages) treat as an account that comes due on schedule. A cup of the wine of fury is handed to nation after nation in a roster that runs from Judah's nearest neighbors to powers at the edge of the known world &mdash; Judah drinks first, not last &mdash; and ends with a name hidden in a cipher: &lsquo;the king of SHESHACH,&rsquo; which unscrambles, letter for letter, to &lsquo;Babylon&rsquo; itself, the empire about to serve as everyone else's sentence discovering its own name on the list. &#9888; The chapter closes with Jehovah roaring &lsquo;from on high&rsquo; in the same verb pair Amos used to open his own book a century and a half earlier, and the shepherds &mdash; warned three chapters ago &mdash; finally get their actual sentence instead of a woe."),
    ("jer26", "Jeremiah", 26, "Jeremiah is put on trial for his life, and the charge is a sermon. Told to stand in the temple court and preach without <strong>cutting back a word</strong>, he says the one thing guaranteed to end badly: God will make this house &lsquo;like <strong>Shiloh</strong>&rsquo; &mdash; the sanctuary that already fell once, whose ruins everyone in that courtyard could have walked to. Priests, prophets, and all the people seize him on the spot: &lsquo;You will surely die.&rsquo; &#9888; What follows is the closest thing to a courtroom transcript in the prophets. The princes come up from the palace and SIT in the New Gate, which is what a court does; the priests move for conviction in three Hebrew words, &lsquo;a sentence of death for this man&rsquo;; and the verdict five verses later is the identical phrase with a negative in front. Jeremiah offers no defence at all &mdash; he confirms the charge, repeats the sermon, and says &lsquo;I am in your hand,&rsquo; arguing only that killing him would put innocent blood on the city. &#9888; Then the elders rise with a legal brief: a century earlier <strong>Micah of Moresheth</strong> said Zion would be plowed as a field, and Hezekiah did not kill him &mdash; the only place in the Hebrew Bible where one writing prophet is quoted BY NAME by another, used in court to save a man's life. And the chapter ends by telling you what usually happened instead: Uriah son of Shemaiah, who preached the same message, was extradited from Egypt by royal warrant and killed by the king personally. Jeremiah lived because one official's hand was on his side."),
    ("jer27", "Jeremiah", 27, "Jeremiah puts on a wooden yoke and walks through Jerusalem wearing it, then breaks the pieces apart and sends them to five allied kings &mdash; Edom, Moab, Ammon, Tyre, and Sidon &mdash; carrying the same order he gives Zedekiah in person: put your necks under Babylon's yoke, and live. &#9888; Verse 1 dates the chapter to the reign of Jehoiakim, but everything else addresses Zedekiah, a decade later &mdash; one of the book's best-known textual cruxes, reported here rather than silently corrected. The reason God gives for submission is not political expedience but creation itself: &lsquo;I made the earth&hellip; and I give it to whomever is right in my eyes&rsquo; &mdash; and that authority has now been handed to Nebuchadnezzar, called &lsquo;my servant,&rsquo; with an expiration date built into the same sentence. Five distinct categories of diviners promising otherwise are dismissed together. And the chapter closes on a prophecy this project can already trace from both ends: the temple vessels still left in Jerusalem &mdash; after the first deportation already took some &mdash; are going to Babylon too, against everything the false prophets promise, and will come home only on the day Jehovah decides to &lsquo;attend to&rsquo; them."),
    ("jer28", "Jeremiah", 28, "Two prophets, both titled &lsquo;the prophet,&rsquo; both claiming to speak for Jehovah, in the same room, saying opposite things. Hananiah of Gibeon confronts Jeremiah in the temple with a detailed counter-prophecy: within two years the vessels come home, Jeconiah comes home, all the exiles come home, because &lsquo;I have broken the yoke of the king of Babylon&rsquo; &mdash; said to a man still wearing an actual wooden yoke on his neck. &#9888; Jeremiah's first word is &lsquo;Amen&rsquo; &mdash; not sarcasm, a real wish to be wrong &mdash; before he states the test: prophets of doom need no verification, but a prophet of peace makes the harder claim, and &lsquo;then it will be known&rsquo; only once the words come true. Hananiah does not argue. He breaks the wooden bar off Jeremiah's neck in front of everyone. Jehovah's reply escalates rather than contradicts &mdash; wood exchanged for iron, the identical oracle in a harder material &mdash; and Jeremiah delivers a public, checkable verdict: this year, Hananiah will die, for inventing words and putting them in Jehovah's mouth. The closing verse reports the death two months later, in the seventh month &mdash; one of the only prophecies in the Bible whose fulfillment lands inside the very chapter that made it."),
    ("jer30", "Jeremiah", 30, "Jeremiah is told, almost uniquely in this book, to &lsquo;write it in a book&rsquo; &mdash; the opening half of the Book of Consolation, thirty chapters of judgment finally breaking into sustained hope. The yoke of chs. 27&ndash;28 is broken for good, on Jehovah's own timetable this time, and the people will serve &lsquo;David their king&rsquo; &mdash; a phrase the shelf splits over reading literally or dynastically, left open here. Six unbroken verses call the nation's wound flatly incurable, by any medicine that exists &mdash; and then Jehovah supplies the cure anyway, because the healer isn't bound by what medicine can normally do. The chapter closes on the &lsquo;tempest of Jehovah,&rsquo; copied almost word for word from ch. 23's denunciation of false prophets seven chapters earlier &mdash; the same storm doing different work the second time. &#9888; Its last verse belongs, in Hebrew, to this chapter, but every English Bible numbers it as Jeremiah 31:1 &mdash; a real content boundary already crossed once before on this site, at ch. 31 itself."),
]
# Spanish home-page teasers, keyed by chapter slug. The Spanish index used to
# reuse CHAPTERS' ENGLISH teaser text, so es.html showed Spanish titles over
# English descriptions. Add a line here whenever a source/es/<slug>.html lands;
# build_es WARNS (and prints no description) if one is missing, rather than
# silently falling back to English again.
TEASERS_ES = {
    "prov31": "\u26a0 Chayil es una palabra de FUERZA \u2014 como se llama a un ej\u00e9rcito, lo que es el valor, lo que son la riqueza y la capacidad \u2014 y eshet chayil (v. 10) es una MUJER DE VALOR, no un adjetivo moral. Y aqu\u00ed el castellano acierta donde el ingl\u00e9s no: RV 1909 pone \u00abMujer fuerte\u00bb, conservando la fuerza que la KJV cambi\u00f3 por \u00abvirtuous\u00bb. El registro no es accidental: a su marido no le falta SHALAL, bot\u00edn (v. 11), ella se ci\u00f1e los lomos (v. 17) y da PRESA a su casa (v. 15). \u26a0 La palabra hasta se da la vuelta dentro del cap\u00edtulo: el v. 3, en el or\u00e1culo aparte que una reina madre ense\u00f1a al rey Lemuel, le advierte que no d\u00e9 su CHAYIL a las mujeres. Le\u00eddos como lista de actividades, los vv. 13-24 describen un negocio. Y la forma importa: los vv. 10-31 son un acr\u00f3stico COMPLETO, de alef a tav sin una sola irregularidad, lo que se lee mucho mejor como alabanza hecha para recordarse que como lista de requisitos.",
    "2th1": "La más discutida de las cartas de Pablo fuera de las Pastorales se abre mirando por encima del hombro a la primera. Los remitentes son los mismos tres nombres, y el saludo completa justamente la mitad que 1 Tesalonicenses dejó cortada —«gracia a vosotros y paz, DE Dios Padre y del Señor Jesucristo»—, la primera de una serie de deudas verbales con la carta anterior que hacen pensar a algunos que una mano posterior la escribió con la primera abierta delante. ⚠ Luego el capítulo se vuelve hacia la página más fuerte de RETRIBUCIÓN que hay en Pablo: a una congregación perseguida de hecho, le promete que Dios «pagará con tribulación a los que os atribulan» en la revelación del Señor Jesús desde el cielo «en llama de fuego» —una escena extraída entera de Isaías—. El consuelo es cuidadoso y fácil de pasar por alto: la venganza es de Dios y no de ellos, la cuenta se salda al final y no por la propia mano de los que sufren. ⚠ Y la frase que ha dividido a los lectores durante siglos está en el versículo 9 —«destrucción eterna, lejos del rostro del Señor»—, cuya única preposición griega puede significar excluido DE su presencia o ruina que viene DE ella, y bajo la cual late la vieja pregunta de si «destrucción eterna» es interminable o definitiva. La biblioteca conserva la ambigüedad y no vota. La oración con que cierra el capítulo vuelve una vez más atrás, citando la «obra de la fe» y el «con poder» de la primera carta casi palabra por palabra.",
    "1pe1": "La gran carta del Nuevo Testamento sobre la esperanza en el sufrimiento —escrita a EXILIADOS dispersos por cinco provincias de Asia Menor, por (en la lectura tradicional) el pescador Pedro—. Nombra a sus lectores por su condición entera, <em>parepíd&#275;moi</em>, residentes extranjeros que viven en un mundo que no es su hogar, y responde a su penuria con un nacimiento: ⚠ «nos hizo NACER DE NUEVO a una esperanza viva por la resurrección», a «una herencia incorruptible, incontaminada e inmarcesible, reservada en los cielos». Las pruebas presentes son «un poco de tiempo» y un fuego de ensayador: la fe probada vale más que el oro, que perece aunque el oro mismo se pruebe por fuego. ⚠ El capítulo contiene algunas de las líneas más memorables del NT —amar a un Cristo «a quien, sin haberlo visto, amáis… con gozo inefable»; los profetas que «escudriñaron sus propios oráculos» sobre «los padecimientos de Cristo y las glorias tras ellos»; «ceñid los lomos de vuestro entendimiento»; «sed santos, porque yo soy santo»; y el rescate pagado «no con plata ni oro, sino con la sangre preciosa de Cristo, un cordero sin mancha»—. Cierra con la palabra que sobrevive a la hierba: «toda carne es como hierba… mas la palabra del Señor permanece para siempre».",
    "2pe1": "El libro MÁS DISPUTADO del canon del Nuevo Testamento —la iglesia primitiva misma vaciló ante él, y fue el último escrito en ganar un lugar seguro—. Se presenta, deliberadamente, como el ÚLTIMO TESTAMENTO de Pedro, escrito sabiendo que «el abandonar mi tienda es inminente». Se abre llamando a Jesús Dios sin rodeos —«nuestro Dios y Salvador Jesucristo» (la gramática de Granville-Sharp que las notas nombran)— y dice a los que llegaron después que su fe es de «IGUAL VALOR» (<em>isótimos</em>) que la de los apóstoles. ⚠ Luego la frase más audaz de su clase en el NT: por medio de las promesas los creyentes «llegan a ser PARTÍCIPES de la NATURALEZA DIVINA» (<em>theías koin&#333;noí physe&#333;s</em>) —la semilla de la doctrina oriental de la <em>theosis</em>, matizada por el versículo como huir de la corrupción, no absorción en Dios—. Sigue una escalera de virtudes, un <em>sorites</em> que cristianiza la lista estoica: fe &rarr; excelencia (<em>aret&#275;</em>, la palabra-corona de la ética griega) &rarr; conocimiento &rarr; dominio propio &rarr; perseverancia &rarr; piedad &rarr; afecto fraternal &rarr; AMOR. ⚠ Contra maestros que llaman fábula la venida de Cristo, el escritor lo apuesta todo a haber VISTO: «fuimos TESTIGOS OCULARES de su majestad» en el monte santo, cuando la voz del Padre lo nombró «mi Hijo, mi amado». Y termina con la palabra más clara del NT sobre la inspiración —la palabra profética como «una lámpara que alumbra en lugar oscuro, hasta que… salga el LUCERO de la mañana»—, y la profecía llevada no «por voluntad humana, sino que hombres, LLEVADOS por el Espíritu Santo, hablaron de parte de Dios».",
    "jas1": "El libro más judío y más práctico del Nuevo Testamento —literatura sapiencial en clave cristiana, muy posiblemente de SANTIAGO el hermano de Jesús, que se llama solo «un esclavo» y nunca menciona el parentesco—. Se abre con las pruebas: «tenedlo por sumo gozo… cuando caigáis en diversas PRUEBAS», porque la prueba hace la perseverancia y la perseverancia hace a una persona entera. ⚠ El capítulo gira sobre una sola palabra griega, <em>peirasmós</em> —una «prueba» que viene de fuera (v2) y una «tentación» que obra desde dentro (v13)— y Santiago usa el pivote para bloquear la excusa más antigua: Dios no tienta a nadie; a cada uno lo arrastra «su propia concupiscencia», que concibe y da a luz el pecado, y el pecado engendra la muerte. Frente a eso pone a un Dios que no cambia —«el Padre de las luces, en quien no hay mudanza ni sombra de variación»— que en cambio nos engendra por la palabra de verdad. Está lleno de ecos del Sermón del Monte (pedid y se os dará; los buenos dones del Padre; el que oye y <em>hace</em>), acuña la palabra «de doble alma» y termina con la definición que ha sobrevivido a mil sermones: ⚠ «La RELIGIÓN pura y sin mancha… es esta: visitar a los huérfanos y a las viudas en su aflicción, y guardarse sin mancha del mundo».",
    "heb1": "Una obra maestra anónima se abre con la frase más pulida del Nuevo Testamento —sin saludo, sin nombre de autor, solo un período de griego tan acabado que la identidad de su escritor se volvió uno de los grandes enigmas (el encogimiento de hombros de Orígenes: «solo Dios lo sabe»)—. La tesis se enuncia de golpe: el habla antigua de Dios fue FRAGMENTARIA —«en muchas partes y de muchas maneras», un trozo a cada profeta— y su habla nueva es única y definitiva, «en un Hijo» por medio del cual además «hizo los siglos». ⚠ El versículo 3 echa mano de las palabras más fuertes disponibles —el Hijo es el RESPLANDOR de la gloria de Dios y «la impronta exacta de su sustancia» (<em>charaktḗr</em>, el cuño que acuña una moneda; <em>hypóstasis</em>, la palabra por la que el siglo IV fue a la guerra)— y luego, tras correr la frase entera desde antes de la creación hasta la cruz, descansa sobre un ASIENTO: «se sentó a la diestra de la Majestad», el sacerdote que se sienta porque la obra está terminada. ⚠ Después una cadena de siete citas del Antiguo Testamento que prueban al Hijo superior a los ángeles, a quienes se manda adorarlo (v6), que son meros «vientos y llama» (v7) —mientras que al Hijo se le llama «Dios» (v8) y «Señor» que «fundó la tierra» (v10, un salmo dirigido a Yahvé entregado directamente al Hijo)—. Los ángeles terminan el capítulo degradados a recaderos de la gente que el Hijo vino a salvar.",
    "heb11": "\u26a0 El cap\u00edtulo tiene un esqueleto contable: PISTEI, \u00abpor fe\u00bb, abre exactamente DIECIOCHO vers\u00edculos, y los huecos importan tanto como las apariciones. Un segundo hilo lo enmarca: martyr\u00e9o, dar testimonio, cinco veces, la \u00faltima en el v. 39 \u2014 y es la ra\u00edz de M\u00c1RTIR, en un cap\u00edtulo que acaba con gente aserrada en dos. \u26a0 El v. 1 gira sobre hyp\u00f3stasis, literalmente un ESTAR-DEBAJO: sustancia (RV), certeza (TNM) o, en los papiros comerciales, un T\u00cdTULO DE PROPIEDAD, el documento que prueba que posees lo que no puedes ver. Aparece cinco veces en el NT, y una de ellas es Hebreos 1:3, la palabra que los concilios del siglo IV hicieron t\u00e9rmino t\u00e9cnico de PERSONA. \u26a0 \u00bfY de qui\u00e9n es la fe del v. 11? El texto base lee el dativo, \u00abjunto con Sara\u00bb, haciendo sujeto a ABRAH\u00c1N; todas las versiones leen el nominativo y hacen sujeto a SARA. Lo decide una frase sobre anatom\u00eda. \u26a0 Ventaja del espa\u00f1ol: el etympanisthesan del v. 35 es ser estirado sobre un TAMBOR, y s\u00f3lo RV conserva la imagen con \u00abestirados\u00bb donde todas las dem\u00e1s ponen \u00abtorturados\u00bb. Y el cap\u00edtulo m\u00e1s famoso de la Biblia sobre la fe acaba en negativo: no recibieron la promesa, y no pueden ser COMPLETADOS aparte de nosotros.",
    "phm1": "La más breve de las cartas de Pablo y la única verdaderamente privada —una sola página de puro tacto, escrita a un hombre acerca de un hombre—. Onésimo, un esclavo, huyó de su amo Filemón (un creyente acomodado de Colosas), llegó hasta Pablo en la cárcel y se convirtió; ahora Pablo lo envía a casa llevando esta carta. ⚠ La estrategia está en la primera palabra: no «apóstol» sino «PRESO de Cristo Jesús» —Pablo tiene todo el derecho a mandar y se pasa la carta entera negándose a hacerlo, apelando «por amor» en su lugar, porque una elección libre vale lo que una orden no vale—. Juega con el nombre del esclavo (Onésimo, «útil»): «antes te era INÚTIL, ahora es ÚTIL». Se ofrece a pagar cualquier deuda de su puño y letra —«ponlo a mi cuenta; yo, Pablo, lo pagaré»— y le recuerda a Filemón que le debe «tu propio ser». ⚠ Y en el centro está la frase que más ha pesado en la larga discusión sobre la esclavitud: recíbelo «ya no como esclavo, sino como más que esclavo, como HERMANO AMADO». Pablo nunca llega a mandar la manumisión —los lectores llevan dos mil años discutiendo ese silencio—, pero la palabra «hermano» disuelve calladamente la palabra «esclavo» sin atacarla de frente. La biblioteca deja la frase puesta y la deja hacer su trabajo lento.",
    "2ti1": "En la lectura tradicional, lo ÚLTIMO que escribió Pablo —desde una segunda prisión, con frío y casi abandonado, con la ejecución a la vista— y la más personal de las tres Pastorales, razón por la cual aun algunos que dudan que él las escribiera piensan que esta conserva notas suyas. Donde 1 Timoteo llamaba a Timoteo su «verdadero» hijo, esta se abre al «AMADO» hijo y hacia «la promesa de vida», tono apropiado bajo una sentencia de muerte. ⚠ Rastrea una fe por tres generaciones nombradas —la abuela Loida, la madre Eunice, luego Timoteo—, el único lugar donde el Nuevo Testamento sigue la fe por una familia, y por la línea femenina de un matrimonio mixto. Su corazón es un encargo a no AVERGONZARSE: «no nos dio Dios un espíritu de cobardía, sino de poder y de amor y de dominio propio»; y una confianza de banquero: «sé a quién he creído… es poderoso para guardar mi DEPÓSITO hasta aquel día» —el evangelio confiado, para sostenerlo y transmitirlo íntegro—. Termina en un contraste sombrío y tierno: una provincia entera «se apartó de mí», y un solo hombre, Onesíforo, que «no se avergonzó de mi cadena» y buscó por Roma hasta hallar al preso.",
    "tit1": "La más breve de las tres cartas Pastorales, y un encargo de trabajo: Tito queda en CRETA para «poner en orden lo que falta» y nombrar ancianos ciudad por ciudad. El saludo es el más teológico de las Pastorales —toda una frase de doctrina antes de llegar al destinatario— y apoya la esperanza de vida eterna en un título llamativo: «el Dios que no MIENTE», que la prometió «antes de los tiempos eternos». ⚠ El capítulo 1 ofrece una de las ventanas más claras del Nuevo Testamento al orden eclesial más antiguo: manda nombrar «ancianos» (v5) y luego, describiendo al mismo hombre, lo llama «obispo» (v7) —dos palabras para un solo oficio, faltando aún siglos para el obispo-sobre-ancianos—. Los requisitos son casi todos de carácter; la única destreza que se pide es sostener la sana enseñanza y refutar a los que la contradicen. ⚠ Luego la confrontación, con su célebre remate: Pablo cita a un poeta cretense —«los cretenses, siempre mentirosos, malas bestias, glotones holgazanes»—, lo llama «un profeta de ellos» y añade «este testimonio es verdadero» (la línea es de Epiménides y arrastra el antiguo nudo de la paradoja del mentiroso). Cierra con toda la teología de la conducta de la carta: «profesan conocer a Dios, pero con los hechos lo niegan».",
    "1ti1": "La primera de las tres cartas Pastorales —y el primer libro de la biblioteca cuya autoría paulina duda la mayoría de los estudiosos, por vocabulario, orden eclesial y una trayectoria que no encaja en Hechos—. ⚠ El debate se expone por ambos lados; no se emite voto. Lo que el capítulo hace es enfrentar a Timoteo con un error efesio escurridizo —maestros de «otra doctrina» perdidos en «mitos y genealogías interminables»— y responderles no con un conocimiento rival sino con un fin: «la META del encargo es el amor, de corazón puro». Luego la ley «usada legítimamente», y una lista de vicios construida sobre los Diez Mandamientos que incluye <em>arsenokoitai</em>, palabra rara acuñada a partir del Levítico y vertida de siete maneras distintas por las versiones de referencia —la biblioteca expone la filología y el abanico y no dirime la cuestión moderna—. ⚠ En el centro está el primero de los «dichos fieles» de las Pastorales: «Cristo Jesús vino al mundo para salvar a los pecadores —de los cuales yo soy el primero—», en presente, el primero de los pecadores conservado como título vigente y ofrecido como prueba de la paciencia de Dios. Estalla en una doxología —«al Rey de los siglos, inmortal, invisible, al único Dios»— donde la King James, siguiendo el texto posterior, imprime «al único y SABIO Dios». Termina con dos hombres «entregados a Satanás» —una disciplina para corregir, no una maldición—.",
    "mat1": "El Nuevo Testamento se abre con una genealogía —«el libro de la génesis de Jesucristo, hijo de David, hijo de Abraham»— la palabra que abre la Biblia (Génesis) escogida para abrir el Evangelio. Cuarenta y dos generaciones en tres paneles de catorce, de Abraham a David, de David al destierro, del destierro al Cristo —y ⚠ cuatro mujeres irrumpen en la lista de padres, tres de ellas gentiles y cada una tocada por el escándalo: Tamar, Rahab, Rut y «la mujer de Urías»—. La cuenta es cosa diseñada (catorce es el número del nombre de DAVID en hebreo), no un registro: omite tres reyes, hace correr la línea real a través del maldito Jeconías, y rompe su tamborileo de «engendró… engendró» en el último eslabón, donde Jesús no es engendrado por José sino «NACIDO de» María. ⚠ Luego el nacimiento mismo: María hallada encinta «del Espíritu Santo»; José, hombre justo, resuelto a repudiarla en secreto hasta que un ángel lo detiene en un sueño; el nombre JESÚS desplegado como «YHWH salva» («él salvará a su pueblo de sus pecados»); y la señal de la virgen de Isaías aterrizada como EMMANUEL, «Dios con nosotros» —el nombre que enmarca todo el Evangelio, que se cerrará con «yo estoy con vosotros todos los días».",
    "mat11": "Juan, ya preso, envía a preguntar lo que su propio ministerio nunca lo dejó preguntar en persona: «¿Eres tú el que ha de venir, o esperamos a otro?». Jesús responde con el vocabulario mismo de Isaías —ciegos que ven, sordos que oyen, pobres a quienes se anuncia la buena nueva—, y luego se vuelve a las multitudes: ni una caña, ni ropas suaves, sino un profeta y más que un profeta, sobre quien cita una segunda profecía del mensajero y a quien llama Elías, «si queréis recibirlo». ⚠ En el centro está uno de los versículos más discutidos del Nuevo Testamento: «el reino de los cielos padece violencia» —lecturas dadas, ninguna impuesta—. Niños que no bailan a ninguna melodía en la plaza; una variante textual real sobre si la sabiduría se justifica por sus obras o por sus hijos; ayes sobre Corazín, Betsaida y Cafarnaúm medidos contra Tiro, Sidón y Sodoma, con la jactancia de un rey de Babilonia vuelta sobre un pueblo de pescadores; una oración que esconde estas cosas de los sabios y las revela a los niños pequeños; y las palabras más suaves del Evangelio, sin paralelo en ningún otro —«venid a mí, todos los que estáis trabajados y cargados»—, que cierran sobre un yugo fácil.",
    "mat13": "El discurso de las Parábolas — siete en una sola sesión, abriendo con el Sembrador y sus cuatro tipos de suelo, y una respuesta dura a «¿por qué parábolas?»: la antigua profecía del endurecimiento de Isaías, citada con el mandato suavizado en descripción, presentada con lecturas y sin veredicto. ⚠ La cizaña sembrada entre el trigo por un enemigo de noche — una mala hierba venenosa e indistinguible del trigo hasta que espiga — dejada crecer hasta una siega con sus propios segadores. La imaginería imperial del árbol prestada para la semilla más pequeña posible en la parábola del grano de mostaza; la levadura escondida en «tres medidas» de harina, la misma palabra rara ya encontrada en la tienda de Sara (Génesis 18:6). Una fórmula de cumplimiento que no nombra a ningún profeta, citando un salmo de Asaf contra una variante minoritaria que añade «Isaías». La cizaña explicada — hijos del reino, hijos del maligno, un campo que es el mundo entero — y luego el tesoro escondido y la perla, uno hallado por accidente y otra por una búsqueda de toda la vida, ambos terminando igual. La red, y un escriba «discipulado para el reino» que bien podría ser el autorretrato del propio Mateo. Y cierra en Nazaret, rechazado en su propio pueblo, donde — una promesa del capítulo anterior cumplida por fin — sus hermanos son nombrados: Santiago, José, Simón y Judas.",
    "mat14": "Un banquete de cumpleaños termina en una ejecución — el juramento imprudente de Herodes, una hija instigada por su madre, y la cabeza de Juan el Bautista en un plato, contado en un retroceso narrativo que Mateo cierra antes de volver al «ahora». ⚠ El dolor lleva a Jesús a su séptima retirada en este Evangelio, y en vez de soledad encuentra una multitud de la que se compadece — cinco panes y dos peces, una bendición, y doce cestas sobrantes de cinco mil alimentados, el vocabulario mismo (una cesta judía pequeña, no la más grande que recibirá una multitud gentil el próximo capítulo) marcando en silencio a quién se alimenta. Luego una barca luchando contra el viento hasta la cuarta vigilia de la noche, Jesús caminando sobre el mar, y el grito de los discípulos — «¡un fantasma!» — respondido con «tened ánimo, yo soy», la misma palabra de aliento ya dada a un paralítico y a una mujer con flujo de sangre, ahora dicha por quien hace algo que el Antiguo Testamento reserva solo para Dios. ⚠ Pedro pide venir, recibe una sola palabra — «Ven» — y ya está fuera de la barca antes de empezar a hundirse: «Señor, sálvame», el mismo verbo que el propio nombre de Jesús, y «hombre de poca fe, ¿por qué dudaste?», un reproche emparejado con un verbo tan raro que solo vuelve a sonar una vez más en todo el Nuevo Testamento. Sin reprensión a la tormenta esta vez, solo presencia — y una postración en la barca por fin emparejada, tras seis postraciones anteriores en este Evangelio, con las palabras que siempre esperó: «verdaderamente eres Hijo de Dios». Cierra sobre toda una región tendiendo la mano hacia el borde de su manto.",
    "mat12": "Espigas arrancadas en sábado, respondidas con Oseas 6:6 una segunda vez, tal como se prometió —y «algo mayor que el templo está aquí». Una mano seca sanada, y por primera vez la palabra de los fariseos es «destruir», no solo «acusar». El Canto del Siervo de Isaías citado por extenso —la cita más larga del Antiguo Testamento en este Evangelio hasta ahora— sobre un siervo que «no reñirá ni gritará». ⚠ La acusación de Beelzebul, plantada en 9:34 y nombrada en 10:25, obtiene por fin su escena completa: un reino dividido no puede permanecer, y «el reino de Dios ha llegado a vosotros». ⚠ La blasfemia del Espíritu —el único pecado que no se perdona, «ni en este siglo ni en el venidero»— ofrecida con lecturas, no con un veredicto. «Camada de víboras», el insulto de Juan, regresa de la boca de Jesús contra los mismos opositores; un árbol conocido por su fruto; toda palabra ociosa, pesada. La señal de Jonás pedida y concedida —tres días y tres noches, y Nínive y la reina del sur levantándose para condenar «a esta generación». Y cierra sobre una redefinición de la familia misma: «todo aquel que haga la voluntad de mi Padre… ese es mi hermano, y hermana, y madre».",
    "mat8": "Baja del MONTE del Sermón, y empieza la mitad sanadora del resumen de 4:23 —los capítulos 5-7 fueron la enseñanza, los capítulos 8-9 son esto—. Un leproso se postra (proskynéō, el verbo de los magos, por cuarta vez) y duda no del poder sino de la VOLUNTAD: «si quieres» —«quiero»—; y entonces Jesús lo TOCA, lo que según la Ley transmite impureza al que toca, y Mateo no informa de ninguna que viaje en esa dirección. ⚠ Después un oficial romano usa las palabras exactas del Bautista, «no soy digno» (3:11, de las sandalias; aquí, de su propio techo), y argumenta desde una cadena de mando y no desde el mérito —la única inferencia de la que se dice que Jesús se maravilló—, lo que provoca la frase más dura hasta ahora: muchos se recostarán con los patriarcas desde el oriente y el occidente, y «los hijos del reino» quedarán fuera. ⚠ Pedro tiene suegra, lo que significa que Pedro tiene esposa; e Isaías 53:4 se cita sobre una tarde de visitas a enfermos, siguiendo al HEBREO («nuestras enfermedades… nuestros dolores») donde el Antiguo Testamento griego convierte el primer sustantivo en «pecados». El primer «Hijo del Hombre» del Evangelio pertenece a un hombre sin dónde dormir. ⚠ Mateo llama a la tormenta un TERREMOTO (seismós —Marcos y Lucas dicen ambos «borrasca»—), la misma palabra que usa en la crucifixión y en el sepulcro vacío; Jesús REPRENDE al mar con el verbo que se usa con los demonios, y nadie en la barca concluye nada: preguntan. Y donde Marcos tiene un endemoniado, Mateo tiene DOS; el capítulo que abrió con multitudes siguiéndolo termina con un pueblo entero pidiéndole que se vaya.",
    "mat4": "Otra vez el desierto —pero cuarenta días de él, y solo Mateo escribe «cuarenta días Y CUARENTA NOCHES», que es la frase de Moisés en el monte, donde «no comió pan»—. Tres tentaciones, respondidas cada una desde DEUTERONOMIO, el libro de la generación del desierto; y el tentador abre sobre lo último que dijo Dios: «SI eres Hijo de Dios». ⚠ Él también cita la Escritura —y omite una cláusula—. El Salmo 91 promete que los ángeles te guardarán «en todos tus caminos»; el diablo salta de la primera línea a la tercera y deja fuera esas palabras, que son justamente las que lo habrían respondido. ⚠ Luego la palabra que esta biblioteca sigue desde los magos: el diablo pide que se POSTREN ante él (proskynéō —el verbo de los magos, y la mentira de Herodes—), y Jesús responde con el único versículo de la Ley que nombra su objeto. Después, una cuarta «retirada» —el verbo de la natividad— lo lleva al norte, a Capernaúm, y la «Galilea de las NACIONES» de Isaías se cita sobre una franja fronteriza mixta (hebreo 8:23–9:1, donde el pueblo ANDA en tinieblas y Mateo lo tiene SENTADO). El ministerio se abre entonces con la frase misma del Bautista, palabra por palabra, inmediatamente después de que al Bautista lo arrestan por decirla —y cuatro pescadores dejan dos barcas, mientras el griego distingue en silencio la red de mano del par más pobre del negocio familiar con casco, padre y jornaleros—.",
    "mat3": "El desierto y el agua —los dos pasos siguientes del patrón del éxodo que puso en marcha el capítulo 2—. Un hombre con pelo de camello y un cinturón de cuero aparece en el desierto de Judea con una sola frase: «Arrepentíos, porque el reino de los cielos se ha acercado», que es, palabra por palabra, la frase con que Jesús mismo empezará en 4:17. ⚠ La ropa es una cita: 2 Reyes 1:8 viste a Elías exactamente así, y Malaquías había prometido a Elías antes del día del Señor. El versículo de Isaías con que se identifica a Juan lleva la discusión de puntuación más famosa de la Biblia —el paralelo hebreo pone el desierto con el CAMINO («en el desierto preparad el camino»), el griego lo pone con la VOZ— y Mateo lee en silencio «sus sendas» donde Isaías y el griego leen «nuestro Dios». ⚠ Después llegan juntos los fariseos y los saduceos, cosa que casi nunca ocurre, y son llamados generación de víboras y advertidos de que Dios puede levantar hijos a Abraham de las piedras que tienen a los pies —un juego de palabras que solo funciona en hebreo (banim / avanim)—. Y al final, la dificultad que todo lector siente, y que solo Mateo registra: Juan intenta impedírselo. «Yo necesito ser bautizado por ti, ¿y tú vienes a mí?». Las primeras palabras registradas de Jesús en este Evangelio son la respuesta —«deja ahora, porque así nos es conveniente cumplir toda justicia»— y entonces una voz de los cielos dice una frase armada con tres Escrituras a la vez: el hijo real del Salmo 2, el hijo amado (único) de Génesis 22, y el siervo de Isaías 42, cuya línea siguiente es «he puesto sobre él mi espíritu».",
    "mat2": "La mitad oscura de la natividad. Magos del oriente —sacerdotes astrólogos de Persia, no reyes, y Mateo nunca los cuenta— llegan a Jerusalén preguntando por un rey que NACIÓ tal, lo único que Herodes, a quien el Senado romano votó el título, no era; y la ciudad que debía alegrarse se «estremece» junto con él. ⚠ Los principales sacerdotes responden correctamente desde Miqueas, y luego nadie recorre los pocos kilómetros para ir a mirar, mientras los hombres que tienen una estrella y ninguna Escritura cruzan medio oriente y se postran en una CASA (aquí no hay establo ni pastores: esos son de Lucas, y los dos relatos nunca se solapan). Después el capítulo gira: el «en secreto» de Herodes es la misma palabra que el «en secreto» de José un capítulo antes, y el tiempo que averigua «con exactitud» se convierte en la anchura de la matanza. ⚠ Cuatro sueños, cuatro retiradas y cuatro citas —Belén, Egipto, Ramá, Nazaret—, tres de ellas célebremente difíciles: «de Egipto llamé a mi hijo» es un versículo sobre ISRAEL, el «han muerto los que buscaban la vida del niño» del ángel son las órdenes de marcha de Moisés citadas sin nota alguna, y «será llamado nazareno» es una profecía que no existe en ningún libro. Raquel, sepultada en Belén, llora por sus hijos y no quiere ser consolada —las mismas dos palabras que usó Jacob junto a la cisterna—.",
    "1john1": "La más cálida y penetrante de las cartas —y apenas una carta: sin saludo, sin nombre, sin destinatario, solo una voz que ha VISTO y TOCADO lo que predica—. ⚠ Abre como el Evangelio de Juan («lo que era desde el principio… el Verbo de vida») y luego, contra secesionistas que negaban que Cristo hubiera venido en carne, le pone las manos encima: «lo que hemos oído… visto con nuestros ojos… y palparon nuestras manos». Los testigos oculares comparten lo que vieron para que los lectores tengan COMUNIÓN (koinōnía) —con ellos, y así con el Padre y el Hijo—. Luego la primera gran declaración: ⚠ «Dios es LUZ, y en él no hay ningunas tinieblas» —la primera de las afirmaciones joánicas «Dios es», coronada por «Dios es amor» (4:8)—. Andar en luz es vivir con verdad, y «la sangre de Jesús su Hijo nos limpia de todo pecado» —una limpieza presente y continua, no impecabilidad—. El capítulo cierra citando y demoliendo tres consignas de los adversarios perfeccionistas («no tenemos pecado»; «no hemos pecado») y respondiéndolas con una admisión sincera: «si CONFESAMOS nuestros pecados, él es fiel y justo para perdonar».",
    "1th1": "Muy probablemente el escrito cristiano más antiguo que se conserva —más antiguo que cualquier Evangelio, redactado hacia el año 50, quizá veinte años después de la crucifixión—. Pablo había estado en Tesalónica solo unas semanas: discutió en la sinagoga tres sábados, se alborotó a una turba en la plaza, se asaltó la casa de su anfitrión Jasón y a los misioneros se los sacó de la ciudad de noche, dejando atrás a una congregación de conversos recién hechos para lidiar con las consecuencias. No había logrado volver. Esta carta es lo que escribió cuando Timoteo regresó por fin con la noticia de que seguían en pie. ⚠ Casi todo en ella es temprano: el saludo es el más breve que escribió —cuatro palabras, «gracia a vosotros y paz», y ahí se detiene, mientras que todas las demás cartas lo alargan—; no hay título apostólico, ni siquiera «esclavo», sino tres nombres; y las convenciones de la correspondencia cristiana manifiestamente aún no se habían endurecido. En el versículo 3 la tríada de fe, amor y esperanza aparece por primera vez en la literatura, de pasada, como si los lectores ya la conocieran —y las palabras que la acompañan son palabras de faena: el TRABAJO del amor es fatiga extenuante, y «perseverancia» es literalmente un permanecer-debajo—. ⚠ El capítulo termina con dos versículos que se consideran más antiguos que la carta que los transporta, un resumen portátil de lo que se enseñaba a los conversos gentiles —volverse, servir, esperar— que desemboca en la frase datable más antigua en que unos cristianos dicen qué esperan: «y para esperar a su Hijo desde los cielos». No hay en ella calendario alguno.",
    "php1": "Una nota de agradecimiento por dinero, escrita encadenado, por un hombre que espera un veredicto que puede ir en cualquier dirección —y es lo más cálido que escribió Pablo—. Ni siquiera se llama apóstol: solo «Pablo y Timoteo, esclavos de Cristo Jesús», a la par con su joven colaborador, porque nada en esta carta necesita defensa. Los filipenses fueron la única congregación que nunca le dio problemas; le habían estado enviando dinero desde el primer día, y «vuestra sociedad en el evangelio» es casi un recibo comercial. La palabra que hay que vigilar es GOZO: suena cuatro veces en este capítulo y dieciséis en cuatro capítulos breves, desde una celda. Luego dos de los párrafos más desarmantes del Nuevo Testamento. Primero: hay gente en Roma predicando a Cristo precisamente para fastidiarlo, «por envidia y rivalidad», esperando agravarle la prisión —y su respuesta es «¿y qué?… sea por pretexto, sea de verdad, Cristo es anunciado, y en esto me gozo». Los malos motivos los encoge de hombros; un evangelio distinto lo había maldecido dos veces en Gálatas. Segundo: puesto a escoger entre la ejecución y la libertad, no puede. «Para mí el vivir es Cristo, y el morir es ganancia» —diez palabras griegas sin un solo verbo— y luego, con franqueza, «cuál escoger, no lo sé». ⚠ Decide esperar la libertad con el argumento de que otros todavía lo necesitan. Y a una orgullosa colonia romana le dice: «ejerced vuestra CIUDADANÍA de manera digna del evangelio», palabra que toda versión aplana a conducta.",
    "php4": "\u26a0 Escribiendo a una colonia romana, Pablo sale de su propio vocabulario, y se puede contar: prosphiles (\u00abamable\u00bb) y euphemos (\u00abde buena fama\u00bb) aparecen UNA SOLA VEZ en todo el Nuevo Testamento, las dos en el v. 8; arete \u2014 VIRTUD, la palabra maestra de la \u00e9tica griega \u2014 aparece cuatro veces, tres en Pedro, y el v. 8 es EL \u00daNICO USO DE PABLO; autarkes (v. 11) es el t\u00e9rmino central del ESTOICISMO; y memyemai (v. 12), \u00abhe sido iniciado\u00bb, es el verbo de los CULTOS MIST\u00c9RICOS y un hapax. Cuatro pr\u00e9stamos en cinco vers\u00edculos \u2014 y rompe el mayor: dice que ha APRENDIDO la autosuficiencia y acto seguido sit\u00faa su suficiencia en otro. \u26a0 Y al vers\u00edculo m\u00e1s citado de la carta le falta una palabra: en el v. 13 el texto bizantino a\u00f1ade Christo, de modo que el texto m\u00e1s antiguo dice \u00abpara todo tengo fuerza en AQUEL QUE ME DA PODER\u00bb. La estanter\u00eda se divide por donde se dividi\u00f3 en Romanos 8:1. Panta ischyo es \u00absoy fuerte para todo\u00bb: capacidad de AGUANTAR, dentro de un p\u00e1rrafo sobre pasar hambre. Luego el cap\u00edtulo se vuelve un libro de cuentas, con apecho, la palabra de los recibos \u2014 pagado en su totalidad \u2014 y el dinero llamado aroma fragante y sacrificio aceptable en la misma frase. Evodia y S\u00edntique son las dos mujeres, las dos nombradas.",
    "col1": "La carta más alta sobre Cristo, dirigida al pueblo más pequeño. Pablo nunca había estado en Colosas —un pueblo lanero en decadencia del valle del Lico, eclipsado por sus vecinas y arrasado por un terremoto poco después—; la congregación la fundó Epafras, un hombre del lugar, y Pablo escribe apoyado en su informe, llamándolo «nuestro consiervo». Escribe porque algo perturba a Colosas: una mezcla de observancia judía, rigor ascético, veneración de ángeles y pretensiones de conocimiento especial. ⚠ Y obsérvese su táctica: no evita el vocabulario de los adversarios —pleno conocimiento, sabiduría, plenitud, misterio, madurez—, se lo devuelve rezado y lleno de otro contenido. Dice que Dios «nos TRASLADÓ» al reino de su Hijo, con el verbo que los imperios usaban para deportar poblaciones enteras, aquí invertido. Luego cita lo que casi con certeza es un HIMNO que la iglesia ya cantaba antes que él lo escribiera: «imagen del Dios invisible, primogénito de toda la creación… en él todas las cosas subsisten unidas… reconciliar consigo TODAS LAS COSAS, habiendo hecho la paz mediante la sangre de su cruz». ⚠ «Primogénito» es la palabra por la que el siglo IV fue a la guerra, y la nota expone ambos argumentos con sus linajes sin votar; también nombra como doctrinal la cuádruple inserción de «demás» que hace la NWT en los vv16-17, que ningún manuscrito trae. Termina con la frase más difícil de la carta —«completo lo que falta de las aflicciones de Cristo»— y con cuatro palabras que son toda la carta: «Cristo en vosotros, la esperanza de la gloria».",
    "eph2": "El capítulo 1 terminó en doxología; el capítulo 2 abre con un diagnóstico que nadie suaviza. «Estabais MUERTOS» —no enfermos, no luchando, muertos en delitos y pecados, siguiendo «al príncipe de la potestad del aire»— y luego, a los cuatro versículos, la bisagra de toda la carta: «PERO DIOS». Dos palabras hacia las que la propia gramática griega venía tensándose, porque la frase inicial nunca encuentra su verbo principal hasta que Dios lo aporta. Por gracia sois salvos —la frase interrumpe su propia oración dos veces, casi murmurada, como si Pablo no pudiera avanzar tres cláusulas en el argumento sin volver a decirlo—. Luego la carta se dirige directamente a los lectores gentiles: antes llamados «la incircuncisión» por la llamada «circuncisión», sin esperanza y sin Dios en el mundo —pero ahora acercados por la sangre—. &#9888; «El muro divisorio de la valla» muy probablemente no es una abstracción: los atrios interiores del templo de Jerusalén estaban cercados por una barrera de piedra, el soreg, con inscripciones de advertencia que amenazaban de muerte a todo gentil que la cruzara —dos de esas piedras exactas han sido excavadas y hoy están en museos de Estambul y Jerusalén—. Pablo estuvo a punto de morir por la acusación de romper esa regla precisa (Hechos 21:28). Dice a esta iglesia que Cristo ha derribado el muro e hizo UN SOLO HOMBRE NUEVO donde había dos —y cierra con una metáfora de edificio que no se queda quieta: «sois juntamente edificados», en presente, para un templo que todavía no está terminado.",
    "eph1": "Lo más sereno y más cósmico que escribió Pablo —y puede que no vaya dirigida a donde dice el título—. ⚠ Las palabras «en Éfeso» FALTAN en los manuscritos más antiguos, dejando un hueco donde debería ir una dirección; Marción conocía esta carta como la dirigida a Laodicea; y aunque Pablo pasó tres años en Éfeso, más que en ningún otro sitio, la carta no contiene ni un solo saludo personal y dos veces dice que solo ha OÍDO hablar de la fe de sus lectores. Se lee exactamente como una circular llevada de congregación en congregación con el destino en blanco. Lo que sigue al encabezado es extraordinario: los versículos 3 al 14 son UNA SOLA FRASE en griego —unas doscientas palabras sin un punto, la más larga del Nuevo Testamento—, un hombre que se propuso decir «bendito sea Dios» y no halló dónde parar. Va desde antes de la fundación del mundo hasta la reunión de todas las cosas del cielo y de la tierra bajo una sola cabeza, y no es un argumento sino una doxología que se le fue de las manos. Después ora —no para que se añada nada, sino para que «los ojos de vuestro corazón» se abran y vean lo que ya es suyo—. Y cuando busca una medida del poder de Dios no usa una metáfora: usa un suceso. ¿Cuán grande es? Es el poder que resucitó a Jesús de entre los muertos y lo sentó por encima de todo principado y autoridad y poder y señorío —lo cual, en una ciudad famosa por la magia, los amuletos y el gran templo de Artemisa, era la frase más práctica de la carta—.",
    "gal1": "La carta más airada del Nuevo Testamento, y se oye en lo que FALTA. Todas las demás cartas de Pablo abren con un párrafo de agradecimiento por sus lectores —hasta los exasperantes corintios recibieron uno—. Ésta dice «gracia y paz a vosotros» y luego, donde debería ir el agradecimiento, cae directamente en «me asombra que tan pronto os estéis apartando…». Un lector del siglo I sentiría el frío en el instante en que la cortesía no llegó. Unos misioneros rivales habían seguido a Pablo hasta sus congregaciones de Galacia enseñando que los conversos gentiles debían circuncidarse y guardar la ley de Moisés para pertenecer del todo a Dios —y, al parecer, que la autoridad del propio Pablo era de segunda mano, prestada por los apóstoles de Jerusalén—. Así que la carta abre negándolo dos veces en sus primeras palabras («apóstol —no DE PARTE de hombres ni POR MEDIO de hombre—»), pronuncia una maldición sobre cualquiera que predique un evangelio diferente —incluido él mismo, incluido «un ángel del cielo», y lo dice dos veces— y luego dedica el resto del capítulo a demostrar su independencia con un itinerario: tras la revelación no fue a Jerusalén, se fue a Arabia; tres años después visitó a Cefas quince días y no vio a más apóstol que a Jacobo, el hermano del Señor; las congregaciones de Judea ni siquiera le habían visto la cara. ⚠ Y el capítulo que empieza en furia termina en otra cosa muy distinta: las iglesias que él había intentado destruir repitiendo un rumor sobre él —«el que en otro tiempo nos perseguía ahora anuncia la fe que en otro tiempo asolaba»— y glorificando a Dios por ello.",
    "2cor1": "La carta más personal de Pablo abre como un hombre que exhala. Un año después de la argumentativa Primera de Corintios, la relación casi se había roto —una visita que salió mal, misioneros rivales que habían vuelto a la congregación en su contra, una severa «carta de lágrimas»— y luego, en el último momento, la reconciliación. Por eso no empieza con el habitual «doy gracias a mi Dios» sino con una bendición judía: «Bendito sea el Dios y Padre de nuestro Señor Jesucristo, el Padre de las compasiones y Dios de todo consuelo». La palabra CONSUELO tañe entonces diez veces en cinco versículos, un redoble intraducible, porque ese es el argumento: el Dios que nos consuela en la tribulación lo hace para que podamos consolar a otros con el consuelo que recibimos. Casi murió «en Asia» —una prueba que se niega rotundamente a describir— y ello le enseñó a confiar en «Dios, que resucita a los muertos». Luego la herida que rodeaba toda la cálida apertura: sus enemigos habían usado un plan de viaje cambiado para llamarlo hombre de doble lenguaje cuyo «sí» no vale nada, y Pablo convierte incluso eso en una de sus grandes frases —cada promesa de Dios es «Sí» en Cristo, y el «Amén» de la iglesia es el eco de ello—. ⚠ El Espíritu es un «anticipo» (arrabōn —la misma palabra, todavía, que un anillo de compromiso en griego moderno—), y el capítulo termina con el apóstol defendiendo su autoridad y luego renunciando a ella en el mismo aliento: «no que nos enseñoreemos de vuestra fe, sino que somos colaboradores de vuestro gozo».",
    "1cor1": "El libro más práctico del Nuevo Testamento abre con la primera división eclesial de la que hay registro —y no va de doctrina—. Va de qué predicador le caía mejor a cada cual. A Pablo, en Éfeso, le ha llegado noticia por medio de una mujer llamada Cloé y su casa de que la congregación que él fundó en Corinto se ha partido en bandos que corean consignas: «yo soy de Pablo», «yo de Apolos», «yo de Cefas», «yo de Cristo». Su respuesta no arbitra entre ellos. Se mete por debajo, hasta aquello por lo que compiten en realidad los cuatro bandos —posición, ingenio, un nombre que dejar caer— y les quita el suelo: «¿Ha sido repartido Cristo? ¿Acaso fue Pablo crucificado por vosotros?». Y luego el argumento que nunca ha dejado de ser difícil: el instrumento escogido por Dios es un provinciano ejecutado, lo cual para los griegos es una idiotez y para los judíos una obscenidad, y Dios parece haberlo escogido justamente porque no impresiona. «Mirad vuestra vocación, hermanos: no muchos sabios, no muchos poderosos, no muchos de noble cuna». ⚠ Por el camino el apóstol pierde la cuenta de a quién ha bautizado y lo dice por escrito; aparece un cofirmante que puede ser el hombre golpeado por causa de Pablo en Hechos 18; y todo el capítulo termina donde siempre iba: «El que se jacta, jáctese en el Señor».",
    "1cor13": "El cap\u00edtulo del amor \u2014 le\u00eddo en las bodas, escrito a una congregaci\u00f3n que se peleaba por qui\u00e9n ten\u00eda el don m\u00e1s alto. Los vv. 4-7 son QUINCE verbos conjugados y ning\u00fan adjetivo: \u26a0 \u00abel amor es sufrido, es benigno\u00bb es makrothyme\u012b, chr\u0113steuetai \u2014 \u00abel amor espera largamente, obra con bondad\u00bb. Un solo verbo, katarg\u00e9o, recorre cuatro veces el cap\u00edtulo y RV lo reparte en tres expresiones distintas. Un espejo de bronce, no de vidrio, y un ENIGMA en vez de una oscuridad. Y en el v. 13 el castellano lee mejor que el ingl\u00e9s: \u00abla MAYOR\u00bb es comparativo, como el griego, mientras que todas las versiones inglesas fuerzan el superlativo. \u26a0 El v. 3 depende de una sola consonante \u2014 \u00abpara ser QUEMADO\u00bb frente a \u00abpara JACTARME\u00bb \u2014 y aqu\u00ed no se vota.",
    "rom1": "El comienzo de la carta más consecuente jamás escrita. Pablo está en Corinto, con unos cincuenta y seis años, el Mediterráneo oriental a la espalda y España delante —y necesita el respaldo de unas congregaciones de la capital que nunca ha visto y que no fundó—. Así que les escribe una carta de presentación, y le sale el argumento más sostenido del Nuevo Testamento. Los siete primeros versículos son UNA sola frase griega en la que se llama ESCLAVO antes de llamarse apóstol; luego una aproximación cuidadosa, y hasta simpática, a unos desconocidos: se ofrece a darles un don espiritual y acto seguido se corrige y dice que quiere recibir otro. Y entonces, en dos frases, la tesis que reorganizó Europa: «No me avergüenzo del evangelio; porque es poder de Dios para salvación a todo el que cree, al judío primeramente y también al griego. Porque en él se revela la justicia de Dios, de fe a fe» —citando a Habacuc, la respuesta que el profeta subió a su atalaya a esperar, y la línea en la que Agustín, Lutero y Wesley fecharon cada uno su vuelco—. El resto del capítulo es la acusación: la humanidad conoció a Dios, no quiso honrarlo, y cambió su gloria bajando por la lista de criaturas de Génesis 1 al revés —hombre, aves, bestias, reptiles—, tras lo cual Dios, tres veces, sencillamente «los entregó». ⚠ Contiene el párrafo más discutido de la Biblia, impreso aquí con el vocabulario desplegado, las lecturas con su linaje y ningún voto emitido. ⚠ Y es una trampa: la lista de vicios es cebo, y la frase que sigue al corte de capítulo la cierra —«por lo cual estás sin defensa, quienquiera que seas tú que juzgas»—.",
    "rom2": "La trampa que el cap\u00edtulo 1 tendi\u00f3 se cierra en la primera palabra: \u00abpor lo cual eres inexcusable, quienquiera que seas t\u00fa que juzgas \u2014pues en lo que juzgas a otro, te condenas a ti mismo\u2014\u00bb. Dios no muestra ACEPCI\u00d3N DE PERSONAS, y paga a cada uno conforme a sus obras, \u00abal jud\u00edo primeramente y tambi\u00e9n al griego\u00bb \u2014la misma frase de la tesis de la carta, ahora cortando hacia el juicio en vez de hacia el avance del evangelio\u2014. \u26a0 Luego la frase que sobrevivir\u00eda al argumento que la rodea: los gentiles que nunca recibieron la ley pueden, aun as\u00ed, hacer por naturaleza lo que la ley exige, \u00abley para s\u00ed mismos\u00bb, su obra \u00abescrita en sus corazones\u00bb \u2014lo m\u00e1s cercano en el Nuevo Testamento a una doctrina de la conciencia y la ley natural, citada durante siglos por lectores que nunca abrieron el resto de la carta\u2014. Cuatro preguntas ret\u00f3ricas golpean al maestro seguro de s\u00ed que no puede ense\u00f1arse a s\u00ed mismo \u2014hurto, adulterio, \u00eddolos, sacrilegio\u2014 y \u00abel nombre de Dios es blasfemado entre los gentiles por causa de vosotros, como est\u00e1 escrito\u00bb. Cierra con la frase m\u00e1s dura que la propia nota final del cap\u00edtulo 1 anunci\u00f3 de antemano: el verdadero jud\u00edo lo es interiormente, y la circuncisi\u00f3n es la del coraz\u00f3n, \u00aben esp\u00edritu, no en letra\u00bb.",
    "rom8": "El cap\u00edtulo est\u00e1 construido sobre la preposici\u00f3n CON. Nueve compuestos con syn- van del v. 16 al v. 29: el esp\u00edritu da testimonio JUNTO CON el nuestro, somos coherederos, padecemos CON y somos glorificados JUNTAMENTE, la creaci\u00f3n gime JUNTAMENTE y est\u00e1 de parto JUNTAMENTE, el esp\u00edritu toma la carga JUNTO CON nosotros, todas las cosas obran JUNTAMENTE, y somos formados CON la imagen del Hijo. \u26a0 El v. 28 es el OCTAVO DE LOS NUEVE: la promesa m\u00e1s citada del cap\u00edtulo es un comp\u00e1s de un patr\u00f3n, no una garant\u00eda suelta. Y en el v. 22 el espa\u00f1ol acierta donde el ingl\u00e9s no: RV pone \u00abgimen \u00e1 una, y \u00e1 una est\u00e1n de parto\u00bb, doblando la expresi\u00f3n igual que el griego dobla el prefijo. Dos pasajes disputados y sin voto: la cl\u00e1usula que RV lleva en el v. 1 y los testigos m\u00e1s antiguos no, y si DIOS es el sujeto en el v. 28, donde TNM toma la lectura larga y RV la breve.",
    "acts1": "La única secuela de la Biblia. Lucas toma la pluma por segunda vez, se dirige al mismo Teófilo, y abre llamando a su Evangelio entero apenas «el primer relato… de todo lo que Jesús COMENZÓ a hacer y a enseñar» —lo que deja en pie la pregunta obvia de quién está haciendo la continuación—. Cuarenta días de apariciones terminan en un monte a las afueras de Jerusalén con los discípulos haciendo la pregunta que llevan haciendo desde siempre —«Señor, ¿es en este tiempo cuando restauras el reino a Israel?»— y recibiendo una respuesta que rechaza el calendario sin rechazar la esperanza, y que además les entrega un mapa: Jerusalén, Judea y Samaria, y el extremo de la tierra. Ese mapa resulta ser el índice de los veintisiete capítulos que siguen. Luego una nube, y dos varones de blanco preguntándoles por qué siguen ahí parados mirando hacia arriba. El resto del capítulo es la iglesia haciendo lo único que puede hacer antes de Pentecostés: vuelve andando camino de un sábado, sube la escalera y espera —un pescador, un recaudador que había trabajado para Roma y un zelote del partido que mataba a esos recaudadores, junto con las mujeres, los hermanos que no habían creído, y María, en la última mención que la Escritura le concede—. Después Pedro se pone de pie entre «una multitud de nombres, como ciento veinte» para llenar la duodécima silla vacía, y la iglesia echa suertes por última vez en toda la Biblia. ⚠ Trae además el paréntesis más incómodo del Nuevo Testamento: el relato de Lucas sobre cómo murió Judas, que no concuerda con el de Mateo —impreso aquí con las dos lecturas y sin voto—.",
    "acts3": "Un hombre cojo de nacimiento, sanado en la puerta la Hermosa del templo — el primer milagro de Hechos obrado por alguien que no es Jesús, y el primer movimiento de Pedro es negar el mérito. «No tengo plata ni oro», y una orden, «en el nombre de Jesucristo el Nazareno, levántate y anda» — una frase que de verdad divide a los manuscritos, no solo a las traducciones: el testigo más antiguo por sí solo trae el simple «anda», mientras que el texto bizantino y el estándar crítico moderno añaden los dos «levántate y». ⚠ El sermón de Pedro en el Pórtico de Salomón nombra a Jesús con una palabra griega, <em>pais</em>, que todo el estante se divide en traducir — KJV «Hijo» (Son), el resto «siervo» (servant), la misma bifurcación entre RV60 y NVI. Cierra con «los tiempos de la RESTAURACIÓN de todas las cosas» — un solo sustantivo raro, apokatástasis, que Orígenes después estiraría hasta una doctrina de salvación universal que la iglesia en general nunca adoptó. Y una promesa entregada a una multitud judía en un atrio judío, «a vosotros primeramente», el orden que Pablo pasará Romanos entero repitiendo.",
    "acts2": "Pentecostés, y el día en que se paga la promesa que el capítulo 1 se negó a fechar. ⚠ Lucas es cuidadoso dos veces y todas las versiones lo desdibujan una: no hay viento y no hay fuego, hay un SONIDO COMO de viento violento y lenguas COMO DE fuego —y <em>glōssa</em> significa el órgano, la forma que hace una llama y un idioma, los tres vivos en un mismo párrafo—. El milagro se sitúa en el oído de los que escuchan tanto como en la boca de los que hablan. ⚠ La lista de naciones lleva dentro JUDEA, textualmente segura en toda edición impresa y geográficamente inexplicable. Luego el sermón de Pedro, y dos lugares donde el argumento está visiblemente construido sobre la Biblia griega: el «después» sin fecha de Joel se cita como «EN LOS ÚLTIMOS DÍAS», y todo el argumento sobre David gira en torno a <em>diaphthora</em>, DESCOMPOSICIÓN —donde el hebreo <em>shachat</em> es «la fosa» y el caso a partir de un cuerpo podrido no llega a plantearse—. ⚠ Y en el v38 el bautismo es «sobre el nombre de Jesucristo»: el patrón de Hechos que la nota de Mateo 28 nombró y dejó sin resolver, ya en estas páginas.",
    "psalms1": "La puerta de entrada al himnario de la Biblia. Los 150 salmos son las oraciones y cánticos de Israel para todo clima del alma —pero el libro no abre con una oración—. Abre con un POEMA DE SABIDURÍA, el Salmo 1, que se planta en el umbral y te dice cómo leer todo lo que hay detrás: hay dos caminos, el del justo y el del malvado, y toda la vida depende de cuál andes. El hombre feliz —y la primera palabra del Salterio es «Feliz» (ashrei), la misma que abre las Bienaventuranzas— no baja la escalera de los malvados (andar, luego detenerse, luego sentarse) sino que se deleita en la ley de Jehová y la murmura de día y de noche; y así es un árbol plantado junto al agua, fecundo y verde, mientras que los malvados son tamo que el viento sencillamente se lleva. «Jehová conoce el camino de los justos, mas el camino de los malvados perecerá.» Un poema callado que es la puerta al cancionero que Jesús cantó.",
    "psalms23": "El capítulo más leído del Salterio y uno de los más leídos de la Biblia: seis versículos en los que casi todas las líneas famosas resultan llevar algo que el castellano ha dejado caer sin decirlo. &#9888; «Pastor» es un título REAL en todo el Cercano Oriente antiguo, no una ternura campestre, así que el primer verso afirma quién gobierna — la misma metáfora que Jeremías 23 recorre desde el extremo contrario. &#9888; «Confortará mi alma» no tiene ningún alma: nefesh es la garganta, el aliento, el ser entero, y yeshovev es shuv — «me hace volver la VIDA». Las sendas son ma'gelei, RODADAS de rueda. &#9888; En el verso 4 el poema deja de hablar DE Dios y empieza a hablarLE — de tercera a segunda persona, en el centro exacto, a oscuras — y ya no vuelve atrás; el valle es un gei, un barranco angosto; y tsalmavet es la crux: la «sombra de muerte» masorética frente a la «oscuridad profunda» revocalizada de los léxicos, 18 apariciones, diez de ellas en Job. Luego el pastor sencillamente sale de escena: los versos 5 y 6 son un ANFITRIÓN y una casa, y el aceite es dashen — untar de grasa a un huésped — y no mashach, el verbo de ungir del que sale Mesías. &#9888; El último verso guarda dos cosas que toda versión conocida pierde: el bien y el amor leal no «siguen» sino que PERSIGUEN (radaph, el verbo de caza), y le-orekh yamim es «por largura de días», una vida larga, no «para siempre». Las consonantes finales admiten tres lecturas; los masoretas las vocalizaron shuv, «VOLVERÉ» — lo que enmarca la segunda mitad del salmo con la misma raíz del verso 3, un marco que desaparece en toda traducción que imprima «moraré».",
    "psalms27": "Un salmo de dos mitades que parecen dos estados de \u00e1nimo distintos hasta que la \u00faltima l\u00ednea los une. Los vers\u00edculos 1-6 son pura confianza \u2014\u00abJehov\u00e1 es mi luz y mi salvaci\u00f3n, \u00bfa qui\u00e9n temer\u00e9?\u00bb\u2014, un ej\u00e9rcito acampado, guerra que se levanta, y nada de eso basta para sacudir lo \u00fanico que David pide: sentarse en la casa de Jehov\u00e1 y ser examinado como un sacerdote examina una ofrenda. Luego, sin aviso, el vers\u00edculo 7 gira hacia un ruego urgente y sin resolver \u2014\u00abno escondas tu rostro\u00bb, un padre y una madre que han soltado, testigos falsos que se cierran\u2014, y la l\u00ednea m\u00e1s famosa del salmo se corta a media frase, sin que la cl\u00e1usula del \u00abentonces\u00bb llegue jam\u00e1s. &#9888; El grito con que se ofrecen los sacrificios del v. 6 usa la misma palabra hebrea, teru'ah, que el ruido que derrib\u00f3 el muro de Jeric\u00f3 dos cap\u00edtulos antes en este estante: el mismo grito, vuelto de arma en alabanza.",
    "psalms51": "\u26a0 El verbo del v. 12 es BARA \u2014 el verbo de G\u00e9nesis 1:1, que en toda la Biblia hebrea lleva S\u00d3LO a Dios como sujeto. Ning\u00fan ser humano bara nada, y no es la palabra corriente de hacer o formar. As\u00ed que \u00abcrea en m\u00ed un coraz\u00f3n limpio\u00bb no pide una mejora: pide el acto de la primera frase de la Biblia, ejecutado sobre un coraz\u00f3n. \u26a0 Sobre la numeraci\u00f3n: en hebreo el encabezamiento ES el texto, de modo que cada vers\u00edculo va dos por delante \u2014 la l\u00ednea famosa es el Salmo 51:10 en castellano y el v. 12 en esta p\u00e1gina. \u26a0 Y el salmo se contradice a la vista: \u00abno quieres sacrificio\u00bb (v. 18) y tres l\u00edneas despu\u00e9s \u00abentonces subir\u00e1n novillos sobre tu altar\u00bb (v. 21). La lectura m\u00e1s llana es que los dos \u00faltimos vers\u00edculos son una mano posterior que no pudo dejar el v. 18 como \u00faltima palabra. Tres palabras para el mal que no son sin\u00f3nimas, cada una con su verbo: borrar, lavar, limpiar. El hisopo, el manojo que unta la sangre en los postes de la Pascua. Y \u00abcontra ti solo he pecado\u00bb, dicho por un hombre que hizo matar a un soldado.",
    "psalms91": "El capítulo más buscado de 2025 y la promesa de protección de sonido más incondicional de la Biblia &mdash;razón por la cual el diablo la cita&mdash;. &#9888; No lleva encabezamiento alguno: ni autor, ni tono, ni ocasión (la Septuaginta se lo atribuyó luego a David; el Talmud, a Moisés; el hebreo no nombra a nadie). Abre apilando CUATRO nombres de Dios en dos versos —Elyon, Shaddai, YHVH, «mi Dios»—, del título más alto al posesivo más íntimo en un respiro, y sus verbos hablan de hospedarse hasta el alba, no de residir. &#9888; El verso 4 hace de la FIDELIDAD de Dios la armadura («escudo y socherah es su emet» —y socherah no aparece en ningún otro lugar de la Biblia hebrea—). Los versos 5 y 6 disponen cuatro terrores sobre un reloj, noche-día-oscuridad-mediodía; y el cuarto, qetev, es por donde entró en el cristianismo el DEMONIO MERIDIANO: un azote en hebreo, <em>daimoniou mesembrinou</em> en la Septuaginta, <em>daemonium meridianum</em> en la Vulgata, y ya en el siglo IV el demonio patrono de la acedia monástica. &#9888; La gramática del verso 9 se rompe a mitad de frase y tres versiones la reparan de tres maneras distintas. &#9888; Los versos 11 y 12 son los que cita el tentador en Mateo 4:6, y desde el lado hebreo se ve exactamente lo que omitió: el hebreo tiene tres cláusulas y la cita tiene dos, y la que falta es «que te guarden en todos tus caminos» —protección en el camino, que no es garantía para tirarse de un tejado—. El verso 13 pone cuatro bestias bajo el pie, entre ellas <em>tannin</em>, el gran monstruo marino de Génesis 1:21; y su <em>peten</em> se convirtió en el BASILISCO de la Vulgata, un segundo monstruo que este salmo le regaló a Europa por vía de traducción. Luego, en el verso 14, la voz cambia a la primera persona de Dios sin aviso alguno, y el salmo se cierra en <em>orekh yamim</em>, la misma frase con que termina el Salmo 23 —aquí con el verbo («lo SACIARÉ») que zanja que se trata de una vida larga y no de la eternidad.",
    "psalms121": "El primero de quince Cánticos de las subidas (120-134), la única serie de salmos consecutivos del Salterio que comparte un solo título — cantados, dice la tradición, por peregrinos que subían a Jerusalén para las grandes fiestas, o uno por uno en los quince escalones del Templo mismo. Ocho versículos giran sobre una sola palabra: SHAMAR, «guardar», cae seis veces en seis líneas, la mayor concentración de una raíz en un salmo tan corto. «Alzaré mis ojos a los montes: ¿de dónde vendrá mi ayuda?» abre con una pregunta real que el hebreo deja abierta (solo la KJV inglesa la lee como afirmación); el v. 2 la responde, y el resto del salmo se dedica a insistir en que la respuesta nunca duerme — ni dormita, ni duerme, ni una sola vez, de día o de noche, sol o luna — y cierra con la misma promesa que Dios le hizo una vez a un hombre asustado y solo en Betel: te guardaré por dondequiera que fueres.",
    "psalms139": "\u26a0 Chaqar, escudri\u00f1ar, aparece exactamente DOS VECES y enmarca el salmo: \u00abme has escudri\u00f1ado\u00bb (v. 1) y \u00abescudri\u00f1ame\u00bb (v. 23) \u2014 y en medio est\u00e1n los vv. 19-22, la parte que nadie cita, donde el que habla pide a Dios que mate a gente y dice que los aborrece con un ODIO COMPLETO. Le\u00edda como marco, la petici\u00f3n final no es un a\u00f1adido piadoso: es someter a examen lo que se acaba de decir. \u26a0 El vers\u00edculo m\u00e1s dif\u00edcil lo decide una nota de escriba: en el v. 16 el hebreo trae un KETIV/QER\u00c9 \u2014 escrito \u00aby NO\u00bb, le\u00eddo \u00aby PARA \u00c9L\u00bb \u2014, una letra y la cl\u00e1usula se da la vuelta. \u26a0 El golmi del mismo vers\u00edculo aparece UNA SOLA VEZ en la Biblia hebrea: masa informe, la ra\u00edz del GOLEM de la leyenda posterior, que RV y TNM traducen \u00abembri\u00f3n\u00bb. Y la l\u00ednea m\u00e1s citada descansa sobre una palabra suplida: RV 1909 lee la maravilla del v. 14 como perteneciente a LAS OBRAS DE DIOS y no al que habla. Ri\u00f1ones como sede de la conciencia (v. 13), un vientre ENTRETEJIDO como una sucot, una persona BORDADA en las profundidades de la tierra, y un \u00abcamino de dolor\u00bb final que la KJV s\u00f3lo admite en su margen.",
    "jhn3": "Nicodemo viene de noche, y toda la conversación corre sobre un juego de palabras que ninguna lengua puede conservar. &#9888; <em>An&#333;then</em> significa a la vez «de arriba» y «otra vez»: Jesús dice que hay que nacer <em>an&#333;then</em>, Nicodemo oye el segundo sentido y hace la famosa pregunta absurda sobre volver al vientre. Contada en el archivo, la palabra aparece 13 veces en el Nuevo Testamento, cinco de ellas en Juan, y todos los demás usos jonaicos son espaciales; Gálatas 4:9 demuestra que el sentido temporal existe, así que el malentendido es una posibilidad real del griego. &#9888; Y Juan lo resuelve él mismo en el v31, glosando <em>an&#333;then</em> con «del cielo» en el mismo verso. Cinco versos después llega un segundo juego: <em>pneuma</em> es viento Y espíritu. &#9888; Luego la frase más citada del mundo, con dos cosas que las traducciones pierden: <em>hout&#333;s</em> es MODO y no cantidad («así fue como Dios amó al mundo», no «tanto» —y aquí la RV 1909 antigua acierta donde casi todos fallan—), y <em>monogen&#275;s</em> es «el Hijo único», no «unigénito», que entró por el latín. &#9888; Y una decisión tomada en público: los manuscritos griegos no llevan comillas, muchos editores leen los vv16-21 como el evangelista y no como Jesús, y como esta traducción imprime letra roja no puede abstenerse de elegir; <strong>el rojo termina en el versículo 15 y Juan 3:16 no va en rojo aquí</strong>, con la nota dando las dos lecturas y diciendo que nada teológico depende de ello.",
    "jhn6": "Cinco panes y dos pececillos alimentan a cinco mil, sobran doce cestas, y la multitud trata de hacerlo rey a la fuerza — así que se retira solo a un monte. Esa noche los discípulos reman en una tormenta y lo ven caminando sobre el agua: «Yo soy; no temáis» — las mismas dos palabras, <em>egō eimi</em>, que este Evangelio deja en otros lugares como afirmación absoluta de autonombramiento divino. La multitud lo alcanza pidiendo una señal mayor que la que acaba de comer, y recibe en cambio el primero de los siete dichos «yo soy» de este Evangelio con predicado expreso: «YO SOY EL PAN DE VIDA». ⚠ Luego el lenguaje se vuelve físico y no retrocede: el verbo corriente para comer cede, seis veces seguidas, a una palabra griega más tosca que propiamente significa ROER — siguiendo con exactitud cuánto público le cuesta la enseñanza. «Dura es esta palabra; ¿quién la puede oír?», dicen algunos de sus propios discípulos, y por primera vez en este Evangelio, se vuelven atrás y ya no andan con él. La respuesta de Pedro a «¿queréis iros también vosotros?» no es una lectura más fácil de la enseñanza, sino una confesión de que no hay ningún otro lugar que valga la pena — «Señor, ¿a quién iremos? Tú tienes palabras de vida eterna» — un título para Jesús en el v. 69 («el Santo de Dios» frente al bizantino «el Cristo, el Hijo del Dios viviente») en el que ni el propio estante se pone de acuerdo. Cierra con Judas, nombrado por primera vez con el nombre de su padre, ya un diablo, todavía uno de los doce.",
    "jhn5": "Un hombre que lleva treinta y ocho años tendido junto a un estanque, y una pregunta que suena casi cruel — «¿Quieres quedar sano?». Es sanado, se le manda cargar su camilla, y es SÁBADO: aquí empieza la primera hostilidad real de este Evangelio, no por la sanación sino por la camilla. ⚠ El versículo 4 — el ángel que agita el agua — falta en estas páginas; los manuscritos griegos más antiguos no lo tienen, así que la numeración simplemente lo salta, del v. 3 al v. 5. Luego, por llamar a Dios su propio Padre, Jesús es acusado de «hacerse IGUAL A DIOS» (isos, la palabra llana, sin suavizar en ninguna versión comparada) — y el largo discurso que sigue (vv. 19–47), el discurso más largo de Jesús en este Evangelio hasta ahora, responde a esa acusación en vez de retirarse de ella: el Hijo no puede hacer nada por sí mismo, que resulta ser la afirmación mayor, no la menor. ⚠ «Viene la hora, y ahora es» (v. 25) es la fórmula exacta que plantó Juan 4:23, aplicada ahora a los muertos que oyen la voz del Hijo y viven — y tres versículos después la MISMA fórmula pierde su segunda mitad (v. 28), marcando una hora que todavía solo viene. Se llaman cuatro testigos — Juan el Bautista, las obras, el Padre, las Escrituras — y el «escudriñáis las Escrituras» del v. 39 es genuinamente ambiguo en griego entre una orden y una afirmación, con la KJV leyéndolo de un modo y casi todas las demás del otro.",
    "jhn4": "La conversación más larga que Jesús tiene con nadie en ningún Evangelio, y empieza pidiéndole ÉL un favor a ELLA. &#9888; Léase contra <em>Juan 3</em>, porque los dos están construidos como pareja: un varón con nombre, principal, de dentro, que viene DE NOCHE; y una mujer extranjera y anónima encontrada al MEDIODÍA. Él entiende mal <em>an&#333;then</em>; ella entiende mal «agua viva» —que en griego corriente significa sencillamente agua CORRIENTE, así que lo está oyendo bien en su sentido ordinario, exactamente como él—. &#9888; Y aquí Juan marca el malentendido con el vocabulario: el narrador y Jesús dicen <em>p&#275;g&#275;</em>, FUENTE, y la mujer dice <em>phrear</em>, POZO excavado; dos palabras para el mismo agujero, repartidas según quién habla. La RV 1909 conserva la distinción con exactitud (fuente/pozo) y la TNM moderna la pierde. Luego los cinco maridos, donde el texto nunca la llama pecadora y Jesús no la reprende; el templo samaritano demolido del Guerizim detrás de «este monte»; y <em>pneuma ho theos</em> en el v24, la misma construcción sin artículo que Juan 1:1. &#9888; El primer <em>eg&#333; eimi</em> del libro se dice a una samaritana sola al mediodía; los discípulos se asombran no de que sea samaritana sino de que sea MUJER, y Juan cita las dos preguntas que nadie hizo. Ella deja su cántaro y el pueblo entero sale —y luego le dice que ya no cree por lo que ella contó, y lo llama <em>Salvador del mundo</em>, que era un título del César.",
    "jhn14": "\u00abEn la casa de mi Padre hay muchas moradas\u00bb \u2014 y aqu\u00ed el castellano lleva cuatro siglos de ventaja sobre el ingl\u00e9s, que puso \u00abmansiones\u00bb. MONE sale dos veces en todo el Nuevo Testamento y las dos en este cap\u00edtulo. \u26a0 Tres puntos donde los manuscritos se dividen de verdad: el v. 7 es un reproche en un texto y una promesa en otro; el v. 14 lleva o no lleva la palabra \u00abme\u00bb, que lo convertir\u00eda en el \u00fanico lugar de Juan donde se ora a Jes\u00fas; y una palabra peque\u00f1a decide si el v. 2 es una pregunta. M\u00e1s la divisi\u00f3n m\u00e1s ancha de la estanter\u00eda \u2014Consolador, Ayudante, Abogado, Par\u00e1clito\u2014 y por qu\u00e9 1 Juan 2:1 la resuelve.",
    "jhn15": "La vid, los sarmientos y \u00abpermaneced en m\u00ed\u00bb: MENO once veces en cinco vers\u00edculos, la palabra que el cap\u00edtulo anterior estuvo plantando sin mandarla nunca. \u26a0 Los vv. 2 y 3 llevan un juego de tres palabras \u2014airei, kathairei, katharoi\u2014 y aqu\u00ed el castellano gana: la RV conserva \u00ablimpiar\u00e1\u00bb y \u00ablimpios\u00bb donde el ingl\u00e9s lo pierde. El que trabaja la vid lleva la palabra que los sin\u00f3pticos dan a los labradores que matan al hijo. A unos esclavos se los asciende a amigos por haberles contado cosas. Y el v. 26 es la frase por la que se separaron Oriente y Occidente en 1054.",
    "zechariah1": "El profeta que abrió la era de lo apocalíptico. Contemporáneo exacto de Hageo en los escombros del 520 a.C., Zacarías responde al mismo desaliento no con la orden llana de un constructor sino con OCHO VISIONES NOCTURNAS. El capítulo 1 da la primera: un jinete sobre un caballo rojo parado entre los mirtos en una hondonada sombreada, una patrulla divina que ha recorrido la tierra e informa —inquietante— que «toda la tierra está en reposo» mientras Sion sigue de luto; y «el ángel que hablaba conmigo» (el ángel intérprete sobre el que se construye todo apocalipsis posterior) clama «¿hasta cuándo?». Dios responde con un celo POR Jerusalén, un cordel tendido sobre ella para reedificar, y consuelo renovado —todo enmarcado por la palabra más antigua de los profetas: «Volveos a mí, y yo me volveré a vosotros»—. ⚠ Zacarías es sacerdote además de profeta, y su genealogía («hijo de Berequías») guarda el enredado enigma de Mateo 23:35. ⚠ El capítulo 1 masorético tiene diecisiete versículos; la visión de los cuatro cuernos que el inglés imprime como 1:18-21 es hebreo 2:1-4. Con este capítulo, cada uno de los Doce tiene ya un primer capítulo en el sitio.",
    "haggai1": "El libro que logró que la obra se HICIERA. Dieciocho años después de que los desterrados volvieran de Babilonia, el cimiento del templo seguía intacto y el pueblo se decía «no ha llegado el tiempo». En cuatro oráculos fechados al mismo DÍA —el libro más preciso en el tiempo de todo el Antiguo Testamento—, el profeta Hageo los avergüenza por techar sus propias casas artesonadas mientras la casa de Dios está en ruinas, nombra la extraña futilidad que se fuga del «yo primero, Dios después» (ganas el jornal «en saco roto»), y convierte un juego sobre tres consonantes en todo el punto: porque dejasteis mi casa charev, «en ruinas», llamó una chorev, una sequía, sobre vuestros campos. Entonces ocurre lo más raro en todos los profetas —el pueblo OBEDECE, y comienza la obra veintitrés días después—. Lo que los mueve no es una amenaza sino cuatro palabras del «mensajero de Jehová»: «yo estoy con vosotros». ⚠ Dirigido al príncipe Zorobabel (heredero davídico, el futuro anillo de sellar) y al sacerdote Josué, y fechado por un emperador PERSA —porque ya no hay rey en Jerusalén—.",
    "zephaniah1": "El «día de Jehová» más oscuro de los Doce —y abre con la frase más aterradora de los profetas: «arrasaré por completo todo de sobre la faz de la tierra», Génesis 1 al REVÉS (el hombre, las bestias, las aves y los peces barridos de la tierra que recibieron en el sexto día)—. Luego el lente se estrecha a una ciudad: Dios corta el remanente de Baal, los sacerdotes idólatras, los que adoran los astros en las azoteas y —su verdadero blanco— los que apuestan a dos paños, que se postran «jurando por Jehová Y jurando por Milcom». Prepara un sacrificio donde Judá es la carne y los invasores son los invitados, registra Jerusalén con lámparas buscando a los cómodos que dicen «Jehová no hará bien ni hará mal», y se alza al Día de la Ira cuya Vulgata latina («dies irae, dies illa») se volvió el himno fúnebre más famoso de Occidente. ⚠ Y sin embargo el nombre del profeta significa «Jehová ha ESCONDIDO», y el libro gira (2:3) sobre «quizá seáis escondidos» y termina con Dios «regocijándose por ti con cantos». Un profeta de sangre real: su encabezado lo traza cuatro generaciones atrás hasta el rey Ezequías —la genealogía más larga de los profetas—.",
    "habakkuk1": "El profeta que DISCUTE. Único entre los Doce, el libro de Habacuc no es un mensaje de Dios al pueblo sino un DIÁLOGO con Dios —una disputa en dos rondas sobre la pregunta dura más antigua que existe—. Primera queja: ¿hasta cuándo, Jehová, tolerarás la violencia que pudre a Judá, la ley entumecida, los tribunales torcidos? La respuesta de Dios es la conmoción sobre la que gira todo el libro —«yo levanto a los CALDEOS», la máquina de guerra babilonia (caballos más veloces que leopardos, que «se ríen de toda fortaleza» y cuya «propia fuerza es su dios»)—, el remedio peor que la enfermedad. Lo que dispara la segunda queja, más dura, el problema de la teodicea planteado con tanta limpieza como jamás: «eres de ojos demasiado puros para mirar el mal… ¿por qué, pues, miras a los traidores, y callas mientras el impío devora al que es más justo que él?». El capítulo termina con la pregunta colgando en el aire y el profeta subiendo a su atalaya a esperar —y la respuesta, en el capítulo 2, será el versículo que más cita el Nuevo Testamento: «el justo vivirá por su fe». ⚠ Un comentario de este mismo libro estuvo entre los primeros Rollos del Mar Muerto hallados en 1947.",
    "nahum1": "El gemelo oscuro de Jonás: la misma ciudad, Nínive, siglo y medio después —y esta vez sin misericordia—. Donde la Nínive de Jonás se arrepintió y fue perdonada, la de Nahúm ha vuelto a ser la máquina de matar más eficiente del mundo antiguo, y Dios anuncia su fin. El libro no abre con la ciudad sino con un HIMNO de ira construido como un acróstico alfabético que se corta a la mitad —un alfabeto de juicio dejado sin terminar— y cita la famosa fórmula de Éxodo 34 inclinada hacia la JUSTICIA: «lento para la ira y grande en poder, y de ningún modo dará por inocente al culpable». Y sin embargo, en el centro exacto está el único versículo de misericordia («Bueno es Jehová, fortaleza en el día de la angustia») que hace que todo el libro de perdición merezca su nombre —Nahúm significa CONSUELO, porque la caída del destructor es la buena noticia para todos los que aplastó—. ⚠ Y el famoso versículo de «los pies del que trae buenas noticias» NO está aquí: es Nahúm 2:1 hebreo (las Biblias castellanas lo renumeran 1:15); este sitio sigue el conteo masorético.",
    "micah1": "El primo campesino de Isaías: un profeta de la Sefela que predicó desde abajo de la sociedad el mismo mensaje del siglo VIII que Isaías predicó desde arriba. El capítulo se abre como un tribunal (cielo y tierra convocados como testigos) y luego una gran teofanía: Dios DESCIENDE y los montes se DERRITEN bajo él como cera ante el fuego. Y el crimen resulta ser las dos ciudades capitales: «¿Cuál es la rebelión de Jacob? ¿No es SAMARIA? ¿Y cuáles son las alturas de Judá? ¿No es JERUSALÉN?». Luego el pasaje más intraducible de los profetas: Miqueas llora su comarca pueblo por pueblo, convirtiendo el NOMBRE de cada aldea en un juego sobre su SUERTE mientras la invasión asiria pasa por ellas —Casa-del-Polvo revolcándose en polvo, Ciudad-Hermosa desnuda, la Salida que no puede salir, y su propia Moréset entregada como una novia—. ⚠ Miqueas es el único profeta escritor que la Biblia hebrea cita POR SU NOMBRE (Jeremías 26:18), y su libro da al Nuevo Testamento Belén (5:2) y «hacer justicia, amar misericordia, andar humildemente» (6:8).",
    "jonah1": "El raro de los Doce: no un libro de oráculos sino una HISTORIA, y el único libro profético cuyo profeta DESOBEDECE. Mandado al este a clamar contra Nínive —la gran capital enemiga, el futuro verdugo de Israel—, Jonás huye al oeste, hasta el extremo del mar, y se embarca en Jope «lejos de la presencia de Jehová». Dios arroja una tormenta; los marineros paganos oran, echan suertes y le ruegan misericordia al Dios de Jonás mientras Jonás duerme en la bodega, y cuando por fin lo arrojan al mar (primero remando con fuerza para salvarlo —son más misericordiosos que el profeta—), acaban temiendo a Jehová y ofreciéndole sacrificio. El capítulo se traza con una palabra —ABAJO: abajo a Jope, abajo al barco, abajo a la bodega— y se construye sobre una ironía: «temo a Jehová, que hizo el mar y la tierra seca», dice el hombre que huye por el mar. ⚠ Y el famoso pez NO está aquí: es el 2:1 hebreo, que las Biblias castellanas renumeran 1:17; este sitio sigue el conteo masorético, y es un «gran pez», no una ballena.",
    "obad1": "El libro MÁS CORTO del Antiguo Testamento —veintiún versículos, un capítulo— y cada palabra apunta a un solo blanco: EDOM, la nación descendiente de Esaú, condenada por quedarse mirando (y celebrar, y saquear) mientras Babilonia arrasaba Jerusalén. Sus primeros nueve versículos corren casi palabra por palabra con Jeremías 49. La acusación es una sola palabra —«la VIOLENCIA hecha a tu HERMANO Jacob»— porque el crimen de Edom no es que atacara sino que MIRÓ, y al mirar se unió; se cuenta en ocho órdenes, cada una clavada en «el día» de la caída de Jerusalén, con la palabra «día» resonando diez veces en cuatro versículos. Luego el gozne del libro entero: «como hiciste, se te hará». Y termina devolviendo el mapa disputado a su dueño —«y el reino será de Jehová»— pasando de camino por SEFARAD, un lugar desconocido cuya confusión se volvió el nombre del judaísmo español.",
    "amos1": "Un criador de ovejas de una aldea de Judá se planta en el reino del norte, en su momento más rico, y empieza condenando a todos los demás — Damasco, Gaza, Tiro, Edom, Amón — cinco naciones sentenciadas con una fórmula que sonará OCHO veces, y cuya octava apunta a los que llevan toda la lista asintiendo. Ninguna acusación es de idolatría: todas son atrocidades contra seres humanos —trillar una región con trillos de hierro, vender poblaciones enteras, olvidar un pacto de hermanos, cazar al propio gemelo y «arruinar sus entrañas de compasión» (palabra construida sobre el hebreo de ÚTERO)— y, la única con motivo declarado, abrir en canal a las mujeres encintas de Galaad para ensanchar una frontera. ⚠ Y el libro se fecha dos veces: por dos reyes, y por un terremoto — «dos años antes DEL terremoto», con artículo, porque sus lectores sabían cuál.",
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
    "mark2": "Cinco choques en un solo capítulo, y el primer indicio de que esto va a acabar mal. ⚠ Cuatro hombres desmontan un techo —Marcos usa dos verbos, destechar y EXCAVAR, que es exactamente como se abre un techo galileo de barro y ramaje, mientras que Lucas, al contarlo, los hace bajar por TEJAS—. Al hombre lo bajan en un <em>krabattos</em>, un jergón de paja, palabra baja que Mateo y Lucas sustituyen por una cama en regla; esta traducción conserva la estera. Luego una frase que se parte por la mitad y se deja partida. ⚠ Un recaudador es llamado desde su garita y Marcos lo llama LEVÍ hijo de Alfeo, donde el Evangelio de Mateo lo llama Mateo —con la segunda mitad del enigma dicha: la lista de los Doce de Marcos no tiene ningún Leví—. Un novio que será ARREBATADO, tres palabras, la primera sombra del libro. Y luego ⚠ «en tiempos de Abiatar el sumo sacerdote» —donde 1 Samuel dice que el sacerdote era AJIMÉLEC y Abiatar es su hijo—, expuesto en vez de remendado. El capítulo acaba en la frase que ningún otro Evangelio conservó: el sábado vino a ser por causa del ser humano, y no al revés.",
    "mark4": "La barca que quedó lista en 3:9 por fin se usa: Jesús enseña desde el agua a toda una multitud en la orilla, empezando por un sembrador cuya semilla cae en cuatro tipos de tierra indistinguibles entre sí hasta que llega la cosecha. Luego los discípulos preguntan por qué habla en parábolas, y reciben la frase más difícil del capítulo &mdash; las parábolas se dan PARA QUE los de afuera vean y no perciban, oigan y no entiendan, «no sea que se conviertan y les sea perdonado». &#9888; La versión de Mateo del mismo momento cita a Isaías como profecía cumplida, enmarcada con PORQUE; el Jesús de Marcos lo declara como su propio propósito, sin ninguna cita &mdash; una diferencia real entre los dos Evangelios, no una decisión de traductor. Siguen una lámpara y una medida, dos dichos que reaparecen en escenarios completamente distintos dentro del Sermón del Monte de Mateo. Luego una parábola que solo tiene Marcos: un agricultor esparce semilla y la tierra da fruto AUTOMÁTICAMENTE, sin que él sepa cómo &mdash; y un grano de mostaza, proverbialmente la semilla más pequeña que sembraría un agricultor galileo, se convierte en la mayor de las hortalizas. El capítulo termina en un lago: una tempestad llena la barca, Jesús duerme durante ella, y al despertar REPRENDE al viento y ordena al mar, «Enmudece» &mdash; la misma orden, el mismo verbo, que ya le dio a un espíritu inmundo en 1:25. El propio miedo e incredulidad de los discípulos cierran el capítulo, todavía preguntando lo que nunca se responde: ¿quién es este?",
    "mark3": "El plan para matarlo se forma a los seis versículos, por una coalición que no debería existir. ⚠ Jesús los mira en derredor CON IRA —y a diferencia de la ira discutida de 1:41, esta está textualmente asegurada, que es la mejor corroboración que podía recibir la lectura difícil del capítulo 1—. Mateo suprime la mirada y la emoción; Lucas conserva el mirar en derredor, le quita el sentimiento y cuatro palabras después entrega la furia a los ADVERSARIOS. Luego los Doce son HECHOS —el verbo llano, sin suavizar— y entre ellos dos hombres reciben un apodo que nadie vuelve a usar jamás. ⚠ Y después los dos versículos que ni Mateo ni Lucas tienen en forma alguna: su propia familia viene a PRENDERLO, diciendo que está fuera de sí. Marcos envuelve la acusación de Beelzebul dentro de esa escena —la primera muestra clara del emparedado con que construye todo este Evangelio— de modo que el veredicto de la familia y el de los escribas se lean el uno a través del otro. ⚠ La sentencia imperdonable gira sobre un sustantivo en disputa: un PECADO eterno, condición que no cesa, frente al JUICIO eterno del texto tardío, de donde sale la «condenación». Y el capítulo acaba con su madre fuera de un círculo y la palabra dada a quien esté sentado dentro.",
    "luke1": "El cap\u00edtulo m\u00e1s largo de los Evangelios: dos anunciaciones \u2014un sacerdote enmudecido por dudar, una joven bendecida por creer\u2014 y dos c\u00e1nticos, el Magn\u00edficat y el Benedictus.",
    "luke2": "\u26a0 En este cap\u00edtulo no hay ning\u00fan mes\u00f3n, y Lucas s\u00ed tiene palabra para mes\u00f3n: la usa ocho cap\u00edtulos despu\u00e9s, en el buen samaritano. La de aqu\u00ed es KATALYMA, aposento de hu\u00e9spedes, que es como Lucas llama al aposento alto de la \u00faltima cena. Tampoco hay posadero: llega con los autos medievales. \u26a0 Una sigma final decide lo que cantaron los \u00e1ngeles, y aqu\u00ed RV y NVI se separan. El c\u00e1ntico de Sime\u00f3n es vocabulario de manumisi\u00f3n, su espada es la larga que el Apocalipsis usa seis veces, y Ana pertenece a una tribu desaparecida hac\u00eda setecientos a\u00f1os.",
    "3john1": "El documento más privado de la Biblia: \u00abel anciano\u00bb a Gayo, y contra Di\u00f3trefes, \u00abque ama ser el primero\u00bb.",
    "jude1": "La carta breve más feroz del NT: un hermano de Jesús que se llama solo «esclavo», luchando por «la fe una vez dada» — y que cita a Enoc, un libro que no está en la Biblia.",
    "2john1": "El libro más corto de la Biblia: \u00abel anciano\u00bb a \u00abuna se\u00f1ora elegida\u00bb — verdad y amor, y una puerta que no se abre.",
    "judg1": "La conquista contada por debajo: empieza bien, y luego, tribu por tribu, la misma frase suena siete veces — no expuls\u00f3.",
    "ruth1": "La contrahistoria serena de los Jueces: hambre, huida a Moab, tres muertes — y una nuera moabita que no se aparta con el gran juramento: «tu pueblo mi pueblo, tu Dios mi Dios».",
    "1sam1": "El libro que da reyes a Israel abre sobre una mujer estéril: Ana ora en silencio en Silo, el sacerdote Elí la toma por ebria, y cuando nace Samuel lo entrega —«prestado a Jehová» de por vida. El primer «Jehová de los ejércitos» de la Biblia, y la semilla del cántico que será el Magníficat.",
    "josh1": "\u00abMois\u00e9s ha muerto\u00bb — y ahora, cruza el Jord\u00e1n. Tres veces: s\u00e9 fuerte y resuelto; y el valor es para el rollo, no la espada.",
    "josh6": "Jericó cae sin una sola batalla: siete días marchando en silencio detrás del arca y siete trompetas de cuerno de carnero, y al séptimo día, un grito. Los muros caen, y una sola casa se salva por nombre — Rahab, cuyo cordón escarlata sigue en la ventana.",
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
    "jer18": 'La casa del alfarero: enviado a un taller en el borde de la ciudad, Jeremías ve una vasija estropearse bajo la mano y ser rehecha, y oye la frase más CONDICIONAL de los profetas: «si esa nación se vuelve de su mal… me arrepiento del mal que pensaba hacerle». La respuesta del barro es una sola palabra llana —«Sin esperanza»—, rechazando una oferta que seguía abierta. Entonces el propio verbo del alfarero se vuelve contra ellos («estoy FORMANDO el mal contra vosotros»), el cuarto «designio» del capítulo apunta al profeta mismo, y todo termina en una oración imprecatoria que esta biblioteca no va a suavizar. ⚠ Dos pasajes genuinamente disputados quedan en pie con sus pedigríes y sin voto: la «roca del campo» del versículo 14 y «la espalda y no el rostro» del versículo 17.',
    "jer1": "El llamado de Jeremías: un muchacho que dice «solo soy un joven», conocido antes del vientre, hecho «profeta a las naciones» — con los seis verbos (arrancar, derribar… edificar y plantar), la rama de almendro y la olla hirviente del norte.",
    "jer2": "El verdadero argumento de apertura del libro, justo después del llamado: Jehová recuerda el amor leal de los años de desposorio y desierto de Israel antes de nombrar un solo cargo — y luego hace una pregunta que el capítulo nunca deja que nadie responda: «¿qué falta hallaron en mí vuestros padres?». La imagen central es un fallo de plomería jugado casi como comedia negra: abandonar una fuente de agua viva que se renueva sola para cavar a mano cisternas que resultan agrietadas. ⚠ Un ketiv/qere real cae en la línea más cargada del capítulo — el texto hebreo ESCRIBE «no serviré» justo después de «rompí tu yugo», pero la tradición LEE un verbo no emparentado, «no transgrediré»; esta traducción sigue el ketiv y la mayoría del estante. El mismo lenguaje de romper el yugo reaparece, casi literal, en el ya publicado Jeremías 30:8 — una liberación ya cumplida aquí, una segunda todavía prometida allí. Camella, asna montés, ladrón y un padre hecho de madera: cinco imágenes seguidas, cada una atrapando la misma infidelidad desde un ángulo distinto, cada vez más indigno.",
    "jer23": '¡Ay de los pastores! — y luego la promesa contra ellos: un RENUEVO justo levantado para David, cuyo nombre corrige el del rey que entonces reinaba («Jehová es nuestra justicia»). Después el capítulo se vuelve contra el propio oficio de Jeremías y no para en veintiocho versículos: profetas que llenan de vapor a quien los oye, que predican paz a los que desprecian a Dios, que se roban los oráculos unos a otros y se quedan con el sello de goma —«declaración de Jehová»— tras soltar el nombre. La prueba es una sola pregunta, «¿quién ha estado en el CONSEJO de Jehová?», y un resultado verificable: si hubieran estado dentro, habrían hecho volver al pueblo. Paja contra grano, una palabra como fuego y como martillo que destroza la roca, un Dios de quien no hay dónde esconderse — y un juego de palabras de ocho versículos sobre la palabra CARGA que acaba confiscándola. ⚠ Dos pasajes genuinamente disputados quedan en pie con sus pedigríes y sin voto: el «¡qué carga!» del versículo 33 frente al «vosotros sois la carga» de las versiones antiguas, y el olvidar-o-levantar del versículo 39.',
    "jer29": 'La carta de Jerem\u00edas a los desterrados en Babilonia: edifiquen casas, planten huertos, busquen la SHALOM de la ciudad que los deport\u00f3 \u2014 «porque en SU paz tendr\u00e1n ustedes paz». Y luego el vers\u00edculo m\u00e1s citado de internet, le\u00eddo en plural y dentro de sus setenta a\u00f1os: shalom aparece cuatro veces en el cap\u00edtulo y TRES son la prosperidad de Babilonia. El espa\u00f1ol lo ve mejor que el ingl\u00e9s \u2014 «vosotros» en RV, «ustedes» en TNM \u2014 donde el «you» ingl\u00e9s esconde que la promesa nunca fue a una sola persona. \u26a0 En el mismo cap\u00edtulo hay dos profetas asados al fuego (vv. 21-23) y espada, hambre y peste para los que se quedaron (v. 17); la biblioteca los imprime juntos porque juntos est\u00e1n en la carta.',
    "jer31": "El centro del Libro de la Consolación: Jehová edifica de nuevo a la virgen de Israel, Raquel llora en Ramá por hijos que van a volver, se le pregunta a Efraín si es hijo precioso — y Jehová promete un PACTO NUEVO, la ley escrita en el corazón, el pecado no recordado más. La cita del Antiguo Testamento más larga de todo el Nuevo Testamento (Hebreos 8) empieza aquí.",
    "dan2": "El sueño de Nabucodonosor y una prueba imposible: la estatua de oro, plata, bronce y hierro con pies de barro, y la piedra cortada sin manos que la deshace y se hace montaña — los cuatro reinos y el quinto eterno; y el capítulo donde el libro pasa del hebreo al ARAMEO.",
    "dan3": "Nabucodonosor levanta una imagen enteramente de oro — su propia respuesta no declarada al sueño de un capítulo antes — y exige que toda la provincia se postre al sonido de la orquesta. Tres hombres se niegan: «nuestro Dios puede librarnos; y si no, no serviremos a tus dioses». El horno calentado siete veces más mata a quienes los arrojan y deja caminar libre dentro del fuego a una cuarta figura, «como hijo de los dioses». El rey que intentó ejecutarlos termina el capítulo bendiciendo a su Dios por su nombre.",
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
    "exod15": "El Cántico del Mar —una de las piezas de poesía más antiguas de la Biblia, y el primer lugar donde aparece el nombre divino corto YAH («mi fortaleza y mi cántico es Yah»), una línea que Isaías 12:2 y el Salmo 118:14 citan después palabra por palabra. Dieciocho versículos de puro poema de victoria: a Jehová se le llama VARÓN DE GUERRA sin rodeos, el mar se amontona al soplo de su nariz, y «quién como tú entre los dioses» se convierte en Mi Chamocha, una línea que sigue recitándose a diario en la oración matutina judía tres mil años después. Luego Miriam —la primera persona de la Biblia llamada profetisa— responde con un estribillo de dos líneas que algunos eruditos creen que es en realidad el cántico más antiguo y original, antes de que el relato retome a pie: tres días secos, agua amarga en Mara endulzada por un árbol, y «yo soy Jehová tu sanador», la primera vez que Dios reclama el título como nombre propio.",
    "exod16": "Seis semanas fuera de Egipto, el pueblo murmura por las ollas de carne que dej\u00f3 atr\u00e1s \u2014 un verbo hebreo que cae nueve veces en once vers\u00edculos, la repetici\u00f3n m\u00e1s densa del libro hasta ahora. La respuesta son codornices, y una escama sobre el suelo tan extra\u00f1a que todos hacen la misma pregunta, MAN HU, \u00ab\u00bfqu\u00e9 es esto?\u00bb \u2014 y esa misma pregunta se convierte en el nombre de la sustancia tres vers\u00edculos antes de que el nombre se declare de verdad. No se puede acumular (lo que sobra se pudre de un d\u00eda para otro) ni recogerse de forma injusta (a quien recoge mucho no le sobra, a quien recoge poco no le falta) \u2014 salvo el sexto d\u00eda, cuando una raci\u00f3n doble sobrevive limpia a la noche, porque el s\u00e9ptimo d\u00eda es S\u00c1BADO, pronunciado aqu\u00ed como sustantivo por primera vez en la Biblia, cuatro cap\u00edtulos antes de que los Diez Mandamientos lo legislen. Una vasija de ello se aparta delante del Testimonio, guardada cuarenta a\u00f1os para que jam\u00e1s pudiera comerse.",
    "exod19": "Israel llega al Sinaí, y todo en este capítulo sucede antes de que se dé un solo mandamiento. La oferta de Jehová se apoya en lo que ya ha ocurrido —«vosotros habéis visto lo que hice a los egipcios, y cómo os llevé sobre alas de águilas»— y es una propuesta, todavía no una ley: guardad el pacto, y sed mi «posesión atesorada» entre todos los pueblos, un «reino de sacerdotes y una nación santa». El pueblo acepta antes de conocer las condiciones. Luego tres días de preparación —lavad vuestros vestidos, no os acerquéis a mujer, límites señalados alrededor del monte con pena de muerte por tocarlo, ejecutada a distancia para que quien cumple la sentencia no tenga que cruzar la misma línea—. ⚠ Y entonces el monte mismo responde: truenos, relámpagos, una nube espesa, un sonido de cuerno que crece sin trompetista humano, humo como de un horno, todo el monte temblando. Moisés sube y baja tres veces distintas en este único capítulo, cada viaje volviendo a la misma advertencia —contened al pueblo, santificad a los sacerdotes, que nadie traspase el límite para mirar—. El peligro nombrado no es la desobediencia. Es la curiosidad.",
    "exod18": "Jetro le devuelve a Mois\u00e9s a su esposa y sus dos hijos \u2014 Gers\u00f3n, nombrado al nacer (\u00abforastero all\u00ed\u00bb), y un hermano nombrado por primera vez en toda la Biblia, d\u00e9cadas despu\u00e9s del hecho: Eliezer, \u00abel Dios de mi padre me ayud\u00f3\u00bb. Jetro escucha toda la historia y llega a su propio veredicto: \u00abahora conozco que Jehov\u00e1 es m\u00e1s grande que todos los dioses\u00bb \u2014 una afirmaci\u00f3n comparativa de un sacerdote madianita, alcanzada por argumento y no por decreto. \u26a0 Luego toma \u00e9l mismo la ofrenda y preside una comida sacrificial a la que Aar\u00f3n y los ancianos de Israel simplemente asisten \u2014 antes de que Aar\u00f3n tenga sacerdocio alguno. Al d\u00eda siguiente ve a Mois\u00e9s juzgar a toda la naci\u00f3n solo, de la ma\u00f1ana a la tarde, y dice lo que nadie m\u00e1s hab\u00eda dicho: \u00abno est\u00e1 bien lo que haces... desfallecer\u00e1s del todo\u00bb. La soluci\u00f3n es la primera lecci\u00f3n de gesti\u00f3n de la Biblia \u2014 hombres capaces, temerosos de Dios, que amen la verdad y aborrezcan la avaricia, puestos como jefes de millares, centenas, cincuenta y diez, de modo que solo los casos dif\u00edciles lleguen jam\u00e1s a Mois\u00e9s. \u26a0 Y un enigma en el calendario: el lenguaje de este mismo cap\u00edtulo ya tiene a Mois\u00e9s dando a conocer \u00ablas ordenanzas de Dios y sus leyes\u00bb \u2014 antes de que el Sina\u00ed, a un cap\u00edtulo de distancia, las entregue siquiera.",
    "exod17": "Sin agua en Refidim, y el pueblo que acaba de comer man\u00e1 recurre al mismo verbo de murmuraci\u00f3n que us\u00f3 el cap\u00edtulo anterior. Mois\u00e9s golpea la pe\u00f1a en Horeb con la misma vara que un d\u00eda convirti\u00f3 el Nilo en sangre, y llama al lugar MASAH y MERIBA \u2014 prueba y rencilla, un solo suceso nombrado dos veces en dos ra\u00edces distintas. Luego ataca Amalec, y a un hombre sin presentaci\u00f3n alguna se le entrega un ej\u00e9rcito: la primera aparici\u00f3n de Josu\u00e9 en toda la Biblia, mientras las manos alzadas de Mois\u00e9s \u2014 sostenidas por Aar\u00f3n y Hur cuando pesan demasiado para seguir solas \u2014 deciden una batalla de la que nunca se describe ninguna t\u00e1ctica. Termina con la l\u00ednea m\u00e1s dif\u00edcil del cap\u00edtulo: una palabra que aparece exactamente una vez en toda la Biblia hebrea, traducida aqu\u00ed \u00abuna mano sobre el trono de Jah\u00bb, que el propio estante no logra resolver de la misma manera.",
    "exod20": "Los Diez Mandamientos \u2014 y el cap\u00edtulo que muestra por qu\u00e9 DIEZ es una decisi\u00f3n y no una lectura. El hebreo tiene 22 vers\u00edculos donde las Biblias castellanas imprimen 26, cuatro mandamientos caben en un solo vers\u00edculo (separados no por n\u00fameros sino por las marcas de p\u00e1rrafo de los escribas), y el mismo texto se cuenta de tres maneras distintas en las tradiciones jud\u00eda, cat\u00f3lico-luterana y reformada. \u26a0 El sexto es lo tirtzaj, y RATZACH es el verbo que N\u00fameros 35 usa del homicida que huye a una ciudad de refugio, no harag, la palabra corriente para matar. El tercero no trata de jurar sino de LEVANTAR el Nombre en vano. Y termina con el pueblo a lo lejos mientras Mois\u00e9s entra en la densa oscuridad donde estaba Dios.",
    "exod21": "Los Diez Mandamientos eran ley apod\u00edctica \u2014 desnuda, incondicional. Este cap\u00edtulo abre los Mishpatim, el derecho de casos que los desarrolla: \u00absi\u2026 entonces\u00bb, el mismo g\u00e9nero que el C\u00f3digo de Hammurabi, siglos m\u00e1s antiguo. Un siervo hebreo sirve seis a\u00f1os y sale libre \u2014 un techo firme que esta ley no establece para un esclavo de origen extranjero. \u26a0 La l\u00ednea m\u00e1s famosa del cap\u00edtulo, \u00abojo por ojo, diente por diente\u00bb, se sit\u00faa dentro de un caso espec\u00edfico, y su funci\u00f3n all\u00ed es fijar un L\u00cdMITE a la venganza, no darle licencia \u2014 dos vers\u00edculos despu\u00e9s, da\u00f1ar el ojo de un siervo le cuesta al amo no su propio ojo, sino la libertad del siervo. Y un buey que mata por segunda vez tras una advertencia documentada le cuesta a su due\u00f1o la vida, a menos que se pague un rescate \u2014 casi la misma ley palabra por palabra que aparece en el C\u00f3digo de Hammurabi, siglos antes de la fecha convencional de este texto.",
    "exod22": "Este cap\u00edtulo no tiene vers\u00edculo 1 \u2014 las Biblias hebrea y en espa\u00f1ol dividen el cap\u00edtulo de forma distinta, y lo que los lectores conocen como \u00c9xodo 22:1 ya est\u00e1 en estas p\u00e1ginas como el \u00faltimo vers\u00edculo del cap\u00edtulo 21. \u26a0 Sigue el tramo m\u00e1s expuesto de los Mishpatim hasta ahora: un sistema de dep\u00f3sitos con una l\u00f3gica de reparto de riesgo genuinamente coherente (prestado, depositado, alquilado), la ley de seducci\u00f3n y dote, tres sentencias capitales disparadas en fila sin ninguna explicaci\u00f3n \u2014 incluido el vers\u00edculo cuya formulaci\u00f3n inglesa, \u00abno dejar\u00e1s con vida a una bruja\u00bb, aliment\u00f3 siglos de juicios de brujas \u2014 y la \u00fanica ley de todo el cap\u00edtulo que Dios hace cumplir \u00e9l mismo, sin ning\u00fan tribunal: maltratad a una viuda o hu\u00e9rfano, y \u00abciertamente oir\u00e9 su clamor\u00bb.",
    "exod23": "Los Mishpatim cierran con una \u00e9tica judicial que corta en las dos direcciones \u2014 no tuerzas la justicia contra el pobre, pero tampoco lo favorezcas \u2014 y luego ordenan algo que el resto del cap\u00edtulo nunca explica: ayuda al buey o al asno ca\u00eddo de tu ENEMIGO, antes de que aparezca siquiera la palabra \u00abpr\u00f3jimo\u00bb. \u26a0 La cl\u00e1usula del calendario tiene seis palabras en hebreo y se convirti\u00f3 en toda una rama del derecho jud\u00edo: \u00abno cocer\u00e1s un cabrito en la leche de su madre\u00bb \u2014 repetida dos veces m\u00e1s en otros lugares y le\u00edda por la tradici\u00f3n rab\u00ednica como la ra\u00edz de la separaci\u00f3n kosher entre carne y l\u00e1cteos. Y un \u00e1ngel es enviado por delante con una advertencia m\u00e1s extra\u00f1a que la de cualquier mensajero: no perdonar\u00e1 vuestra transgresi\u00f3n, \u00abporque mi nombre est\u00e1 en \u00e9l\u00bb \u2014 seguido de una conquista deliberadamente lenta para no terminar demasiado pronto, para que la tierra no quede vac\u00eda antes de que Israel pueda sostenerla.",
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
    "joel1": "Cuatro oleadas de langostas dejan a Judá en la madera —y Joel usa CUATRO palabras hebreas distintas para ellas, cuyas diferencias nadie ha establecido jamás: cuatro especies, cuatro estadios o cuatro nombres amontonados por peso—. Pero la pérdida no se mide en fanegas: se mide por lo que ha cesado en el templo. Sin harina y sin vino no puede hacerse la ofrenda diaria, así que la conversación permanente del país con Dios ha enmudecido, y por eso son los SACERDOTES, y no los labradores, quienes reciben la orden de dormir en saco. Después llega el día de Jehová en un juego de palabras intraducible (shod de SHADDAI), y un versículo con tres palabras que no aparecen en ningún otro lugar de la Biblia. Termina con el ganado, y con un verbo tomado del Salmo 42: también las bestias del campo JADEAN hacia ti, porque se secaron los cauces.",
    "hos1": "Dios le dice a un profeta que se case con una mujer promiscua, y luego que ponga a sus tres hijos los nombres de la sentencia sobre su país: JEZREEL, por una matanza; LO-RUHAMA, No-compadecida —y el hebreo construye su palabra para misericordia sobre la palabra MATRIZ, así que llamar a una recién nacida No-amada-de-madre es peor en hebreo que en castellano—; y LO-AMMÍ, No-mi-pueblo. El último desarma la fórmula del pacto, y va más lejos de lo que muestra ninguna Biblia castellana: el hebreo del v. 9 no tiene palabra alguna para «Dios». Lo que dice es «yo no seré EHYÉ para vosotros»: el nombre que Dios se dio a sí mismo en la zarza, retirado. Fíjese además en quién fecha este libro: cuatro reyes de JUDÁ, para un profeta que predicó solo al norte. Y en que tiene nueve versículos, no once.",
    "lam1": "Veintidós versículos, porque el alfabeto hebreo tiene veintidós letras y cada versículo empieza por la siguiente: el texto más férreamente controlado de la Biblia, sobre lo más incontrolable que le pasa a la gente. Jerusalén ha ardido, y la ciudad es una viuda sentada a solas: los caminos de Sion están de luto porque nadie los pisa, los sacerdotes y los ancianos mueren en la calle mientras buscan comida, y cinco veces distintas el poema dice lo mismo — NO TIENE CONSOLADOR. No que no haya rescate: que no hay nadie sentado con ella. A mitad de camino la ciudad interrumpe la descripción de sí misma y se apodera del poema, y concede que el veredicto fue justo. Babilonia quemó esta ciudad, y Babilonia no se nombra ni una vez en cinco capítulos: cada frase tiene a Dios por sujeto, que es justamente por lo que las quejas pueden dirigírsele a él.",
    "lam2": "El capítulo más feroz del libro, y el que dice sin rodeos lo que el capítulo 1 solo insinuaba: «el Señor vino a ser como enemigo». Entesa su arco contra su propia ciudad, derriba su propio templo como un contratista de demoliciones que tiende un cordel de medir, y borra el mismo calendario de fiestas que hacía posible el culto. La imagen sobre la que gira todo el capítulo es un grito de victoria alzado DENTRO de la casa de Jehová, como en día de fiesta señalada: el vocabulario de la celebración usado para el triunfo del propio enemigo. Los niños preguntan a sus madres «¿dónde está el trigo y el vino?» y desfallecen en las calles; al final, se le pregunta a Dios sin rodeos si de verdad las mujeres han llegado a comerse a sus propios hijos. Y por primera vez en este libro, dos letras del acróstico intercambian su lugar — la pe impresa antes que la áyin —, una pequeña irregularidad sin explicar en un poema construido, por lo demás, enteramente sobre el orden.",
    "lev19": "El corazón del Código de Santidad: «Santos seréis, porque santo soy yo, Jehová vuestro Dios» — desplegado en treinta y cinco versículos sobre bordes de campo dejados para el pobre, salarios pagados a tiempo, imparcialidad en los tribunales, no quedarse de brazos cruzados ante la sangre de un prójimo, y la línea más citada de la Torá, «amarás a tu prójimo como a ti mismo», repetida palabra por palabra dieciséis versículos después para el extranjero. Semillas mezcladas, telas mezcladas, las esquinas de una barba, tatuajes, balanzas honestas — lo ordinario y lo cósmico en una sola lista, cerrada quince veces con las mismas dos palabras: Yo Jehová.",
    "isa1": "Isaías no abre con un sermón sino con un PLEITO: se convoca al cielo y a la tierra como testigos —los mismos dos que convoca el pacto en Deuteronomio— y se lee el cargo. El buey sabe quién le da de comer; Israel no. Luego, el pasaje más duro de los profetas: Dios dice que está harto de los sacrificios QUE ÉL MISMO MANDÓ —«¿quién pidió esto de vuestra mano?»— porque las manos que se alzan en oración están llenas de sangre, y los tribunales no oyen a un huérfano. El v. 8 se puede fechar: Jerusalén queda «como enramada en viña», y eso es el 701 a.C.; el prisma de Senaquerib dice que encerró allí a Ezequías «como pájaro en jaula». Y después el versículo más citado del libro —aunque vuestros pecados sean como la grana— que en hebreo quizá no sea una promesa, sino la pregunta de un fiscal. El tinte, por cierto, era un gusano, y era famoso porque no se iba al lavar.",
    "isa40": "La costura del libro — el capítulo 40 es donde el horizonte cambia a un exilio ya cumplido, y consuelo se vuelve la palabra de los siguientes veintisiete capítulos. «Consolad, consolad a mi pueblo» abre paso a una voz que clama en el desierto (los cuatro evangelios la citan para Juan el Bautista), «toda carne es hierba» (1 Pedro 1:24), un pastor que recoge los corderos en su brazo, y un argumento cósmico —quién midió las aguas con su mano, quién enseñó al espíritu de Jehová (Pablo lo cita dos veces)— que termina en la línea más querida del capítulo: los que esperan a Jehová tendrán nuevas fuerzas, levantarán alas como las águilas.",
    "isa53": "El siervo sufriente \u2014 el pasaje m\u00e1s discutido de la Biblia hebrea, y la discusi\u00f3n es textual, no s\u00f3lo teol\u00f3gica. \u26a0 Que el siervo sea ISRAEL (Isa\u00edas 49:3 lo dice por su nombre) o un INDIVIDUO (53:8 lo pone frente a \u00abmi pueblo\u00bb) queda en pie con los dos casos expuestos enteros y sin voto. Dos plurales que casi toda Biblia vuelve singulares: lamo en el v. 8 es normalmente \u00aba ELLOS\u00bb, y be-motav en el v. 9 es \u00absus MUERTES\u00bb. \u26a0 Y en el v. 11 el Gran Rollo de Isa\u00edas de Qumr\u00e1n, mil a\u00f1os m\u00e1s antiguo que nuestros manuscritos masor\u00e9ticos m\u00e1s viejos, lee \u00ab\u00e9l ver\u00e1 LUZ\u00bb donde el texto masor\u00e9tico no tiene objeto alguno. Un solo verbo, paga (encontrarse), enmarca el poema: nuestra iniquidad se hace encontrar con \u00e9l en el v. 6, y \u00e9l intercede en el v. 12.",
    "sos1": "El título es un superlativo hebreo —un sustantivo que rige su propio plural, como «santo de los santos»—, así que significa EL MEJOR CANTAR QUE HAY; y «el cual es de Salomón» es una sola letra prefijada que puede significar igualmente por él, para él, acerca de él o a su estilo. Entonces, sin narrador y sin presentación, una mujer empieza en pleno deseo: «¡Que me bese con los besos de su boca!». Ella dirá la mayor parte de este libro, lo abrirá y lo cerrará. Dice que es negra Y hermosa —el hebreo trae la conjunción corriente, y el «pero» de Jerónimo ha modelado el versículo desde entonces— y lo explica ella misma: quemadura de sol, por haber sido puesta a guardar las viñas de sus hermanos. Él la compara con una yegua entre los carros de Faraón, lo cual no va de tamaño: los carros egipcios los tiraban sementales, y una yegua deshace la formación. Termina con dos amantes tumbados en la hierba bajo cedros, llamándolo su casa.",
    "qoh1": "El libro más escéptico de la Biblia se abre con una palabra que casi todas las versiones han traducido como un veredicto cuando el hebreo da una imagen: HEVEL, vapor — un aliento, el vaho que se ve y no se puede retener. «Vanidad» y «absurdo» deciden algo que el hebreo deja abierto. Luego un poema en el que el sol JADEA de vuelta a su punto de partida, el viento gira y regresa, los ríos corren a un mar que nunca se llena y las generaciones pasan mientras la tierra permanece — cuatro sistemas en movimiento perpetuo, ninguno llegando a nada. «No hay nada nuevo debajo del sol». El que habla se llama Qohélet, que no es un nombre sino un oficio — «el que convoca» — y dice «FUI rey», un pasado que no encaja con Salomón y que originó una leyenda rabínica sobre un rey destronado que anduvo mendigando. Cierra el capítulo con la factura: en mucha sabiduría hay mucha vejación, y quien añade conocimiento añade dolor.",
    "qoh3": "Tiempo de nacer y tiempo de morir \u2014 catorce pares de opuestos, dos por vers\u00edculo, con la palabra ET encabezando veintiocho cl\u00e1usulas, y sin un solo veredicto en la lista: matar est\u00e1 en ella tan llanamente como sanar. \u26a0 En el v. 11 las consonantes de ha-OLAM dan ETERNIDAD (TNM), EL MUNDO (RV, KJV) o, repuntuadas, OCULTAMIENTO \u2014 que nadie imprime y que es la \u00fanica lectura que hace concordar el vers\u00edculo con su propia segunda mitad. \u26a0 Y en el v. 21 el texto masor\u00e9tico punt\u00faa dos participios con el ART\u00cdCULO DEFINIDO (la se\u00f1al es el dagesh en la yod); repuntuados, preguntan \u00ab\u00bfsube? \u00bfbaja?\u00bb. La KJV inglesa es la que sigui\u00f3 las vocales, y RV se escuda en el subjuntivo. \u26a0 Y una inconsistencia dentro de RV: traduce el mismo ruach como \u00abrespiraci\u00f3n\u00bb en el v. 19 y \u00abesp\u00edritu\u00bb en el v. 21. La ventaja del hombre sobre la bestia es NADA (v. 19).",
    "est1": "El único libro de la Biblia que nunca menciona a Dios abre con ciento ochenta días de un rey enseñando su dinero. Asuero es JERJES, y el año es el 483 a.C. — el mismo en que Heródoto lo tiene reuniendo a sus nobles para planear la invasión de Grecia, una guerra que este libro no menciona jamás y cuya duración es exactamente el hueco entre los capítulos 1 y 2. Entonces, el séptimo día del segundo banquete, bebido, manda traer a su mujer para exhibirla junto con el mobiliario, y ella se niega — y el hebreo no da razón alguna. Lo que sigue es una comedia a costa de unos funcionarios asustados: todo el aparato jurídico de un imperio convocado por un desaire de sobremesa, y un decreto llevado por el correo imperial a ciento veintisiete provincias anunciando que los hombres manden en casa.",
    "mat15": "Una pregunta dura sobre el lavado de manos se convierte en una lección sobre lo que en verdad contamina — citando el «este pueblo me honra con los labios» de Isaías y llamando a los fariseos «guías ciegos de ciegos». ⚠ Luego una mujer cananea cruza al único territorio gentil que los Evangelios registran que Jesús pisó en persona, y discute con él y sale mejor parada: «hasta los perritos comen de las migajas que caen de la mesa de sus amos» — el propio superlativo del Evangelio, «grande es tu fe», dado a la extraña que más ha marcado como tal. Una multitud junto al mar glorifica «al Dios de Israel»; luego pan y peces multiplicados una segunda vez para cuatro mil más, siete cestas sobrantes esta vez, no doce — el vocabulario mismo sigue registrando a quién se alimenta.",
    "mat16": "Los fariseos y los saduceos piden juntos una señal, tal como se prometió hace tres capítulos, y reciben la misma respuesta ya dada una vez. ⚠ Luego Jesús pregunta quién dice la gente que es él, y Pedro responde: «Tú eres el Cristo, el Hijo del Dios viviente» — recibido con un juego de palabras sobre el propio nombre de Pedro, una promesa de edificar «mi congregación» (no, insiste esta traducción, «mi iglesia»), y llaves para atar y desatar en la tierra. Después, en el mismo aliento, la primera predicción clara de la cruz — y Pedro, elogiado un momento, llamado «Satanás» al siguiente por tratar de disuadir a Jesús. Cierra sobre el costo de seguirlo: niégate a ti mismo, toma tu cruz, y una promesa de que algunos de los que están aquí no probarán la muerte hasta que vean al Hijo del Hombre viniendo en su reino.",
    "mat17": "Seis días después, tres de ellos suben a un monte alto y él es TRANSFIGURADO — su rostro como el sol, Moisés y Elías a su lado, Pedro ofreciéndose a levantar tiendas, y desde una nube luminosa la voz del bautismo diciendo la misma frase con un imperativo nuevo pegado: «escuchadle a él». Al bajar, una orden de callar con fecha de caducidad, y la pregunta de los escribas sobre Elías respondida sin rodeos: ya vino, e hicieron con él lo que quisieron. Y en seguida, un desastre al pie del monte — un muchacho lunático que los discípulos no pudieron curar, un reproche por la «poca fe», y un grano de mostaza frente a una montaña. El segundo anuncio de la pasión, esta vez sin discusión de Pedro. Y, solo en Mateo, el impuesto del templo: los reyes cobran a los extraños y no a sus propios hijos, así que los hijos están exentos — libertad afirmada e inmediatamente renunciada, y saldada con una moneda de cuatro dracmas en la boca de un pez que el capítulo nunca dice que se pescara. ⚠ Aquí no hay versículo 21: las palabras que imprime la RV faltan en los manuscritos más antiguos, y se deja el hueco a la vista en vez de renumerar.",
    "mat18": "El CUARTO DISCURSO — sobre la vida dentro de la congregación, y abre con la pregunta equivocada: los discípulos preguntan quién es el MAYOR. Jesús responde con su propio comparativo, pone a un niño en medio de ellos y dice que el camino de entrada es VOLVERSE y hacerse como uno. Luego la piedra de molino que gira un asno, la mano y el pie y el ojo ya cortados una vez en el Sermón, y la Gehena. Las noventa y nueve dejadas EN LOS MONTES para buscar a la que se descarrió. Un procedimiento de tres pasos para el hermano que te agravia, construido para detenerse en la etapa más temprana y que acaba —si hace falta— en la <em>ekkl&#275;sia</em>, palabra que Jesús pronuncia solo dos veces en todo el Evangelio y que aquí tiene que ser algo lo bastante pequeño como para oír una riña privada; y después atar y desatar, dado en 16:19 a Pedro en singular y aquí a todos en plural. Y el discurso se cierra donde se abrió: dos o tres reunidos, y Cristo «en medio de ellos» — el sitio exacto del niño, en las mismas tres palabras griegas. Pedro pregunta cuántas veces perdonar; la respuesta cita el cantar vengativo de Lamec y lo corre al revés. Luego diez mil talentos frente a cien denarios, dos súplicas idénticas de paciencia, y un final que nadie cita. ⚠ Aquí no hay versículo 11: las palabras que imprime la RV faltan en los manuscritos más antiguos, y se deja el hueco a la vista.",
    "mat19": "Fuera de Galilea por fin — la cuarta de las cinco junturas de discurso cierra el capítulo 18, y desde aquí el libro solo viaja hacia Jerusalén. Unos fariseos preguntan si un hombre puede repudiar a su mujer POR CUALQUIER CAUSA, que no es una pregunta neutral sino el lema de uno de los bandos de una disputa rabínica viva; Jesús responde yéndose por detrás de Moisés hasta el Génesis, y distingue lo que Moisés MANDÓ de lo que PERMITIÓ, «por vuestra dureza de corazón». Los discípulos concluyen que no conviene casarse. Luego traen unos niños — y los discípulos los reprenden, un capítulo después de que se les dijera que de los tales es el reino; Mateo no comenta, y no le hace falta. ⚠ Después el joven rico, donde el texto más antiguo de Mateo NO es el familiar: no «Maestro bueno / ¿por qué me llamas bueno?» (que es como leen Marcos y Lucas, y como los copistas posteriores hicieron leer a Mateo) sino «¿qué COSA BUENA he de hacer / por qué me preguntas acerca de lo bueno?» — el adjetivo movido del hombre a la obra. Se va entristecido: la única persona del libro a quien se invita a seguirlo y no lo hace. Un camello, una aguja, y dos rescates populares que no sobreviven al contacto con la evidencia. Y luego la pregunta contable de Pedro, doce tronos prometidos a oídos de Judas, y una advertencia apuntada justo al que preguntó: muchos primeros serán últimos.",
    "mat20": "La parábola de la viña es un CORCHETE: 19:30 dijo «muchos primeros serán últimos», dieciséis versículos lo argumentan, y el v 16 lo repite. Obreros contratados al amanecer, a las nueve, al mediodía, a las tres y a las cinco — y los últimos están parados por una razón que las versiones populares no suelen mencionar: «<em>porque nadie nos ha contratado</em>». A todos se les paga un denario, y la queja es precisa: no que a nadie se le pagara de menos, sino «los has hecho IGUALES a nosotros». El agravio es la igualdad, y la respuesta es un modismo semítico sobre un ojo tacaño. Luego el TERCER anuncio de la pasión, el más completo — el primero que nombra a los gentiles y el primero que dice la palabra CRUCIFICAR, que tuvo que esperar a que los romanos entraran en la frase. Y en seguida, una madre pidiendo los dos mejores asientos; una copa que sus hijos aceptan beber sin saber qué es; y dos verbos de mezquindad respondidos con dos palabras en una escalera que BAJA — servidor, y luego esclavo — para terminar en el único lugar de Mateo donde Jesús declara el propósito de su muerte como una transacción: un rescate en cambio por muchos. Cierra en Jericó con dos ciegos gritando un título real por encima de la objeción de la multitud, y siguiéndolo camino arriba en cuanto ven. ⚠ La línea de más que la RV trae en el v 16 («muchos son llamados, mas pocos escogidos») falta aquí en los manuscritos más antiguos y es original en 22:14.",
    "mat21": "Jerusalén, por fin. ⚠ Mateo es el único evangelista con DOS animales —una asna y un pollino— porque lee el paralelismo hebreo de Zacarías como si nombrara dos bestias en vez de decir una cosa dos veces; toda la tradición visual, Giotto incluido, pinta calladamente una. HOSANNA no es alabanza sino un grito de auxilio, <em>hoshi&rsquo;a-na</em>, «salva, por favor» — y la multitud está cantando el Salmo 118, cuyos versículos centrales Jesús citará de vuelta contra las autoridades antes de que acabe el capítulo. Toda la ciudad se SACUDE, con la palabra del terremoto que Mateo reserva para las bisagras. Luego el templo: mesas volcadas, y una acusación soldada de Isaías y Jeremías — no una cueva de rateros, sino una CUEVA DE BANDIDOS, la misma palabra que los dos hombres crucificados a su lado. Una higuera con hojas y sin fruto, colocada justo después de un templo con actividad y sin fruto. La pregunta por la autoridad, respondida con una pregunta que ellos no pueden permitirse contestar, y Mateo nos dice por qué: «tememos a la multitud». ⚠ Después los dos hijos, donde tres arreglos manuscritos dan dos respuestas distintas y los dos testigos del estante en español caen a lados opuestos. Y los labradores de la viña, que abre con el Cantar de la Viña de Isaías y cierra sobre una piedra desechada — con la frase sobre «una nación que produzca sus frutos» cuya lectura sustitutoria esta biblioteca nombra en vez de esquivar.",
    "mat22": "Cuatro grupos lo interrogan en el templo y él hace la última pregunta él mismo, tras lo cual «nadie osó preguntarle nada más». Un banquete de bodas al que los invitados no quieren ir, sustituidos por quien esté en los cruces de caminos —«malos y buenos»— y un convidado sin traje que queda <em>amordazado</em>, el mismo verbo vivo que Jesús usará con los saduceos doce versículos después. ⚠ Y la frase «muchos son llamados, pero pocos escogidos» se sienta por fin en su propia casa: la nota del capítulo 20 dijo que pertenecía aquí y que allí fue importada, y en 22:14 los manuscritos no plantean ninguna disputa. Luego la moneda: fariseos aliados con HERODIANOS, una trampa que funciona responda lo que responda, y una pregunta sobre de quién es la IMAGEN que lleva —<em>eikōn</em>, la palabra de Génesis 1:27— respondida con DEVOLVED, no con «dad». Los siete hermanos de los saduceos, contestados con un argumento que descansa en un «YO SOY» en presente que el griego suple y que el hebreo de Éxodo 3:6 no escribe. Dos mandamientos de los que PENDE toda la Ley, como un abrigo de una clavija. Y los dos señores del Salmo 110, enigma más agudo en griego que en hebreo, que él deja abierto.",
    "mat23": "Nadie interrumpe. Treinta y ocho versículos de discurso ininterrumpido, el ataque sostenido más largo del Evangelio — y abre CONCEDIÉNDOLES la autoridad: se han sentado en la cátedra de Moisés, así que «haced todo cuanto os digan», frase que la biblioteca expone sin limar. Filacterias ensanchadas y flecos alargados — y el fleco es el que Jesús lleva él mismo, tocado para sanar en 9:20. Tres títulos rechazados, incluido el que la práctica cristiana posterior ha conservado con más claridad. ⚠ Luego SIETE ayes — siete en el texto crítico, porque el octavo de la RV (el versículo 14, el de las casas de las viudas) falta en los manuscritos más antiguos y no logra ni ponerse de acuerdo consigo mismo sobre dónde colocarse. Un sistema de juramentos desmontado hasta que no queda juramento que no alcance a Dios; menta y anís diezmados mientras se deja el juicio, la misericordia y la fidelidad; un mosquito colado y un camello tragado; y sepulcros blanqueados — donde la cal era una ADVERTENCIA y no un adorno, porque tocar una tumba te dejaba impuro. ⚠ Y luego un nombre que no encaja: Zacarías hijo de Baraquías, cuya filiación es la del profeta y cuyo asesinato es de otro hombre. Y entonces, sin aviso, se rompe el registro: «Jerusalén, Jerusalén… cuántas veces quise juntar a tus hijos, del modo que una gallina junta a sus polluelos — y no quisisteis».",
    "mat24": "Empieza el quinto y último discurso. Sale del templo tres versículos después de llamarlo desierto, un discípulo señala la mampostería, y la respuesta es que no quedará piedra sobre piedra. ⚠ Y luego la pregunta que hereda todo el capítulo: los discípulos preguntan por la caída del templo, por su PRESENCIA (<em>parousia</em>, palabra que Mateo usa cuatro veces y las cuatro aquí) y por la conclusión del siglo — y en griego las dos últimas comparten un solo artículo, lo que puede significar que lo toman todo por un mismo suceso. Guerras y hambres son solo DOLORES DE PARTO, el dolor que indica que un proceso está en marcha. Daniel nombrado sin rodeos por la abominación, con el único aparte al lector de todo el Evangelio. Instrucciones de huida demasiado locales y de corto alcance para tratar del fin del mundo. Un relámpago del que nadie necesita ser informado, y buitres sobre un cuerpo. ⚠ Después las dos frases más difíciles de Mateo: «esta generación no pasará…» (cuatro lecturas expuestas, con lo que cuesta cada una, incluida la que concede que los términos no se cumplieron), y «acerca de aquel día y hora nadie sabe — ni los ángeles, NI EL HIJO» — tres palabras presentes en los manuscritos más antiguos, ausentes de la tradición bizantina, e impresas aquí, porque ningún copista tiene motivo para añadirlas. La generación de Noé se invoca por la inadvertencia, no por la maldad; y uno es llevado y otro dejado, donde la lectura popular y el diluvio de dos versículos antes apuntan en direcciones contrarias. Termina en un solo imperativo: permaneced despiertos.",
    "mat25": "El mismo discurso, todavía en marcha, y la última enseñanza del Evangelio. ⚠ Diez muchachas con lámparas —no «vírgenes», porque nada en el relato depende de la castidad y lo que distingue a las dos cincos es el ACEITE— y nótese que, cuando el novio se demora, TODAS LAS DIEZ se duermen. La parábola no reprocha el dormir; lo que las separa es una decisión tomada antes de que empezara la espera, y las cinco sensatas se niegan a compartir porque hay cosas que no se pueden prestar en el último momento. Luego los talentos, donde la parte más pequeña son veinte años de jornal, los dos que invirtieron reciben elogios palabra por palabra idénticos, y ⚠ el tercer esclavo llama DURO a su señor — y el señor no lo niega: argumenta desde la premisa del propio esclavo. Después las ovejas y los cabritos, que deja de ser parábola y se vuelve veredicto: seis puntos corrientes, ninguno religioso, y los dos grupos haciendo la misma pregunta — «¿CUÁNDO te vimos?». Ninguno lo sabía. ⚠ Termina en dos palabras discutidas, <em>kolasis</em> (arraigada en la poda, no en la retribución) y <em>ai&#333;nios</em> (duración, o la cualidad del siglo venidero), aplicadas a los dos destinos en una sola frase — el terreno textual de una discusión a tres bandas que la biblioteca describe y en la que no entra. Después de cinco discursos, el criterio final no es la doctrina, ni la vigilancia, ni la productividad. Es si alguien comió.",
    "mat26": "Se acabaron los discursos; desde aquí Mateo narra. ⚠ Un frasco de perfume quebrado sobre su cabeza y una objeción sobre los pobres —donde el versículo que se cita para postergar la limosna es, en Deuteronomio, la premisa de un mandato de dar—. Treinta piezas de plata, pesadas con el verbo de pesar de Zacarías. Una cena donde el pan y una copa reciben nombres nuevos, y donde el texto más antiguo NO lee pacto «nuevo» y sí lee «por muchos». Getsemaní, el lagar de aceite, donde la copa que ofreció a dos hermanos ambiciosos se vuelve la que pide que se le pase, y donde el «permaneced despiertos» de los dos capítulos anteriores se falla tres veces. Un beso, una espada envainada, y una frase a Judas sin verbo principal. Luego dos audiencias en una casa: dentro, bajo juramento, describe el trono del capítulo 25 desde el banquillo; fuera, en el mismo patio, bajo juramento, Pedro lo niega tres veces —llanamente, luego jurando, luego invocando maldiciones— y lo delata su acento.",
    "mat27": "El capítulo que Mateo cuenta con menos adjetivos y más Salmos. ⚠ Judas se llena de PESAR, no de arrepentimiento —la palabra más blanda— y los sacerdotes se lo quitan de encima con la frase exacta que Pilato usará después con ellos. Luego una cita que Mateo atribuye a JEREMÍAS y cuyas palabras son de Zacarías, aquí expuesta en vez de remendada: el hebreo de Zacarías lee «alfarero» donde casi todas las Biblias imprimen «tesoro», y los sacerdotes de Mateo rechazan el tesoro y compran el campo del alfarero. ⚠ El preso se imprime como JESÚS Barrabás —la lectura que Orígenes encontró en sus manuscritos y a la que objetó— de modo que Pilato ofrece elegir entre dos hombres llamados Jesús, uno de ellos «hijo del padre». Una jofaina de agua que no transfiere nada, y luego ⚠ el versículo 25, impreso llanamente y con su historia nombrada, porque ningún versículo de este Evangelio se ha usado para hacer más daño. Un forastero de Cirene reclutado con el verbo de requisa del propio Sermón. Vino con hiel, no vinagre. Un grito en hebreo y arameo a la vez, y por eso lo oyen mal como «Elías». Y una cortina rasgada, un temblor, tres líneas sobre sepulcros abiertos que ningún otro Evangelio tiene y nadie puede explicar, un centurión cuyo griego no lleva artículo, y una piedra sellada.",
    "mat28": "El último capítulo del Evangelio, y el primer libro del Nuevo Testamento que este proyecto termina. ⚠ Un gran TEMBLOR en el sepulcro y los guardias sacudidos con el mismo verbo; un mensajero que hace rodar la piedra y luego SE SIENTA sobre ella, cosa que ningún otro Evangelio tiene; y «FUE LEVANTADO» en pasiva, con el agente sin declarar, como prefiere este Evangelio. La plata cambia de manos por segunda vez, y el relato que se paga a los soldados por contar los condenaría por dormir de guardia —Mateo deja el agujero a la vista y no lo señala—. Luego un monte, y ⚠ la palabra que prometió el capítulo 14: los once se postraron «pero algunos de ellos DUDARON» —<em>distazō</em>, usado dos veces en todo el Nuevo Testamento, de Pedro hundiéndose y de estos hombres, y esta vez sin ningún reproche antes de que se entregue toda autoridad—. La frontera dura de 10:5-6 se abre a TODAS LAS NACIONES sin reconciliación alguna; la fórmula bautismal se imprime con el estado de la evidencia expuesto con precisión; y el libro cierra con las mismas tres palabras con que abrió: «yo estoy con vosotros» respondiendo a Emmanuel, «Dios con nosotros». Sin ascensión y sin Amén final en el texto más antiguo: se detiene con él todavía hablando.",
    "rev8": "El Cordero abre el séptimo sello, y en vez de un séptimo horror hay silencio en el cielo como por media hora -- uno de los momentos menos explicados de todo el libro, y la biblioteca expone varias conjeturas antiguas sin decidirse por ninguna. A siete ángeles se les dan siete trompetas; antes de que suene ninguna, otro ángel ofrece incienso con las oraciones de los santos sobre el altar de oro, probablemente las mismas oraciones ya escuchadas, el propio «¿hasta cuándo?» de los mártires del capítulo 6 -- y luego llena el mismo incensario de fuego y lo arroja a la tierra. Suenan las primeras cuatro trompetas: granizo y fuego mezclados con sangre queman una tercera parte de la tierra, reescribiendo la séptima plaga de Egipto; una montaña ardiendo convierte en sangre una tercera parte del mar; una estrella caída llamada Ajenjo, la vieja imagen propia de la Biblia hebrea para la amargura del juicio, envenena una tercera parte de las aguas; una tercera parte del sol, la luna y las estrellas se oscurece. Donde el jinete del cuarto sello alcanzaba una cuarta parte de la tierra, cada trompeta alcanza ahora una tercera -- el mismo patrón parcial, no total, intensificado. El capítulo se cierra con una sola águila -- &#9888; «ángel» en KJV y RV60, siguiendo el Textus Receptus; «águila» en todas las demás versiones aquí comparadas, siguiendo los manuscritos más antiguos -- clamando tres ayes por lo que las últimas tres trompetas todavía han de traer.",
    "rev7": "El capítulo 6 terminó con una pregunta -- ¿quién podrá sostenerse en pie? -- y este capítulo retrasa la respuesta todavía más. Cuatro ángeles detienen los cuatro vientos; la tierra, el mar y todo árbol esperan intactos mientras un quinto ángel sella primero a «los siervos de nuestro Dios» en sus frentes. Ciento cuarenta y cuatro mil son sellados, tribu por tribu, doce mil cada una -- y &#9888; Dan falta de la lista, la única de las doce tribus de los hijos de Jacob que nunca se nombra aquí, por razones que el texto mismo nunca declara. Luego aparece una segunda multitud, que nadie podía contar, de toda nación, tribu, pueblo y lengua, vestida de blanco y con palmas en las manos, clamando que la salvación pertenece a Dios y al Cordero. Un anciano explica: son los que están saliendo de la gran tribulación, que lavaron sus ropas y las emblanquecieron en la sangre del Cordero -- una paradoja que el griego no suaviza. Ya no tendrán hambre ni sed, resguardados por el que «extenderá su tabernáculo» sobre ellos, en un lenguaje que tres versiones en inglés traducen de tres maneras distintas. La promesa final del capítulo, que Dios enjugará toda lágrima de sus ojos, no es la única vez en este libro -- las mismas palabras regresan, exactas, cuando toda la visión se cierra en el capítulo 21.",
    "rev6": "El Cordero comienza a abrir los siete sellos, uno por uno. Cuatro jinetes salen por turnos, cada uno convocado por la palabra única de un ser viviente, «Ven»: un caballo blanco cuyo jinete lleva un arco y una corona, venciendo; un caballo bermejo que quita la paz de la tierra; un caballo negro cuyo jinete lleva una balanza, tasando la comida de un día en el salario de un día mientras respeta el aceite y el vino; y un caballo amarillo llamado Muerte, seguido por el Hades, con poder para matar a la cuarta parte de la tierra. &#9888; Quién es el primer jinete, el texto nunca lo dice, y la biblioteca expone dos lecturas vivas en vez de elegir una: la conquista misma, o Cristo saliendo a vencer. El quinto sello se abre sobre las almas de los muertos bajo el altar, clamando la vieja pregunta propia del Salterio, «¿hasta cuándo?», y se les dice que descansen un poco más hasta que se complete un número fijo aún por venir. El sexto sello sacude el cielo mismo -- el sol se pone negro, la luna se vuelve sangre, caen las estrellas, el cielo se enrolla como un rollo, citando directamente a Joel y a Isaías -- hasta que todo rango de la humanidad, de reyes a esclavos, suplica a los montes que caigan sobre ellos y los escondan, la misma súplica que Jesús dijo a las mujeres de Jerusalén que llorarían un día. La última línea del capítulo es una pregunta que nada en él responde: ¿quién podrá sostenerse en pie?",
    "rev5": "El rollo de la nota final del capítulo 4 está ahora en la mano del que está sentado en el trono, sellado con siete sellos, y un ángel poderoso pregunta quién es digno de abrirlo. Nadie en el cielo, ni en la tierra, ni debajo de la tierra puede — hasta que un anciano le dice a Juan que deje de llorar: «el León de la tribu de Judá, la Raíz de David, ha vencido». Juan se vuelve a mirar al León, y lo que ve es un Cordero, en pie, como inmolado. La palabra es <em>arnión</em>, un diminutivo que el Evangelio de Juan nunca usa de Cristo, y este libro la repetirá veintiocho veces más, hasta sus últimos capítulos. El Cordero toma el rollo, y toda la escena estalla en canto — primero los veinticuatro ancianos y los cuatro seres vivientes, luego incontables ángeles, luego «toda criatura en el cielo, en la tierra, debajo de la tierra y en el mar», declarando al Cordero digno por un motivo distinto del que el capítulo 4 dio a Dios: no por crear, sino por haber sido inmolado y comprado un pueblo «de toda tribu, lengua, pueblo y nación». &#9888; Los versículos 9-10 llevan una diferencia textual real: RV60, siguiendo el Textus Receptus, lee en primera persona todo el pasaje («nos has redimido&hellip; reinaremos»); los manuscritos más antiguos detrás de ASV, NIV y ESV leen en tercera persona («personas&hellip; ellos reinarán») — la lectura que sigue esta traducción.",
    "rev4": "Las siete cartas están completas, y el siguiente movimiento del libro se abre exactamente donde la propia nota final del capítulo 3 dijo que lo haría: una puerta que está abierta en el cielo. Juan es arrebatado y ve un trono — nunca descrito físicamente, solo comparado con el destello de piedras preciosas y el color de un arco iris, la misma contención que toda la Biblia guarda en torno a la forma divina. Veinticuatro ancianos de blanco, siete llamas ardiendo que son «los siete espíritus de Dios» (nombrados aquí por tercera vez), un mar de vidrio, y cuatro seres vivientes cubiertos de ojos. ⚠ KJV es la única versión que los llama «bestias» — todas las demás, en los dos idiomas, leen «seres vivientes», el sentido llano del griego. No son invención de Juan: los cuatro rostros (león, buey, hombre, águila) vienen de la visión del trono de Ezequiel, donde cada ser llevaba los cuatro a la vez; las seis alas y el clamor incesante vienen de los serafines de Isaías, clamando las mismas tres palabras que este capítulo repite ahora — «santo, santo, santo». Los ancianos responden echando sus propias coronas delante del trono y declarando a Dios digno por un solo motivo: creó todas las cosas. Es el primero de dos himnos de adoración que este libro cantará a dos tronos que resultan ser uno — el Cordero del capítulo 5 será declarado digno por un motivo completamente distinto, no por haber creado, sino por haber sido inmolado.",
    "rev3": "Las cartas concluyen — Sardis, Filadelfia, Laodicea. ⚠ Sardis no recibe ningún elogio: «tienes nombre de que vives, y estás muerto», una ciudad famosa por haber sido tomada dos veces de noche porque sus centinelas dejaron de vigilar el único acceso escalable. Filadelfia, junto con Esmirna, no recibe ninguna queja: «una puerta abierta, la cual nadie puede cerrar» — la frase que se volvió taquigrafía cristiana para la oportunidad — y una promesa de convertirse en columna, dicha a una ciudad que aún se reconstruía de un terremoto. Luego Laodicea, rica, satisfecha de sí misma, «ni fría ni caliente» — una ciudad cuya propia agua de acueducto llegaba tibia desde las fuentes termales de Hierápolis y las frías de Colosas, y cuyas tres grandes jactancias (banca, lana negra, colirio) son respondidas una por una: oro refinado en fuego, vestiduras blancas, colirio que de verdad sana. Y el versículo más reproducido del capítulo, «yo estoy a la puerta y llamo» (v. 20), dirigido no a un forastero sino a la propia iglesia, al otro lado de su reprimenda más dura.",
    "rev21": "Un cielo nuevo y una tierra nueva, sin mar, y toda l\u00e1grima enjugada \u2014 y \u26a0 la palabra para \u00abnuevo\u00bb es una decisi\u00f3n que el libro entero mantiene: KAINOS nueve veces, NEOS ninguna. Nuevo en clase, no en tiempo. \u26a0 La tienda de Dios est\u00e1 con los hombres, y el verbo es el de Juan 1:14: sale en dos libros nada m\u00e1s. La ciudad es un CUBO de doce mil estadios por lado, y el \u00fanico otro cubo de la Biblia es el Lugar Sant\u00edsimo. No hay santuario en ella. Y la lista del v. 8 empieza por LOS COBARDES, la misma palabra de la \u00faltima frase de Jes\u00fas a sus amigos.",
    "mark5": "Un hombre poseído por &lsquo;Legión&rsquo; &mdash; palabra militar romana tomada prestada para describir una multitud dentro de un solo hombre &mdash; queda libre entre los sepulcros, y una piara de unos dos mil cerdos se precipita colina abajo hacia el lago, llevando consigo a los espíritus que Jesús les permite entrar sin comentario alguno. &#9888; El propio nombre de la región es discutido en los manuscritos, &lsquo;gadarenos&rsquo; frente a &lsquo;gerasenos&rsquo;, una verdadera controversia textual que esta traducción reporta en vez de resolver. El pueblo, más temeroso del hombre sanado que del poseído, le pide a Jesús que se vaya &mdash; la única petición del capítulo que él no discute &mdash; y por primera vez en este Evangelio le dice a alguien que vaya a su casa y PROCLAME en vez de callar, enviando al primer misionero de la Decápolis a la historia sin trasfondo de pescador alguno. Luego dos milagros se entrelazan: un jefe de sinagoga llamado Jairo cae a los pies del mismo tipo de autoridad que ya conspira contra Jesús, por una &lsquo;hijita&rsquo; a punto de morir; en el camino, una mujer enferma desde hace doce años &mdash; el mismo número que la edad de la niña hacia la que él corre &mdash; toca su manto por detrás y es sanada por un PODER que el texto describe casi físicamente, que sale de él y se percibe al salir. &ldquo;Hija&rdquo;, la llama &mdash; la única vez en este Evangelio que usa esa palabra para una mujer adulta. Luego Pedro, Jacobo y Juan aparecen juntos por primera vez como grupo, llevados a solas a una habitación que ya se ríe de la afirmación de que la niña solo duerme &mdash; y &ldquo;Talita cum&rdquo;, dicho en el arameo que Jesús realmente hablaba, conservado sin traducir y traducido de inmediato después, el mismo patrón ya usado para &lsquo;Boanerges&rsquo;. La orden de guardar silencio regresa de inmediato, la instrucción opuesta a la que se acaba de dar un capítulo antes, sin que se declare la regla que conecta ambas decisiones.",
    "jer24": "Dos cestas de higos, puestas delante del templo tras la primera deportación a Babilonia en el 597 a.C. &mdash; una cesta con higos muy buenos, como higos tempranos, y otra tan mala que no se puede comer. La propia interpretación de Jehová invierte todo instinto: los higos buenos son los exiliados que ya se fueron, despojados y llevados a Babilonia, y los higos malos son Sedequías, sus príncipes, y todos los que siguen en Jerusalén o dispersos en Egipto. A los higos buenos, Jehová promete &lsquo;edificarlos y no derribarlos, plantarlos y no arrancarlos&rsquo; &mdash; dos de los mismos seis verbos entregados al profeta en su propio llamado (1:10), ahora dichos como misericordia y no como mandato &mdash; y &lsquo;un corazón para conocerme&rsquo;, la misma fórmula del pacto que este libro amplía a toda la casa de Israel tres capítulos después, en el oráculo del Nuevo Pacto. &#9888; El &lsquo;así consideraré&rsquo; del v. 5 y el &lsquo;conocerme&rsquo; del v. 7 traducen dos raíces hebreas distintas a cuatro versículos de diferencia, una de reconocimiento formal y otra de relación &mdash; mantenidas aparte en vez de aplanarlas en una sola palabra. A los higos malos: la misma sentencia de espada, hambre y pestilencia ya entregada a Sedequías por nombre tres capítulos antes, y una división del estante a cinco bandas sobre la única palabra para lo que llegan a ser ante &lsquo;todos los reinos de la tierra&rsquo; &mdash; removidos, zarandeados, u objeto de horror, según qué versión esté abierta.",
    "jer25": "Una fecha lo bastante precisa como para hacer la cuenta &mdash; el año cuarto de Joacim, que fue también el primer año de Nabucodonosor, 605 a.C., el año en que Babilonia se convirtió en la potencia indiscutida de la región. Jeremías audita primero su propia carrera: veintitrés años del mismo mensaje, sin escuchar. Luego Jehová llama a Nabucodonosor &lsquo;mi siervo&rsquo; sin suavizarlo, y pronuncia el número más determinante de todo el resto del libro &mdash; setenta años de servicio a Babilonia, una profecía que los capítulos posteriores de este mismo libro (ya en estas páginas) tratan como una cuenta que vence a su tiempo. Una copa del vino del furor se entrega a nación tras nación en una lista que va desde los vecinos más cercanos de Judá hasta potencias en el borde del mundo conocido &mdash; Judá bebe primero, no al final &mdash; y termina con un nombre escondido en una clave: &lsquo;el rey de SESAC&rsquo;, que se descifra, letra por letra, como &lsquo;Babilonia&rsquo; misma, el imperio a punto de servir de verdugo de todos los demás descubriendo su propio nombre en la lista. &#9888; El capítulo cierra con Jehová rugiendo &lsquo;desde lo alto&rsquo; con el mismo par de verbos que Amós usó para abrir su propio libro siglo y medio antes, y los pastores &mdash; advertidos tres capítulos atrás &mdash; reciben por fin su sentencia real en vez de un ay.",
    "jer26": "Jeremías es juzgado por su vida, y la acusación es un sermón. Con la orden de plantarse en el atrio del templo y predicar sin <strong>recortar ni una palabra</strong>, dice lo único que garantiza un mal final: Dios hará a esta casa &lsquo;como a <strong>Silo</strong>&rsquo; &mdash; el santuario que ya cayó una vez, y a cuyas ruinas cualquiera en aquel atrio podría haber caminado. Los sacerdotes, los profetas y todo el pueblo lo agarran en el acto: &lsquo;¡De cierto morirás!&rsquo; &#9888; Lo que sigue es lo más parecido a un acta judicial en todos los profetas. Los príncipes suben del palacio y se SIENTAN en la Puerta Nueva, que es lo que hace un tribunal; los sacerdotes piden la condena en tres palabras hebreas, &lsquo;sentencia de muerte para este hombre&rsquo;; y el fallo, cinco versículos después, es la frase idéntica con una negación delante. Jeremías no ofrece defensa alguna &mdash; confirma la acusación, repite el sermón y dice &lsquo;estoy en vuestra mano&rsquo;, argumentando solo que matarlo pondría sangre inocente sobre la ciudad. &#9888; Entonces los ancianos se levantan con un escrito jurídico: un siglo antes, <strong>Miqueas de Moreset</strong> dijo que Sion sería arada como un campo, y Ezequías no lo mató &mdash; el único lugar de la Biblia hebrea donde un profeta con libro propio es citado POR NOMBRE por otro, usado en un tribunal para salvarle la vida a un hombre. Y el capítulo termina contándote lo que solía pasar en cambio: Urías hijo de Semaías, que predicó el mismo mensaje, fue extraditado de Egipto por orden real y muerto por el rey en persona. Jeremías vivió porque la mano de un solo funcionario estuvo de su lado.",
    "jer27": "Jeremías se pone un yugo de madera y camina por Jerusalén con él, luego desmonta las piezas y las envía a cinco reyes aliados &mdash; Edom, Moab, Amón, Tiro y Sidón &mdash; junto con la misma orden que le da a Sedequías en persona: sometan el cuello al rey de Babilonia y vivan. &#9888; El propio versículo 1 fecha el capítulo en el reinado de Joacim, pero todo el resto se dirige a Sedequías &mdash; una de las cruces textuales más conocidas del libro, que esta traducción reporta en vez de corregir en silencio. La razón que Dios da para el sometimiento no es la conveniencia política, sino la creación misma: &lsquo;yo hice la tierra&hellip; y la doy a quien me parece recto&rsquo; &mdash; y ahora mismo se la ha dado a Nabucodonosor, a quien llama &lsquo;mi siervo&rsquo;, con una fecha de caducidad incorporada en la misma frase. Cinco categorías distintas de adivinos son descartadas juntas por decir lo contrario. Y el capítulo cierra con una profecía que este proyecto ya puede rastrear por los dos extremos: los utensilios del templo que aún quedan en Jerusalén &mdash; después de que la primera deportación ya se llevara algunos &mdash; también irán a Babilonia, contra lo que prometen los falsos profetas, y solo volverán el día que Jehová decida &lsquo;visitarlos&rsquo;.",
    "jer28": "Dos profetas, ambos titulados &lsquo;el profeta&rsquo;, ambos afirmando hablar por Jehová, en la misma sala, diciendo cosas opuestas. Hananías de Gabaón enfrenta a Jeremías en el templo con una contraprofecía detallada: dentro de dos años vuelven los utensilios, vuelve Jeconías, vuelven todos los exiliados, porque &lsquo;yo he quebrado el yugo del rey de Babilonia&rsquo; &mdash; dicho a un hombre que todavía lleva puesto un yugo de madera real sobre el cuello. &#9888; La primera palabra de Jeremías es &lsquo;Amén&rsquo; &mdash; no es sarcasmo, es un deseo genuino de estar equivocado &mdash; antes de plantear la prueba: los profetas de desastre no necesitan verificación, pero un profeta de paz hace la afirmación más difícil, y &lsquo;entonces se sabrá&rsquo; solo cuando las palabras se cumplan. Hananías no discute. Le quiebra la barra de madera del cuello a Jeremías delante de todos. La respuesta de Jehová escala en vez de contradecir &mdash; madera cambiada por hierro, el mismo oráculo en un material más duro &mdash; y Jeremías entrega un veredicto público y comprobable: este año, Hananías morirá, por inventar palabras y ponerlas en boca de Jehová. El versículo final reporta la muerte dos meses después, en el mes séptimo &mdash; una de las pocas profecías de la Biblia cuyo cumplimiento cae dentro del mismo capítulo que la pronunció.",
    "jer30": "A Jeremías se le ordena, casi de forma única en este libro, &lsquo;escríbelo en un libro&rsquo; &mdash; la mitad inicial del Libro de la Consolación, treinta capítulos de juicio que por fin dan paso a la esperanza sostenida. El yugo de los caps. 27&ndash;28 se quiebra para siempre, ahora en el propio calendario de Jehová, y el pueblo servirá a &lsquo;David su rey&rsquo; &mdash; una frase que el estante divide entre leer literal o dinásticamente, dejada abierta aquí. Seis versículos seguidos llaman a la herida de la nación llanamente incurable, por cualquier medicina que exista &mdash; y luego Jehová entrega la cura imposible de todos modos, porque el sanador no está limitado por lo que la medicina puede hacer normalmente. El capítulo cierra con la &lsquo;tempestad de Jehová&rsquo;, copiada casi palabra por palabra de la denuncia de los falsos profetas del cap. 23, siete capítulos atrás &mdash; la misma tormenta haciendo un trabajo distinto la segunda vez. &#9888; Su último versículo pertenece, en hebreo, a este capítulo, pero toda Biblia en español lo numera como Jeremías 31:1 &mdash; un límite de contenido real ya cruzado una vez antes en este sitio, en el propio cap. 31.",
    "rev22": "El \u00faltimo cap\u00edtulo de la Biblia: el r\u00edo, el \u00e1rbol de la vida en las dos orillas y hojas para la curaci\u00f3n de las naciones. \u26a0 Dos variantes de aqu\u00ed valen m\u00e1s que muchos libros de cr\u00edtica textual. El v. 14 es \u00ablavan sus ropas\u00bb en todos los textos cr\u00edticos y tambi\u00e9n en el mayoritario bizantino \u2014RV y NVI aciertan aqu\u00ed donde la King James se equivoca\u2014. Y el v. 19 dice \u00ab\u00e1rbol de la vida\u00bb en todos los testigos griegos: el \u00ablibro de la vida\u00bb de la RV viene de Erasmo retraduciendo desde el lat\u00edn en 1516, porque a su \u00fanico manuscrito le faltaba la \u00faltima hoja. La frase que proh\u00edbe a\u00f1adir al libro tiene, en la Biblia castellana m\u00e1s le\u00edda, una palabra que le fue a\u00f1adida.",
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


# Chapters whose SOURCE TEXT is Aramaic, not Hebrew: Daniel 2:4b-7:28 is the Bible's
# best-known Aramaic block (Ezra has two more, 4:8-6:18 and 7:12-26, not yet on
# these pages). Daniel 2 itself is mixed -- Hebrew for its first four verses, Aramaic
# for the other forty-five -- so "Aramaic" is the more honest single label for the
# whole chapter's toggle button even though it is not the whole story.
# Added 2026-08-01 shipping Daniel 3: the "Hide Hebrew" toggle was wrong on every
# Aramaic chapter already on the site (Daniel 2), not just the new one.
_ARAMAIC_CHAPTERS = {("Daniel", n) for n in (2, 3, 4, 5, 6, 7)}


def _source_lang(book, num):
    """The Hide-original toggle label: Greek / Aramaic / Hebrew."""
    if _is_nt(book):
        return "Greek"
    if (book, num) in _ARAMAIC_CHAPTERS:
        return "Aramaic"
    return "Hebrew"


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
    # Share rides as the last item in the same nav row as Home/About/etc (not a
    # separate floating line below it — that read as disjointed). Views moved to
    # the footer (see _FOOT_VIEWS_LINE) -- it was competing for room in this row
    # and it's the kind of thing a reader checks at the end, not the top, anyway.
    share_item = '<span class="share-widget"></span>'
    if lang == "es":
        # Spanish locale header. The nav links ONLY to pages that exist in Spanish
        # (so a Spanish-only reader is never dumped into English); it grows as the
        # Spanish edition is built out. The 🌐 switch jumps to the English home.
        # "Preguntar" sits on its own on the LEFT (mirroring the English layout's
        # split -- see the note below) so it isn't crowded against the brand icon.
        return f"""<header class="site-head">
  <div class="utilnav utilnav-left">
    <a class="util-ask" href="contact.es.html" title="Enviar una pregunta">✉️ Preguntar</a>
  </div>
  <div class="utilnav utilnav-right">
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
  <details class="mobmenu">
    <summary>\U00002630 Menú</summary>
    <div class="mobmenu-panel">
      <a href="es.html"{cls('home')}>Inicio</a>
      <a href="biblioteca.html"{cls('biblioteca')}>Biblioteca</a>
      <div class="mobmenu-sep"></div>
      <a href="contact.es.html">\U00002709\U0000FE0F Preguntar</a>
      <div class="mobmenu-sep"></div>
      <a href="index.html">English</a>
      <a href="es.html" class="cur">Español</a>
      <div class="mobmenu-sep"></div>
      <span class="share-widget"></span>
    </div>
  </details>
  <nav class="topnav">
    <a href="es.html"{cls('home')}>Inicio</a>
    <a href="biblioteca.html"{cls('biblioteca')}>Biblioteca</a>
    {share_item}
  </nav>
</header>"""
    # "Ask a Question" (contact.html, submit yours) now sits on the LEFT, mirrored
    # from "Dear Mr. Librarian" + the language switch on the right -- on desktop
    # the two used to crowd together right next to the brand icon; splitting them
    # across both sides balances the header instead of bunching everything on one
    # side. "Ask a Question" and "Dear Mr. Librarian" (ask.html, browse answered
    # ones) are still a real pair conceptually -- every answered post links back to
    # the contact form as "send yours to the librarian's desk" -- that relationship
    # doesn't depend on them being pixel-adjacent.
    ask_on = " on" if active == "ask" else ""
    return f"""<header class="site-head">
  <div class="utilnav utilnav-left">
    <a class="util-ask" href="contact.html" title="Ask a question">✉️ Ask a Question</a>
  </div>
  <div class="utilnav utilnav-right">
    <a class="util-ask{ask_on}" href="ask.html" title="Reader questions, answered one at a time">\U0001F4D6 Dear Mr. Librarian</a>
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
  <details class="mobmenu">
    <summary>\U00002630 Menu</summary>
    <div class="mobmenu-panel">
      <a href="index.html"{cls('home')}>Home</a>
      <a href="toc.html"{cls('toc')}>Table of Contents</a>
      <a href="reading.html"{cls('reading')}>📗 My Reading</a>
      <a href="library.html"{cls('library')}>📚 Library</a>
      <a href="chronology.html"{cls('chronology')}>🕰 Chronology</a>
      <a href="about.html"{cls('about')}>About</a>
      <div class="mobmenu-sep"></div>
      <a href="contact.html">✉️ Ask a Question</a>
      <a href="ask.html"{cls('ask')}>\U0001F4D6 Dear Mr. Librarian</a>
      <div class="mobmenu-sep"></div>
      <a href="index.html" class="cur">English</a>
      <a href="es.html">Español</a>
      <div class="mobmenu-sep"></div>
      <span class="share-widget"></span>
    </div>
  </details>
  <nav class="topnav">
    <a href="index.html"{cls('home')}>Home</a>
    <a href="toc.html"{cls('toc')}>Table of Contents</a>
    <a href="reading.html"{cls('reading')}>📗 My Reading</a>
    <a href="library.html"{cls('library')}>📚 Library</a>
    <a href="chronology.html"{cls('chronology')}>🕰 Chronology</a>
    <a href="about.html"{cls('about')}>About</a>
    {share_item}
  </nav>
</header>"""


# The "N views" count moved here from the nav row (2026-07-27) -- it was competing
# for room in an already-busy nav, and it's a bit of trivia a reader checks at the
# end of a page, not something that belongs up top with the destinations. Sits as
# its own line at the very bottom-left, after the footer's other two paragraphs
# (which are already left-aligned by default -- .site-foot has no centering).
# Empty string (renders nothing) when GoatCounter isn't configured.
_FOOT_VIEWS_LINE = ('\n  <p class="foot-views"><span class="pageviews" id="pgviews"></span></p>'
                    if GOATCOUNTER_CODE else "")

FOOTER = f"""<footer class="site-foot">
  <p>The MisterLibrarian Bible Project — a fresh translation of the Bible into modern English, made from
  the original Hebrew and Greek (the Masoretic Text and the critical Greek text) one chapter at a time,
  with translator's notes comparing every choice against seven landmark versions. Kept by Mr. Librarian.</p>
  <p><a href="toc.html">Table of Contents</a> · <a href="reading.html">My Reading</a> · <a href="library.html">Library</a> · <a href="chronology.html">Chronology</a> · <a href="contact.html">Ask Mr. Librarian a question</a> · <a href="about.html">About the project</a></p>{_FOOT_VIEWS_LINE}
</footer>"""

# Spanish-locale footer — links only to what exists in Spanish, so a Spanish-only
# reader is never dropped into English. Grows as the Spanish edition is built out.
ES_FOOTER = f"""<footer class="site-foot">
  <p>La Traducción Mister — una nueva traducción de la Biblia al español, hecha desde el hebreo y el griego
  originales (el Texto Masorético y el texto crítico griego), capítulo por capítulo, con notas del traductor
  que comparan cada decisión con la Reina-Valera y otras versiones. Cuidada por Mr. Librarian. Esta edición está creciendo capítulo por capítulo.</p>
  <p><a href="es.html">Inicio</a> · <a href="index.html">English edition</a></p>{_FOOT_VIEWS_LINE}
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


def _og_tags(title, desc, url="", image="", og_type=None):
    """Open Graph + Twitter-card meta so a shared link unfurls with a title,
    description and image. canonical + og:url are emitted ONLY when the page's
    own url is given — a wrong canonical (defaulting to the homepage) is worse
    for SEO than none, so pages that don't pass a url simply omit it.

    og_type defaults to "article" whenever a url is given (chapter/dict/ency/
    atlas/ask-post pages really are articles) and "website" otherwise -- but a
    caller can override it explicitly. That matters once url= started being
    passed just to fix a missing canonical (2026-07-28): the homepage, TOC,
    dictionary/encyclopedia/concordance/atlas INDEXES, and similar hub pages
    now have canonicals but are not articles, so they pass og_type="website"
    to keep the social-preview type honest."""
    img = image or OG_IMAGE
    d = desc or ("A fresh translation of the Bible from the Hebrew and Greek, "
                 "verse by verse.")
    t = html.escape(title, quote=True)
    de = html.escape(d, quote=True)
    ogt = og_type or ("article" if url else "website")
    tags = [
        f'<meta property="og:site_name" content="Mister Translation"/>',
        f'<meta property="og:type" content="{ogt}"/>',
        f'<meta property="og:title" content="{t}"/>',
        f'<meta property="og:description" content="{de}"/>',
        f'<meta property="og:image" content="{img}"/>',
        f'<meta name="twitter:card" content="summary_large_image"/>',
        f'<meta name="twitter:title" content="{t}"/>',
        f'<meta name="twitter:description" content="{de}"/>',
        f'<meta name="twitter:image" content="{img}"/>',
    ]
    if url:
        # The home page answers at BOTH https://mistertranslation.com/ and
        # .../index.html. We used to declare .../index.html everywhere — canonical,
        # og:url, sitemap and nav all agreed on it — and Google OVERRODE us: it
        # indexed the bare directory form and filed /index.html under "Duplicate
        # without user-selected canonical" (GSC, confirmed 2026-08-01). That is
        # Google's documented preference for a site root, and arguing with it just
        # spends a sitemap entry to be told no. So declare what it already chose,
        # which is also the URL a person would type or share.
        full = f"{SITE_URL}/" if url == "index.html" else f"{SITE_URL}/{url}"
        tags.insert(0, f'<link rel="canonical" href="{full}"/>')
        tags.append(f'<meta property="og:url" content="{full}"/>')
    return "\n" + "\n".join(tags)


def _page_view_script(lang="en"):
    """Populates the '\U0001F441️ N views' line FOOTER/ES_FOOTER already emitted (as
    #pgviews, at the very bottom-left of the page -- moved out of the nav row
    2026-07-27, where it was competing for space). GoatCounter has been recording
    a per-path count since the sitewide script was added (_goatcounter_script) --
    this just displays it, no new tracking. Mirrors _stats_box()'s hard-won
    handling: fetch().then(r=>r.json())
    WITHOUT checking r.ok, because GoatCounter's counter endpoint returns HTTP 404
    for a thin/zero-hit path even when the JSON body is a perfectly valid
    {"count":"..."}. A brand-new page with no hits yet, or the fetch failing
    outright (network error, ad-blocker, GoatCounter unconfigured), just removes the
    item rather than showing a wrong or empty number.

    Wrapped in DOMContentLoaded (2026-07-27, paid for): this script tag is still
    emitted right after header(), but #pgviews now lives all the way down in the
    footer -- document.getElementById would run before the footer is even parsed
    and silently capture null, making the whole thing a permanent no-op (found
    live: the element existed, un-removed AND un-filled, because `el` was null
    from the start so neither the success nor the .catch() branch ever had
    anything to act on). Deferring the lookup to DOMContentLoaded means it runs
    after the whole document -- footer included -- is parsed, regardless of where
    in the page this <script> tag itself sits."""
    if not GOATCOUNTER_CODE:
        return ""
    label = "vistas" if lang == "es" else "views"
    return f"""<script>
document.addEventListener("DOMContentLoaded", function(){{
  var el = document.getElementById("pgviews");
  fetch("https://{GOATCOUNTER_CODE}.goatcounter.com/counter/" + encodeURIComponent(location.pathname) + ".json")
    .then(function(r){{ return r.json(); }})
    .then(function(d){{
      if (el && d && d.count) el.textContent = "\U0001F441️ " + d.count + " {label}";
      else if (el) el.remove();
    }})
    .catch(function(){{ if (el) el.remove(); }});
}});
</script>"""


def _chapter_jsonld(book, num, desc, url, lang="en", label=None):
    """Article + BreadcrumbList structured data for a chapter page.

    Added 2026-07-31. The site had no structured data at all. This is
    second-order next to the meta descriptions, but it is cheap, it gives search
    engines an explicit author/publisher/date and a Book > Chapter trail, and the
    breadcrumb is what produces the site-hierarchy line under a result instead of
    a bare URL. Deliberately minimal and honest: no fake ratings, no invented
    dates, nothing the page does not actually contain."""
    site = "https://mistertranslation.com/"
    def esc(x):
        return json.dumps(x, ensure_ascii=False)
    head = label or f"{book} {num}"
    if lang == "es":
        # The Spanish edition has no per-book index page, so its trail is two
        # levels deep, not three. Better an honest short breadcrumb than one
        # pointing at a URL that does not exist.
        crumbs = (
            f'{{"@type":"ListItem","position":1,"name":"La Traducci\u00f3n Mister",'
            f'"item":{esc(site + "es.html")}}},'
            f'{{"@type":"ListItem","position":2,"name":{esc(head)}}}')
    else:
        crumbs = (
            f'{{"@type":"ListItem","position":1,"name":"Table of Contents","item":{esc(site + "toc.html")}}},'
            f'{{"@type":"ListItem","position":2,"name":{esc(book)},"item":{esc(site + "book-" + book_slug(book) + ".html")}}},'
            f'{{"@type":"ListItem","position":3,"name":{esc(head)}}}')
    return (
        '\n<script type="application/ld+json">'
        '{"@context":"https://schema.org","@graph":['
        '{"@type":"Article",'
        f'"headline":{esc(head)},'
        f'"description":{esc(desc)},'
        f'"mainEntityOfPage":{esc(site + url)},'
        f'"isPartOf":{{"@type":"Book","name":{esc(book)}}},'
        f'"inLanguage":{esc(lang)},'
        '"author":{"@type":"Person","name":"Mr. Librarian"},'
        '"publisher":{"@type":"Organization","name":"The MisterLibrarian Bible Project",'
        f'"url":{esc(site)}}}}},'
        '{"@type":"BreadcrumbList","itemListElement":['
        + crumbs +
        ']}]}</script>'
    )


def _meta_desc(book, num, teaser, src, lang="en", label=None):
    """Front-load the CHAPTER'S OWN HOOK into the meta description.

    Search engines truncate descriptions around 155-160 characters. The old text
    opened with ~140 characters of boilerplate ("... translated fresh from the
    Hebrew, with verse-by-verse notes comparing NIV, KJV, Douay-Rheims, The Living
    Bible, the 1599 Geneva, ASV, and NWT") and only then appended the teaser --
    so the distinctive part, the only part that would earn a click, was cut off on
    every one of the 180+ chapter pages, and every description was identical for
    its first hundred-odd characters. Boilerplate descriptions are also the kind
    Google most often discards and rewrites.

    So: lead with the teaser, trimmed at a sentence boundary, and keep the
    provenance line only as a short tail when there is room. Added 2026-07-31.

    2026-08-01: extended to the Spanish twin, which had been left behind -- all
    130 es.html chapters shipped the SAME 178-character boilerplate, over the
    truncation limit and with no chapter-specific hook in it at all. Same
    treatment, Spanish lead and tail."""
    t = re.sub(r"<[^>]+>", "", teaser or "")
    t = (t.replace("\u26a0", "").replace("&mdash;", "\u2014").replace("&rsquo;", "\u2019")
          .replace("&ldquo;", "\u201c").replace("&rdquo;", "\u201d").replace("&laquo;", "\u00ab")
          .replace("&raquo;", "\u00bb").replace("&nbsp;", " "))
    t = re.sub(r"\s+", " ", t).strip()
    lead = f"{label or f'{book} {num}'}: "
    room = 158 - len(lead)
    if len(t) > room:
        cut = t[:room]
        # prefer a sentence end, then a clause end, then a word boundary
        for sep in (". ", "; ", " \u2014 ", ", "):
            i = cut.rfind(sep)
            if i > room * 0.45:
                cut = cut[:i]
                break
        else:
            i = cut.rfind(" ")
            if i > 0:
                cut = cut[:i]
        t = cut.rstrip(" ,;\u2014-") + "\u2026"
    out = lead + t
    if len(out) < 120:
        tail = (f" Traducci\u00f3n nueva desde {src}." if lang == "es"
                else f" Translated fresh from {src}.")
        if len(out) + len(tail) <= 155:
            out += tail
    return out


def page(title, body, active="", desc="", url="", image="", lang="en", base="", og_type=None):
    # Trim here, at the choke point. Descriptions were being hand-written at ~70
    # call sites and three of them (the book intros, the testament intros, the
    # "Dear Mr. Librarian" answers) ran to 200-400 characters, which Google cuts
    # mid-sentence. Trimming in page() means no call site can reintroduce it.
    # 2026-08-01.
    desc = _trim_desc(desc)
    d = f'\n<meta name="description" content="{html.escape(desc, quote=True)}"/>' if desc else ""
    og = _og_tags(title, desc, url, image, og_type)
    # `base` is only passed by pages that live inside a subdirectory (ency/, dict/) --
    # it lets every existing root-relative href in header()/FOOTER/body (style.css,
    # img/..., encyclopedia.html#slug, ...) resolve correctly without rewriting a
    # single one of them. Every other page omits it, so this is a no-op everywhere else.
    base_tag = f'\n<base href="{html.escape(base, quote=True)}"/>' if base else ""
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>{base_tag}
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{html.escape(title)}</title>{d}{og}
<link rel="icon" href="{FAVICON}"/>
<link rel="stylesheet" href="style.css?v={CSS_VER}"/>{_goatcounter_script()}
</head>
<body>
<div class="wrap">
{header(active, lang)}
{_page_view_script(lang)}
<script src="share.js?v={SHARE_JS_VER}" defer></script>
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


def osm_bbox_embed(lat_min, lat_max, lon_min, lon_max, label, caption=None, pad_frac=0.08):
    """A key-less OpenStreetMap embed framed to an explicit bounding box -- the
    real-map companion to a journey's schematic overview (osm_embed's sibling,
    which frames on a single point+span instead). No `marker` param: a route
    has several stops, not one, and the embed macro only supports one pin.
    `pad_frac` grows the box a little on every side so the edge stops aren't
    cropped flush against the frame."""
    lat_pad = (lat_max - lat_min) * pad_frac
    lon_pad = (lon_max - lon_min) * pad_frac
    bbox = (f"{lon_min - lon_pad:.4f},{lat_min - lat_pad:.4f},"
            f"{lon_max + lon_pad:.4f},{lat_max + lat_pad:.4f}")
    clat, clon = (lat_min + lat_max) / 2.0, (lon_min + lon_max) / 2.0
    view_url = f"https://www.openstreetmap.org/#map=6/{clat:.4f}/{clon:.4f}"
    cap_html = f'<div class="atlas-caption">{caption}</div>' if caption else ""
    return f"""<div class="mapembed">
  <div class="mapembed-frame">
    <iframe src="https://www.openstreetmap.org/export/embed.html?bbox={bbox}&layer=mapnik"
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
            entry = _SLUG_TO_ENTRY[slug]
            name = html.escape(entry["name"], quote=True)
            # A PLACE goes straight to its atlas page (description + refs +
            # the actual live map, in one hop) rather than the Encyclopedia's
            # lean index -- a reader mid-chapter who clicks "Ur" wants to see
            # where that is, not a one-line teaser two more clicks from the
            # map. Every place has an atlas page regardless of whether it's
            # mappable (an undetermined site still gets its note + refs), so
            # this is unconditional on kind, not on e.get("coords").
            # Non-place entries (people, crafts) are unaffected.
            if entry["kind"] == "place":
                return (f'<a class="eterm" href="atlas/{slug}.html" '
                        f'title="{name} — see the Atlas">{word}</a>')
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
                    "word, every verse, rebuilt as each chapter is added.", url="concordance.html",
               og_type="website")
    open(os.path.join(OUT, "concordance.html"), "w", encoding="utf-8").write(out)
    return len(words), total_refs


def _dict_card(slug, term, orig, translit, gloss, ref, permalink=True):
    """One dictionary entry's HTML block -- shared by dictionary.html (many cards,
    each keeping its id="slug" anchor so dictionary.html#slug stays live) and the
    entry's own standalone page (dict/<slug>.html). `permalink` mirrors _ency_card."""
    book, ch, v = _ref(ref)
    script_cls = "dgreek" if _is_nt(book) else "dheb"   # Greek renders LTR, Hebrew RTL
    perma = (f'<a href="dict/{slug}.html" style="font-size:11px;font-weight:400;opacity:.55" '
             f'title="Permalink — link directly to this entry">🔗 permalink</a>' if permalink else "")
    return f"""<div class="dentry" id="{slug}">
  <div class="dhead"><span class="dterm">{html.escape(term)}</span>
    <span class="{script_cls}">{orig}</span> <span class="dtr">{html.escape(translit)}</span> {perma}</div>
  <p>{gloss} <a class="dref" href="{verse_url(book, ch, v)}">→ first discussed at {book_abbr(book)} {ch}:{v}</a></p>
</div>"""


def _dict_index_row(slug, term, orig, translit, gloss, ref):
    """Lean clickable line for the dictionary INDEX page (dictionary.html) -- term
    + a short gloss teaser. Full entry (original script, transliteration, full
    gloss, first-discussed link) lives on dict/<slug>.html now. Keeps id="slug"
    so an already-shared dictionary.html#slug link still lands close to the term."""
    teaser = _plain(gloss)
    if len(teaser) > 110:
        teaser = teaser[:107].rsplit(" ", 1)[0].rstrip(",;:—") + "…"
    return (f'<a class="eirow" id="{slug}" href="dict/{slug}.html">'
            f'<span class="ei-name">{html.escape(term)}</span>'
            f'<span class="ei-teaser">{html.escape(teaser)}</span></a>')


def build_dictionary():
    entries = sorted(DICTIONARY, key=lambda e: e[1].lower())
    items = [_dict_index_row(*e) for e in entries]
    body = f"""<h1 class="pagetitle">📖 Dictionary</h1>
<p class="lede">The original-language words this translation has met so far — Hebrew for the Tanakh, Greek for
the New Testament — <strong>{len(entries)} terms</strong>. Click a term for its full entry — original script,
transliteration, gloss, and a link back to the chapter that first discussed it.</p>
<div class="panel eilist">
{''.join(items)}
</div>"""
    out = page(f"Dictionary — {SITE_NAME}", body, active="library",
               desc="A growing dictionary of the Hebrew terms behind the MisterLibrarian translation, "
                    "added chapter by chapter.", url="dictionary.html", og_type="website")
    open(os.path.join(OUT, "dictionary.html"), "w", encoding="utf-8").write(out)
    return len(entries)



# --- entry images -----------------------------------------------------------
# Michael asked to start hosting images (2026-07-25), specifically "a photo of a
# statue of Baal", with a hard constraint: "we don't wanna pay anything... we have
# to follow those rules for where we find something."
#
# ⚠ TWO THINGS THAT ARE NOT OBVIOUS:
#
# 1. WHERE THE FILE LIVES. The published copy must be committed to THIS repo,
#    because GitHub Pages can only serve what it hosts — our S3 bucket is private,
#    so a browser cannot load an image from it. The ORIGINAL goes to S3 for
#    archival. That is exactly the split tools/travel_archive.py already uses, and
#    the same live-in-git / durable-in-S3 pattern as the rest of Michael's records.
#
# 2. LICENSING IS ENFORCED, NOT TRUSTED. _entry_image_html REFUSES to render an
#    image that is missing its license, credit or source, so an unlicensed file
#    cannot reach the site by being added carelessly later. We credit even
#    public-domain photographs whose licence requires no attribution — it costs a
#    line and it is the same habit as showing a reading's pedigree.
#
# A 3-D object like a stele is the case to be careful about: the ARTEFACT is
# thousands of years old and out of copyright, but the PHOTOGRAPH of it carries its
# own fresh copyright, so the photographer's licence is the one that matters.
_IMG_REQUIRED = ("file", "alt", "credit", "license", "source_url")


def _entry_image_html(img, lang="en"):
    missing = [k for k in _IMG_REQUIRED if not img.get(k)]
    if missing:
        raise SystemExit(f"entry image {img.get('file', '?')!r} is missing {missing} — "
                         f"every image must carry its licence, credit and source before "
                         f"it can be published")
    path = f"img/ency/{img['file']}"
    if not os.path.isfile(os.path.join(OUT, path)):
        raise SystemExit(f"entry image {path} is referenced but not in the repo — "
                         f"GitHub Pages can only serve committed files")
    es = lang == "es"
    cap = img.get("caption_es") if es else img.get("caption")
    # A Spanish page must not carry an English credit line — same rule as every
    # other Spanish surface here. Falls back to the English string only if no
    # Spanish one was supplied, which is visible rather than silent.
    lic_txt = (img.get("license_es") or img["license"]) if es else img["license"]
    credit_txt = (img.get("credit_es") or img["credit"]) if es else img["credit"]
    lic = html.escape(lic_txt)
    if img.get("license_url"):
        lic = f'<a href="{html.escape(img["license_url"], quote=True)}" rel="noopener">{lic}</a>'
    word = "Foto" if es else "Photo"
    via = "vía" if es else "via"
    credit = (f'{word}: {html.escape(credit_txt)} · {lic} · '
              f'{via} <a href="{html.escape(img["source_url"], quote=True)}" rel="noopener">'
              f'{html.escape(img.get("source_name", "Wikimedia Commons"))}</a>')
    capline = f'<div class="eimg-cap">{cap}</div>' if cap else ""
    return f"""<figure class="eimg" style="margin:10px 0;padding:0">
  <img src="{path}" alt="{html.escape(img['alt'], quote=True)}" loading="lazy"
       style="max-width:100%;height:auto;border-radius:6px;display:block"/>
  {capline}
  <figcaption class="eimg-credit" style="font-size:11.5px;opacity:.72;margin-top:5px">{credit}</figcaption>
</figure>"""


def _entry_images_html(e, lang="en"):
    return "".join(_entry_image_html(i, lang) for i in (e.get("images") or []))


def _ency_card(e, permalink=True):
    """One encyclopedia entry's HTML block -- shared by encyclopedia.html (many
    cards on one page, each keeping its id="slug" anchor so an already-shared
    encyclopedia.html#slug link keeps working) and the entry's own standalone
    page (ency/<slug>.html, one card alone). `permalink` prints a small share
    link to that standalone page; the entry's own page passes False, since
    linking a page to itself is pointless."""
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
        maplink = (f'<div class="emap"><a href="atlas/{e["slug"]}.html">{label} →</a></div>')
    perma = (f'<a href="ency/{e["slug"]}.html" style="font-size:11px;font-weight:400;opacity:.55;'
              f'margin-left:8px" title="Permalink — link directly to this entry">🔗 permalink</a>'
             if permalink else "")
    return f"""<div class="eentry" id="{e['slug']}">
  <div class="ehead">{html.escape(e['name'])}{perma}</div>
  <p>{e['desc']}</p>
  {_entry_images_html(e)}
  <div class="erefs"><span class="xr-label">in the text</span> {refs}</div>
  {maplink}
  {vids}
</div>"""


def _ency_index_row(e):
    """One lean, clickable line for the encyclopedia INDEX page (encyclopedia.html)
    -- name + a short teaser, linking straight to ency/<slug>.html where the full
    entry (description/images/refs/map link/videos) actually lives now. Keeps the
    entry's `id="slug"` anchor so an already-shared encyclopedia.html#slug link
    still lands on (a leaner version of) the right spot."""
    teaser = _plain(e["desc"])
    if len(teaser) > 130:
        teaser = teaser[:127].rsplit(" ", 1)[0].rstrip(",;:—") + "…"
    return (f'<a class="eirow" id="{e["slug"]}" href="ency/{e["slug"]}.html">'
            f'<span class="ei-name">{html.escape(e["name"])}</span>'
            f'<span class="ei-teaser">{html.escape(teaser)}</span></a>')


def build_encyclopedia():
    places = [e for e in ENCYCLOPEDIA if e["kind"] == "place"]
    people = [e for e in ENCYCLOPEDIA if e["kind"] in ("person", "people")]
    # A third bucket for the things the text keeps reaching for that are neither
    # a person nor a place — a craft, a trade, an object. The potter of Jeremiah
    # 18 is the first: the metaphor only lands once you know how the job was
    # actually done, and that belongs in prose with the verses attached, not in
    # a one-line dictionary gloss. Anything whose kind is not place/person/
    # people/craft would be silently dropped from every section, so the build
    # refuses it rather than letting an entry go invisible.
    things = [e for e in ENCYCLOPEDIA if e["kind"] in ("craft", "thing")]
    _known = {"place", "person", "people", "craft", "thing"}
    stray = sorted({e["kind"] for e in ENCYCLOPEDIA} - _known)
    if stray:
        raise SystemExit(f"encyclopedia: unknown kind(s) {stray} would render nowhere — "
                         f"add a section in build_encyclopedia() or fix the entry")

    def render(entries):
        return "".join(_ency_index_row(e) for e in sorted(entries, key=lambda x: x["name"].lower()))

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

    things_section = ""
    if things:
        things_section = f"""<h2>Crafts &amp; Trades</h2>
<p class="lede">The work of ordinary hands — the jobs the prophets and poets reach for when they want
to say something about God. These entries explain how the craft was actually done, because that is
usually where the metaphor's force is hiding.</p>
<div class="panel eilist">{render(things)}</div>"""

    counts = f"<strong>{len(places)} places, {len(people)} people</strong>"
    if things:
        _c = "craft" if len(things) == 1 else "crafts"
        counts = f"<strong>{len(places)} places, {len(people)} people, {len(things)} {_c}</strong>"

    body = f"""<h1 class="pagetitle">🏺 Encyclopedia</h1>
<p class="lede">The people and places the translation has reached — {counts}. Click a name for the full
entry — description, every verse it appears in, and (for places) a growing film shelf of archaeology
and geography footage from Expedition Bible.</p>

<h2>Places</h2>
<div class="panel eilist">{render(places)}</div>

<h2>People</h2>
<div class="panel eilist">{render(people)}</div>

{things_section}

{queue_section}"""
    out = page(f"Encyclopedia — {SITE_NAME}", body, active="library",
               desc="People and places of the MisterLibrarian translation — every entry verse-linked, "
                    "with embedded archaeology videos credited to Expedition Bible.", url="encyclopedia.html",
               og_type="website")
    open(os.path.join(OUT, "encyclopedia.html"), "w", encoding="utf-8").write(out)
    return len(places), len(people), len(things)


def build_encyclopedia_entry_pages():
    """One standalone, shareable page per encyclopedia entry: ency/<slug>.html.

    Purely additive. encyclopedia.html still carries every entry in full, each
    still at its id="slug" anchor -- an already-shared encyclopedia.html#slug
    link keeps working exactly as before. This just gives each entry a page of
    its OWN, with its own title/description/OG image, so pasting the link into
    iMessage/Slack/X unfurls with that entry's name and blurb instead of the
    whole Encyclopedia's -- and gives it a URL worth sharing in the first place.
    """
    outdir = os.path.join(OUT, "ency")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for e in ENCYCLOPEDIA:
        img = (e.get("images") or [None])[0]
        og_image = f"{SITE_URL}/img/ency/{img['file']}" if img else ""
        body = f"""<p style="font-size:12px;opacity:.6;margin:0 0 12px">
  <a href="encyclopedia.html">🏺 Encyclopedia</a></p>
{_ency_card(e, permalink=False)}"""
        out = page(f"{e['name']} — Encyclopedia — {SITE_NAME_SHORT}", body, active="library",
                   desc=_entry_desc(e['name'], e['desc']), url=f"ency/{e['slug']}.html", image=og_image,
                   base=f"{SITE_URL}/")
        open(os.path.join(outdir, f"{e['slug']}.html"), "w", encoding="utf-8").write(out)
        n += 1
    return n


def build_dictionary_entry_pages():
    """One standalone, shareable page per dictionary entry: dict/<slug>.html.
    Purely additive -- see build_encyclopedia_entry_pages()'s docstring; the
    same reasoning applies here, with dictionary.html in place of encyclopedia.html."""
    outdir = os.path.join(OUT, "dict")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for slug, term, orig, translit, gloss, ref in DICTIONARY:
        body = f"""<p style="font-size:12px;opacity:.6;margin:0 0 12px">
  <a href="dictionary.html">📖 Dictionary</a></p>
{_dict_card(slug, term, orig, translit, gloss, ref, permalink=False)}"""
        out = page(f"{term} — Dictionary — {SITE_NAME_SHORT}", body, active="library",
                   desc=_entry_desc(term, gloss), url=f"dict/{slug}.html", base=f"{SITE_URL}/")
        open(os.path.join(outdir, f"{slug}.html"), "w", encoding="utf-8").write(out)
        n += 1
    return n


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
# The Euphrates, from its Raqqa-area bend (the Balikh confluence -- also a `via`
# point on Abram's route, see ROUTES) down through Deir ez-Zor and along the
# Syria/Iraq border, past Ramadi and Fallujah, by Babylon, and on down toward Ur.
# A journey up this river is the only way to get from southern Mesopotamia to
# Haran without crossing open desert, and it is why the Ur-to-Haran leg of
# Abram's migration bends northwest before it ever turns toward Canaan --
# without the river drawn in, that bend looks arbitrary. Hand-simplified like
# every other polyline here, not survey-grade.
_EUPHRATES = [(35.95, 39.02), (35.34, 40.15), (34.45, 40.92), (33.85, 42.20),
              (33.42, 43.30), (33.35, 43.77), (32.90, 44.10), (32.5422, 44.4208),
              (32.00, 44.93), (31.32, 45.28), (30.9626, 46.1035)]


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


def _basemap_fragments(proj, visible, inframe, clear):
    """The Levant + Egypt basemap fragments that don't move: coastlines, the
    rift-valley water bodies, and the rivers (Jordan, Euphrates, the Nile and
    its two surviving branches) -- each drawn only if some point of it is
    actually `visible` in the current frame, with its label additionally
    gated on `clear` (the CALLER's own label-priority reservation) so a
    lower-priority basemap label yields to whatever the caller has already
    reserved (a region's named sites; a route's numbered stops) rather than
    overlapping it. The graticule and every FOREGROUND layer (a territory's
    dashed boundary; a journey's dashed route + stops) stay with the caller,
    since those differ per map -- this is only the shared backdrop.

    Shared by render_region_map (a territory's fixed backdrop) and
    render_route_panel (a journey's) so a map crossing real geography always
    orients on the same ground -- and so a future route through Egypt (the
    Exodus) gets the Nile for free instead of needing its own copy of this."""
    parts = []
    if visible(_EGYPT_COAST):
        parts.append(f'<path d="{_path(proj, _EGYPT_COAST)}" class="reg-coast"/>')
    if visible(_COAST):
        parts.append(f'<path d="{_path(proj, _COAST)}" class="reg-coast"/>')
        clat, clon = _COAST[len(_COAST) // 2]
        if inframe(clat, clon):
            cx, cy = proj(clat, clon)
            if clear(cx - 40, cy, 64):
                parts.append(f'<text x="{cx-8:.1f}" y="{cy:.1f}" class="reg-sea" text-anchor="end">Great Sea</text>')
    for poly, label, anchor in ((_DEAD_SEA, "Salt Sea", (31.40, 35.48)),
                                (_AQABA, "Gulf of Aqaba", (28.55, 34.62)),
                                (_BITTER_LAKES, "Bitter Lakes", (30.18, 32.40)),
                                (_GALILEE, None, None)):
        if visible(poly):
            parts.append(f'<path d="{_path(proj, poly, close=True)}" class="reg-water"/>')
            if label and inframe(*anchor):
                lx, ly = proj(*anchor)
                if clear(lx, ly, len(label) * 5.6):
                    parts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="reg-sea" text-anchor="middle">{label}</text>')
    for line, label in ((_JORDAN, "the Jordan"), (_ARABAH, "the Arabah"),
                        (_EUPHRATES, "the Euphrates"),
                        (_NILE, "the Nile"), (_NILE_ROSETTA, None), (_NILE_DAMIETTA, None)):
        if visible(line):
            parts.append(f'<path d="{_path(proj, line)}" class="reg-river"/>')
            mlat, mlon = line[len(line) // 2]
            if label and inframe(mlat, mlon):
                mx, my = proj(mlat, mlon)
                if clear(mx + 6, my, len(label) * 5.6):
                    parts.append(f'<text x="{mx+6:.1f}" y="{my:.1f}" class="reg-rlab">{label}</text>')
    return "".join(parts)


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

    # basemap: the things that don't move (shared with render_route_panel)
    parts.append(_basemap_fragments(proj, visible, inframe, clear))

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
    external tiles: real lat/lon projected onto the SAME fixed basemap the
    territory maps use (coastline, the Jordan and Euphrates traced as real
    paths, not just labels dropped in empty space), a dashed route line,
    numbered PRIMARY stops labeled directly by name, small `via` bend-points
    that curve the line to the rivers, a faint degree graticule, a compass,
    and a supporting legend with each stop's note and verse ref.

    Without a real basemap this used to be a bare coordinate grid with two
    river names floating at arbitrary points -- geographically accurate
    (real lat/lon) but unreadable as a MAP (nothing to orient by, and the
    numbered dots meant nothing without reading the legend below). This
    reuses `render_region_map`'s basemap fragments and priority-reservation
    pattern (stops matter more than river/sea labels, so those degrade first
    on collision) so a journey drawn across real geography looks like one."""
    stops = route["stops"]
    proj, W, H, (lat_min, lat_max, lon_min, lon_max) = _route_geo(stops)

    def visible(pts):
        return any(lat_min <= a <= lat_max and lon_min <= b <= lon_max for a, b in pts)

    def inframe(lat, lon):
        return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

    # A journey can sweep a much wider longitude range than a single territory
    # (Ur to Shechem is ~11°), so label every OTHER degree once the frame gets
    # that wide -- labeling every one would just crowd the bottom edge.
    lon_step = 2 if (lon_max - lon_min) > 6 else 1
    grid = []
    for lon in range(int(math.ceil(lon_min)), int(math.floor(lon_max)) + 1):
        x, _ = proj(lat_max, lon)
        grid.append(f'<line x1="{x:.1f}" y1="0" x2="{x:.1f}" y2="{H:.1f}" class="rg-grid"/>')
        if lon % lon_step == 0:
            grid.append(f'<text x="{x:.1f}" y="{H-5:.1f}" class="rg-tick" text-anchor="middle">{lon}°E</text>')
    for lat in range(int(math.ceil(lat_min)), int(math.floor(lat_max)) + 1):
        _, y = proj(lat, lon_min)
        grid.append(f'<line x1="0" y1="{y:.1f}" x2="{W:.1f}" y2="{y:.1f}" class="rg-grid"/>')
        grid.append(f'<text x="5" y="{y-3:.1f}" class="rg-tick">{lat}°N</text>')

    pts = [proj(s["coord"][0], s["coord"][1]) for s in stops]
    d = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in pts)

    # Reserve every stop's dot AND its prospective name label FIRST -- the
    # stops are the most important thing on this map, so the basemap's own
    # labels (rivers, the coast) below have to give way to them, never the
    # reverse (see render_region_map's identical site-labels-first rule).
    reserved = []
    for s, (x, y) in zip(stops, pts):
        w = 22.0 if s.get("via") else 30.0 + len(s.get("name", "")) * 6.2
        reserved.append((x - w / 2.0, x + w / 2.0, y))

    def clear(x, y, w=0.0, ry=13.0):
        lo, hi = x - w / 2.0, x + w / 2.0
        return all(hi < sx - 6 or lo > ex + 6 or abs(y - sy) > ry
                   for sx, ex, sy in reserved)

    # basemap: the real, fixed geography this route actually crosses. Drawn
    # UNDER the dashed route line, exactly like a territory map's coastline --
    # same shared fragments render_region_map uses, so a future route through
    # Egypt (the Exodus) gets the Nile without needing its own copy of this.
    basemap = _basemap_fragments(proj, visible, inframe, clear)

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
        # The name goes right on the map next to its dot -- a reader
        # shouldn't have to cross-reference a numbered legend just to know
        # what "3" is. Labels near the right edge flip to the left so they
        # never run off the canvas (same rule the inset uses for the Jordan).
        label_left = x > W * 0.82
        anchor_attr = ' text-anchor="end"' if label_left else ""
        lx = x - 16 if label_left else x + 16
        marks.append(f'<text x="{lx:.1f}" y="{y+3.6:.1f}" class="rg-ilbl"{anchor_attr}>'
                     f'{html.escape(s["name"])}</text>')
        name = html.escape(s["name"])
        if s.get("slug"):
            name = f'<a href="atlas/{s["slug"]}.html">{name}</a>'
        ref = ""
        if s.get("ref"):
            c, v = s["ref"]
            ref = f' <a class="route-ref" href="{verse_url("Genesis", c, v)}">Gen {c}:{v}</a>'
        note = f' — {html.escape(s["note"])}' if s.get("note") else ""
        legend.append(f'<li><span class="route-num">{n}</span>'
                      f'<span><strong>{name}</strong>{note}{ref}</span></li>')

    compass = (f'<g transform="translate({W-24:.0f},26)">'
               f'<line x1="0" y1="9" x2="0" y2="-7" class="rg-comp"/>'
               f'<path d="M0,-11 L3.5,-4 L-3.5,-4 Z" class="rg-compf"/>'
               f'<text x="0" y="-13" class="rg-cn" text-anchor="middle">N</text></g>')

    svg = (f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" '
           f'aria-label="Route map: {html.escape(route["title"])}" xmlns="http://www.w3.org/2000/svg">'
           f'<title>{html.escape(route["title"])}</title>'
           f'{"".join(grid)}{basemap}'
           f'<path d="{d}" class="rg-under"/><path d="{d}" class="rg-line"/>'
           f'{"".join(via)}{"".join(marks)}{compass}</svg>')

    # The real-place companion: the schematic carries the numbered-stop story
    # (notes, verse refs) a real map can't show; a real map carries actual
    # terrain/place-names/scale the schematic -- a hand-drawn illustration --
    # never will. Framed to the whole route's extent, not one point.
    real_caption = (f'🌍 <strong>{html.escape(route["title"])}</strong> — the real ground this '
                    f'route crosses (not a pin on any one stop — the whole journey\'s extent)')
    real_map = osm_bbox_embed(lat_min, lat_max, lon_min, lon_max, route["title"], caption=real_caption)

    return (f'<section class="route-panel" id="route-{route["slug"]}">'
            f'<h2>🧭 {html.escape(route["title"])}</h2>'
            f'<div class="route-sub">{html.escape(route["chapters"])} · the journey at a glance</div>'
            f'<p class="route-blurb">{route["blurb"]}</p>'
            f'<div class="route-map">{svg}</div>'
            f'<div class="route-realmap-h">🌍 The real place <span>live map, OpenStreetMap</span></div>'
            f'<div class="route-realmap">{real_map}</div>'
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


def _atlas_card(e, permalink=True):
    """One place's COMPLETE atlas content -- description, images, verse refs,
    videos, the live map (+ territory-boundary overlay when the place is a
    REGION, not a point), and the ancient-world-overlay placeholder.

    This carries everything the Encyclopedia's own card has (images/videos)
    PLUS the actual embedded map the Encyclopedia only links out to, so a
    reader who reaches a place through EITHER an in-text mention (which now
    goes straight here -- see inject_encyclopedia_links) or the Encyclopedia
    entry gets the same complete page, not two different partial ones.
    Shared by the standalone page (atlas/<slug>.html, one place alone) and
    formerly by atlas.html's per-chapter listing (now a lean link list
    instead -- see build_atlas())."""
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
        reg = _REGION_BY_SLUG.get(e["slug"])
        if reg:
            badge = ' <span class="atlas-territory">territory</span>' + badge
            map_html = render_region_map(reg, others=REGIONS) + map_html
    else:
        badge = ""
        map_html = ('<div class="atlas-nomap">📍 No fixed point plotted — the location is genuinely '
                    "undetermined (see the note above), so this shows no guessed pin.</div>")
    if e.get("videos"):
        vids = "".join(youtube_embed(u, t) for t, u in e["videos"])
    else:
        vids = ('<div class="evids-empty">▶ No films on the shelf yet — archaeology and '
                'geography videos get added here as Mr. Librarian finds good ones.</div>')
    perma = (f'<a href="atlas/{e["slug"]}.html" style="font-size:11px;font-weight:400;opacity:.55;'
              f'margin-left:8px" title="Permalink — link directly to this place">🔗 permalink</a>'
             if permalink else "")
    return f"""<div class="atlas-place" id="atlas-{e['slug']}">
  <div class="atlas-place-h"><a href="ency/{e['slug']}.html">{html.escape(e['name'])}</a>{badge}{perma}</div>
  <p>{e['desc']}</p>
  {_entry_images_html(e)}
  <div class="erefs"><span class="xr-label">in the text</span> {refs}</div>
  {map_html}
  <div class="atlas-overlay-empty">🗺️ No ancient-world overlay on the shelf yet for this site — a period map
  showing how the region actually looked in the biblical world gets added here as Mr. Librarian curates one,
  the same way the encyclopedia's film shelf grows.</div>
  {vids}
</div>"""


def _route_index_row(route):
    """One lean, clickable card for a Journey on the Atlas index -- title, a
    trimmed teaser, and the stop count, linking to the full map+legend on its
    own page (routes/<slug>.html). Mirrors _ency_index_row's reasoning: full
    content moves OUT of the index so it never grows as more journeys (the
    Exodus, the wilderness years, Paul's missionary journeys) get added --
    the same reason encyclopedia.html stopped carrying every full entry."""
    teaser = _plain(route["blurb"])
    if len(teaser) > 170:
        teaser = teaser[:167].rsplit(" ", 1)[0].rstrip(",;:—") + "…"
    n_stops = sum(1 for s in route["stops"] if not s.get("via"))
    # Reuses the site's existing generic .card/.cardgrid (build_library's card
    # language) rather than inventing a parallel set of classes for one more
    # kind of teaser card.
    return (f'<a class="card" href="routes/{route["slug"]}.html">'
            f'<div class="card-t">🧭 {html.escape(route["title"])}</div>'
            f'<div class="card-d"><strong>{html.escape(route["chapters"])} · {n_stops} stops</strong><br>'
            f'{html.escape(teaser)}</div></a>')


def _atlas_index_row(e):
    """One lean, clickable line for the Atlas' alphabetical gazetteer -- name +
    a short teaser + a mapped/unmapped pin, linking to atlas/<slug>.html where
    the full entry (map, description, refs, videos) lives. This is the ONE
    place a place's `id="atlas-slug"` anchor is printed (a place can legitimately
    appear in many chapters' sections below, but a gazetteer lists it once)."""
    teaser = _plain(e["desc"])
    if len(teaser) > 130:
        teaser = teaser[:127].rsplit(" ", 1)[0].rstrip(",;:—") + "…"
    pin = "📍" if e.get("coords") else "❓"
    return (f'<a class="eirow" id="atlas-{e["slug"]}" href="atlas/{e["slug"]}.html">'
            f'<span class="ei-name">{pin} {html.escape(e["name"])}</span>'
            f'<span class="ei-teaser">{html.escape(teaser)}</span></a>')


def build_atlas():
    """One INDEX page, THREE ways to reach every mapped place -- following how
    real print Bible atlases (Zondervan, Holman, Carta) are actually organized:
    they lead with a sequence of big narrative/era maps (Patriarchal Age,
    Exodus, the Conquest, Paul's journeys...), then carry an alphabetical
    GAZETTEER, usually at the back, for looking a name up once you already
    know it. Neither of those is "by chapter" -- that third mode is unique to
    a chapter-by-chapter translation project, so it's kept, just last:

    1. Journeys -- a lean teaser card per multi-stop trip (Abram's migration
       today; more as the translation reaches them), linking to its own full
       map+legend on routes/<slug>.html.
    2. Places, A-Z -- the gazetteer, one lean row per place.
    3. Browse by Chapter -- "what's mapped in the chapter I'm reading", so a
       chapter's own 🗺️ Atlas toggle can jump straight to its section.

    A place's full content (description, images, refs, live map, videos) lives
    on its own standalone page (atlas/<slug>.html, see
    build_atlas_entry_pages()); every section here is a lean list of links.
    Its `id="atlas-slug"` anchor -- so an already-shared atlas.html#atlas-seir
    link still works -- is printed ONCE now, on its A-Z row (two elements
    sharing one id is invalid HTML, which the old per-chapter-mention version
    had to work around with a seen_ids set; the gazetteer needs no such thing,
    since a place is listed there exactly once).
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
            rows = []
            for pslug, _first_v in entries:
                e = _SLUG_TO_ENTRY[pslug]
                pin = "📍" if e.get("coords") else "❓"
                rows.append(f'<a class="atlas-item" href="atlas/{pslug}.html">'
                            f'{pin} {html.escape(e["name"])}</a>')
            body_html = f'<div class="atlas-items">{"".join(rows)}</div>'
        else:
            body_html = '<div class="atlas-empty">No places are named in this chapter yet — nothing to map.</div>'
        sections.append(f"""<div class="atlas-chapter" id="{book_slug(book)}-{num}">
  <div class="atlas-chhead"><a href="{chapter_filename(book, num)}">{book} {num}</a>
    <span class="atlas-chteaser">{html.escape(teaser)}</span></div>
  {body_html}
</div>""")

    routes_html = "".join(_route_index_row(r) for r in ROUTES)
    gazetteer_html = "".join(_atlas_index_row(e) for e in sorted(places, key=lambda x: x["name"].lower()))

    body = f"""<h1 class="pagetitle">🗺️ Atlas</h1>
<p class="lede">Every place the translation has named so far — <strong>{n_mapped} of {len(places)}
places</strong> located on a live map (a handful are genuinely debated or unidentified, and say so
rather than guess a pin). Where Expedition Bible's Joel Kramer stakes out a specific site — Eden and
Havilah via the Pishon, Sodom and Gomorrah at Tall el-Hammam — that identification is the one plotted,
credited in the place's own note.</p>

<h2>🧭 Journeys</h2>
<p class="lede">The big multi-stop trips the story covers, start to finish — the way a printed atlas
leads with its narrative maps before the alphabetical index at the back.</p>
<div class="cardgrid">{routes_html}</div>

<h2>Places, A–Z</h2>
<p class="lede">Click a name for its full entry — description, verse links, and a live map.</p>
<div class="panel eilist">{gazetteer_html}</div>

<h2>Browse by Chapter</h2>
<p class="lede">Jump here straight from any chapter's own 🗺️ Atlas toggle, or browse chapter by chapter.</p>
{''.join(sections)}"""
    out = page(f"Atlas — {SITE_NAME}", body, active="library",
               desc="An atlas of the MisterLibrarian Bible Project — the big journeys mapped in full, "
                    "every named place in an A-Z gazetteer, and a chapter-by-chapter browse.", url="atlas.html",
               og_type="website")
    open(os.path.join(OUT, "atlas.html"), "w", encoding="utf-8").write(out)
    return n_mapped, len(places)


def build_atlas_entry_pages():
    """One standalone, shareable page per mapped place: atlas/<slug>.html. Purely
    additive in spirit -- see build_encyclopedia_entry_pages()'s docstring; the
    place's `atlas-<slug>` anchor on atlas.html (see build_atlas()) still works
    for an already-shared link, this just gives it a real page of its own too."""
    outdir = os.path.join(OUT, "atlas")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for e in ENCYCLOPEDIA:
        if e["kind"] != "place":
            continue
        img = (e.get("images") or [None])[0]
        og_image = f"{SITE_URL}/img/ency/{img['file']}" if img else ""
        body = f"""<p style="font-size:12px;opacity:.6;margin:0 0 12px">
  <a href="atlas.html">🗺️ Atlas</a></p>
{_atlas_card(e, permalink=False)}"""
        out = page(f"{e['name']} — Atlas — {SITE_NAME_SHORT}", body, active="library",
                   desc=_entry_desc(e['name'], e['desc']), url=f"atlas/{e['slug']}.html", image=og_image,
                   base=f"{SITE_URL}/")
        open(os.path.join(outdir, f"{e['slug']}.html"), "w", encoding="utf-8").write(out)
        n += 1
    return n


def build_route_pages():
    """One standalone, shareable page per Journey: routes/<slug>.html. Same
    reasoning as build_encyclopedia_entry_pages() -- a shareable URL with its
    own title/OG description, and (as more journeys are added -- the Exodus,
    the wilderness years, Paul's missionary journeys) an atlas.html that stays
    a lean index of teaser cards instead of inlining every journey's full map
    and legend on one ever-growing page."""
    outdir = os.path.join(OUT, "routes")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for r in ROUTES:
        body = f"""<p style="font-size:12px;opacity:.6;margin:0 0 12px">
  <a href="atlas.html">🗺️ Atlas</a></p>
{render_route_panel(r)}"""
        out = page(f"{r['title']} — Atlas — {SITE_NAME_SHORT}", body, active="library",
                   desc=_entry_desc(r['title'], r["blurb"]), url=f"routes/{r['slug']}.html", base=f"{SITE_URL}/")
        open(os.path.join(outdir, f"{r['slug']}.html"), "w", encoding="utf-8").write(out)
        n += 1
    return n


def build_library(stats):
    n_words, n_refs, n_dict, n_places, n_people, n_things, n_xrefs, n_mapped, n_atlas_places = stats
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
  <div class="card-d">{n_places} places · {n_people} people · {n_things} {'craft' if n_things == 1 else 'crafts'} — verse-linked
  entries, with a film shelf on every place for archaeology &amp; geography videos.</div></a>
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
                    "encyclopedia, and cross-references — all growing with the translation.", url="library.html",
               og_type="website")
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
    else:
        # At the last SHIPPED chapter, point "coming soon" at the chapter the book is
        # actually next in line for. If the previous chapter is also shipped we are on
        # a live sequential run, so num+1 is right (Jeremiah 22->23->24). Otherwise the
        # chapter was translated out of order (Psalms 1, then 23) and num+1 would
        # promise a chapter nobody is heading for -- so point at the lowest unpublished
        # one, where the sequence really resumes.
        #
        # 2026-07-31: this used to be gated on `num < BOOK_TOTAL`, which silently
        # dropped the pointer whenever the last SHIPPED chapter was also the book's
        # LAST chapter -- Proverbs 1 + 31 left Proverbs 31 with no forward pointer at
        # all while 29 chapters were still unwritten, and the info-block on the page
        # claimed the nav pointed at Proverbs 2. A book is only finished when nothing
        # is missing, so test that instead.
        total = BOOK_TOTAL.get(book, num)
        missing = [c for c in range(1, total + 1) if c not in same]
        if not missing:
            next_html = ""
        else:
            nxt = num + 1 if ((num - 1) in same and num < total) else missing[0]
            next_html = f'<span class="dis">{book} {nxt} (coming soon)</span>'
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


def _trim_desc(t, limit=158):
    """Trim a description to `limit` characters at the nearest sentence, clause or
    word boundary, appending an ellipsis if anything was cut. Shared by page() and
    _entry_desc() so there is exactly one definition of 'too long' on the site."""
    t = re.sub(r"\s+", " ", t or "").strip()
    if len(t) <= limit:
        return t
    cut = t[:limit]
    for sep in (". ", "; ", " \u2014 ", ", "):
        i = cut.rfind(sep)
        if i > limit * 0.45:
            return cut[:i].rstrip(" ,;\u2014-") + "\u2026"
    i = cut.rfind(" ")
    return (cut[:i] if i > 0 else cut).rstrip(" ,;\u2014-") + "\u2026"


SITE_NAME_SHORT = "Mister Translation"   # already the brand on verse-stub pages


def _entry_desc(label, prose, lang="en"):
    """Search-facing description for a LIBRARY ENTRY page (dict/ency/atlas).

    These pages were passing the entry's whole gloss to `desc=`. That is not a
    description, it is an essay: dict/tzeakah shipped 860 characters, taarog 530,
    niflaot 350, against a truncation limit of about 155. Google cut every one of
    them mid-sentence, and Search Console showed these exact pages ranking in the
    top ten with a click-through rate of zero.

    Added 2026-08-01, from the site's first week of real GSC data. 28 of the 54
    pages ranking at position <= 10 are dictionary entries, so this is where a
    snippet fix is worth most. Same treatment the chapter descriptions got on
    2026-07-31: lead with the thing itself, trim at a sentence boundary, keep it
    under the limit."""
    t = re.sub(r"<[^>]+>", "", prose or "")
    t = html.unescape(t)
    t = (t.replace("\u26a0\ufe0f", "").replace("\u26a0", "")
          .replace("\u2014", " \u2014 ").replace("\u2013", "-"))
    t = re.sub(r"\s+", " ", t).strip(" \u2014-\u2013 ")
    lead = f"{label}: " if label else ""
    return lead + _trim_desc(t, 158 - len(lead))


def check_built_descriptions():
    """Scan the BUILT output for meta descriptions over the truncation limit.

    This is the guard that would actually have caught the bug it was written for.
    check_entry_seo() validates _entry_desc(), which caps by construction and so
    can never fail; what went wrong was that three ES page builders (and, before
    2026-07-31, every ES chapter) were still passing raw prose straight through.
    A guard on the function cannot see that. A guard on the output can.

    Added 2026-08-01 after Search Console showed 54 pages ranking at position <=
    10 with a click-through rate of zero, 28 of them dictionary entries whose
    descriptions ran to several hundred characters and were cut mid-sentence."""
    import glob as _glob
    bad = []
    for pat in ("*.html", "dict/*.html", "ency/*.html", "atlas/*.html", "routes/*.html"):
        for f in _glob.glob(os.path.join(OUT, pat)):
            txt = open(f, encoding="utf-8").read()
            m = re.search(r'<meta name="description" content="([^"]*)"', txt)
            if not m:
                continue
            n = len(html.unescape(m.group(1)))
            if n > 160:
                bad.append((n, os.path.relpath(f, OUT)))
    if bad:
        bad.sort(reverse=True)
        raise SystemExit(
            "BUILT-DESCRIPTION CHECK FAILED -- %d page(s) over the 160-character "
            "truncation limit:\n" % len(bad)
            + "\n".join(f"  {n:5d}  {f}" for n, f in bad[:20])
            + ("\n  ... and %d more" % (len(bad) - 20) if len(bad) > 20 else "")
            + "\n(route the description through _entry_desc() or _meta_desc())")


def check_entry_seo():
    """Library entry pages must carry a real description, not a whole gloss.

    Guards _entry_desc(). Fails the build if any dict/ency description would ship
    over the truncation limit -- which is how 795 dictionary pages came to have
    descriptions averaging several hundred characters without anyone noticing."""
    bad = []
    for slug, term, orig, translit, gloss, ref in DICTIONARY:
        d = _entry_desc(term, gloss)
        if len(d) > 160:
            bad.append(f"  dict/{slug}: {len(d)} chars")
    for e in ENCYCLOPEDIA:
        d = _entry_desc(e["name"], e["desc"])
        if len(d) > 160:
            bad.append(f"  ency/{e['slug']}: {len(d)} chars")
    # The Spanish twins were left out of the first pass, exactly as the Spanish
    # CHAPTER descriptions were on 2026-07-31. 350 entry pages, median 400-700
    # characters. Guard both sides from the start this time.
    for slug, (term_es, desc_es) in DICTIONARY_ES.items():
        d = _entry_desc(term_es, desc_es, lang="es")
        if len(d) > 160:
            bad.append(f"  dict/{slug}.es: {len(d)} chars")
    for slug, (name_es, desc_es) in ENCYCLOPEDIA_ES.items():
        d = _entry_desc(name_es, desc_es, lang="es")
        if len(d) > 160:
            bad.append(f"  ency/{slug}.es: {len(d)} chars")
    if bad:
        raise SystemExit("ENTRY SEO CHECK FAILED -- descriptions over the truncation limit:\n"
                         + "\n".join(bad[:20]))


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



# --- chapter art ------------------------------------------------------------
# A public-domain painting of the scene, inserted as a frontispiece right under
# the chapter heading, with painter / year / where it hangs underneath — Michael's
# "art education along the way" (2026-07-25). See library_data.CHAPTER_ART for the
# licence reasoning (2-D reproductions are PD-Art, unlike a photo of a 3-D object).
_ART_REQUIRED = ("file", "title", "artist", "year", "location", "alt", "license", "source_url")


def _chapter_art_html(art, lang="en"):
    missing = [k for k in _ART_REQUIRED if not art.get(k)]
    if missing:
        raise SystemExit(f"chapter art {art.get('file', '?')!r} is missing {missing} — "
                         f"a painting cannot be published without its painter, year, "
                         f"location, licence and source")
    path = f"img/art/{art['file']}"
    if not os.path.isfile(os.path.join(OUT, path)):
        raise SystemExit(f"chapter art {path} is referenced but not committed — "
                         f"GitHub Pages can only serve files in the repo")
    es = lang == "es"
    title = art.get("title_es") if es and art.get("title_es") else art["title"]
    where = art.get("location_es") if es and art.get("location_es") else art["location"]
    note = (art.get("note_es") if es else art.get("note")) or ""
    lic = html.escape(art["license"])
    src = html.escape(art["source_url"], quote=True)
    seen = "Ver el original" if es else "View the original"
    line = (f'<span class="art-artist">{html.escape(art["artist"])}</span>, '
            f'{html.escape(art["year"])} · {html.escape(where)}')
    notep = f'<p class="art-note">{note}</p>' if note else ""
    return f"""<figure class="chapter-art">
  <img src="{path}" alt="{html.escape(art['alt'], quote=True)}" loading="lazy"/>
  <figcaption>
    <div class="art-title"><em>{html.escape(title)}</em></div>
    <div class="art-meta">{line}</div>
    {notep}
    <div class="art-lic">{lic} · <a href="{src}" rel="noopener">{seen}</a></div>
  </figcaption>
</figure>"""


def inject_chapter_art(content, slug, lang="en"):
    """Drop the chapter's painting in immediately after the <h2> heading, like the
    plate facing the text in an illustrated Bible. No-op for a chapter with no art,
    which is most of them — the shelf grows one chapter at a time."""
    arts = CHAPTER_ART.get(slug) or []
    if not arts:
        return content
    block = "".join(_chapter_art_html(a, lang) for a in arts)
    m = re.search(r"(</h2>)", content)
    if not m:
        return content          # no heading to anchor to: leave the page alone
    i = m.end()
    return content[:i] + "\n" + block + content[i:]


def build_chapter_pages(chapters):
    es_panels = _es_panels()   # chapters with a Spanish edition -> the reader's español toggle
    for slug, book, num, teaser in CHAPTERS:
        content = clean_chapter(chapters[slug])
        content = inject_chapter_art(content, slug)
        content = inject_encyclopedia_links(content, book, num)
        content = inject_xrefs(content, book, num)
        content = move_clips_into_verses(content)
        content = render_film_clips(content)
        content, has_es = inject_spanish(content, slug, es_panels)
        orig_lang = _source_lang(book, num)   # the Hide-original toggle label
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
        desc = _meta_desc(book, num, teaser, src)
        out = page(f"{book} {num} — {SITE_NAME}", body, desc=desc,
                   url=chapter_filename(book, num))
        out = out.replace("</head>", _chapter_jsonld(book, num, desc,
                                                     chapter_filename(book, num)) + "\n</head>", 1)
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
                    "the fresh-from-the-Hebrew translation, and everything still ahead.", url="toc.html",
               og_type="website")
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
                    "chapter — kept privately in your browser, no account needed.", url="reading.html",
               og_type="website")
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
  <a class="card" href="ask.html"><div class="card-t">\U0001F4D6 Dear Mr. Librarian</div>
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
                    "one chapter at a time, with verse-by-verse notes comparing seven landmark versions.",
               url="index.html", og_type="website")
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
  <p style="margin-top:14px"><strong>Honesty note.</strong> This translation is made by Mr. Librarian, working from the pointed Hebrew and the critical Greek text. It is a study rendering, not the
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
                    "essentially literal in a modern register, compared against seven landmark versions.",
               url="about.html", og_type="website")
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
                    "why the translation renders the divine Name as Jehovah.", url="old-testament.html")
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
                    "are weighed, and what carries over from the Hebrew.", url="new-testament.html")
    open(os.path.join(OUT, "new-testament.html"), "w", encoding="utf-8").write(out)


def build_ask_enoch():
    body = """<div class="askbar"><a href="ask.html">← Dear Mr. Librarian</a></div>
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
    out = page(f"Dear Mr. Librarian: the Book of Enoch — {SITE_NAME}", body, active="ask",
               desc="Why the Book of Enoch isn't part of this Bible translation: the Masoretic source "
                    "text, the canon question, the Ethiopian exception, and the Dead Sea Scrolls.",
               url="ask-enoch.html")
    open(os.path.join(OUT, "ask-enoch.html"), "w", encoding="utf-8").write(out)


def build_ask_newton():
    """Dear Mr. Librarian: did Isaac Newton write about the Bible? Presents his three
    public-domain biblical works, their genuine fit with this site (Daniel/Revelation,
    the Johannine Comma on the NT apparatus page, the Chronology), and — under the
    project's neutrality rule — handles his private anti-Trinitarianism factually,
    distinguishing his sound textual findings from his partisan doctrinal motive. The
    works themselves are archived (source/newton/ + S3) by tools/archive_newton.py."""
    body = """<div class="askbar"><a href="ask.html">← Dear Mr. Librarian</a></div>
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
  <p class="muted" style="font-size:12px">My own takeaway: the most famous scientist in history spent his hidden hours doing something very like what this project does — sourcing, collating, comparing, and
  refusing to take a text on trust. On his best days (the manuscripts) he was decades ahead of his time; on his
  boldest (the prophecy timetable, the chronology) he over-read the evidence; and on the deepest question he
  took a side this library will not. Worth knowing, worth keeping — and worth weighing for yourself.</p>
</div>"""
    out = page(f"Did Isaac Newton write about the Bible? — {SITE_NAME}", body, active="ask",
               desc="Isaac Newton wrote more on the Bible than on physics. His Observations on Daniel and "
                    "Revelation, his textual criticism of the Johannine Comma (1 John 5:7), and his biblical "
                    "chronology — how they fit The MisterLibrarian Bible Project, his private anti-Trinitarianism "
                    "handled honestly, and where to read the public-domain works.", url="ask-newton.html")
    open(os.path.join(OUT, "ask-newton.html"), "w", encoding="utf-8").write(out)


ES_BOOK = {"Genesis": "Génesis", "Exodus": "Éxodo", "Leviticus": "Levítico",
           "Numbers": "Números", "Deuteronomy": "Deuteronomio", "Joshua": "Josué",
           "Judges": "Jueces", "Ruth": "Rut", "1 Samuel": "1 Samuel", "1 Kings": "1 Reyes", "1 Chronicles": "1 Crónicas", "2 Chronicles": "2 Crónicas", "2 Kings": "2 Reyes",
           "2 Samuel": "2 Samuel", "Jeremiah": "Jeremías", "Proverbs": "Proverbios",
           "Daniel": "Daniel", "Ezra": "Esdras", "Esther": "Ester", "Ecclesiastes": "Eclesiastés", "Song of Solomon": "Cantar de los Cantares", "Isaiah": "Isaías", "Lamentations": "Lamentaciones", "Hosea": "Oseas", "Joel": "Joel", "Nehemiah": "Nehemías", "Ezekiel": "Ezequiel", "Job": "Job", "Malachi": "Malaquías", "Matthew": "Mateo",
           "Mark": "Marcos", "Luke": "Lucas", "John": "Juan", "Acts": "Hechos", "Romans": "Romanos", "1 Corinthians": "1 Corintios", "2 Corinthians": "2 Corintios", "Galatians": "Gálatas", "Ephesians": "Efesios", "Philippians": "Filipenses", "Colossians": "Colosenses", "1 Thessalonians": "1 Tesalonicenses", "2 Thessalonians": "2 Tesalonicenses", "2 John": "2 Juan",
           "Mark": "Marcos", "Luke": "Lucas", "John": "Juan", "Acts": "Hechos", "Romans": "Romanos", "1 Corinthians": "1 Corintios", "2 Corinthians": "2 Corintios", "Galatians": "Gálatas", "Ephesians": "Efesios", "Philippians": "Filipenses", "Colossians": "Colosenses", "1 Thessalonians": "1 Tesalonicenses", "1 Timothy": "1 Timoteo", "2 Timothy": "2 Timoteo", "Titus": "Tito", "Philemon": "Filemón", "Hebrews": "Hebreos", "James": "Santiago", "1 Peter": "1 Pedro", "2 Peter": "2 Pedro", "2 John": "2 Juan",
           "Mark": "Marcos", "Luke": "Lucas", "John": "Juan", "Acts": "Hechos", "Romans": "Romanos", "1 Corinthians": "1 Corintios", "2 Corinthians": "2 Corintios", "Galatians": "Gálatas", "Ephesians": "Efesios", "Philippians": "Filipenses", "Colossians": "Colosenses", "1 Thessalonians": "1 Tesalonicenses", "1 John": "1 Juan", "2 John": "2 Juan",
           "3 John": "3 Juan", "Amos": "Amós", "Obadiah": "Abdías", "Jonah": "Jonás", "Micah": "Miqueas", "Nahum": "Nahúm", "Habakkuk": "Habacuc", "Zephaniah": "Sofonías", "Haggai": "Hageo", "Zechariah": "Zacarías", "Psalms": "Salmos", "Jude": "Judas", "Revelation": "Apocalipsis"}


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



# ---------------------------------------------------------------------------
# THE SPANISH LIBRARY (2026-07-25) — diccionario, enciclopedia, concordancia,
# atlas, and the biblioteca hub that gathers them.
#
# The governing rule is the one already written into the Spanish nav: a page is
# linked in Spanish ONLY if it exists in Spanish, and a Spanish-only reader is
# never dumped into English. So:
#   * the CONCORDANCIA is complete on day one, because it is generated from the
#     Spanish verse text itself -- no translation needed, ever;
#   * the DICCIONARIO and ENCICLOPEDIA render ONLY the entries present in
#     library_data.DICTIONARY_ES / ENCYCLOPEDIA_ES, and each page prints its own
#     honest coverage ("8 de 572") rather than padding itself with English;
#   * the ATLAS shows only places that have a Spanish entry, for the same reason.
# ---------------------------------------------------------------------------

SITE_NAME_ES = "La Traducción Mister"

# Spanish book names for citations like "Jeremías 18:3".
# ⚠ Reuses the EXISTING ES_BOOK map (158 entries, defined just above) rather than
# keeping a second copy — two book-name maps would drift the first time a book was
# added to one and not the other. Falls back to the English name so a new book can
# never crash a build.
def book_es(book):
    return ES_BOOK.get(book, book)


# Spanish function words, plus the few translation-mechanical words that would
# otherwise top the frequency list and tell a reader nothing.
_STOPWORDS_ES = {
    "los", "las", "una", "unos", "unas", "del", "por", "para", "con", "sin",
    "sobre", "entre", "hasta", "desde", "como", "más", "pero", "porque", "que",
    "sus", "sea", "ser", "son", "fue", "era", "eran", "está", "están", "estaba",
    "han", "has", "hay", "había", "les", "nos", "vos", "ellos", "ellas",
    "esto", "esta", "este", "estos", "estas", "eso", "esa", "ese", "esos",
    "esas", "aquel", "todo", "toda", "todos", "todas", "cada", "cual",
    "cuales", "quien", "quienes", "donde", "cuando", "también", "así",
    "aun", "aún", "muy", "tan", "mis", "tus", "nuestro", "nuestra",
    "vuestro", "vuestra", "vuestros", "vuestras", "dijo", "dice", "diciendo",
    "dijeron", "hizo", "hacer", "haré", "fueron", "sino", "aunque",
    "según", "entonces", "luego", "ahora", "he", "ha", "mi", "tu", "su",
    "me", "te", "se", "le", "lo", "la", "el", "un", "no", "ni", "si", "ya",
}


def extract_verses_spanish(panels):
    """[(book, chapter_num, anchor, verse_num, plain_spanish_text), ...] for every
    Spanish verse we have. The ANCHOR is carried through verbatim rather than
    rebuilt, because a book's chapter 1 uses a bare `vN` while later chapters use
    `vCH-N` -- recomputing it would silently produce dead links."""
    rows = []
    en_by_slug = {slug: (book, num) for slug, book, num, _ in CHAPTERS}
    for slug, content in panels.items():
        bk = en_by_slug.get(slug)
        if not bk:
            continue
        book, num = bk
        for m in re.finditer(r'id="(v(?:\d+-)?\d+)".*?<div class="esp">(.*?)</div>',
                             content, re.S):
            anchor, esp = m.group(1), m.group(2)
            vnum = int(anchor.rsplit("-", 1)[-1] if "-" in anchor else anchor[1:])
            text = re.sub(r"<[^>]+>", " ", esp)
            text = html.unescape(text)
            text = re.sub(r"\s*nota\s*$", "", text.strip())
            text = re.sub(r"\s+", " ", text)
            rows.append((book, num, anchor, vnum, text))
    return rows


def es_verse_url(book, ch, anchor):
    return f"{book_slug(book)}-{ch}.es.html#{anchor}"


def es_ref_link(book, ch, anchor, vnum):
    return (f'<a href="{es_verse_url(book, ch, anchor)}">'
            f'{book_es(book)} {ch}:{vnum}</a>')


def _es_slugs_available(panels):
    """{'jeremiah-18', ...} -- which chapters have a Spanish page."""
    en_by_slug = {slug: (book, num) for slug, book, num, _ in CHAPTERS}
    out = set()
    for slug in panels:
        bk = en_by_slug.get(slug)
        if bk:
            out.add(f"{book_slug(bk[0])}-{bk[1]}")
    return out


def _es_dict_ref(book, ch, v, es_slugs):
    """Cite a verse in Spanish. Links ONLY when that chapter has a SPANISH page;
    otherwise plain text, so a Spanish reader is never sent into English."""
    label = f"{book_es(book)} {ch}:{v}"
    slug = f"{book_slug(book)}-{ch}"
    if slug in es_slugs:
        anchor = f"v{v}" if ch == 1 else f"v{ch}-{v}"
        return f'<a href="{slug}.es.html#{anchor}">{label}</a>'
    return f'<span class="ref-unpub" title="capítulo aún no traducido">{label}</span>'


def build_concordance_es(panels):
    """The one Spanish library page COMPLETE from day one: generated from the
    Spanish verse text, so it needs no separate translation and cannot fall
    behind the chapters."""
    rows = extract_verses_spanish(panels)
    index = defaultdict(list)
    for book, ch, anchor, vnum, text in rows:
        seen = set()
        for raw in re.findall(
                r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]"
                r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ'’\-]*",
                text):
            w = raw.lower().strip("'’-")
            if len(w) < 3 or w in _STOPWORDS_ES or w in seen:
                continue
            seen.add(w)
            index[w].append((book, ch, anchor, vnum))
    words = sorted(index.keys())
    total_refs = sum(len(v) for v in index.values())

    letters = sorted({w[0].upper() for w in words})
    jump = " ".join(f'<a href="#L{L}">{L}</a>' for L in letters)
    sections, cur = [], None
    for w in words:
        L = w[0].upper()
        if L != cur:
            if cur is not None:
                sections.append("</div>")
            sections.append(f'<h2 id="L{L}">{L}</h2><div class="panel conc">')
            cur = L
        refs = index[w]
        links = " ".join(es_ref_link(b, c, a, v) for b, c, a, v in refs)
        sections.append(
            f'<div class="cw"><span class="cw-w">{html.escape(w)}</span>'
            f'<span class="cw-n">×{len(refs)}</span>'
            f'<span class="cw-refs">{links}</span></div>')
    if cur is not None:
        sections.append("</div>")

    body = f"""<h1 class="pagetitle">\U0001F520 Concordancia</h1>
<p class="lede">Todas las palabras significativas de la traducción española, indexadas a cada
versículo donde aparecen — <strong>{len(words)} palabras · {total_refs} apariciones</strong>
en {len(rows)} versículos. Se genera automáticamente del texto español en cada compilación,
así que nunca se queda atrás: es la única página de esta biblioteca que está
<strong>completa</strong> desde el primer día.</p>
<div class="panel alpha">{jump}</div>
{"".join(sections)}"""
    out = page(f"Concordancia — {SITE_NAME_ES}", body, active="biblioteca", lang="es",
               desc="Concordancia completa de la traducción española, generada del texto mismo.",
               url="concordancia.html", og_type="website")
    open(os.path.join(OUT, "concordancia.html"), "w", encoding="utf-8").write(out)
    return len(words), total_refs


def _dict_card_es(slug, term_es, orig, translit, desc_es, book, ch, v, es_slugs, permalink=True):
    """Spanish twin of _dict_card -- shared by diccionario.html and dict/<slug>.es.html."""
    script_cls = "dgreek" if _is_nt(book) else "dheb"
    perma = (f'<a href="dict/{slug}.es.html" style="font-size:11px;font-weight:400;opacity:.55" '
             f'title="Enlace permanente — comparte esta entrada">🔗 enlace</a>' if permalink else "")
    return f"""<div class="dentry" id="{slug}">
  <div class="dhead"><span class="dterm">{html.escape(term_es)}</span>
    <span class="{script_cls}">{orig}</span> <span class="dtr">{html.escape(translit)}</span> {perma}</div>
  <p>{desc_es} <span class="dref">→ primero comentado en {_es_dict_ref(book, ch, v, es_slugs)}</span></p>
</div>"""


def _dict_index_row_es(slug, term_es, desc_es):
    """Lean clickable line for diccionario.html -- full entry lives on
    dict/<slug>.es.html now."""
    teaser = _plain(desc_es)
    if len(teaser) > 110:
        teaser = teaser[:107].rsplit(" ", 1)[0].rstrip(",;:—") + "…"
    return (f'<a class="eirow" id="{slug}" href="dict/{slug}.es.html">'
            f'<span class="ei-name">{html.escape(term_es)}</span>'
            f'<span class="ei-teaser">{html.escape(teaser)}</span></a>')


def build_dictionary_es(panels):
    es_slugs = _es_slugs_available(panels)
    by_slug = {d[0]: d for d in DICTIONARY}
    items = []
    for slug in sorted(DICTIONARY_ES, key=lambda k: DICTIONARY_ES[k][0].lower()):
        term_es, desc_es = DICTIONARY_ES[slug]
        src = by_slug.get(slug)
        if not src:
            continue
        items.append(_dict_index_row_es(slug, term_es, desc_es))
    body = f"""<h1 class="pagetitle">\U0001F4D6 Diccionario</h1>
<p class="lede">Las palabras del idioma original que esta traducción ha encontrado — hebreo para el
Tanaj, griego para el Nuevo Testamento — explicadas en español.
<strong>{len(items)} de {len(DICTIONARY)} términos</strong> tienen ya su entrada española. Haz clic en un
término para ver la entrada completa.</p>
<div class="panel" style="padding:10px 14px">
  <p style="margin:0"><strong>Esta página crece capítulo a capítulo.</strong> Aquí aparecen
  únicamente los términos que ya están escritos en español, porque una entrada en inglés
  dentro de una página española no le sirve a nadie que lea solo español. Los que faltan se van
  añadiendo a medida que se traduce cada capítulo nuevo.</p>
</div>
<div class="panel eilist">{"".join(items)}</div>"""
    out = page(f"Diccionario — {SITE_NAME_ES}", body, active="biblioteca", lang="es",
               desc="Diccionario hebreo y griego de la traducción, en español.", url="diccionario.html",
               og_type="website")
    open(os.path.join(OUT, "diccionario.html"), "w", encoding="utf-8").write(out)
    return len(items)


def _ency_card_es(slug, name_es, desc_es, e, es_slugs, permalink=True):
    """Spanish twin of _ency_card -- the standalone page ency/<slug>.es.html."""
    refs = " ".join(_es_dict_ref(b, c, v, es_slugs) for b, c, v in e["refs"])
    maplink = ""
    if e.get("coords"):
        maplink = (f'<div class="emap"><a href="atlas/{slug}.es.html">'
                   f'\U0001F5FA️ Verlo en el atlas →</a></div>')
    perma = (f'<a href="ency/{slug}.es.html" style="font-size:11px;font-weight:400;opacity:.55;'
              f'margin-left:8px" title="Enlace permanente — comparte esta entrada">🔗 enlace</a>'
             if permalink else "")
    return f"""<div class="eentry" id="{slug}">
  <div class="ehead">{html.escape(name_es)}{perma}</div>
  <p>{desc_es}</p>
  {_entry_images_html(e, "es")}
  <div class="erefs"><span class="xr-label">en el texto</span> {refs}</div>
  {maplink}
</div>"""


def _ency_index_row_es(slug, name_es, desc_es):
    """Lean clickable line for enciclopedia.html -- full entry lives on
    ency/<slug>.es.html now."""
    teaser = _plain(desc_es)
    if len(teaser) > 130:
        teaser = teaser[:127].rsplit(" ", 1)[0].rstrip(",;:—") + "…"
    return (f'<a class="eirow" id="{slug}" href="ency/{slug}.es.html">'
            f'<span class="ei-name">{html.escape(name_es)}</span>'
            f'<span class="ei-teaser">{html.escape(teaser)}</span></a>')


def build_encyclopedia_es(panels):
    by_slug = {e["slug"]: e for e in ENCYCLOPEDIA}
    groups = {"place": [], "people": [], "craft": []}
    for slug, (name_es, desc_es) in ENCYCLOPEDIA_ES.items():
        e = by_slug.get(slug)
        if not e:
            continue
        k = e["kind"]
        k = ("people" if k in ("person", "people")
             else "craft" if k in ("craft", "thing") else "place")
        groups[k].append((slug, name_es, desc_es))

    def render(entries):
        return "".join(_ency_index_row_es(slug, name_es, desc_es)
                       for slug, name_es, desc_es in sorted(entries, key=lambda x: x[1].lower()))

    total = sum(len(v) for v in groups.values())
    secs = []
    for key, title in (("place", "Lugares"), ("people", "Personas"),
                       ("craft", "Oficios y artes")):
        if groups[key]:
            secs.append(f'<h2>{title}</h2><div class="panel eilist">{render(groups[key])}</div>')

    body = f"""<h1 class="pagetitle">\U0001F3FA Enciclopedia</h1>
<p class="lede">Las personas, los lugares y los oficios que la traducción ha alcanzado —
<strong>{total} de {len(ENCYCLOPEDIA)} entradas</strong> están ya escritas en español. Haz clic en un
nombre para ver la entrada completa.</p>
<div class="panel" style="padding:10px 14px">
  <p style="margin:0"><strong>Esta página crece capítulo a capítulo.</strong> Solo se muestran las
  entradas que ya tienen texto español; nada se rellena con inglés.</p>
</div>
{"".join(secs)}"""
    out = page(f"Enciclopedia — {SITE_NAME_ES}", body, active="biblioteca", lang="es",
               desc="Personas, lugares y oficios de la traducción, en español.", url="enciclopedia.html",
               og_type="website")
    open(os.path.join(OUT, "enciclopedia.html"), "w", encoding="utf-8").write(out)
    return total


def build_dictionary_entry_pages_es(panels):
    """Spanish twin of build_dictionary_entry_pages() -- dict/<slug>.es.html, one
    per term that already has a Spanish entry. Nothing falls back to English:
    a slug with no DICTIONARY_ES entry simply gets no Spanish page yet."""
    es_slugs = _es_slugs_available(panels)
    by_slug = {d[0]: d for d in DICTIONARY}
    outdir = os.path.join(OUT, "dict")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for slug in DICTIONARY_ES:
        term_es, desc_es = DICTIONARY_ES[slug]
        src = by_slug.get(slug)
        if not src:
            continue
        _, term, orig, translit, _gloss, ref = src
        book, ch, v = _ref(ref)
        body = f"""<p style="font-size:12px;opacity:.6;margin:0 0 12px">
  <a href="diccionario.html">📖 Diccionario</a></p>
{_dict_card_es(slug, term_es, orig, translit, desc_es, book, ch, v, es_slugs, permalink=False)}"""
        out = page(f"{term_es} — Diccionario — {SITE_NAME_ES}", body, active="biblioteca",
                   lang="es", desc=_entry_desc(term_es, desc_es, lang="es"),
                   url=f"dict/{slug}.es.html", base=f"{SITE_URL}/")
        open(os.path.join(outdir, f"{slug}.es.html"), "w", encoding="utf-8").write(out)
        n += 1
    return n


def build_encyclopedia_entry_pages_es(panels):
    """Spanish twin of build_encyclopedia_entry_pages() -- ency/<slug>.es.html, one
    per entry that already has an ENCYCLOPEDIA_ES translation."""
    es_slugs = _es_slugs_available(panels)
    by_slug = {e["slug"]: e for e in ENCYCLOPEDIA}
    outdir = os.path.join(OUT, "ency")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for slug, (name_es, desc_es) in ENCYCLOPEDIA_ES.items():
        e = by_slug.get(slug)
        if not e:
            continue
        img = (e.get("images") or [None])[0]
        og_image = f"{SITE_URL}/img/ency/{img['file']}" if img else ""
        body = f"""<p style="font-size:12px;opacity:.6;margin:0 0 12px">
  <a href="enciclopedia.html">🏺 Enciclopedia</a></p>
{_ency_card_es(slug, name_es, desc_es, e, es_slugs, permalink=False)}"""
        out = page(f"{name_es} — Enciclopedia — {SITE_NAME_ES}", body, active="biblioteca",
                   lang="es", desc=_entry_desc(name_es, desc_es, lang="es"),
                   url=f"ency/{slug}.es.html", image=og_image,
                   base=f"{SITE_URL}/")
        open(os.path.join(outdir, f"{slug}.es.html"), "w", encoding="utf-8").write(out)
        n += 1
    return n


def _atlas_card_es(slug, name_es, desc_es, e, es_slugs, permalink=True):
    """Spanish twin of _atlas_card -- the standalone page atlas/<slug>.es.html."""
    refs = " ".join(_es_dict_ref(b, c, v, es_slugs) for b, c, v in e["refs"])
    if e.get("coords"):
        lat, lon, span = e["coords"]
        badge = ' <span class="atlas-approx">aproximado</span>' if e.get("approx") else ""
        caption = f'\U0001F4CD <strong>{html.escape(name_es)}</strong>'
        if e.get("modern"):
            caption += f' — hoy {html.escape(e["modern"])}'
        map_html = osm_embed(lat, lon, span, name_es, caption=caption)
    else:
        badge = ""
        map_html = ('<div class="atlas-nomap">\U0001F4CD Sin punto fijo: la ubicación está '
                    "genuinamente sin determinar, así que no se muestra ninguna chincheta "
                    "adivinada.</div>")
    perma = (f'<a href="atlas/{slug}.es.html" style="font-size:11px;font-weight:400;opacity:.55;'
              f'margin-left:8px" title="Enlace permanente — comparte este lugar">🔗 enlace</a>'
             if permalink else "")
    return f"""<div class="atlas-place" id="atlas-{slug}">
  <div class="atlas-place-h"><a href="enciclopedia.html#{slug}">{html.escape(name_es)}</a>{badge}{perma}</div>
  <p>{desc_es}</p>
  <div class="erefs"><span class="xr-label">en el texto</span> {refs}</div>
  {map_html}
</div>"""


def build_atlas_es(panels):
    """Spanish atlas INDEX. Shows only places that HAVE a Spanish entry -- the
    coordinates are language-neutral and reused, but the prose must be Spanish or
    the page would dump a Spanish reader into English. Already place-organized
    (unlike the English atlas's chapter-by-chapter layout), so this is a
    straightforward lean-list conversion -- full content moves to
    atlas/<slug>.es.html (build_atlas_entry_pages_es())."""
    by_slug = {e["slug"]: e for e in ENCYCLOPEDIA}
    places = []
    for slug, (name_es, desc_es) in ENCYCLOPEDIA_ES.items():
        e = by_slug.get(slug)
        if e and e["kind"] == "place":
            places.append((slug, name_es, e))
    mapped = sum(1 for _, _, e in places if e.get("coords"))

    rows = []
    for slug, name_es, e in sorted(places, key=lambda x: x[1].lower()):
        pin = "📍" if e.get("coords") else "❓"
        rows.append(f'<a class="atlas-item" id="atlas-{slug}" href="atlas/{slug}.es.html">'
                    f'{pin} {html.escape(name_es)}</a>')

    body = f"""<h1 class="pagetitle">\U0001F5FA️ Atlas</h1>
<p class="lede">Los lugares de la traducción, situados en un mapa vivo —
<strong>{mapped} de {len(places)}</strong> con coordenadas. Las coordenadas se comparten con la
edición inglesa; el texto es español. Haz clic en un lugar para ver la entrada completa.</p>
<div class="panel" style="padding:10px 14px">
  <p style="margin:0"><strong>Esta página crece capítulo a capítulo.</strong> Aparecen únicamente
  los lugares que ya tienen entrada en español.</p>
</div>
<div class="atlas-items">{"".join(rows)}</div>"""
    out = page(f"Atlas — {SITE_NAME_ES}", body, active="biblioteca", lang="es",
               desc="Atlas de los lugares de la traducción, en español.", url="atlas-es.html",
               og_type="website")
    open(os.path.join(OUT, "atlas-es.html"), "w", encoding="utf-8").write(out)
    return mapped, len(places)


def build_atlas_entry_pages_es(panels):
    """Spanish twin of build_atlas_entry_pages() -- atlas/<slug>.es.html, one per
    mapped place that already has an ENCYCLOPEDIA_ES translation."""
    es_slugs = _es_slugs_available(panels)
    by_slug = {e["slug"]: e for e in ENCYCLOPEDIA}
    outdir = os.path.join(OUT, "atlas")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for slug, (name_es, desc_es) in ENCYCLOPEDIA_ES.items():
        e = by_slug.get(slug)
        if not e or e["kind"] != "place":
            continue
        img = (e.get("images") or [None])[0]
        og_image = f"{SITE_URL}/img/ency/{img['file']}" if img else ""
        body = f"""<p style="font-size:12px;opacity:.6;margin:0 0 12px">
  <a href="atlas-es.html">🗺️ Atlas</a></p>
{_atlas_card_es(slug, name_es, desc_es, e, es_slugs, permalink=False)}"""
        out = page(f"{name_es} — Atlas — {SITE_NAME_ES}", body, active="biblioteca",
                   lang="es", desc=_entry_desc(name_es, desc_es, lang="es"),
                   url=f"atlas/{slug}.es.html", image=og_image,
                   base=f"{SITE_URL}/")
        open(os.path.join(outdir, f"{slug}.es.html"), "w", encoding="utf-8").write(out)
        n += 1
    return n


def build_library_es(stats):
    n_words, n_refs, n_dict, n_ency, n_mapped, n_places = stats
    body = f"""<h1 class="pagetitle">\U0001F4DA La Biblioteca</h1>
<p class="lede">La sala de consulta de la edición española. Cada estante crece —
automáticamente o a mano — a medida que se traduce cada capítulo, así que la biblioteca es
siempre exactamente tan honda como la traducción misma.</p>

<div class="cardgrid">
  <a class="card" href="concordancia.html"><div class="card-t">\U0001F520 Concordancia</div>
  <div class="card-d">{n_words} palabras · {n_refs} apariciones — todas las palabras significativas
  del texto español, indexadas a cada versículo. Generada del texto mismo:
  <strong>completa</strong>.</div></a>
  <a class="card" href="diccionario.html"><div class="card-t">\U0001F4D6 Diccionario</div>
  <div class="card-d">{n_dict} de {len(DICTIONARY)} términos hebreos y griegos explicados en
  español — crece con cada capítulo.</div></a>
  <a class="card" href="enciclopedia.html"><div class="card-t">\U0001F3FA Enciclopedia</div>
  <div class="card-d">{n_ency} de {len(ENCYCLOPEDIA)} entradas de personas, lugares y oficios en
  español — crece con cada capítulo.</div></a>
  <a class="card" href="atlas-es.html"><div class="card-t">\U0001F5FA️ Atlas</div>
  <div class="card-d">{n_mapped} de {n_places} lugares situados en el mapa, con el texto en
  español.</div></a>
</div>

<div class="panel" style="padding:12px 16px">
  <h3 style="margin-top:0">Por qué algunas páginas están incompletas</h3>
  <p>La regla de esta edición es sencilla: <strong>nada se rellena con inglés</strong>. La
  navegación española enlaza solo a páginas que existen en español, y una entrada del
  diccionario escrita en inglés dentro de una página española no le sirve de nada a quien lee
  solo español. Así que cada estante muestra su cobertura real y va creciendo capítulo a
  capítulo.</p>
  <p>La <strong>concordancia</strong> es la excepción: se construye a partir del texto español
  mismo, de modo que está completa desde el primer día y no puede quedarse atrás.</p>
</div>"""
    out = page(f"La Biblioteca — {SITE_NAME_ES}", body, active="biblioteca", lang="es",
               desc="La sala de consulta de la edición española: concordancia, diccionario, "
                    "enciclopedia y atlas.", url="biblioteca.html", og_type="website")
    open(os.path.join(OUT, "biblioteca.html"), "w", encoding="utf-8").write(out)


def build_library_es_all(panels):
    """Build all four Spanish library pages + the hub. Returns a summary tuple."""
    n_words, n_refs = build_concordance_es(panels)
    n_dict = build_dictionary_es(panels)
    n_ency = build_encyclopedia_es(panels)
    build_dictionary_entry_pages_es(panels)
    build_encyclopedia_entry_pages_es(panels)
    n_mapped, n_places = build_atlas_es(panels)
    build_atlas_entry_pages_es(panels)
    build_library_es((n_words, n_refs, n_dict, n_ency, n_mapped, n_places))
    return n_words, n_refs, n_dict, n_ency, n_mapped, n_places


def build_es():
    """The Spanish locale — a parallel edition built chapter by chapter from
    source/es/*.html. Each Spanish chapter renders to <slug>.es.html with Spanish
    chrome (Spanish nav, an 'Ocultar hebreo' toggle, and the 🌐 language switch back
    to English); es.html is the Spanish home. The English site is untouched. Grows as
    source/es/ files are added — the same 'chapter by chapter on both sides' cadence."""
    panels = _es_panels()
    if not panels:
        return
    # The Spanish reference room, built from the same panels. Kept inside build_es
    # so it can never run without Spanish chapters to build from.
    es_lib = build_library_es_all(panels)
    print(f"   biblioteca es: concordancia {es_lib[0]}w/{es_lib[1]}refs, "
          f"diccionario {es_lib[2]}/{len(DICTIONARY)}, enciclopedia {es_lib[3]}/{len(ENCYCLOPEDIA)}, "
          f"atlas {es_lib[4]}/{es_lib[5]}")
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
        content = inject_chapter_art(content, slug, "es")
        es_title = f"{ES_BOOK.get(book, book)} {num}"
        en_file = chapter_filename(book, num)
        es_file = en_file[:-5] + ".es.html"          # genesis-1.html -> genesis-1.es.html
        # 2026-08-01: this toggle hardcoded "hebreo" on all 135+ built Spanish
        # chapters, including every NT chapter (actually Greek) and now Daniel 3
        # (Aramaic) -- the same mislabel as the English side's toggle before
        # _source_lang() existed. ES_LANG_LABEL mirrors that fix.
        _src = _source_lang(book, num)
        _lbl = {"Greek": "griego", "Aramaic": "arameo", "Hebrew": "hebreo"}[_src]
        toggle = (f'<div class="togglebar"><div class="tgl-group">'
                  f'<button class="tgl" id="hebtgl" onclick="toggleHeb()">Ocultar {_lbl}</button>'
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
  document.getElementById("hebtgl").textContent = hidden ? "Mostrar {_lbl}" : "Ocultar {_lbl}";
  try{{ localStorage.setItem("mtlib_hideheb", hidden ? "1" : "0"); }}catch(e){{}}
}}
(function(){{ try{{ if(localStorage.getItem("mtlib_hideheb")==="1"){{
  document.body.classList.add("hide-heb");
  document.getElementById("hebtgl").textContent = "Mostrar {_lbl}";
}} }}catch(e){{}} }})();
</script>"""
        # The source language is per-BOOK: the Tanakh is translated from the Hebrew,
        # the New Testament from the Greek. This description was hardcoded to "desde
        # el hebreo" and so told every Spanish reader of Lucas/Marcos/Hechos/Romanos
        # that a Greek letter had been translated out of Hebrew. The divine-name note
        # is likewise OT-only: the NT's Greek reads kyrios, and this translation
        # prints "Señor" there (see the 1 Corinthians 1:24 / Acts 1:24 notes).
        _es_src = "el griego" if _is_nt(book) else "el hebreo"
        # 2026-08-01: the Spanish twin used to ship ONE hand-written boilerplate
        # description on every chapter -- 178 characters, past the truncation
        # limit, and identical across all 130 pages, so a search result for
        # Éxodo 20 and one for Salmo 23 read exactly the same. Now it comes from
        # the chapter's own Spanish teaser through the same _meta_desc() the
        # English side uses, and a new chapter inherits it for free.
        _es_raw = TEASERS_ES.get(slug)
        if _es_raw:
            _es_desc = _meta_desc(book, num, _es_raw, _es_src, lang="es", label=es_title)
        else:
            _es_name = "" if _is_nt(book) else " El Nombre: \u00abJehov\u00e1\u00bb."
            _es_desc = (f"{es_title}: una traducci\u00f3n nueva desde {_es_src}, vers\u00edculo por "
                        f"vers\u00edculo, con notas del traductor.{_es_name}")
        out = page(f"{es_title} — La Traducción Mister", body, lang="es",
                   url=es_file, desc=_es_desc)
        out = out.replace("</head>", _chapter_jsonld(book, num, _es_desc, es_file,
                                                     lang="es", label=es_title) + "\n</head>", 1)
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
    body = """<h1 class="pagetitle">\U0001F4D6 Dear Mr. Librarian</h1>
<p class="lede">Reader questions about the translation — a word-choice, the text, the canon, a comparison
between versions — answered one at a time, the way everything here is done: sourced, compared, and left for you to
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
    out = page(f"Dear Mr. Librarian — {SITE_NAME}", body, active="ask",
               desc="Reader questions about The MisterLibrarian Bible Project, answered one at a time — sourced, "
                    "compared, and left for you to weigh.", url="ask.html", og_type="website")
    open(os.path.join(OUT, "ask.html"), "w", encoding="utf-8").write(out)


def build_ask_jesus_god():
    """The exhaustive, balanced Dear Mr. Librarian post on John 1:1 and the deity of
    Christ. Presents BOTH the subordinationist/unitarian case and the full-deity case
    at full strength and declines to hand down a verdict — the project's 'catalogue,
    source, compare, don't preach' ethos. Edit this function to revise the post."""
    body = """<div class="askbar"><a href="ask.html">← Dear Mr. Librarian</a></div>
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
  of very God, a lesser divine being, or the first of creatures. On <em>that</em>, I set the two cases side by side, as above, and hands the scales to you.</p>
  <p class="muted" style="margin-top:6px">Read the verse in place, with its note: <a href="john-1.html#v1">John
  1:1</a>. The manuscripts behind 1:18 and 1:34: the <a href="new-testament.html">New Testament introduction</a>.
  More questions become posts here — <a href="contact.html">send yours to the librarian's desk</a>.</p>
</div>

<div class="panel" style="margin-top:14px">
  <p class="muted" style="margin:0 0 12px">More from <a href="ask.html">Dear Mr. Librarian</a>:
  <a href="ask-enoch.html">Why isn't the Book of Enoch in this translation?</a></p>
  <a class="btn" href="contact.html">✉️ Ask Mr. Librarian a question</a>
</div>"""
    out = page(f"Dear Mr. Librarian: was the Word God, or a god? — {SITE_NAME}", body, active="ask",
               desc="John 1:1 and the deity of Christ: the Greek grammar of the missing article (Colwell, "
                    "Harner), the three readings, 'firstborn of all creation,' the Angel of Jehovah and Michael "
                    "the archangel, the earliest manuscripts, and the whole case on both sides — laid out, not "
                    "settled.", url="ask-jesus-god.html")
    open(os.path.join(OUT, "ask-jesus-god.html"), "w", encoding="utf-8").write(out)


def build_ask_jehovah():
    """Dear Mr. Librarian post explaining the divine-name choice: the Tetragrammaton,
    why nearly every Bible hides it behind 'the LORD,' Yahweh vs. Jehovah, and why this
    project restores the traditional English form 'Jehovah.'"""
    body = """<div class="askbar"><a href="ask.html">← Dear Mr. Librarian</a></div>
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
  <a href="ask.html">Dear Mr. Librarian</a>: <a href="ask-jesus-god.html">Was the Word God, or a god?</a> &middot;
  <a href="ask-enoch.html">Why isn&rsquo;t the Book of Enoch here?</a></p>
  <a class="btn" href="contact.html">✉️ Ask Mr. Librarian a question</a>
</div>"""
    out = page(f"Dear Mr. Librarian: why “Jehovah”? — {SITE_NAME}", body, active="ask",
               desc="The divine name in this translation: the Tetragrammaton (YHWH), why nearly every Bible hides "
                    "it behind 'the LORD,' the difference between 'Yahweh' and 'Jehovah,' and why this project "
                    "restores the traditional English form 'Jehovah.'", url="ask-jehovah.html")
    open(os.path.join(OUT, "ask-jehovah.html"), "w", encoding="utf-8").write(out)


def build_ask_creation_days():
    """Dear Mr. Librarian post on the length of the creation 'days' — the word yom,
    the internal signals of Genesis 1, the ordinary-day / day-age / framework
    readings with their pedigrees, and the honest 'isn't this just bending the Bible
    to fit science?' question. Companion to the Genesis 1 v5 note and the yom
    dictionary entry. Neutrality habit: lay out the views, don't cast a vote."""
    body = """<div class="askbar"><a href="ask.html">← Dear Mr. Librarian</a></div>
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

<div class="askbar askbar-foot"><a href="ask.html">← More from Dear Mr. Librarian</a></div>"""
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
<a href="ask-enoch.html">Dear Mr. Librarian</a> posts (anonymously unless you say otherwise), and reader
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
                    "good questions become Dear Mr. Librarian posts.", url="contact.html", og_type="website")
    open(os.path.join(OUT, "contact.html"), "w", encoding="utf-8").write(out)


def build_thanks():
    body = """<h1 class="pagetitle">📬 It's on the librarian's desk</h1>
<div class="panel prose">
  <p><strong>Your question is in.</strong> Thank you — reader questions are the lifeblood of the
  <a href="ask-enoch.html">Dear Mr. Librarian</a> series, and every one gets read. If yours becomes a post,
  it will appear anonymously unless you asked otherwise; if you left an email, you may get a reply
  directly.</p>
  <p>Meanwhile, the shelves are open: the <a href="toc.html">Table of Contents</a> has every chapter
  published so far.</p>
</div>"""
    out = page(f"Question received — {SITE_NAME}", body,
               desc="Your question is on Mr. Librarian's desk.", url="thanks.html", og_type="website")
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
               desc="Tu pregunta está en el escritorio de Mr. Librarian.", url="thanks.es.html",
               og_type="website")
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
                    "growing chapter by chapter.", url="chronology.html")
    open(os.path.join(OUT, "chronology.html"), "w", encoding="utf-8").write(out)


def check_library_slug_collisions():
    """One slug, one entry. The per-word page is built from
    {d[0]: d for d in DICTIONARY}, so a repeated slug SILENTLY DISCARDS the earlier
    entry while the dictionary index still lists the word twice, with two different
    definitions. Added 2026-07-29 after a reader question about parthenos surfaced
    six collisions (parthenos, phronimos, hypokrites, eikon, diakonos, skandalon) —
    every one of them a later sitting re-coining a term an earlier book had already
    catalogued, and the term count overstated by six as a result. Nothing in the
    build noticed, because both entries were individually well-formed."""
    from collections import Counter
    dupes = {s: n for s, n in Counter(e[0] for e in DICTIONARY).items() if n > 1}
    if dupes:
        raise SystemExit("LIBRARY SLUG COLLISION — one slug, one entry:" + chr(10)
            + chr(10).join("  %s: %d entries" % (s, n) for s, n in sorted(dupes.items()))
            + chr(10) + "(a term catalogued for an earlier book is already there — EXTEND that"
            + chr(10) + " entry to cover the new passage instead of adding a second one)")


def check_library_parity():
    """Every library addition ships in BOTH languages, or the build says so.

    The Spanish twin is a first-class page, not a courtesy: a term coined for a
    chapter that never gets a DICTIONARY_ES entry is invisible to half the site,
    and an ENCYCLOPEDIA place with no ENCYCLOPEDIA_ES entry drops out of the
    Spanish atlas silently. Added 2026-07-30 after an audit of one night's six
    chapters found John 3 had shipped two terms (apeitheo, phaulos) and one
    person (nicodemus) English-only, and 1 Corinthians 13 nearly shipped with
    corinth/paul untranslated.

    This is a WARNING, not a build failure, because the legacy backlog is large
    (most of the 684-term dictionary predates the Spanish library). It fails only
    on terms and entries anchored to chapters the site has shipped SINCE the
    Spanish library existed, which is the set a chapter author actually controls."""
    SINCE = 2026  # the Spanish library landed 2026-07-25; everything after is in scope
    shipped = {(b, n) for _, b, n, _ in CHAPTERS}
    dict_gap, ency_gap = [], []
    for d in DICTIONARY:
        ref = d[5] if len(d) > 5 else None
        if isinstance(ref, (list, tuple)) and len(ref) == 3 and tuple(ref[:2]) in {(b, n) for b, n in shipped}:
            if d[0] not in DICTIONARY_ES:
                dict_gap.append(f"{d[0]} ({ref[0]} {ref[1]}:{ref[2]})")
    for e in ENCYCLOPEDIA:
        if e["slug"] not in ENCYCLOPEDIA_ES:
            ency_gap.append(e["slug"])
    if dict_gap or ency_gap:
        print(f"   \u26a0 library parity: {len(dict_gap)} dictionary term(s) and "
              f"{len(ency_gap)} encyclopedia entr(ies) have no Spanish")
        if dict_gap:
            head = ", ".join(sorted(dict_gap)[:8])
            more = " \u2026" if len(dict_gap) > 8 else ""
            print("     dict \u2192 " + head + more)
        if ency_gap:
            head = ", ".join(sorted(ency_gap)[:8])
            more = " \u2026" if len(ency_gap) > 8 else ""
            print("     ency \u2192 " + head + more)
    return len(dict_gap), len(ency_gap)


def check_canonicals():
    """Every URL in the sitemap must match the canonical its page declares.

    Runs on the BUILT output, at the end, because that is the only point the
    two are comparable. Added 2026-08-01 after Search Console reported the home
    page as "Duplicate without user-selected canonical": we were submitting
    /index.html while Google had chosen the bare directory form, so the
    submitted URL was discarded. Silent by nature — the sitemap reports
    success and the page looks fine.

    Cheap: ~1,900 local reads of the first 2 KB of each file."""
    sm = os.path.join(OUT, "sitemap.xml")
    if not os.path.exists(sm):
        return
    bad = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", open(sm, encoding="utf-8").read()):
        rel = loc[len(SITE_URL) + 1:] or "index.html"
        fp = os.path.join(OUT, rel)
        if not os.path.exists(fp):
            bad.append(f"  {loc}: submitted but no such file was built")
            continue
        head = open(fp, encoding="utf-8").read(4000)
        m = re.search(r'<link rel="canonical" href="([^"]+)"', head)
        if m and m.group(1) != loc:
            bad.append(f"  {loc}: canonical disagrees -> {m.group(1)}")
    if bad:
        raise SystemExit("Sitemap/canonical check failed — submitted URLs that "
                         "contradict their own pages:\n" + "\n".join(bad[:25]))


def check_seo(chapters):
    """Every chapter must carry its own search-facing metadata.

    Two of the three SEO pieces are structural and therefore automatic: the meta
    description is generated from the chapter's TEASER by _meta_desc(), and the
    Article/BreadcrumbList JSON-LD by _chapter_jsonld(). A new chapter inherits
    both simply by existing in CHAPTERS with a teaser. This guard exists so that
    stays true -- it fails the build if a chapter would ship with a description
    that is boilerplate-length, duplicated, or missing.

    Added 2026-07-31, after finding that all 180+ chapters had been shipping an
    IDENTICAL first ~140 characters ("... translated fresh from the Hebrew, with
    verse-by-verse notes comparing NIV, KJV ...") with the distinctive teaser
    appended AFTER the point search engines truncate -- so the only part that
    could earn a click was cut off on every page on the site.

    The third piece -- writing note headings that lead with the term a person
    would actually search for -- is editorial and cannot be checked mechanically.
    It lives in the per-chapter checklist."""
    seen, bad = {}, []
    for slug, book, num, teaser in CHAPTERS:
        src = "the Greek" if _is_nt(book) else "the Hebrew"
        d = _meta_desc(book, num, teaser, src)
        if len(d) < 90:
            bad.append(f"  {book} {num}: description only {len(d)} chars -- teaser too thin")
        if len(d) > 160:
            bad.append(f"  {book} {num}: description {len(d)} chars -- will be truncated")
        key = d[:60]
        if key in seen:
            bad.append(f"  {book} {num}: description opening duplicates {seen[key]}")
        seen[key] = f"{book} {num}"
    # 2026-08-01: the Spanish twin is now checked on the same terms. It had been
    # exempt from this guard, and had quietly shipped ONE identical 178-character
    # boilerplate description across all 130 of its chapter pages.
    seen_es = {}
    for slug, book, num, teaser in CHAPTERS:
        t_es = TEASERS_ES.get(slug)
        if not t_es:
            continue  # a missing Spanish teaser is already reported by the ES build
        label = f"{ES_BOOK.get(book, book)} {num}"
        d = _meta_desc(book, num, t_es, "el griego" if _is_nt(book) else "el hebreo",
                       lang="es", label=label)
        if len(d) < 90:
            bad.append(f"  {label} (es): description only {len(d)} chars -- teaser too thin")
        if len(d) > 160:
            bad.append(f"  {label} (es): description {len(d)} chars -- will be truncated")
        key = d[:60]
        if key in seen_es:
            bad.append(f"  {label} (es): description opening duplicates {seen_es[key]}")
        seen_es[key] = label
    if bad:
        raise SystemExit("SEO CHECK FAILED -- every chapter needs its own search-facing hook:\n"
                         + "\n".join(bad)
                         + "\n(the description is generated from the chapter's teaser in CHAPTERS; "
                           "give the chapter a real teaser and this passes)")


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


def check_sblgnt_sigla(chapters):
    """The SBLGNT source (source/originals/sblgnt/*.json, fetched via the
    bible.helloao.org API) embeds CRITICAL-APPARATUS SIGLA in its Greek text --
    Unicode Supplemental Punctuation marks (U+2E00-U+2E05: ⸀⸁ single-word
    variant markers, ⸂⸃⸄⸅ paired-span variant brackets) that anchor the
    accompanying footnotes. They exist to mark WHERE a textual variant sits for
    the apparatus, not to be read -- every chapter shipped before Matthew 16 is
    clean of them (a full scan of all 260 archived NT chapter files found only
    these six sigla in use, nothing broader). Added 2026-07-28 after a chapter
    almost shipped with four of them still sitting in the Greek, copy-pasted
    straight from the source JSON and caught only by a manual byte-comparison
    against the previous chapter's clean text -- this makes that comparison
    automatic and permanent, the same way check_shelf_density did for shelf
    comparisons. Scoped to <div class="grk"> content specifically, so it can
    never misfire on Hebrew (class="heb") chapters, which don't carry these
    marks at all."""
    SIGLA_LO, SIGLA_HI = 0x2E00, 0x2E7F   # the whole Supplemental Punctuation block
    bad = []
    for slug, body in chapters.items():
        for m in re.finditer(r'<div class="vrs" id="([^"]+)">.*?<div class="grk">([^<]*)</div>', body, re.S):
            vid, grk = m.group(1), m.group(2)
            sigla = sorted(set(ch for ch in grk if SIGLA_LO <= ord(ch) <= SIGLA_HI))
            if sigla:
                bad.append(f"  {slug} #{vid}: {''.join(sigla)}")
    if bad:
        raise SystemExit("SBLGNT SIGLA CHECK FAILED — critical-apparatus marks left in the Greek text:\n"
                         + "\n".join(bad)
                         + "\n(strip ⸀⸁⸂⸃⸄⸅ from the Greek before pasting into the source panel --"
                           " they anchor footnotes, they are not part of the reading text)")


def build_sitemap():
    """Write sitemap.xml for the main site.

    Until now this site had none at all — 320 indexable pages and no map handed to
    any search engine. (The travel blog has always had its own; the two stay
    separate and both are listed in robots.txt.)

    Three decisions worth keeping:

    * The 3,800+ /v/ verse stubs are EXCLUDED. They are `noindex` with a canonical
      pointing at their chapter and a meta-refresh on top — they exist to give a
      shared verse link its own card, not to be indexed. Listing noindex URLs in a
      sitemap is a reported error in Search Console, and 3,800 thin redirect pages
      would swamp the 320 real ones twelve to one.
    * `lastmod` comes from GIT, not the filesystem. Every build rewrites every
      file, so mtime would stamp today's date on all 320 pages every time — and a
      lastmod that is always "today" is one search engines learn to ignore. One
      `git log` pass gives the real date each page last changed.
    * No `priority` or `changefreq`. Google ignores both; emitting them is noise.

    Spanish pages are paired with their English twin via hreflang alternates, so a
    Spanish reader is offered the Spanish edition rather than either being treated
    as a duplicate of the other.
    """
    import subprocess
    pages = sorted(f for f in os.listdir(OUT)
                   if f.endswith(".html") and os.path.isfile(os.path.join(OUT, f)))
    # ency/ and dict/ hold real, indexable per-entry pages (unlike /v/'s noindex
    # redirect stubs above) -- they just live one level down, so os.listdir(OUT)
    # alone never sees them. Walked separately and added with their subdir prefix
    # so every downstream step (hreflang pairing via string-slicing, lastmod
    # lookup, the noindex sniff) treats "ency/seir.html" exactly like a root page.
    for sub in ("ency", "dict", "atlas", "routes"):
        subdir = os.path.join(OUT, sub)
        if os.path.isdir(subdir):
            pages += sorted(f"{sub}/{f}" for f in os.listdir(subdir) if f.endswith(".html"))

    # Real dates, one subprocess call. Recent history is plenty: anything older
    # than the window simply omits lastmod, which is better than inventing one.
    dates = {}
    try:
        log = subprocess.run(
            ["git", "-C", OUT, "log", "--format=%cI", "--name-only", "-n", "600"],
            capture_output=True, text=True, timeout=45).stdout
        cur = None
        for line in log.splitlines():
            if line[:2] == "20" and "T" in line:
                cur = line[:10]
            elif line.strip() and cur:
                dates.setdefault(line.strip(), cur)
    except Exception:
        pass                      # a sitemap without lastmod is still a fine sitemap

    entries = []
    for f in pages:
        try:
            head = open(os.path.join(OUT, f), encoding="utf-8").read(2500)
        except OSError:
            continue
        if 'name="robots" content="noindex' in head:
            continue              # never advertise a page we've asked not to index

        # Must match the canonical the page declares — see the note in the head
        # builder. Submitting /index.html while the page canonicalises to / is
        # how the home page ended up as a "Duplicate without user-selected
        # canonical" in Search Console.
        loc = f"{SITE_URL}/" if f == "index.html" else f"{SITE_URL}/{f}"
        alts = []
        if f.endswith(".es.html"):
            en = f[:-8] + ".html"
            if en in pages:
                alts = [("es", loc), ("en", f"{SITE_URL}/{en}")]
        else:
            es = f[:-5] + ".es.html"
            if es in pages:
                alts = [("en", loc), ("es", f"{SITE_URL}/{es}")]

        row = [f"  <url><loc>{loc}</loc>"]
        if f in dates:
            row.append(f"<lastmod>{dates[f]}</lastmod>")
        for lang, href in alts:
            row.append(f'<xhtml:link rel="alternate" hreflang="{lang}" href="{href}"/>')
        row.append("</url>")
        entries.append("".join(row))

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
           + "\n".join(entries) + "\n</urlset>\n")
    open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8").write(xml)
    return len(entries)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=DEFAULT_SOURCE)
    args = ap.parse_args()
    chapters = extract_source(args.source)
    check_shelf_density(chapters)
    check_library_parity()
    check_seo(chapters)
    check_entry_seo()
    check_sblgnt_sigla(chapters)
    check_library_slug_collisions()
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
    n_places, n_people, n_things = build_encyclopedia()
    build_dictionary_entry_pages()
    build_encyclopedia_entry_pages()
    n_mapped, n_atlas_places = build_atlas()
    build_atlas_entry_pages()
    build_route_pages()
    build_library((n_words, n_refs, n_dict, n_places, n_people, n_things, len(XREFS), n_mapped, n_atlas_places))
    n_sitemap = build_sitemap()
    check_canonicals()
    check_built_descriptions()
    save_card_manifest()
    report_card_budget()
    print(f"built {len(CHAPTERS)} chapters + core pages + library "
          f"(concordance {n_words}w/{n_refs}refs, dict {n_dict}, ency {n_places}p/{n_people}pp/{n_things}c, "
          f"atlas {n_mapped}/{n_atlas_places} mapped, xrefs {len(XREFS)}), sitemap {n_sitemap} urls from {args.source}")


if __name__ == "__main__":
    main()
