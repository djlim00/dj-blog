---
title: "[Baton] Kafka의 도입과 활용"
publish: true
created: 2026-08-05T16:24:52+09:00
modified: 2026-08-05T16:26:30+09:00
cover: pasted-image-20260805162427.png
---
 1. 기본적으로 모듈간 통신에서 이벤트를기반으로 함
 2. Claim Check Pattern (S3에 원본저장하고 카프카로는 원본을 가르키는 메시지를 보냄 -> 컨슈머에서는 메시지를 보고 S3에서 가져와서 작업 실행)
	- Confluent(Kafka만든 사람이 차린 회사)의 관련 문서 : https://developer.confluent.io/patterns/event-processing/claim-check/?utm_medium=sem&utm_source=google&utm_campaign=ch.sem_br.nonbrand_tp.prs_tgt.dsa_mt.dsa_rgn.apac_sbrgn.southkorea_lng.eng_dv.all_con.confluent-developer&utm_term=&creative=&device=c&placement=&gad_source=1&gad_campaignid=23278654016&gbraid=0AAAAADRv2c180r5wrJfzzlExGM28DCziy&gclid=CjwKCAjwvsvTBhBaEiwAmf-3ntoUrE_5i0wm3Pa5yWFShvLkGUx0mXxlFnOS3JzTPcebnsVqnfIkThoCLkQQAvD_BwE
	- ![[Pasted image 20260805162427.png]]


3. Kafa를 도입했을 때의 효용성은 어떻게 될까?