#!/bin/bash
if [ "x$BASH_VERSION" = "x" -a "x$INSTALLER_LOOP_BASH" = "x" ]; then
    if [ -x /bin/bash ]; then
        export INSTALLER_LOOP_BASH=1
        exec /bin/bash -- $0 $*
    else
        echo "bash must be installed at /bin/bash before proceeding!"
        exit 1
    fi
fi
sudo yum upgrade -y
sudo yum -y groupinstall "Development Tools"
sudo yum -y install openssl-devel bzip2-devel libffi-devel
curl -o ./Python-3.9.16.tgz https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
tar xvf Python-3.9.16.tgz
cd Python-3.9.16 || exit
./configure --enable-optimizations
sudo make altinstall
sed -i 's/^PATH=.*/&:\/usr\/local\/bin/' ~/.bash_profile
source ~/.bash_profile
/usr/local/bin/python3.9 -m pip install --upgrade pip
cd ~ || exit
sudo yum install git -y
git clone https://github.com/sinanartun/binance_4.git
cd binance_4 || exit
python3.9 -m venv venv
pip3.9 install -r requirements.txt
sudo tee /etc/systemd/system/binance.service << EOF
[Unit]
Description=Binance Service

[Service]
User=ec2-user
ExecStart=/usr/local/bin/python3.9 /home/ec2-user/binance_4/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable binance
sudo systemctl start binance