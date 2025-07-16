import React from "react";

export interface CheckboxProps {
  name: string;
  label: string;
  checked: boolean;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onBlur?: (e: React.FocusEvent<HTMLInputElement>) => void;
  error?: string;
  className?: string;
  spanText?: string;
}

export const Checkbox: React.FC<CheckboxProps> = ({
  name,
  label,
  checked,
  onChange,
  onBlur,
  error,
  className = "",
  spanText,
}) => (
  <label className={`flex items-center cursor-pointer ${className}`}>
    {spanText && <span className="mr-2 text-sm">{spanText}</span>}
    <input
      type="checkbox"
      name={name}
      checked={checked}
      onChange={onChange}
      onBlur={onBlur}
      className="sr-only peer"
    />
    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:bg-blue-500 transition-colors duration-200 relative">
      <div
        className={`absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform duration-200 ${
          checked ? "translate-x-5" : ""
        }`}
      ></div>
    </div>
    <span className="ml-2 text-sm">{label}</span>
    {error && <div className="text-red-500 text-xs ml-2">{error}</div>}
  </label>
);
