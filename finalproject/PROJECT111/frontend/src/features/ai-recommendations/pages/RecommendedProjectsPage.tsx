import React, { useState, useEffect, useMemo } from 'react';
import { getRecommendedProjects } from '../../../api';
import { Link, useNavigate, type NavigateFunction } from 'react-router-dom';
import type { Project } from '../../../shared/types/project';

// --- Interfaces ---

interface RecommendedProjectData {
  project: Project;
  score: number;
  explanation?: {
    for_recommendation_page: {
      primary_reason: string;
      additional_reasons: string[];
    };
  };
}

interface UserProfile {
  tech_stack?: string[];
  preferred_team_size?: 'SMALL' | 'MEDIUM' | 'LARGE';
  availability_period?: 'SHORT' | 'MEDIUM' | 'LONG';
}

interface StatCardProps {
  title: string;
  value: number;
  icon: string;
  unit: string;
  onClick: () => void;
  isActive: boolean;
}

interface TechTagProps {
  text: string;
  isPrimary?: boolean;
}

interface ProjectCardProps {
  projectData: RecommendedProjectData;
  userProfile: UserProfile | null;
  rank: number;
  navigate: NavigateFunction;
}

// --- Helper Components ---

const StatCard: React.FC<StatCardProps> = ({ title, value, icon, unit, onClick, isActive }) => (
    <button 
        onClick={onClick} 
        className={`w-full text-left rounded-lg shadow-sm transition-all duration-200 ${isActive ? 'ring-2 ring-blue-500' : 'ring-1 ring-gray-200 hover:ring-blue-400'}`}>
        <div className={`p-4 rounded-lg flex items-center h-full ${isActive ? 'bg-blue-50' : 'bg-white'}`}>
            <div className="mr-4 text-blue-500">{icon}</div>
            <div>
                <p className="text-sm text-gray-500">{title}</p>
                <p className="text-2xl font-bold">{value}<span className="text-lg ml-1">{unit}</span></p>
            </div>
        </div>
    </button>
);

const TechTag: React.FC<TechTagProps> = ({ text, isPrimary = false }) => (
    <span className={`text-xs font-medium mr-2 px-2.5 py-1 rounded-md ${isPrimary ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'}`}>
        {text}
        {isPrimary && <span className="text-yellow-500 ml-1">⭐</span>}
    </span>
);

const ProjectCard: React.FC<ProjectCardProps> = ({ projectData, userProfile, rank, navigate }) => {
  const { project, score, explanation } = projectData;

  const recommendation = explanation?.for_recommendation_page;

  const userTech = useMemo(() => new Set(userProfile?.tech_stack?.map(t => t.toLowerCase()) || []),
   [userProfile]);

  const projectTech = useMemo(() => project.tech_stack?.split(',').map(t => t.trim()) || [], [project.tech_stack]);

  const learningOpportunities = useMemo(() => 
    projectTech.filter(tech => !userTech.has(tech.toLowerCase())),
    [projectTech, userTech]
  );

  const getScoreInfo = (score: number) => {
      if (score >= 85) {
        return { text: '높음', color: 'text-green-600', bg: 'bg-green-100' };
      }
      if (score <= 50) {
        return { text: '낮음', color: 'text-red-600', bg: 'bg-red-100' };
      }
      return { text: '보통', color: 'text-blue-600', bg: 'bg-blue-100' };
  };

  const scoreInfo = getScoreInfo(score);

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-4">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-blue-600 font-semibold">#{rank}</p>
          <h3 className="text-xl font-bold mt-1">{project.title}</h3>
          <p className="text-gray-600 mt-2">{project.description}</p>
        </div>
        <div className="text-center ml-4 flex-shrink-0">
            <div className={`w-24 h-24 rounded-full flex items-center justify-center ${scoreInfo.bg}`}>
                <p className={`text-3xl font-bold ${scoreInfo.color}`}>{Math.round(score)}%</p>
            </div>
            <p className="text-sm font-semibold mt-2">매칭률</p>
            <p className={`text-xs ${scoreInfo.color}`}>{scoreInfo.text}</p>
        </div>
      </div>

      <div className="mt-4 flex items-center space-x-4 text-sm text-gray-600">
        <span>🕒 {project.start_date} ~ {project.end_date}</span>
        <span>👥 {project.recruitment_count}명</span>
      </div>

      <div className="mt-6 bg-gray-100 p-4 rounded-lg">
        <h4 className="font-semibold text-gray-800">🤔 왜 이 프로젝트를 추천하나요?</h4>
        <div className="mt-3 space-y-2">
            {recommendation?.primary_reason && (
                <div className=" flex items-start">
                    <span className="bg-gray-800 text-white text-xs font-semibold mr-3 px-2 py-1 rounded-md">주요</span>
                    <p className="text-sm text-gray-700">{recommendation.primary_reason}</p>
                </div>
            )}
            {recommendation?.additional_reasons?.map((reason, index) => (
                <div key={index} className=" flex items-start">
                    <span className="bg-gray-200 text-gray-700 text-xs font-semibold mr-3 px-2 py-1 rounded-md">추가</span>
                    <p className="text-sm text-gray-700">{reason}</p>
                </div>
            ))}
        </div>
      </div>

      <div className="mt-4">
        <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8" aria-label="Tabs">
                <a href="#" className="border-blue-500 text-blue-600 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm">기술 분석</a>
            </nav>
        </div>
        <div className="py-4">
            <h5 className="font-semibold">보유 기술 매칭</h5>
            <div className="mt-2">
                {projectTech.map(tech => <TechTag key={tech} text={tech} isPrimary={userTech.has(tech.toLowerCase())} />)}
            </div>
            <h5 className="font-semibold mt-4">학습 기회</h5>
            <div className="mt-2">
                {learningOpportunities.map(tech => <TechTag key={tech} text={tech} />)}
            </div>
        </div>
      </div>

      <div className="mt-6 flex justify-between items-center">
        <Link to={`/projects/${project.project_id}`} className="text-sm font-medium text-blue-600 hover:underline">상세 보기 &gt;</Link>
        <button onClick={() => navigate(`/apply/${project.project_id}`)} className="px-6 py-2 bg-gray-800 text-white font-semibold rounded-lg hover:bg-gray-900">지원하기</button>
      </div>
    </div>
  );
};

// --- Filtering Helpers ---
const isHighMatch = (p: RecommendedProjectData): boolean => p.score >= 85;

const isTeamSizeFit = (p: RecommendedProjectData, userProfile: UserProfile | null): boolean => {
    if (!userProfile?.preferred_team_size) return false;
    const preference = userProfile.preferred_team_size;
    const count = p.project.recruitment_count;
    if (preference === 'SMALL' && count >= 2 && count <= 3) return true;
    if (preference === 'MEDIUM' && count >= 4 && count <= 5) return true;
    if (preference === 'LARGE' && count >= 6) return true;
    return false;
};

const isPeriodFit = (p: RecommendedProjectData, userProfile: UserProfile | null): boolean => {
    if (!userProfile?.availability_period) return false;
    const preference = userProfile.availability_period;
    const start = new Date(p.project.start_date);
    const end = new Date(p.project.end_date);
    const durationMonths = (end.getFullYear() - start.getFullYear()) * 12 + (end.getMonth() - start.getMonth());
    if (preference === 'SHORT' && durationMonths <= 1) return true;
    if (preference === 'MEDIUM' && durationMonths >= 2 && durationMonths <= 3) return true;
    if (preference === 'LONG' && durationMonths > 3) return true;
    return false;
};

const isGrowthOpportunity = (p: RecommendedProjectData, userProfile: UserProfile | null): boolean => {
    if (!userProfile?.tech_stack) return false;
    const userTech = new Set(userProfile.tech_stack.map(t => t.toLowerCase()));
    const projectTech = p.project.tech_stack?.split(',').map(t => t.trim().toLowerCase()) || [];
    return projectTech.some(tech => !userTech.has(tech));
};


// --- Main Page Component ---

export const RecommendedProjectsPage: React.FC = () => {
  const [projects, setProjects] = useState<RecommendedProjectData[]>([]);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeFilter, setActiveFilter] = useState('all');
  const [sortBy, setSortBy] = useState('recommendation');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        setLoading(true);
        const response = await getRecommendedProjects();
        setProjects(response.recommended_projects || []);
        setUserProfile(response.user_profile || null);
      } catch (err) {
        setError('추천 프로젝트를 불러오는 데 실패했습니다.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, []);

  const stats = useMemo(() => [
      { title: '높은 매칭률', filterKey: 'high-match', value: projects.filter(isHighMatch).length, icon: '📈', unit: '개' },
      { title: '팀 규모 적합', filterKey: 'team-size', value: projects.filter(p => isTeamSizeFit(p, userProfile)).length, icon: '👥', unit: '개' },
      { title: '기간 적합', filterKey: 'period', value: projects.filter(p => isPeriodFit(p, userProfile)).length, icon: '🕒', unit: '개' },
      { title: '성장 기회', filterKey: 'growth', value: projects.filter(p => isGrowthOpportunity(p, userProfile)).length, icon: '✨', unit: '개' },
  ], [projects, userProfile]);

  const filteredProjects = useMemo(() => {
      if (activeFilter === 'all') return projects;
      if (activeFilter === 'high-match') return projects.filter(isHighMatch);
      if (activeFilter === 'team-size') return projects.filter(p => isTeamSizeFit(p, userProfile));
      if (activeFilter === 'period') return projects.filter(p => isPeriodFit(p, userProfile));
      if (activeFilter === 'growth') return projects.filter(p => isGrowthOpportunity(p, userProfile));
      return projects;
  }, [projects, userProfile, activeFilter]);

  const sortedProjects = useMemo(() => {
    const sortable = [...filteredProjects];
    if (sortBy === 'newest') {
        sortable.sort((a, b) => new Date(b.project.created_at).getTime() - new Date(a.project.created_at).getTime());
    } else if (sortBy === 'oldest') {
        sortable.sort((a, b) => new Date(a.project.created_at).getTime() - new Date(b.project.created_at).getTime());
    }
    // Default is 'recommendation', which is the original order from the API
    return sortable;
  }, [filteredProjects, sortBy]);

  const handleFilterClick = (filterKey: string) => {
      setActiveFilter(prev => prev === filterKey ? 'all' : filterKey);
  }

  return (
    <div className="bg-gray-50 min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold flex items-center">✨ AI 추천 프로젝트</h1>
          <p className="mt-2 text-gray-600">당신의 프로필을 분석하여 가장 적합한 프로젝트를 추천해드립니다.</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {stats.map(stat => (
                <StatCard 
                    key={stat.title} 
                    {...stat} 
                    isActive={activeFilter === stat.filterKey}
                    onClick={() => handleFilterClick(stat.filterKey)}
                />
            ))}
        </div>

        <div className="flex justify-between items-center mb-4">
            <div className="text-sm">
                <span className="font-semibold text-blue-600">{sortedProjects.length}개</span> 프로젝트
            </div>
            <div className="relative">
                <select 
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="appearance-none rounded-md border border-gray-300 bg-white py-2 pl-3 pr-10 text-sm focus:border-blue-500 focus:outline-none focus:ring-blue-500"
                >
                    <option value="recommendation">추천순</option>
                    <option value="newest">최신순</option>
                    <option value="oldest">오래된 순</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                    <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                </div>
            </div>
        </div>

        {loading && <p>추천 프로젝트를 불러오는 중...</p>}
        {error && <p className="text-red-500">{error}</p>}
        {!loading && !error && (
          <div>
            {sortedProjects.map((p, index) => (
              <ProjectCard key={p.project.project_id} projectData={p} userProfile={userProfile} rank={index + 1} navigate={navigate} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
