### echo
multi-user echo server, runs on LAN (w/ port-forwarding enabled)

#### Run
*   Optionally provide host and port values
```
python3 -m tcp.mserver 192.0.0.1 55555
```

###### TODO
*   develop sha key generator
*   incorporate AES
*   develop message packets
    *   origin, timestamp, message