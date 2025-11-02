import React, { useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Link } from 'react-router-dom';
import { Button } from '@/shared/components/Button';
import { Input } from '@/shared/components/Input';
import { Label } from '@/shared/components/Label';
import { useAuth } from '@/shared/contexts/AuthContext';
import apiClient from '@/api';
import { UserInfoDisplay } from '../components/UserInfoDisplay'; // Import the display component

// --- Data Constants (Should be centralized) ---
const REGION_OPTIONS = [
    { value: 'SEOUL', label: '서울특별시' }, { value: 'BUSAN', label: '부산광역시' }, 
    { value: 'DAEGU', label: '대구광역시' }, { value: 'INCHEON', label: '인천광역시' }, 
    { value: 'GWANGJU', label: '광주광역시' }, { value: 'DAEJEON', label: '대전광역시' }, 
    { value: 'ULSAN', label: '울산광역시' }, { value: 'SEJONG', label: '세종특별자치시' }, 
    { value: 'GYEONGGI', label: '경기도' }, { value: 'GANGWON', label: '강원도' }, 
    { value: 'CHUNGCHEONGBUK', label: '충청북도' }, { value: 'CHUNGCHEONGNAM', label: '충청남도' }, 
    { value: 'JEOLLABUK', label: '전라북도' }, { value: 'JEOLLANAM', label: '전라남도' }, 
    { value: 'GYEONGSANGBUK', label: '경상북도' }, { value: 'GYEONGSANGNAM', label: '경상남도' }, 
    { value: 'JEJU', label: '제주특별자치도' },
];
const MAJOR_OPTIONS = [
  { value: "PROGRAMMING", label: "개발/프로그래밍" }, { value: "DATA_AI", label: "데이터/AI" },
  { value: "SECURITY_NET", label: "보안/네트워크" }, { value: "DESIGN", label: "디자인/기획" },
  { value: "NON_MAJOR", label: "비전공자/기타" }
];
const SPECIALTY_OPTIONS = [{ value: 'frontend', label: '프론트엔드' }, { value: 'backend', label: '백엔드' }, { value: 'ai', label: 'AI/머신러닝' }, { value: 'app', label: '앱 개발' }, { value: 'game', label: '게임 개발' }, { value: 'data', label: '데이터 분석' },{ value: 'UX', label: 'UX/UI 디자인'}, { value: 'PM', label: '기획/PM' }, { value: 'security', label: '정보보안' } ];
const TECH_STACK_OPTIONS = [ { value: 'React', label: 'React' }, { value: 'Vue', label: 'Vue' }, { value: 'HTML/CSS/JS', label: 'HTML/CSS/JS' }, { value: 'Django', label: 'Django' }, { value: 'Flask', label: 'Flask' }, { value: 'Node.js', label: 'Node.js' }, { value: 'Java', label: 'Java' }, { value: 'Spring', label: 'Spring' }, { value: 'Python', label: 'Python' }, { value: 'C/C++', label: 'C/C++' }, { value: 'Kotlin', label: 'Kotlin' }, { value: 'Swift', label: 'Swift' }, { value: 'TensorFlow', label: 'TensorFlow' }, { value: 'PyTorch', label: 'PyTorch' }, { value: 'MySQL', label: 'MySQL' }, { value: 'MongoDB', label: 'MongoDB' }, { value: 'Other', label: '기타' } ];
const COLLAB_TOOL_OPTIONS = [ { value: 'Git', label: 'Git' }, { value: 'GitHub', label: 'GitHub' }, { value: 'Notion', label: 'Notion' }, { value: 'Figma', label: 'Figma' }, { value: 'Slack', label: 'Slack' }, { value: 'Discord', label: 'Discord' }, { value: 'Jira', label: 'Jira' }, { value: 'Trello', label: 'Trello' } ];
const EXPERIENCE_OPTIONS = [ { value: 'NONE', label: '없음' }, { value: 'ONCE', label: '1회' }, { value: 'FEW', label: '2~3회' }, { value: 'MANY', label: '4회 이상' } ];
const COLLABORATION_STYLE_OPTIONS = [ { value: 'OFFLINE', label: '오프라인 중심' }, { value: 'ONLINE', label: '온라인 중심' }, { value: 'HYBRID', label: '혼합' } ];
const MEETING_FREQUENCY_OPTIONS = [ { value: 'WEEKLY_1', label: '주 1회' }, { value: 'WEEKLY_2_3', label: '주 2~3회' }, { value: 'DAILY', label: '매일 가능' }, { value: 'PROJECT_ONLY', label: '프로젝트 중심만 가능' } ];
const BELBIN_ROLE_OPTIONS = [
    { value: 'PL', label: 'PL - 아이디어 뱅크 (Plant)', description: '창의적이고, 문제를 새로운 아이디어로 해결하는 데 능하다.' },
    { value: 'RI', label: 'RI - 자원탐색자 (Resource Investigator)', description: '외부 자원을 탐색하고, 네트워킹과 기회를 잘 활용한다.' },
    { value: 'CO', label: 'CO - 조정자 (Coordinator)', description: '팀 내 사람들을 조율하고, 자원을 효율적으로 배분할 수 있다.' },
    { value: 'SH', label: 'SH - 추진자 (Shaper)', description: '압박 속에서도 목표를 추진하고 성과를 이끌어내는 데 능하다.' },
    { value: 'ME', label: 'ME - 평가자 (Monitor Evaluator)', description: '논리적이고 객관적인 판단으로 전략적 사고를 지향한다.' },
    { value: 'TW', label: 'TW - 팀 워커 (Teamworker)', description: '협력과 공감을 통해 팀 분위기를 부드럽게 만든다.' },
    { value: 'IMP', label: 'IMP - 실행자 (Implementer)', description: '실행력과 체계적인 방식으로 계획을 현실로 옮긴다.' },
    { value: 'CF', label: 'CF - 완성자 (Completer Finisher)', description: '꼼꼼하고 세심하게 마무리까지 책임진다.' },
    { value: 'SP', label: 'SP - 전문가 (Specialist)', description: '특정 분야의 전문성을 바탕으로 깊이 있는 기여를 한다.' },
];
const TEAM_SIZE_OPTIONS = [ { value: 'SMALL', label: '2~3명' }, { value: 'MEDIUM', label: '4~5명' }, { value: 'LARGE', label: '6명 이상도 가능/기타' } ];
const PROJECT_TOPIC_OPTIONS = [ { value: 'web', label: '웹 서비스' }, { value: 'app', label: '앱 개발' }, { value: 'ai', label: '인공지능' }, { value: 'chatbot', label: '챗봇' }, { value: 'social', label: '소셜 미디어' }, { value: 'community', label: '커뮤니티' }, { value: 'healthcare', label: '헬스케어' }, { value: 'education', label: '교육' }, { value: 'finance', label: '금융' }, { value: 'other', label: '기타' } ];
const AVAILABILITY_PERIOD_OPTIONS = [ { value: 'SHORT', label: '단기: 1달 이내' }, { value: 'MEDIUM', label: '중기: 2~3달' }, { value: 'LONG', label: '장기: 3달 이상/기타' } ];

// --- API Functions ---
const fetchUserInfo = async () => {
  const response = await apiClient.get('/user-info/');
  return response.data;
};

const updateUserInfo = async (data: any) => {
  const response = await apiClient.put('/user-info/', data);
  return response.data;
};

// --- Reusable Components ---
const Section = ({ title, children }: { title: string, children: React.ReactNode }) => (
  <div className="p-6 border rounded-lg shadow-sm bg-white dark:bg-gray-800">
    <h2 className="text-2xl font-bold mb-6">{title}</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">{children}</div>
  </div>
);

const FormField = ({ label, children }: { label: string, children: React.ReactNode }) => (
  <div className="flex flex-col gap-2">
    <Label className="font-semibold">{label}</Label>
    <div>{children}</div>
  </div>
);

// --- Form Component ---
const UserInfoForm = ({ onSaveSuccess, onCancel }: { onSaveSuccess: () => void, onCancel?: () => void }) => {
  const { register, handleSubmit, reset, control } = useForm();
  const { user, refreshUser } = useAuth();

  useEffect(() => {
    if (user) {
      reset({
        ...user,
        available_region: user.available_region || [],
        specialty: user.specialty || [],
        tech_stack: user.tech_stack || [],
        collaboration_tools: user.collaboration_tools || [],
        preferred_project_topics: user.preferred_project_topics || [],
      });
    }
  }, [user, reset]);

  const onSubmit = async (data: any) => {
    try {
      await updateUserInfo(data);
      await refreshUser(); // Refresh user context after update
      alert('정보가 성공적으로 저장되었습니다.');
      onSaveSuccess(); // Notify parent to switch mode
    } catch (error: any) {
      console.error("정보 저장 중 에러:", error.response?.data || error);
      const errorDetails = JSON.stringify(error.response?.data, null, 2);
      alert(`정보 저장에 실패했습니다. 서버 응답:\n${errorDetails}`);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      <h1 className="text-4xl font-bold text-center my-8">내 정보 입력</h1>
      {/* Form sections would be modularized in a real app, but are included here for simplicity */}
      <BasicInfoSection register={register} control={control} />
      <SkillsExperienceSection register={register} control={control} />
      <CollaborationStyleSection register={register} control={control} />
      <ProjectPreferencesSection register={register} control={control} />

      <div className="flex justify-center gap-4 mt-10">
        {onCancel && <Button type="button" variant="outline" size="lg" onClick={onCancel}>취소</Button>}
        <Button type="submit" size="lg">정보 저장하기</Button>
      </div>
    </form>
  );
};

// --- Section Components for the Form ---
const BasicInfoSection = ({ register, control }: { register: any, control: any }) => (
    <Section title="기본 정보 입력">
        <FormField label="이름 (필수)"><Input {...register('name', { required: true })} placeholder="이름을 입력하세요" /></FormField>
        <FormField label="활동 가능 지역 (필수)">
            <Controller name="available_region" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">{REGION_OPTIONS.map(opt => (<label key={opt.value} className="flex items-center gap-2"><input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => field.onChange(e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value))} /> {opt.label}</label>))}</div>
            )} />
        </FormField>
        <FormField label="깃허브 주소"><Input {...register('github_url')} placeholder="https://github.com/username" /></FormField>
        <FormField label="포트폴리오 주소"><Input {...register('portfolio_url')} placeholder="https://your-portfolio.com" /></FormField>
        <FormField label="간단한 소개 (150자 이내)"><textarea {...register('introduction')} className="w-full p-2 border rounded-md" rows={4} maxLength={150} /></FormField>
    </Section>
);

const SkillsExperienceSection = ({ register, control }: { register: any, control: any }) => (
    <Section title="기술 역량 및 경험">
        <FormField label="전공 또는 주요 학습 분야"><select {...register('major')} className="w-full p-2 border rounded-md">{MAJOR_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></FormField>
        <FormField label="가장 자신 있는 분야 (1~2개)">
            <Controller name="specialty" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">{SPECIALTY_OPTIONS.map(opt => (<label key={opt.value} className="flex items-center gap-2"><input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => field.onChange(e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value))} /> {opt.label}</label>))}</div>
            )} />
        </FormField>
        <FormField label="사용 가능한 기술 스택">
            <Controller name="tech_stack" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">{TECH_STACK_OPTIONS.map(opt => (<label key={opt.value} className="flex items-center gap-2"><input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => field.onChange(e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value))} /> {opt.label}</label>))}</div>
            )} />
        </FormField>
        <FormField label="협업 툴 사용 경험">
            <Controller name="collaboration_tools" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">{COLLAB_TOOL_OPTIONS.map(opt => (<label key={opt.value} className="flex items-center gap-2"><input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => field.onChange(e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value))} /> {opt.label}</label>))}</div>
            )} />
        </FormField>
        <FormField label="사이드 프로젝트 참여 경험 횟수"><select {...register('experience_level')} className="w-full p-2 border rounded-md">{EXPERIENCE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></FormField>
    </Section>
);

const CollaborationStyleSection = ({ register, control }: { register: any, control: any }) => {
    const [selectedBelbin, setSelectedBelbin] = useState('');
    return (
        <Section title="협업 성향 및 방식">
            <FormField label="선호하는 협업 방식"><select {...register('collaboration_style')} className="w-full p-2 border rounded-md">{COLLABORATION_STYLE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></FormField>
            <FormField label="가능한 미팅 빈도 (주 단위)"><select {...register('meeting_frequency')} className="w-full p-2 border rounded-md">{MEETING_FREQUENCY_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></FormField>
            <div className="md:col-span-2"><FormField label="벨빈 팀 역할 유형"><Controller name="belbin_role" control={control} render={({ field }) => (<div className="space-y-2">{BELBIN_ROLE_OPTIONS.map(opt => (<label key={opt.value} className="flex items-start gap-3"><input type="radio" value={opt.value} checked={field.value === opt.value} onChange={e => { field.onChange(e.target.value); setSelectedBelbin(e.target.value); }} /><span>{opt.label}</span></label>))}</div>)} />{BELBIN_ROLE_OPTIONS.find(opt => opt.value === selectedBelbin) && <div className="mt-4 p-3 bg-gray-100 rounded-md"><p className="font-semibold">{BELBIN_ROLE_OPTIONS.find(opt => opt.value === selectedBelbin)!.label}</p><p className="text-sm text-gray-600">{BELBIN_ROLE_OPTIONS.find(opt => opt.value === selectedBelbin)!.description}</p></div>}</FormField></div>
        </Section>
    );
};

const ProjectPreferencesSection = ({ register, control }: { register: any, control: any }) => (
    <Section title="프로젝트 관련 선호도">
        <FormField label="희망하는 팀원 수"><select {...register('preferred_team_size')} className="w-full p-2 border rounded-md">{TEAM_SIZE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></FormField>
        <FormField label="선호하는 프로젝트 주제">
            <Controller name="preferred_project_topics" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">{PROJECT_TOPIC_OPTIONS.map(opt => (<label key={opt.value} className="flex items-center gap-2"><input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => field.onChange(e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value))} /> {opt.label}</label>))}</div>
            )} />
        </FormField>
        <FormField label="참여 가능 기간"><select {...register('availability_period')} className="w-full p-2 border rounded-md">{AVAILABILITY_PERIOD_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}</select></FormField>
    </Section>
);

// --- Main Page Component ---
export function UserInformationPage() {
  const { user } = useAuth();
  const [isEditMode, setIsEditMode] = useState(false);

  // Decide whether to start in edit mode
  useEffect(() => {
    if (user && !user.is_profile_complete) {
      setIsEditMode(true);
    }
  }, [user]);

  if (!user) {
    return <div>로딩 중...</div>; // Or a spinner component
  }

  return (
    <div className="container mx-auto p-4 sm:p-6 lg:p-8">
      {isEditMode ? (
        <UserInfoForm 
          onSaveSuccess={() => setIsEditMode(false)} 
          onCancel={() => user.is_profile_complete ? setIsEditMode(false) : null} // Only show cancel if profile is already complete
        />
      ) : (
        <UserInfoDisplay onEdit={() => setIsEditMode(true)} />
      )}
    </div>
  );
}