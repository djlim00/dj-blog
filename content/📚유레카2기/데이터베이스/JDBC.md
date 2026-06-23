#### MySQL 인텔리제이 연동방법
https://wisdom-and-record.tistory.com/61




![[Pasted image 20250306091219.png]]
- <mark style="background: #FFF3A3A6;">인터페이스는 구현을 강제하는 표준이다</mark>
- <mark style="background: #FFF3A3A6;">따라서 애플리케이션과 DB 양쪽 전부 JDBC를 이용해서 접속할거면, 해당 인터페이스를 구현한 표준에 따라서 만들어라.</mark>
#### <span style="background:rgba(3, 135, 102, 0.2)">JDBC 인터페이스 구조</span>
![[Pasted image 20250306091238.png]]
![[Pasted image 20250306091300.png]]
1. **Diver Manager** : 한번에 여러개의 Driver Manger를 만드는 것이 아니라, 하나의 매니저가 여러 종류의 드라이버를 관리해준다.(각각의 드라이버가 한종류씩 등록 가능하다)
	- 반드시 Connection을 Driver Manager를 통해서 맻어야한다.
2. **Connection** : Statement, PreparedStatement, CallableStatement 구현객체를 생성, 트랜잭션 철리 및 DB연결을 끊을 때 사용.
3. Statement : DDL, DML 을 실행 할 떄
4. **PreparedStatement** : Statement와 동일하지만, <span style="background:rgba(3, 135, 102, 0.2)">?을 사용한 매개변수화된 SQL을 사용할 수 있음</span>
5. CallableStatement : DB에 저장되어 있는 프로시저와 함수를 호출하는데 사용
6. **ResultSet** 
	- SELECT : 결과의 집합이 반환
	- INSERT, UPDATE, DELETE : 성공한 건수만 온다
7. **resultset.close(), statement.close(), connection.close()**


```java 
package m1jdbc.general;  
  
import java.sql.*;  
import java.util.Scanner;  
  
public class JDBC4Insert {  
    public static void main(String[] args) throws ClassNotFoundException, SQLException {  
        // step1  
        Class.forName("com.mysql.cj.jdbc.Driver");  
  
        // step2  
        String url = "jdbc:mysql://localhost:3306/UREKA"; // 연결명령,IP,PORT,dbname  
        String user = "ureka"; // 유저 아이디  
        String password = "ureka"; // 유저 패스워드  
  
        Connection con = DriverManager.getConnection(url,user,password);  
  
        // data 입력  
        Scanner sc = new Scanner(System.in);  
        System.out.print("제목 : ");  
        String title = sc.nextLine();  
        System.out.print("저자 : ");  
        String writer = sc.nextLine();  
        System.out.print("내용 : ");  
        String contents = sc.nextLine();  
  
        // step3  
        String query = "insert into test_board(brd_title, brd_writer, brd_cntns, brd_date)"  
                + " values( ?, ? ,?, now() )";  
        PreparedStatement pstmt = con.prepareStatement(query);  
        pstmt.setString(1,title);  
        pstmt.setString(2,writer);  
        pstmt.setString(3,contents);  
  
        // step4  
  
        int successCnt = 0;  
        successCnt = pstmt.executeUpdate();  
        System.out.println(successCnt + "건이 입력되었습니다");  
  
        pstmt.close();  
        con.close();  
    }  
}
```
- URL 형식은 DB마다 다르기 때문에 알아볼 필요가 있음!
	- "jdbc:mysql://localhost:3306/UREKA";
	- <mark style="background: #FFF3A3A6;">localhost 말고 localhost를 나타내는 정확한 ip인 127.0.0.1을 입력할 수도 있음</mark>


#### ResultSet의 테이터 커서 이동
https://m.blog.naver.com/questzz/220073134475


