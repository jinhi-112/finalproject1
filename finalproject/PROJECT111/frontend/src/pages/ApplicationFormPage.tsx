import React, { useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import apiClient from '@/api';

const ApplicationFormPage: React.FC = () => {
  const [role, setRole] = useState<string>('');
  const [motivation, setMotivation] = useState<string>('');
  const [time, setTime] = useState<string>('');

  const [roleError, setRoleError] = useState<string>('');
  const [motivationError, setMotivationError] = useState<string>('');
  const [timeError, setTimeError] = useState<string>('');

  const [applicationComplete, setApplicationComplete] = useState<boolean>(false);
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();

  const validateForm = (): boolean => {
    let isValid = true;
    setRoleError('');
    setMotivationError('');
    setTimeError('');

    if (role.trim() === '') {
      setRoleError('지원 역할을 입력해주세요.');
      isValid = false;
    }
    if (motivation.trim() === '') {
      setMotivationError('지원 동기를 입력해주세요.');
      isValid = false;
    }
    if (time === '') {
      setTimeError('참여 가능 시간을 선택해주세요.');
      isValid = false;
    }

    return isValid;
  };

  const handleSubmit = async () => {
    if (!projectId) {
      alert("프로젝트 ID를 찾을 수 없습니다.");
      return;
    }

    if (validateForm()) {
      try {
        const response = await apiClient.post(`/projects/${projectId}/apply/`, {
          role,
          motivation,
          available_time: time,
        });
        alert(response.data.message || "지원서가 성공적으로 제출되었습니다.");
        setApplicationComplete(true);
        console.log('Application Submitted:', { role, motivation, time });
      } catch (error: any) {
        alert(error.response?.data?.message || "지원서 제출 중 오류가 발생했습니다.");
        console.error("Application submission error:", error);
      }
    }
  };

  if (applicationComplete) {
    return (
      <div className="container mx-auto p-4">
        <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md text-center">
          <h1 className="text-3xl font-bold text-blue-600 mb-4">지원 완료!</h1>
          <p className="text-gray-700">프로젝트 지원이 성공적으로 완료되었습니다.</p>
          <button onClick={() => navigate(-1)} className="mt-6 inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            이전 페이지로 돌아가기
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow-md">
        <Link to="/projects" className="text-gray-600 hover:text-gray-800 flex items-center mb-6">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          프로젝트로 돌아가기
        </Link>

        <h1 className="text-2xl font-bold mb-4">프로젝트 지원서</h1>
        <div className="w-full bg-gray-200 rounded-full h-2.5 mb-6">
          <div className="bg-blue-600 h-2.5 rounded-full" ></div>
        </div>
        <div className="mb-8">
          <h2 className="text-xl font-semibold mb-4">기본 정보</h2>
          <p className="text-gray-600 mb-4">지원하고자 하는 역할과 동기를 작성해주세요</p>

          <div className="mb-4">
            <label htmlFor="role" className="block text-gray-700 text-sm font-bold mb-2">지원 역할</label>
            <input
              type="text"
              id="role"
              className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${roleError ? 'border-red-500' : ''}`}
              placeholder="지원하고자 하는 역할을 입력하세요"
              value={role}
              onChange={(e) => setRole(e.target.value)}
            />
            {roleError && <p className="text-red-500 text-xs italic mt-1">{roleError}</p>}
          </div>

          <div className="mb-4">
            <label htmlFor="motivation" className="block text-gray-700 text-sm font-bold mb-2">지원 동기</label>
            <textarea
              id="motivation"
              rows={5}
              className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${motivationError ? 'border-red-500' : ''}`}
              placeholder="이 프로젝트에 지원하는 이유와 동기를 자세히 작성해주세요"
              value={motivation}
              onChange={(e) => setMotivation(e.target.value)}
            ></textarea>
            <p className="text-xs text-gray-500 mt-1">프로젝트에 대한 관심과 참여 의지를 구체적으로 표현해주세요</p>
            {motivationError && <p className="text-red-500 text-xs italic mt-1">{motivationError}</p>}
          </div>

          <div className="mb-4">
            <label htmlFor="time" className="block text-gray-700 text-sm font-bold mb-2">참여 가능 시간</label>
            <select
              id="time"
              className={`shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline ${timeError ? 'border-red-500' : ''}`}
              value={time}
              onChange={(e) => setTime(e.target.value)}
            >
              <option value="">주당 참여 가능한 시간을 선택하세요</option>
              <option value="1-5">주 1-5시간</option>
              <option value="5-10">주 5-10시간</option>
              <option value="10-15">주 10-15시간</option>
              <option value="15-20">주 15-20시간</option>
              <option value="20+">주 20시간 이상</option>
            </select>
            {timeError && <p className="text-red-500 text-xs italic mt-1">{timeError}</p>}
          </div>
        </div>

        <div className="flex justify-between">
          <button className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
            취소
          </button>
          <button onClick={handleSubmit} className="bg-black hover:bg-gray-800 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
            지원하기
          </button>
        </div>
      </div>
    </div>
  );
};

export default ApplicationFormPage;
