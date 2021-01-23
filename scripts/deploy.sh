cd /home/deploy-user/Translations-Tool
cat TOKEN.txt | docker login https://docker.pkg.github.com -u arturkasperek --password-stdin
docker stack deploy -c stack.yml --with-registry-auth translation-tool-prod
