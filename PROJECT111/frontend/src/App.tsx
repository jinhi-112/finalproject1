import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import RegisterPage from "./features/auth/pages/RegisterPage";
import LoginPage from "./features/auth/pages/LoginPage";
import { UserInformationPage } from "./features/user-information/pages/UserInformationPage";
import { Header } from "./widgets/Header";
import { Body } from "./widgets/Body";
import { AuthGuard } from "./features/auth/guards/AuthGuard";
import { useEffect, useState } from "react";
import { ProjectCard } from "./features/projects/components/ProjectCard";
import { ProjectDetailPage } from "./features/projects/pages/ProjectDetailPage";
import { ProjectRegisterPage } from "./features/projects/pages/ProjectRegisterPage";
import { Button } from "./shared/components/Button";
import { AuthProvider, useAuth } from "./shared/contexts/AuthContext";

// API로부터 받아올 프로젝트 데이터의 타입을 정의합니다.
interface Project {
  project_id: number;
  title: string;
  description: string;
  tech_stack: string;
  // 필요에 따라 다른 필드들도 추가할 수 있습니다。
}

const ProfileCompletionBanner = () => {
  const { user } = useAuth();
  const [isProfileComplete, setIsProfileComplete] = useState(true);

  useEffect(() => {
    const checkProfile = async () => {
      if (user) {
        try {
          const response = await fetch('/api/user-info/');
          const data = await response.json();
          setIsProfileComplete(data.is_profile_complete);
        } catch (error) {
          console.error("Failed to check profile completion status", error);
        }
      }
    };
    checkProfile();
  }, [user]);

  if (user && !isProfileComplete) {
    return (
      <div className="bg-yellow-200 text-center p-2">
        <p>매칭을 위해선 더 많은 정보를 입력해주셔야 합니다. <Link to="/user-info" className="underline font-bold">정보 입력하기</Link></p>
      </div>
    );
  }

  return null;
};

// 메인 페이지 컴포넌트
function MainPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [error, setError] = useState<string | null>(null);

  // useEffect(() => {
  //   // 백엔드 API를 호출하는 함수
  //   const fetchProjects = async () => {
  //     try {
  //       // Django 서버의 API 엔드포인트로 요청을 보냅니다.
  //       const response = await fetch('http://127.0.0.1:8000/api/projects/');
        
  //       if (!response.ok) {
  //         // 응답이 성공적이지 않은 경우 에러를 발생시킵니다.
  //         throw new Error(`HTTP error! status: ${response.status}`);
  //       }
        
  //       const data = await response.json();
        
  //       // `views.py`에서 정의한 커스텀 응답 형식에 맞춰 데이터를 추출합니다.
  //       setProjects(data); 
        
  //     } catch (e) {
  //       if (e instanceof Error) {
  //         console.error("API 호출 중 에러 발생:", e.message);
  //         setError(`데이터를 불러오는 데 실패했습니다: ${e.message}`);
  //       }
  //     }
  //   };

  //   fetchProjects();
  // }, []); // 빈 배열을 전달하여 컴포넌트가 처음 마운트될 때 한 번만 실행되도록 합니다.

  if (error) {
    return <div>{error}</div>;
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
          <p>프로젝트가 없습니다. 백엔드 서버를 실행하고 데이터를 추가해보세요.</p>
        )}
      </section>
    </div>
  );
}


function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
      <div className="relative flex flex-col h-screen">
        <Header />
        <ProfileCompletionBanner /> {/* 배너 추가 */}
        <Body>
          <Routes>
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/user-info" element={
              <AuthGuard>
                <UserInformationPage />
              </AuthGuard>
            } />
            <Route path="/" element={<MainPage />} />
            <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
            <Route path="/register-project" element={
              <AuthGuard>
                <ProjectRegisterPage />
              </AuthGuard>
            } />
          </Routes>
        </Body>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
