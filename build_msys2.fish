git config --global user.email "test@test.com"
git config --global user.name "test"
curl -OL https://github.com/msys2/MSYS2-packages/archive/refs/heads/master.zip
bsdtar xvf master.zip
cd MSYS2-packages-master/msys2-runtime
mv ../../PKGBUILD-msys2 ./PKGBUILD
MSYSTEM=msys2 makepkg --skipchecksums -s --noconfirm
