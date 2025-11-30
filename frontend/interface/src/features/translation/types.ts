export type Context = {
  description?: string;
  details?: Record<string, any>;
  filename?: string;
};

export type PolicySummaryRequestPayload = {
  message: string;
  context: Context;
};

export type PolicyTranslateRequestPayload = {
  session_id: string;
  confirm: boolean;
};
