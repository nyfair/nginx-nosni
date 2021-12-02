curl -OL https://github.com/nginx/nginx/archive/release-$_nginxver.tar.gz
curl -OL https://github.com/openssl/openssl/archive/openssl-$_opensslver.tar.gz
curl -OL https://zlib.net/zlib-$_zlibver.tar.xz
for i in *tar*; do bsdtar xf $i; done
sed -i 's/MT/MD/g' openssl-openssl-$_opensslver/Configurations/10-main.conf
cd nginx-release-$_nginxver
sed -i 's/MT/MD/g' auto/cc/msvc
sed -i '/-WX/d' auto/cc/msvc
auto/configure \
  --with-cc=cl \
  --prefix= \
  --conf-path=nginx.conf \
  --pid-path=nginx.pid \
  --http-log-path=access.log \
  --error-log-path=error.log \
  --sbin-path=nginx.exe \
  --http-client-body-temp-path=client_body_temp \
  --http-proxy-temp-path=proxy_temp \
  --with-zlib=../zlib-$_zlibver \
  --with-openssl=../openssl-openssl-$_opensslver \
  --with-cc-opt=-DFD_SETSIZE=65536 ${_module}
