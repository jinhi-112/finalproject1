import React, { useEffect, useState } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Button } from '../../../shared/components/Button';
import { Input } from '../../../shared/components/Input';
import { Label } from '../../../shared/components/Label';
import { useAuth } from '../../../shared/contexts/AuthContext';
import axios from 'axios';

function getCookie(name: string) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// --- 데이터 상수 --- //
const REGION_OPTIONS = [{ value: 'SEOUL', label: '수도권' }, { value: 'CHUNGCHEONG', label: '충청권' }, { value: 'YEONGNAM', label: '영남권' }, { value: 'HONAM', label: '호남권' }, { value: 'ETC', label: '기타' }];
const MAJOR_OPTIONS = [{ value: 'CS', label: '컴퓨터공학' }, { value: 'SECURITY', label: '정보보호' }, { value: 'DESIGN', label: '디자인' }, { value: 'BUSINESS', label: '경영/기타' }, { value: 'NON_CS', label: '비전공자' }];
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

// --- API 통신 함수 --- //
const fetchUserInfo = async () => {
  const response = await axios.get('http://127.0.0.1:8000/api/user-info/');
  return response.data;
};

const updateUserInfo = async (data: any) => {
  const csrftoken = getCookie('csrftoken');
  const response = await axios.put('http://127.0.0.1:8000/api/user-info/', data, {
    headers: {
      'X-CSRFToken': csrftoken || '',
    },
  });
  return response.data;
};

// --- 재사용 컴포넌트 --- //
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

// --- 섹션별 컴포넌트 --- //
const BasicInfoSection = ({ register, control }: { register: any, control: any }) => (
    <Section title="기본 정보 입력">
        <FormField label="활동 가능 지역 (필수)">
            <Controller name="available_region" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">
                    {REGION_OPTIONS.map(opt => (
                        <label key={opt.value} className="flex items-center gap-2">
                            <input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => {
                                const newValues = e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value);
                                field.onChange(newValues);
                            }} /> {opt.label}
                        </label>
                    ))}
                </div>
            )} />
        </FormField>
        <FormField label="깃허브 주소"><Input {...register('github_url')} placeholder="https://github.com/username" /></FormField>
        <FormField label="포트폴리오 주소"><Input {...register('portfolio_url')} placeholder="https://your-portfolio.com" /></FormField>
        <FormField label="간단한 소개 (150자 이내)"><textarea {...register('introduction')} className="w-full p-2 border rounded-md" rows={4} maxLength={150} /></FormField>
    </Section>
);

const SkillsExperienceSection = ({ register, control }: { register: any, control: any }) => (
    <Section title="기술 역량 및 경험">
        <FormField label="전공 또는 주요 학습 분야">
            <select {...register('major')} className="w-full p-2 border rounded-md">
                {MAJOR_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
        </FormField>
        <FormField label="가장 자신 있는 분야 (1~2개)">
            <Controller name="specialty" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">
                    {SPECIALTY_OPTIONS.map(opt => (
                        <label key={opt.value} className="flex items-center gap-2">
                            <input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => {
                                const newValues = e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value);
                                field.onChange(newValues);
                            }} /> {opt.label}
                        </label>
                    ))}
                </div>
            )} />
        </FormField>
        <FormField label="사용 가능한 기술 스택">
            <Controller name="tech_stack" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">
                    {TECH_STACK_OPTIONS.map(opt => (
                        <label key={opt.value} className="flex items-center gap-2">
                            <input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => {
                                const newValues = e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value);
                                field.onChange(newValues);
                            }} /> {opt.label}
                        </label>
                    ))}
                </div>
            )} />
        </FormField>
        <FormField label="협업 툴 사용 경험">
            <Controller name="collaboration_tools" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">
                    {COLLAB_TOOL_OPTIONS.map(opt => (
                        <label key={opt.value} className="flex items-center gap-2">
                            <input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => {
                                const newValues = e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value);
                                field.onChange(newValues);
                            }} /> {opt.label}
                        </label>
                    ))}
                </div>
            )} />
        </FormField>
        <FormField label="사이드 프로젝트 참여 경험 횟수">
            <select {...register('experience_level')} className="w-full p-2 border rounded-md">
                {EXPERIENCE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
        </FormField>
    </Section>
);

const CollaborationStyleSection = ({ register, control }: { register: any, control: any }) => {
    const [selectedBelbin, setSelectedBelbin] = useState('');
    const selectedRole = BELBIN_ROLE_OPTIONS.find(opt => opt.value === selectedBelbin);

    return (
        <Section title="협업 성향 및 방식">
            <FormField label="선호하는 협업 방식">
                <select {...register('collaboration_style')} className="w-full p-2 border rounded-md">
                    {COLLABORATION_STYLE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
            </FormField>
            <FormField label="가능한 미팅 빈도 (주 단위)">
                <select {...register('meeting_frequency')} className="w-full p-2 border rounded-md">
                    {MEETING_FREQUENCY_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                </select>
            </FormField>
            <div className="md:col-span-2">
                <FormField label="벨빈 팀 역할 유형">
                    <Controller name="belbin_role" control={control} render={({ field }) => (
                        <div className="space-y-2">
                            {BELBIN_ROLE_OPTIONS.map(opt => (
                                <label key={opt.value} className="flex items-start gap-3">
                                    <input type="radio" value={opt.value} checked={field.value === opt.value} onChange={e => { field.onChange(e.target.value); setSelectedBelbin(e.target.value); }} />
                                    <span>{opt.label}</span>
                                </label>
                            ))}
                        </div>
                    )} />
                    {selectedRole && <div className="mt-4 p-3 bg-gray-100 rounded-md"><p className="font-semibold">{selectedRole.label}</p><p className="text-sm text-gray-600">{selectedRole.description}</p></div>}
                </FormField>
            </div>
        </Section>
    );
};

const ProjectPreferencesSection = ({ register, control }: { register: any, control: any }) => (
    <Section title="프로젝트 관련 선호도">
        <FormField label="희망하는 팀원 수">
            <select {...register('preferred_team_size')} className="w-full p-2 border rounded-md">
                {TEAM_SIZE_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
        </FormField>
        <FormField label="선호하는 프로젝트 주제">
            <Controller name="preferred_project_topics" control={control} render={({ field }) => (
                <div className="flex gap-4 flex-wrap">
                    {PROJECT_TOPIC_OPTIONS.map(opt => (
                        <label key={opt.value} className="flex items-center gap-2">
                            <input type="checkbox" value={opt.value} checked={field.value?.includes(opt.value)} onChange={e => {
                                const newValues = e.target.checked ? [...(field.value || []), e.target.value] : field.value.filter((v: string) => v !== e.target.value);
                                field.onChange(newValues);
                            }} /> {opt.label}
                        </label>
                    ))}
                </div>
            )} />
        </FormField>
        <FormField label="참여 가능 기간">
            <select {...register('availability_period')} className="w-full p-2 border rounded-md">
                {AVAILABILITY_PERIOD_OPTIONS.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
            </select>
        </FormField>
    </Section>
);

// --- 메인 페이지 컴포넌트 --- //
export function UserInformationPage() {
  // ⭐️⭐️⭐️ 수정된 부분 ⭐️⭐️⭐️
  // useForm을 defaultValues와 함께 초기화하여 모든 필드를 제어 컴포넌트로 만듭니다.
  const { register, handleSubmit, reset, control } = useForm({
    defaultValues: {
      available_region: [],
      github_url: '',
      portfolio_url: '',
      introduction: '',
      major: 'CS',
      specialty: [],
      tech_stack: [],
      collaboration_tools: [],
      experience_level: 'NONE',
      collaboration_style: 'OFFLINE',
      meeting_frequency: 'WEEKLY_1',
      belbin_role: '',
      preferred_team_size: 'SMALL',
      preferred_project_topics: [],
      availability_period: 'SHORT'
    }
  });
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      const loadUserInfo = async () => {
        try {
          const userInfo = await fetchUserInfo();
          const transformedInfo = {
              ...userInfo,
              available_region: userInfo.available_region?.split(',') || [],
              specialty: userInfo.specialty?.split(',') || [],
              tech_stack: userInfo.tech_stack?.split(',') || [],
              collaboration_tools: userInfo.collaboration_tools?.split(',') || [],
              preferred_project_topics: userInfo.preferred_project_topics?.split(',') || [],
          };
          reset(transformedInfo);
        } catch (error) {
          console.error(error);
          alert('사용자 정보를 불러오는 데 실패했습니다.');
        }
      };
      loadUserInfo();
    }
  }, [user, reset]);

  const onSubmit = async (data: any) => {
    try {
      // 1. 저장용 데이터 변환 (배열 -> 문자열)
      const transformedData = {
          ...data,
          available_region: data.available_region?.join(','),
          specialty: data.specialty?.join(','),
          tech_stack: data.tech_stack?.join(','),
          collaboration_tools: data.collaboration_tools?.join(','),
          preferred_project_topics: data.preferred_project_topics?.join(','),
      };
      
      // 2. 데이터 저장
      await updateUserInfo(transformedData);
      alert('정보가 성공적으로 저장되었습니다.');

      // 3. 저장된 최신 정보 다시 불러오기
      const latestUserInfo = await fetchUserInfo();

      // 4. 화면 표시용 데이터 변환 (문자열 -> 배열)
      const transformedForDisplay = {
          ...latestUserInfo,
          available_region: latestUserInfo.available_region?.split(',') || [],
          specialty: latestUserInfo.specialty?.split(',') || [],
          tech_stack: latestUserInfo.tech_stack?.split(',') || [],
          collaboration_tools: latestUserInfo.collaboration_tools?.split(',') || [],
          preferred_project_topics: latestUserInfo.preferred_project_topics?.split(',') || [],
      };

      // 5. 폼을 최신 정보로 갱신
      reset(transformedForDisplay);

    } catch (error) {
      console.error(error);
      alert(`정보 저장에 실패했습니다: ${error.message}`);
    }
  };

  return (
    <div className="container mx-auto p-4 space-y-8">
        <h1 className="text-4xl font-bold text-center my-8">내 정보 입력</h1>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
            <BasicInfoSection register={register} control={control} />
            <SkillsExperienceSection register={register} control={control} />
            <CollaborationStyleSection register={register} control={control} />
            <ProjectPreferencesSection register={register} control={control} />

            <div className="flex justify-center mt-10">
                <Button type="submit" size="lg">정보 저장하기</Button>
            </div>
        </form>
    </div>
  );
}