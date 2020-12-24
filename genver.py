from urllib import request

req = request.Request('https://github.com/nginx/nginx/releases')
resp = request.urlopen(req).read().decode()
l = resp.find('nginx-') + 6
r = resp.find('-RELEASE', l)
print('export _nginxver=%s' % resp[l:r])
req = request.Request('https://github.com/openssl/openssl/releases')
resp = request.urlopen(req).read().decode()
l = resp.find('OpenSSL_') + 8
r = resp.find('"', l)
print('export _opensslver=%s' % resp[l:r])
req = request.Request('https://zlib.net')
resp = request.urlopen(req).read().decode()
l = resp.find('Current release')
l = resp.find('zlib ', l) + 5
r = resp.find('<', l)
print('export _zlibver=%s' % resp[l:r])
