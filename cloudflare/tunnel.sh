#!/bin/bash
/usr/local/bin/cloudflared tunnel --url http://localhost:80 >> ~/Homelab/logs/tunnel.log 2>&1

