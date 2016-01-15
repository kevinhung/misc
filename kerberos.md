# Kerberos

Summarize [wiki](https://zh.wikipedia.org/wiki/Kerberos), the principles are:

1. Each tickets corresponds to a service and will be encrypted by its key.
1. Ticket contains a session key for communications between client and corresponding service.
  1. Maybe we can take encrypted ```K_s1``` (see [Notation](#notation)) as a special ticket where user itself is the service.
1. That's why KDC must have everyone's key to encrypt all tickets.
1. KDC contains 2 services: "authentication server" and "ticket-granting server".
  1. These can be running on different hosts.
1. Client just bypass all tickets.
1. NO password is transmitted among entities, in case of insecure network.

## Notation

* UID: user ID
* SID: service ID
* K\_u: user key, hashed from plaintext password
* K\_as: key of authentication service
* K\_ss: key of service server
* K\_s1, K\_s2: session keys
* TGT: ticket-grant ticket, contains K\_s1
* SGT: service-grant ticket, contains K\_s2
* enc(M, K): encrypt message M by key K, via symmetric key cryptography

## Collaboration

```
Client                   KDC      Service Server
  |                       |              |
  |         UID           |              |
  |---------------------->|              |
  |    enc(K_s1, K_u)     |              |
  |<----------------------|              |   authenticate
  | TGT' = enc(TGT, K_as) |              |
  |<----------------------|              |
  |                       |              |
  |                       |              |
  |      TGT' & SID       |              |
  |---------------------->|              |
  |    enc(req, K_s1)     |              |
  |---------------------->|              |
  |    enc(K_s2, K_s1)    |              |   authorize
  |<----------------------|              |
  | SGT' = enc(SGT, K_ss) |              |
  |<----------------------|              |
  |                       |              |
  |                                      |
  |               SGT'                   |
  |------------------------------------->|
  |        enc(token, K_s2)              |
  |------------------------------------->|   access
  |         accept or deny               |
  |<-------------------------------------|
  |                                      |
```

