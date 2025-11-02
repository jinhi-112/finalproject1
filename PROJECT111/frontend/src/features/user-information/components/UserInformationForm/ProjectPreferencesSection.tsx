import { useFormContext } from "react-hook-form";
import { Card, CardContent } from "../../../../shared/components/Card";
import { Checkbox } from "../../../../shared/components/Checkbox";
import { FormField } from "../../../../shared/components/FormField";
import { Radio } from "../../../../shared/components/Radio";
import {
  AVAILABLE_PERIODS,
  PREFERRED_PROJECT_TOPICS,
  PREFERRED_TEAM_SIZES
} from "../../model/userInformationTypes";

export function ProjectPreferencesSection() {
  const { register, watch, setValue, formState: { errors } } = useFormContext();
  const preferredProjectTopics = watch("preferredProjectTopics") || [];

  const handleProjectTopicsChange = (topic: string, checked: boolean) => {
    if (checked) {
      setValue("preferredProjectTopics", [...preferredProjectTopics, topic]);
    } else {
      setValue("preferredProjectTopics", preferredProjectTopics.filter((t: string) => t !== topic));
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardContent className="flex-1 space-y-4 overflow-y-auto">
        <FormField label="희망하는 팀원 수" error={errors.preferredTeamSize?.message as string}>
          <div className="grid grid-cols-2 gap-3 mt-3">
            {PREFERRED_TEAM_SIZES.map((size) => (
              <Radio
                key={size.id}
                label={size.label}
                value={size.id}
                {...register("preferredTeamSize")}
              />
            ))}
          </div>
        </FormField>

        <FormField label="선호하는 프로젝트 주제" error={errors.preferredProjectTopics?.message as string}>
          <div className="grid grid-cols-2 gap-3 mt-3">
            {PREFERRED_PROJECT_TOPICS.map((topic) => (
              <Checkbox
                key={topic.id}
                label={topic.label}
                checked={preferredProjectTopics.includes(topic.id)}
                onChange={(e) => handleProjectTopicsChange(topic.id, e.target.checked)}
              />
            ))}
          </div>
        </FormField>

        <FormField label="참여 가능 기간" error={errors.availablePeriod?.message as string}>
          <div className="grid grid-cols-2 gap-3 mt-3">
            {AVAILABLE_PERIODS.map((period) => (
              <Radio
                key={period.id}
                label={period.label}
                value={period.id}
                {...register("availablePeriod")}
              />
            ))}
          </div>
        </FormField>
      </CardContent>
    </Card>
  );
} 