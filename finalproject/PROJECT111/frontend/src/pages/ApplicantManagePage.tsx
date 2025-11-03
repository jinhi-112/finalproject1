import React, { useEffect, useState, useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getApplicantsByProject, updateApplicantStatus } from '@/api';
import { ArrowLeft } from "lucide-react";

// Summary Card Component
function SummaryCard({ label, value, color, onClick, isActive }: any) {
  return (
    <button
      onClick={onClick}
      className={`w-full text-left rounded-lg shadow-sm transition-all duration-200 ${
        isActive ? 'ring-2 ring-indigo-500 bg-indigo-50' : 'bg-white ring-1 ring-gray-200 hover:ring-indigo-400'
      }`}
    >
      <div className="p-6">
        <p className="text-gray-600 text-sm font-medium">{label}</p>
        <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
      </div>
    </button>
  );
}

// Progress Bar Component
function Progress({ label, percent, color }: any) {
  const colorMap: any = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    purple: "bg-purple-500",
  };
  return (
    <div className="flex flex-col w-1/3">
      <div className="flex justify-between text-xs text-gray-500 mb-1">
        <span>{label}</span>
        <span>{percent}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full">
        <div
          className={`${colorMap[color]} h-2 rounded-full`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

export default function ApplicantManagePage() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const [applicants, setApplicants] = useState<any[]>([]);
  const [filter, setFilter] = useState("검토 대기"); // Default filter changed to 'Pending Review'

  const summary = useMemo(() => {
    return {
      pending: applicants.filter(a => a.status === '검토 대기').length,
      reviewed: applicants.filter(a => a.status === '검토 완료').length,
      approved: applicants.filter(a => a.status === '승인').length,
      rejected: applicants.filter(a => a.status === '거절').length,
    };
  }, [applicants]);

  useEffect(() => {
    const fetchApplicants = async () => {
      if (!projectId) return;
      try {
        const res = await getApplicantsByProject(parseInt(projectId, 10));
        setApplicants(res.applicants || []);
      } catch (err) {
        console.error("지원자 목록 불러오기 실패:", err);
        setApplicants([]);
      }
    };
    fetchApplicants();
  }, [projectId]);

  const handleUpdateStatus = async (applicantId: number, newStatus: string) => {
    try {
      await updateApplicantStatus(applicantId, newStatus);
      setApplicants(prevApplicants =>
        prevApplicants.map(app =>
          app.id === applicantId ? { ...app, status: newStatus } : app
        )
      );
    } catch (error) {
      console.error("Failed to update applicant status:", error);
      alert("상태 변경에 실패했습니다.");
    }
  };

  // Simplified filtering logic
  const filteredApplicants = applicants.filter((a) => a.status === filter);

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* Header (Re-arranged) */}
      <div className="mb-8">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-sm text-gray-600 hover:text-black mb-4"
        >
          <ArrowLeft size={16} className="mr-1" />
          프로젝트 관리로 돌아가기
        </button>
        <h1 className="text-3xl font-bold text-gray-900">지원자 관리</h1>
      </div>

      {/* Summary Cards (4 cards) */}
      <div className="grid grid-cols-4 gap-6 mb-10">
        <SummaryCard 
          label="검토 대기" 
          value={summary.pending} 
          color="text-yellow-500"
          onClick={() => setFilter('검토 대기')}
          isActive={filter === '검토 대기'}
        />
        <SummaryCard 
          label="검토 완료" 
          value={summary.reviewed} 
          color="text-blue-600"
          onClick={() => setFilter('검토 완료')}
          isActive={filter === '검토 완료'}
        />
        <SummaryCard 
          label="승인" 
          value={summary.approved} 
          color="text-green-600"
          onClick={() => setFilter('승인')}
          isActive={filter === '승인'}
        />
        <SummaryCard 
          label="거절" 
          value={summary.rejected} 
          color="text-red-500"
          onClick={() => setFilter('거절')}
          isActive={filter === '거절'}
        />
      </div>

      {/* Filter Area (No 'All' tab) */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-4 border-b border-gray-200">
          {["검토 대기", "검토 완료", "승인", "거절"].map((tab) => (
            <button
              key={tab}
              className={`pb-2 ${
                filter === tab
                  ? "border-b-2 border-black text-black font-semibold"
                  : "text-gray-400 hover:text-black"
              }`}
              onClick={() => setFilter(tab)}
            >
              {tab}
            </button>
          ))}
        </div>

        <input
          type="text"
          placeholder="지원자 이름 또는 직무로 검색"
          className="px-4 py-2 border rounded-md text-sm w-80"
        />
      </div>

      {/* Applicant Card List */}
      {filteredApplicants.map((applicant) => (
        <div
          key={applicant.id}
          className="bg-white shadow-sm rounded-xl p-6 mb-6 border border-gray-100"
        >
          <div className="flex justify-between mb-2">
            <div>
              <h2 className="text-lg font-semibold">{applicant.name}</h2>
              <p className="text-sm text-gray-500">{applicant.role}</p>
            </div>
            <p className="text-green-600 font-bold text-lg">
              {applicant.match_rate}% 매칭률
            </p>
          </div>

          {/* Match Bars */}
          <div className="flex items-center gap-4 mb-4">
            <Progress label="기술 매칭" percent={applicant.tech_match} color="blue" />
            <Progress label="경험 매칭" percent={applicant.exp_match} color="green" />
            <Progress label="참여 시간" percent={applicant.time_match} color="purple" />
          </div>

          {/* Skills */}
          <div className="flex flex-wrap gap-2 mb-4">
            {applicant.skills && applicant.skills.map((skill: string, i: number) => (
              <span
                key={i}
                className="bg-gray-100 text-sm px-3 py-1 rounded-full text-gray-700"
              >
                {skill}
              </span>
            ))}
          </div>

          {/* Motivation */}
          <p className="text-gray-600 text-sm mb-4">{applicant.motivation}</p>

          {/* Footer Buttons */}
          <div className="flex justify-between text-sm text-gray-500">
            <div>
              <p>{new Date(applicant.date).toLocaleDateString()}</p>
              <p>주 {applicant.hours}시간</p>
            </div>
            <div className="flex gap-2">
              <button 
                onClick={() => handleUpdateStatus(applicant.id, '거절')}
                className="px-4 py-2 rounded-md border border-gray-300 hover:bg-gray-100 text-gray-700"
              >
                거절
              </button>
              <button 
                onClick={() => handleUpdateStatus(applicant.id, '검토 완료')}
                className="px-4 py-2 rounded-md border border-gray-300 hover:bg-gray-100 text-gray-700"
              >
                검토 완료
              </button>
              <button 
                onClick={() => handleUpdateStatus(applicant.id, '승인')}
                className="px-4 py-2 rounded-md bg-black text-white hover:bg-gray-800"
              >
                승인
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}