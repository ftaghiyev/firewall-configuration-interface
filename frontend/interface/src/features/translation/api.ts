import axiosClient from "@/axios-client";
import type { PolicyTranslateRequestPayload } from "./types";

export async function confirmPolicy(payload: PolicyTranslateRequestPayload) {
  const res = await axiosClient.post("/policies/confirm", payload);

  return res.data;
}
