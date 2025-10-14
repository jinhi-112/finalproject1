import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import RegisterPage from "./features/auth/pages/RegisterPage";
import LoginPage from "./features/auth/pages/LoginPage";
import { UserInformationPage } from "./features/user-information/pages/UserInformationPage";
import { Header } from "./widgets/Header";
import { Body } from "./widgets/Body";
import { AuthGuard } from "./features/auth/guards/AuthGuard";
import { ProjectDetailPage } from "./features/projects/pages/ProjectDetailPage";
import { ProjectRegisterPage } from "./features/projects/pages/ProjectRegisterPage";
import { FindProjectsPage } from "./features/projects/pages/FindProjectsPage";
import { AuthProvider, useAuth } from "./shared/contexts/AuthContext";
import { MainPage } from "./pages/MainPage";



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
            </Routes>
          </Body>
        </div>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;