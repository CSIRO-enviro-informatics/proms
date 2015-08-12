#!/bin/bash
sudo kill \`ps aux | grep proms_server | grep -v "grep" | head -3 | awk '{print \$2}'\`
