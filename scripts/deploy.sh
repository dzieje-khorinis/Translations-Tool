cd /home/deploy-user/Translations-Tool
cat TOKEN.txt | docker login ghcr.io -u arturkasperek --password-stdin
docker stack deploy -c stack.yml --with-registry-auth translation-tool-prod
