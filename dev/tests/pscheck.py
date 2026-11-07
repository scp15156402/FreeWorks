import re,sys
def check(path):
    s=open(path,encoding='utf-8').read()
    s=re.sub(r'<#.*?#>', '', s, flags=re.S); s=re.sub(r'@"\n.*?\n"@', '""', s, flags=re.S)
    stack=[]; i=0; line=1; n=len(s); errs=[]; pairs={'(':')','{':'}','[':']'}
    while i<n:
        c=s[i]
        if c=='\n': line+=1
        if c=='#':
            while i<n and s[i]!='\n': i+=1
            continue
        if c in '"\'':
            q=c; i+=1
            while i<n:
                if s[i]=='\n': line+=1
                if q=='"' and s[i]=='`': i+=2; continue
                if s[i]==q:
                    if i+1<n and s[i+1]==q: i+=2; continue
                    break
                i+=1
            i+=1; continue
        if c=='`': i+=2; continue
        if c in pairs: stack.append((c,line))
        elif c in ')}]':
            if not stack or pairs[stack[-1][0]]!=c: errs.append('line %d'%line)
            else: stack.pop()
        i+=1
    ok = not errs and not stack
    print(path, 'OK' if ok else (errs[:3], stack[-3:]))
    return ok
sys.exit(0 if all([check(f) for f in sys.argv[1:]]) else 1)
