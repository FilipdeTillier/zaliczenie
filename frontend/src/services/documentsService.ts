import axios from "axios";

export interface DocumentItem {
  filename: string;
  checksum_sha256: string;
  size_bytes: number;
  storage_key: string;
  content_type: string;
  created_at: string;
  download_url: string;
}

export interface DocumentsResponse {
  count: number;
  items: DocumentItem[];
}

export const postDocuments = async (files: File[]) => {
  const formData = new FormData();
  files.forEach((file) => {
    formData.append("files", file, file.name);
  });

  const response = await axios.post("http://localhost:8080/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const getDocuments = async (): Promise<DocumentsResponse> => {
  const { data } = await axios.get<DocumentsResponse>(
    "http://localhost:8080/files"
  );
  return data;
};

export const deleteDocument = async (checksum: string, filename: string) => {
  const response = await axios.delete("http://localhost:8080/files/delete", {
    headers: {
      "Content-Type": "application/json",
    },
    data: {
      checksum,
      filename,
    },
  });

  return response.data;
};
