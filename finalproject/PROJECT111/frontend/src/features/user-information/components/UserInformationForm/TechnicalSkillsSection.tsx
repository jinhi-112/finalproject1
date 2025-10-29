import { useFormContext } from "react-hook-form";
import { Card, CardContent } from "../../../../shared/components/Card";
import { Checkbox } from "../../../../shared/components/Checkbox";
import { FormField } from "../../../../shared/components/FormField";
import { Radio } from "../../../../shared/components/Radio";
import {
  COLLABORATION_TOOLS,
  EXPERTISE_AREAS,
  MAJORS,
  SIDE_PROJECT_EXPERIENCE,
  TECH_STACKS
} from "../../model/userInformationTypes";

export function TechnicalSkillsSection() {
  const { register, watch, setValue, formState: { errors } } = useFormContext();
  const expertise = watch("expertise") || [];
  const techStack = watch("techStack") || [];
  const collaborationTools = watch("collaborationTools") || [];

  const handleMultiSelect = (field: string, value: string, checked: boolean) => {
    const currentValues = watch(field) || [];
    if (checked) {
      setValue(field, [...currentValues, value]);
    } else {
      setValue(field, currentValues.filter((v: string) => v !== value));
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardContent className="flex-1 space-y-4 overflow-y-auto">
        <FormField label="전공 또는 주요 학습 분야" error={errors.major?.message as string}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {MAJORS.map((major) => (
              <Radio
                key={major.id}
                label={major.label}
                value={major.id}
                {...register("major")}
              />
            ))}
          </div>
        </FormField>

        <FormField label="가장 자신 있는 분야 (1~2개 선택)" error={errors.expertise?.message as string}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {EXPERTISE_AREAS.map((area) => (
              <Checkbox
                key={area.id}
                label={area.label}
                checked={expertise.includes(area.id)}
                onChange={(e) => handleMultiSelect("expertise", area.id, e.target.checked)}
              />
            ))}
          </div>
        </FormField>

        <FormField label="사용 가능한 기술 스택" error={errors.techStack?.message as string}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {TECH_STACKS.map((tech) => (
              <Checkbox
                key={tech.id}
                label={tech.label}
                checked={techStack.includes(tech.id)}
                onChange={(e) => handleMultiSelect("techStack", tech.id, e.target.checked)}
               />
            ))}
          </div>
        </FormField>

        <FormField label="협업 툴 사용 경험" error={errors.collaborationTools?.message as string}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {COLLABORATION_TOOLS.map((tool) => (
              <Checkbox
                key={tool.id}
                label={tool.label}
                checked={collaborationTools.includes(tool.id)}
                onChange={(e) => handleMultiSelect("collaborationTools", tool.id, e.target.checked)}
              />
            ))}
          </div>
        </FormField>

        <FormField label="사이드 프로젝트 참여 경험" error={errors.sideProjectExperience?.message as string}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {SIDE_PROJECT_EXPERIENCE.map((experience) => (
              <Radio
                key={experience.id}
                label={experience.label}
                value={experience.id}
                {...register("sideProjectExperience")}
              />
            ))}
          </div>
        </FormField>
      </CardContent>
    </Card>
  );
} 