export type PolicyTranslateRequestPayload = {
  message: string;
  context: string | Record<string, any> | File;
};
