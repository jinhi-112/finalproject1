import { Link } from "react-router-dom";
import { Button } from "../../../shared/components/Button";

// This should eventually be moved to a shared types file
interface Project {
  project_id: number;
  title: string;
  description: string;
  tech_stack: string; // Assuming it's a string for now
}

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  // Placeholder data as the API doesn't provide this yet
  const teamSize = "4명";
  const duration = "3개월";
  const matchRate = "95%";

  // The API currently returns a single string. Let's handle it gracefully.
  const techTags = project.tech_stack?.split(',').map(tag => tag.trim()).filter(tag => tag) || [];

  return (
    <div className="p-6 bg-white rounded-lg border border-gray-200 shadow-md h-full flex flex-col">
      <h5 className="mb-2 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
        {project.title}
      </h5>
      <p className="mb-4 font-normal text-gray-600 text-sm dark:text-gray-400 flex-grow">
        {project.description}
      </p>
      <div className="mb-4 flex flex-wrap gap-2">
        {techTags.map(tag => (
          <span key={tag} className="bg-gray-200 text-gray-800 text-xs font-medium px-2.5 py-0.5 rounded-full dark:bg-gray-700 dark:text-gray-300">
            {tag}
          </span>
        ))}
      </div>
      
      <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center text-sm text-gray-700 dark:text-gray-400 mb-2">
          <span>모집 인원:</span>
          <span className="font-semibold text-gray-900 dark:text-white">{teamSize}</span>
        </div>
        <div className="flex justify-between items-center text-sm text-gray-700 dark:text-gray-400 mb-2">
          <span>기간:</span>
          <span className="font-semibold text-gray-900 dark:text-white">{duration}</span>
        </div>
        <div className="flex justify-between items-center text-sm text-gray-700 dark:text-gray-400 mb-6">
          <span>매칭률:</span>
          <span className="font-semibold text-blue-600 dark:text-blue-500">{matchRate}</span>
        </div>

        <Link to={`/projects/${project.project_id}`} className="w-full">
          <Button variant="outline" className="w-full">자세히 보기</Button>
        </Link>
      </div>
    </div>
  );
}