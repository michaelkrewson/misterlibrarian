# -*- coding: utf-8 -*-
"""The priority order for the chapters Mister Translation has not translated yet.

WHY THIS IS A FILE OF DATA, NOT A STATUS PARAGRAPH. "What is left" changes every time a chapter
ships, so the remaining list is always computed from CHAPTERS in build.py (see tools/next_chapter.py).
This file holds only the part that is a judgment and does not change: the ORDER.

HOW THE ORDER WAS MADE (2026-11-16). No public dataset ranks Bible CHAPTERS by search demand. What
exists is verse-level and per-year, and it points one way: Bible Gateway's year-end lists are almost
all Psalm 23 and Psalm 91; YouVersion's top verses of recent years include Isaiah 41:10 and
Philippians 4:6; Bible Gateway's all-time most-searched verses are John 3:16 and Jeremiah 29:11; the
Psalms are the most-read book. By the time this list was written those chapters, and most of the New
Testament, were already on the site (Psalms 1, 23, 27, 34, 37, 46, 51, 91, 100, 103, 119, 121, 139;
Proverbs 3 and 31; Isaiah 40, 41, 53; Jeremiah 29; Daniel 1-4). So the order below is the remaining
famous chapters, ranked by my judgment of how often people look them up by name or quote a line from
them, with that evidence as the tiebreaker. It is an ESTIMATE, not a measurement.

TO REPLACE THE ESTIMATE WITH MEASUREMENT: export Search Console's Queries.csv (Performance ->
Export) and run `python3 tools/next_chapter.py --gsc Queries.csv`; chapters people already search the
site for jump the queue.
"""

# (book, chapter), in rank order. Tier boundaries are in TIERS below; the reason strings are for the
# top of the list, where a reader of the card will want to know why.
TOP = [
    # ---- Tier 1: names people type into a search box --------------------------------------------
    ("Psalms", 22, "'My God, my God, why have you forsaken me'; read on Good Friday in many churches"),
    ("Isaiah", 43, "'Fear not, for I have redeemed you'; 'through the waters'"),
    ("Psalms", 150, "the last psalm; 'let everything that has breath praise'"),
    ("Psalms", 118, "'this is the day Jehovah has made'; 'the stone the builders rejected'"),
    ("Isaiah", 55, "'Ho, everyone who thirsts'; 'my thoughts are not your thoughts'"),
    ("Psalms", 19, "'the heavens declare the glory of God'"),
    ("Isaiah", 6, "'Here am I, send me'; the seraphim"),
    ("Psalms", 8, "'what is man that you are mindful of him'"),
    ("Isaiah", 9, "'unto us a child is born'; read at Advent"),
    ("Psalms", 130, "'out of the depths'"),
    ("2 Chronicles", 7, "7:14, 'if my people who are called by my name'"),
    ("Psalms", 90, "'teach us to number our days'; Moses's psalm"),
    ("Isaiah", 61, "'the Spirit of the Lord is upon me'; Jesus reads it at Nazareth"),
    ("Psalms", 63, "'my soul thirsts for you'"),
    ("Psalms", 42, "'as the deer pants for streams of water'"),
    ("Ezekiel", 37, "the valley of dry bones"),
    ("Daniel", 6, "the lions' den"),
    ("Job", 38, "'where were you when I laid the foundations of the earth'"),
    ("Isaiah", 11, "the shoot from Jesse; the wolf and the lamb"),
    ("Psalms", 138, "'I give you thanks with all my heart'"),
    ("Isaiah", 58, "the fast that God chooses"),
    ("Esther", 4, "'for such a time as this'"),
    ("Psalms", 24, "'the earth is Jehovah's and everything in it'"),
    ("Isaiah", 54, "54:17, 'no weapon formed against you'"),
    ("Joel", 2, "'I will restore the years the locust has eaten'; the outpouring of the Spirit"),
    ("Malachi", 3, "3:10, tithes; 'the messenger of the covenant'"),
    ("Psalms", 25, "'to you, Jehovah, I lift up my soul'"),
    ("Psalms", 32, "'blessed is the one whose transgression is forgiven'"),
    ("Daniel", 9, "Daniel's prayer; the seventy weeks"),
    ("Psalms", 40, "'he lifted me out of the slimy pit'"),
    # ---- Tier 2: well known, searched by passage or by story ------------------------------------
    ("Job", 42, "the end of Job; 'now my eye sees you'"),
    ("Ecclesiastes", 12, "'remember your Creator in the days of your youth'"),
    ("Nehemiah", 8, "Ezra reads the law; 'the joy of Jehovah is your strength'"),
    ("Micah", 5, "Bethlehem Ephrathah; read at Advent"),
    ("Zephaniah", 3, "3:17, 'he will rejoice over you with singing'"),
    ("1 Chronicles", 4, "the prayer of Jabez"),
    ("Isaiah", 14, "'how you have fallen from heaven, morning star'"),
    ("Daniel", 5, "the writing on the wall"),
    ("Daniel", 7, "the four beasts; 'one like a son of man'"),
    ("Isaiah", 35, "'the desert shall rejoice'"),
    ("Psalms", 145, "'great is Jehovah and most worthy of praise'"),
    ("Psalms", 62, "'my soul finds rest in God alone'"),
    ("Psalms", 18, "David's song of deliverance"),
    ("Psalms", 2, "'why do the nations rage'"),
    ("Jeremiah", 17, "17:7-8, the tree by the water; 'the heart is deceitful'"),
    ("Jeremiah", 33, "'call to me and I will answer you'"),
    ("Ezekiel", 36, "'a new heart I will give you'"),
    ("Ezekiel", 34, "the shepherds of Israel; 'I myself will shepherd my sheep'"),
    ("Isaiah", 60, "'arise, shine, for your light has come'"),
    ("Isaiah", 49, "the servant, light to the nations; 'can a woman forget her nursing child'"),
    ("Song of Solomon", 2, "'I am the rose of Sharon'; 'my beloved is mine'"),
    ("Song of Solomon", 8, "'love is as strong as death'"),
    ("Ecclesiastes", 9, "'whatever your hand finds to do'; 'the race is not to the swift'"),
    ("Ecclesiastes", 7, "'a good name is better than precious oil'"),
    ("Job", 19, "'I know that my Redeemer lives'"),
    ("Job", 14, "'if a man dies, shall he live again?'"),
    ("Proverbs", 6, "the sluggard; the six things Jehovah hates"),
    ("Proverbs", 15, "'a soft answer turns away wrath'"),
    ("Proverbs", 14, "'there is a way that seems right to a man'"),
    ("Proverbs", 27, "'iron sharpens iron'"),
    ("Proverbs", 10, "the first of the sayings of Solomon"),
    ("Proverbs", 12, "'whoever loves discipline loves knowledge'"),
    ("Proverbs", 11, "'a false balance is an abomination'"),
    ("Proverbs", 17, "'a friend loves at all times'"),
    ("Proverbs", 19, "'many are the plans in the mind of a man'"),
    ("Proverbs", 20, "'wine is a mocker'"),
    ("Proverbs", 23, "'do not wear yourself out to get rich'; 'as he thinks in his heart'"),
    ("Proverbs", 30, "Agur's sayings; 'give me neither poverty nor riches'"),
    ("Ezekiel", 28, "the king of Tyre"),
    ("Ezekiel", 18, "'the soul who sins shall die'"),
    ("Ezekiel", 47, "the river from the temple"),
    ("2 Kings", 19, "Hezekiah and Sennacherib"),
    ("2 Kings", 22, "the book of the law found"),
    ("1 Chronicles", 16, "David's psalm of thanksgiving"),
    ("1 Chronicles", 17, "the Davidic covenant"),
    ("2 Chronicles", 20, "'the battle is not yours but God's'; Jehoshaphat"),
    ("Nehemiah", 2, "rebuilding the wall begins"),
    ("Nehemiah", 4, "'the people had a mind to work'"),
    ("Jonah", 2, "Jonah's prayer from the fish"),
    ("Jonah", 3, "Nineveh repents"),
    ("Jonah", 4, "'should I not pity Nineveh'"),
    ("Hosea", 11, "'when Israel was a child'"),
    ("Hosea", 6, "'I desire mercy, not sacrifice'"),
    ("Amos", 5, "'let justice roll down like waters'"),
    ("Zechariah", 9, "the king riding on a donkey"),
    ("Zechariah", 12, "'they will look on me, the one they have pierced'"),
    ("Zechariah", 14, "the day of Jehovah; the mount of Olives splits"),
    ("Malachi", 4, "'the sun of righteousness'; Elijah before the day"),
    ("Psalms", 133, "'how good and pleasant when brothers dwell together'"),
    ("Psalms", 95, "'come, let us sing to Jehovah'"),
    ("Psalms", 4, "'in peace I will lie down and sleep'"),
    ("Psalms", 16, "'you will not abandon my soul to Sheol'"),
    ("Psalms", 33, "'by the word of Jehovah the heavens were made'"),
    ("Psalms", 73, "'surely God is good to Israel'"),
    ("Psalms", 84, "'how lovely is your dwelling place'"),
    ("Psalms", 110, "'sit at my right hand' (110:1), a verse the New Testament quotes again and again"),
    ("Psalms", 136, "'his steadfast love endures forever'"),
    ("Psalms", 143, "'teach me to do your will'"),
    ("Psalms", 20, "'some trust in chariots'"),
    ("Psalms", 30, "'weeping may tarry for the night'"),
    ("Psalms", 31, "'into your hand I commit my spirit'"),
    ("Psalms", 57, "'my heart is steadfast'"),
    ("Psalms", 61, "'lead me to the rock that is higher than I'"),
    ("Psalms", 67, "'may God be gracious to us and bless us'"),
    ("Psalms", 96, "'sing to Jehovah a new song'"),
    ("Psalms", 98, "'sing to Jehovah a new song, for he has done marvelous things'"),
    ("Psalms", 107, "'let the redeemed of Jehovah say so'"),
    ("Psalms", 126, "'those who sow in tears'"),
    ("Psalms", 127, "'unless Jehovah builds the house'"),
    ("Psalms", 128, "'blessed is everyone who fears Jehovah'"),
    ("Psalms", 148, "'praise Jehovah from the heavens'"),
    ("Psalms", 149, "'sing to Jehovah a new song'"),
    ("Isaiah", 25, "'he will swallow up death forever'"),
    ("Isaiah", 52, "'how beautiful on the mountains'"),
    ("Isaiah", 64, "'we are the clay, you are the potter'"),
    ("Isaiah", 65, "'new heavens and a new earth'"),
    ("Isaiah", 2, "'they shall beat their swords into plowshares'"),
    ("Isaiah", 5, "the song of the vineyard; 'woe to those who call evil good'"),
    ("Isaiah", 12, "'with joy you will draw water from the wells of salvation'"),
    ("Isaiah", 66, "the last chapter of Isaiah"),
    ("Daniel", 8, "the ram and the goat"),
    ("Daniel", 10, "the man clothed in linen; Michael"),
    ("Esther", 2, "Esther becomes queen"),
    ("Esther", 3, "Haman's plot"),
    ("Esther", 7, "Haman exposed"),
    ("Esther", 5, "Esther approaches the king"),
    ("Esther", 6, "the king cannot sleep"),
    ("Job", 28, "'where shall wisdom be found?'"),
    ("Job", 3, "'let the day perish on which I was born'"),
    ("Job", 2, "the second test"),
    ("Job", 40, "Behemoth begins"),
    ("Job", 41, "Leviathan"),
    ("Lamentations", 4, "the last of the acrostics before the prayer"),
    ("Lamentations", 5, "'restore us to yourself, Jehovah'"),
    ("Ecclesiastes", 2, "'I made great works'"),
    ("Ecclesiastes", 4, "'two are better than one'; 'a threefold cord'"),
    ("Ecclesiastes", 5, "'let your words be few'"),
    ("Ecclesiastes", 11, "'cast your bread upon the waters'"),
    ("Song of Solomon", 4, "'you are altogether beautiful'"),
    ("Song of Solomon", 5, "the lover at the door"),
    ("Jeremiah", 10, "against the idols of the nations"),
    ("Jeremiah", 7, "the temple sermon; 'a den of robbers'"),
    ("Jeremiah", 32, "the field at Anathoth bought"),
    ("Jeremiah", 9, "'let not the wise boast of his wisdom'"),
    ("Ezekiel", 16, "the foundling bride"),
    ("Ezekiel", 3, "the watchman"),
    ("Ezekiel", 10, "the glory leaves the temple"),
    ("Ezekiel", 40, "the vision of the new temple begins"),
]

TIERS = [
    (1, 30, "Tier 1 - names people type into a search box, or a line everybody quotes"),
    (31, None, "Tier 2 - well known by passage or by story, then the rest of the famous Psalms, Proverbs, Isaiah, Job and the prophets"),
]  # a None end means "to the end of TOP"

# Everything not in TOP follows, ordered by book weight (descending) then chapter number.
# A heavier book comes first: more people read it, so a gap in it costs more.
BOOK_WEIGHT = {
    "Psalms": 10, "Isaiah": 9, "Proverbs": 9, "Job": 8, "Ecclesiastes": 8, "Daniel": 8,
    "Song of Solomon": 7, "Jeremiah": 7, "Jonah": 7, "Ezekiel": 6, "Esther": 6, "Nehemiah": 6,
    "Joel": 5, "Amos": 5, "Micah": 5, "Malachi": 5, "Zechariah": 5, "Hosea": 5, "Lamentations": 5,
    "2 Kings": 5, "2 Chronicles": 4, "1 Chronicles": 4, "Nahum": 4, "Zephaniah": 4, "Haggai": 4,
    "Ezra": 3,
}

# Spanish-only backfill: chapters already live in English with no Spanish twin. Order = demand,
# except that Genesis 15-33 is kept in book order (the Spanish pages of later chapters quote the
# earlier ones, so each has to supply what the next one cites).
ES_BACKFILL_ORDER = (
    [("Matthew", 10), ("Matthew", 9), ("Daniel", 12), ("Daniel", 11), ("Daniel", 1)]
    + [("Genesis", c) for c in range(15, 34)]
    + [("Jeremiah", 19), ("Jeremiah", 20), ("Jeremiah", 21), ("Jeremiah", 22)]
)
