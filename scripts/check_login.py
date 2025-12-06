import urllib.request, urllib.error
u='http://127.0.0.1:8000/accounts/login/'
req=urllib.request.Request(u, headers={'Accept':'text/html'})
try:
    r=urllib.request.urlopen(req, timeout=10)
    print('OK', r.getcode())
    print(r.read(4000).decode('utf-8',errors='replace'))
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8',errors='replace')
    print('HTTPError', e.code)
    print(body[:8000])
except Exception as e:
    print('ERR', e)
