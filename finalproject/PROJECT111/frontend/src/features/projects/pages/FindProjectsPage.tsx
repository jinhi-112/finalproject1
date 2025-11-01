import { useState, useEffect } from "react";
import { ProjectCard } from "../components/ProjectCard";
import { Input } from "../../../shared/components/Input";
import { Button } from "../../../shared/components/Button";
import apiClient from "../../../api"; // Import apiClient
import { Label } from "../../../shared/components/Label";
import type { Project } from "../../../shared/types/project";

interface ProjectListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Project[];
}

export function FindProjectsPage() {
  // Input states
  const [searchField, setSearchField] = useState("title"); // 'title', 'description', 'tech_stack'
  const [searchTerm, setSearchTerm] = useState("");
  const [recruitmentCount, setRecruitmentCount] = useState<string>("");
  const [ordering, setOrdering] = useState("-created_at");

  // States that trigger actual search (updated on button click)
  const [currentSearchField, setCurrentSearchField] = useState("title");
  const [currentSearchTerm, setCurrentSearchTerm] = useState("");
  const [currentRecruitmentCount, setCurrentRecruitmentCount] = useState<string>("");
  const [currentOrdering, setCurrentOrdering] = useState("-created_at");

  const [projects, setProjects] = useState<Project[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Function to trigger search
  const handleSearch = () => {
    setCurrentSearchField(searchField);
    setCurrentSearchTerm(searchTerm);
    setCurrentRecruitmentCount(recruitmentCount);
    setCurrentOrdering(ordering);
  };

  useEffect(() => {
    const fetchProjects = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = new URLSearchParams();

        if (currentSearchTerm) {
          params.append(`${currentSearchField}__icontains`, currentSearchTerm);
        }
        
        if (currentRecruitmentCount) {
          params.append('recruitment_count__gte', currentRecruitmentCount);
        }

        // Always include ordering
        params.append('ordering', currentOrdering);

        const queryString = params.toString();
        const url = `/projects/search/?${queryString}`;

        const response = await apiClient.get<ProjectListResponse>(url);
        setProjects(response.data.results || []);
        setTotalCount(response.data.count || 0);
      } catch (err) {
        console.error("프로젝트 검색 실패:", err);
        setError("프로젝트를 검색하는 데 실패했습니다.");
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [currentSearchField, currentSearchTerm, currentRecruitmentCount, currentOrdering]);

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6 text-center">프로젝트 검색</h1>
      
      {/* Specific Field Search */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 items-end">
        <div className="md:col-span-1">
          <Label htmlFor="searchField">검색 기준</Label>
          <select
            id="searchField"
            className="w-full p-2 border border-gray-300 rounded-md"
            value={searchField}
            onChange={(e) => setSearchField(e.target.value)}
          >
            <option value="title">제목</option>
            <option value="description">내용</option>
            <option value="tech_stack">기술 스택</option>
          </select>
        </div>
        <div className="md:col-span-2">
          <Label htmlFor="searchTerm">검색어</Label>
          <Input
            type="text"
            id="searchTerm"
            placeholder="검색어를 입력하세요..."
            className="w-full p-2 border border-gray-300 rounded-md"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <div>
          <Label htmlFor="recruitmentCount">모집 인원 (최소)</Label>
          <Input
            type="number"
            id="recruitmentCount"
            placeholder="최소 모집 인원..."
            className="w-full p-2 border border-gray-300 rounded-md"
            value={recruitmentCount}
            onChange={(e) => setRecruitmentCount(e.target.value)}
            min="0"
          />
        </div>
        <div>
          <Label htmlFor="ordering">정렬 기준</Label>
          <select
            id="ordering"
            className="w-full p-2 border border-gray-300 rounded-md"
            value={ordering}
            onChange={(e) => setOrdering(e.target.value)}
          >
            <option value="-created_at">최신순</option>
            <option value="created_at">오래된순</option>
            <option value="title">제목순 (오름차순)</option>
            <option value="-title">제목순 (내림차순)</option>
            <option value="recruitment_count">모집 인원순 (적은순)</option>
            <option value="-recruitment_count">모집 인원순 (많은순)</option>
          </select>
        </div>
      </div>

      <div className="flex justify-end mb-8">
        <Button onClick={handleSearch} className="px-6 py-2 text-lg">검색하기</Button>
      </div>

      {loading && <p className="text-center text-blue-600">검색 중...</p>}
      {error && <p className="text-center text-red-600">{error}</p>}

      {!loading && !error && (
        <p className="text-right text-gray-700 mb-4">조건에 맞는 프로젝트: <span className="font-bold">{totalCount}</span>개</p>
      )}

      {!loading && !error && projects.length === 0 && (
        <p className="text-center text-gray-500">검색 결과가 없습니다.</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map((project) => (
          <ProjectCard key={project.project_id} project={project} />
        ))}
      </div>
    </div>
  );
}
