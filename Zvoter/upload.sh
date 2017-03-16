#!/usr/bin/env bash
scp static/css/user_weixin_binding.css root@121.41.18.246:/home/web/5666/static/css/user_weixin_binding.css
scp static/js/user_weixin_binding.js root@121.41.18.246:/home/web/5666/static/js/user_weixin_binding.js
scp templates/user_weixin_binding.html root@121.41.18.246:/home/web/5666/templates/user_weixin_binding.html
scp flask_server.py root@121.41.18.246:/home/web/5666
scp user.py root@121.41.18.246:/home/web/5666
#ssh root@121.41.18.246 './restart.sh'