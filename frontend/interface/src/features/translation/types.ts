export type Context = {
  description?: string;
  details?: Record<string, any>;
};

export type PolicyTranslateRequestPayload = {
  message: string;
  context: Context;
};
