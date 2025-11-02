import { Button } from "@/shared/components/Button";
import { useAuth } from "@/shared/contexts/AuthContext";

interface DisplayFieldProps {
  label: string;
  value: string | string[] | undefined;
}

const DisplayField = ({ label, value }: DisplayFieldProps) => {
  const displayValue = Array.isArray(value) ? value.join(', ') : value;
  return (
    <div className="grid grid-cols-3 gap-4 py-2 border-b border-slate-100">
      <dt className="text-sm font-medium text-slate-500">{label}</dt>
      <dd className="text-sm text-slate-900 col-span-2">{displayValue || '-'}</dd>
    </div>
  );
};

interface UserInfoDisplayProps {
  onEdit: () => void;
}

export function UserInfoDisplay({ onEdit }: UserInfoDisplayProps) {
  const { user } = useAuth();

  if (!user) {
    return <div>사용자 정보를 불러오는 중입니다...</div>;
  }

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">내 프로필</h1>
        <Button onClick={onEdit}>정보 수정하기</Button>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md border border-slate-200">
        <h2 className="text-xl font-semibold mb-6 border-b pb-4">기본 정보</h2>
        <dl className="space-y-2">
          <DisplayField label="이름" value={user.name} />
          <DisplayField label="이메일" value={user.email} />
          <DisplayField label="활동 가능 지역" value={user.available_region} />
          <DisplayField label="GitHub 주소" value={user.github_url} />
          <DisplayField label="포트폴리오 주소" value={user.portfolio_url} />
          <DisplayField label="자기소개" value={user.introduction} />
        </dl>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md border border-slate-200">
        <h2 className="text-xl font-semibold mb-6 border-b pb-4">기술 및 경험</h2>
        <dl className="space-y-2">
          <DisplayField label="전공" value={user.major} />
          <DisplayField label="전문 분야" value={user.specialty} />
          <DisplayField label="기술 스택" value={user.tech_stack} />
          <DisplayField label="협업 툴" value={user.collaboration_tools} />
          <DisplayField label="프로젝트 경험" value={user.experience_level} />
        </dl>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md border border-slate-200">
        <h2 className="text-xl font-semibold mb-6 border-b pb-4">협업 성향</h2>
        <dl className="space-y-2">
          <DisplayField label="협업 스타일" value={user.collaboration_style} />
          <DisplayField label="미팅 빈도" value={user.meeting_frequency} />
          <DisplayField label="팀 역할 (벨빈)" value={user.belbin_role} />
        </dl>
      </div>

      <div className="bg-white p-8 rounded-lg shadow-md border border-slate-200">
        <h2 className="text-xl font-semibold mb-6 border-b pb-4">선호 프로젝트</h2>
        <dl className="space-y-2">
          <DisplayField label="선호 팀 규모" value={user.preferred_team_size} />
          <DisplayField label="선호 주제" value={user.preferred_project_topics} />
          <DisplayField label="참여 가능 기간" value={user.availability_period} />
        </dl>
      </div>
    </div>
  );
}
