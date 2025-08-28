import { File, FileText, Table, Upload, X } from "lucide-react";
import React, { useState } from "react";

import { Dialog } from "@headlessui/react";
import type { FileAttachment } from "../../types";
import { postDocuments } from "../../services/documentsService";

interface FileAttachmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAttach: (files: FileAttachment[]) => void;
  currentFiles: FileAttachment[];
}

const fileTypeConfig = {
  pdf: {
    icon: File,
    color: "text-red-600",
    bgColor: "bg-red-50",
    label: "PDF Documents",
  },
  docx: {
    icon: FileText,
    color: "text-blue-600",
    bgColor: "bg-blue-50",
    label: "Word Documents",
  },
  xlsx: {
    icon: Table,
    color: "text-green-600",
    bgColor: "bg-green-50",
    label: "Excel Spreadsheets",
  },
};

const acceptedFormats = {
  pdf: ".pdf",
  docx: ".doc,.docx",
  xlsx: ".xls,.xlsx",
};

export const FileAttachmentModal: React.FC<FileAttachmentModalProps> = ({
  isOpen,
  onClose,
  onAttach,
  currentFiles,
}) => {
  const [selectedFileType, setSelectedFileType] = useState<
    "pdf" | "docx" | "xlsx"
  >("pdf");
  const [dragActive, setDragActive] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleFileSelect = async (files: FileList | null) => {
    if (!files) return;

    const newFiles: FileAttachment[] = [];

    Array.from(files).forEach((file) => {
      const extension = file.name.split(".").pop()?.toLowerCase();
      let fileType: "pdf" | "docx" | "xlsx" | null = null;

      if (extension === "pdf") fileType = "pdf";
      else if (extension === "doc" || extension === "docx") fileType = "docx";
      else if (extension === "xls" || extension === "xlsx") fileType = "xlsx";

      if (fileType) {
        newFiles.push({
          name: file.name,
          type: fileType,
          size: file.size,
          file,
        });
      }
    });

    const updatedFiles = [...currentFiles, ...newFiles];
    onAttach(updatedFiles);

    try {
      setUploadError(null);
      setIsUploading(true);
      await postDocuments(updatedFiles.map((f) => f.file));
    } catch {
      setUploadError("Failed to upload files. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const removeFile = (index: number) => {
    const newFiles = currentFiles.filter((_, i) => i !== index);
    onAttach(newFiles);
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/30 backdrop-blur-sm"
        aria-hidden="true"
      />

      {/* Dialog */}
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="w-full max-w-md bg-white rounded-xl shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <Dialog.Title className="text-lg font-semibold text-gray-900">
              Attach Files
            </Dialog.Title>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* File Type Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Select File Type
              </label>
              <div className="grid grid-cols-1 gap-2">
                {Object.entries(fileTypeConfig).map(([type, config]) => {
                  const IconComponent = config.icon;
                  return (
                    <button
                      key={type}
                      type="button"
                      onClick={() =>
                        setSelectedFileType(type as keyof typeof fileTypeConfig)
                      }
                      className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-200 ${
                        selectedFileType === type
                          ? `border-blue-300 ${config.bgColor} ring-2 ring-blue-500 ring-opacity-20`
                          : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                      }`}
                    >
                      <IconComponent
                        className={`w-5 h-5 ${
                          selectedFileType === type
                            ? config.color
                            : "text-gray-400"
                        }`}
                      />
                      <span
                        className={`text-sm font-medium ${
                          selectedFileType === type
                            ? "text-gray-900"
                            : "text-gray-600"
                        }`}
                      >
                        {config.label}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* File Upload Area */}
            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
                dragActive
                  ? "border-blue-400 bg-blue-50"
                  : "border-gray-300 hover:border-gray-400 hover:bg-gray-50"
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
              <p className="text-sm text-gray-600 mb-2">
                Drag and drop your files here, or{" "}
                <label className="text-blue-600 hover:text-blue-700 cursor-pointer font-medium">
                  browse
                  <input
                    type="file"
                    multiple
                    accept={acceptedFormats[selectedFileType]}
                    onChange={(e) => handleFileSelect(e.target.files)}
                    className="hidden"
                  />
                </label>
              </p>
              <p className="text-xs text-gray-500">
                Supports {fileTypeConfig[selectedFileType].label.toLowerCase()}
              </p>
            </div>

            {/* Current Files */}
            {currentFiles.length > 0 && (
              <div className="mt-6">
                <h4 className="text-sm font-medium text-gray-700 mb-3">
                  Selected Files ({currentFiles.length})
                </h4>
                <div className="space-y-2">
                  {currentFiles.map((file, index) => {
                    const config = fileTypeConfig[file.type];
                    const IconComponent = config.icon;

                    return (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <IconComponent
                            className={`w-4 h-4 ${config.color}`}
                          />
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {file.name}
                            </p>
                            <p className="text-xs text-gray-500">
                              {formatFileSize(file.size)}
                            </p>
                          </div>
                        </div>
                        <button
                          onClick={() => removeFile(index)}
                          className="text-gray-400 hover:text-red-600 transition-colors duration-200"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            {uploadError && (
              <p className="mt-4 text-sm text-red-600">{uploadError}</p>
            )}
          </div>

          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
            >
              Cancel
            </button>
            <button
              onClick={onClose}
              disabled={currentFiles.length === 0 || isUploading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2"
            >
              {isUploading && (
                <svg
                  className="animate-spin h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                  />
                </svg>
              )}
              {isUploading
                ? "Uploading..."
                : `Done (${currentFiles.length} files)`}
            </button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};
