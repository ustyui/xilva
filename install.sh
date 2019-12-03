GREEN='\033[1;32m'
RED='\033[0;31m'
bold=$(tput bold)
cd xilva_core
INSTALL_DIR=$PWD
sudo -H chmod -R u+x $INSTALL_DIR/src
sudo -H chmod -R u+x $INSTALL_DIR/src/modules
sudo -H chmod -R u+x $INSTALL_DIR/scripts
sudo -H apt-get install python-pandas -y

echo "${GREEN}${bold}---The xilva is installed!---${NC}" 
