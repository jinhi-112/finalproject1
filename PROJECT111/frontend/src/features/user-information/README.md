# User Information Feature

사용자 프로필 정보 입력을 위한 feature입니다.

## 구조

```
user-information/
├── components/
│   └── UserInformationForm/
│       ├── UserInformationForm.tsx (메인 폼)
│       ├── BasicInfoSection.tsx (기본 정보)
│       ├── TechnicalSkillsSection.tsx (기술 역량)
│       ├── CollaborationSection.tsx (협업 성향)
│       ├── ProjectPreferencesSection.tsx (프로젝트 선호도)
│       └── index.ts
├── pages/
│   └── UserInformationPage.tsx
├── model/
│   └── userInformationTypes.ts
└── README.md
```

## 기능

- 4단계로 구성된 사용자 정보 입력 폼
- 각 섹션별 유효성 검사
- 진행률 표시
- 벨빈 팀 역할 설명 자동 표시

## 사용법

`/profile` 경로로 접속하여 사용자 정보를 입력할 수 있습니다. 