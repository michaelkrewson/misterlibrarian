// Shared reading-progress helpers for The MisterLibrarian Bible Project.
// Everything lives in the reader's own browser via localStorage — nothing is
// ever sent anywhere, no account needed. Key: 'mtlib_read', a map of
// chapter slug -> true for every chapter the reader has checked off.
function mtlibGetRead(){
  try{ return JSON.parse(localStorage.getItem('mtlib_read') || '{}'); }
  catch(e){ return {}; }
}
function mtlibSetRead(slug, val){
  var r = mtlibGetRead();
  if (val) r[slug] = true; else delete r[slug];
  try{ localStorage.setItem('mtlib_read', JSON.stringify(r)); }catch(e){}
  return r;
}
