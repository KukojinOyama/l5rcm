#!/bin/bash
cwd=${PWD}
printf 'clear'
rm $1.tar.gz
rm $1.deb

printf 'make source tarball'
tar -vzcf $1.tar.gz --exclude-vcs -X exclude_from_source --exclude-backups --exclude-caches ../

printf 'make workingdir'
rm -rf ./tmp
mkdir tmp
mkdir tmp/opt
mkdir tmp/opt/l5rcm
mkdir tmp/usr
mkdir tmp/usr/bin
mkdir tmp/usr/menu
mkdir tmp/usr/share
mkdir tmp/usr/share/applications
mkdir tmp/usr/share/pixmaps
tar -vxzf $1.tar.gz -C ./tmp/opt/l5rcm

cp ./l5rcm.png ./tmp/usr/share/pixmaps
cp ./l5rcm.desktop ./tmp/usr/share/applications
cp ./l5rcm.menu ./tmp/usr/menu/l5rcm
cp ./l5rcm ./tmp/usr/bin


cp -r ../debian ./tmp
ln -s ./debian ./tmp/DEBIAN
rm -rf ./tmp/DEBIAN/.svn

dpkg-deb -b ./tmp $1.deb
cd $cwd