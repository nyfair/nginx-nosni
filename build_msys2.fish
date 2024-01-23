git config --global user.email "test@test.com"
git config --global user.name "test"
curl -OL https://github.com/msys2/MSYS2-packages/archive/refs/heads/master.zip
bsdtar xvf master.zip
cd MSYS2-packages-master/msys2-runtime
sed -i '/apply_git_am_with_msg /ised -i \'s/NAME_MAX 255/NAME_MAX 1024/\' winsup/cygwin/include/cygwin/limits.h' PKGBUILD
sed -i '/fixup-Add-functionality-for-converting-UNIX/d' PKGBUILD
cat PKGBUILD
MSYSTEM=msys2 makepkg --skipchecksums -s --noconfirm
