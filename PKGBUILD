# Maintainer: nyfair <nyfair2012@gmail.com>
pkgname=nginx
pkgver=$_nginxver
pkgrel=1
pkgdesc='Lightweight HTTP server'
arch=('x86_64')
url='https://nginx.org/'
makedepends=('zlib-devel' 'openssl-devel')
license=('custom')
source=("https://github.com/nginx/nginx/archive/release-$pkgver.tar.gz")
md5sums=('SKIP')

build() {
  cd $srcdir/nginx-release-$pkgver
  auto/configure \
    --prefix=/etc/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --sbin-path=/usr/bin/nginx.exe \
    --pid-path=/tmp/nginx.pid \
    --http-log-path=/tmp/nginx_access.log \
    --error-log-path=/tmp/nginx_error.log \
    --http-client-body-temp-path=/tmp/nginx_clientbody \
    --http-proxy-temp-path=/tmp/nginx_proxy \
    --with-cc-opt="$CFLAGS -DFD_SETSIZE=1024" ${_module}
  make
}

package() {
  cd $srcdir/nginx-release-$pkgver
  make DESTDIR=$pkgdir install
  rm -rf $pkgdir/etc/nginx/*
}
