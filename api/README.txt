sudo cp heating-api.service /lib/systemd/system
sudo systemctl daemon-reload
sudo systemctl enable heating-api.service
