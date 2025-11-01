import { Link } from "react-router-dom";
import { Button } from "../shared/components/Button";
import { useAuth } from "../shared/contexts/AuthContext";

export function Header() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-background py-4 px-6 flex items-center border-b shadow-sm">
      {/* Left Section */}
      <div className="flex-1">
        <Link to="/" className="text-xl font-bold">AI 프로젝트 매칭</Link>
      </div>

      {/* Center Navigation */}
      <nav className="hidden md:flex gap-8">
        <Link to="/find-projects" className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">프로젝트 찾기</Link>
        {isAuthenticated && (
          <Link to="/recommended-projects" className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">AI 추천</Link>
        )}
        <Link to="/register-project" className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">프로젝트 등록</Link>
        <Link to="/about" className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">서비스 소개</Link>
        <Link to="/faq" className="text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white">자주 묻는 질문</Link>
      </nav>

      {/* Right Section */}
      <div className="flex-1 flex justify-end">
        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <Link to="/user-info">
                <Button variant="ghost">마이페이지</Button>
              </Link>
              <Button onClick={logout}>로그아웃</Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost">로그인</Button>
              </Link>
              <Link to="/register">
                <Button>회원가입</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}