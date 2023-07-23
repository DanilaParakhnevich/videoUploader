URPMI_CMD=$(which urpmi)
APT_GET_CMD=$(which apt-get)

if [[ ! -z $URPMI_CMD ]]; then
    echo "1"
    bash install_urpmi.sh
 elif [[ ! -z $APT_GET_CMD ]]; then
    echo "2"
    bash install_get.sh
 else
    echo "error can't install package $PACKAGE"
 fi
