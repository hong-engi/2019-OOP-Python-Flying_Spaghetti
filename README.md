# 2019-2 객체지향 프로그래밍 프로젝트 - **박이홍**
구성원: 2-6 이현지 | 2-3 박로진 | 2-2 홍은기

## 1. 주제
서버/클라이언트를 이용한 여러 명이 할 수 있는 마피아 게임

## 2. 동기
기본적인 마피아게임은 오프라인이므로 사회자가 있어서 이를 주최해야 게임을 진행할 수 있다. 또한 사회자가 있음에도 불구하고 한 명이 절차를 실수하거나 양심적으로 게임하지 않아 재미없게 끝나는 경우가 종종 있다. 이는 사람이 진행하면 실수를 할 수 있을 뿐더러, 사람들이 모두 계획적/암묵적으로 설정한 규칙이 지켜지지 않을 수 있기 때문이다.\
컴퓨터 프로그램으로 마피아게임을 한다면 우선 주어진 절차를 서버가 알고리즘대로 진행시키므로 실수를 하지 않으며, 시간 또한 정확하게 측정이 가능하다. 또한 특정 사람에게 유리하거나 불리하지 않게 공정한 사회를 볼 수 있다. 또한 사람들끼리 서로를 볼 수 없으므로 직업의 익명성이 보장되며, 이는 게임을 더 정확하고 재미있게 만들 수 있다.

## 3. 프로그램 사용 대상
마피아 게임을 아는 사람이라면 누구든지 즐길 수 있다. 특별한 사용 대상이 있지 않다.\
원하신다면 교장 선생님께서도 즐기실 수 있다 히히

## 4. 목적
이 프로젝트의 목적은 서버/클라이언트를 이용하여 다수가 참여할 수 있고, 기존의 마피아 게임의 규칙을 적용하여 다수가 쉽게 즐길 수 있는 마피아 게임을 만드는 것이다.  여러 가지, 작지만 새로운 방식으로의 접근을 통해 기존과 달리 조금 다양하고, 즐겁게 즐길 수 있도록 만들고자 한다.

## 5. 주요기능
1. 메인 서버
- 플레이어의 이름 설정 가능
- 게임 방 만들기 가능
- 방 들어가기 기능
2. 방(서버의 일부)
- 낮, 밤 설정 기능
  - 낮에는 회의 후 투표
    - 투표로 인해서 죽는 사람 결정
  - 밤에는 서로 자신의 능력 사용
    - 직업에 따라 다르게
- 타이머 기능
- 생사나 직업 여부에 따라 채팅 관찰자 다르게
3. 직업
#
마피아 팀이 아닌 모든 사람은 시민이다.\
마피아 팀은 마피아 팀의 생존인원이 시민 팀의 생존인원보다 많아지는 것이 승리 조건이며, 시민은 모든 마피아  죽이는 것이 승리의 조건이다.\
직업에 따라 승리 조건, 밤에 사용하는 능력이 다름
#
1) 마피아
  - 밤마다 죽일 사람을 선택한다
  - 여러 명의 마피아여도 한 명만을 고를 수 있음
  - 마피아 팀끼리 밤에도 채팅이 가능함. 이때 마피아끼리의 채팅은 죽은 사람들에게 보인다.
2) 스파이
  - 밤마다 플레이어 한 명을 조사하여 직업을 알아낼 수 있음
  - 밤에 조사한 플레이어가 마피아일 경우, 마피아와 '접선'한 상태가 되며, 이후 마피아 채팅에 참여 가능
  - 마피아와 접선에 성공하는 순간부터 마피아 팀 인원으로 카운트됨. 이전까지는 시민 팀 인원으로 카운트
3) 의사
  - 밤마다 살릴 사람을 선택한다
  - 군인의 방탄 효과보다 우선으로 발동됨
4) 경찰
  - 밤마다 한 명을 선택하여 마피아인지 확인 가능
5) 기자
  - 밤에 단 1회, 한 명을 선택하여 직업을 알아낼 수 있음(취재). 알아낸 직업은 다음날 낮에 모두에게 공개됨
  - 단, 취재를 한 밤에 기자가 죽을 경우 알아낸 직업은 공개되지 않음.
  - 첫 번째 밤에는 불가능
6) 정치인
  - 투표 시 자신의 표가 2표로 인정됨.
  - 투표로 죽지 않음
7) 탐정
  - 밤마다 사람을 한 명 선택해, 어떤 사람을 선택했는지 관찰 가능함
8) 영매
  - 사망자의 채팅을 볼 수 있음
  - 밤마다 사망자 1명을 선택하여 직업을 알 수 있음. 단, 이때 선택당한 사망자는 이후 채팅을 할 수 없음.
9) 군인
  - 마피아의 공격을 1회 방어 가능.(방탄) 방어 시 다음날 낮에 모두에게 이 사실이 공개됨
  - 스파이가 군인을 조사할 경우, 군인은 스파이인 플레이어를 알게 됨.
0) 이 직업도 추가할까?
  - 짐승인간
  - 연인
  - 건달
  - 도굴꾼
  - 테러리스트

## 6. 프로젝트 핵심
- 게임이 시작되면 정해진 개수에 맞춰 랜덤으로 직업이 배정되어야 한다.
- 밤에 직업별로 특수 행동을 할 수 있도록 구현해야 한다.
- 낮에 모두가 함께 채팅을 하고, 투표 역시 실시간으로 진행되도록 해야 한다. 이때 채팅에서 사망자의 채팅과 생존자의 채팅이 구분되어야 하며, 사망자의 채팅은 사망자 및 영매에게만 보여야 한다.

## 7. 구현에 필요한 라이브러리나 기술
{pygame, matplotlib,  ...}

## 8. **분업 계획**
- 서버, 클라이언트 담당:
- 직업 구현 담당:
- 기타 기능(채팅, 투표 등) 구현 담당:

## 9. 기타

<hr>

#### readme 작성관련 참고하기 [바로가기](https://heropy.blog/2017/09/30/markdown/)

#### 예시 계획서 [[예시 1]](https://docs.google.com/document/d/1hcuGhTtmiTUxuBtr3O6ffrSMahKNhEj33woE02V-84U/edit?usp=sharing) | [[예시 2]](https://docs.google.com/document/d/1FmxTZvmrroOW4uZ34Xfyyk9ejrQNx6gtsB6k7zOvHYE/edit?usp=sharing) | [[예시 3]](https://github.com/goldmango328/2018-OOP-Python-Light) | [[예시4]](https://github.com/ssy05468/2018-OOP-Python-lightbulb) | [[모두보기]](https://github.com/kadragon/oop_project_ex/network/members)
