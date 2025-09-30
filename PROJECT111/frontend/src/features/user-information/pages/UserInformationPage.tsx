import React, { useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Button } from '../../../shared/components/Button';
import { Input } from '../../../shared/components/Input';
import { Label } from '../../../shared/components/Label';

// API 통신을 위한 가상 함수 (실제 구현 필요)
const fetchUserInfo = async () => {
  const response = await fetch('/api/user-info/'); // 실제 API 엔드포인트
  if (!response.ok) throw new Error('Failed to fetch user info');
  return response.json();
};

const updateUserInfo = async (data: any) => {
  const response = await fetch('/api/user-info/', { // 실제 API 엔드포인트
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error('Failed to update user info');
  return response.json();
};

// 각 섹션 컴포넌트들
const Section = ({ title, children }: { title: string, children: React.ReactNode }) => (
  <div className="p-6 border rounded-lg shadow-sm bg-white dark:bg-gray-800">
    <h2 className="text-2xl font-bold mb-4">{title}</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">{children}</div>
  </div>
);

const FormField = ({ label, children }: { label: string, children: React.ReactNode }) => (
  <div>
    <Label className="font-semibold">{label}</Label>
    <div className="mt-2">{children}</div>
  </div>
);

// --- 1. 기본 정보 입력 섹션 ---
const BasicInfoSection = ({ register }: { register: any }) => (
  <Section title="기본 정보 입력">
    <FormField label="활동 가능 지역 (필수)">
      {/* 체크박스 구현 예시 */}
      <input type="checkbox" {...register('available_region')} value="SEOUL" /> 수도권
    </FormField>
    <FormField label="깃허브 주소">
      <Input {...register('github_url')} placeholder="https://github.com/username" />
    </FormField>
    <FormField label="포트폴리오 주소">
      <Input {...register('portfolio_url')} placeholder="https://your-portfolio.com" />
    </FormField>
    <FormField label="간단한 소개 (150자 이내)">
      <textarea {...register('introduction')} className="w-full p-2 border rounded-md" rows={4} maxLength={150} />
    </FormField>
  </Section>
);

// --- 2. 기술 역량 및 경험 섹션 ---
const SkillsExperienceSection = ({ register }: { register: any }) => (
    <Section title="기술 역량 및 경험">
        {/* 라디오 버튼, 체크박스 등 다양한 입력 타입 구현 */}
        <FormField label="전공 또는 주요 학습 분야">
            <select {...register('major')} className="w-full p-2 border rounded-md">
                <option value="CS">컴퓨터공학</option>
                <option value="SECURITY">정보보호</option>
                <option value="DESIGN">디자인</option>
                <option value="BUSINESS">경영/기타</option>
                <option value="NON_CS">비전공자</option>
            </select>
        </FormField>
        {/* 다른 필드들도 유사하게 추가... */}
    </Section>
);

// --- 3. 협업 성향 및 방식 섹션 ---
const CollaborationStyleSection = ({ register }: { register: any }) => (
    <Section title="협업 성향 및 방식">
        <FormField label="선호하는 협업 방식">
            <select {...register('collaboration_style')} className="w-full p-2 border rounded-md">
                <option value="OFFLINE">오프라인 중심</option>
                <option value="ONLINE">온라인 중심</option>
                <option value="HYBRID">혼합</option>
            </select>
        </FormField>
        {/* 다른 필드들도 유사하게 추가... */}
    </Section>
);

// --- 4. 프로젝트 관련 선호도 섹션 ---
const ProjectPreferencesSection = ({ register }: { register: any }) => (
    <Section title="프로젝트 관련 선호도">
        <FormField label="희망하는 팀원 수">
            <select {...register('preferred_team_size')} className="w-full p-2 border rounded-md">
                <option value="SMALL">2~3명</option>
                <option value="MEDIUM">4~5명</option>
                <option value="LARGE">6명 이상</option>
            </select>
        </FormField>
        {/* 다른 필드들도 유사하게 추가... */}
    </Section>
);


export function UserInformationPage() {
  const { register, handleSubmit, reset } = useForm();

  useEffect(() => {
    // 페이지 로드 시 사용자 정보 불러오기
    const loadUserInfo = async () => {
      try {
        const userInfo = await fetchUserInfo();
        reset(userInfo); // 폼에 데이터 채우기
      } catch (error) {
        console.error(error);
        alert('사용자 정보를 불러오는 데 실패했습니다.');
      }
    };
    loadUserInfo();
  }, [reset]);

  const onSubmit = async (data: any) => {
    try {
      await updateUserInfo(data);
      alert('정보가 성공적으로 저장되었습니다.');
    } catch (error) {
      console.error(error);
      alert('정보 저장에 실패했습니다.');
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-8">
        <h1 className="text-4xl font-bold text-center">내 정보 입력</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <BasicInfoSection register={register} />
            <SkillsExperienceSection register={register} />
            <CollaborationStyleSection register={register} />
            <ProjectPreferencesSection register={register} />

            <div className="flex justify-center">
                <Button type="submit" size="lg">정보 저장하기</Button>
            </div>
        </form>
    </div>
  );
}