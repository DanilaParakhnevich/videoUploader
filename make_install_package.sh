URPMI_CMD=$(which urpmi)
APT_GET_CMD=$(which apt-get)
PACMAN_CMD=$(which pacman)

if [[ ! -z $URPMI_CMD ]]; then
    echo "1"
    bash install_urpmi.sh

    tar -czf BuxarVideoUploader.tar.gz BuxarVideoUploader/
    mv BuxarVideoUploader.tar.gz rpmbuild/SOURCES

    cd rpmbuild

    rpmbuild --define "_topdir $PWD" -bb SPECS/BuxarVideoUploader.spec

    sudo rm SOURCES/BuxarVideoUploader.tar.gz
 elif [[ ! -z $APT_GET_CMD ]]; then
    echo "2"
    bash install_get.sh

    mkdir debpack/usr/
    mkdir debpack/usr/share/
    mkdir debpack/usr/share/BuxarVideoUploader

    cd debpack

    tar czf data.tar.gz usr/share/
    tar czf  control.tar.gz control postinst postrm
    echo 2.0 > debian-binary
    ar -r ../BuxarVideoUploader.deb  debian-binary control.tar.gz data.tar.gz

    sudo rm -r usr
    sudo rm data.tar.gz
    sudo rm control.tar.gz

    cd ../
    rm Application.spec
 elif [[ ! -z $PACMAN_CMD ]]; then
    echo "3"
    bash install_pacman.sh

    mkdir debpack/usr/
    mkdir debpack/usr/share/
    mkdir debpack/usr/share/BuxarVideoUploader

    cd debpack

    tar czf data.tar.gz usr/share/
    tar czf  control.tar.gz control postinst postrm
    echo 2.0 > debian-binary
    ar -r ../BuxarVideoUploader.deb  debian-binary control.tar.gz data.tar.gz

    sudo rm -r usr
    sudo rm data.tar.gz
    sudo rm control.tar.gz

    cd ../
    rm Application.spec
 else
    echo "error can't install package $PACKAGE"
 fi
