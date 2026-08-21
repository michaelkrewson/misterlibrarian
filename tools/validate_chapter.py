# -*- coding: utf-8 -*-
"""Compose-time link validator: run BEFORE splicing a drafted chapter panel in.

    python3 tools/validate_chapter.py /tmp/num21_en.html
    python3 tools/validate_chapter.py /tmp/num21_es.html      # .es. in the name = Spanish

Exists because the same defect class has now been caught in five consecutive
chapters (Leviticus 1 and Genesis 4/6 bare anchors, an invented `t-rva` tag,
dictionary anchors that did not exist yet, a link to an unpublished chapter,
Spanish notes citing chapters with no Spanish page). A remembered discipline
kept failing; a forty-line script does not.

Checks, for a drafted panel fragment:
  1. every href="<file>.html#<anchor>" resolves against the REAL panel in the source
     (or the real .es.html file), with the target's actual v*/n* ids printed on a miss
  2. every dictionary.html#slug  / diccionario.html#slug  exists in DICTIONARY / DICTIONARY_ES
  3. every encyclopedia.html#slug / enciclopedia.html#slug exists in ENCYCLOPEDIA / ENCYCLOPEDIA_ES
  4. every `class="tag t-*"` is a class that actually exists in style.css
  5. a Spanish note may not cite a chapter that has no Spanish page
"""
import io, re, sys, os
sys.path.insert(0, '.')
import library_data as L

frag_path = sys.argv[1]
LANG = 'es' if frag_path.endswith('.es.html') or '.es.' in frag_path else 'en'
frag = io.open(frag_path, encoding='utf-8').read()

SRC = io.open('source/mister_translation.html', encoding='utf-8').read()
CSS = io.open('style.css', encoding='utf-8').read()
DICT = {e[0] for e in L.DICTIONARY}
DICT_ES = set(L.DICTIONARY_ES)
ENCY = {e['slug'] for e in L.ENCYCLOPEDIA}
ENCY_ES = set(L.ENCYCLOPEDIA_ES)
TAGS = set(re.findall(r'\.(t-[a-z0-9]+)', CSS))

# slug for each chapter page file name, e.g. numbers-13.html -> num13
import build as B  # noqa: E402  (build.py holds CHAPTERS)

def file_to_slug(fn):
    base = fn[:-5] if fn.endswith('.html') else fn
    if base.endswith('.es'):
        base = base[:-3]
    for slug, book, ch, _ in B.CHAPTERS:
        if "%s-%d" % (book.lower().replace(' ', '-'), ch) == base:
            return slug
    return None

def panel_ids(slug):
    m = re.search(r'<div class="chapter-panel[^"]*" id="chapter-%s">(.*?)</div><!-- /chapter-%s -->'
                  % (slug, slug), SRC, re.S)
    if not m:
        return None
    return set(re.findall(r'id="([vn][0-9a-z\-]+)"', m.group(1)))

# ids inside the fragment itself (self-references)
SELF_IDS = set(re.findall(r'id="([vn][0-9a-z\-]+)"', frag))

problems = []
checked = 0

for m in re.finditer(r'href="([^"]+)"', frag):
    href = m.group(1)
    checked += 1
    if href.startswith('#'):
        if href[1:] not in SELF_IDS:
            problems.append("SELF-ANCHOR %s not in this fragment" % href)
        continue
    if href.startswith('http'):
        continue
    file, _, anchor = href.partition('#')
    base = file.split('.')[0]
    if base in ('dictionary', 'diccionario'):
        pool, name = (DICT, 'DICTIONARY') if base == 'dictionary' else (DICT_ES, 'DICTIONARY_ES')
        if anchor not in pool:
            problems.append("DEAD DICT LINK %s (not in %s)" % (href, name))
        continue
    if base in ('encyclopedia', 'enciclopedia'):
        pool, name = (ENCY, 'ENCYCLOPEDIA') if base == 'encyclopedia' else (ENCY_ES, 'ENCYCLOPEDIA_ES')
        if anchor not in pool:
            problems.append("DEAD ENCY LINK %s (not in %s)" % (href, name))
        continue
    if base in ('atlas', 'concordance', 'concordancia', 'index', 'library', 'biblioteca'):
        continue
    # a chapter page
    slug = file_to_slug(file)
    if slug is None:
        problems.append("UNKNOWN CHAPTER FILE %s" % file)
        continue
    if file.endswith('.es.html'):
        # published as <name>.es.html, but the SOURCE file drops the .es infix
        src_name = file[:-8] + '.html'
        if not os.path.exists(os.path.join('source', 'es', src_name)):
            problems.append("NO SPANISH PAGE: %s (source/es/%s missing - cite as prose instead)"
                            % (file, src_name))
            continue
    ids = panel_ids(slug)
    if ids is None:
        problems.append("NO PANEL for %s (%s)" % (slug, file))
        continue
    if anchor and anchor not in ids:
        near = sorted(i for i in ids if i.startswith(anchor[0]))[:14]
        problems.append("BAD ANCHOR %s -> %s has no #%s ; real ids look like %s"
                        % (file, slug, anchor, near))

for t in sorted(set(re.findall(r'class="tag (t-[a-z0-9]+)"', frag))):
    if t not in TAGS:
        problems.append("INVENTED TAG CLASS %s (style.css has %s)" % (t, sorted(TAGS)))

print("%s: %d hrefs checked, %d shelf-tag classes" %
      (frag_path, checked, len(set(re.findall(r'class="tag (t-[a-z0-9]+)"', frag)))))
if problems:
    print("\n!! %d PROBLEM(S)" % len(problems))
    for p in problems:
        print("   -", p)
    sys.exit(1)
print("clean.")
