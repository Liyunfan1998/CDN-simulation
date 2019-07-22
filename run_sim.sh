# install pytohn3.7
sudo apt-get install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install build-essential libpq-dev libssl-dev openssl libffi-dev zlib1g-dev
sudo apt-get install python3-pip python3.7-dev
sudo apt-get install python3.7

# install requirements
python3.7 -m pip install --upgrade pip pandas numpy scipy matplotlib

# run simulation
nohup python3.7 simulate_attack.py > out.txt &