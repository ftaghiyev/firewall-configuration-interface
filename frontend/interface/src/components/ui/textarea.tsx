import * as React from "react"

import { cn } from "@/lib/utils"

const Textarea = React.forwardRef<HTMLTextAreaElement, React.ComponentProps<"textarea">>(
  ({ className, onChange, ...props }, ref) => {
    const textareaRef = React.useRef<HTMLTextAreaElement | null>(null)

    React.useImperativeHandle(ref, () => textareaRef.current!)

    const adjustHeight = () => {
      const textarea = textareaRef.current
      if (textarea) {
        textarea.style.height = "auto"
        textarea.style.height = `${textarea.scrollHeight}px`
      }
    }

    React.useEffect(() => {
      adjustHeight()
    }, [props.value, props.defaultValue])

    return (
      <textarea
        data-slot="textarea"
        ref={textareaRef}
        className={cn(
          "border-input placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-ring/50 aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive dark:bg-input/30 flex min-h-16 w-full rounded-md border bg-transparent px-3 py-2 text-base shadow-xs transition-[color,box-shadow] outline-none focus-visible:ring-[3px] disabled:cursor-not-allowed disabled:opacity-50 md:text-sm resize-y",
          className
        )}
        onChange={(e) => {
          adjustHeight()
          onChange?.(e)
        }}
        {...props}
      />
    )
  }
)
Textarea.displayName = "Textarea"

export { Textarea }
