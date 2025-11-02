import { useFormContext } from "react-hook-form";
import { Card, CardContent } from "../../../../shared/components/Card";
import { FormField } from "../../../../shared/components/FormField";
import { Radio } from "../../../../shared/components/Radio";
import {
  BELBIN_ROLES,
  COLLABORATION_STYLES,
  MEETING_FREQUENCIES
} from "../../model/userInformationTypes";

export function CollaborationSection() {
  const { register, watch, formState: { errors } } = useFormContext();
  const selectedBelbinRole = watch("belbinRole");

  return (
    <Card className="h-full flex flex-col">
      <CardContent className="flex-1 space-y-4 overflow-y-auto">
        <FormField label="선호하는 협업 방식" error={errors.collaborationStyle?.message as string}>
          <div className="grid grid-cols-3 gap-3 mt-3">
            {COLLABORATION_STYLES.map((style) => (
              <Radio
                key={style.id}
                label={style.label}
                value={style.id}
                {...register("collaborationStyle")}
              />
            ))}
          </div>
        </FormField>

        <FormField label="가능한 미팅 빈도 (주 단위)" error={errors.meetingFrequency?.message as string}>
          <div className="grid grid-cols-2 gap-3 mt-3">
            {MEETING_FREQUENCIES.map((frequency) => (
              <Radio
                key={frequency.id}
                label={frequency.label}
                value={frequency.id}
                {...register("meetingFrequency")}
              />
            ))}
          </div>
        </FormField>

        <FormField label="벨빈 팀 역할 유형" error={errors.belbinRole?.message as string}>
          <div className="space-y-3 mt-3">
            {BELBIN_ROLES.map((role) => (
              <div key={role.id} className="border rounded-lg p-3">
                <Radio
                  label={role.label}
                  value={role.id}
                  description={role.description}
                  {...register("belbinRole")}
                />
              </div>
            ))}
          </div>
          {selectedBelbinRole && (
            <div className="mt-3 p-3 bg-muted rounded-lg">
              <p className="text-sm font-medium">선택된 역할 설명:</p>
              <p className="text-sm text-muted-foreground mt-1">
                {BELBIN_ROLES.find(role => role.id === selectedBelbinRole)?.description}
              </p>
            </div>
          )}
        </FormField>
      </CardContent>
    </Card>
  );
} 