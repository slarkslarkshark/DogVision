# DogVision

```
docker build -t dog-vision .

docker run -d -v $(pwd)/logs:/app/logs --restart unless-stopped dog-vision
```