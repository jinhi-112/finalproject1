import { useFormContext } from "react-hook-form";
import { Card, CardContent } from "../../../../shared/components/Card";
import { Checkbox } from "../../../../shared/components/Checkbox";
import { FormField } from "../../../../shared/components/FormField";
import { Input } from "../../../../shared/components/Input";
import { ACTIVITY_REGIONS } from "../../model/userInformationTypes";

export function BasicInfoSection() {
  const { register, watch, setValue, formState: { errors } } = useFormContext();
  const activityRegions = watch("activityRegions") || [];

  const handleRegionChange = (region: string, checked: boolean) => {
    if (checked) {
      setValue("activityRegions", [...activityRegions, region]);
    } else {
      setValue("activityRegions", activityRegions.filter((r: string) => r !== region));
    }
  };

  return (
    <Card className="h-full flex flex-col">
      <CardContent className="flex-1 space-y-3 overflow-y-auto">
        <FormField label="활동 가능 지역" error={errors.activityRegions?.message as string}>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
            {ACTIVITY_REGIONS.map((region) => (
              <Checkbox
                key={region.id}
                label={region.label}
                checked={activityRegions.includes(region.id)}
                onChange={(e) => handleRegionChange(region.id, e.target.checked)}
              />
            ))}
          </div>
        </FormField>
        <FormField label="깃허브 주소" error={errors.githubUrl?.message as string}>
          <Input
            {...register("githubUrl")}
            placeholder="https://github.com/username" 
            type="url"
          />
        </FormField>
        <FormField label="포트폴리오 주소" error={errors.portfolioUrl?.message as string}>
          <Input
            {...register("portfolioUrl")}
            placeholder="https://your-portfolio.com"
            type="url"
          />
        </FormField>
        <FormField label="자기소개" error={errors.introduction?.message as string}>
          <textarea
            {...register("introduction")}
            placeholder="자신에 대한 간단한 소개를 작성해주세요 (150자 이내)"
            maxLength={150}
            className="w-full min-h-[100px] rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-sm transition-colors placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
          />
          <div className="text-xs text-muted-foreground mt-1 text-right">
            {watch("introduction")?.length || 0}/150
          </div>
        </FormField>
      </CardContent>
    </Card>
  );
} 