import { useParams, Link } from "react-router-dom";
import { useState, useEffect } from "react";
import apiClient from "../../../api";
import { Button } from "../../../shared/components/Button";
import { useAuth } from "../../../shared/contexts/AuthContext";

// --- Interfaces ---
interface Project {
  project_id: number;
  creator: {
    user_id: number;
    name: string;
    email: string;
    specialty?: string;
    introduction?: string;
  };
  title: string;
  description: string;
  goal: string;
  tech_stack: string;
  recruitment_count: number;
  start_date: string;
  end_date: string;
  application_deadline: string | null;
  applicant_count: number;
  user_matching_rate: number | null;
  user_match_explanation?: string;
  user_match_scores?: {
    tech: number;
    personality: number;
    experience: number;
  };
  is_open: boolean;
  created_at: string;
}

// --- Helper & Sub-components ---
const InfoItem = ({ icon, text }: { icon: React.ReactNode, text: string }) => (
  <div className="flex items-center gap-2 text-slate-600">
    {icon}
    <span className="text-sm font-medium">{text}</span>
  </div>
);

const ProgressBar = ({ label, score, maxScore }: { label: string, score: number, maxScore: number }) => (
  <div>
    <div className="flex justify-between mb-1">
      <span className="text-sm font-medium text-slate-600">{label}</span>
      <span className="text-sm font-medium text-slate-500">{score}/{maxScore}</span>
    </div>
    <div className="w-full bg-slate-200 rounded-full h-2">
      <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${(score / maxScore) * 100}%` }}></div>
    </div>
  </div>
);

// --- Main Page Component ---
export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user, isAuthenticated } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');

  const fetchProject = async () => {
    if (!projectId) return;
    try {
      const response = await apiClient.get<Project>(`/projects/${projectId}/`);
      setProject(response.data);
      return response.data;
    } catch (err) {
      setError("프로젝트 정보를 불러오는 데 실패했습니다.");
      console.error("프로젝트 상세 정보 불러오기 실패:", err);
      return null;
    }
  };

  useEffect(() => {
    const initialFetch = async () => {
      setLoading(true);
      const fetchedProject = await fetchProject();
      setLoading(false);

      if (fetchedProject && isAuthenticated && !fetchedProject.user_match_scores) {
        console.log("Triggering match calculation...");
        apiClient.get(`/match/project/${projectId}/`)
          .then(() => fetchProject()) // Re-fetch after calculation
          .catch(matchErr => console.error("Could not generate match score:", matchErr.response?.data || matchErr.message));
      }
    };
    initialFetch();
  }, [projectId, isAuthenticated]);

  const handleApply = async () => {
    if (!isAuthenticated) {
      alert("로그인이 필요합니다.");
      return;
    }
    try {
      const response = await apiClient.post(`/projects/${projectId}/apply/`);
      alert(response.data.message);
      fetchProject(); // Re-fetch to update applicant count
    } catch (error: any) {
      alert(error.response?.data?.message || "지원 처리 중 오류가 발생했습니다.");
      console.error("Apply error:", error);
    }
  };

  if (loading) return <div className="text-center p-10">프로젝트 정보를 불러오는 중...</div>;
  if (error) return <div className="text-center p-10 text-red-500">{error}</div>;
  if (!project) return <div className="text-center p-10">프로젝트를 찾을 수 없습니다.</div>;

  const techTags = project.tech_stack?.split(',').map(tag => tag.trim()).filter(tag => tag) || [];
  const duration = project.start_date && project.end_date 
    ? `${Math.round((new Date(project.end_date).getTime() - new Date(project.start_date).getTime()) / (1000 * 60 * 60 * 24 * 30))}개월`
    : "미정";

  const leaderRole = project.creator.specialty?.split(',')[0] || '미지정';
  const leaderBio = project.creator.introduction || '자기소개가 없습니다.';
  const leaderReviews = project.creator.review_count || 0;

  return (
    <div className="bg-slate-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-7xl mx-auto">
        <Link to="/find-projects" className="inline-flex items-center gap-2 text-sm font-medium text-slate-600 hover:text-slate-900 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          추천 목록으로 돌아가기
        </Link>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Header Card */}
            <div className="bg-white p-6 rounded-lg border border-slate-200">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <span className="bg-slate-100 text-slate-700 text-xs font-semibold px-2.5 py-1 rounded-md">웹 애플리케이션</span>
                    <span className="bg-green-100 text-green-700 text-xs font-semibold px-2.5 py-1 rounded-md">모집 중</span>
                  </div>
                  <h1 className="text-3xl font-bold text-slate-900 mb-2">{project.title}</h1>
                  <p className="text-slate-500">{project.goal}</p>
                </div>
              </div>
              <div className="flex flex-wrap gap-x-6 gap-y-3 mt-4 pt-4 border-t border-slate-100">
                <InfoItem icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>} text={duration} />
                <InfoItem icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.653-.084-1.28-.24-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.653.084-1.28.24-1.857m10 0a5 5 0 00-9.52 0M12 6a3 3 0 110-6 3 3 0 010 6z" /></svg>} text={`${project.recruitment_count}명`} />
                <InfoItem icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>} text={project.start_date ? `시작: ${new Date(project.start_date).toLocaleDateString()}` : '시작일 미정'} />
                <InfoItem icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>} text="원격/하이브리드" />
              </div>
            </div>

            {/* Tabs & Content */}
            <div className="bg-white rounded-lg border border-slate-200">
              <div className="border-b border-slate-200">
                <nav className="-mb-px flex gap-6 px-6">
                  <button onClick={() => setActiveTab('overview')} className={`shrink-0 border-b-2 px-1 pb-4 text-sm font-medium ${activeTab === 'overview' ? 'border-sky-500 text-sky-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}`}>개요</button>
                  <button onClick={() => setActiveTab('requirements')} className={`shrink-0 border-b-2 px-1 pb-4 text-sm font-medium ${activeTab === 'requirements' ? 'border-sky-500 text-sky-600' : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'}`}>요구사항</button>
                </nav>
              </div>
              <div className="p-6">
                {activeTab === 'overview' && (
                  <div className="prose max-w-none text-slate-600">
                    <h4>프로젝트 상세 설명</h4>
                    <p>{project.description}</p>
                    <h4>주요 기능</h4>
                    <ul><li>AI 기반 여행지 추천 시스템</li><li>실시간 예산 관리 및 최적화</li><li>소셜 기능 (여행 계획 공유)</li></ul>
                    <h4>기대 효과</h4>
                    <p>사용자들이 더 쉽고 효율적으로 여행을 계획할 수 있도록 도와주며, AI 기술을 활용한 개인화 서비스의 경험을 쌓을 수 있습니다.</p>
                  </div>
                )}
                {activeTab === 'requirements' && (
                  <div>
                    <h4 className="font-bold mb-2">필요 기술 스택</h4>
                    <div className="flex flex-wrap gap-2">
                      {techTags.map(tag => <span key={tag} className="bg-slate-100 text-slate-600 text-xs font-medium px-2.5 py-1 rounded-md">{tag}</span>)}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="lg:col-span-1 space-y-6">
            {/* AI Matching Card */}
            <div className="bg-white p-6 rounded-lg border border-slate-200">
              <h3 className="text-lg font-semibold mb-4">AI 매칭 분석</h3>
              <div className="text-center mb-4">
                <p className="text-5xl font-bold text-blue-600">{project.user_matching_rate?.toFixed(0) || 'N/A'}%</p>
                <p className="text-sm font-medium text-slate-500">매칭률</p>
              </div>
              <div className="space-y-4">
                {project.user_match_scores ? (
                  <>
                    <ProgressBar label="기술 매칭" score={project.user_match_scores.tech} maxScore={30} />
                    <ProgressBar label="성향 적합도" score={project.user_match_scores.personality} maxScore={25} />
                    <ProgressBar label="경험 수준" score={project.user_match_scores.experience} maxScore={20} />
                  </>
                ) : (
                  <p className="text-sm text-center text-slate-500 py-4">세부 매칭 점수를 분석 중입니다...</p>
                )}
              </div>
            </div>
            {/* Apply Card */}
            <div className="bg-white p-6 rounded-lg border border-slate-200">
              <Button onClick={handleApply} className="w-full text-lg">지원하기</Button>
              <div className="text-center text-sm text-slate-500 mt-3">
                <p>지원 마감: {project.application_deadline ? new Date(project.application_deadline).toLocaleDateString() : '미정'}</p>
                <p>현재 {project.applicant_count}명 지원</p>
              </div>
            </div>
            {/* Leader Card */}
            <div className="bg-white p-6 rounded-lg border border-slate-200">
              <h3 className="text-lg font-semibold mb-4">프로젝트 리더</h3>
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 bg-slate-200 rounded-full"></div>
                <div>
                  <p className="font-bold text-slate-800">{project.creator.name}</p>
                  <p className="text-sm text-slate-500">{leaderRole}</p>
                </div>
              </div>
              <p className="text-sm text-slate-600 mt-4">{leaderBio}</p>
              
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}