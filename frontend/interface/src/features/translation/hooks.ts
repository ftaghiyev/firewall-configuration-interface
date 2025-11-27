import { useMutation } from "@tanstack/react-query";
import type {
  PolicySummaryRequestPayload,
  PolicyTranslateRequestPayload,
} from "./types";
import {
  summarizePolicy as apiSummarizePolicy,
  translatePolicy as apiTranslatePolicy,
} from "./api";

export function useSummarizePolicy() {
  const { mutateAsync, isPending: loading } = useMutation({
    mutationFn: (payload: PolicySummaryRequestPayload) =>
      apiSummarizePolicy(payload),
  });

  return { summarizePolicy: mutateAsync, loading };
}

export function useTranslatePolicy() {
  const { mutateAsync, isPending: loading } = useMutation({
    mutationFn: (payload: PolicyTranslateRequestPayload) =>
      apiTranslatePolicy(payload),
  });

  return { translatePolicy: mutateAsync, loading };
}
