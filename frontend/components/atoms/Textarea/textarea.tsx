import React from "react";

export interface TextareaProps {
  name: string;
  label?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLTextAreaElement>) => void;
  placeholder?: string;
  error?: string;
  className?: string;
  rows?: number;
}

export const Textarea: React.FC<TextareaProps> = ({
  name,
  label,
  value,
  onChange,
  onBlur,
  placeholder,
  error,
  className = "",
  rows = 2,
}) => (
  <div className={className}>
    {label && (
      <label htmlFor={name} className="block mb-1 text-sm font-medium">
        {label}
      </label>
    )}
    <textarea
      id={name}
      name={name}
      value={value}
      onChange={onChange}
      onBlur={onBlur}
      placeholder={placeholder}
      className="flex-1 p-2 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
      rows={rows}
    />
    {error && <div className="text-red-500 text-xs mt-1">{error}</div>}
  </div>
);
