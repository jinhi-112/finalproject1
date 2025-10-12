import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import RegisterPage from "./features/auth/pages/RegisterPage";
import LoginPage from "./features/auth/pages/LoginPage";
import { UserInformationPage } from "./features/user-information/pages/UserInformationPage";
import { Header } from "./widgets/Header";
import { Body } from "./widgets/Body";
import { AuthGuard } from "./features/auth/guards/AuthGuard";
import { ProjectDetailPage } from "./features/projects/pages/ProjectDetailPage";
import { ProjectRegisterPage } from "./features/projects/pages/ProjectRegisterPage";
import { AuthProvider, useAuth } from "./shared/contexts/AuthContext";
import { MainPage } from "./pages/MainPage";

const ProfileCompletionBanner = () => {
  const { user } = useAuth();

  if (user && !user.is_profile_complete) {
    return (
      <div className="bg-yellow-200 text-center p-2">
        <p>매칭을 위해선 더 많은 정보를 입력해주셔야 합니다. <Link to="/user-info" className="underline font-bold">정보 입력하기</Link></p>
      </div>
    );
  }

  return null;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <div className="relative flex flex-col h-screen">
          <Header />
          <ProfileCompletionBanner />
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
                  <UserInformationPage />
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