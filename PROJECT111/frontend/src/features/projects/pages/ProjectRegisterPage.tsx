import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup"; // Explicitly added
import { useNavigate } from "react-router-dom";
import { useState } from "react"; // Explicitly added
import { Input } from "../../../shared/components/Input";
import { Label } from "../../../shared/components/Label";
import { ErrorMessage } from "../../auth/components/ErrorMessage";
import { Button } from "../../../shared/components/Button";
import { Modal } from "../../../shared/components/Modal"; // New import
import apiClient from "../../../api";

const schema = yup.object().shape({
  title: yup.string().required("프로젝트 제목은 필수입니다."),
  description: yup.string().required("프로젝트 설명은 필수입니다."),
  goal: yup.string().required("프로젝트 목표는 필수입니다."),
  tech_stack: yup.string().required("기술 스택은 필수입니다."),
  is_open: yup.boolean().required("모집 여부는 필수입니다."),
});

export function ProjectRegisterPage() {
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
  });
  const navigate = useNavigate();
  const [showSuccessModal, setShowSuccessModal] = useState(false); // New state

  const onSubmit = async (data: any) => {
    try {
      const result = await apiClient.post('/projects/', data);

      console.log('프로젝트 등록 성공:', result.data);
      setShowSuccessModal(true); // Show modal on success
    } catch (error) {
      console.error('프로젝트 등록 실패:', error);
      // TODO: 사용자에게 오류 메시지 표시
    }
  };

  const handleCancel = () => {
    navigate('/');
  };

  const handleModalClose = () => {
    setShowSuccessModal(false);
    navigate('/'); // Navigate to main page after closing modal
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-center">새 프로젝트 등록</h2>
      <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-4">
        <div>
          <Label htmlFor="title">프로젝트 제목</Label>
          <Input {...register("title")} placeholder="프로젝트 제목을 입력하세요" />
          <ErrorMessage>{errors.title?.message}</ErrorMessage>
        </div>

        <div>
          <Label htmlFor="description">프로젝트 설명</Label>
          <Input {...register("description")} placeholder="프로젝트 설명을 입력하세요" />
          <ErrorMessage>{errors.description?.message}</ErrorMessage>
        </div>

        <div>
          <Label htmlFor="goal">프로젝트 목표</Label>
          <Input {...register("goal")} placeholder="프로젝트 목표를 입력하세요" />
          <ErrorMessage>{errors.goal?.message}</ErrorMessage>
        </div>

        <div>
          <Label htmlFor="tech_stack">기술 스택</Label>
          <Input {...register("tech_stack")} placeholder="예: React, Node.js, Python" />
          <ErrorMessage>{errors.tech_stack?.message}</ErrorMessage>
        </div>

        <div className="flex items-center gap-2">
          <Input type="checkbox" {...register("is_open")} id="is_open" className="w-auto" />
          <Label htmlFor="is_open" className="mb-0">모집 중</Label>
          <ErrorMessage>{errors.is_open?.message}</ErrorMessage>
        </div>

        <div className="flex justify-end gap-4 mt-6">
          <Button type="button" variant="outline" onClick={handleCancel}>취소</Button>
          <Button type="submit">프로젝트 등록</Button>
        </div>
      </form>

      {/* Success Modal */}
      <Modal
        isOpen={showSuccessModal}
        onClose={handleModalClose}
        title="프로젝트 등록 완료"
        footer={<Button onClick={handleModalClose}>메인 페이지로 이동</Button>}
      >
        <p>새 프로젝트가 성공적으로 등록되었습니다.</p>
      </Modal>
    </div>
  );
}