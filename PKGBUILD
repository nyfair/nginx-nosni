# Maintainer: nyfair <nyfair2012@gmail.com>
pkgname=nginx
pkgver=1.22.0
pkgrel=1
pkgdesc='Lightweight HTTP server'
arch=('x86_64')
url='https://nginx.org/'
license=('custom')
source=("https://github.com/nginx/nginx/archive/release-$pkgver.tar.gz")
md5sums=('SKIP')

build() {
  cd $srcdir/nginx-release-$pkgver
  sed -i '/ -g/d' auto/cc/gcc
  sed -i '/-Werror/d' auto/cc/gcc
  sed -i 's/NGX_PLATFORM=win32/# NGX_PLATFORM=win32/' auto/configure
  auto/configure \
    --prefix=/etc/nginx \
    --conf-path=/etc/nginx/nginx.conf \
    --sbin-path=/usr/bin/nginx.exe \
    --pid-path=/tmp/nginx.pid \
    --http-log-path=/tmp/nginx_access.log \
    --error-log-path=/tmp/nginx_error.log \
    --http-client-body-temp-path=/tmp/nginx_clientbody \
    --http-proxy-temp-path=/tmp/nginx_proxy \
    --with-cc-opt="$CFLAGS -DFD_SETSIZE=65536" ${_module}
  make
}

package() {
  cd $srcdir/nginx-release-$pkgver
  make DESTDIR=$pkgdir install
  rm -rf $pkgdir/etc/nginx/*
}
