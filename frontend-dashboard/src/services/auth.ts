import api from "./api";

export const login = async (username: string, password: string) => {
  const formData = new URLSearchParams();

  formData.append("username", username);
  formData.append("password", password);

  const response = await api.post(
    "/auth/login",
    formData,
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    }
  );

  console.log("AUTH RESPONSE:", response);

  return response.data;
};