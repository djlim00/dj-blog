
![[Pasted image 20250613083622.png]]
### **우리의 CI/CD 구조 설명**

1. **개발자가 GitHub에 Push/PR**
2. **GitHub Actions가 자동으로 실행**되어 다음을 수행:
    - 테스트 및 빌드
    - Docker Image 생성
    - Docker Hub에 업로드
3. **업로드된 Docker 이미지를 EC2에서 `docker pull` 하여 배포**
    - 이 작업은 수동으로 하거나, 필요하면 EC2 인스턴스에서 `watchtower` 등을 통해 자동화 가능
4. **배포가 완료되면 Discord Webhook 등으로 알림 전송**

![[Pasted image 20250613083729.png]]
- 단점 : 우리가 띄운 서버가 아니라서 로컬 서버 제어가 어렵다. 과금
- 장점 : 소규모 팀에 가볍고 유지보수 부담이 적음. 이미 Github를 사용하기 떄문에 사용하기 편하고 러닝커브가 작음.
- Docker 이미지 배포 후에 EC2에서 docker-compose up -d