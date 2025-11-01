import { useEffect, useRef, useState } from 'react';
import apiClient from '@/api';
import type { Project } from '../types/project';

export const useScorePoller = (initialProjects: Project[], onUpdate: (updatedProject: Project) => void) => {
  const [pollingIds, setPollingIds] = useState<Set<number>>(new Set());
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  // 1. Identify projects that need polling when the initial list changes
  useEffect(() => {
    const newPollingIds = new Set<number>();
    for (const project of initialProjects) {
      if (project.user_matching_rate === 0 || project.user_matching_rate === null) {
        newPollingIds.add(project.project_id);
      }
    }
    setPollingIds(newPollingIds);
  }, [initialProjects]);

  // 2. Start or stop the polling interval based on the polling list
  useEffect(() => {
    // Stop any existing interval when pollingIds change
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }

    // If there are projects to poll, start a new interval
    if (pollingIds.size > 0) {
      intervalRef.current = setInterval(async () => {
        console.log(`Polling for scores for projects: ${[...pollingIds].join(', ')}`);
        const currentIds = Array.from(pollingIds);

        for (const id of currentIds) {
          try {
            const response = await apiClient.get<Project>(`/projects/${id}/`);
            const updatedProject = response.data;

            // If the score is now calculated (not 0 or null), update the state
            if (updatedProject.user_matching_rate && updatedProject.user_matching_rate > 0) {
              onUpdate(updatedProject);
              // Remove from polling list
              setPollingIds(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(id);
                  return newSet;
              });
            }
          } catch (error) {
            console.error(`Failed to poll for project ${id}:`, error);
            // Optional: Stop polling for this ID if it fails consistently
            setPollingIds(prev => {
                const newSet = new Set(prev);
                newSet.delete(id);
                return newSet;
            });
          }
        }
      }, 5000); // Poll every 5 seconds
    }

    // Cleanup function to clear interval when the component unmounts
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [pollingIds, onUpdate]);
};
