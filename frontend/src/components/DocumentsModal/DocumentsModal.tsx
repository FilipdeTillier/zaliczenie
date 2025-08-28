import React, { useEffect, useMemo, useState } from "react";
import { Dialog } from "@headlessui/react";
import { FileText, X } from "lucide-react";
import {
  getDocuments,
  type DocumentItem,
} from "../../services/documentsService";
import { useAppDispatch } from "../../hooks/useAppDispatch";
import { useAppSelector } from "../../hooks/useAppSelector";
import { setDocuments } from "../../store/chatSlice";

interface DocumentsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const DocumentsModal: React.FC<DocumentsModalProps> = ({
  isOpen,
  onClose,
}) => {
  const dispatch = useAppDispatch();
  const selectedDocuments = useAppSelector((state) => state.chat.documents);

  const [documents, setDocumentsList] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedChecksums, setSelectedChecksums] = useState<Set<string>>(
    () => new Set(selectedDocuments.map((d) => d.checksum_sha256))
  );

  useEffect(() => {
    if (!isOpen) return;
    setSelectedChecksums(
      new Set(selectedDocuments.map((d) => d.checksum_sha256))
    );
    const fetchDocs = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await getDocuments();
        setDocumentsList(data.items);
      } catch {
        setError("Failed to load documents.");
      } finally {
        setIsLoading(false);
      }
    };
    fetchDocs();
  }, [isOpen, selectedDocuments]);

  const toggleSelect = (checksum: string) => {
    setSelectedChecksums((prev) => {
      const next = new Set(prev);
      if (next.has(checksum)) next.delete(checksum);
      else next.add(checksum);
      return next;
    });
  };

  const currentSelectedDocuments = useMemo(
    () => documents.filter((d) => selectedChecksums.has(d.checksum_sha256)),
    [documents, selectedChecksums]
  );

  const handleSave = () => {
    dispatch(setDocuments(currentSelectedDocuments));
    onClose();
  };

  const formatDateTime = (iso: string) => {
    const d = new Date(iso);
    const pad = (n: number) => String(n).padStart(2, "0");
    const yyyy = d.getFullYear();
    const mm = pad(d.getMonth() + 1);
    const dd = pad(d.getDate());
    const HH = pad(d.getHours());
    const MM = pad(d.getMinutes());
    const SS = pad(d.getSeconds());
    return `${yyyy}-${mm}-${dd} ${HH}:${MM}:${SS}`;
  };

  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      <div
        className="fixed inset-0 bg-black/30 backdrop-blur-sm"
        aria-hidden="true"
      />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="w-full max-w-xl bg-white rounded-xl shadow-2xl">
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <Dialog.Title className="text-lg font-semibold text-gray-900">
              Select Saved Documents
            </Dialog.Title>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors duration-200"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="p-6">
            {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
            <div
              className="border rounded-lg bg-gray-50"
              style={{ maxHeight: 360, overflowY: "auto" }}
            >
              {isLoading ? (
                <div className="p-6 text-sm text-gray-600">Loading...</div>
              ) : documents.length === 0 ? (
                <div className="p-6 text-sm text-gray-600">
                  No documents found.
                </div>
              ) : (
                <ul className="divide-y divide-gray-200">
                  {documents.map((doc) => (
                    <li
                      key={doc.checksum_sha256}
                      className="flex items-center justify-between p-3 hover:bg-gray-100 cursor-pointer transition-colors duration-150"
                      onClick={() => toggleSelect(doc.checksum_sha256)}
                    >
                      <div className="flex items-center gap-3">
                        <FileText className="w-4 h-4 text-blue-600" />
                        <div>
                          <p className="text-sm font-medium text-gray-900">
                            {doc.filename}
                          </p>
                          <p className="text-xs text-gray-500">
                            {formatDateTime(doc.created_at)}
                          </p>
                        </div>
                      </div>
                      <input
                        type="checkbox"
                        className="w-4 h-4 accent-blue-600"
                        checked={selectedChecksums.has(doc.checksum_sha256)}
                        onChange={(e) => {
                          e.stopPropagation();
                          toggleSelect(doc.checksum_sha256);
                        }}
                      />
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
            <button
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors duration-200"
            >
              Save ({currentSelectedDocuments.length})
            </button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};
