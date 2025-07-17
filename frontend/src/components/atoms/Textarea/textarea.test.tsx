import { Textarea, TextareaProps } from "./textarea";
import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import React from "react";

const baseProps: TextareaProps = {
  name: "test-textarea",
  value: "",
  onChange: vi.fn(),
};

describe("Textarea", () => {
  it("renders label if provided", () => {
    render(<Textarea {...baseProps} label="Test Label" />);
    expect(screen.getByText("Test Label")).toBeInTheDocument();
  });

  it("does not render label if not provided", () => {
    render(<Textarea {...baseProps} />);
    expect(screen.queryByText("Test Label")).not.toBeInTheDocument();
  });

  it("renders value", () => {
    render(<Textarea {...baseProps} value="Hello" />);
    expect(screen.getByDisplayValue("Hello")).toBeInTheDocument();
  });

  it("calls onChange when value changes", () => {
    const onChange = vi.fn();
    render(<Textarea {...baseProps} onChange={onChange} />);
    const textarea = screen.getByRole("textbox");
    fireEvent.change(textarea, { target: { value: "abc" } });
    expect(onChange).toHaveBeenCalled();
  });

  it("calls onBlur when blurred", () => {
    const onBlur = vi.fn();
    render(<Textarea {...baseProps} onBlur={onBlur} />);
    const textarea = screen.getByRole("textbox");
    fireEvent.blur(textarea);
    expect(onBlur).toHaveBeenCalled();
  });

  it("shows placeholder if provided", () => {
    render(<Textarea {...baseProps} placeholder="Type here..." />);
    expect(screen.getByPlaceholderText("Type here...")).toBeInTheDocument();
  });

  it("shows error message if error prop is provided", () => {
    render(<Textarea {...baseProps} error="Error!" />);
    expect(screen.getByText("Error!")).toBeInTheDocument();
  });

  it("applies custom className", () => {
    render(<Textarea {...baseProps} className="custom-class" />);
    const wrapper = screen.getByRole("textbox").parentElement;
    expect(wrapper?.className).toContain("custom-class");
  });

  it("sets rows prop", () => {
    render(<Textarea {...baseProps} rows={5} />);
    const textarea = screen.getByRole("textbox");
    expect(textarea).toHaveAttribute("rows", "5");
  });
});
