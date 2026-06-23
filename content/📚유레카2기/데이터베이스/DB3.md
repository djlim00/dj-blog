### 문자열 타입 - char, varchar
___
- char(10) - 두글자를 입력해도 저장공간은 10글자 만큼의 저장공간이 생김 -> 낭비!
- varchar(10) - 10라고 정의로 해도 두글자를 입력하면 2글자 만큼의 저장공간만 생김 -> 낭비없음!
	- oracle에서는 varchar2

그럼 char를 왜 씀?
: 그렇지만 어떤 필드들은 ~_YN 이런식으로 저장되는 경우는 Y(Yes), N(No)이거 한자리를 쓰기 위해서 char(1)로 선언하는 경우도 있음!
: 사실 그냥 0,1로 int로 저장하는게 더 좋긴 함.


### Primary key
___
- <mark style="background: #FFF3A3A6;">not null + unique => 반드시 값이 존재한다 + 각 row는 유일한 값을 가진다</mark>

