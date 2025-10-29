import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { ProjectCard } from "../features/projects/components/ProjectCard";
import { getMatchedProjects } from '../api'; // Import getMatchedProjects
import { useAuth } from "../shared/contexts/AuthContext"; // Import useAuth
import { Button } from "../shared/components/Button";
import apiClient from "@/api";

// Define Project interface locally
interface Project {
  project_id: number;
  creator: { user_id: number; name: string; email: string };
  title: string;
  description: string;
  goal: string;
  tech_stack: string;
  recruitment_count: number;
  start_date: string;
  end_date: string;
  matching_rate: number | null; // From Projects model
  user_matching_rate: number | null; // From MatchScores
  user_match_explanation?: string; // From MatchScores, optional for list view
  is_open: boolean;
  created_at: string;
}

const ProfileCompletionBanner = () => {
  const { user } = useAuth();

  // Show banner only if user is logged in but profile is not complete
  if (user && !user.is_profile_complete) {
    return (
      <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4 rounded-md mb-8 flex items-center justify-between">
        <p className="font-medium">매칭을 위해선 추가 정보를 입력해주세요.</p>
        <Link to="/user-info">
          <Button variant="outline" size="sm">정보 입력하러 가기</Button>
        </Link>
      </div>
    );
  }

  return null;
};

// ----------------------------------------------------------------
// ⭐️ 메인 페이지 컴포넌트
// ----------------------------------------------------------------
export function MainPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true); // 로딩 상태 추가
  const { isAuthenticated } = useAuth(); // Get isAuthenticated from AuthContext
  const location = useLocation(); // Add useLocation hook

  useEffect(() => {
    console.log("MainPage useEffect triggered by location or auth change");
    // 백엔드 API를 호출하는 함수
    const fetchProjects = async () => {
      try {
        setLoading(true); // 데이터 요청 시작 시 로딩 상태를 true로 설정
        // Always fetch generic projects for the main page for now
        const response = await apiClient.get<{
          count: number;
          next: string | null;
          previous: string | null;
          results: Project[];
        }>(`/projects/search/?ordering=-created_at`); // Use the search endpoint
        const fetchedProjects = response.data.results || [];
        
        setProjects(fetchedProjects); 
        console.log("MainPage: Projects state set to", fetchedProjects);
        
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : "알 수 없는 에러가 발생했습니다.";
        console.error("API 호출 중 에러 발생:", errorMessage);
        setError(`데이터를 불러오는 데 실패했습니다: ${errorMessage}`);
      } finally {
        setLoading(false); // 요청 완료 시 (성공/실패 모두) 로딩 상태를 false로 설정
      }
    };

    fetchProjects();
  }, [isAuthenticated, location]); // Re-fetch when location changes

  return (
    <div className="space-y-12">
      <section className="text-center py-16">
        <h1 className="text-5xl font-bold mb-4">AI 기반 사이드 프로젝트 매칭</h1>
        <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">당신의 기술과 성향에 맞는 완벽한 사이드 프로젝트 팀을 AI가 찾아드립니다</p>
        <div className="flex justify-center gap-4">
          <Button size="lg">시작하기 →</Button>
          <Link to="/register-project">
            <Button size="lg" variant="outline">프로젝트 등록하기</Button>
          </Link>
        </div>
      </section>

      <section>
        <h2 className="text-3xl font-bold text-center mb-8">
          {isAuthenticated ? "나에게 맞는 프로젝트" : "최신 프로젝트"}
        </h2>
        <ProfileCompletionBanner />
        {projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map(project => (
              <ProjectCard key={project.project_id} project={project} />
            ))}
          </div>
        ) : (
          <p className="text-center text-gray-500">표시할 프로젝트가 없습니다.</p>
        )}
      </section>
    </div>
  );
}
