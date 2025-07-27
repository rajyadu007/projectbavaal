git clone git@github.com:rajyadu007/projectbavaal.git
cd projectbavaal/
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirement.txt
#test on ip

sudo cp gunicorn.socket /etc/systemd/system/gunicorn.socket
sudo cp gunicorn.service /etc/systemd/system/gunicorn.service