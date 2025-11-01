import { Link } from "react-router-dom";
import type { Project } from "../../../shared/types/project";

// This should eventually be moved to a shared types file

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const techTags = project.tech_stack?.split(',').map(tag => tag.trim()).filter(tag => tag) || [];

  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR');
  };

  const duration = project.start_date && project.end_date 
    ? `${formatDate(project.start_date)} ~ ${formatDate(project.end_date)}`
    : "미정";

  return (
    <Link to={`/projects/${project.project_id}`} className="block group">
      <div className="p-6 bg-white rounded-xl border border-slate-200 flex flex-col transition-all duration-300 ease-in-out group-hover:shadow-lg group-hover:-translate-y-1">
        
        {/* Header Section */}
        <div>
          <div className="flex justify-between items-start mb-4">
            <h5 className="text-lg font-extrabold text-slate-800 tracking-tight">
              {project.title}
            </h5>
            {project.user_matching_rate !== undefined && project.user_matching_rate !== null ? (
              <div className="bg-blue-50 text-blue-600 px-3 py-1 rounded-full flex items-center gap-1.5">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
                </svg>
                {project.user_matching_rate > 0 ? (
                    <span className="font-bold text-sm">{project.user_matching_rate}%</span>
                ) : (
                    <span className="font-bold text-xs">계산 중...</span>
                )}
              </div>
            ) : null}
          </div>

          {/* Tech Tags */}
          <div className="mb-5 flex flex-wrap gap-2">
            {techTags.slice(0, 4).map(tag => ( // Show max 4 tags
              <span key={tag} className="bg-slate-100 text-slate-600 text-xs font-medium px-2.5 py-1 rounded-md">
                {tag}
              </span>
            ))}
            {techTags.length > 4 && (
              <span className="bg-slate-100 text-slate-500 text-xs font-medium px-2.5 py-1 rounded-md">
                +{techTags.length - 4}
              </span>
            )}
          </div>
        </div>

        {/* Footer Section */}
        <div className="pt-4">
          <div className="flex justify-between items-center text-sm text-slate-500 mb-2">
            <span>모집 인원</span>
            <span className="font-semibold text-slate-700">{project.recruitment_count}명</span>
          </div>
          <div className="flex justify-between items-center text-sm text-slate-500">
            <span>프로젝트 기간</span>
            <span className="font-semibold text-slate-700">{duration}</span>
          </div>
        </div>
      </div>
    </Link>
  );
}