import axiosClient from "@/axios-client";
import type {
  PolicySummaryRequestPayload,
  PolicyTranslateRequestPayload,
} from "./types";

export async function summarizePolicy(payload: PolicySummaryRequestPayload) {
  const res = await axiosClient.post("/policies/confirm", payload);

  return res.data;
}

export async function translatePolicy(payload: PolicyTranslateRequestPayload) {
  const res = await axiosClient.post("/policies/translate", payload);

  return res.data;
}
