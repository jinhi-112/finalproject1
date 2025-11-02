import * as React from "react";
import { ErrorMessage } from "../../features/auth/components/ErrorMessage";
import { cn } from "../utils/cn";
import { Label } from "./Label";

interface FormFieldProps {
  label?: string;
  htmlFor?: string;
  error?: string;
  className?: string;
  children?: React.ReactNode;
}

function FormField({ 
  label, 
  htmlFor, 
  error, 
  className,
  children 
}: FormFieldProps) {
  return (
    <div className={cn("flex flex-col gap-2", className)}>
      {label && (
        <Label htmlFor={htmlFor} className="text-sm font-medium">
          {label}
        </Label>
      )}
      {children}
      {error && <ErrorMessage>{error}</ErrorMessage>}
    </div>
  );
}

export { FormField };
