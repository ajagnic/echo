### echo
multi-user echo server, runs on LAN (w/ port-forwarding enabled)

#### Run
*   mserver requires the passing of a host url, port number, and a password for clients to connect
```
python3 -m tcp.mserver 192.0.0.1 55555 supersecret
```

###### TODO
*   develop message packets
    *   origin, timestamp, message