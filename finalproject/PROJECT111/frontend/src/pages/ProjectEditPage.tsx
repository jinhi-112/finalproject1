
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useNavigate, useParams } from "react-router-dom";
import { Input } from "../shared/components/Input";
import { Label } from "../shared/components/Label";
import { Button } from "../shared/components/Button";
import { ErrorMessage } from "../features/auth/components/ErrorMessage";
import { getProject, updateProject } from "../api";

const schema = yup.object().shape({
  title: yup.string().required("프로젝트 제목은 필수입니다."),
  description: yup.string().required("프로젝트 설명은 필수입니다."),
  goal: yup.string().required("프로젝트 목표는 필수입니다."),
  tech_stack: yup.string().required("기술 스택은 필수입니다."),
  recruitment_count: yup.number()
    .typeError("모집 인원은 숫자여야 합니다.")
    .required("모집 인원은 필수입니다.")
    .min(1, "모집 인원은 최소 1명 이상이어야 합니다."),
  start_date: yup.string().required("시작일은 필수입니다."),
  end_date: yup.string()
    .required("종료일은 필수입니다.")
    .test(
      "end-date-after-start-date",
      "종료일은 시작일보다 늦어야 합니다.",
      function (value) {
        const { start_date } = this.parent;
        return new Date(value) >= new Date(start_date);
      }
    ),
  application_deadline: yup.string()
    .required("지원 마감일은 필수입니다.")
    .test(
      "deadline-before-end-date",
      "지원 마감일은 프로젝트 종료일보다 빨라야 합니다.",
      function (value) {
        const { end_date } = this.parent;
        return new Date(value) < new Date(end_date);
      }
    ),
  is_open: yup.boolean().required("모집 여부는 필수입니다."),
});

export default function ProjectEditPage() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { register, handleSubmit, reset, formState: { errors } } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      title: '',
      description: '',
      goal: '',
      tech_stack: '',
      recruitment_count: 1,
      start_date: '',
      end_date: '',
      application_deadline: '',
      is_open: true,
    }
  });

  useEffect(() => {
    if (projectId) {
      const fetchProject = async () => {
        try {
          const project = await getProject(projectId);
          reset({
            ...project,
            start_date: project.start_date?.split('T')[0],
            end_date: project.end_date?.split('T')[0],
            application_deadline: project.application_deadline?.split('T')[0],
          });
        } catch (error) {
          console.error("Failed to fetch project:", error);
        }
      };
      fetchProject();
    }
  }, [projectId, reset]);

  const onSubmit = async (data: any) => {
    if (!projectId) return;
    try {
      await updateProject(projectId, data);
      navigate("/manage-projects");
    } catch (error) {
      console.error("Failed to update project:", error);
    }
  };

  return (
    <div className="w-full min-h-screen py-10">
      <div className="max-w-3xl mx-auto bg-white p-8 rounded-lg shadow-lg">
        <h2 className="text-3xl font-bold mb-8 text-center text-gray-800">프로젝트 수정</h2>
        <form onSubmit={handleSubmit(onSubmit)} className="flex flex-col gap-6">
          <div>
            <Label htmlFor="title" className="text-lg font-medium text-gray-700">프로젝트 제목</Label>
            <Input {...register("title")} placeholder="프로젝트 제목을 입력하세요" className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
            <ErrorMessage>{errors.title?.message}</ErrorMessage>
          </div>

          <div>
            <Label htmlFor="description" className="text-lg font-medium text-gray-700">프로젝트 설명</Label>
            <textarea {...register("description")} placeholder="프로젝트 설명을 입력하세요" rows={4} className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"></textarea>
            <ErrorMessage>{errors.description?.message}</ErrorMessage>
          </div>

          <div>
            <Label htmlFor="goal" className="text-lg font-medium text-gray-700">프로젝트 목표</Label>
            <textarea {...register("goal")} placeholder="프로젝트 목표를 입력하세요" rows={3} className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"></textarea>
            <ErrorMessage>{errors.goal?.message}</ErrorMessage>
          </div>

          <div>
            <Label htmlFor="tech_stack" className="text-lg font-medium text-gray-700">기술 스택</Label>
            <Input {...register("tech_stack")} placeholder="예: React, Node.js, Python" className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
            <ErrorMessage>{errors.tech_stack?.message}</ErrorMessage>
          </div>

          <div>
            <Label htmlFor="recruitment_count" className="text-lg font-medium text-gray-700">모집 인원</Label>
            <Input type="number" {...register("recruitment_count")} placeholder="예: 4" min="1" className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
            <ErrorMessage>{errors.recruitment_count?.message}</ErrorMessage>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <Label htmlFor="start_date" className="text-lg font-medium text-gray-700">시작일</Label>
              <Input type="date" {...register("start_date")} className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
              <ErrorMessage>{errors.start_date?.message}</ErrorMessage>
            </div>
            <div>
              <Label htmlFor="end_date" className="text-lg font-medium text-gray-700">종료일</Label>
              <Input type="date" {...register("end_date")} className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
              <ErrorMessage>{errors.end_date?.message}</ErrorMessage>
            </div>
            <div>
              <Label htmlFor="application_deadline" className="text-lg font-medium text-gray-700">지원 마감일</Label>
              <Input type="date" {...register("application_deadline")} className="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500" />
              <ErrorMessage>{errors.application_deadline?.message}</ErrorMessage>
            </div>
          </div>

          <div className="flex items-center gap-3 mt-2">
            <Input type="checkbox" {...register("is_open")} id="is_open" className="h-5 w-5 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
            <Label htmlFor="is_open" className="text-lg font-medium text-gray-700 mb-0">모집 중</Label>
            <ErrorMessage>{errors.is_open?.message}</ErrorMessage>
          </div>

          <div className="flex justify-end gap-4 mt-8">
            <Button type="button" variant="outline" onClick={() => navigate('/manage-projects')} className="px-6 py-2 text-lg">취소</Button>
            <Button type="submit" className="px-6 py-2 text-lg">프로젝트 수정</Button>
          </div>
        </form>
      </div>
    </div>
  );
}
