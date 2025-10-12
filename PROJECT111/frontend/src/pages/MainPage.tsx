import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ProjectCard } from "../features/projects/components/ProjectCard";
import { Button } from "../shared/components/Button";
import apiClient from '../api';

// API로부터 받아올 프로젝트 데이터의 타입을 정의합니다.
interface Project {
  project_id: number;
  title: string;
  description: string;
  tech_stack: string;
  // 필요에 따라 다른 필드들도 추가할 수 있습니다.
}

// ----------------------------------------------------------------
// ⭐️ 메인 페이지 컴포넌트
// ----------------------------------------------------------------
export function MainPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true); // 로딩 상태 추가

  useEffect(() => {
    // 백엔드 API를 호출하는 함수
    const fetchProjects = async () => {
      try {
        setLoading(true); // 데이터 요청 시작 시 로딩 상태를 true로 설정
        const response = await apiClient.get('/projects/');
        
        // Django REST Framework의 페이지네이션 응답을 고려하여
        // 실제 데이터는 'results' 키에 있을 수 있습니다.
        // 'results'가 없으면 data 자체를 사용합니다.
        setProjects(response.data.results || response.data); 
        
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : "알 수 없는 에러가 발생했습니다.";
        console.error("API 호출 중 에러 발생:", errorMessage);
        setError(`데이터를 불러오는 데 실패했습니다: ${errorMessage}`);
      } finally {
        setLoading(false); // 요청 완료 시 (성공/실패 모두) 로딩 상태를 false로 설정
      }
    };

    fetchProjects();
  }, []); // 컴포넌트가 처음 마운트될 때 한 번만 실행되도록 합니다.

  if (loading) {
    return <div className="text-center p-10">프로젝트 목록을 불러오는 중...</div>;
  }

  if (error) {
    return <div className="text-center p-10 text-red-500">{error}</div>;
  }

  return (
    <div className="space-y-12">
      {/* Hero Section */}
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

      {/* Search and Filter Bar */}
      <section>
        <div className="flex justify-center items-center mb-6 gap-4">
          <div className="relative w-full">
            <input type="search" placeholder="프로젝트 검색..." className="w-full p-3 pl-10 border rounded-md" />
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <svg className="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            </div>
          </div>
          <Button variant="outline">▼ 필터</Button>
        </div>
      </section>

      {/* Projects Grid */}
      <section>
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
