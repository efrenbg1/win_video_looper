sudo apt update
sudo apt install python3-pil.imagetk
cp looper.service /etc/systemd/system/
systemctl enable looper
# Important disable screen saver in raspberry pi settings