git config --global user.email "test@test.com"
git config --global user.name "test"
curl -OL https://github.com/msys2/MSYS2-packages/archive/refs/heads/master.zip
bsdtar xvf master.zip
cd MSYS2-packages-master/msys2-runtime
sed -i '/autogen/ased -i "/end && \\\*it/,+33d" ${srcdir}/msys2-runtime/winsup/cygwin/msys2_path_conv.cc' PKGBUILD
sed -i '/autogen/ased -i "s/NAME_MAX 255/NAME_MAX 1024/" ${srcdir}/msys2-runtime/winsup/cygwin/include/cygwin/limits.h' PKGBUILD
MSYSTEM=msys2 makepkg --skipchecksums -s --noconfirm
