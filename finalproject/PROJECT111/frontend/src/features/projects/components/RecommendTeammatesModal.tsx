import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { proposeToProject } from '../../../api'; // Import the new API function

// Define types for clarity
interface User {
  user_id: number;
  name: string;
  email: string;
  specialty?: string[];
  introduction?: string;
}

interface Recommendation {
  user: User;
  score: number;
}

interface RecommendTeammatesModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendations: Recommendation[];
  isLoading: boolean;
  projectName: string;
  projectId: number | null; // Add projectId prop
}

export const RecommendTeammatesModal: React.FC<RecommendTeammatesModalProps> = ({
  isOpen,
  onClose,
  recommendations,
  isLoading,
  projectName,
  projectId, // Destructure projectId
}) => {
  const [proposedUserIds, setProposedUserIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    // Reset proposed state when recommendations change (e.g., new project selected)
    setProposedUserIds(new Set());
  }, [recommendations]);

  const handlePropose = async (userId: number) => {
    if (!projectId) return;

    try {
      await proposeToProject(projectId, userId);
      setProposedUserIds(prev => new Set(prev).add(userId));
      // Optionally, show a success toast/message
    } catch (error) {
      console.error("Failed to send proposal", error);
      // Optionally, show an error toast/message
      alert("제안을 보내는 데 실패했습니다. 이미 제안했거나, 오류가 발생했습니다.");
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-center items-center p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="p-6 border-b flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">
            '{projectName}' 프로젝트 추천 팀원
          </h2>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-gray-100">
            <X size={24} className="text-gray-600" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto">
          {isLoading ? (
            <div className="text-center py-10">
              <p className="text-gray-600">AI가 최적의 팀원을 찾고 있습니다...</p>
            </div>
          ) : recommendations.length === 0 ? (
            <div className="text-center py-10 text-gray-500">
              <p>추천할 만한 팀원을 찾지 못했습니다.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {recommendations.map((rec, index) => {
                const isProposed = proposedUserIds.has(rec.user.user_id);
                return (
                  <div key={rec.user.user_id} className="border rounded-lg p-5 transition hover:shadow-md hover:border-indigo-300">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm text-indigo-600 font-semibold">#{index + 1} 추천</p>
                        <h3 className="text-xl font-bold mt-1 text-gray-900">{rec.user.name}</h3>
                        <p className="text-sm text-gray-500">{rec.user.email}</p>
                        {rec.user.specialty && rec.user.specialty.length > 0 && (
                          <div className="mt-3 flex flex-wrap gap-2">
                            {rec.user.specialty.map(s => (
                              <span key={s} className="bg-gray-100 text-gray-800 text-xs font-medium px-2.5 py-1 rounded-full">{s}</span>
                            ))}
                          </div>
                        )}
                      </div>
                      <div className="text-center flex-shrink-0 ml-4">
                        <p className="text-3xl font-bold text-green-600">{Math.round(rec.score)}점</p>
                        <p className="text-sm text-gray-500">매칭 점수</p>
                      </div>
                    </div>
                    {rec.user.introduction && (
                       <p className="text-sm text-gray-700 mt-4 pt-4 border-t">{rec.user.introduction}</p>
                    )}
                    <div className="mt-4 flex justify-end">
                      <button
                        onClick={() => handlePropose(rec.user.user_id)}
                        disabled={isProposed}
                        className={`px-4 py-2 text-sm font-semibold rounded-md transition-colors duration-200 ${
                          isProposed
                            ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                            : 'bg-indigo-600 text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
                        }`}
                      >
                        {isProposed ? '제안 완료' : '프로젝트 참여 제안하기'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-gray-50 border-t text-right rounded-b-lg">
          <button 
            onClick={onClose}
            className="px-6 py-2 bg-gray-700 text-white font-semibold rounded-lg hover:bg-gray-800 transition-colors duration-200"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};