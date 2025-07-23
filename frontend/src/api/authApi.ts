import type {
  LoginCredentials,
  RegisterCredentials,
  User,
} from "../types/auth";

import { useMutation } from "@tanstack/react-query";

// Simulate API calls - replace with actual backend endpoints
const loginUser = async (credentials: LoginCredentials): Promise<User> => {
  await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate network delay

  // Simulate login validation
  if (
    credentials.email === "demo@example.com" &&
    credentials.password === "password"
  ) {
    return {
      id: "1",
      email: credentials.email,
      name: "Demo User",
      avatar:
        "https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=2",
    };
  }

  throw new Error("Invalid email or password");
};

const registerUser = async (
  credentials: RegisterCredentials
): Promise<User> => {
  await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate network delay

  if (credentials.password !== credentials.confirmPassword) {
    throw new Error("Passwords do not match");
  }

  return {
    id: Date.now().toString(),
    email: credentials.email,
    name: credentials.email.split("@")[0],
  };
};

const loginWithGoogle = async (): Promise<User> => {
  await new Promise((resolve) => setTimeout(resolve, 1000)); // Simulate network delay

  // Simulate Google OAuth response
  return {
    id: "google_" + Date.now(),
    email: "user@gmail.com",
    name: "Google User",
    avatar:
      "https://images.pexels.com/photos/614810/pexels-photo-614810.jpeg?auto=compress&cs=tinysrgb&w=100&h=100&dpr=2",
  };
};

export const useLogin = () => {
  return useMutation({
    mutationFn: loginUser,
  });
};

export const useRegister = () => {
  return useMutation({
    mutationFn: registerUser,
  });
};

export const useGoogleLogin = () => {
  return useMutation({
    mutationFn: loginWithGoogle,
  });
};
