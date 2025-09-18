import React from "react";

interface FormattedTextProps {
  text: string;
}

export const formatText = (text: string): React.ReactNode[] => {
  if (!text) return [];

  const paragraphs = text.split("\n\n");

  return paragraphs
    .map((paragraph, paragraphIndex) => {
      if (!paragraph.trim()) return null;

      const headingMatch = paragraph.trim().match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const headingText = headingMatch[2];

        const headingProps = {
          key: paragraphIndex,
          className: `font-bold text-gray-900 mb-3 mt-4 first:mt-0 ${
            level === 1
              ? "text-2xl"
              : level === 2
              ? "text-xl"
              : level === 3
              ? "text-lg"
              : level === 4
              ? "text-base"
              : level === 5
              ? "text-sm"
              : "text-xs"
          }`,
        };

        switch (level) {
          case 1:
            return <h1 {...headingProps}>{formatInlineText(headingText)}</h1>;
          case 2:
            return <h2 {...headingProps}>{formatInlineText(headingText)}</h2>;
          case 3:
            return <h3 {...headingProps}>{formatInlineText(headingText)}</h3>;
          case 4:
            return <h4 {...headingProps}>{formatInlineText(headingText)}</h4>;
          case 5:
            return <h5 {...headingProps}>{formatInlineText(headingText)}</h5>;
          case 6:
          default:
            return <h6 {...headingProps}>{formatInlineText(headingText)}</h6>;
        }
      }

      if (/^\d+\.\s/.test(paragraph.trim())) {
        return (
          <div key={paragraphIndex} className="mb-4">
            {formatList(paragraph, "numbered")}
          </div>
        );
      }

      if (/^[-*•]\s/.test(paragraph.trim())) {
        return (
          <div key={paragraphIndex} className="mb-4">
            {formatList(paragraph, "bullet")}
          </div>
        );
      }

      return (
        <div key={paragraphIndex} className="mb-4 last:mb-0">
          {formatInlineText(paragraph)}
        </div>
      );
    })
    .filter(Boolean);
};

const formatList = (
  text: string,
  type: "numbered" | "bullet"
): React.ReactNode => {
  const lines = text.split("\n");

  return (
    <ul
      className={
        type === "numbered"
          ? "list-decimal list-inside"
          : "list-disc list-inside"
      }
    >
      {lines.map((line, index) => {
        if (!line.trim()) return null;

        const cleanLine = line.replace(/^(\d+\.\s|[-*•]\s)/, "");

        return (
          <li key={index} className="mb-2 ml-4">
            {formatInlineText(cleanLine)}
          </li>
        );
      })}
    </ul>
  );
};

const formatInlineText = (text: string): React.ReactNode => {
  const lines = text.split("\n");

  return lines.map((line, lineIndex) => {
    if (!line.trim()) {
      return <br key={lineIndex} />;
    }

    const parts = line.split(/(\*\*.*?\*\*|\*.*?\*)/g);

    return (
      <span key={lineIndex}>
        {parts.map((part, partIndex) => {
          if (part.startsWith("**") && part.endsWith("**")) {
            return (
              <strong key={partIndex} className="font-semibold">
                {part.slice(2, -2)}
              </strong>
            );
          } else if (
            part.startsWith("*") &&
            part.endsWith("*") &&
            part.length > 2
          ) {
            return (
              <em key={partIndex} className="italic">
                {part.slice(1, -1)}
              </em>
            );
          } else {
            return part;
          }
        })}
        {lineIndex < lines.length - 1 && <br />}
      </span>
    );
  });
};

/**
 * React component that renders formatted text
 */
export const FormattedText: React.FC<FormattedTextProps> = ({ text }) => {
  return <div className="text-sm leading-relaxed">{formatText(text)}</div>;
};
