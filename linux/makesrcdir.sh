#!/bin/bash
cwd=${PWD}

# remove old files
rm $1.tar.gz
rm $1.deb

# make source tarball
tar -vzcf $1.tar.gz --exclude-vcs -X exclude_from_source --exclude-backups --exclude-caches ../

# remove old directory
# should ask for root password
rm -rf ./tmp

# make working dir
mkdir tmp
mkdir tmp/opt
mkdir tmp/opt/l5rcm
mkdir tmp/opt/l5rcm/mime
mkdir tmp/usr
mkdir tmp/usr/bin
#mkdir tmp/usr/menu
mkdir tmp/usr/share
mkdir tmp/usr/share/doc
mkdir tmp/usr/share/doc/l5rcm
mkdir tmp/usr/share/applications
mkdir tmp/usr/share/pixmaps
tar -vxzf $1.tar.gz -C ./tmp/opt/l5rcm

cp ./l5rcm.png ./tmp/usr/share/pixmaps
cp ./l5rcm.desktop ./tmp/usr/share/applications
cp ./l5rcm ./tmp/usr/bin

cp ./*.xml ./tmp/opt/l5rcm/mime

# copyright file
cp ../debian/copyright ./tmp/usr/share/doc/l5rcm/

cp -r ./DEBIAN ./tmp
rm -rf ./tmp/DEBIAN/.svn

# change GID
chown -R root:root ./tmp/usr
chown -R root:root ./tmp/opt

# fix permission
find ./tmp -type d | xargs chmod 755
find ./tmp/opt -type f | xargs chmod 644
find ./tmp/usr -type f | xargs chmod 644

chmod +x ./tmp/usr/bin/l5rcm

dpkg-deb -b ./tmp $1.deb

# give my debs!
chown daniele:daniele $1* 
cd $cwd
