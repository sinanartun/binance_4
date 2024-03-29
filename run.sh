#!/bin/bash
cd /home/ec2-user || exit
sudo yum upgrade -y
sudo yum -y groupinstall "Development Tools"
sudo yum -y install openssl-devel bzip2-devel libffi-devel python3-pip
curl -o ./Python-3.9.16.tgz https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
tar xvf Python-3.9.16.tgz
cd Python-3.9.16 || exit
./configure --enable-optimizations
sudo make altinstall
sed -i 's/^PATH=.*/&:\/usr\/local\/bin/' /root/.bash_profile
sed -i 's/^PATH=.*/&:\/usr\/local\/bin/' /home/ec2-user/.bash_profile
source ~/.bash_profile
/usr/local/bin/python3.9 -m pip install --upgrade pip
cd /home/ec2-user || exit
git clone https://github.com/sinanartun/binance_4.git
sudo chown -R ec2-user:ec2-user /home/ec2-user/binance_4
sudo chmod 2775 /home/ec2-user/binance_4 && find /home/ec2-user/binance_4 -type d -exec sudo chmod 2775 {} \;
cd binance_4 || exit
python3.9 -m venv venv
pip3.9 install -r requirements.txt
sudo tee /etc/systemd/system/binance.service << EOF
[Unit]
Description=Binance Service

[Service]
User=root
ExecStart=/usr/local/bin/python3.9 /home/ec2-user/binance_4/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable binance
sudo systemctl start binance