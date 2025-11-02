import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getApplicantsByProject } from '@/api'; // ✅ 백엔드 연동용 API
import { ArrowLeft } from "lucide-react";

export default function ApplicantManagePage() {
  const navigate = useNavigate();
  const [applicants, setApplicants] = useState<any[]>([]);
  const [filter, setFilter] = useState("전체");
  const [summary, setSummary] = useState({
    pending: 0,
    reviewed: 0,
    approved: 0,
    rejected: 0,
  });

  useEffect(() => {
    const fetchApplicants = async () => {
      try {
        const res = await getApplicantsByProject(); // 실제 프로젝트 ID 전달 필요
        setApplicants(res.applicants);
        setSummary(res.summary);
      } catch (err) {
        console.error("지원자 목록 불러오기 실패:", err);
      }
    };
    fetchApplicants();
  }, []);

  const filtered =
    filter === "전체"
      ? applicants
      : applicants.filter((a) => a.status === filter);

  return (
    <div className="p-8 bg-gray-50 min-h-screen">
      {/* 상단 헤더 */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center text-gray-600 hover:text-black"
          >
            <ArrowLeft size={20} className="mr-1" />
            프로젝트 관리로 돌아가기
          </button>
          <h1 className="text-3xl font-bold ml-4">지원자 관리</h1>
        </div>
        <button className="px-5 py-2 bg-gray-800 text-white rounded-md text-sm">
          지원서 다운로드
        </button>
      </div>

      {/* 요약 카드 */}
      <div className="grid grid-cols-4 gap-6 mb-10">
        <SummaryCard label="검토 대기" value={summary.pending} color="text-yellow-500" />
        <SummaryCard label="검토 완료" value={summary.reviewed} color="text-blue-600" />
        <SummaryCard label="승인" value={summary.approved} color="text-green-600" />
        <SummaryCard label="거절" value={summary.rejected} color="text-red-500" />
      </div>

      {/* 필터 영역 */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex gap-4 border-b border-gray-200">
          {["전체", "검토 대기", "검토 완료", "승인", "거절"].map((tab) => (
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

      {/* 지원자 카드 리스트 */}
      {filtered.map((applicant) => (
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

          {/* 매칭 바 */}
          <div className="flex items-center gap-4 mb-4">
            <Progress label="기술 매칭" percent={applicant.tech_match} color="blue" />
            <Progress label="경험 매칭" percent={applicant.exp_match} color="green" />
            <Progress label="참여 시간" percent={applicant.time_match} color="purple" />
          </div>

          {/* 보유 기술 */}
          <div className="flex flex-wrap gap-2 mb-4">
            {applicant.skills.map((skill: string, i: number) => (
              <span
                key={i}
                className="bg-gray-100 text-sm px-3 py-1 rounded-full text-gray-700"
              >
                {skill}
              </span>
            ))}
          </div>

          {/* 지원 동기 */}
          <p className="text-gray-600 text-sm mb-4">{applicant.motivation}</p>

          {/* 하단 버튼 */}
          <div className="flex justify-between text-sm text-gray-500">
            <div>
              <p>{applicant.date}</p>
              <p>주 {applicant.hours}시간</p>
            </div>
            <div className="flex gap-2">
              <button className="px-4 py-2 rounded-md border border-gray-200 hover:bg-gray-50">
                거절
              </button>
              <button className="px-4 py-2 rounded-md bg-black text-white hover:bg-gray-800">
                승인
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ✅ 요약 카드 컴포넌트
function SummaryCard({ label, value, color }: any) {
  return (
    <div className="bg-white shadow rounded-xl p-6 text-center">
      <p className="text-gray-500 text-sm">{label}</p>
      <p className={`text-2xl font-bold mt-2 ${color}`}>{value}</p>
    </div>
  );
}

// ✅ 매칭률 바 컴포넌트
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
