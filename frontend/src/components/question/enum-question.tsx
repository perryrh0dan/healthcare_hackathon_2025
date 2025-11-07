import type { IEnumQuestion } from "@/views/DailyQuestions"
import { Button } from "../ui/button"
import { useState } from "react"

type EnumQuestionProps = {
  value?: string | number
  options: IEnumQuestion['options']
  onChange: (value: string) => void
}

const EnumQuestion = ({ value, options, onChange }: EnumQuestionProps) => {
  const [active, setActive] = useState<string>(value?.toString() ?? '')

  const handleClick = (value: string) => {
    setActive(value)
    onChange(value)
  }

  return (
    <div className="flex flex-col h-full gap-2">
      {options.map((option, idx) => (
        <Button autoFocus={idx === 0} onClick={() => handleClick(option.value)} className="w-full" variant={active === option.value ? 'default' : 'outline'}>
          {option.label}
        </Button>
      ))}
    </div>
  )

}

export default EnumQuestion
