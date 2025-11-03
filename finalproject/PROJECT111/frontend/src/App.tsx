import { BrowserRouter, Routes, Route } from "react-router-dom";
import RegisterPage from "./features/auth/pages/RegisterPage";
import LoginPage from "./features/auth/pages/LoginPage";
import { UserInformationPage } from "./features/user-information/pages/UserInformationPage";
import { Header } from "./widgets/Header";
import { Body } from "./widgets/Body";
import { AuthGuard } from "./features/auth/guards/AuthGuard";
import { ProjectDetailPage } from "./features/projects/pages/ProjectDetailPage";
import { ProjectRegisterPage } from "./features/projects/pages/ProjectRegisterPage";
import { FindProjectsPage } from "./features/projects/pages/FindProjectsPage";
import { AuthProvider } from "./shared/contexts/AuthContext";
import { MainPage } from "./pages/MainPage";
import { RecommendedProjectsPage } from "./features/ai-recommendations/pages/RecommendedProjectsPage";
import ApplicationFormPage from "./pages/ApplicationFormPage";
import ProjectManagePage from "./pages/ProjectManagePage";
import ApplicantManagePage from "./pages/ApplicantManagePage";
import ProjectEditPage from "./pages/ProjectEditPage";


function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="relative flex flex-col h-screen">
          <Header />
          
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
              <Route path="/find-projects" element={<FindProjectsPage />} />
              <Route path="/recommended-projects" element={
                <AuthGuard>
                  <RecommendedProjectsPage />
                </AuthGuard>
              } />
              <Route path="/apply/:projectId" element={
                <AuthGuard>
                  <ApplicationFormPage />
                </AuthGuard>
              } />
              <Route path="/project-management" element={
                <AuthGuard>
                  <ProjectManagePage />
                </AuthGuard>
              } />
              <Route path="/applicants/:projectId" element={
                <AuthGuard>
                  <ApplicantManagePage />
                </AuthGuard>
              } />
              <Route path="/edit-project/:projectId" element={
                <AuthGuard>
                  <ProjectEditPage />
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