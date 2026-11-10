import re
_cache={}
def find_page(txtfile, phrase):
    """Tryckt sidnummer (=PDF-sida i dessa propositioner) där frasen (blankstegsnormaliserad) börjar."""
    if txtfile not in _cache: _cache[txtfile]=open(txtfile).read().split('\f')
    P=_cache[txtfile]
    norm=lambda s: re.sub(r'\s+',' ',re.sub(r'-\s*\n\s*','',s))
    ph=norm(phrase)[:60]
    for i,p in enumerate(P):
        if ph in norm(p): return i+1
    # över sidbrytning
    for i in range(len(P)-1):
        if ph in norm(P[i][-400:]+' '+P[i+1][:400]): return i+1
    return None
