from urllib import request

with open('init.sh', 'a') as w:
  req = request.Request('https://github.com/nginx/nginx/releases')
  resp = request.urlopen(req).read().decode()
  l = resp.find('nginx-') + 6
  r = resp.find('-RELEASE', l)
  w.write('export _nginxver=%s\n' % resp[l:r])
  req = request.Request('https://github.com/openssl/openssl/releases')
  resp = request.urlopen(req).read().decode()
  l = resp.find('OpenSSL_') + 8
  r = resp.find('"', l)
  w.write('export _opensslver=%s\n' % resp[l:r])
  req = request.Request('https://zlib.net')
  resp = request.urlopen(req).read().decode()
  l = resp.find('Current release')
  l = resp.find('zlib ', l) + 5
  r = resp.find('<', l)
  w.write('export _zlibver=%s\n' % resp[l:r])
