-- m8k.io site-wide search (2026-10-10). Cloudflare D1 database "m8k-search".
-- One row per public page (from every sitemap) + an FTS5 full-text index kept in
-- sync by triggers. Rebuilt incrementally by tools/build_search_index.py.
CREATE TABLE IF NOT EXISTS docs (
  url   TEXT PRIMARY KEY,   -- canonical public URL
  pub   TEXT NOT NULL,      -- bible | ask | ledger | notebook | regimen | abroad | west
  kind  TEXT NOT NULL,      -- chapter | book | answer | post | board | reference | page
  lang  TEXT NOT NULL,      -- en | es
  title TEXT NOT NULL,
  descr TEXT NOT NULL DEFAULT '',
  body  TEXT NOT NULL DEFAULT '',
  date  TEXT NOT NULL DEFAULT '',
  hash  TEXT NOT NULL
);
CREATE VIRTUAL TABLE IF NOT EXISTS docs_fts USING fts5(
  title, descr, body,
  content='docs', content_rowid='rowid',
  tokenize='porter unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS docs_ai AFTER INSERT ON docs BEGIN
  INSERT INTO docs_fts(rowid, title, descr, body) VALUES (new.rowid, new.title, new.descr, new.body);
END;
CREATE TRIGGER IF NOT EXISTS docs_ad AFTER DELETE ON docs BEGIN
  INSERT INTO docs_fts(docs_fts, rowid, title, descr, body) VALUES ('delete', old.rowid, old.title, old.descr, old.body);
END;
CREATE TRIGGER IF NOT EXISTS docs_au AFTER UPDATE ON docs BEGIN
  INSERT INTO docs_fts(docs_fts, rowid, title, descr, body) VALUES ('delete', old.rowid, old.title, old.descr, old.body);
  INSERT INTO docs_fts(rowid, title, descr, body) VALUES (new.rowid, new.title, new.descr, new.body);
END;
