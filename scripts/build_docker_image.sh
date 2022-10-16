set -u
set -e
set -o pipefail
docker build -f ./Dockerfile -t "tomateit/telegram_pa:latest" .