import { useParams } from "react-router-dom";

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();

  return (
    <div>
      <h2>프로젝트 상세 정보</h2>
      <p>현재 보고 있는 프로젝트 ID: {projectId}</p>
      {/* TODO: 이 ID를 사용하여 백엔드에서 전체 프로젝트 데이터를 가져와 표시합니다. */}
    </div>
  );
}
