
- 갑자기 훅 어려운 걸로 온 느낌이 없지 않아 있지만,, 결론적으로 우리가 서버를 배포할 때 있어서 할만한 것들(로드밸런싱, 오토스케일링, 클라우드워치)을 붙여서 배포를 하는 방법이다.
- aws 서비스를 통합적으로 사용하려면 IAM 설정이 필요하다
	- 각각의 서비스에서 다른 서비스를 조작할 수 있는 권한을 부여해야한다.
	- ex) CodeDeploy에서 EC2와 ASG(오토스케일링 그룹)에 대한 권한이 있어야지 CD(지속적인 배포) 중에 EC2와 ASG에서 기능을 실행할 수 있다.

# 1. CodeDeploy에 대한 서비스 역할 설정

- 먼저 CodeDeploy의 권한을 설정을 해주자. 아래 파일을 보자.

1. IAM → 역할 → 역할 생성
2. 사용사례의 드롭다운에서 CodeDeploy 선택 → 다음
3. 권한 추가 페이지는 확인 후 넘어감
4. 이름 지정, 검토 및 생성 페이지에서 역할 이름 입력 → 역할 생성
5. 역할 → 역할 목록에서 앞서 생성한 역할 검색 및 선택
6. 신뢰 관계 탭 선택
7. 신뢰 정책 편집 선택, 이하 내용 입력

```
{
	"Version": "2012-10-17",
	"Statement": [
	{
		"Sid": "",
		"Effect": "Allow",
		"Principal": {
		"Service": [
		"codedeploy.amazonaws.com"
		]
	},
	"Action": "sts:AssumeRole"
		}
	]
}
```

8. IAM 콘솔에서 해당 역할의 ARN 확인
9. 이하 내용의 정책 부여

``` json, title:"CodeDeploy 정책 설정"
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Effect": "Allow",
			"Action": [
				"ec2:RunInstances",
				"ec2:CreateTags",
				"iam:PassRole"
			],
			"Resource": "*"
		},
		{
			"Effect": "Allow",
			"Action": [
				"autoscaling:CompleteLifecycleAction",
				"autoscaling:DeleteLifecycleHook",
				"autoscaling:DescribeAutoScalingGroups",
				"autoscaling:DescribeLifecycleHooks",
				"autoscaling:PutLifecycleHook",
				"autoscaling:RecordLifecycleActionHeartbeat"
			],
			"Resource": "*"
		},
		{
			"Effect": "Allow",
			"Action": [
				"ec2:Describe*",
				"codedeploy:*"
			],
			"Resource": "*"
		}
	]
}
```

