import { LoginForm } from "../components/LoginForm";
import { Card } from "../../../shared/components/Card";

export default function LoginPage() {
  return (
    <div className="flex justify-center items-center w-full h-full flex-1">
      <Card className="p-6 flex flex-col gap-4 w-full max-w-2xl">
        <div className="flex flex-col gap-2">
          <h3>로그인</h3>
          <p className="text-sm text-muted-foreground">AI 기반 사이드 프로젝트 매칭 서비스에 로그인하세요</p>
        </div>
        <LoginForm />
      </Card>
    </div>
  );
}
