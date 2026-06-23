## 이상호 멘토님

### 1. 기존의 Naive RAG의 문제점
1. 청크와 청크를 hopping(넘나들어야지 알 수 있는) 정보는 안나옴(A의 선생님인 B의 이름은?)
	- B가 A의 선생님이라는 것 + B의 이름 -> 이 두개의 청킹이 함께 top-k로 안나옴
2. 청킹이 제대로 되지 않으면 이상한 대답이 나옴
3. 문서 전체에 대한 답변은 명확하지 않음 -> top-k 기반으로만 답변을 생성하기 때문에

- 각각의 청크들을 독립적으로 저장한다.
- 검색을 할 때 쿼리와 청크의 유사도를 보고 top-k 청크만 볼 수 있음
	- 즉 청크들 간의 연결된 내용이나 관계를 전혀 알 수 없음.

### 2. GraphRAG는 Naive RAG와 다르게 Structer(구조)를 저장한다.
- 원본 텍스트가 있다면 -> <u>그래프를 구성</u>
	1. 엔티티(Entity) 추출 -> MS에서 나온 GraphRAG에서 굉장히 디테일한 프롬프트를 통해서 추출함
	2. 관계(Relation) 추출
	3. 커뮤니티(Community) 생성, 탐지 -> leiden 알고리즘
	4. 커뮤니티 요약

![[Pasted image 20260413144322.png]]
-> <font color="#ffc000">왜 이 답이 나왔는지를 쉽게 알 수 있다!!!</font>

![[Pasted image 20260413144520.png]]
- type은 일종의 메타데이터(사람이면 Person, 조직이면 Organization)


![[Pasted image 20260413145320.png]]
- 라이브러리에서 gpt를 통해서 전체 문서를 읽고 json형식으로 Relation과 Entity를 규정해준다.
	- 그렇지만 확인을 하는 과정이 필요하다 <font color="#ffc000">할루시네이션 조심!!!</font>
##### 할루시네이션 데이터 검수
	1. **엔티티의 이름이 normalized 되었는지 확인해야함**
		 - 콰빅스 연구소, 콰빅스 랩, => 이런 애들이 다 따로 되는 경우가 있음..
		 - 검색에서의 지표들을 어떻게 만드는지가 중요함.
	2. **놓친 관계가 있는지 확인해야함**
		- mentor_of가 화살표가 누락이 되어 있다던가,,

- 사실 노가다를 하지 않기 위해서 라이브러리를 사용하는거라서,, 쉽지 않음.

##### MS의 GraphRAG에서 해주는 것
	1. **청킹**
		- 일반적으로 gpt4 모델의 컨텍스트 사이즈는 128k token(13만 토큰==A4용지 5~6장)
			- System prompt+context+user-prompt+(output) 이거를 위한 공간이 부족함
			- 따라서 청킹은 무조건 해야한다는 것임
	2. **엔티티/관계 중복 제거, 요약**
	3. **커뮤니티 탐지 (leiden Algorithm)**
	4. **커뮤니티 요약**
	5. **parquet 파일로 저장** (저장 후 영구적으로 사용)



![[Pasted image 20260413153446.png]]


with open(settings_path, encoding='utf-8') as f:
cfg = yaml.safe_load(f)
**Smaller chunks → more granular entities (at the cost of more LLM calls)**
chunk_key = 'chunking' if 'chunking' in cfg else 'chunks'
cfg[chunk_key]['size'] = 600
**Enable GraphML export so we can visualise the graph in section 7**
cfg.setdefault('snapshots', {})['graphml'] = True
with open(settings_path, 'w', encoding='utf-8') as f:
yaml.dump(cfg, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
print(f'Patched settings.yaml:')
print(f'  {chunk_key}.size = 600')
print(f'  snapshots.graphml = true')
