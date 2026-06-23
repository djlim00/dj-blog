## 20년
```c
#include <stdio.h>
 
main() {
  int c=1;
  switch(3){
    case 1:c+=3;
    case 2:c++;
    case 3:c=0;
    case 4:c+=3;
    case 5:c-=10;
    default : c--;
    
  }
	printf("%d",c);
  }
```
- **switch문에 break;가 없기 때문에, 그냥 쭉 다 연산을 해야한다.**
답 : -8

```c
#include <stdio.h>
void align(int a[]){
  int temp;
  for(int i=0;i<4;i++)
    for(int j=0;j<4-i;j++)
      if(a[j]>a[j+1]){
        temp=a[j];
        a[j]=a[j+1];
        a[j+1]=temp;
      }
}
 main() {
   int a[]={85, 75, 50, 100, 95};
   align(a);
   for(int i=0;i<5;i++)
     printf("%d",a[i]);
}
```
- 
답 :  50758595100

```c
	#include <stdio.h>
int r1(){
  return 4;
}
int r10(){
  return(30+r1());
}
int r100(){
  return(200+r10());
}
int main(){
  printf("%d\n",r100());
}
```
답 : 200+30+4 = 234

```c
#include <stdio.h> 
 main() {
   char *p="KOREA";
   printf("%s\n",p);
   printf("%s\n",p+3);
   printf("%c\n",*p);
   printf("%c\n",*(p+3));
   printf("%c\n",*p+2);
   }
```
- p는 가르키고 있는 KOREA 전체
- p+3은 가르키고 있는 곳에서+3부터
- * p는 첫번째로 가르키는 곳
- 세번째로 가르키는 곳
- K보다 두개 위의 알파벳
답 :
	KOREA
	EA
	K
	E
	M

```c
	#include <stdio.h>
void main(){
struct insa {
	char name[10];
    int age;
 }a[] = {"Kim",28,"Lee",38,"Park",42,"Choi",31};
    struct insa *p;
    p = a;
    p++;
    printf("%s\n", p-> name);
    printf("%d\n", p-> age);
  }
```
- a[]는 insa 구조체를 저장하고 있다. p는 a의 시작점을 가르키고 있고, p++하기 때문에 두번째 구조체를 자르키게 된다. 
답 : 
	LEE
	38

```c
#include <stdio.h>
int main(){
   int res;
   res = mp(2,10);
   printf("%d",res);
   return 0;
}
 
int mp(int base, int exp) {
   int res = 1;
   for(int i=0; i < exp; i++){
      res *= base;
   }
   
   return res;
}
```
답 : 1024 

```c
#include <stdio.h>
int main(){
 
int ary[3];
int s = 0;
*(ary+0)=1; // ary[0]=1
ary[1] = *(ary+0)+2; // arr[1]=3
ary[2] = *ary+3; // arr[2] = 4
for(int i=0; i<3; i++){
  s=s+ary[i];
}
 
printf("%d",s);
 
}
```
답 : 8

```c
#include <stdio.h>
 
int main(){
int *arr[3];
int a = 12, b = 24, c = 36;
arr[0] = &a;
arr[1] = &b;
arr[2] = &c;
 
printf("%d\n", *arr[1] + **arr + 1);
 
}
```
답 : 24+12+1 = 37

```c
#include <stdio.h>
 
struct jsu {
  char name[12];
  int os, db, hab, hhab;
};
 
int main(){
struct jsu st[3] = {{"데이터1", 95, 88}, 
                    {"데이터2", 84, 91}, 
                    {"데이터3", 86, 75}};
struct jsu* p;
 
p = &st[0];
 
(p + 1)->hab = (p + 1)->os + (p + 2)->db; // 84+75 = 159
(p + 1)->hhab = (p+1)->hab + p->os + p->db; // 84+75+95+88 = 159+183
 
printf("%d\n", (p+1)->hab + (p+1)->hhab);
}
```
답 : 501

##### 5를 입력받았을 때 출력 결과
```c
#include <stdio.h>

int func(int a) {
 if(a<=1) return 1;
 return a*func(a-1);
}
 
int main(){
 int a;
 scanf("%d",&a);
 printf("%d",func(a));
}
```
- 
답 : 120

##### 아래 프로그램은 정수를 역순으로 출력하는데 (1)(2)(3)에 들어갈 연산자를 쓰시오
```c
#include <stdio.h>
int main() {
 
  int number = 1234;
  int div = 10;
  int result = 0;
 
  while (number ( 1 ) 0) {
  
    result = result * div;
    result = result + number ( 2 ) div;
    number = number ( 3 ) div;
  
  }
 
  printf("%d", result);
return 0;
 
}
```
답 : (1) >  (2) % (3) /

```c
	#include <stdio.h>
struct A{
  int n;
  int g;
};
 
int main() { 
struct A a[2];
  for(int i=0;i<2;i++){
    a[i].n=i, a[i].g=i+1;
  }
  printf("%d",a[0].n+a[1].g);
}
```
답 : 2

```c
	#include <stdio.h>
 
int len(char*p);
 
int main(){
 
  char*p1 = "2022";
  char*p2 = "202207";  
  
  int a = len(p1); // 4
  int b = len(p2); // 6
  
  printf("%d", a+b);
}
 
int len(char*p){
  int r = 0;
  while(*p != '\0'){
    p++;
    r++;
  }
return r;
}
```
답 : 10

```c
#include <stdio.h>
 
int main(int argc, char*argv[]) {
  int a[4]={0,2,4,8};
  int b[3]={};
  int i=1;
  int sum=0;
  int *p1;
 
  for(i;i<4;i++){
    p1=a+i;
    b[i-1]=*p1-a[i-1]; // b[0]=2-0=2
    sum=sum+b[i-1]+a[i];
  }
  printf("%d",sum);
 
  return 0;
}
```
답 : 22

##### 🔥 아래는 C언어의 2차원 배열 형태이다. field의 경우 2차원 배열 형태는 예시처럼 출력되므로, 이를 참고하여 mines의 2차원 배열 형태를 작성하시오.
```c
#include <stdio.h>
void main(){
 
int mines[4][4] = {{0,0,0,0},{0,0,0,0},{0,0,0,0},{0,0,0,0}};
int field[4][4] = {{0,1,0,1},{0,0,0,1},{1,1,1,0},{0,1,1,1}};
 
int w = 4, h = 4;
 
  for(int y=0; y<h; y++) {
      for(int x=0;x<w;x++) {  
        if(field[y][x] == 0) continue;
        for(int j=y-1;j<=y+1;j++) {
          for(int i=x-1;i<=x+1;i++) {
                  if(chkover(w,h,j,i) == 1) 
                     mines[j][i] += 1;
          }
        }
      }
    }
 }
 
int chkover(int w,int h,int j,int i) {
  if (i >= 0 && i < w && j >= 0 && j < h) return 1;
  return 0;
}
```
답: 
	1 1 3 2
	3 4 5 3
	3 5 6 4
	3 5 5 3

```c
#include<stdio.h>
main(){
  int s, el =0;
  for(int i=6; i<=30; i++){
    s=0;
    for(int j=1; j<=i/2; j++){
      if(i%j==0){
        s=s+j;
      }
    }
    if(s==i){
    el++;
    }
  }
  
  // i가 6이면, 1~3을 돌면서, 5/j==0 즉 약수면 해당 약수를 더한다.
  // 약수의 합이 i랑 동일하면 el++
  printf("%d", el);
  }
```
- **결국은 6~30사이의 i라는 숫자가 있을 때, 약수 중에서 i/2 이하인 약수들의 합이 i와 동일한 경우를 찾는 것**
- 완전수가 6이랑 28이라네요.
답 : 2

```c
#include <stdio.h>
 
int main(void) {
  char a[]="Art";
  char*p=NULL;
  p=a;
  printf("%s\n",a);
  printf("%c\n",*p);
  printf("%c\n",*a);
  printf("%s\n",a);
 
  for(int i=0;a[i]!='\0';i++){
    printf("%c",a[i]);
  }
}
```
- 
답 :
	Art
	A
	A
	Art
	Art


```c
	#include <stdio.h>
 
int main(void) {
  char *a = "qwer";
  char *b = "qwtety";
  for (int i = 0; a[i] != '\0'; i++) {
    for (int j = 0; b[j] != '\0'; j++) {
      if (a[i] == b[j]) printf("%c", a[i]);
    }
  }
}
```
답 : qwe

```c
	#include <stdio.h>
 
int main(void) {
int input = 101110;
int di = 1;
int sum = 0;
 
while (input > 0) {
sum = sum + (input (가)(나) * di);
di = di * 2;
input = input / 10;
}
 
printf("%d", sum);
 
return 0;
}
```
- ![[Pasted image 20260414165622.png]]
답 : **(가) % (나) 10**

```c
#include <stdio.h>
 
void swap(int* idx1, int* idx2) {
  
  int t = *idx1;
  *idx1 = *idx2;
  *( 가 ) = t;
}
void Usort(int a[], int len) {
  for (int i = 0; i < len - 1; i++) {
    for (int j = 0; j < len - i - 1; j++) {
      if (a[j] > a[j + 1])
        swap(&a[j], &a[j + 1]);
    }
  }
 
  for (int k = 0; k < 5; k++) {
    printf("%d ", a[k]);
  }
}
 
int main(void) {
  int arr[] = {64, 34, 25, 12, 40};
  int nx = 5;
 
  Usort(arr, (나));
  return 0;
}
```
답 : (가) idx2 (나) nx

```c
int main()
{
    int n[5];
    int i;
    
    for(i=0;i<5;i++){
        printf("숫자를 입력하세요 : ");
        scanf("%d",&n[i]);
    }
    
    for(i=0;i<5;i++){
        printf("%d",(가));
    }
 
    return 0;
}
```
- n[] = {5,4,3,2,1}
답 : **n[(i+1)%5]**

```c
#include<stdio.h> 
 
int main()
{
	int m=4620;
	int a,b,c,d;
	a=(가)
	b=(나)
	c=(다)
	d=(라)
	printf("1000원 개수: %d",a);
	printf("500원 개수: %d",b);
	printf("100원 개수: %d",c);
	printf("10원 개수: %d",d);
	return 0;
}
```
답 : 
- m/1000;
- (m%1000)/500;
- (m%500)/100;
- (m%100)/10;

##### 🔥 다음 문제에서 홍길동, 김철수, 박영희 순서대로 입력했다고 할 때 출력결과
```c
#include<stdio.h> 
#include<stdlib.h> 
 
char n[30];
 
char *test() {
	printf("입력하세요 : ");
	gets(n);
	return n;
}
 
int main()
{
	char * test1;
	char * test2;
	char * test3;
	 
	test1 = test();
	test2 = test();
	test3 = test();
	 
	printf("%s\n",test1);
	printf("%s\n",test2);
	printf("%s",test3);
	return 0;
}
```
- **gets(n) : \n기준으로 n에 차례대로 입력 데이터를 채움**
- **return n이기 때문에, 계속해서 n의 시작 주소 위치에 저장하고 있다.**
- **따라서 마지막에 저장된 "박영희"를 test1, test2, test3 모두 n의 시작 가르키고 있다.**
답 : 
	박영희
	박영희
	박영희

```c
#include<stdio.h>
 
int main(void)
{
    int n[3] = {73, 95, 82};
    int sum = 0;
    for(int i=0;i<3;i++){
        sum += n[i];
	}
 
	switch(sum/30){
	  case 10:
	  case 9: printf("A");
	  case 8: printf("B");
	  case 7: 
	  case 6: printf("C");
	  default: printf("D");
	}
    return 0;
}
```
답 : BCD


```c
	#include<stdio.h>
 
int main(void){
    int c=0;
    for(int i = 1; i <=2023; i++) { 
      if(i%4 == 0) c++; 
	}
	printf("%d", c);
	return 0;
}
```
답 : 505

```c
#include<stdio.h>
#define MAX_SIZE 10
 
int isWhat[MAX_SIZE];
int point= -1; 
 
void into(int num) {
    if (point >= 10) printf("Full");
    isWhat[++point] = num;
}
 
int take() {
if (isEmpty() == 1) printf("Empty");
return isWhat[point--];
}
 
int isEmpty() {
    if (point == -1) return 1;
    return 0;
}
 
int isFull() {
    if (point == 10) return 1;
    return 0;
}
 
int main(int argc, char const *argv[])
{
    int e;
    into(5); 
    into(2);
    while(!isEmpty())
    {
        printf("%d", take()); // point -> 0  print2
        into(4); //1
        into(1); //2
        printf("%d", take()); //p1 print1
 
        into(3); 
        printf("%d", take()); 
        printf("%d", take()); 
 
        into(6); 
        printf("%d", take()); 
        printf("%d", take()); 
    }
    return 0;
}
```
- 
답 : 213465

##### 선택정렬을 하는 코드이다. (가)에 들어갈 기호를 쓰시오.
```c
#include<stdio.h>
int main(void){
int E[] = {64, 25, 12, 22, 11};
    int n = sizeof(E) / sizeof(E[0]); // n=5
    
    int i = 0;
    do {
        int j = i + 1;
        do {
 
            if (E[i] (가) E[j]) {
                int tmp = E[i];
                E[i] = E[j];
                E[j] = tmp;
            }
            j++;
 
       } while (j < n);
       
       i++;
    } while (i < n - 1);
    
return 0;
    
}
```
답 : (가) >

```c
#include <stdio.h>
int main() {
	char* p = "KOREA";
	printf("%s\n", p);
	printf("%s\n", p+1);
	printf("%c\n", *p);
	printf("%c\n", *(p+3));
	printf("%c\n", *p+4);
}
```
답 : 
	KOREA
	OREA
	K
	E
	O


##### 4번 C언어에서 구조체의 멤버에 접근하기 위한 기호를 쓰시오.
답 : ->


```c
#include<stdio.h>
int complete(int n) {
	int sum = 0;
	for(int j=1; j<=n/2; j++) {
		if(n%j == 0) {
			sum = sum+j;
		}
	}
	if(sum==n) {
		return 1;
	} else {
		return 0;
	}
}
int main() {
	int s = 0;
	for(int i=1; i<=100; i++) {
		if(complete(i))
			s += i;
	}
	printf("%d", s);
}
```
- 6+28 = 34
- 496까지 외워두자
답 : 34

```c
#include<stdio.h>
int f(int n) {
	if(n<=1) return 1;
	else return n*f(n-1);
}
int main() {
	printf("%d", f(7));
}
```
답 : 5040


___

## 24년

```c
#include <stdio.h>
 
int main() {
 
    int v1 = 0, v2 = 35, v3 = 29;
    
    if(v1 > v2 ? v2 : v1) {
        v2 = v2 << 2;
    }else{
        v3 = v3 << 2;
    }
    
    printf("%d", v2+v3);
}
```
답 : 151

```c
#include <stdio.h>
#include <string.h>
 
void reverse(char* str){
    int len = strlen(str);
    char temp;
    char*p1 = str;
    char*p2 = str + len - 1;
    while(p1<p2){
        temp = *p1;
        *p1 = *p2;
        *p2 = temp;
        p1++;
        p2--;
    }
}
 
int main(int argc, char* argv[]){
    char str[100] = "ABCDEFGH";
 
    reverse(str);
 
    int len = strlen(str);
 
    for(int i=1; i<len; i+=2){
        printf("%c",str[i]);
    }
 
    printf("\n");
 
    return 0;
 
}
```
답 : GECA

```c
#include <stdio.h>
 
 
typedef struct{
    int accNum;
    double bal;
}BankAcc;
 
 
 
double sim_pow(double base, int year){
    int i;
    double r = 1.0;
 
    for(i=0; i<year; i++){
        r = r*base;
    }
    return r;
} 
 
 
 
void initAcc(BankAcc *acc, int x, double y){
    acc -> accNum = x;
    acc -> bal = y;
}
 
 
 
void xxx(BankAcc *acc, double *en){
    if (*en > 0 && *en < acc -> bal) {
        acc -> bal = acc -> bal-*en;
    }else{
        acc -> bal = acc -> bal+*en;
    }
}
 
 
 
void yyy(BankAcc *acc){
    acc -> bal = acc -> bal * sim_pow((1+0.1),3);
}
 
 
int main(){
 
    BankAcc myAcc;
    initAcc(&myAcc, 9981, 2200.0);
    double amount = 100.0;
    xxx(&myAcc, &amount);
    yyy(&myAcc);
    printf("%d and %.2f", myAcc.accNum, myAcc.bal);
    return 0;
 
}
```
	- **자바나 파이썬이랑 다르게 C에서는 구조체를 그냥 넘기면(포인터가 아니라) 복사본으로 생성**
	- **따라서 아무리 뭘 해도 myAcc 값은 안바뀜!!**
- 1.1^3 만큼 곱해야함.
답 : 9981 and 2795.10


```c
#include<stdio.h>
#include<ctype.h>
 
int main(){
    char*p = "It is 8";
    char result[100];
    int i;
 
    for(i=0; p[i]!='\0'; i++){
        if(isupper(p[i]))
            result[i] = (p[i]-'A'+5)% 25 + 'A';
        else if(islower(p[i]))
            result[i] = (p[i]-'a'+10)% 26 + 'a';
        else if(isdigit(p[i]))
            result[i] = (p[i]-'0'+3)% 10 + '0';
        else if(!(isupper(p[i]) || islower(p[i]) || isdigit(p[i])))    
            result[i] = p[i];
    }
 
    result[i] = '\0';
    printf("%s\n",result);
 
    return 0;
}
```

답 : Nd sc 1

```c
	#include <stdio.h>
 
int main() {
    int arr[3][3] = {1, 2, 3, 4, 5, 6, 7, 8, 9};
    int* parr[2] = {arr[1], arr[2]};
    printf("%d", parr[1][1] + *(parr[1]+2) + **parr);
    
    return 0;
}
```
답 : 21

#### 🔥 포인터로 인해서 while문 밖의 값도 바뀌게 된다.
```c
#include <stdio.h>
#include <string.h>
 
void sumFn(char* d, char* s) {
    int sum = 0;
 
    while (*s) {
        *d = *s;
        d++;
        s++;
    }
    *d = '\0'; 
}
 
int main() {
    char* str1 = "first";
    char str2[50] = "teststring";  
    int result=0;
    sumFn(str2, str1);
 
    for (int i = 0; str2[i] != '\0'; i++) {
        result += i;
    }
    printf("%d", result);
    
    return 0;
}
```
- 0+1+2+3+4 = 10
-  *** d를 하면서 first로 대체된다!**
답 : 10

- 우논시절 통순기(응집도 높아지는 순서)
- 내공외제스자(결합도 낮아지는 순서)

#### 🔥 포인터로 안넘기면, 별개의 복사본으로 들어감
```c
	#include <stdio.h>
 
void swap(int a, int b) {
    int t = a;
    a = b;
    b = t;
}
 
int main() {
    
    int a = 11;
    int b = 19;
    swap(a, b);
    
    switch(a) {
        case 1:
            b += 1;
        case 11:
            b += 2;
        default:
            b += 3;
        break;
    }
    
    printf("%d", a-b);
}
```
- 포인터 없어서 swap()해도 안바뀜
- a가 11이니까 +2하고 break 없으니까 default도 해야함
- 11-24 =-13
답 : -13

```c
	#include <stdio.h>
 
struct node {
    int n1;
    struct node *n2;
};
 
int main() {
 
    struct node a = {10, NULL};
    struct node b = {20, NULL};
    struct node c = {30, NULL};
 
    struct node *head = &a;
    a.n2 = &b;
    b.n2 = &c;
 
    printf("%d\n", head->n2->n1);
 
    return 0;
}
```
답 : 20


```c
#include <stdio.h>
 
int func(){
 static int x =0; 
  x+=2; 
  return x;
}
 
int main(){
  int x = 1; 
  int sum=0; 
  for(int i=0;i<4;i++) {
    x++; 
    sum+=func();
  } 
  printf("%d", sum);
 
  return 0;
}
```
- **static 조심**
답 : 20

#### 🔥 꼼꼼하게 안보면 실수하기 딱 좋은 문제
```c
#include <stdio.h>
 
struct Node {
 int value;
 struct Node* next;
};
 
void func(struct Node* node){
  while(node != NULL && node->next != NULL){
     int t = node->value;
     node->value = node->next->value;
     node->next->value = t;
     node = node->next->next;
  }
}
 
int main(){
  struct Node n1 = {1, NULL};
  struct Node n2 = {2, NULL};
  struct Node n3 = {3, NULL};
  
  n1.next = &n3;
  n3.next = &n2;
 
  func(&n1);  
 
  struct Node* current = &n1;
 
  while(current != NULL){
    printf("%d", current->value);
    current = current->next;
 }
 
 return 0;
 
}
```
- **시행 횟수가 적으면 그냥 직접 다 쓰면서 하자!**
답: 312

```c
#include <stdio.h>
 
void func(int** arr, int size){
  for(int i=0; i<size; i++){
     *(*arr + i) = (*(*arr+i) + i) % size;
  }
}
 
int main(){
  int arr[] = {3,1, 4, 1, 5};
  int* p = arr;
  int** pp = &p;
  int num = 6;
  
  func(pp, 5);  
  num = arr[2];
  printf("%d", num);  
 
  return 0;
}
```
답 : 1

```c
#include <stdio.h>
char Data[5] = {'B', 'A', 'D', 'E'};
char c;
 
int main(){
    int i, temp, temp2;
 
    c = 'C';
    printf("%d\n", Data[3]-Data[1]); // 4
 
    for(i=0;i<5;++i){
        if(Data[i]>c) // i=2
            break;
    }
 
    temp = Data[i]; // temp='D'
    Data[i] = c; // Data[2] = ='C'
    i++; // i=3
 
	// BACE
	// BACD
    for(;i<5;++i){
        temp2 = Data[i]; // E / 
        Data[i] = temp; // 
        temp = temp2; // temp='E'
    }
 
    for(i=0;i<5;i++){
        printf("%c", Data[i]);
    }
}
```
답 : 
	4
	