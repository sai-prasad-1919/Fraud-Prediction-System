import api from "./client";

export const adminLogin = (admin_id, password) => {
  return api.post("/admin/login", { admin_id, password });
};

export const adminRegister = (name, email, password) => {
  return api.post("/admin/register", { name, email, password });
};