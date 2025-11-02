import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Input } from "../../../shared/components/Input";
import { Label } from "../../../shared/components/Label";
import { ErrorMessage } from "./ErrorMessage";
import { Button } from "../../../shared/components/Button";
import { Modal } from '../../../shared/components/Modal'; // New import
import apiClient from '@/api';

const schema = yup.object().shape({
  email: yup.string().email("이메일 형식이 아닙니다.").required("필수 입력"),
  password: yup.string()
    .matches(/^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,24}$/, "영문+숫자 8~24자")
    .required("필수 입력"),
  passwordConfirm: yup.string()
    .oneOf([yup.ref("password")], "비밀번호가 일치하지 않습니다.")
    .required("필수 입력"),
  nickname: yup.string()
    .max(12, "닉네임은 12자 이내")
    .required("필수 입력"),
});

export function RegisterForm() {
  const { register, handleSubmit, formState: { errors }, watch } = useForm({
    resolver: yupResolver(schema),
  });
  const [emailError, setEmailError] = useState("");
  const [nicknameError, setNicknameError] = useState("");
  const [passwordMatchMessage, setPasswordMatchMessage] = useState("");
  const [showSuccessModal, setShowSuccessModal] = useState(false); // New state
  const navigate = useNavigate();

  const password = watch("password");
  const passwordConfirm = watch("passwordConfirm");

  useEffect(() => {
    if (password && passwordConfirm && password === passwordConfirm) {
      setPasswordMatchMessage("비밀번호가 일치합니다.");
    } else {
      setPasswordMatchMessage("");
    }
  }, [password, passwordConfirm]);

  const checkEmailDuplicate = async (_email: string) => {
    // TODO
    return false;
  };

  const checkNicknameDuplicate = async (_nickname: string) => {
    // TODO
    return false;
  };

  const onSubmit = async (data: any) => {
    setEmailError("");
    setNicknameError("");
    if (await checkEmailDuplicate(data.email)) {
      setEmailError("이미 사용 중인 이메일입니다.");
      return;
    }
    if (await checkNicknameDuplicate(data.nickname)) {
      setNicknameError("이미 사용 중인 닉네임입니다.");
      return;
    }
    // const hashedPassword = bcrypt.hashSync(data.password, 10);
    try {
      await apiClient.post('/register/', {
        email: data.email,
        password: data.password,
        name: data.nickname,
      });

      setShowSuccessModal(true); // Show modal on success
    } catch (error: any) {
      console.error("Registration failed:", error);
      const errorData = error.response?.data;
      if (errorData) {
        // Handle specific error messages from backend if any
        if (errorData.username) {
          setEmailError(errorData.username[0]);
        } else if (errorData.email) {
          setEmailError(errorData.email[0]);
        } else if (errorData.password) {
          // Handle password errors if needed
        } else if (errorData.nickname) {
          setNicknameError(errorData.nickname[0]);
        } else {
          // Generic error
          alert(errorData.detail || "회원가입 중 오류가 발생했습니다.");
        }
      } else {
        alert("회원가입 중 네트워크 오류가 발생했습니다.");
      }
    }
  };

  const handleCancel = () => {
    navigate("/");
  };

  const handleModalClose = () => {
    setShowSuccessModal(false);
    navigate("/login"); // Navigate to login page after closing modal
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-2">
      <Label htmlFor="email">이메일</Label>
      <Input id="email" {...register("email")} placeholder="이메일" />
      <ErrorMessage>{errors.email?.message || emailError}</ErrorMessage>
      <Label htmlFor="password">비밀번호</Label>
      <Input id="password" type="password" {...register("password")} placeholder="비밀번호" />
      <ErrorMessage>{errors.password?.message}</ErrorMessage>
      <Label htmlFor="passwordConfirm">비밀번호 확인</Label>
      <Input id="passwordConfirm" type="password" {...register("passwordConfirm")} placeholder="비밀번호 확인" />
      <ErrorMessage>{errors.passwordConfirm?.message}</ErrorMessage>
      {passwordMatchMessage && <p className="text-green-600 text-sm mt-1">{passwordMatchMessage}</p>} {/* Display success message */}
      <Label htmlFor="nickname">닉네임</Label>
      <Input id="nickname" {...register("nickname")} placeholder="닉네임" maxLength={12} />
      <ErrorMessage>{errors.nickname?.message || nicknameError}</ErrorMessage>
      <div className="flex justify-between gap-2 mt-4">
        <Button type="button" variant="outline" size="lg" onClick={handleCancel}>취소</Button>
        <Button type="submit" size="lg">{`다음 >`}</Button>
      </div>

      {/* Success Modal */}
      <Modal
        isOpen={showSuccessModal}
        onClose={handleModalClose}
        title="회원가입 완료"
        footer={<Button onClick={handleModalClose}>로그인 페이지로 이동</Button>}
      >
        <p>회원가입이 성공적으로 완료되었습니다.</p>
      </Modal>
    </form>
  );
}

