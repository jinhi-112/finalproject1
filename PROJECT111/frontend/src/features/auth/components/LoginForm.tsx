import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "../../../shared/components/Input";
import { Label } from "../../../shared/components/Label";
import { ErrorMessage } from "./ErrorMessage";
import { Button } from "../../../shared/components/Button";
import { useAuth } from "../../../shared/contexts/AuthContext"; // New import

// Helper to get CSRF token from cookies
function getCookie(name: string) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const schema = yup.object().shape({
  email: yup.string().email("이메일 형식이 아닙니다.").required("필수 입력"),
  password: yup.string().required("필수 입력"),
});

export function LoginForm() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
  });
  const [loginError, setLoginError] = useState("");
  const [loginSuccess, setLoginSuccess] = useState("");
  const navigate = useNavigate();
  const { login } = useAuth(); // Use auth context

  const onSubmit = async (data: any) => {
    setLoginError("");

    try {
      const response = await fetch('http://127.0.0.1:8000/api/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email: data.email, password: data.password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        setLoginError(errorData.error || "이메일 또는 비밀번호가 올바르지 않습니다.");
        return;
      }

      // 로그인 성공
      const responseData = await response.json();
      alert(responseData.message); // "로그인 완료" 알림창 띄우기

      // AuthContext에 백엔드로부터 받은 실제 사용자 정보 저장
      login(responseData.user);

      navigate("/"); // 메인 페이지로 이동

    } catch (error) {
      console.error("Login failed:", error);
      setLoginError("로그인 중 오류가 발생했습니다.");
    }
  };

  const handleCancel = () => {
    navigate("/");
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-2">
      <Label htmlFor="email">이메일</Label>
      <Input id="email" {...register("email")}
        placeholder="이메일"
        autoComplete="username"
      />
      <ErrorMessage>{errors.email?.message}</ErrorMessage>
      <Label htmlFor="password">비밀번호</Label>
      <Input id="password" type="password" {...register("password")}
        placeholder="비밀번호"
        autoComplete="current-password"
      />
      <ErrorMessage>{errors.password?.message}</ErrorMessage>
      {loginError && <ErrorMessage>{loginError}</ErrorMessage>} {/* Display error if exists */}
      {loginSuccess && <p className="text-green-600 text-sm mt-2">{loginSuccess}</p>} {/* Display success message */}
      <div className="flex justify-between gap-2 mt-4">
        <Button variant="outline" size="lg" onClick={handleCancel}>취소</Button>
        <Button type="submit" size="lg">로그인</Button>
      </div>
    </form>
  );
}
