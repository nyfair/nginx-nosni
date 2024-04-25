import json

with open('old.json') as f:
  x = json.load(f)
  x = dict(map(lambda p: (p, x['data'][p]['version']), x['data'].keys()))
with open('init.sh', 'a', newline='') as w:
  w.write('export _nginxver=%s\n' % x['nginx'])
  w.write('export _opensslver=%s\n' % x['openssl'])
  w.write('export _zlibver=%s\n' % x['zlib'])

try:
  import in_place
  with in_place.InPlace('PKGBUILD', newline='') as f:
    for line in f:
      if line.startswith('pkgver'):
        line = 'pkgver=%s\n' % x['nginx']
      f.write(line)
except:
  pass
