![[Pasted image 20250728142221.png]]
![[Pasted image 20250728142226.png]]


UPDATE brands SET logo_image = 'https://uhyu-bucket.s3.ap-northeast-2.amazonaws.com/logo/%E1%84%91%E1%85%A9%E1%84%90%E1%85%A9%E1%84%87%E1%85%B3%E1%86%AF%E1%84%85%E1%85%AE.jpg' WHERE brand_name = '포토블루';  
UPDATE brands SET logo_image = 'https://uhyu-bucket.s3.ap-northeast-2.amazonaws.com/logo/%E1%84%91%E1%85%AE%E1%84%83%E1%85%B3%E1%84%8B%E1%85%A6%E1%86%B7%E1%84%91%E1%85%A1%E1%84%8B%E1%85%B5%E1%84%8B%E1%85%A5.png' WHERE brand_name = '푸드엠파이어';  
UPDATE brands SET logo_image = 'https://uhyu-bucket.s3.ap-northeast-2.amazonaws.com/logo/%E1%84%91%E1%85%B5%E1%84%8C%E1%85%A1%E1%84%92%E1%85%A5%E1%86%BA.png' WHERE brand_name = '피자헛';  
UPDATE brands SET logo_image = 'https://uhyu-bucket.s3.ap-northeast-2.amazonaws.com/logo/%E1%84%91%E1%85%B5%E1%86%AF%E1%84%85%E1%85%B5.png' WHERE brand_name = '필리';  
UPDATE brands SET logo_image = 'https://uhyu-bucket.s3.ap-northeast-2.amazonaws.com/logo/%E1%84%92%E1%85%A1%E1%86%AB%E1%84%80%E1%85%A1%E1%86%BC%E1%84%8B%E1%85%B2%E1%84%85%E1%85%A1%E1%86%B7%E1%84%89%E1%85%A5%E1%86%AB%20%E1%84%8B%E1%85%B5%E1%84%8F%E1%85%B3%E1%84%85%E1%85%AE%E1%84%8C%E1%85%B3.png' WHERE brand_name = '한강유람선 이크루즈';  
UPDATE brands SET logo_image = 'https://uhyu-bucket.s3.ap-northeast-2.amazonaws.com/logo/%E1%84%92%E1%85%A5%E1%84%80%E1%85%B3%E1%84%86%E1%85%A1%E1%86%B7.png' WHERE brand_name = '허그맘';  
UPDATE brands SET logo_image = 'https://uhyu-bucket.s3.ap-northeast-2.amazonaws.com/logo/%E1%84%92%E1%85%A7%E1%86%AB%E1%84%83%E1%85%A2%E1%84%86%E1%85%A7%E1%86%AB%E1%84%89%E1%85%A6%E1%84%8C%E1%85%A5%E1%86%B7.png' WHERE brand_name = '현대면세점';  
  
SELECT * FROM brands WHERE brand_name = '현대면세점'; -- 조합형  
SELECT * FROM brands WHERE brand_name = '현대면세점';       -- 완성형



### 위의 INSERT문이 안먹는 문제,, brand_name이 영어인 경우만 INSERT가 되었음
### 한국어는 INSERT가 안되서 찾아보니, 조합형과 완성형 중에서 완성형의 경우는 조회가 되는데, 조합형은 SELECT도 안되는 것을 알 수 있었음..

![[Pasted image 20250728142350.png]]
