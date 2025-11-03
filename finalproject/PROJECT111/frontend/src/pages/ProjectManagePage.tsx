import React, { useEffect, useState } from "react";
import { getMyProjects, getRecommendedTeammates, deleteProject } from "../api"; // Import deleteProject
import { useAuth } from "../shared/contexts/AuthContext";
import { Eye, Settings, Trash2 } from "lucide-react"; // Import Trash2 icon
import { useNavigate } from "react-router-dom";
import { RecommendTeammatesModal } from "../features/projects/components/RecommendTeammatesModal";

export default function ProjectManagePage() {
  const { isAuthenticated } = useAuth();
  const [summary, setSummary] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [activeTab, setActiveTab] = useState("active");
  const navigate = useNavigate();

  // State for recommendation modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoadingRecs, setIsLoadingRecs] = useState(false);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<any>(null);

  useEffect(() => {
    if (!isAuthenticated) return;

    const fetchProjects = async () => {
      try {
        const res = await getMyProjects();
        setSummary(res.summary);
        setProjects(res.projects);
      } catch (err) {
        console.error("프로젝트 목록을 불러오는 중 오류 발생:", err);
      }
    };

    fetchProjects();
  }, [isAuthenticated]);

  const handleShowRecommendations = async (project: any) => {
    setSelectedProject(project);
    setIsModalOpen(true);
    setIsLoadingRecs(true);
    try {
      const recs = await getRecommendedTeammates(project.project_id);
      setRecommendations(recs);
    } catch (error) {
      console.error("추천 팀원 목록을 불러오는 중 오류 발생:", error);
      setRecommendations([]);
    } finally {
      setIsLoadingRecs(false);
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedProject(null);
    setRecommendations([]);
  };

  const handleDeleteProject = async (projectId: number) => {
    if (window.confirm('정말로 이 프로젝트를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      try {
        await deleteProject(projectId);
        setProjects(prevProjects => prevProjects.filter(p => p.project_id !== projectId));
      } catch (error) {
        console.error("Failed to delete project:", error);
        alert("프로젝트 삭제에 실패했습니다.");
      }
    }
  };

  const safeProjects = projects || [];
  const filtered = safeProjects.filter((p) =>
    activeTab === "active"
      ? p.status === "active"
      : activeTab === "completed"
      ? p.status === "completed"
      : p.status === "draft"
  );

  return (
    <>
      <div className="p-8 bg-gray-50 min-h-screen">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">프로젝트 관리</h1>
          <p className="text-gray-500 mt-1">
            등록한 프로젝트를 관리하고 팀원을 모집하세요
          </p>
        </div>

        {!isAuthenticated ? (
          <div className="text-gray-500">로그인 후 이용할 수 있습니다.</div>
        ) : (
          <>
            {summary && (
              <div className="grid grid-cols-2 gap-6 mb-10">
                <SummaryCard
                  label="활성 프로젝트"
                  value={summary.active_projects}
                  color="text-green-600"
                  icon="🚀"
                />
                <SummaryCard
                  label="총 지원자"
                  value={summary.total_applicants}
                  color="text-blue-600"
                  icon="👥"
                />
              </div>
            )}

            <div className="flex gap-6 mb-8 border-b border-gray-200">
              {["active", "completed", "draft"].map((tab) => (
                <TabButton
                  key={tab}
                  label={
                    tab === "active"
                      ? `활성 프로젝트 (${safeProjects.filter(p => p.status === "active").length})`
                      : tab === "completed"
                      ? `완료된 프로젝트 (${safeProjects.filter(p => p.status === "completed").length})`
                      : `임시 저장 (${safeProjects.filter(p => p.status === "draft").length})`
                  }
                  active={activeTab === tab}
                  onClick={() => setActiveTab(tab)}
                />
              ))}
            </div>

            {filtered.length > 0 ? (
              filtered.map((p) => (
                <div
                  key={p.project_id}
                  className="bg-white shadow-sm border border-gray-100 rounded-2xl p-6 mb-6 hover:shadow-md transition"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <div className="flex gap-2 mb-1">
                        <span className="bg-green-100 text-green-600 text-xs px-2 py-1 rounded-md">
                          {p.status === "active" ? "모집중" : "완료"}
                        </span>
                      </div>
                      <h2 className="text-xl font-semibold text-gray-900">{p.title}</h2>
                      <p className="text-gray-500 text-sm mt-1">{p.description}</p>
                    </div>
                    <button 
                      onClick={() => handleShowRecommendations(p)}
                      className="bg-black text-white text-sm px-4 py-2 rounded-md hover:bg-gray-800"
                    >
                      팀원 추천 보기
                    </button>
                  </div>

                  <div className="mb-4">
                    <p className="text-gray-500 text-sm mb-2">팀 구성 현황</p>
                    <div className="w-full bg-gray-100 rounded-full h-2">
                      <div
                        className="bg-black h-2 rounded-full"
                        style={{ width: `${((p.current_members ?? 2) / (p.recruitment_count ?? 4)) * 100}%` }}
                      ></div>
                    </div>
                    <p className="text-right text-gray-400 text-xs mt-1">
                      {(p.current_members ?? 2)}/{p.recruitment_count ?? 4}명
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-4">
                    {(() => {
                      if (!p.tech_stack) return <span className="text-gray-400 text-sm">기술 스택 정보 없음</span>;
                      const stackArray = typeof p.tech_stack === "string" ? p.tech_stack.split(",") : Array.isArray(p.tech_stack) ? p.tech_stack : [];
                      return stackArray.map((tech: string, i: number) => (
                        <span key={i} className="border border-gray-300 text-gray-700 text-xs px-3 py-1 rounded-full">{tech.trim()}</span>
                      ));
                    })()}
                  </div>

                  <div className="flex justify-between items-center text-sm text-gray-600">
                    <div className="flex gap-6">
                      <p><span className="text-blue-600 font-medium">{p.applicants_count ?? 0}</span> 지원자</p>
                      <p><span className="text-green-600 font-medium">{p.ai_recommended_count ?? 0}</span> AI 추천</p>
                      <p><span className="text-orange-500 font-medium">{p.views ?? 0}</span> 조회수</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <button 
                        onClick={() => navigate(`/applicants/${p.project_id}`)}
                        className="bg-black text-white text-sm px-4 py-2 rounded-md"
                      >
                        지원자 관리
                      </button>
                      <Settings size={18} className="text-gray-400 hover:text-black cursor-pointer" onClick={() => navigate(`/edit-project/${p.project_id}`)} />
                      <Trash2
                        onClick={() => handleDeleteProject(p.project_id)}
                        size={18}
                        className="text-gray-400 hover:text-red-600 cursor-pointer"
                      />
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-gray-500">등록된 프로젝트가 없습니다.</div>
            )}
          </>
        )}
      </div>
      
      <RecommendTeammatesModal
        isOpen={isModalOpen}
        onClose={handleCloseModal}
        recommendations={recommendations}
        isLoading={isLoadingRecs}
        projectName={selectedProject?.title || ''}
        projectId={selectedProject?.project_id || null}
      />
    </>
  );
}

function SummaryCard({ label, value, color, icon }: any) {
  return (
    <div className="bg-white shadow-sm border border-gray-100 rounded-2xl p-6 text-center">
      <div className="flex justify-center mb-2 text-2xl">{icon}</div>
      <p className="text-gray-500 text-sm">{label}</p>
      <p className={`text-2xl font-bold mt-1 ${color}`}>{value}</p>
    </div>
  );
}

function TabButton({ label, active, onClick }: any) {
  return (
    <button
      onClick={onClick}
      className={`pb-2 transition-all border-b-2 text-sm ${
        active
          ? "border-black text-black font-semibold"
          : "border-transparent text-gray-400 hover:text-black"
      }`}
    >
      {label}
    </button>
  );
}
