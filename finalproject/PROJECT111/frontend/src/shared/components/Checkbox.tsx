import * as React from "react"
import { cn } from "../utils/cn"

interface CheckboxProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  description?: string;
}

function Checkbox({ className, label, description, ...props }: CheckboxProps) {
  return (
    <div className="flex items-start space-x-2">
      <input
        type="checkbox"
        className={cn(
          "h-4 w-4 rounded border border-input bg-background text-primary transition-colors",
          "focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring",
          "disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        {...props}
      />
      {(label || description) && (
        <div className="grid gap-1.5 leading-none">
          {label && (
            <label className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              {label}
            </label>
          )}
          {description && (
            <p className="text-sm text-muted-foreground">{description}</p>
          )}
        </div>
      )}
    </div>
  )
}

export { Checkbox } 