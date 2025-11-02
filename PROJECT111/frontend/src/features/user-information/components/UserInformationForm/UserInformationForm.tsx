import { useForm, FormProvider } from "react-hook-form";
import { yupResolver } from "@hookform/resolvers/yup";
import * as yup from "yup";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../../../../shared/components/Button";
import { BasicInfoSection } from "./BasicInfoSection";
import { TechnicalSkillsSection } from "./TechnicalSkillsSection";
import { CollaborationSection } from "./CollaborationSection";
import { ProjectPreferencesSection } from "./ProjectPreferencesSection";
import type { UserInformation } from "../../model/userInformationTypes";

const schema = yup.object().shape({
  // 기본 정보 - 활동 가능 지역만 필수
  activityRegions: yup.array().min(1, "활동 가능 지역을 하나 이상 선택해주세요.").required("활동 가능 지역을 선택해주세요."),
  githubUrl: yup.string().url("올바른 URL 형식이 아닙니다.").optional(),
  portfolioUrl: yup.string().url("올바른 URL 형식이 아닙니다.").optional(),
  introduction: yup.string().max(150, "150자 이내로 작성해주세요.").optional(),
  
  // 기술 역량 및 경험 - 모두 선택
  major: yup.string().nullable().optional(),
  expertise: yup.array().optional(),
  techStack: yup.array().optional(),
  collaborationTools: yup.array().optional(),
  sideProjectExperience: yup.string().nullable().optional(),
  
  // 협업 성향 및 방식 - 모두 선택
  collaborationStyle: yup.string().nullable().optional(),
  meetingFrequency: yup.string().nullable().optional(),
  belbinRole: yup.string().nullable().optional(),
  
  // 프로젝트 관련 선호도 - 모두 선택
  preferredTeamSize: yup.string().nullable().optional(),
  preferredProjectTopics: yup.array().optional(),
  availablePeriod: yup.string().nullable().optional(),
});

const sections = [
  { id: "basic", title: "기본 정보", component: BasicInfoSection },
  { id: "technical", title: "기술 역량", component: TechnicalSkillsSection },
  { id: "collaboration", title: "협업 성향", component: CollaborationSection },
  { id: "preferences", title: "프로젝트 선호도", component: ProjectPreferencesSection },
];

export function UserInformationForm() {
  const [currentSection, setCurrentSection] = useState(0);
  const navigate = useNavigate();
  
  const methods = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      activityRegions: [],
      expertise: [],
      techStack: [],
      collaborationTools: [],
      preferredProjectTopics: [],
      preferredTeamSize: null,
      availablePeriod: null,
      belbinRole: null,
      collaborationStyle: null,
      meetingFrequency: null,
      sideProjectExperience: null,
    },
  });

  const { handleSubmit, trigger } = methods;

  const onSubmit = async (data: any) => {
    console.log("User Information Data:", data);
    // TODO: 프로필 저장 API 호출
    navigate("/");
  };

  const handleNext = async () => {
    const currentSectionFields = getSectionFields(currentSection);
    const isValid = await trigger(currentSectionFields);
    
    if (isValid) {
      if (currentSection < sections.length - 1) {
        setCurrentSection(currentSection + 1);
      } else {
        handleSubmit(onSubmit)();
      }
    }
  };

  const handlePrevious = () => {
    if (currentSection > 0) {
      setCurrentSection(currentSection - 1);
    }
  };

  const getSectionFields = (sectionIndex: number): (keyof UserInformation)[] => {
    switch (sectionIndex) {
      case 0: // 기본 정보
        return ["activityRegions"];
      case 1: // 기술 역량
        return [];
      case 2: // 협업 성향
        return [];
      case 3: // 프로젝트 선호도
        return [];
      default:
        return [];
    }
  };

  const CurrentSectionComponent = sections[currentSection].component;

  return (
    <div className="h-full flex flex-col">
      <div className="mb-4">
        <h3 className="text-lg font-semibold mb-1">
          {`유저 정보 입력 > ${sections[currentSection].title} (${currentSection + 1} / ${sections.length})`}
        </h3>
        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-3">
          <div 
            className="bg-primary h-1.5 rounded-full transition-all duration-300"
            style={{ width: `${((currentSection + 1) / sections.length) * 100}%` }}
          />
        </div>
      </div>

      <div className="flex-1 overflow-hidden">
        <FormProvider {...methods}>
          <CurrentSectionComponent />
        </FormProvider>
      </div>

      <div className="flex justify-between gap-4 pt-4">
        <Button 
          variant="outline" 
          size="lg" 
          onClick={handlePrevious}
          disabled={currentSection === 0}
        >
          이전
        </Button>
        
        <Button 
          size="lg" 
          onClick={handleNext}
        >
          {currentSection === sections.length - 1 ? "완료" : "다음"}
        </Button>
      </div>
    </div>
  );
} 