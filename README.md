# Bookshelf

한 줄 소개

## 소개

이 프로젝트가 어떤 문제를 해결하려고 하는지 설명합니다.

## 주요 기능

- 블로그 작성/수정/삭제
- 태그 기반 글 분류
- 댓글 작성
- 실시간 채팅
- 도서 검색
- 도서 기반 독서 기록

## 기술 스택

- Backend: Django
- Database: SQLite
- Realtime: Django Channels
- Frontend: Django Template, Bootstrap, JavaScript
- External API: Aladin Open API
- Editor: CKEditor

## 앱 구조

- users: 회원가입, 로그인, 프로필 이미지
- blogs: 블로그, 댓글, 태그
- chat: 채팅방, WebSocket 실시간 메시지
- library: 도서 검색, 독서 기록

## 핵심 구현

### 도서 검색과 독서 기록

알라딘 API로 도서를 검색하고, 사용자가 기록을 남길 때 Book과 BookNote를 저장합니다.

### 블로그 태그

쉼표로 입력받은 태그를 분리하고, 기존 태그가 없으면 생성한 뒤 블로그에 연결합니다.

### 실시간 채팅

Django Channels를 사용해 채팅방 단위 WebSocket 통신을 구현했습니다.

## 실행 방법

1. 저장소 클론

```bash
git clone ...
cd Bookshelf
