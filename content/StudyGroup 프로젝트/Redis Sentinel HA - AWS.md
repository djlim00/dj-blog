---
title: "[studygroup] Redis Sentinel HA - AWS"
publish: true
created: 2026-07-12T02:39:33+09:00
modified: 2026-07-12T05:15:36+09:00
cover: pasted-image-20260712045126.png
---
![[Pasted image 20260712045126.png]]

![[Pasted image 20260712045225.png]]


#### 중지 후 로그
``` hl:8-9,24,36,64,72,76,84
[ec2-user@ip-10-0-0-128 ~]$ redis6-cli -p 26379 psubscribe '*'
Reading messages... (press Ctrl-C to quit)
1) "psubscribe"
2) "*"
3) (integer) 1
4) "pmessage"
5) "*"
6) "+sdown"
7) "sentinel 54c33a765e3f25f90783cea7c1be6414397e0fff 10.0.0.113 26379 @ mymaster 10.0.0.113 6379"
8) "pmessage"
9) "*"
10) "+sdown"
11) "master mymaster 10.0.0.113 6379"
12) "pmessage"
13) "*"
14) "+odown"
15) "master mymaster 10.0.0.113 6379 #quorum 2/2"
16) "pmessage"
17) "*"
18) "+new-epoch"
19) "1"
20) "pmessage"
21) "*"
22) "+try-failover"
23) "master mymaster 10.0.0.113 6379"
24) "pmessage"
25) "*"
26) "+vote-for-leader"
27) "059e0c1941bf3ba60b779edcb3a55bfe675f9f26 1"
28) "pmessage"
29) "*"
30) "+elected-leader"
31) "master mymaster 10.0.0.113 6379"
32) "pmessage"
33) "*"
34) "+failover-state-select-slave"
35) "master mymaster 10.0.0.113 6379"
36) "pmessage"
37) "*"
38) "+selected-slave"
39) "slave 10.0.0.48:6379 10.0.0.48 6379 @ mymaster 10.0.0.113 6379"
40) "pmessage"
41) "*"
42) "+failover-state-send-slaveof-noone"
43) "slave 10.0.0.48:6379 10.0.0.48 6379 @ mymaster 10.0.0.113 6379"
44) "pmessage"
45) "*"
46) "+failover-state-wait-promotion"
47) "slave 10.0.0.48:6379 10.0.0.48 6379 @ mymaster 10.0.0.113 6379"
48) "pmessage"
49) "*"
50) "-role-change"
51) "slave 10.0.0.48:6379 10.0.0.48 6379 @ mymaster 10.0.0.113 6379 new reported role is master"
52) "pmessage"
53) "*"
54) "+promoted-slave"
55) "slave 10.0.0.48:6379 10.0.0.48 6379 @ mymaster 10.0.0.113 6379"
56) "pmessage"
57) "*"
58) "+failover-state-reconf-slaves"
59) "master mymaster 10.0.0.113 6379"
60) "pmessage"
61) "*"
62) "+slave-reconf-sent"
63) "slave 10.0.0.36:6379 10.0.0.36 6379 @ mymaster 10.0.0.113 6379"
64) "pmessage"
65) "*"
66) "-odown"
67) "master mymaster 10.0.0.113 6379"
68) "pmessage"
69) "*"
70) "+slave-reconf-inprog"
71) "slave 10.0.0.36:6379 10.0.0.36 6379 @ mymaster 10.0.0.113 6379"
72) "pmessage"
73) "*"
74) "+slave-reconf-done"
75) "slave 10.0.0.36:6379 10.0.0.36 6379 @ mymaster 10.0.0.113 6379"
76) "pmessage"
77) "*"
78) "+failover-end"
79) "master mymaster 10.0.0.113 6379"
80) "pmessage"
81) "*"
82) "+switch-master"
83) "mymaster 10.0.0.113 6379 10.0.0.48 6379"
84) "pmessage"
85) "*"
86) "+slave"
87) "slave 10.0.0.36:6379 10.0.0.36 6379 @ mymaster 10.0.0.48 6379"
88) "pmessage"
89) "*"
90) "+slave"
91) "slave 10.0.0.113:6379 10.0.0.113 6379 @ mymaster 10.0.0.48 6379"
92) "pmessage"
93) "*"
94) "+sdown"
95) "slave 10.0.0.113:6379 10.0.0.113 6379 @ mymaster 10.0.0.48 6379"
```


#### master가 바뀐 것을 확인
``` hl:5
[ec2-user@ip-10-0-0-195 ~]$ redis6-cli -p 26379 sentinel master mymaster | head -6
name
mymaster
ip
10.0.0.48
port
6379


[ec2-user@ip-10-0-0-195 ~]$ NEW_MASTER=10.0.0.48   # 위에서 확인한 새 마스터 IP로
[ec2-user@ip-10-0-0-195 ~]$ redis6-cli -h $NEW_MASTER -p 6379 GET failover-test
"before-failover"
[ec2-user@ip-10-0-0-195 ~]$ redis6-cli -h $NEW_MASTER -p 6379 SET after-failover "yes-still-works"
OK
[ec2-user@ip-10-0-0-195 ~]$ redis6-cli -h $NEW_MASTER -p 6379 GET after-failover
"yes-still-works"
[ec2-user@ip-10-0-0-195 ~]$ 
```



#### 다시 켰을 때의 로그
``` hl:4,12
1) "pmessage"
2) "*"
3) "-role-change"
4) "slave 10.0.0.113:6379 10.0.0.113 6379 @ mymaster 10.0.0.48 6379 new reported role is master"
5) "pmessage"
6) "*"
7) "-sdown"
8) "slave 10.0.0.113:6379 10.0.0.113 6379 @ mymaster 10.0.0.48 6379"
9) "pmessage"
10) "*"
11) "+role-change"
12) "slave 10.0.0.113:6379 10.0.0.113 6379 @ mymaster 10.0.0.48 6379 new reported role is slave"
```


#### 진짜로 10.0.0.48이 새로운 master이다.
```
[ec2-user@ip-10-0-0-195 ~]$ redis6-cli -p 26379 sentinel master mymaster | head -6
name
mymaster
ip
10.0.0.48
port
6379
```

#### 데이터 무손실(페일오버 전에 넣엏던 값이 유지 되는가?)
```
[ec2-user@ip-10-0-0-195 ~]$ redis6-cli -h 10.0.0.48 -p 6379 GET failover-test
"before-failover"
```

#### 이전 master는 replica가 되었다.
```
Last login: Sat Jul 11 19:46:17 2026 from 210.178.11.117
[ec2-user@ip-10-0-0-113 ~]$ redis6-cli info replication
# Replication
role:slave
master_host:10.0.0.48
master_port:6379
master_link_status:up
```