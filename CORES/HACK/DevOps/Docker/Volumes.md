## Volumes and it types
1. Anonymous Volumes
	1. `$docker run -v /data01`
	2. indocker:  /data01
	3. inhost: /var/lib/docker/volumes/random-hash/_data
	4. ex: `$docker run -it --name mycontainer -v /data01 nginx /bin/bash`
2. Named Volumes
	1. `$docker run -v myvolume1:/data01`
	2. indocker: /data01
	3. inhost: /var/lib/docker/volumes/myvolume1/__data
	4. ex: `$docker run -it --name mycontainer -v myvolume:/data01 nginx /bin/bash`
	5. equv
		1. `docker volume create myvolume`
		2. `docker run -it --name mycontainer -v myvolume:/data01 nginx /bin/bash`
	6. volume with size
		1. `$docker volume create --opt o=size=1g --opt device=/data3 --opt o=size=1gb type=btrfs myvolume`
3. Host Volumes or Bind Volumes
	1. `$docker run -v /opt/data01:/data01`
	2. indocker: /data01
	3. inhost: /opt/data01
