import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login } from "../services/auth";

function Login() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const data = await login(username, password);

      console.log("Login response:", data);
      console.log("Access token:", data.access_token);

      localStorage.setItem("access_token", data.access_token);

      console.log(
        "After storing:",
        localStorage.getItem("access_token")
      );

      alert("Login Successful!");

      navigate("/dashboard");

    } catch (error: any) {
      console.error("Login Error:", error);

      if (error.response) {
        console.error("Status:", error.response.status);
        console.error("Data:", error.response.data);
      } else {
        console.error("Message:", error.message);
      }

      alert("Login Failed");
    }
  };

  return (
    <div style={{ padding: "30px" }}>
      <h2>CyBreach Validator Login</h2>

      <form onSubmit={handleLogin}>
        <div style={{ marginBottom: "15px" }}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>

        <div style={{ marginBottom: "15px" }}>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button type="submit">
          Login
        </button>
      </form>
    </div>
  );
}

export default Login;