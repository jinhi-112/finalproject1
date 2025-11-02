import { BrowserRouter, Routes, Route } from "react-router-dom";
import RegisterPage from "./features/auth/pages/RegisterPage";
import LoginPage from "./features/auth/pages/LoginPage";
import { UserInformationPage } from "./features/user-information/pages/UserInformationPage";
import Header from "./widgets/Header";
import { Body } from "./widgets/Body";
import { AuthGuard } from "./features/auth/guards/AuthGuard";
import { ProjectDetailPage } from "./features/projects/pages/ProjectDetailPage";
import { ProjectRegisterPage } from "./features/projects/pages/ProjectRegisterPage";
import { FindProjectsPage } from "./features/projects/pages/FindProjectsPage";
import { AuthProvider } from "./shared/contexts/AuthContext";
import { MainPage } from "./pages/MainPage";
import ProjectManagePage from "./pages/ProjectManagePage";
import ApplicantManagePage from "./pages/ApplicantManagePage";

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="relative flex flex-col min-h-screen">
          {/* 헤더 항상 상단 */}
          <Header className="fixed top-0 left-0 w-full z-50" />

          {/* 헤더 높이만큼 여백 */}
          <Body className="pt-[80px] flex-1">
            <Routes>
              {/* 회원가입 & 로그인 */}
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/login" element={<LoginPage />} />

              {/* 유저 정보 */}
              <Route
                path="/user-info"
                element={
                  <AuthGuard>
                    <UserInformationPage />
                  </AuthGuard>
                }
              />

              {/* 메인 */}
              <Route path="/" element={<MainPage />} />

              {/* 프로젝트 */}
              <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
              <Route
                path="/register-project"
                element={
                  <AuthGuard>
                    <ProjectRegisterPage />
                  </AuthGuard>
                }
              />
              <Route path="/find-projects" element={<FindProjectsPage />} />

              {/* 관리 */}
              <Route path="/project/manage" element={<ProjectManagePage />} />
              <Route path="/applicants/:projectId" element={<ApplicantManagePage />} />
            </Routes>
          </Body>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
