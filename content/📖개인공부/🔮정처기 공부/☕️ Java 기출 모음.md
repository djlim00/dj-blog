```java
class Main {  
  static int[] arr() { 
    int a[]=new int[4];
    int b = a.length; // 4 
    for(int i =0; i<b;i++)
      a[i]=i;
    return a;
  } 
 
  public static void main(String args[]) { 
  int a[]=arr(); // 0,1,2,3
  for(int i =0; i< a.length; i++)
    System.out.print(a[i]+" ");
  } 
}
```
- 
답 : 0 1 2 3

```java
class Parent{
  void show(){System.out.println("parent");}  
}
class Child extends Parent{
  void show() {System.out.println("child");}
}
 
class Main {  
  public static void main(String args[]) { 
    Parent pa=(가) Child();
    pa.show();
  } 
}
```
답 : new 

```java 
	class A{
	private int a;
    public A(int a){
    	this.a = a;
    }
    public void display(){
    	System.out.println("a=" + a);
    }
}
 
class B extends A {
	public B(int a){
    	super(a);
        super.display();
    }
}
 
 
public class Main {
	public static void main(String[] args){
    	B obj = new B(10);
    }
}
```
답 : a=10

```java
	public class Main{
	public static void main(String[] args){
    	int i=0, c=0;
        while (i<10){
         i++;
         c*=i;
        }
        System.out.println(c);
   }
  }
```
답 : 0

```java
abstract class Vehicle{
	String name;
    abstract public String getName(String val);
    public String getName(){
    	return "Vehicle name:" + name;
    }
}
 
class Car extends Vehicle{
  private String name;
	public Car(String val){
    	name=super.name=val;
   }
public String getName(String val){
	return "Car name : " + val;
   }
public String getName(byte val[]){
	return "Car name : " + val;
   }
}
 
public class Main {
	public static void main(String[] args){
    Vehicle obj = new Car("Spark");
    System.out.print(obj.getName());
    }
}
```
답 : Vehicle name: Spark

#### 🔥 whlie문 종료시점은 i < 10, i++로 인해 10으로 바뀐거까지 더해줘야함.
```java
public class Main {
	public static void main(String[] args){
    int i=0, sum=0;
    while (i<10){
    	i++;
        if(i%2 ==1)
        	continue;
        sum += i;
     }
     System.out.println(sum);
   }
}
```
- 0+2+4+6+8+10 = 30
답 : 30

#### 🔥 다음은 변수 n에 저장된 10진수를 2진수로 변환하여 출력하는 java프로그램이다. 프로그램을 분석하여 ( 1번 )( 2번 )빈칸에 알맞은 답을 쓰시오
```java
class Main {
	public static void main (String[] args) {
    	int[]a = new int[8];
        int i=0; int n=10;
        while (  1번 ) {
        	a[i++] = ( 2번 );
            n /= 2;
        }
        for(i=7; i>=0; i--){
         System.out.print(a[i]);
        }
     }
  }
```
- 2진수는 결국 $2^0, 2^1, 2^2 \dots$ 자릿값의 합입니다. 어떤 숫자를 2로 나누었을 때 발생하는 **나머지(Remainder)**는 그 자릿수의 값이 **0인지 1인지**를 결정하는 핵심 데이터가 됩니다.
- 출력은 `i = 7`부터 거꾸로 할까?
	우리가 나머지를 구할 때는 **가장 낮은 자리(2^0)**부터 구해지지만, 읽을 때는 **가장 높은 자리**부터 읽어야 합니다.
답 : (1) n>0 (2)  n%2


```java
public class Main {
	public static void main(String[] args) {
    	int ary[][] = new int[가][나];
   
        for(int i = 0; i <3; i++){
        for(int j=0; j < 5; j++){
        ary[i][j] = j*3+(i+1);
        	System.out.print(ary[i][j]+"");
         }
         System.out.println();
       }
     }
   }
```
답 : 3, 5


```java
class Parent{
	public int compute(int num){
    	if(num <=1) return num;
        return compute(num-1) + compute(num-2);
    }
 }
 
 class Child extends parent {
 	public int compute(int num){
    	if(num<=1) return num;
        	return compute(num-1) + compute(num-3);
        }
   }
   
  class Main{
  	public static void main (String[] args){
    Parent obj = new Child();
    System.out.print(obj.compute(4));
   }
 }
```

답 : 1 

```java
public class Main{
	public static void main(String[] args){
    	int arr[][] = new int[][]{{45,50,75},{89}};
        System.out.println(arr[0].length);
        System.out.println(arr[1].length);
        System.out.println(arr[0][0]);
        System.out.println(arr[0][1]);
        System.out.println(arr[1][0]);
  }
}
```
- **가변배열이라서 arr[1].length는 3임!!**
- 
답 : 
	3
	1
	45
	50
	89

```java
public class Main {
   public static void main(String[] args){
      System.out.print(Main.check(1));
   }
   
  (가) String check (int num) {
      return (num >= 0) ? "positive" : "negative";
   }
}
```

답 : static


```java
public class ovr1 {
	public static void main(String[] args){
    	ovr1 a1 = new ovr1();
        ovr2 a2 = new ovr2();
        System.out.println(a1.sun(3,2) + a2.sun(3,2)); 
    }
    
    int sun(int x, int y){
    	return x + y;
    }
}
class ovr2 extends ovr1 {
 
	int sun(int x, int y){
    	return x - y + super.sun(x,y);
    }
 
}
```
답 : 11

```java
class Connection {
	  private static Connection _inst = null;
	  private int count = 0;
      
      public static Connection get() {
      if(_inst == null) {
      _inst = new Connection();
      return _inst; 
      }
    return _inst;
    }
  public void count() { count ++; }
  public int getCount() { return count; }
}
 
public class Main {
  public static void main(String[] args) {
    Connection conn1 = Connection.get();
    conn1.count();
    Connection conn2 = Connection.get();
    conn2.count();
    Connection conn3 = Connection.get();
    conn3.count();
    
    System.out.print(conn1.getCount());
  }
}
```
- _inst가 static 이기 때문에 conn1에서 한번 생성이 되면 conn2, conn3가 공유를 한다. 
- 따라서 count()가 세번 호출되었기 때문에 3
답 : 3


#### 🔥 ^(XOR) 연산자 까먹지 말자
```java
public class Main {
    public static void main(String[] args) {
        int a = 3, b = 4, c = 3, d = 5;

        if ((a == 2 | a == c) & !(c > d) & (1 == b ^ c != d)) {
            a = b + c;
            if (7 == b ^ c != a) {
                System.out.println(a);
            } else {
                System.out.println(b);
            }
        } else {
            a = c + d;
            if (7 == c ^ d != a) {
                System.out.println(a);
            } else {
                System.out.println(d);
            }
        }
    }
}
```
- ^ 연산자 -> 둘이 달라야지 true
답 : 7

```java
class A {
  int a;
  int b;
}
  
  public class Main {
  
  static void func1(A m){
   m.a *= 10;
  }
  
  static void func2(A m){
    m.a += m.b;
  }
  
  public static void main(String args[]){
  
  A m = new A();
  
  m.a = 100; //
  func1(m); // a = 1000
  m.b = m.a; // b = 1000
  func2(m); // 
  
  System.out.printf("%d", m.a);
  
  }
}
```
- 그냥 뭐 하라는대로 하면 됨.
답 : 2000

#### 🔥 Thread 객체 -> new를 통해서 만들려면 Runnable
```java
class Car implements Runnable{
  int a;
  
  public void run(){
    try{
      while(++a<100){
        System.out.println("miles traveled :" +a);
        Thread.sleep(100);
      }
    }
     catch(Exception E){}
  }
}
  
public class Main{
  public static void main(String args[]){
    Thread t1 = new Thread(new (가)());
    t1.start();
  }
}
```
- **자바에서 `Thread` 객체를 만들 때, 생성자 안에 `new`를 통해 무언가를 집어넣는다면 그 객체는 반드시 `Runnable` 인터페이스를 구현(implements)**한 클래스여야 합니다.**
답 : Car

```java
class Main {  
  public static void main(String args[]) { 
    int i=3, k=1;
  switch(i){
    case 1:k+=1;
    case 2:k++;
    case 3:k=0;
    case 4:k+=3;
    case 5:k-=10;
    default : k--;
  }
System.out.print(k);
  } 
}
```
답 -8

```java
class Conv {
  int a; 
 
  public Conv(int a) {
    this.a = a;
  }
 
  int func() {
    int b = 1;
    for (int i = 1; i < a; i++) {
      b = a * i + b;
    }
    return a + b;
  }
}
 
 public class Main {
  public static void main(String args[]) {
    Conv obj = new Conv(3);
    obj.a = 5; 
    int b = obj.func();
    System.out.print(obj.a + b);
  }
}
```
- **for 문 안에서 b값이 계속 갱신되고 있다는 사실을 잊으면 안된다!**
답 : 61

```java
	public class Test{
 public static void main(String[] args){
  int []result = int[5];
  int []arr = [77,32,10,99,50];
  for(int i = 0; i < 5; i++) {
    result[i] = 1;
    for(int j = 0; j < 5; j++) {
      if(arr[i] <arr[j]) 
        result[i]++;
    }
  }
 
  for(int k = 0; k < 5; k++) {
    printf(result[k]);
   }
 }
}
```
답 : 24513

```java
public class Main {
  static int[] MakeArray(){
	  int[] tempArr = new int[4];
	  
	  for(int i=0; i<tempArr.Length;i++){
	    tempArr[i] = i;
	  }
	  
	  return tempArr;
  }
  
  public static void main(String[] args){
	  int[] intArr;
	  intArr = MakeArray();
	  
	  for(int i=0; i < intArr.Length; i++)
		  System.out.print(intArr[i]);
	  }
}
```
답 : 0123

```java
public class Exam {
  public static void main(String[] args){
  
  int a = 0;
  for(int i=1; i<999; i++){
    if(i%3==0 && i%2!=0)
      a = i;
    }
    System.out.print(a);
  }
}
```
- 3의 배수이면서 2의 배수가 아닌 999미만의 수 -> 6의 배수 구하고 -3
답 : 993

```java
class Static{
  public int a=20;
  static int b=0;
}
 
 
public class Main {
  public static void main(String[] args) {
    int a=10;
    Static.b=a;
    Static st=new Static();
 
    System.out.println(Static.b++);
     System.out.println(st.b);
     System.out.println(a);
     System.out.println(st.a);
  }
}
```
- **Static.b++ 이니까, 출력을 하고나서 증가한다!!!**
답 : 
	10
	11
	10
	20

```java
abstract class Vehicle{
	String name;
    abstract public String getName(String val);
    public String getName(){
    	return "Vehicle name:" + name;
    }
}
 
class Car extends Vehicle{
  private String name;
	public Car(String val){
    	name=super.name=val;
   }
public String getName(String val){
	return "Car name : " + val;
   }
public String getName(byte val[]){
	return "Car name : " + val;
   }
}
 
public class Main {
	public static void main(String[] args){
    Vehicle obj = new Car("Spark");
    System.out.print(obj.getName());
    }
}
```
답 : Vehicle name: Spark

```java
class Parent {
	int x = 100;
	 
	Parent() {
		this(500);
	}
	Parent(int x) {
		this.x = x;
	}
	int getX() {
		return x;
	}
}

class Child extends Parent {
	int x = 1000;
 
	Child() {
		this(5000);
	}
	 
	Child(int x) {
	// super();
		this.x = x;
	}
}
 
public class Main {
	public static void main(String[] args) {
		Child obj = new Child();
		System.out.println(obj.getX());
	}
}
```
- 생성자 맨 윗줄에 this()가 있으면, 해당 객체의 다른 생성자를 호출하라는 뜻.
- this()생성자가 없으면 -> super로 가는거임
답 : 500

```java
public class Main {
	public static void main(String[] args) {
		  String str1 = "Programming"; 
	      String str2 = "Programming";
	      String str3 = new String("Programming");
	      
	      System.out.println(str1==str2);
	      System.out.println(str1==str3);
	      System.out.println(str1.equals(str3));
	      System.out.print(str2.equals(str3));
	}
}
```
- 문자열 상수풀 -> 기존이랑 같은 문자열이 있으면 같은 주소 할당
- new String으로 하면 달라짐.
- == 은 주솟값을 비교함.
답 :
	**true**
	false
	true
	true


```java
public class Main {
	public static void main(String[] args) {
		A b = new B();
		b.paint();
		b.draw();
	}
}
class A {
	public void paint() {
		System.out.print("A");
		draw();
	}
	public void draw() {
		System.out.print("B");
		draw();
	}
}
class B extends A {
	public void paint() {
		super.draw();
		System.out.print("C");
		this.draw();
	}
	public void draw() {
		System.out.print("D");
	}
}
```
- super.draw()에서의 draw()는 선언된 타입의 draw()를 따라야한다!
답 : BDCDD

#### 🔥 static 사용시 주의!
```java
class Person {
	private String name;
	public Person(String val) {
		name = val;
	}
	public static String get() {
		return name;
	}
	public void print() {
		System.out.println(name);
	}
 }
 public class Main {
	public static void main(String[] args) {
		Person obj = new Person("Kim");
		obj.print();
	}
 }
```
- static String get()에서는 아직 생성되지도 않은 name을 가져오라고 하는 함수가 이미 떠있기 때문에 오류가 발생한다.
답 : 7


```java
class Parent {
    int x, y;
 
    Parent(int x, int y) { (가)
        this.x=x;
        this y=y;
    }
 
    int getT() { (나)
        return x*y;
    }
}

​class Child extend Parent {
    int x;
 
    Child (int x) { (다)
        super(x+1, x);
        this.x=x;
    }
 
    int getT(int n){ (라)
        return super.getT()+n;
    }
}
 
class Main {
    public static void main(String[] args) { (마)
        Parent parent = new Child(3); (바)
        System.out.println(parent.getT()); (사)
    }
}
```

**답 : 바, 다, 가, 사, 나**

```java
class classOne {
    int a, b;
 
    public classOne(int a, int b) {
        this.a = a;
        this.b = b;
    }
 
    public void print() {
        System.out.println(a + b);
    }
 
}
class classTwo extends classOne {
    int po = 3;
    
    public classTwo(int i) {
        super(i, i+1);
    }
 
    public void print() {
        System.out.println(po*po);
    }
}
 
public class main {  
    public static void main(String[] args) {
        classOne one = new classTwo(10);
        one.print();
    }
}
```
답  : 9

```java
	class Main {
    public static void main(String[] args) {
        int[] a = new int[]{1, 2, 3, 4};
        int[] b = new int[]{1, 2, 3, 4};
        int[] c = new int[]{1, 2, 3};
        
        check(a, b);
        check(a, c); 
        check(b, c); 
    }
 
    public static void check(int[] a, int[] b) {
        if (a==b) {
            System.out.print("O");
        }else{
            System.out.print("N");
        }
        
    }
}
```
답 : NNN

```java
class Main {    
    public static void main(String[] args) {
        int a[] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
        ODDNumber OE = new ODDNumber();
        System.out.print(OE.sum(a, true) + ", " + OE.sum(a, false));
    }
}
 
interface Number {
    int sum(int[] a, boolean odd);
}
 
class ODDNumber implements Number {
    public int sum(int[] a, boolean odd) {
        int result = 0;
        for(int i=0; i < a.length; i++){
            if((odd && a[i] % 2 != 0) || (!odd && a[i] % 2 == 0))
                result += a[i];
        }        
        return result;
    }    
}
```
답 : 25, 20

#### 🔥 헷갈리면 진짜 무조건 그리면서 하기
```java
class Main {
    public static void main(String[] args) {
        String str = "abacabcd";
        boolean[] seen = new boolean[256];
        System.out.print(calculFn(str, str.length()-1, seen));
    }
 
    public static String calculFn(String str, int index, boolean[] seen) {
        if(index < 0) return "";
        char c = str.charAt(index);
        String result = calculFn(str, index-1, seen);
        if(!seen[c]) {
            seen[c] = true;
            return c + result;
        }
        return result;
    }
}
```
- **중복되는 알파벳이 나오기 전까지 역순으로 print**
답 : dcba

```java
class Main {
    public static void main(String[] args) {
        String str = "ITISTESTSTRING";
        String[] result = str.split("T");
        System.out.print(result[3]);
    }
}
```
- **split()하게 되면 해당 문자는 없어지고, 사이에 낀 애들만 남는다**
- 0부터 시작하는거 까먹지 않기
답 : S


```java
public class Main{
  static String[] s = new String[3];
 
  static void func(String[]s, int size){
    for(int i=1; i<size; i++){
      if(s[i-1].equals(s[i])){
        System.out.print("O");
      }else{
        System.out.print("N");
      }
    }
    
    for (String m : s){
	    System.out.print(m);
    }
}
  
  public static void main(String[] args){
    s[0] = "A";
    s[1] = "A";
    s[2] = new String("A");
 
    func(s, 3);
  }
}
```
답 : 00AAA

```java
public class Main{
  public static void main(String[] args){
    Base a =  new Derivate();
    Derivate b = new Derivate();
    
    System.out.print(a.getX() + a.x + b.getX() + b.x);
  }
}
 
 
class Base{
  int x = 3;
 
  int getX(){
     return x * 2; 
  }
}
 
class Derivate extends Base{
  int x = 7;
  
  int getX(){
     return x * 3;
  }
}
```
- 7 * 3 + 3 + 7 * 3  + 7 = 52
답 : 52

#### 🔥 Exeption 개념
```java
public class ExceptionHandling {
  public static void main(String[] args) {
      int sum = 0;
      try {
          func();
      } catch (NullPointerException e) {
          sum = sum + 1;
      } catch (Exception e) {
          sum = sum + 10;
      } finally {
          sum = sum + 100;
      }
      System.out.print(sum);
  }
 
  static void func() throws Exception {
      throw new NullPointerException(); 
  }
}
```
- func()에서 NullPointerException을 발생시킴 -> sum+1 -> finally에서 +100
- 만약에 다른 예외였으면 Exception e로 빠져야함.
답 : 101

```java
class Main {
 
  public static class Collection<T>{
    T value;
 
    public Collection(T t){
        value = t;
    }
 
    public void print(){
       new Printer().print(value);
    }
 
   class Printer{
      void print(Integer a){
        System.out.print("A" + a);
      }
      void print(Object a){
        System.out.print("B" + a);
      } 
      void print(Number a){
        System.out.print("C" + a);
      }
   }
 }
 
  public static void main(String[] args) {
      new Collection<>(0).print();
  }
  
}
```
- "제네릭 `T`는 컴파일 후 `Object`가 되고, 오버로딩은 컴파일 시점의 타입(`Object`)을 보고 메서드를 고르기 때문에 `print(Object)`가 실행되어 `B0`이 나온다!"
답 : B0