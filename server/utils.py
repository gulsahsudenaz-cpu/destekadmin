import secrets, string

def make_cid(name: str):
    suf = ''.join(secrets.choice(string.hexdigits.upper()) for _ in range(4))
    return f"{(name or 'Misafir').split()[0]}-{suf}"

def ensure_cid(room, name, cid_maker):
    """Deprecated: use get_or_create_chat instead"""
    return cid_maker(name)
