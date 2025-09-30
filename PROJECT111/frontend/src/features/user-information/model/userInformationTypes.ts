export interface UserInformation {
  // 기본 정보
  activityRegions: ActivityRegion[];
  githubUrl?: string;
  portfolioUrl?: string;
  introduction?: string;
  
  // 기술 역량 및 경험
  major?: Major;
  expertise: ExpertiseArea[];
  techStack: TechStack[];
  collaborationTools: CollaborationTool[];
  sideProjectExperience?: SideProjectExperience;
  
  // 협업 성향 및 방식
  collaborationStyle?: CollaborationStyle;
  meetingFrequency?: MeetingFrequency;
  belbinRole?: BelbinRole;
  
  // 프로젝트 관련 선호도
  preferredTeamSize?: PreferredTeamSize;
  preferredProjectTopics: PreferredProjectTopic[];
  availablePeriod?: AvailablePeriod;
}

export interface Option<T> {
  id: T;
  label: string;
}

// Activity Regions
export const ActivityRegion = {
  SEOUL: "SEOUL",
  CHUNGCHEONG: "CHUNGCHEONG",
  YEONGNAM: "YEONGNAM",
  HONAM: "HONAM",
  OTHER: "OTHER"
} as const;

export type ActivityRegion = typeof ActivityRegion[keyof typeof ActivityRegion];

export const ACTIVITY_REGIONS: Option<ActivityRegion>[] = [
  { id: ActivityRegion.SEOUL, label: "수도권" },
  { id: ActivityRegion.CHUNGCHEONG, label: "충청권" },
  { id: ActivityRegion.YEONGNAM, label: "영남권" },
  { id: ActivityRegion.HONAM, label: "호남권" },
  { id: ActivityRegion.OTHER, label: "기타" }
];

// Majors
export const Major = {
  COMPUTER_SCIENCE: "COMPUTER_SCIENCE",
  INFORMATION_SECURITY: "INFORMATION_SECURITY",
  DESIGN: "DESIGN",
  BUSINESS: "BUSINESS",
  NON_MAJOR: "NON_MAJOR"
} as const;

export type Major = typeof Major[keyof typeof Major];

export const MAJORS: Option<Major>[] = [
  { id: Major.COMPUTER_SCIENCE, label: "컴퓨터공학" },
  { id: Major.INFORMATION_SECURITY, label: "정보보호" },
  { id: Major.DESIGN, label: "디자인" },
  { id: Major.BUSINESS, label: "경영/기타" },
  { id: Major.NON_MAJOR, label: "비전공자" }
];

// Expertise Areas
export const ExpertiseArea = {
  FRONTEND: "FRONTEND",
  BACKEND: "BACKEND",
  AI_ML: "AI_ML",
  APP_DEV: "APP_DEV",
  GAME_DEV: "GAME_DEV",
  DATA_ANALYSIS: "DATA_ANALYSIS",
  PLANNING_PM: "PLANNING_PM",
  UI_UX: "UI_UX"
} as const;

export type ExpertiseArea = typeof ExpertiseArea[keyof typeof ExpertiseArea];

export const EXPERTISE_AREAS: Option<ExpertiseArea>[] = [
  { id: ExpertiseArea.FRONTEND, label: "프론트엔드" },
  { id: ExpertiseArea.BACKEND, label: "백엔드" },
  { id: ExpertiseArea.AI_ML, label: "AI/머신러닝" },
  { id: ExpertiseArea.APP_DEV, label: "앱 개발" },
  { id: ExpertiseArea.GAME_DEV, label: "게임 개발" },
  { id: ExpertiseArea.DATA_ANALYSIS, label: "데이터 분석" },
  { id: ExpertiseArea.PLANNING_PM, label: "기획/PM" },
  { id: ExpertiseArea.UI_UX, label: "UI/UX 디자인" }
];

// Tech Stacks
export const TechStack = {
  REACT: "REACT",
  VUE: "VUE",
  HTML_CSS_JS: "HTML_CSS_JS",
  DJANGO: "DJANGO",
  FLASK: "FLASK",
  NODEJS: "NODEJS",
  JAVA: "JAVA",
  SPRING: "SPRING",
  PYTHON: "PYTHON",
  C_CPP: "C_CPP",
  KOTLIN: "KOTLIN",
  SWIFT: "SWIFT",
  TENSORFLOW: "TENSORFLOW",
  PYTORCH: "PYTORCH",
  MYSQL: "MYSQL",
  MONGODB: "MONGODB",
  OTHER: "OTHER"
} as const;

export type TechStack = typeof TechStack[keyof typeof TechStack];

export const TECH_STACKS: Option<TechStack>[] = [
  { id: TechStack.REACT, label: "React" },
  { id: TechStack.VUE, label: "Vue" },
  { id: TechStack.HTML_CSS_JS, label: "HTML/CSS/JS" },
  { id: TechStack.DJANGO, label: "Django" },
  { id: TechStack.FLASK, label: "Flask" },
  { id: TechStack.NODEJS, label: "Node.js" },
  { id: TechStack.JAVA, label: "Java" },
  { id: TechStack.SPRING, label: "Spring" },
  { id: TechStack.PYTHON, label: "Python" },
  { id: TechStack.C_CPP, label: "C/C++" },
  { id: TechStack.KOTLIN, label: "Kotlin" },
  { id: TechStack.SWIFT, label: "Swift" },
  { id: TechStack.TENSORFLOW, label: "TensorFlow" },
  { id: TechStack.PYTORCH, label: "PyTorch" },
  { id: TechStack.MYSQL, label: "MySQL" },
  { id: TechStack.MONGODB, label: "MongoDB" },
  { id: TechStack.OTHER, label: "기타" }
];

// Collaboration Tools
export const CollaborationTool = {
  GIT: "GIT",
  GITHUB: "GITHUB",
  NOTION: "NOTION",
  FIGMA: "FIGMA",
  SLACK: "SLACK",
  DISCORD: "DISCORD",
  JIRA: "JIRA",
  TRELLO: "TRELLO"
} as const;

export type CollaborationTool = typeof CollaborationTool[keyof typeof CollaborationTool];

export const COLLABORATION_TOOLS: Option<CollaborationTool>[] = [
  { id: CollaborationTool.GIT, label: "Git" },
  { id: CollaborationTool.GITHUB, label: "GitHub" },
  { id: CollaborationTool.NOTION, label: "Notion" },
  { id: CollaborationTool.FIGMA, label: "Figma" },
  { id: CollaborationTool.SLACK, label: "Slack" },
  { id: CollaborationTool.DISCORD, label: "Discord" },
  { id: CollaborationTool.JIRA, label: "Jira" },
  { id: CollaborationTool.TRELLO, label: "Trello" }
];

// Side Project Experience
export const SideProjectExperience = {
  NONE: "NONE",
  ONCE: "ONCE",
  TWICE_THRICE: "TWICE_THRICE",
  FOUR_PLUS: "FOUR_PLUS"
} as const;

export type SideProjectExperience = typeof SideProjectExperience[keyof typeof SideProjectExperience];

export const SIDE_PROJECT_EXPERIENCE: Option<SideProjectExperience>[] = [
  { id: SideProjectExperience.NONE, label: "없음" },
  { id: SideProjectExperience.ONCE, label: "1회" },
  { id: SideProjectExperience.TWICE_THRICE, label: "2~3회" },
  { id: SideProjectExperience.FOUR_PLUS, label: "4회 이상" }
];

// Collaboration Styles
export const CollaborationStyle = {
  OFFLINE: "OFFLINE",
  ONLINE: "ONLINE",
  HYBRID: "HYBRID"
} as const;

export type CollaborationStyle = typeof CollaborationStyle[keyof typeof CollaborationStyle];

export const COLLABORATION_STYLES: Option<CollaborationStyle>[] = [
  { id: CollaborationStyle.OFFLINE, label: "오프라인 중심" },
  { id: CollaborationStyle.ONLINE, label: "온라인 중심" },
  { id: CollaborationStyle.HYBRID, label: "혼합" }
];

// Meeting Frequencies
export const MeetingFrequency = {
  WEEKLY: "WEEKLY",
  TWICE_THRICE_WEEKLY: "TWICE_THRICE_WEEKLY",
  DAILY: "DAILY",
  PROJECT_BASED: "PROJECT_BASED"
} as const;

export type MeetingFrequency = typeof MeetingFrequency[keyof typeof MeetingFrequency];

export const MEETING_FREQUENCIES: Option<MeetingFrequency>[] = [
  { id: MeetingFrequency.WEEKLY, label: "주 1회" },
  { id: MeetingFrequency.TWICE_THRICE_WEEKLY, label: "주 2~3회" },
  { id: MeetingFrequency.DAILY, label: "매일 가능" },
  { id: MeetingFrequency.PROJECT_BASED, label: "프로젝트 중심만 가능" }
];

// Belbin Roles
export const BelbinRole = {
  PL: "PL",
  RI: "RI",
  CO: "CO",
  SH: "SH",
  ME: "ME",
  TW: "TW",
  IMP: "IMP",
  CF: "CF",
  SP: "SP"
} as const;

export type BelbinRole = typeof BelbinRole[keyof typeof BelbinRole];

export interface BelbinRoleOption extends Option<BelbinRole> {
  description: string;
}

export const BELBIN_ROLES: BelbinRoleOption[] = [
  {
    id: BelbinRole.PL,
    label: "PL - 아이디어 뱅크 (Plant)",
    description: "창의적이고, 문제를 새로운 아이디어로 해결하는 데 능하다."
  },
  {
    id: BelbinRole.RI,
    label: "RI - 자원탐색자 (Resource Investigator)",
    description: "외부 자원을 탐색하고, 네트워킹과 기회를 잘 활용한다."
  },
  {
    id: BelbinRole.CO,
    label: "CO - 조정자 (Coordinator)",
    description: "팀 내 사람들을 조율하고, 자원을 효율적으로 배분할 수 있다."
  },
  {
    id: BelbinRole.SH,
    label: "SH - 추진자 (Shaper)",
    description: "압박 속에서도 목표를 추진하고 성과를 이끌어내는 데 능하다."
  },
  {
    id: BelbinRole.ME,
    label: "ME - 평가자 (Monitor Evaluator)",
    description: "논리적이고 객관적인 판단으로 전략적 사고를 지향한다."
  },
  {
    id: BelbinRole.TW,
    label: "TW - 팀 워커 (Teamworker)",
    description: "협력과 공감을 통해 팀 분위기를 부드럽게 만든다."
  },
  {
    id: BelbinRole.IMP,
    label: "IMP - 실행자 (Implementer)",
    description: "실행력과 체계적인 방식으로 계획을 현실로 옮긴다."
  },
  {
    id: BelbinRole.CF,
    label: "CF - 완성자 (Completer Finisher)",
    description: "꼼꼼하고 세심하게 마무리까지 책임진다."
  },
  {
    id: BelbinRole.SP,
    label: "SP - 전문가 (Specialist)",
    description: "특정 분야의 전문성을 바탕으로 깊이 있는 기여를 한다."
  }
];

// Preferred Team Sizes
export const PreferredTeamSize = {
  TWO_THREE: "TWO_THREE",
  FOUR_FIVE: "FOUR_FIVE",
  SIX_PLUS: "SIX_PLUS",
  OTHER: "OTHER"
} as const;

export type PreferredTeamSize = typeof PreferredTeamSize[keyof typeof PreferredTeamSize];

export const PREFERRED_TEAM_SIZES: Option<PreferredTeamSize>[] = [
  { id: PreferredTeamSize.TWO_THREE, label: "2~3명" },
  { id: PreferredTeamSize.FOUR_FIVE, label: "4~5명" },
  { id: PreferredTeamSize.SIX_PLUS, label: "6명 이상도 가능" },
  { id: PreferredTeamSize.OTHER, label: "기타" }
];

// Preferred Project Topics
export const PreferredProjectTopic = {
  WEB_SERVICE: "WEB_SERVICE",
  APP_DEV: "APP_DEV",
  AI: "AI",
  CHATBOT: "CHATBOT",
  SOCIAL_MEDIA: "SOCIAL_MEDIA",
  COMMUNITY: "COMMUNITY",
  HEALTHCARE: "HEALTHCARE",
  EDUCATION: "EDUCATION",
  FINANCE: "FINANCE",
  OTHER: "OTHER"
} as const;

export type PreferredProjectTopic = typeof PreferredProjectTopic[keyof typeof PreferredProjectTopic];

export const PREFERRED_PROJECT_TOPICS: Option<PreferredProjectTopic>[] = [
  { id: PreferredProjectTopic.WEB_SERVICE, label: "웹 서비스" },
  { id: PreferredProjectTopic.APP_DEV, label: "앱 개발" },
  { id: PreferredProjectTopic.AI, label: "인공지능" },
  { id: PreferredProjectTopic.CHATBOT, label: "챗봇" },
  { id: PreferredProjectTopic.SOCIAL_MEDIA, label: "소셜 미디어" },
  { id: PreferredProjectTopic.COMMUNITY, label: "커뮤니티" },
  { id: PreferredProjectTopic.HEALTHCARE, label: "헬스케어" },
  { id: PreferredProjectTopic.EDUCATION, label: "교육" },
  { id: PreferredProjectTopic.FINANCE, label: "금융" },
  { id: PreferredProjectTopic.OTHER, label: "기타" }
];

// Available Periods
export const AvailablePeriod = {
  SHORT: "SHORT",
  MEDIUM: "MEDIUM",
  LONG: "LONG",
  OTHER: "OTHER"
} as const;

export type AvailablePeriod = typeof AvailablePeriod[keyof typeof AvailablePeriod];

export const AVAILABLE_PERIODS: Option<AvailablePeriod>[] = [
  { id: AvailablePeriod.SHORT, label: "단기: 1달 이내" },
  { id: AvailablePeriod.MEDIUM, label: "중기: 2~3달" },
  { id: AvailablePeriod.LONG, label: "장기: 3달 이상" },
  { id: AvailablePeriod.OTHER, label: "기타" }
]; 