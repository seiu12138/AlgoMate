import axios from "axios";

export const apiClient = axios.create({
    baseURL: "http://localhost:8000/api",
    timeout: 30000,
});

// 请求拦截器
apiClient.interceptors.request.use(
    (config) => {
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// 响应拦截器
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("API Error:", error);
        return Promise.reject(error);
    }
);
