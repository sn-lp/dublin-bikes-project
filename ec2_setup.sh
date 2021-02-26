#!/usr/bin/bash
# Run this as ec2-user on an Amazon Linux EC2 instance

sudo yum update -y

# Install git
sudo yum install git -y

# clone repo
git clone https://github.com/sn-lp/dublin-bikes-project.git

# get miniconda3 installation script
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

# make it executable and execute
chmod u+x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc

# make conda env
conda create --name comp30830
conda activate comp30830
cd dublin-bikes-project

# get pip
curl -O https://bootstrap.pypa.io/get-pip.py
/home/ec2-user/miniconda3/bin/python get-pip.py --user
pip install -r requirements.txt

# Add to the path. Doesn't seem to do this automatically for some reason
export PATH="/home/ec2-user/miniconda3/bin:$PATH"
