# DogVision

```
docker build -t dog-vision .

docker run -d \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  -e TG_BOT_TOKEN="YOUR TOKEN" \
  -e TG_USER_LIST='[user_id1,user_id2,...]' \
  dog-vision
```